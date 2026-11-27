"""Print a player's full prompt for a day, with every placeholder filled, so the daily run hands each
player exactly the same kind of prompt and nothing (report card, lessons) is left out by hand.

    python3 scripts/player_prompt.py <flat|bankroll|double_elim> <player> [--date YYYY-MM-DD]

Bankroll and double-elimination prompts include the player's report card (data/report_cards/) and its
own lessons from earlier rounds (data/lessons/). Flat prompts get neither: flat is the comparison group.
Run `python3 scripts/leaderboard.py` and `python3 scripts/report_card.py` first so standings and report
cards are current. Exits with an error if any placeholder is left unfilled.
"""
import argparse
import json
import re
import sys

from common import DATA, LESSONS, ROOT, load_config, today

PROMPTS = {"flat": "player.md", "bankroll": "bankroll_player.md", "double_elim": "double_elim_player.md"}


def read_or(path, fallback):
    return path.read_text().strip() if path.exists() else fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("competition", choices=sorted(PROMPTS))
    ap.add_argument("player")
    ap.add_argument("--date", default=today())
    args = ap.parse_args()
    cfg = load_config()
    comp, name = args.competition, args.player
    players = cfg["players"] if comp == "flat" else cfg[comp]["players"]
    if name not in {p["name"] for p in players}:
        sys.exit(f"{name} is not a {comp} player")

    values = {"DATE": args.date}
    if comp == "flat":
        values["MAX_PICKS"] = str(cfg["max_picks_per_player_per_day"])
    else:
        ccfg = cfg[comp]
        values["START"] = f"{ccfg['start']:.2f}"
        values["REPORT_CARD"] = read_or(DATA / "report_cards" / comp / f"{name}.md", "No report card yet.")
        values["LESSONS"] = read_or(LESSONS / comp / f"{name}.md", "No lessons yet.")
        s = json.loads((DATA / comp / "standings.json").read_text())[name]
        if comp == "bankroll":
            values.update(MAX_PICKS=str(ccfg["max_picks_per_player_per_day"]), MIN_BET=f"{ccfg['min_bet']:.2f}",
                          MIN_DAILY=f"{ccfg['min_daily_stake']:.2f}", BANKROLL=f"{s['bankroll']:.2f}",
                          RIDING=f"{s['riding']:.2f}", AVAILABLE=f"{s['available']:.2f}")
        else:
            values.update(MIN_PRICE=f"{ccfg['min_price_decimal']:.2f}", BANKROLL=f"{s['bankroll']:.2f}",
                          STAKE=f"{s['next_stake']:.2f}",
                          LAST="none yet" if s["last"] == "start" else s["last"],
                          STAKE_RULE="all of your bankroll, because your last bet lost" if s["last"] == "loss"
                          else "half of your bankroll")

    text = (ROOT / "prompts" / PROMPTS[comp]).read_text()
    # Fill the template's own placeholders only; the pasted report card and lessons are never re-scanned.
    out = re.sub(r"\{([A-Z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), text)
    left = set(re.findall(r"\{([A-Z_]+)\}", text)) - set(values)
    if left:
        sys.exit(f"unfilled placeholders in {PROMPTS[comp]}: {', '.join(sorted(left))}")
    print(out)


if __name__ == "__main__":
    main()
