# Betting: AI model tournament

Several Claude players (different models and effort levels) independently bet a flat $1 per pick on
the same daily odds snapshot. Everything runs as a cloud scheduled task; no local machine needed.
Currently **paper mode**: no real money moves.

## How a day works
1. `scripts/grade.py` settles yesterday's bets from final scores.
2. `scripts/snapshot_odds.py` takes **one** odds snapshot (The Odds API) for games starting today (before
   midnight US Central, `slate_timezone`) and locks it as `data/slates/<date>.json`. Every player sees identical lines.
3. The runner starts one subagent per player in `config.json`, in parallel, with that player's
   model and effort. Players see only the slate and `prompts/player.md`, never each other's picks.
4. `scripts/record_picks.py` is the only way into the ledger and enforces the rules in code: option
   must be in the slate, game not started, one pick per game, daily pick cap, fixed stake, picks
   locked once recorded.
5. `scripts/leaderboard.py` writes `data/leaderboard.md` (P/L, ROI, record, Brier calibration).
6. `scripts/dashboard_data.py` writes `data/dashboard/*.json`, which the runner uploads to the
   [dashboard](https://claude.ai/artifact/4VHrzZa1pbBpQTGEw42c9C) (live bets, history, value over time).
   The page itself is `dashboard/index.html`, stored in the dashboard, not served from here.

The daily runner prompt is `prompts/daily.md`. Schedule: 9am US Central (8:49, to avoid the top-of-hour rush), via a scheduled task that wakes a dedicated cloud runner session pinned to this branch.

## Bankroll competition
A second competition runs on the same daily slate with its own players (`bankroll` in `config.json`):
Opus high, Opus low, Fable high and Fable low.
- Each starts with **$10**. Winnings stay in the bankroll and can be bet later; losses come out of it.
- Players choose each stake (at least $1). Today's stakes can't exceed the available bankroll
  (settled bankroll; all of a day's games settle before the next run, so normally nothing is
  still riding). Up to 8 picks a day, one per game.
- Each player must stake at least **$1 a day** (or everything left, if less). Staking less forfeits
  the shortfall as a loss.
- A player below $1 with nothing riding is out.
- Ranked by bankroll in `data/bankroll/leaderboard.md`; `data/bankroll/standings.json` holds each
  player's bankroll, riding and available amounts. Not mirrored to Kalshi.
- Record with `python3 scripts/record_picks.py <player> <picks.json> --competition bankroll`.
  Player prompt: `prompts/bankroll_player.md`.

## Double elimination
A third competition on the same slate (`double_elim` in `config.json`): high and low effort of Opus,
Sonnet, Haiku and Fable, 8 players.
- Each starts with **$2** and makes **exactly one bet a day**, at decimal odds of at least **1.80**
  (about −125 or longer), so a win returns at least 1.8× the stake.
- The stake is set by the rules: **half the bankroll** at the start or after a win, **all of it** after
  a loss (rounded to the cent). So two losses in a row leave $0 and the player is **out**.
  A push changes nothing.
- Betting is required: no valid pick on a day with games forfeits that day's stake, counted as a loss.
  A player whose last bet hasn't settled sits the day out with no forfeit.
- Eliminated players stop betting but keep their history; their chart line ends at $0 on the day
  they went out. Survivors rank by bankroll, then the eliminated by how long they lasted.
- State (bankroll, last result, next stake, out) is replayed from `data/double_elim/ledger.csv` each
  run into `data/double_elim/standings.json`; nothing is edited by hand.
- Mirrored onto Kalshi demo like the flat competition, each bet at its own stake (whole contracts,
  so slightly under), sharing the same daily and total caps. The paper ledger stays the score.
- Record with `python3 scripts/record_picks.py <player> <picks.json> --competition double_elim`.
  Player prompt: `prompts/double_elim_player.md`.

## Files
| Path | What |
|---|---|
| `config.json` | players, stake, pick cap, sports, markets, preferred bookmakers |
| `data/slates/` | daily odds snapshots |
| `data/picks/<date>/<player>.json` | each player's accepted and rejected picks |
| `data/ledger.csv` | every bet and its result (source of truth) |
| `data/leaderboard.md` | standings |
| `data/bankroll/` | bankroll competition: `picks/`, `ledger.csv`, `leaderboard.md`, `standings.json` |
| `data/double_elim/` | double elimination: same layout as `data/bankroll/` |

## Setup
- Environment secret `ODDS_API_KEY` (free key from the-odds-api.com; ~7 sports × 1 call/day + scores fits the free tier).
- Optional: Google Sheets connector granted to the scheduled task to mirror the ledger to
  "Gemini vs Claude - Daily Betting Showdown".

## Running by hand
```
cd scripts
python3 grade.py
python3 snapshot_odds.py
python3 record_picks.py opus-max picks.json
python3 leaderboard.py
```

## Kalshi (demo)
`scripts/kalshi.py` mirrors validated flat and double-elimination ledger picks onto Kalshi
(`data/kalshi_orders.csv` has a `competition` column; older rows without one are flat). It is the only code that holds the key.
- `check` (auth + balance), `place` (today's picks), `settle` (fills + results) → `data/kalshi_orders.csv`.
- Mapping: ML → YES on "Team wins"; draw → YES on "Tie"; favorite −X → YES on "Team wins by over X";
  underdog +X → NO on the favorite's "wins by over X"; Over/Under X → YES/NO on "Over X".
- Skips (logged with a reason) when there's no matching market or strike, no usable ask, the ask is more
  than `max_slippage` worse than the slate price, or a cap would be exceeded.
- Config `kalshi`: `env` (`demo`/`prod`), `dry_run`, `max_slippage`, `daily_cap`, `total_cap` (dollars).
- Secrets: `KALSHI_API_KEY_ID`, `KALSHI_PRIVATE_KEY_B64` (base64 of the private key PEM).
- The paper ledger stays the tournament score; Kalshi shows what actually executes. Real money means
  `env: prod` with production keys, and should only be switched deliberately.

Sportsbooks such as DraftKings or FanDuel are not supported: they have no betting API and ban automation.
