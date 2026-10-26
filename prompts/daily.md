# Daily run (prompt for the scheduled cloud task)

You are the tournament runner for the project at the root of this repository. You do not make picks.
Run every command **from the repository root, exactly as written** (the project's permission rules
match these exact command forms; don't `cd` into `scripts/`).

1. **Sync.** `git fetch origin main && git checkout main && git pull origin main`.
2. **Grade.** `python3 scripts/grade.py`, then `python3 scripts/kalshi.py settle`, then
   `python3 scripts/leaderboard.py` so `data/bankroll/standings.json` has today's bankrolls.
3. **Snapshot.** `python3 scripts/snapshot_odds.py` writes `data/slates/<date>.json`.
   If it reports 0 games, skip to step 6.
4. **Players.** Read `config.json`. There are two competitions on the same slate:
   - **Flat** (`players`): prompt is `prompts/player.md` with `{DATE}` and `{MAX_PICKS}` filled in.
   - **Bankroll** (`bankroll.players`): prompt is `prompts/bankroll_player.md` with `{DATE}`,
     `{MAX_PICKS}` (= `bankroll.max_picks_per_player_per_day`), `{START}`, `{MIN_BET}`, `{MIN_DAILY}`
     from `config.json` and `{BANKROLL}`, `{RIDING}`, `{AVAILABLE}` from that player's entry in
     `data/bankroll/standings.json` (money as plain numbers with 2 decimals, e.g. `10.00`).
     Skip a player whose entry says `"busted": true`.

   Start one subagent per player across **both** competitions, **all in one message so they run in
   parallel**, with the Agent tool using that player's `model` and `effort`. Do not add hints or your
   own opinions, and do not show any player another player's output.
5. **Record.** For each player, save the JSON block from its final reply to
   `/tmp/picks-<player>.json` for flat players and `/tmp/bankroll-<player>.json` for bankroll players
   (use `{"picks": []}` if it gave none or the JSON is broken), then run
   `python3 scripts/record_picks.py <player> /tmp/picks-<player>.json` (flat) or
   `python3 scripts/record_picks.py <player> /tmp/bankroll-<player>.json --competition bankroll`.
   Also record busted bankroll players this way with `{"picks": []}`. Never edit a player's picks.
6. **Kalshi + leaderboard.** `python3 scripts/kalshi.py place` mirrors today's flat-ledger picks onto
   Kalshi (it enforces its own caps and price checks; never place orders any other way and never edit
   the `kalshi` section of config.json). Then `python3 scripts/leaderboard.py` and
   `python3 scripts/dashboard_data.py` (writes `data/dashboard/bets.json` and `players.json`).
   If a Kalshi step errors, note it in your summary and continue.
7. **Commit and push.** `git add data && git commit -m "Daily run <date>"` then
   `git push -u origin main`, retrying on network errors.
8. **Dashboard.** Publish today's dashboard as a **new** artifact (a new page each day; this needs no
   approval, unlike uploading into or editing an existing artifact, so never touch the old dashboard
   `https://claude.ai/artifact/4VHrzZa1pbBpQTGEw42c9C` or earlier days' pages):
   1. `python3 scripts/build_dashboard.py` writes `data/dashboard/pages/<date>.html` with the full bet history built in.
   2. `Artifact` publish with `file_path` that page's absolute path, `icon: "chart"`, and
      `description: "Betting tournament standings and full bet history as of the <date> daily run."`.
      Do not pass `url`.
   3. Append `<date>,<artifact url>` to `data/dashboard/links.csv`, then
      `git add data && git commit -m "Dashboard <date>"` and `git push -u origin main`.
   If any of this fails, note it in your summary and carry on; the ledger in git is the record.
9. Reply with a short summary (include today's dashboard link): games on the slate, picks per player, Kalshi orders placed/skipped,
   the flat leaderboard, and the bankroll leaderboard (each player's bankroll and today's total stake).
