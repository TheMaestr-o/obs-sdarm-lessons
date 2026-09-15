# Who wrote what in this repository

**Short answer: most of what you actually use on stream is your own work. Three files are
someone else's code, kept unchanged. One folder of lesson text is not code at all and is the
thing most worth thinking about. Nothing here is stolen — but a few labels are wrong or
missing, and fixing them is about an hour of work.**

> I am not a lawyer, and neither are you. Nothing in this file is legal advice. If anything
> here ever matters for real — money, a complaint, a takedown, publishing under your church's
> name — ask a real lawyer. What follows is an honest practical read, which is what you asked
> for.

---

## 1. What is yours

These files you wrote from nothing. No one else's code is inside them.

| File | What it is |
|---|---|
| `OBS_InforR-Lower/panel.html` | The control panel. 1482 lines. The lesson picker, the question letter buttons, Previous/Next, the color swatches, the settings memory — all yours. |
| `OBS_InforR-Lower/result.html` | The OBS Browser Source page. 148 lines. |
| `OBS_InforR-Lower/panel-wirecast.html` | Wirecast version of the panel. 893 lines. |
| `OBS_InforR-Lower/result-wirecast.html` | Wirecast version of the result page. 90 lines. |
| `OBS_InforR-Lower/native/overlay.html` | The overlay renderer. 167 lines. Builds the markup with normal DOM calls. |
| `OBS_InforR-Lower/native/overlay.css` | The overlay styling and animation. See section 3 — this one has a footnote. |
| `OBS_InforR-Lower/tools/build-lessons-data.py` | Builds `lessons-data.json` from your lesson files. |
| `OBS_InforR-Lower/LOCAL-SETUP.md`, `WIRECAST-SETUP.md` | Your documentation. |
| `sbl-question-card/extract-questions.py`, `STREAMING_GUIDE.md` | Your earlier script and guide. |
| `HOW-TO-USE-IN-OBS.md`, `index.html`, `tests/`, `screenshots/` | Yours. |

I checked this two ways and both agree:

- **Git history.** Out of 19 commits, 15 are you building this. The other people's files were
  added once, in the very first commit, and never touched again.
- **The code itself.** Your `panel.html`, `result.html` and `native/overlay.html` contain no
  `<link>` and no `<script src>` pointing at any of the borrowed files. They do not load
  `lower.css`, `lower.js`, `site.css`, `getmdl-select`, jQuery, or anything from a CDN. They
  run completely on their own.

That last point is the strongest fact in this whole document. **You could delete the three
borrowed files today and your system would keep working exactly as it does now.** That is not
true of a project that merely "customized" someone else's code.

---

## 2. What is someone else's

### 2a. Code you kept, unchanged, inside `OBS_InforR-Lower/`

| File | Author | Licence |
|---|---|---|
| `lower.html` | Vasco Cruz | MIT |
| `css/lower.css` | Vasco Cruz | MIT |
| `js/lower.js` | Vasco Cruz | MIT |
| `css/site.css`, `js/site.js` | Vasco Cruz | MIT |
| `img/*`, `scripts/lower-thirds-read-file.lua` | Vasco Cruz | MIT |
| `css/getmdl-select/`, `js/getmdl-select/` | getmdl-select project | MIT |

From https://github.com/vjccruz/lower-thirds-obs. **`OBS_InforR-Lower/LICENSE` is present and
correct** — it carries "Copyright (c) 2021 Vasco Cruz" and the full MIT text. His `README.md`
is also still there, crediting the After Effects template by Amaksi and the CodePen by Matt
Chestnut.

**This is done right.** MIT asks for exactly one thing: keep the copyright notice and the
licence text with the code. You did. You also did better than required — `LOCAL-SETUP.md`
writes down the two small edits you made to his files (relative paths, local Lua URL) and says
"do not remove" about the attribution. That is careful, honest work.

### 2b. Two other people's whole projects, kept for comparison

| Folder | Author | Licence | Status |
|---|---|---|---|
| `OBS_Animated-Lower-Thirds/` | noeal-dac | MIT — `LICENSE` present, correct | Fine |
| `OBS_LowerThirds/` | unknown | **none** | See below |

`OBS_Animated-Lower-Thirds/` is fine. MIT licence file present, author's README present,
author's name in the source comments.

**`OBS_LowerThirds/` is the one real problem in this repository.** It has no LICENSE file, no
copyright line, and no author. Its own `README.txt` ends with the line:

```
Created by: [Your Name/Antigravity]
```

That is an unfilled template placeholder. Nobody knows who wrote it. With no licence,
**the legal default is "all rights reserved"** — you do not have permission to redistribute it,
and this is a public GitHub repository, so you are redistributing it right now. This is not a
disaster and nobody is coming after you. But it is the one thing here that is actually
unpermitted, as opposed to merely unlabelled.

---

## 3. The CodePen question — the interesting part

You asked specifically what survived from the CodePen design
(https://codepen.io/mattchestnut/pen/dMrONe). I compared `native/overlay.css` against
`css/lower.css` line by line. Here is the honest answer, and it is a split decision.

**Structurally, your file is genuinely a new thing.** The original hides the text again two
seconds after showing it, because every animation is built as `iteration-count: 2` plus
`alternate` — it plays forward, then immediately backward. You needed the opposite: the
question must stay on screen until the presenter advances. You could not patch that from
outside (`LOCAL-SETUP.md` documents the `file://` same-origin dead end you hit first), so you
rebuilt it. Your version splits the original's single long keyframe block into a short
animation plus a delay per element, runs once, and uses `forwards` to hold. Different
selectors, different class names, different structure, different behaviour. That is a
reimplementation, not a copy.

**But specific values were carried across, and some are distinctive.** These are not accidents
of two people solving the same problem:

- `cubic-bezier(0.19, 0.76, 0.32, 1)` — an arbitrary four-number easing curve, identical.
- `translate3d(6em, 0, 0)` — the slash's starting offset, identical.
- `font-size: 5em` and `top: -.15em` on the slash, identical.
- `.93em` and `.55em` — the two text indents, identical numbers (you moved them from `left` to
  `padding-left`).
- The `.mask` rule, all three properties, identical.
- The `Open Sans` / `Arimo` font pairing and `text-transform: uppercase; line-height: 1`.

So: **the motion design is Matt Chestnut's; the implementation is yours.** A fair description
is "an original implementation of a borrowed visual design". Not "our own design".

Two more things worth saying plainly:

**Your third style is fully yours.** You replaced the original's "Framed Reveal" (id 5) with
"Quiet Rule" (id 3). Your own file comment says it has "no counterpart there". That one owes
nothing to anybody.

**The CodePen's own licence is unclear.** CodePen pens default to MIT unless the author says
otherwise, but "defaults to MIT" is a platform convention, not a licence file you can point at.
Vasco Cruz built on it too and released under MIT. You are in the same position he is — which
is a reasonable position, and a very common one, but it is not a documented one.

---

## 4. The lesson text — different kind of problem

`OBS_InforR-Lower/lessons-data.json` is 973 KB. I opened it. It contains the **full text** of
the SDARM Sabbath School lessons for quarter 2026-3: 13 lessons, every question, every day
heading, in **22 languages** (bg, cs, de, en, es, fr, hr, hu, id, it, ja, mk, pt, ro, ru, rw,
sr, th, tl, uk, zh, zu).

This is not code. Software licences like MIT have nothing to say about it. It is written
religious material, and the copyright in it belongs to whoever publishes the SDARM lesson —
almost certainly the church organisation, not you and not the repository.

Right now that full text sits in a **public** GitHub repository, in 22 languages, with no
statement of where it came from or whether anyone said yes.

I am not going to tell you this is illegal, because I do not know your church's position and
that genuinely varies — many denominations distribute their lesson material freely and would be
glad to see it used on a stream. But notice the shape of the situation: **this is the one item
in the repository where you are republishing a substantial complete work that is not yours, at
scale, publicly, with no attribution and no stated permission.** It is a bigger exposure than
anything on the code side, and it is the item most likely to actually cause you a problem.

Concretely, you have three options:

1. **Ask.** Contact whoever publishes the lesson and ask if you may include the text. Written
   permission in an email ends the question permanently. This is the right answer.
2. **Stop shipping it.** Add `lessons-data.json` to `.gitignore`, remove it from the repository,
   and let `build-lessons-data.py` generate it locally on each machine. The script already does
   this — it reads from `~/Developer/sbl/data/`. Your system keeps working; the public repo just
   stops carrying the text. This is the safe answer and costs you almost nothing.
3. **Leave it and add a credit line** saying whose lesson it is. Better than silence, but it
   does not actually give you permission.

If you want this over with quickly, do option 2 now and option 1 when you have time.

---

## 5. What is currently missing or wrong

Five things. None are catastrophic. I have not changed any of them — you asked me not to.

**1. There is no LICENSE file at the top of the repository.**
`OBS_InforR-Lower/` and `OBS_Animated-Lower-Thirds/` each have one, but the repository root has
none. So your own code — `panel.html`, `native/`, the Python tools, roughly 3300 lines — is
published with **no licence at all**. Ironically that means your own work is currently the most
restrictively licensed thing here: legally, "all rights reserved". If you want people to be able
to use it, say so. Add a root `LICENSE` with your name and the year. MIT is the natural choice,
since everything you built on is MIT.

**2. `OBS_LowerThirds/` has no licence and no known author.** See section 2b. My
recommendation: delete the folder. It is kept only for comparison, you are not using it, the
screenshots in `screenshots/` already record what it looked like, and it is the only genuinely
unpermitted item in the repository. If you want to keep it, at minimum add a `NOTICE.txt`
saying where you downloaded it from and that the author is unknown.

**3. `README.md` describes a project that no longer exists.** It still opens with "A comparison
of ready-made lower thirds solutions", and its "Our own work" section lists only
`sbl-question-card/extract-questions.py`. It does not mention `panel.html`, `result.html`,
`native/overlay.html`, `native/overlay.css`, the Wirecast pair, `lessons-data.json`, or
`build-lessons-data.py` — which is to say, it does not mention the system you actually built
and use. **This one undersells you, it does not oversell you**, but it should be rewritten. It
is the file people read first.

**4. `native/overlay.css` and `native/overlay.html` have no author line.** They carry good
technical comments but never say who wrote them or under what terms. Add a short header to each:

```
/* Copyright (c) 2026 <your name>. MIT licence — see /LICENSE.
   Styles 1 and 2 reimplement the visual design of
   https://codepen.io/mattchestnut/pen/dMrONe (via github.com/vjccruz/lower-thirds-obs).
   Style 3 "Quiet Rule" is original. */
```

That single comment resolves the entire section 3 question honestly and permanently.

**5. `index.html` line 124 slightly overstates things.** It says the design was "rebuilt as our
own CSS". Given the identical easing curve and offsets, "reimplemented from the CodePen design"
is the accurate phrasing. Small change, but it is the one sentence in the repo that leans too
far in your favour.

---

## 6. So — can this be "our own plugin"?

**Yes, with one honest qualifier.**

You can truthfully say: *"Our own OBS lesson-question overlay system, built on the
lower-thirds-obs project by Vasco Cruz (MIT). The visual style of two of the three animations
is based on a CodePen design by Matt Chestnut."*

That is not a weak claim. That is how most real open-source software describes itself. The
control panel, the lesson and question picker, the 22-language data pipeline, the Wirecast
port, the hold-forever overlay behaviour, the transparency handling, the localStorage bridge
for OBS docks — all of that is yours, it is the large majority of the code, and it is the part
that makes the thing useful. Nobody else wrote a lower-third that knows what a Sabbath School
lesson is.

What you cannot honestly say is *"our own design, from scratch, no one else involved"* — because
of the easing curve and the offsets in section 3, and because three of Vasco Cruz's files are
still sitting in the folder.

### If you want the claim to be completely clean

Do these five, in this order. Roughly an hour.

1. **Add a root `LICENSE`** with your name. MIT. (5 min — and this one is for your benefit, not
   anyone else's.)
2. **Remove `lessons-data.json` from the public repo**, add it to `.gitignore`, note in the
   README that `build-lessons-data.py` generates it. (10 min. This is the one with real
   exposure.)
3. **Delete `OBS_LowerThirds/`.** Unlicensed, unknown author, unused. (1 min.)
4. **Add the author/attribution header** to `native/overlay.css` and `native/overlay.html`. (5
   min. This is what makes the CodePen question go away.)
5. **Rewrite `README.md`** to describe what this actually is now — your overlay system — with a
   short "Credits" section at the bottom for Vasco Cruz, Matt Chestnut, Amaksi and noeal-dac.
   (30 min.)

**What you do not need to do:** you do not need to rewrite `native/overlay.css`, and you do not
need to delete `OBS_InforR-Lower/`'s borrowed files. The MIT licence already permits exactly
what you are doing with them, and you already satisfied its one condition. Leaving them in place
with their LICENSE intact is correct — arguably more correct than removing them, since they
document where the project came from.

---

## 7. One thing that surprised me, and one bug

**The surprise:** you are cleaner than your own README claims. Your README says "our own work"
is one Python script. In reality it is roughly 3300 lines across ten files, none of which load a
single line of anyone else's code. You wrote significantly more of this than your own
documentation gives you credit for.

**A bug, unrelated to licensing, found while comparing the two CSS files:**
`native/overlay.css` asks for `'Open Sans'` and `'Arimo'` but — unlike `css/lower.css`, which
imports them from Google Fonts at the top — it contains **no `@import` and no `<link>`**. So
those fonts only appear if they happen to be installed on the machine. On a machine without
them, your overlay silently falls back to a generic sans-serif and looks subtly different from
what you designed. Since the whole project is deliberately offline-capable, the right fix is not
a Google Fonts import — it is to bundle the two font files locally and reference them with
`@font-face`. (Check the fonts' own licences first; Open Sans and Arimo are both Apache 2.0,
which permits this and asks for the licence text to be included alongside.)
