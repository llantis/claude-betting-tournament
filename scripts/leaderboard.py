"""Write data/leaderboard.md (flat competition: P/L, ROI, record, Brier per player) and
data/bankroll/leaderboard.md + standings.json (bankroll competition, ranked by bankroll)."""
import json
from collections import defaultdict

from common import BANKROLL, BANKROLL_LEDGER, DATA, bankroll_status, load_config, read_ledger
from kalshi import read_orders


def main():
    cfg = load_config()
    stats = defaultdict(lambda: {"bets": 0, "w": 0, "l": 0, "p": 0, "open": 0, "staked": 0.0, "pnl": 0.0, "brier": []})
    for r in read_ledger():
        s = stats[r["player"]]
        if not r["result"]:
            s["open"] += 1
            continue
        s["bets"] += 1
        s[r["result"][0]] += 1
        s["staked"] += float(r["stake"])
        s["pnl"] += float(r["pnl"])
        if r["result"] != "push":
            s["brier"].append((float(r["confidence"]) - (r["result"] == "win")) ** 2)

    kalshi = defaultdict(lambda: {"orders": 0, "pnl": 0.0})
    for o in read_orders():
        if o["count"]:
            kalshi[o["player"]]["orders"] += 1
            kalshi[o["player"]]["pnl"] += float(o["pnl"] or 0)

    meta = {p["name"]: p for p in cfg["players"]}
    order = sorted(set(meta) | set(stats), key=lambda n: -stats[n]["pnl"])
    lines = [
        f"# Leaderboard ({cfg['mode']} mode)",
        "",
        "| # | Player | Model | Effort | Record (W-L-P) | Open | P/L | ROI | Brier | Kalshi orders | Kalshi P/L |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, name in enumerate(order, 1):
        s, m = stats[name], meta.get(name, {})
        roi = f"{s['pnl'] / s['staked']:+.1%}" if s["staked"] else "-"
        brier = f"{sum(s['brier']) / len(s['brier']):.3f}" if s["brier"] else "-"
        lines.append(
            f"| {i} | {name} | {m.get('model', '?')} | {m.get('effort', '?')} | "
            f"{s['w']}-{s['l']}-{s['p']} | {s['open']} | ${s['pnl']:+.2f} | {roi} | {brier} | "
            f"{kalshi[name]['orders']} | ${kalshi[name]['pnl']:+.2f} |"
        )
    kc = cfg.get("kalshi", {})
    lines += [
        "",
        "Brier = mean squared error of stated confidence vs outcome (lower is better; 0.25 = coin flip).",
        f"Kalshi columns: orders mirrored to Kalshi {kc.get('env', '-')}"
        f"{' (dry run)' if kc.get('dry_run') else ''}; fees not included.",
    ]
    (DATA / "leaderboard.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if "bankroll" in cfg:
        bankroll_board(cfg)


def bankroll_board(cfg):
    bcfg = cfg["bankroll"]
    rows = read_ledger(BANKROLL_LEDGER)
    status = bankroll_status(cfg, rows)
    stats = defaultdict(lambda: {"w": 0, "l": 0, "p": 0, "open": 0, "staked": 0.0, "pnl": 0.0,
                                 "forfeits": 0.0, "brier": []})
    for r in rows:
        s = stats[r["player"]]
        if r["result"] == "forfeit":
            s["forfeits"] += float(r["stake"])
        elif not r["result"]:
            s["open"] += 1
        else:
            s[r["result"][0]] += 1
            s["staked"] += float(r["stake"])
            s["pnl"] += float(r["pnl"])
            if r["result"] != "push":
                s["brier"].append((float(r["confidence"]) - (r["result"] == "win")) ** 2)

    meta = {p["name"]: p for p in bcfg["players"]}
    order = sorted(meta, key=lambda n: (-status[n]["bankroll"], -stats[n]["w"]))
    lines = [
        f"# Bankroll competition (start ${bcfg['start']:.2f}, min ${bcfg['min_daily_stake']:.2f}/day)",
        "",
        "| # | Player | Model | Effort | Bankroll | Riding | Record (W-L-P) | Open | Bet P/L | ROI | Forfeits | Brier |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, name in enumerate(order, 1):
        s, m, b = stats[name], meta[name], status[name]
        roi = f"{s['pnl'] / s['staked']:+.1%}" if s["staked"] else "-"
        brier = f"{sum(s['brier']) / len(s['brier']):.3f}" if s["brier"] else "-"
        bank = f"${b['bankroll']:.2f}" + (" (busted)" if b["busted"] else "")
        lines.append(
            f"| {i} | {name} | {m['model']} | {m['effort']} | {bank} | ${b['riding']:.2f} | "
            f"{s['w']}-{s['l']}-{s['p']} | {s['open']} | ${s['pnl']:+.2f} | {roi} | "
            f"${s['forfeits']:.2f} | {brier} |"
        )
    lines += ["", "Ranked by bankroll (settled). Riding = stakes on bets not yet graded."]
    BANKROLL.mkdir(parents=True, exist_ok=True)
    (BANKROLL / "leaderboard.md").write_text("\n".join(lines) + "\n")
    (BANKROLL / "standings.json").write_text(json.dumps(status, indent=2) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
