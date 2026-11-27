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
