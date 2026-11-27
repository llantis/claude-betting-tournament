"""Archive a finished round of the bankroll or double-elimination competition into data/past_runs/, and
optionally start the next round.

    python3 scripts/archive_round.py <bankroll|double_elim> [--round N] [--start D] [--end D] [--reset D]

Writes data/past_runs/<competition>-round-<N>/:
  summary.md     final standings and stats for every player
  bets.csv       every bet of the round (ledger rows from --start to --end)
  meta.json      competition, round, dates, top finisher (used to build the index)
  report_cards/  each player's report card as it stood at the end of the round (latest round only)
and rebuilds data/past_runs/README.md (the index of every archived round).

Defaults: --round is the competition's current `round` in config.json (1 if unset), --start its
`round_start` (or the first ledger date), --end the last ledger date. Every bet in the range must be
settled. The ledger itself is never changed.

--reset D bumps `round` and sets `round_start` to D in config.json, so from slate date D on every player
is back at the starting bankroll. Players' lessons (data/lessons/) and report cards carry over.
"""
import argparse
import csv
import json
import shutil
import sys
from collections import defaultdict

from common import DATA, LEDGER_FIELDS, LEDGERS, PAST_RUNS, ROOT, load_config, read_ledger

NAMES = {"bankroll": "Bankroll", "double_elim": "Double elimination"}


def replay(cfg, competition, player, rows):
    """Walk a player's settled bets in order: final bankroll, peak, and the date it went out."""
    ccfg = cfg[competition]
    floor = ccfg.get("min_bet", 0.01) if competition == "bankroll" else 0.01
    bank, peak, out_date = ccfg["start"], ccfg["start"], None
    by_date = defaultdict(float)
    for r in rows:
        if r["player"] == player:
            by_date[r["date"]] += float(r["pnl"])
    for d in sorted(by_date):
        bank = round(bank + by_date[d], 2)
        peak = max(peak, bank)
        if bank < floor and out_date is None:
            out_date = d
    return round(bank, 2), round(peak, 2), out_date


def stats(rows):
    bets = [r for r in rows if r["result"] in ("win", "loss", "push")]
    decided = [r for r in bets if r["result"] != "push"]
    staked = sum(float(r["stake"]) for r in bets)
    pnl = sum(float(r["pnl"]) for r in bets)
    n = len(decided)
    return {
        "w": sum(r["result"] == "win" for r in bets), "l": sum(r["result"] == "loss" for r in bets),
        "p": sum(r["result"] == "push" for r in bets),
        "forfeits": sum(r["result"] == "forfeit" for r in rows),
        "staked": round(staked, 2), "pnl": round(pnl, 2), "roi": pnl / staked if staked else None,
        "win": sum(r["result"] == "win" for r in decided) / n if n else None,
        "conf": sum(float(r["confidence"]) for r in decided) / n if n else None,
        "implied": sum(1 / float(r["price_decimal"]) for r in decided) / n if n else None,
        "brier": sum((float(r["confidence"]) - (r["result"] == "win")) ** 2 for r in decided) / n if n else None,
    }


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def build_index():
    metas = sorted((json.loads(p.read_text()) for p in PAST_RUNS.glob("*/meta.json")),
                   key=lambda m: (m["start"], m["competition"]))
    lines = ["# Past runs", "",
             "Finished rounds of the bankroll and double-elimination competitions. Each folder has the final",
             "standings (`summary.md`), every bet (`bets.csv`), each player's report card at the end, and the",
             "post-mortem each player wrote about its own bets (`postmortems/`). The lessons from those",
             "post-mortems live on in `data/lessons/` and go into the players' prompts in later rounds.", "",
             "| Competition | Round | Dates | Days | Bets | Top finisher | Best final bankroll |",
             "|---|---|---|---|---|---|---|"]
    for m in metas:
        lines.append(f"| {NAMES[m['competition']]} | [{m['round']}]({m['folder']}/summary.md) | {m['start']} to {m['end']} | "
                     f"{m['days']} | {m['bets']} | {m['top']} | ${m['best_final']:.2f} |")
    (PAST_RUNS / "README.md").write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("competition", choices=sorted(LEDGERS))
    ap.add_argument("--round", type=int)
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--reset", metavar="YYYY-MM-DD", help="start the next round on this slate date")
    ap.add_argument("--force", action="store_true", help="overwrite an existing archive folder")
    args = ap.parse_args()

    cfg = load_config()
    comp = args.competition
    ccfg = cfg[comp]
    all_rows = read_ledger(LEDGERS[comp])
    rnd = args.round or ccfg.get("round", 1)
    start = args.start or ccfg.get("round_start") or min(r["date"] for r in all_rows)
    in_start = [r for r in all_rows if r["date"] >= start]
    end = args.end or max(r["date"] for r in in_start)
    rows = [r for r in in_start if r["date"] <= end]
    if not rows:
        sys.exit(f"no {comp} bets between {start} and {end}")
    start = min(r["date"] for r in rows)
    open_rows = [r for r in rows if not r["result"]]
    if open_rows:
        sys.exit(f"{len(open_rows)} bet(s) in the round are not settled yet; grade them first")

    folder = f"{comp}-round-{rnd}"
    out = PAST_RUNS / folder
    if out.exists() and not args.force:
        sys.exit(f"{out.relative_to(ROOT)} already exists (use --force to overwrite)")
    out.mkdir(parents=True, exist_ok=True)

    with (out / "bets.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)

    table = []
    for p in ccfg["players"]:
        mine = [r for r in rows if r["player"] == p["name"]]
        final, peak, out_date = replay(cfg, comp, p["name"], mine)
        table.append({**p, **stats(mine), "final": final, "peak": peak, "out_date": out_date,
                      "days": len({r["date"] for r in mine})})
    # Most money left first; among the busted, whoever lasted longest, then the higher peak.
    table.sort(key=lambda t: (-t["final"], -(int(t["out_date"].replace("-", "")) if t["out_date"] else 99999999), -t["peak"]))

    days = len({r["date"] for r in rows})
    all_bets = stats(rows)
    lines = [f"# {NAMES[comp]}, round {rnd}: {start} to {end}", "",
             f"{days} slate days, {len(rows)} bets. Start bankroll ${ccfg['start']:.2f}. "
             f"All players together: win rate {pct(all_bets['win'])} vs stated confidence {pct(all_bets['conf'])} "
             f"vs market-implied {pct(all_bets['implied'])}, ROI {pct(all_bets['roi'])}.", "",
             "| # | Player | Model | Effort | Final | Peak | Out on | Days bet | W-L-P | Forfeits | Staked | Bet P/L | ROI | "
             "Win rate | Avg confidence | Implied | Brier |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, t in enumerate(table, 1):
        brier = "-" if t["brier"] is None else f"{t['brier']:.3f}"
        lines.append(
            f"| {i} | {t['name']} | {t['model']} | {t['effort']} | ${t['final']:.2f} | ${t['peak']:.2f} | "
            f"{t['out_date'] or 'still in'} | {t['days']} | {t['w']}-{t['l']}-{t['p']} | {t['forfeits']} | "
            f"${t['staked']:.2f} | ${t['pnl']:+.2f} | {pct(t['roi'])} | {pct(t['win'])} | {pct(t['conf'])} | "
            f"{pct(t['implied'])} | {brier} |")
    lines += ["", "Out on = the slate date the player's bankroll fell below the minimum bet. "
              "Brier: lower is better, 0.25 is a coin flip.", "",
              "Each player's own post-mortem of this round is in `postmortems/<player>.md`."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")

    # Report cards are rebuilt daily from the whole ledger, so they only describe this round's end when
    # the round is the latest one.
    cards = DATA / "report_cards" / comp
    if cards.exists() and end == max(r["date"] for r in all_rows):
        (out / "report_cards").mkdir(exist_ok=True)
        for p in ccfg["players"]:
            src = cards / f"{p['name']}.md"
            if src.exists():
                shutil.copy(src, out / "report_cards" / src.name)

    meta = {"competition": comp, "round": rnd, "folder": folder, "start": start, "end": end, "days": days,
            "bets": len(rows), "top": table[0]["name"], "best_final": table[0]["final"]}
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    build_index()
    print(f"archived {comp} round {rnd} ({start} to {end}, {len(rows)} bets) -> {out.relative_to(ROOT)}")

    if args.reset:
        ccfg["round"] = rnd + 1
        ccfg["round_start"] = args.reset
        (ROOT / "config.json").write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"{comp}: round {rnd + 1} starts {args.reset}; every player is back at ${ccfg['start']:.2f}")


if __name__ == "__main__":
    main()
