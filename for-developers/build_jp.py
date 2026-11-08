"""Build 何食べる？ — one-file, no-JS app with Simple + Detailed modes (Japanese design)."""
import html, urllib.parse, random, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import FEELS, R, LISTS, MENTION_ONLY
MENTION_ONLY["travelwiththevees"] += ["yamaokaya", "kourakuen"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "what-do-i-eat.html")

E = html.escape
# traditional Japanese colours per feel (light, deep)
TRAD = {"jp": ("#f8c95a", "#e2a32c"), "ramen": ("#f08a5d", "#d2512f"), "sushi": ("#f6b7b0", "#e2847c"),
        "western": ("#c98a6b", "#8f4e35"), "italian": ("#a8cf8e", "#6e9b55"), "chinese": ("#ef6b5b", "#b8312a"),
        "curry": ("#e0b45c", "#b5832e"), "grill": ("#d0705f", "#93403a"), "izakaya": ("#e9a65a", "#b8742e"),
        "coffee": ("#b08b6e", "#6f4b3e"), "sweet": ("#f2bfd0", "#d98aa6"), "konbini": ("#7fa7c9", "#3d6a93")}
JPN = {"all": "おまかせ", "jp": "和食", "ramen": "ラーメン", "sushi": "寿司", "western": "洋食", "italian": "イタリアン",
       "chinese": "中華", "curry": "カレー", "grill": "焼肉・鍋", "izakaya": "居酒屋", "coffee": "珈琲", "sweet": "甘味",
       "konbini": "コンビニ", "spicy": "激辛"}
SHORT = {"all": "Anything", "jp": "Japanese", "ramen": "Ramen", "sushi": "Sushi", "western": "Western", "italian": "Italian",
         "chinese": "Chinese", "curry": "Curry", "grill": "Grill", "izakaya": "Izakaya", "coffee": "Coffee",
         "sweet": "Sweet", "konbini": "Konbini", "spicy": "Spicy"}
FEEL = {k: dict(name=n, emo=e) for k, n, e, *_ in FEELS}
HOURS = {"24": "Often 24h", "late": "Often past midnight", "std": "Shuts ~22–23"}

rows = []
for (rid, en, jp, feel, emo, prof, order, lo, hi, hrs, flags, note) in R:
    sc = [l[rid] for l in LISTS.values() if rid in l]
    n = len(sc) + sum(rid in v for v in MENTION_ONLY.values())
    avg = (sum(sc) + 3.0) / (len(sc) + 1) if sc else None
    bands = []
    if lo <= 700: bands.append("b1")
    if lo < 2000 and hi >= 1000: bands.append("b2")
    if hi >= 2500: bands.append("b3")
    rows.append(dict(id=rid, en=en, jp=jp, feel=feel, emo=emo, base=prof[0], size=prof[1], vibe=prof[2], order=order,
                     lo=lo, hi=hi, hrs=hrs, flags=flags.split(), note=note, avg=avg, n=n, bands=bands))
key = lambda r: (-(r["avg"] if r["avg"] is not None else 3.0), -r["n"])
rows.sort(key=key)
LET = lambda s: "S" if s >= 4.2 else "A" if s >= 3.6 else "B" if s >= 2.9 else "C" if s >= 2.4 else "D"

def maps(r): return "https://www.google.com/maps/search/?api=1&amp;query=" + urllib.parse.quote(r["jp"].split(" / ")[0])
def plate(r, cls="plate"):
    a, b = TRAD[r["feel"]]
    return f'<div class="{cls}" style="background:radial-gradient(circle at 35% 30%,{a},{b})"><span>{r["emo"]}</span></div>'
def stamp(r):
    if r["avg"] is None: return '<span class="stamp tN">NEW</span>'
    l = LET(r["avg"]); return f'<span class="stamp t{l}">{l}</span>'
def meta(r):
    bits = [HOURS[r["hrs"]]] + ([r["note"]] if r["note"] else [])
    return " · ".join(bits)
def yen(r): return f'¥{r["lo"]:,}–{r["hi"]:,}'

def card(r):
    cls = ["card", "f-" + r["feel"], "h" + r["hrs"]] + r["bands"] + r["flags"]
    tags = []
    if "spicy" in r["flags"]: tags.append('<span class="chip hot">🌶️ Spicy</span>')
    if "solo" in r["flags"]: tags.append('<span class="chip">Solo OK</span>')
    rank = (f'Consensus {LET(r["avg"])} · {r["n"]}/8 lists' if r["avg"] is not None
            else (f'Unranked · in {r["n"]}/8 lists' if r["n"] else 'Added: not in the lists'))
    return f'''<div class="{' '.join(cls)}">{plate(r)}<div class="cb"><div class="ct"><b>{E(r["en"])}</b>{stamp(r)}</div>
<div class="cj">{E(r["jp"])}</div><div class="co">{E(r["order"])}</div><div class="cm">{yen(r)} · {E(meta(r))}</div>
<div class="cf">{''.join(tags)}<span class="rk">{rank}</span><a class="mp" href="{maps(r)}">地図 Map</a></div></div></div>'''

def weight(r):
    if r["avg"] is None: return 1
    return 3 if r["avg"] >= 4.2 else 2 if r["avg"] >= 3.6 else 1
def spinner(items, render, sid, empty, kind):
    sl = []
    for r in items: sl += [r] * weight(r)
    random.Random(sum(map(ord, sid))).shuffle(sl)
    n = len(sl)
    if not n:
        return f'<div class="sp {kind}" id="{sid}"><div class="it none">{empty}</div></div>'
    inner = "".join(f'<div class="it">{render(r)}</div>' for r in sl)
    return f'<div class="sp {kind}" id="{sid}"><div class="strip" style="animation:roll {n*0.06:.2f}s steps({n}) infinite">{inner}</div></div>'

GUT = '<div class="gut"><b>Gut check:</b> relieved → go. A little “ugh” → spin again.</div>'
def tagline(r):
    t = [stamp(r)]
    if "spicy" in r["flags"]: t.append('<span class="chip hot">🌶️ Spicy</span>')
    if "solo" in r["flags"]: t.append('<span class="chip">Solo OK</span>')
    t.append(f'<span class="rk">{"Consensus " + LET(r["avg"]) + " · " + str(r["n"]) + "/8 lists" if r["avg"] is not None else "Added pick"}</span>')
    return '<div class="tags">' + "".join(t) + '</div>'
def ticket(r):
    return f'''<div class="tk"><div class="tkh">食券 <small>MEAL TICKET · No.{(sum(map(ord, r["id"]))*37)%9000+1000}</small></div>
<div class="tkt">{plate(r, "bplate")}<div class="tkn"><div class="jp">{E(r["jp"])}</div><div class="en">{E(r["en"])}</div></div></div>
<div class="tkb"><div class="od">{E(r["order"])}</div><div class="meta"><span class="yen">{yen(r)}</span><span>{E(meta(r))}</span></div>
{tagline(r)}{GUT}<a class="btn" href="{maps(r)}">📍 地図 · Find the nearest one</a></div></div>'''
def mini(r):
    return f'''{plate(r)}<div class="mb"><b>{E(r["en"])}</b><span class="mj">{E(r["jp"])}</span>
<div class="mo">{E(r["order"])}</div><div class="mm">{yen(r)} · {E(meta(r))} · <a href="{maps(r)}">地図 Map</a></div></div>'''

# ---- spin (shared) ----
SPIN = ["all"] + [k for k, *_ in FEELS] + ["spicy"]
EMO = dict({k: FEEL[k]["emo"] for k in FEEL}, all="🎲", spicy="🌶️")
def pool(fk, tk):
    return [r for r in rows if (fk == "all" or (fk == "spicy" and "spicy" in r["flags"]) or r["feel"] == fk)
            and (tk == "any" or r["hrs"] != "std")]
grid = "".join(f'<input type="radio" name="sf" id="sf-{k}"{" checked" if k=="all" else ""}><label for="sf-{k}"><span>{EMO[k]}</span>{SHORT[k]}<i>{JPN[k]}</i></label>' for k in SPIN)
spins, css = [], []
for fk in SPIN:
    for tk in ("any", "late"):
        sid = f"sp-{fk}-{tk}"
        spins.append(spinner(pool(fk, tk), ticket, sid, '<b>Nothing open late here.</b><br>Switch to “Any time” or pick another feel.', "hero"))
        css.append(f'body:has(#sf-{fk}:checked):has(#st-{tk}:checked) #{sid}{{clip-path:inset(0 0 0 0);pointer-events:auto}}')

# ---- 松竹梅 ----
P3 = [("matsu", "松", "#2f5d3a", "Matsu · treat yourself", lambda r: r["hi"] >= 2500 or r["feel"] == "sweet"),
      ("take", "竹", "#5d7a3a", "Take · the safe bet", lambda r: r["avg"] is not None and r["avg"] >= 3.6),
      ("ume", "梅", "#c8322a", "Ume · wildcard", lambda r: r["avg"] is None or r["avg"] < 3.6)]
p3 = []
for pk, kj, col, lab, fn in P3:
    inner = ""
    for tk in ("any", "late"):
        sid = f"p3-{pk}-{tk}"
        inner += spinner([r for r in rows if fn(r) and (tk == "any" or r["hrs"] != "std")], mini, sid, '<div class="mb">Nothing late in this slot.</div>', "mini")
        css.append(f'body:has(#pt-{tk}:checked) #{sid}{{clip-path:inset(0 0 0 0);pointer-events:auto}}')
    p3.append(f'<div class="slot"><div class="slab"><span class="k" style="background:{col}">{kj}</span>{lab}</div><div class="reel"><div class="ph2">{kj}</div>{inner}</div></div>')

# ---- quiz ----
Q1 = [("r", "🍚", "Rice"), ("n", "🍜", "Noodles"), ("o", "🥩", "Meat, bread, other"), ("c", "☕️", "Coffee or sweet")]
Q2 = [("s", "🤏", "Snack"), ("m", "🍽️", "Proper meal"), ("f", "🐷", "Feast")]
Q3 = [("q", "⚡️", "Quick, solo-ish"), ("s", "🛋️", "Sit and linger")]
qres = []
for a, *_ in Q1:
    for b, *_ in Q2:
        for c, *_ in Q3:
            pl = [r for r in rows if r["base"] == a]
            groups = [[r for r in pl if r["size"] == b and r["vibe"] == c], [r for r in pl if r["size"] == b],
                      [r for r in pl if r["vibe"] == c], pl]
            picks, feels = [], set()
            for g in groups:
                for r in sorted(g, key=key):
                    if len(picks) < 3 and r not in picks and r["feel"] not in feels: picks.append(r); feels.add(r["feel"])
            for g in groups:
                for r in sorted(g, key=key):
                    if len(picks) < 3 and r not in picks: picks.append(r)
            items = "".join(f'<div class="qi"><span class="md">{"一二三"[i]}</span>{mini(r)}</div>' for i, r in enumerate(picks))
            qres.append(f'<div class="qres" id="qr-{a}{b}{c}"><div class="sh"><span class="n">結</span>Your match</div><div class="grp">{items}</div></div>')
            css.append(f'body:has(#q1-{a}:checked):has(#q2-{b}:checked):has(#q3-{c}:checked) #qr-{a}{b}{c}{{display:block}}')
def qopts(name, opts):
    return "".join(f'<input type="radio" name="{name}" id="{name}-{v}"><label for="{name}-{v}"><span class="qe">{e}</span>{t}</label>' for v, e, t in opts)

# ---- browse ----
for k, *_ in FEELS:
    css.append(f'body:has(#bf-{k}:checked) .card:not(.f-{k}){{display:none}}')
    css.append(f'body:has(#v-{k}:checked) .card.f-{k}{{display:none}}')
css += ['body:has(#bt-late:checked) .card.hstd{display:none}', 'body:has(#bt-24:checked) .card:not(.h24){display:none}',
        'body:has(#bb-b1:checked) .card:not(.b1){display:none}', 'body:has(#bb-b2:checked) .card:not(.b2){display:none}',
        'body:has(#bb-b3:checked) .card:not(.b3){display:none}', 'body:has(#bx-solo:checked) .card:not(.solo){display:none}',
        'body:has(#bx-spicy:checked) .card:not(.spicy){display:none}']
def chips(name, opts, kind="radio"):
    return "".join(f'<input type="{kind}" name="{name}" id="{name}-{v}"{" checked" if (kind=="radio" and i==0) else ""}><label for="{name}-{v}">{t}</label>' for i, (v, t) in enumerate(opts))
seg = lambda name, opts: f'<div class="seg">{chips(name, opts)}</div>'

# ---- home ----
ranked = [r for r in rows if r["avg"] is not None and r["n"] >= 4][:5]
board = "".join(f'<div class="row"><span class="ri">{"一二三四五"[i]}</span>{plate(r, "splate")}<div class="rt"><b>{E(r["en"])} <span class="mj">{E(r["jp"])}</span></b><small>in {r["n"]}/8 lists</small></div><a class="mp" href="{maps(r)}">地図</a></div>' for i, r in enumerate(ranked))
MODES = [("spin", "回", "var(--shu)", "Just pick for me", "Late-night decision fatigue is real. Hand it to the spinner."),
         ("three", "三", "#2f5d3a", "Give me 3 · 松竹梅", "A treat, a safe bet and a wildcard. Three options beat thirty."),
         ("quiz", "問", "var(--ai2)", "Ask me 3 quick questions", "Small this-or-that steps instead of one big choice."),
         ("browse", "否", "#8f4e35", "I only know what I DON'T want", "Veto feels until something's left."),
         ("browse", "覧", "var(--kin)", "Show me everything", "Maximiser mode: filter, compare, take your time.")]
modes = "".join(f'<label class="row" for="t-{t}"><span class="ico" style="background:{c}">{k}</span><div class="rt"><b>{h}</b><small>{s}</small></div><span class="chev">›</span></label>' for t, k, c, h, s in MODES)
GUIDE_S = '''<details class="guide"><summary>使い方 · How to use</summary><ol>
<li>Tap a feel on the grid, or leave it on <b>おまかせ Anything</b>.</li>
<li>After midnight? Tap <b>🌙 Late night</b> to hide places that are likely closed.</li>
<li>Tap <b>回す Spin</b>. Your 食券 meal ticket appears.</li>
<li>Gut check: if you feel relieved, tap <b>📍 地図</b> to find the nearest branch. If you feel “ugh”, tap <b>もう一回 Again</b>, then <b>止める Stop</b>.</li>
<li>Tap <b>✕</b> on the ticket to change the feel.</li></ol></details>'''
GUIDE_D = '''<details class="guide"><summary>使い方 · How to use</summary><ol>
<li><b>簡単 Simple / 詳細 Detailed</b> at the top switches modes any time.</li>
<li><b>回 Spin:</b> pick a feel, then Spin. Again re-rolls; Stop lands it.</li>
<li><b>三 Pick 3:</b> tap Deal 3 for a 松 treat, a 竹 safe bet and a 梅 wildcard.</li>
<li><b>問 Quiz:</b> answer 3 questions and get your top 3. ↺ Start over resets.</li>
<li><b>覧 Browse:</b> veto feels you don't want (they turn red), or filter by time, budget, solo or spicy.</li>
<li>Every chain has a <b>地図 Map</b> button that opens Google Maps nearby.</li></ol></details>'''

page = (open(os.path.join(HERE, "tpl_jp.html")).read()
        .replace("%%N%%", str(len(rows))).replace("%%MODES%%", modes).replace("%%BOARD%%", board)
        .replace("%%GUIDE_S%%", GUIDE_S).replace("%%GUIDE%%", GUIDE_D)
        .replace("%%GRID%%", grid).replace("%%SPINS%%", "".join(spins)).replace("%%P3%%", "".join(p3))
        .replace("%%Q1%%", qopts("q1", Q1)).replace("%%Q2%%", qopts("q2", Q2)).replace("%%Q3%%", qopts("q3", Q3))
        .replace("%%QRES%%", "".join(qres))
        .replace("%%BF%%", chips("bf", [("all", "おまかせ All")] + [(k, f'{FEEL[k]["emo"]} {SHORT[k]}') for k, *_ in FEELS]))
        .replace("%%BT%%", seg("bt", [("any", "Any time"), ("late", "Late"), ("24", "24h")]))
        .replace("%%BB%%", seg("bb", [("any", "Any ¥"), ("b1", "< ¥1k"), ("b2", "¥1–2k"), ("b3", "Splurge")]))
        .replace("%%VETO%%", chips("v", [(k, f'✕ {SHORT[k]}') for k, *_ in FEELS], "checkbox"))
        .replace("%%CARDS%%", "".join(card(r) for r in rows))
        .replace("%%DYNCSS%%", "\n".join(css)))
open(OUT, "w").write(page)
print(len(rows), "chains →", OUT, len(page) // 1024, "KB")
