"""Shared paths, config loading, odds helpers and ledger I/O."""
import csv
import json
import math
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SLATES = DATA / "slates"
PICKS = DATA / "picks"
LEDGER = DATA / "ledger.csv"
# Bankroll competition: same slates, its own players, picks and ledger.
BANKROLL = DATA / "bankroll"
BANKROLL_PICKS = BANKROLL / "picks"
BANKROLL_LEDGER = BANKROLL / "ledger.csv"
# Double elimination: same slates, one forced-size bet per player per day, out at $0.
DOUBLE_ELIM = DATA / "double_elim"
DOUBLE_ELIM_PICKS = DOUBLE_ELIM / "picks"
DOUBLE_ELIM_LEDGER = DOUBLE_ELIM / "ledger.csv"
ODDS_API = "https://api.the-odds-api.com/v4"

LEDGER_FIELDS = [
    "date", "player", "model", "effort", "sport", "matchup", "game_id",
    "commence_time", "option_id", "pick", "price_decimal", "price_american",
    "stake", "confidence", "reason", "placed_at", "result", "pnl",
]


def load_config():
    return json.loads((ROOT / "config.json").read_text())


def now_utc():
    return datetime.now(timezone.utc)


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def today():
    # Slates are keyed by the US Eastern calendar day.
    return now_utc().astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")


def american(decimal_odds):
    if decimal_odds >= 2.0:
        return f"+{round((decimal_odds - 1) * 100)}"
    return f"-{round(100 / (decimal_odds - 1))}"


def odds_api_get(path, **params):
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise SystemExit("ODDS_API_KEY is not set (add it as an environment secret).")
    params["apiKey"] = key
    url = f"{ODDS_API}{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        remaining = resp.headers.get("x-requests-remaining")
        if remaining is not None:
            print(f"  odds-api requests remaining: {remaining}")
        return json.loads(resp.read())


def read_ledger(path=LEDGER):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_ledger(rows, path=LEDGER):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)


def bankroll_status(cfg, rows=None):
    """Per bankroll player: settled bankroll, stakes still riding on open bets, and what's free to bet."""
    bcfg = cfg["bankroll"]
    rows = read_ledger(BANKROLL_LEDGER) if rows is None else rows
    status = {}
    for p in bcfg["players"]:
        mine = [r for r in rows if r["player"] == p["name"]]
        settled = bcfg["start"] + sum(float(r["pnl"]) for r in mine if r["result"])
        riding = sum(float(r["stake"]) for r in mine if not r["result"])
        available = round(settled - riding, 2)
        status[p["name"]] = {
            "bankroll": round(settled, 2),
            "riding": round(riding, 2),
            "available": available,
            "busted": available < bcfg["min_bet"] and riding == 0,
        }
    return status


def half_up(x):
    """Round to the cent, halves up (so a $1.25 bankroll's half-stake is $0.63)."""
    return math.floor(x * 100 + 0.5 + 1e-9) / 100


def double_elim_status(cfg, rows=None):
    """Per double-elimination player, replayed from the ledger: bankroll, what's riding, the stake
    its next bet must be (half the bankroll at the start or after a win, all of it after a loss),
    and whether it's out (nothing left and nothing riding)."""
    dcfg = cfg["double_elim"]
    rows = read_ledger(DOUBLE_ELIM_LEDGER) if rows is None else rows
    status = {}
    for p in dcfg["players"]:
        bank, riding, last, peak, out_date, bets = dcfg["start"], 0.0, "start", dcfg["start"], None, 0
        for r in rows:
            if r["player"] != p["name"]:
                continue
            if not r["result"]:
                riding += float(r["stake"])
                continue
            bank = round(bank + float(r["pnl"]), 2)
            peak = max(peak, bank)
            if r["result"] != "forfeit":
                bets += 1
            if r["result"] in ("loss", "forfeit"):
                last = "loss"
            elif r["result"] == "win":
                last = "win"
            if bank < 0.01 and out_date is None:
                out_date = r["date"]
        status[p["name"]] = {
            "bankroll": bank,
            "riding": round(riding, 2),
            "last": last,
            "next_stake": bank if last == "loss" else half_up(bank / 2),
            "peak": round(peak, 2),
            "settled_bets": bets,
            "out": bank < 0.01 and riding == 0,
            "out_date": out_date,
        }
    return status
