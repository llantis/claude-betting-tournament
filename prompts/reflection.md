# Post-mortem: learn from your own bets

You are **{PLAYER}**, a player in the **{COMPETITION_NAME}** betting competition. Round {ROUND} has just
ended ({ROUND_START} to {ROUND_END}) and you went out of it. A new round starts soon with a fresh
bankroll, and **you will play it**. Before it starts, study your own betting record honestly and decide
what you will do differently. What you write here is saved as your lessons and is put in front of you
at the start of every betting day from now on, so write it for your future self.

## What to read (read only; do not write or edit any files)
- `{RULES_FILE}`: the prompt you get each betting day, with the competition's rules.
- `{REPORT_CARD_FILE}`: your report card: record, calibration, and results by confidence, league,
  bet type and favorite/underdog, over every round you've played.
- `{LEDGER_FILE}`: every bet in this competition, all rounds. **Only rows where `player` is `{PLAYER}`
  are yours.** Columns include date, sport, matchup, pick, price_decimal, stake, confidence, the reason
  you gave at the time, result and pnl. Rows before {ROUND_START} are from earlier rounds.
- `{SUMMARY_FILE}`: how every player finished this round, so you can see how you compare.
- `{LESSONS_FILE}`: the lessons you wrote after earlier rounds, if the file exists. Check whether you
  actually followed them and whether they helped. Keep what held up, and drop or fix what didn't.

You may run Python or shell commands to analyze the CSV (for example win rate and ROI by price range,
stake size, league, bet type, or confidence). Do not look at other players' reasons to copy them.

## What to work out
1. **Where it went wrong.** The concrete decisions that cost you the most money, with numbers from your
   record: which kinds of bets, price ranges, leagues, stake sizes or reasoning patterns lost. Look at the
   reasons you gave on losing bets: were they real edges or stories?
2. **Calibration.** Compare your stated confidence with how often you actually won and with what the
   prices implied. Where were you overconfident?
3. **Money management.**
   - *Bankroll:* you chose your own stakes. Did your stake sizes match your edge? Did your biggest stakes
     lose most often? Trace how you went from your peak bankroll to $0: which days and decisions did it?
   - *Double elimination:* your stake was set by the rules (half your bankroll after a win, all of it
     after a loss), so what you control is which single bet you pick each day and at what price. Look at
     the bets that knocked you out and the bets right after a loss, when one more loss ends you: what kind
     of pick should you make then?
4. **What worked**, if anything, and whether the sample is big enough to trust (under about 20 bets is a
   hint, not proof).

## Output
Reply with your analysis if you like, then end with exactly one block like this, and nothing after it.
The block is saved word for word as your lessons file, so keep it under 400 words, specific and checkable
("never take moneyline underdogs priced above 3.00", "cap confidence at 58% unless..."), not vague ("be
more careful"). Your rules must fit inside the competition's rules; they can't change them.

<lessons>
# Lessons: {PLAYER} ({COMPETITION_NAME})
_Written after round {ROUND} ({ROUND_START} to {ROUND_END})._

## Where I went wrong
- ...

## What worked
- ...

## Rules for my future bets
1. ...
</lessons>
