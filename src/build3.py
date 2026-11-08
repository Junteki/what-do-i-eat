import html, urllib.parse, random, os
from data import FEELS, R, LISTS, MENTION_ONLY
MENTION_ONLY["travelwiththevees"] += ["yamaokaya", "kourakuen"]

E = html.escape
FEEL = {k: dict(name=n, emo=e, c1=a, c2=b) for k, n, e, a, b in FEELS}
HOURS = {"24": "Often 24h", "late": "Often past midnight", "std": "Shuts ~22–23"}
BASE = {"r": "rice", "n": "noodle", "o": "other", "c": "light"}
SIZE = {"s": "snack", "m": "meal", "f": "feast"}
VIBE = {"q": "quick", "s": "sit"}

rows = []
for (rid, en, jp, feel, emo, prof, order, lo, hi, hrs, flags, note) in R:
    sc = [l[rid] for l in LISTS.values() if rid in l]
    n = len(sc) + sum(rid in v for v in MENTION_ONLY.values())
    avg = (sum(sc) + 3.0) / (len(sc) + 1) if sc else None
    bands = []
    if lo <= 700: bands.append("b1")
    if lo < 2000 and hi >= 1000: bands.append("b2")
    if hi >= 2500: bands.append("b3")
    rows.append(dict(id=rid, en=en, jp=jp, feel=feel, emo=emo, base=prof[0], size=prof[1], vibe=prof[2],
                     order=order, lo=lo, hi=hi, hrs=hrs, flags=flags.split(), note=note, avg=avg, n=n, bands=bands))
key = lambda r: (-(r["avg"] if r["avg"] is not None else 3.0), -r["n"])
rows.sort(key=key)
LET = lambda s: "S" if s >= 4.2 else "A" if s >= 3.6 else "B" if s >= 2.9 else "C" if s >= 2.4 else "D"

def maps(r): return "https://www.google.com/maps/search/?api=1&amp;query=" + urllib.parse.quote(r["jp"].split(" / ")[0])
def tile(r, cls="tile"):
    f = FEEL[r["feel"]]
    return f'<div class="{cls}" style="background:linear-gradient(135deg,{f["c1"]},{f["c2"]})"><span>{r["emo"]}</span></div>'
def badge(r):
    if r["avg"] is None: return '<span class="bdg tN">NEW</span>'
    l = LET(r["avg"]); return f'<span class="bdg t{l}">{l}</span>'
def meta(r):
    bits = [f'¥{r["lo"]:,}–{r["hi"]:,}', HOURS[r["hrs"]]]
    if r["note"]: bits.append(r["note"])
    return " · ".join(bits)

# ---------------- Browse cards ----------------
def card(r):
    cls = ["card", "f-" + r["feel"], "h" + r["hrs"]] + r["bands"] + r["flags"]
    tags = []
    if "spicy" in r["flags"]: tags.append('<span class="chip hot">🌶️ Spicy</span>')
    if "solo" in r["flags"]: tags.append('<span class="chip">Solo OK</span>')
    rank = (f'Consensus {LET(r["avg"])} · {r["n"]}/8 lists' if r["avg"] is not None
            else (f'Unranked · in {r["n"]}/8 lists' if r["n"] else 'Added: not in your lists'))
    return f'''<div class="{' '.join(cls)}">{tile(r)}<div class="cb">
<div class="ct"><b>{E(r["en"])}</b>{badge(r)}</div><div class="cj">{E(r["jp"])}</div>
<div class="co">{E(r["order"])}</div><div class="cm">{E(meta(r))}</div>
<div class="cf">{''.join(tags)}<span class="rk">{rank}</span><a class="mp" href="{maps(r)}">Map</a></div></div></div>'''

# ---------------- Spinners ----------------
NS = set()
def weight(r):
    if r["avg"] is None: return 1
    return 3 if r["avg"] >= 4.2 else 2 if r["avg"] >= 3.6 else 1
def spinner(items, render, sid, empty, seed, kind):
    sl = []
    for r in items: sl += [r] * weight(r)
    random.Random(seed).shuffle(sl)
    n = len(sl)
    if not n:
        return f'<div class="sp {kind}" id="{sid}"><div class="it none">{empty}</div></div>'
    T = n * 0.06
    inner = "".join(f'<div class="it">{render(r)}</div>' for r in sl)
    return f'<div class="sp {kind}" id="{sid}"><div class="strip" style="animation:roll {T:.2f}s steps({n}) infinite">{inner}</div></div>'

GUT = '<div class="gut">🪙 <b>Gut check:</b> relieved → go. A little “ugh” → spin again.</div>'
def hero(r):
    return f'''{tile(r, "htile")}<div class="hb"><div class="hk">You’re eating</div><div class="hn">{E(r["en"])}</div>
<div class="hj">{E(r["jp"])}</div><p>{E(r["order"])}</p><div class="hm">{E(meta(r))}</div>
<a class="btn" href="{maps(r)}">📍 Find the nearest one</a>{GUT}</div>'''
def mini(r):
    return f'''{tile(r, "mtile")}<div class="mb"><b>{E(r["en"])}</b> <span class="mj">{E(r["jp"])}</span>
<div class="mo">{E(r["order"])}</div><div class="mm">{E(meta(r))} · <a href="{maps(r)}">Map</a></div></div>'''

SPIN_FEELS = [("all", "Anything", "🎲")] + [(k, FEEL[k]["name"], FEEL[k]["emo"]) for k, *_ in FEELS] + [("spicy", "Spicy", "🌶️")]
def spin_pool(fk, tk):
    out = []
    for r in rows:
        if fk == "spicy" and "spicy" not in r["flags"]: continue
        if fk not in ("all", "spicy") and r["feel"] != fk: continue
        if tk == "late" and r["hrs"] == "std": continue
        out.append(r)
    return out
spin_html, spin_css = [], []
for fk, *_ in SPIN_FEELS:
    for tk in ("any", "late"):
        sid = f"sp-{fk}-{tk}"
        spin_html.append(spinner(spin_pool(fk, tk), hero, sid,
                         '<div class="hb"><div class="hn">Nothing open late here</div><p>Switch to “Any time” or pick another feel.</p></div>', sum(map(ord, sid)), "hero"))
        spin_css.append(f'body:has(#sf-{fk}:checked):has(#st-{tk}:checked) #{sid}{{clip-path:inset(0 0 0 0);pointer-events:auto}}')

P3 = [("safe", "🛟 Safe bet", lambda r: r["avg"] is not None and r["avg"] >= 3.6),
      ("wild", "🃏 Wildcard", lambda r: r["avg"] is None or r["avg"] < 3.6),
      ("treat", "👑 Treat yourself", lambda r: r["hi"] >= 2500 or r["feel"] in ("sweet",))]
p3_html, p3_css = [], []
for pk, lab, fn in P3:
    inner = ""
    for tk in ("any", "late"):
        pool = [r for r in rows if fn(r) and (tk == "any" or r["hrs"] != "std")]
        sid = f"p3-{pk}-{tk}"
        inner += spinner(pool, mini, sid, '<div class="mb">Nothing late in this slot.</div>', sum(map(ord, sid)), "mini")
        p3_css.append(f'body:has(#pt-{tk}:checked) #{sid}{{clip-path:inset(0 0 0 0);pointer-events:auto}}')
    p3_html.append(f'<div class="slot"><div class="slab">{lab}</div><div class="reel"><div class="ph">?</div>{inner}</div></div>')

kf = "" and "".join(f'@keyframes k{n}{{0%{{visibility:visible}}{min(100/n*1.03,100):.4f}%{{visibility:hidden}}100%{{visibility:hidden}}}}' for n in sorted(NS))

# ---------------- Quiz ----------------
Q1 = [("r", "🍚", "Rice"), ("n", "🍜", "Noodles"), ("o", "🥩", "Meat, bread, other"), ("c", "☕️", "Coffee or sweet")]
Q2 = [("s", "🤏", "Snack"), ("m", "🍽️", "Proper meal"), ("f", "🐷", "Feast")]
Q3 = [("q", "⚡️", "Quick, solo-ish"), ("s", "🛋️", "Sit and linger")]
quiz_res, quiz_css = [], []
for a, *_ in Q1:
    for b, *_ in Q2:
        for c, *_ in Q3:
            pool = [r for r in rows if r["base"] == a]
            exact = [r for r in pool if r["size"] == b and r["vibe"] == c]
            near = [r for r in pool if r["size"] == b and r not in exact]
            far = [r for r in pool if r not in exact and r not in near and r["vibe"] == c]
            picks, feels = [], set()
            for grp in (exact, near, far, pool):
                for r in sorted(grp, key=key):
                    if len(picks) == 3: break
                    if r in picks: continue
                    if r["feel"] in feels and any(x["feel"] != r["feel"] for x in grp if x not in picks and x["feel"] not in feels):
                        continue
                    picks.append(r); feels.add(r["feel"])
            for grp in (exact, near, far, pool):
                for r in sorted(grp, key=key):
                    if len(picks) < 3 and r not in picks: picks.append(r)
            rid = f"qr-{a}{b}{c}"
            medals = ["🥇", "🥈", "🥉"]
            items = "".join(f'<div class="qi"><span class="md">{medals[i]}</span>{mini(r)}</div>' for i, r in enumerate(picks))
            quiz_res.append(f'<div class="qres" id="{rid}"><div class="sh">Your match</div><div class="grp">{items}</div></div>')
            quiz_css.append(f'body:has(#q1-{a}:checked):has(#q2-{b}:checked):has(#q3-{c}:checked) #{rid}{{display:block}}')

def qopts(name, opts):
    return "".join(f'<input type="radio" name="{name}" id="{name}-{v}"><label for="{name}-{v}"><span class="qe">{e}</span>{t}</label>' for v, e, t in opts)

# ---------------- Browse filter CSS ----------------
br_css = []
for k, *_ in FEELS:
    br_css.append(f'body:has(#bf-{k}:checked) .card:not(.f-{k}){{display:none}}')
    br_css.append(f'body:has(#v-{k}:checked) .card.f-{k}{{display:none}}')
br_css += ['body:has(#bt-late:checked) .card.hstd{display:none}',
           'body:has(#bt-24:checked) .card:not(.h24){display:none}',
           'body:has(#bb-b1:checked) .card:not(.b1){display:none}',
           'body:has(#bb-b2:checked) .card:not(.b2){display:none}',
           'body:has(#bb-b3:checked) .card:not(.b3){display:none}',
           'body:has(#bx-solo:checked) .card:not(.solo){display:none}',
           'body:has(#bx-spicy:checked) .card:not(.spicy){display:none}']

def chips(name, opts, kind="radio", first=True):
    return "".join(f'<input type="{kind}" name="{name}" id="{name}-{v}"{" checked" if (kind=="radio" and first and i==0) else ""}><label for="{name}-{v}">{t}</label>'
                   for i, (v, t) in enumerate(opts))
def seg(name, opts):
    return f'<div class="seg">{chips(name, opts)}</div>'

feel_opts = [("all", "Anything")] + [(k, f'{FEEL[k]["emo"]} {FEEL[k]["name"]}') for k, *_ in FEELS]
spin_chips = chips("sf", [(k, f"{e} {n}") for k, n, e in SPIN_FEELS])
veto_chips = chips("v", [(k, f'✕ {FEEL[k]["name"]}') for k, *_ in FEELS], "checkbox")

ranked = [r for r in rows if r["avg"] is not None and r["n"] >= 4][:5]
medal = ["🥇", "🥈", "🥉", "4", "5"]
board = "".join(f'<div class="row"><span class="ri">{medal[i]}</span>{tile(r, "stile")}<div class="rt"><b>{E(r["en"])}</b><small>{E(r["jp"])} · {r["n"]}/8 lists</small></div><a class="mp" href="{maps(r)}">Map</a></div>'
                for i, r in enumerate(ranked))

MODES = [("spin", "⚡️", "#ff9500", "Just pick for me", "Late-night decision fatigue is real. Hand it to the dice."),
         ("three", "🃏", "#af52de", "Give me 3, I’ll choose", "Three options beat thirty: less choice, happier with the pick."),
         ("quiz", "🔀", "#007aff", "Ask me 3 quick questions", "Small this-or-that steps instead of one big choice."),
         ("browse", "🙅", "#ff3b30", "I only know what I DON’T want", "Veto feels until something's left (elimination by aspects)."),
         ("browse", "🧐", "#34c759", "Show me everything", "Maximiser mode: filter, compare, take your time.")]
mode_rows = "".join(f'<label class="row" for="t-{t}"><span class="ico" style="background:{c}">{e}</span><div class="rt"><b>{h}</b><small>{s}</small></div><span class="chev">›</span></label>'
                    for t, e, c, h, s in MODES)

N_CH = len(rows)
TPL = open("tpl.html").read()
page = (TPL.replace("%%N%%", str(N_CH))
        .replace("%%MODES%%", mode_rows).replace("%%BOARD%%", board)
        .replace("%%SPINCHIPS%%", spin_chips).replace("%%SPINS%%", "".join(spin_html))
        .replace("%%P3%%", "".join(p3_html))
        .replace("%%Q1%%", qopts("q1", Q1)).replace("%%Q2%%", qopts("q2", Q2)).replace("%%Q3%%", qopts("q3", Q3))
        .replace("%%QRES%%", "".join(quiz_res))
        .replace("%%BF%%", chips("bf", feel_opts)).replace("%%BT%%", seg("bt", [("any", "Any time"), ("late", "Late"), ("24", "24h")]))
        .replace("%%BB%%", seg("bb", [("any", "Any ¥"), ("b1", "< ¥1k"), ("b2", "¥1–2k"), ("b3", "Splurge")]))
        .replace("%%VETO%%", veto_chips).replace("%%CARDS%%", "".join(card(r) for r in rows))
        .replace("%%DYNCSS%%", "\n".join(spin_css + p3_css + quiz_css + br_css) + "\n" + kf))
os.makedirs("out", exist_ok=True)
open("out/what-do-i-eat.html", "w").write(page)
print(N_CH, "chains;", len(page)//1024, "KB; ranked:", sum(r["avg"] is not None for r in rows))
print([r["en"] for r in ranked])

# ---------------- Simple version ----------------
SHORT = {"jp": "Japanese", "ramen": "Ramen", "sushi": "Sushi", "western": "Western", "italian": "Italian",
         "chinese": "Chinese", "curry": "Curry", "grill": "Grill", "izakaya": "Izakaya", "coffee": "Coffee",
         "sweet": "Sweet", "konbini": "Konbini"}
grid_opts = [("all", "🎲", "Anything")] + [(k, FEEL[k]["emo"], SHORT[k]) for k, *_ in FEELS] + [("spicy", "🌶️", "Spicy")]
grid = "".join(f'<input type="radio" name="sf" id="sf-{k}"{" checked" if k=="all" else ""}><label for="sf-{k}"><span>{e}</span>{t}</label>' for k, e, t in grid_opts)
s_html, s_css = [], []
for fk, *_ in grid_opts:
    for tk in ("any", "late"):
        sid = f"sp-{fk}-{tk}"
        s_html.append(spinner(spin_pool(fk, tk), hero, sid,
            '<div class="hb"><div class="hn">Nothing open late here</div><p>Switch to “Any time” or pick another feel.</p></div>', sum(map(ord, sid)) + 11, "hero"))
        s_css.append(f'body:has(#sf-{fk}:checked):has(#st-{tk}:checked) #{sid}{{clip-path:inset(0 0 0 0);pointer-events:auto}}')
DET = "https://github.com/Junteki/what-do-i-eat#readme"
simple = (open("tpl_simple.html").read().replace("%%GRID%%", grid).replace("%%SPINS%%", "".join(s_html))
          .replace("%%DYNCSS%%", "\n".join(s_css)).replace("%%N%%", str(N_CH)).replace("%%DETAILED%%", DET))
open("out/what-do-i-eat-simple.html", "w").write(simple)
os.replace("out/what-do-i-eat.html", "out/what-do-i-eat-detailed.html")
print("simple", len(simple)//1024, "KB")
