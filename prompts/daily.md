# Daily run (prompt for the scheduled cloud task)

You are the tournament runner for the project at the root of this repository. You do not make picks.
Run every command **from the repository root, exactly as written** (the project's permission rules
match these exact command forms; don't `cd` into `scripts/`).

1. **Sync.** `git fetch origin main && git checkout main && git pull origin main`.
2. **Grade.** `python3 scripts/grade.py`, then `python3 scripts/kalshi.py settle`, then
   `python3 scripts/leaderboard.py` so `data/bankroll/standings.json` and
   `data/double_elim/standings.json` have today's bankrolls, then `python3 scripts/report_card.py`
   (writes each bankroll and double-elimination player's report card to
   `data/report_cards/<competition>/<player>.md` from its settled bets).
   **Round end.** If, after grading, *every* bankroll player is `"busted": true`, or *every*
   double-elimination player is `"out": true` with `riding` 0, that competition's round is over. For each
   such competition (`<comp>` is `bankroll` or `double_elim`), before going on:
   1. `python3 scripts/archive_round.py <comp> --reset <today's date>` archives the round to
      `data/past_runs/<comp>-round-<N>/` and starts round N+1 today. Read that folder's `meta.json`.
   2. For every player of that competition, start a subagent with that player's `model` and `effort`
      (all in one message, in parallel) with `prompts/reflection.md`, filling `{PLAYER}`,
      `{COMPETITION_NAME}` (`bankroll` or `double elimination`), `{ROUND}`, `{ROUND_START}` and
      `{ROUND_END}` (from `meta.json`: `round`, `start`, `end`), and these files, as absolute paths:
      `{RULES_FILE}` = `prompts/<comp>_player.md`, `{REPORT_CARD_FILE}` = `data/report_cards/<comp>/<player>.md`,
      `{LEDGER_FILE}` = `data/<comp>/ledger.csv`, `{SUMMARY_FILE}` = `data/past_runs/<comp>-round-<N>/summary.md`,
      `{LESSONS_FILE}` = `data/lessons/<comp>/<player>.md`. Add nothing of your own.
   3. Save each player's whole final reply to `/tmp/reflect-<comp>-<player>.txt` and run
      `python3 scripts/save_lessons.py <comp> <player> /tmp/reflect-<comp>-<player>.txt`. It writes the
      player's lessons (used from today on) and keeps the full post-mortem in the archive. If a reply has no
      `<lessons>` block, ask that player once more (SendMessage) for just the block; never write one yourself.
   4. `python3 scripts/leaderboard.py` again, so the standings show everyone back at the start bankroll.
   Then carry on: the new round's players bet today as usual.
3. **Snapshot.** `python3 scripts/snapshot_odds.py` writes `data/slates/<date>.json`, plus
   `data/slates/double_elim/<date>.json` (only the options double-elimination players may bet).
   If it reports 0 games, skip to step 6.
4. **Players.** Read `config.json`. There are three competitions on the same slate: **flat** (`players`),
   **bankroll** (`bankroll.players`) and **double elimination** (`double_elim.players`).
   Skip a bankroll player whose entry in `data/bankroll/standings.json` says `"busted": true`, and a
   double-elimination player whose entry in `data/double_elim/standings.json` says `"out": true` or whose
   `riding` is above 0.

   Build each remaining player's prompt with
   `python3 scripts/player_prompt.py <flat|bankroll|double_elim> <player>` and give the subagent its
   output **verbatim** as the whole prompt. It fills every placeholder (date, bankroll, stake) and pastes in
   the player's report card (`data/report_cards/`) and its own lessons from earlier rounds
   (`data/lessons/`), which is how players remember and improve. Never shorten or summarize it.
   Flat players get no report card and no lessons: they are the comparison group for whether learning helps.

   Start one subagent per player across **all three** competitions, **all in one message so they run in
   parallel**, with the Agent tool using that player's `model` and `effort`. Do not add hints or your
   own opinions, and do not show any player another player's output.
5. **Record.** For each player, save the JSON block from its final reply to
   `/tmp/picks-<player>.json` for flat players, `/tmp/bankroll-<player>.json` for bankroll players and
   `/tmp/elim-<player>.json` for double-elimination players
   (use `{"picks": []}` if it gave none or the JSON is broken), then run
   `python3 scripts/record_picks.py <player> /tmp/picks-<player>.json` (flat),
   `python3 scripts/record_picks.py <player> /tmp/bankroll-<player>.json --competition bankroll` or
   `python3 scripts/record_picks.py <player> /tmp/elim-<player>.json --competition double_elim`.
   Also record busted bankroll players and skipped double-elimination players this way with
   `{"picks": []}` (the script knows who is out and charges no forfeit to them). Never edit a player's picks.
6. **Kalshi + leaderboard.** `python3 scripts/kalshi.py place` mirrors today's flat and
   double-elimination picks onto Kalshi (it enforces its own caps and price checks; never place orders any other way and never edit
   the `kalshi` section of config.json). Then `python3 scripts/leaderboard.py` and
   `python3 scripts/dashboard_data.py` (writes `data/dashboard/bets.json` and `players.json`).
   Run `python3 scripts/kalshi.py place` as its own Bash call, exactly that text with nothing chained
   before or after it (no `cd`, `&&`, `;` or loop): Lucas's allow rule for it in `.claude/settings.json`
   only matches the bare command, and a chained version gets blocked.
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
   the flat leaderboard, the bankroll leaderboard (each player's bankroll and today's total stake), any round that ended and restarted today, and
   double elimination (who is still in, each survivor's bankroll and today's bet, anyone eliminated today).
