"""Write a report card for each player in the competitions listed under `report_cards` in config.json:
data/report_cards/<competition>/<player>.md, built from that player's settled bets in its own ledger
(every round, for double elimination). The daily run pastes it into the player's prompt so it can
learn from its past results. Only settled bets are used, so nothing about today's picks leaks in.

The flat competition gets no report card on purpose: it is the comparison group that shows whether
the feedback helps.

Usage: python3 scripts/report_card.py
"""
from collections import defaultdict

from common import BANKROLL_LEDGER, DATA, DOUBLE_ELIM_LEDGER, load_config, read_ledger

OUT = DATA / "report_cards"
LEDGERS = {"bankroll": BANKROLL_LEDGER, "double_elim": DOUBLE_ELIM_LEDGER}
LEAGUES = {
    "basketball_nba": "NBA", "americanfootball_nfl": "NFL", "americanfootball_ncaaf": "NCAAF",
    "icehockey_nhl": "NHL", "baseball_mlb": "MLB", "soccer_epl": "EPL", "soccer_uefa_champs_league": "UCL",
}
MARKETS = {"ML": "Moneyline", "SPREAD": "Spread", "TOTAL": "Total"}
RECENT = 10
BUCKETS = ["under 50%", "50-54%", "55-59%", "60% or more"]
MIN_SEGMENT = 4  # bets needed before a segment gets called out as a strength or a leak


def market(r):
    parts = r["option_id"].split("-")
    return MARKETS.get(parts[1], parts[1]) if len(parts) > 1 else "Other"


def side(r):
    return "Underdog (2.00+)" if float(r["price_decimal"]) >= 2.0 else "Favorite (under 2.00)"


def conf_bucket(r):
    c = float(r["confidence"])
    if c < 0.50:
        return "under 50%"
    if c < 0.55:
        return "50-54%"
    if c < 0.60:
        return "55-59%"
    return "60% or more"


def summary(rows):
    """Win/loss stats for settled, non-forfeit bets."""
    bets = [r for r in rows if r["result"] in ("win", "loss", "push")]
    decided = [r for r in bets if r["result"] != "push"]
    w = sum(r["result"] == "win" for r in bets)
    staked = sum(float(r["stake"]) for r in bets)
    pnl = sum(float(r["pnl"]) for r in bets)
    n = len(decided)
    return {
        "n": len(bets), "w": w, "l": sum(r["result"] == "loss" for r in bets),
        "p": sum(r["result"] == "push" for r in bets), "staked": staked, "pnl": pnl,
        "roi": pnl / staked if staked else None,
        "win": w / n if n else None,
        "conf": sum(float(r["confidence"]) for r in decided) / n if n else None,
        "implied": sum(1 / float(r["price_decimal"]) for r in decided) / n if n else None,
    }


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def segment_table(title, rows, key, order=None):
    groups = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    lines = [f"### {title}", "", "| | Bets | W-L-P | Win rate | Your avg confidence | P/L | ROI |",
             "|---|---|---|---|---|---|---|"]
    ranked = sorted(groups.items(), key=(lambda kv: order.index(kv[0])) if order else (lambda kv: -len(kv[1])))
    for name, rs in ranked:
        s = summary(rs)
        lines.append(f"| {name} | {s['n']} | {s['w']}-{s['l']}-{s['p']} | {pct(s['win'])} | {pct(s['conf'])} | "
                     f"${s['pnl']:+.2f} | {pct(s['roi'])} |")
    return lines, groups


def card(competition, player, rows):
    mine = [r for r in rows if r["player"] == player and r["result"]]
    settled = [r for r in mine if r["result"] != "forfeit"]
    forfeits = [r for r in mine if r["result"] == "forfeit"]
    lines = [f"# Report card: {player} ({competition})", ""]
    if not settled:
        lines += ["No settled bets yet, so there is nothing to learn from. This is your first day."]
        if forfeits:
            lines += ["", f"You have forfeited {len(forfeits)} time(s) by giving no valid pick."]
        return "\n".join(lines) + "\n"

    s = summary(settled)
    lines += [
        f"Settled bets: **{s['n']}** ({s['w']} won, {s['l']} lost, {s['p']} pushed). "
        f"Staked ${s['staked']:.2f}, P/L **${s['pnl']:+.2f}**, ROI **{pct(s['roi'])}**.",
        "",
        "## Calibration",
        f"- You said your bets would win **{pct(s['conf'])}** of the time on average.",
        f"- They actually won **{pct(s['win'])}**.",
        f"- The prices you took implied **{pct(s['implied'])}** (what the market expected).",
        "",
    ]
    flags = []
    if s["win"] is not None and s["n"] >= MIN_SEGMENT:
        gap = s["conf"] - s["win"]
        if gap >= 0.05:
            flags.append(f"You have been **overconfident by {gap * 100:.0f} percentage points**: your confidence has run ahead of "
                         "your results, so demand a clearer reason before you claim an edge.")
        elif gap <= -0.05:
            flags.append(f"You have been **underconfident by {-gap * 100:.0f} percentage points**: your bets won more often than you said.")
        if s["win"] < s["implied"]:
            flags.append("Your bets have won **less often than the prices implied**, so far your picks have done "
                         "worse than simply trusting the market.")

    bucket_lines, _ = segment_table("By stated confidence", settled, conf_bucket, BUCKETS)
    lines += bucket_lines + [""]
    for title, key in (("By league", lambda r: LEAGUES.get(r["sport"], r["sport"])),
                       ("By bet type", market), ("Favorites vs underdogs", side)):
        seg_lines, groups = segment_table(title, settled, key)
        lines += seg_lines + [""]
        for name, rs in groups.items():
            g = summary(rs)
            if g["n"] >= MIN_SEGMENT and g["roi"] is not None:
                if g["roi"] <= -0.20:
                    flags.append(f"**{name}** has been a leak: {g['w']}-{g['l']}-{g['p']}, ROI {pct(g['roi'])}.")
                elif g["roi"] >= 0.15:
                    flags.append(f"**{name}** has worked for you: {g['w']}-{g['l']}-{g['p']}, ROI {pct(g['roi'])}.")
    if forfeits:
        flags.append(f"You have forfeited **{len(forfeits)}** time(s) "
                     f"(${-sum(float(r['pnl']) for r in forfeits):.2f}) by not giving a valid pick.")

    lines += ["## What stands out", ""]
    lines += [f"- {f}" for f in flags] or ["- Nothing stands out yet."]
    lines += ["- Small samples are noisy: treat a segment with fewer than about 20 bets as a hint, not proof.", ""]

    recent = sorted(settled, key=lambda r: (r["date"], r["placed_at"]))[-RECENT:][::-1]
    lines += [f"## Your last {len(recent)} settled bets (newest first)", "",
              "| Date | Pick | Price | Stake | Confidence | Result | P/L | Your reason at the time |",
              "|---|---|---|---|---|---|---|---|"]
    for r in recent:
        reason = r["reason"].replace("|", "/").replace("\n", " ")
        lines.append(f"| {r['date']} | {r['pick']} ({LEAGUES.get(r['sport'], r['sport'])}) | {float(r['price_decimal']):.2f} | "
                     f"${float(r['stake']):.2f} | {float(r['confidence']):.0%} | {r['result']} | ${float(r['pnl']):+.2f} | "
                     f"{reason} |")
    return "\n".join(lines) + "\n"


def main():
    cfg = load_config()
    for competition in cfg.get("report_cards", {}).get("competitions", []):
        rows = read_ledger(LEDGERS[competition])
        out = OUT / competition
        out.mkdir(parents=True, exist_ok=True)
        for p in cfg[competition]["players"]:
            (out / f"{p['name']}.md").write_text(card(competition, p["name"], rows))
        print(f"report cards: {len(cfg[competition]['players'])} players -> {out.relative_to(DATA.parent)}")


if __name__ == "__main__":
    main()
