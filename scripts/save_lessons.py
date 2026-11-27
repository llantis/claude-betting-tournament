"""Save a player's post-mortem after a round ends.

    python3 scripts/save_lessons.py <bankroll|double_elim> <player> <reply.txt>

<reply.txt> is the player's full reply to prompts/reflection.md. The last <lessons>...</lessons> block in it
becomes data/lessons/<competition>/<player>.md, which the daily run pastes into the player's prompt as
{LESSONS} in every later round (it replaces the previous lessons; the player read those before writing).
The whole reply is kept as data/past_runs/<competition>-round-<N>/postmortems/<player>.md for the latest
archived round of that competition.
"""
import json
import re
import sys

from common import LESSONS, PAST_RUNS, ROOT, load_config


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    comp, player, reply_file = sys.argv[1:]
    cfg = load_config()
    if player not in {p["name"] for p in cfg[comp]["players"]}:
        sys.exit(f"{player} is not a {comp} player")
    reply = open(reply_file).read()
    blocks = re.findall(r"<lessons>\s*(.*?)\s*</lessons>", reply, re.S)
    if not blocks:
        sys.exit(f"no <lessons> block in {reply_file}; ask the player again rather than writing one yourself")
    lessons = blocks[-1].strip() + "\n"

    out = LESSONS / comp / f"{player}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(lessons)

    metas = [json.loads(m.read_text()) for m in PAST_RUNS.glob(f"{comp}-round-*/meta.json")]
    if metas:
        folder = PAST_RUNS / max(metas, key=lambda m: m["round"])["folder"] / "postmortems"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{player}.md").write_text(reply.strip() + "\n")
        print(f"{player}: lessons -> {out.relative_to(ROOT)}, post-mortem -> {(folder / (player + '.md')).relative_to(ROOT)}")
    else:
        print(f"{player}: lessons -> {out.relative_to(ROOT)} (no archived round to attach the post-mortem to)")


if __name__ == "__main__":
    main()
