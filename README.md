# 🍜 What do I eat?

A pocket picker for **110 Japanese food chains**: gyudon, ramen, sushi, famires, curry, yakiniku, izakaya, coffee and konbini. It's built for the moment you're hungry and can't decide.

It's a single file that works offline. There's nothing to install and no account, and it doesn't need JavaScript, so it also works inside the iPhone Files preview.

## ⬇️ Download

| Version | What's in it | Download |
|---|---|---|
| **Simple** | One screen: pick a feel, tap 🎲, eat. | [what-do-i-eat-simple.html](https://github.com/Junteki/what-do-i-eat/releases/latest/download/what-do-i-eat-simple.html) |
| **Detailed** | Five decision modes plus all 110 chains with filters. | [what-do-i-eat-detailed.html](https://github.com/Junteki/what-do-i-eat/releases/latest/download/what-do-i-eat-detailed.html) |

Prefer the browser? Open it online: **[junteki.github.io/what-do-i-eat](https://junteki.github.io/what-do-i-eat/)**

### 📱 iPhone
1. Tap a download link above, then tap **Download**.
2. Open the **Files** app → **Downloads** → tap the file. It opens right in Files.
3. Optional: long-press the file → **Move** to keep it somewhere handy.

### 🤖 Android / 💻 desktop
Download the file and open it in any browser.

## 🧠 Detailed mode: pick by how decisive you feel

| Mode | For when you're… | The decision trick |
|---|---|---|
| ⚡️ **Spin** | "Just pick for me" | Delegation beats deliberation when you're tired. Includes a coin-flip **gut check**: relieved → go, "ugh" → spin again. |
| 🃏 **Pick 3** | A bit unsure | Choice overload: three options (safe bet, wildcard, treat) beat thirty. |
| 🔀 **Quiz** | Indecisive | Three this-or-that questions: base, hunger, vibe. |
| 🙅 **Veto** | Only sure what you *don't* want | Elimination by aspects: cross out feels until something's left. |
| 🧐 **Browse** | A maximiser | Every chain, with filters for feel, late-night, budget, solo-friendly and spicy. |

## 📊 Where the rankings come from

Tiers (S–D) are a consensus of eight popular Instagram tier lists: tier_japan_lab, tenten_in_japan (×2), tierskingdom, japanpicksbylocals, travelwiththevees, jpn_things and japanfoodtier. Each placement is scored S=5 … D=1 and averaged, with one neutral vote added so a chain ranked by a single list can't top the table. Chains tagged **NEW** were added for coverage and are unranked.

⚠️ Opening hours and prices are rough guides and vary by branch, so check Maps (every chain has a 📍 button).

## 🛠 Rebuild

`src/` holds the data and generator: `cd src && python3 build3.py`. Output goes to `src/out/`.
