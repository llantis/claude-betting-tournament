## Analysis

**Record.** Over two rounds I made 20 bets: 11-9, -$4.00, ROI -10%. Round 1 lasted 5 bets (Oct 28 to Nov 1) and ended with two losses in a row. In round 2 I went 9-6, peaked at $7.48 and was knocked out on Nov 23, the last day. That still ranked 1st of 8, because I survived longest. No earlier lessons file existed.

**1. Where it went wrong.** The costly bets were the days I backed a story instead of the slate's most likely winner. I checked each slate by taking out the bookmaker's margin from two-sided markets.
- Oct 31: Charlotte ML at 2.00, 51% confidence, a "young core finished strong" story. Lost. Options at 53.2% were on the board.
- Nov 1: the all-in bet after that loss. I took Under 41.5 at 1.85 with 55% confidence, based on line movement and under-trend stats. Lost, and I was out. Rangers ML at 53.2% was available.
- Nov 9: Vikings +3 at 2.02, 46% confidence, arguing that "push equity cuts risk". Lost. Bills -3 at 52.6% was available, and the loss put me all-in on day 2.
- Off-rule bets overall: 2-4, and both underdogs at 2.00+ lost. From Nov 10 on, I took the highest margin-free probability every day: 9-5 (64%) against about 53% expected.
- The round-2 knockout was two tied-top NHL Under 6.5 bets at 1.80. These were correct picks that lost; that is variance, not a decision error. NHL (4-5) and totals (3-5) look bad, but at 8-9 bets that is noise. I also padded reasons with "NHL is my best league", which was a story.

**2. Calibration.** Average stated confidence was 53% and actual wins were 55%, with a Brier score of 0.243. Confidence set equal to the margin-free probability was honest. My only bets at 46% and 55% both lost; those were the times I moved away from the market's number.

**3. Money management.** The stake is fixed, so every loss counts the same for survival. The best I can do each day is pick the highest win probability. After a loss, the bets that followed this rule went 4-0. The one that didn't (Nov 1, a narrative under) ended round 1.

**4. What worked.** The "most likely winner" rule. 14 bets is a hint, not proof, but it is the only approach with sound logic behind it.

Data trap: the slate only lists prices of 1.80 or longer, and soccer moneylines have three outcomes. Treating two listed soccer options as a pair gives fake 55-71% "draw" probabilities.

<lessons>
# Lessons: opus-high (double elimination)
_Written after round 2 (2026-11-09 to 2026-11-23)._

## Where I went wrong
- Story bets lost: Charlotte ML 2.00 (Oct 31), Under 41.5 on trend stats (Nov 1, knocked me out), Vikings +3 at 2.02 "push equity" (Nov 9). Each passed over a 52.6-53.2% option on the slate. Off-rule bets went 2-4, and underdogs at 2.00+ went 0-2.
- Reasons like "NHL is my best league" or "high-scoring teams" were stories, not edges.
- Round 2 ended with two correct 53.2% NHL unders losing in a row. That is variance, not a mistake.

## What worked
- Taking the slate's highest margin-free probability every day from Nov 10: 9-5 (64%) against about 53% expected, 4-0 after a loss. Rank 1 of 8 by survival. It is only 14 bets, so a hint, but the logic holds: the stake is fixed, so maximizing win chance maximizes survival.
- Confidence set to the margin-free probability was well calibrated (Brier 0.243).

## Rules for my future bets
1. Every day, compute the margin-free probability only for two-sided markets where both sides are listed: p = (1/price) / (1/price + 1/other price). Bet the highest. Never pick an option more than 0.5 points below the slate's top.
2. Never apply that formula to soccer moneylines (three outcomes: home, draw, away). Skip soccer moneylines and draws entirely.
3. Never bet a price of 2.00 or higher unless it is the slate's top margin-free probability, which almost never happens.
4. Set confidence equal to that margin-free probability, rounded to 0.01 (usually 0.52-0.53). Never above 0.55 without a concrete, checkable fact the price misses, such as a confirmed late injury after the snapshot.
5. Line moves, under/over trends, "my best league", and push-equity arguments are not edges. They do not justify leaving rule 1.
6. After a loss (all-in day), follow rule 1 strictly. No exceptions.
7. Tiebreak among options within 0.5 points: prefer a line that can push (whole-number spread or total, e.g. NFL ±3), since a push uses up a day without risk in a fixed-length round. Otherwise pick the earliest-listed option. Do not tiebreak on league history.
8. Do not tilt away from NHL or totals because of round-2 results; 8-9 bets is noise.
</lessons>
