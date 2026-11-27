Post-mortem for haiku-high, double elimination, round 2 (2026-11-09 to 2026-11-23). No files were written or edited. No lessons file existed before this one (data/lessons/double_elim/haiku-high.md was absent).

Record (all rounds, 5 bets from data/double_elim/ledger.csv): 1-4, staked $5.93, P/L -$4.00, ROI -67%. Round 1 (10-28 to 10-30) bankroll path: $2.00, win Washington +10.5 at 1.93 to $2.93, loss CBJ ML at 3.05 (stake $1.47) to $1.46, loss Knicks ML at 1.80 (all-in $1.46) to $0. Round 2: loss NYR ML at 2.30 ($1.00) to $1.00, loss 76ers ML at 1.99 (all-in $1.00) to $0. Round 2 finished 8th of 8 (out on 11-10, 0-2). Round 2 Brier was 0.237, the second-best of the eight players this round.

Where it went wrong:
- Every bet had a thin claimed edge. Confidence beat the implied price by 4.2, 3.2, 1.4, 0.5 and 2.7 points. The four losses were 0.5 to 3.2 points over the price, which is inside the noise of my own estimates.
- NYR: my own no-vig estimate (41-42%) was below the 43.5% implied price, and I still bet it. That breaks the prompt's rule to say why the price is wrong.
- Both knockout bets were all-in moneyline favorites (Knicks 1.80, 76ers 1.99). Their reasons were "home court" and "stronger side". I found no injury or lineup news for either and bet anyway.
- CBJ at 3.05 was a longshot moneyline justified by season strength alone.
- Calibration: average confidence 49% against a 20% win rate, a 29-point gap. Five bets is too few to prove miscalibration (1 win in 5 at a fair 50% happens about 19% of the time), but the reasons were thin.

What worked:
- The one win (Washington +10.5, 1.93) rested on named, checkable facts: a team's ATS record, a blown 24-point lead and a possible player return. This is one bet, so it is a hint, not proof.
- Confidence near 50% kept the Brier score reasonable. Limiting damage is not the same as winning.

Money management: each round's knockout came from the all-in bet after the first loss. The choice that matters on those days is the pick itself: a verified, named edge at 1.80 to 2.20, not a longshot or a home-court story.

<lessons>
# Lessons: haiku-high (double elimination)
_Written after round 2 (2026-11-09 to 2026-11-23)._

## Where I went wrong
- My edges were tiny and mostly imaginary. Confidence beat the implied price by only 0.5 to 4.2 points on all five bets. The four losses were 0.5 to 3.2 points over the price.
- NYR (round 2, day 1): my own no-vig estimate was 41-42% against 43.5% implied, and I still bet it.
- Both knockouts were all-in moneyline favorites (Knicks 1.80, 76ers 1.99). Their reasons were "home court" and "stronger side", and I found no injury news for either.
- The round 1 CBJ bet was a 3.05 moneyline longshot on season strength alone. It lost.
- Record 1-4, ROI -67%, average confidence 49% against a 20% win rate. Five bets is noise, but the reasons were thin.

## What worked
- The one win (Washington +10.5 at 1.93) rested on named, checkable facts: a team's ATS record, a blown 24-point lead, a possible player return. One bet is a hint, not proof.
- Confidence stayed near 50%, so my Brier score (0.225 overall, 0.237 in round 2, second-best of eight this round) held up. Limiting damage is not the same as winning.

## Rules for my future bets
1. Pick only options where my confidence beats 1/price by at least 5 points. If none does, pick the largest verified gap and say so in the reason.
2. Never pick an option where my own fair probability is at or below 1/price.
3. A gap counts only with a named, verified fact: injury, lineup, rest, ATS or form record, line move. "Home court", "stronger team" and "favored" do not count.
4. After a loss (all-in day), pick a price of 1.80 to 2.20 backed by a verified fact. Never a moneyline priced 3.00 or more.
5. Before picking, search injury and lineup news for each candidate. "No news found" is not a reason to bet.
6. Confidence = implied probability + verified gap, never above 0.60.
</lessons>
