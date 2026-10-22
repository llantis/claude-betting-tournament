"""Validate one player's picks against the day's slate and lock them into the ledger.

Usage: python3 scripts/record_picks.py <player> <picks.json> [--date YYYY-MM-DD] [--competition bankroll]
picks.json: {"picks": [{"option_id": "G03-ML-HOME", "confidence": 0.58, "reason": "...", "stake": 2.5}]}
("stake" is only read in the bankroll competition.)

This is the only path into the ledgers, so every rule is enforced here, not in prompts:
known player, option exists in the slate, game not started, one pick per game,
at most max_picks, and a player's picks can only be recorded once per day.
Flat competition: fixed stake. Bankroll competition: each stake is at least min_bet, today's stakes
fit in the player's available bankroll, and a player who can afford the daily minimum but stakes
less than it forfeits the shortfall.
"""
import argparse
import json

from common import (BANKROLL_LEDGER, BANKROLL_PICKS, LEDGER, PICKS, SLATES, bankroll_status,
                    load_config, now_utc, parse_time, read_ledger, today, write_ledger)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("player")
    ap.add_argument("picks_file")
    ap.add_argument("--date", default=today())
    ap.add_argument("--competition", choices=["flat", "bankroll"], default="flat")
    args = ap.parse_args()

    cfg = load_config()
    bankroll = args.competition == "bankroll"
    rules = cfg["bankroll"] if bankroll else cfg
    picks_dir, ledger = (BANKROLL_PICKS, BANKROLL_LEDGER) if bankroll else (PICKS, LEDGER)
    max_picks = rules["max_picks_per_player_per_day"]

    player = next((p for p in rules["players"] if p["name"] == args.player), None)
    if not player:
        raise SystemExit(f"unknown {args.competition} player {args.player!r}")

    slate = json.loads((SLATES / f"{args.date}.json").read_text())
    options = {o["id"]: (g, o) for g in slate["games"] for o in g["options"]}

    out = picks_dir / args.date / f"{args.player}.json"
    if out.exists():
        raise SystemExit(f"{args.player} already has locked picks for {args.date}")

    status = bankroll_status(cfg)[args.player] if bankroll else None
    if bankroll and status["busted"]:
        submitted = []
        print(f"{args.player}: busted (${status['available']:.2f} left), no picks taken")
    else:
        submitted = json.loads(open(args.picks_file).read()).get("picks", [])

    now = now_utc()
    accepted, rejected, seen_games = [], [], set()
    spent = 0.0
    for p in submitted:
        oid = p.get("option_id")
        if oid not in options:
            rejected.append((oid, "not in slate"))
            continue
        game, opt = options[oid]
        if parse_time(game["commence_time"]) <= now:
            rejected.append((oid, "game already started"))
            continue
        if game["game_id"] in seen_games:
            rejected.append((oid, "second pick on same game"))
            continue
        if len(accepted) >= max_picks:
            rejected.append((oid, "over daily pick limit"))
            continue
        stake = cfg["stake"]
        if bankroll:
            try:
                stake = round(float(p.get("stake")), 2)
            except (TypeError, ValueError):
                rejected.append((oid, "missing or invalid stake"))
                continue
            if stake < rules["min_bet"]:
                rejected.append((oid, f"stake below ${rules['min_bet']:.2f} minimum"))
                continue
            if spent + stake > status["available"] + 1e-9:
                rejected.append((oid, f"stake over available bankroll (${status['available'] - spent:.2f} left)"))
                continue
            spent += stake
        try:
            conf = min(max(float(p.get("confidence", 0.5)), 0.0), 1.0)
        except (TypeError, ValueError):
            conf = 0.5
        seen_games.add(game["game_id"])
        accepted.append({
            "date": args.date,
            "player": player["name"],
            "model": player["model"],
            "effort": player["effort"],
            "sport": game["sport"],
            "matchup": game["matchup"],
            "game_id": game["event_id"],
            "commence_time": game["commence_time"],
            "option_id": oid,
            "pick": opt["label"],
            "price_decimal": opt["price_decimal"],
            "price_american": opt["price_american"],
            "stake": stake,
            "confidence": round(conf, 3),
            "reason": " ".join(str(p.get("reason", "")).split())[:300],
            "placed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "result": "",
            "pnl": "",
        })

    # Daily minimum: a player who can afford a bet but stakes less than the minimum loses the
    # shortfall. Only on days with games on the slate.
    if bankroll and slate["games"] and status["available"] >= rules["min_bet"]:
        minimum = min(rules["min_daily_stake"], status["available"])
        shortfall = round(minimum - spent, 2)
        if shortfall > 0:
            accepted.append({
                "date": args.date, "player": player["name"], "model": player["model"],
                "effort": player["effort"], "sport": "", "matchup": "", "game_id": "",
                "commence_time": "", "option_id": "FORFEIT", "pick": "missed daily minimum",
                "price_decimal": "", "price_american": "", "stake": shortfall, "confidence": "",
                "reason": f"staked ${spent:.2f}, minimum ${minimum:.2f}",
                "placed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "result": "forfeit", "pnl": f"{-shortfall:.2f}",
            })
            print(f"{args.player}: forfeits ${shortfall:.2f} for staking under the daily minimum")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"accepted": accepted, "rejected": rejected}, indent=2))
    write_ledger(read_ledger(ledger) + accepted, ledger)
    bets = [r for r in accepted if r["option_id"] != "FORFEIT"]
    print(f"{args.player}: {len(bets)} accepted, {len(rejected)} rejected"
          + (f", ${spent:.2f} staked of ${status['available']:.2f} available" if bankroll else ""))
    for oid, why in rejected:
        print(f"  rejected {oid}: {why}")


if __name__ == "__main__":
    main()
