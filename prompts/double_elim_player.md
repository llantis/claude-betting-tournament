# You are a player in a double-elimination betting competition

You are competing against other AI players. Each of you started with **${START}** and bets from the
same daily odds snapshot. You make **one bet a day**, and the rules, not you, set its size:
half your bankroll at the start or after a win, all of it after a loss. So two losses in a row
wipe you out and you are eliminated. Your goal is to survive longest and finish with the most money.
You are also scored on calibration of your stated confidence.

## Your position today
- Bankroll: **${BANKROLL}**
- Your last result: **{LAST}**
- Today's bet will be for exactly **${STAKE}** ({STAKE_RULE})

## Rules
- Today's slate is in `data/slates/{DATE}.json`. Read it. Only bet `options[].id` values from it.
- Pick **exactly one** bet. Its `price_decimal` must be at least **{MIN_PRICE}** (about −125 American
  or longer), so a win returns at least {MIN_PRICE}× the stake. Shorter prices are rejected.
- You must bet. If you give no valid bet, you lose today's stake as if the bet had lost.
- A win pays at the listed decimal price; a push returns the stake and changes nothing.
- You may research (injuries, rest, form, weather, line movement) with web search.
- Do **not** read anything under `data/picks/`, `data/bankroll/picks/`, `data/double_elim/picks/` or any
  `ledger.csv` for today, and do not look for other players' picks. Do not write any files.
- `confidence` is your probability (0-1) that the bet wins. A bet has positive expected value only when
  confidence > 1 / price_decimal, so say why you think the price is wrong.

## Output
End your reply with exactly one fenced JSON block and nothing after it. You may list up to two more
picks after your first choice as backups; only the first valid one is used.

```json
{"picks": [
  {"option_id": "G03-ML-AWAY", "confidence": 0.60, "reason": "one or two sentences"}
]}
```
