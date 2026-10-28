"""Write data/dashboard/bets.json and players.json, the two files the tournament dashboard reads.

bets.json holds every bet from all three competitions (result "open" until graded); players.json holds
each player's competition, model, effort and starting value. The dashboard works out standings and
value over time from these, so this script only reshapes the ledgers.
"""
import json

from common import BANKROLL_LEDGER, DATA, DOUBLE_ELIM_LEDGER, LEDGER, load_config, read_ledger

OUT = DATA / "dashboard"
LEAGUES = {
    "basketball_nba": "NBA", "americanfootball_nfl": "NFL", "americanfootball_ncaaf": "NCAAF",
    "icehockey_nhl": "NHL", "baseball_mlb": "MLB", "soccer_epl": "EPL", "soccer_uefa_champs_league": "UCL",
}


def bet_rows(competition, rows):
    for r in rows:
        yield {
            "bet_id": f"{competition}:{r['date']}:{r['player']}:{r['option_id']}",
            "competition": competition,
            "date": r["date"],
            "player": r["player"],
            "model": r["model"],
            "effort": r["effort"],
            "sport": r["sport"],
            "league": LEAGUES.get(r["sport"], r["sport"]),
            "matchup": r["matchup"],
            "commence_time": r["commence_time"],
            "pick": r["pick"],
            "price_american": r["price_american"],
            "price_decimal": float(r["price_decimal"] or 0),
            "stake": float(r["stake"]),
            "confidence": float(r["confidence"] or 0),
            "result": r["result"] or "open",
            "pnl": float(r["pnl"]) if r["result"] else None,
            "reason": r["reason"],
        }


def main():
    cfg = load_config()
    bets = (list(bet_rows("flat", read_ledger(LEDGER))) + list(bet_rows("bankroll", read_ledger(BANKROLL_LEDGER)))
            + list(bet_rows("double_elim", read_ledger(DOUBLE_ELIM_LEDGER))))
    players = [{"key": f"flat:{p['name']}", "competition": "flat", "player": p["name"], "model": p["model"],
                "effort": p["effort"], "start": 0.0} for p in cfg["players"]]
    if "bankroll" in cfg:
        players += [{"key": f"bankroll:{p['name']}", "competition": "bankroll", "player": p["name"],
                     "model": p["model"], "effort": p["effort"], "start": float(cfg["bankroll"]["start"])}
                    for p in cfg["bankroll"]["players"]]
    if "double_elim" in cfg:
        players += [{"key": f"double_elim:{p['name']}", "competition": "double_elim", "player": p["name"],
                     "model": p["model"], "effort": p["effort"], "start": float(cfg["double_elim"]["start"])}
                    for p in cfg["double_elim"]["players"]]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bets.json").write_text(json.dumps(bets, indent=1) + "\n")
    (OUT / "players.json").write_text(json.dumps(players, indent=1) + "\n")
    print(f"dashboard: {len(bets)} bets, {len(players)} players -> {OUT}")


if __name__ == "__main__":
    main()
