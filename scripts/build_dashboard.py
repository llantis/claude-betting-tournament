"""Build a standalone dashboard page with today's data built in: data/dashboard/pages/<date>.html.

The daily run publishes this page as a new artifact each day. Publishing a new page needs no
approval, unlike uploading files into the old dashboard or editing its datasets. Every page holds
the full bet history from both ledgers, and each day's page is kept in git.

It wraps dashboard/index.html (the body of the old Dashboard-type page) with the theme tokens, d3,
and a small stand-in for the `dash` API that page expects, so the page itself stays unchanged.
"""
import argparse
import json

from common import DATA, ROOT, today

OUT = DATA / "dashboard" / "pages"

HEAD = """<title>Betting tournament</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
  /* One column of cards on a quiet ground; the table and chart carry the page. */
  :root {
    --color-bg: #f6f7f9; --color-panel: #ffffff; --color-fg: #1b1f27; --color-fg-muted: #5d6573;
    --color-border-line: #dde1e7; --color-ok: #1f7a4d; --color-bad: #b4372f; --color-warn: #a86a00;
    --cds-border: var(--color-border-line); --cds-surface-popover: var(--color-panel);
    --cds-text-secondary: var(--color-fg-muted); --cds-shadow-popover: 0 4px 16px rgb(20 24 32 / .12);
    --cds-chart-grid: #e7eaef; --cds-chart-axis: #9aa2ae; --cds-chart-reference: #b8bfca;
    --font-anthropic-sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --font-anthropic-serif: Georgia, "Times New Roman", serif;
    --cds-font-size-title: 1.75rem; --cds-font-size-heading: 1.0625rem; --cds-font-size-body: .875rem;
    --cds-font-size-caption: .75rem; --cds-font-weight-medium: 600;
    --cds-gap-xs: .25rem; --cds-gap-sm: .5rem; --cds-gap-md: 1rem; --cds-gap-lg: 1.5rem;
    --cds-pad-xs: .25rem; --cds-pad-sm: .5rem; --cds-pad-md: .75rem; --cds-pad-lg: 1.25rem;
    --cds-radius: 8px; --cds-dur-slow: .3s;
  }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
    --color-bg: #12151b; --color-panel: #1a1e26; --color-fg: #e8ebf0; --color-fg-muted: #9aa3b2;
    --color-border-line: #2c323d; --color-ok: #5cc48d; --color-bad: #ef7a70; --color-warn: #e2a93b;
    --cds-chart-grid: #262b35; --cds-chart-axis: #6b7383; --cds-chart-reference: #4a5160;
    --cds-shadow-popover: 0 4px 16px rgb(0 0 0 / .4); color-scheme: dark;
  } }
  :root[data-theme="dark"] {
    --color-bg: #12151b; --color-panel: #1a1e26; --color-fg: #e8ebf0; --color-fg-muted: #9aa3b2;
    --color-border-line: #2c323d; --color-ok: #5cc48d; --color-bad: #ef7a70; --color-warn: #e2a93b;
    --cds-chart-grid: #262b35; --cds-chart-axis: #6b7383; --cds-chart-reference: #4a5160;
    --cds-shadow-popover: 0 4px 16px rgb(0 0 0 / .4); color-scheme: dark;
  }
  body { background: var(--color-bg); color: var(--color-fg); font-family: var(--font-anthropic-sans);
    padding-block: 1.5rem; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
  .tb { max-width: 72rem; margin: 0 auto; }
  .tb .tb-table td:not(.why) { white-space: nowrap; }
  .tb-asof { margin: 0; color: var(--color-fg-muted); font-size: var(--cds-font-size-caption); }
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
"""

# Stand-in for the Dashboard type's `dash` API: static data, derived calcs, and a page param.
SHIM = """<script>
(() => {
  const raw = __DATA__;
  const calcs = {}, cache = {}, subs = [];
  let params = {};
  const get = (name) => {
    if (name in raw) return raw[name];
    if (!(name in cache)) cache[name] = calcs[name].fn(...calcs[name].inputs.map(get));
    return cache[name];
  };
  const fire = () => subs.forEach((f) => f());
  window.dash = {
    calc: (name, spec) => { calcs[name] = spec; },
    data: (name) => { try { return { status: 'ok', data: get(name) }; } catch (e) { console.error(e); return { status: 'error' }; } },
    onData: (f) => { subs.push(f); if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', f); else f(); },
    params: () => params,
    setParams: (p) => { params = { ...params, ...p }; fire(); },
    setLink: (id) => { try { history.replaceState(null, '', '#' + id); } catch (e) {} },
    colors: ['#3b6fd8', '#d1603d', '#2f9a6a', '#8a5cc7', '#c79a1f', '#d14b8f', '#3a9fb5', '#7b8794'],
  };
  window.addEventListener('resize', () => fire());
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=today())
    args = ap.parse_args()
    data = {name: json.loads((DATA / "dashboard" / f"{name}.json").read_text()) for name in ("bets", "players")}
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    body = (ROOT / "dashboard" / "index.html").read_text()
    asof = f'<p class="tb-asof">Data as of the {args.date} daily run.</p>\n'
    body = body.replace('<h1 id="title">Betting tournament</h1>', '<h1 id="title">Betting tournament</h1>\n      ' + asof, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"{args.date}.html"
    out.write_text(HEAD + SHIM.replace("__DATA__", blob) + body)
    print(f"dashboard page: {len(data['bets'])} bets -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
