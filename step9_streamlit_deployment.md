# Step 9: Streamlit Deployment Guide (Dry Run First)

**Status:** originally written 2026-08-01 before any deployment attempt.
**Partially superseded the same day — read §0 first.**
**Owner:** Yan-Bo
**Audience:** first-time Streamlit user. Assumes no prior deployment experience.

---

## 0. Status update (added 2026-08-01, after local prep)

Sections 1 to 7 below were written before `app/` contained anything. Three of
the four blockers in §1 have since been fixed. This section records what is
actually true now; where it conflicts with §1, this section wins.

**Blocker status:**

| Blocker | Original claim | Actual status now |
|---|---|---|
| 1. `matplotlib` undeclared | fatal, guaranteed | **FIXED.** `app/requirements.txt` created and declares it. |
| 2. research `requirements.txt` too heavy | likely fatal, biggest risk | **FIXED.** `app/requirements.txt` is app-scoped and minimal. The research root file is untouched, as intended. Whether Streamlit Cloud actually reads the app-level file is still UNVERIFIED — that is what the cloud deploy tests (see §5 Failure D). |
| 3. `data/processed/` gitignored | not yet active, a trap | **STILL OPEN.** `app/data/step9_bundle.json` does not exist yet, so the trap has not been sprung. Re-check with `git check-ignore -v` when 9-B produces the bundle. |
| 4. filename / path inconsistency | cosmetic, avoidable rework | **FIXED.** The deployed path is `app/streamlit_app.py`. `step9_streamlit_demo_draft.py` has been marked SUPERSEDED and now names itself correctly in its own docstring. |

**Correction to §3.1: the venv is named `.venv-cs5340-app`, not `.venv-app`.**
That is the one that exists in the working directory and the one the clean
install was tested in. Substitute that name wherever §3.1 says `.venv-app`.

### 0a. Layout superseded 2026-08-02 — does NOT affect the deployment steps below

Wherever this document's earlier sections describe or show the app's layout
(stacked panels, a single intervention slot, no Framework A/B blocks), that
description is superseded by `step9_plan.md` section 10b. Reference
implementation: `step9_layout_prototype_final.html` in the project root.

**This does not touch anything below in this file.** Sections 2 onward (repo
layout, the dry-run steps, failure modes, the checklist) describe how to get
a Streamlit app onto Community Cloud and are layout-agnostic — they apply
the same way regardless of what `app/streamlit_app.py` renders. Only the
*content* of that file changes when 9-C rebuilds it; the *deployment*
procedure does not.

**Progress beyond this document:** `app/streamlit_app.py` and
`app/requirements.txt` exist, ran successfully in the clean venv, and have
been committed and merged to `main`. The app was also updated for Prof.
Sushmita's feedback (key metrics moved to the top) and the deprecated
`use_container_width` call was replaced with `width="content"`.

**What has NOT happened yet:** no Streamlit Community Cloud deployment has
been attempted. §3.2 onward is entirely still to do, and it remains the item
with unknown failure modes. §3.1 is done.

**Purpose.** Deploying to Streamlit Community Cloud is the only Step 9 task
that depends on nothing else: not on Raj's quota, not on Prof. Sushmita's
reply, not on Step 9-A/B producing real data. It is also the only task the
team has never done before, which means its failure modes are unknown.
Do it now, with a throwaway mock, so the unknowns surface with 10 days of
runway instead of 1.

**Core idea: separate two questions.**

| Question | Status | Depends on |
|---|---|---|
| A. Does the app logic/layout work? | mostly solved (`step9_streamlit_demo_draft.py` runs, q033 uses real data) | nothing further |
| B. Does it deploy to a public URL? | **never attempted** | nothing (can do today) |

This document is about question B.

---

## 1. Blockers found in the current draft (2026-08-01 review)

These were found by reading `step9_streamlit_demo_draft.py` against
`requirements.txt` and `.gitignore`. All four would surface during a real
deployment; fixing them beforehand saves a debugging cycle.

### Blocker 1: `matplotlib` is imported but not declared

Line ~94 of the draft runs `import matplotlib.pyplot as plt`, but
`matplotlib` does not appear in `requirements.txt`. On a local Mac this
works because matplotlib is already installed in the environment. On
Streamlit Community Cloud the container installs ONLY what
`requirements.txt` lists, so the app will crash with `ModuleNotFoundError`
on first load.

**Severity: fatal, guaranteed to happen.**

### Blocker 2: `requirements.txt` is a research environment, not an app environment

The current file lists:

```
numpy>=2.0
tqdm>=4.67
sentence-transformers>=4.1
chromadb>=1.0
scikit-learn>=1.7
pandas>=2.3
streamlit>=1.45
```

Under the Route A architecture (`step9_plan.md` §3), Streamlit is a pure
JSON reader and chart renderer. It never embeds text, never queries
ChromaDB, never calls Gemini. So `sentence-transformers`, `chromadb`, and
`scikit-learn` are not needed by the app at all.

This matters because `sentence-transformers` pulls in PyTorch, which is
roughly 2GB. Streamlit Community Cloud's free tier has around 1GB of RAM
and a build time limit. Installing this stack will either time out, run out
of memory, or take many minutes on every rebuild.

**Severity: likely fatal, and the single biggest deployment risk.**

**Fix: use a separate, minimal requirements file for the app.** Do NOT
delete the research `requirements.txt`; the notebooks and pipeline scripts
still need it. Create a second one scoped to the app.

### Blocker 3: `data/processed/` is gitignored, which will bite later

`.gitignore` currently contains:

```
data/processed/*
!data/processed/.gitkeep
```

Today this is harmless, because the draft hardcodes its data in Python
lists (`BASELINE_PAPERS`, `INTERVENTION_PAPERS_MOCK`). But
`step9_plan.md` §9 plans to create `data/step9_bundle.json`. If the bundle
ever lands under `data/processed/`, git will silently skip it, the deployed
app will not find it, and the failure will look like a mysterious
FileNotFoundError in the cloud while working perfectly on the local machine.

**Severity: not yet active, but a trap with a confusing symptom.**

**Fix: put the bundle somewhere the app owns**, for example
`app/data/step9_bundle.json`, and confirm with `git check-ignore -v` that it
is actually tracked before deploying.

### Blocker 3b: bundle hosting decision (GitHub, not Kaggle)

The question was raised whether `step9_bundle.json` should ship inside the
GitHub repo or stay on a Kaggle Dataset that the app downloads at runtime,
out of concern for GitHub storage limits. **Ship it in the repo.** Measured
file sizes from this project on 2026-08-01:

| File | Actual size | Repo-safe? |
|---|---|---|
| `data/processed/qbio_papers.json` | 85.5 MB | No. Correctly gitignored today. |
| `data/retrieval_results.json` | 96 KB | Yes, trivially. |
| `app/data/step9_bundle.json` (projected) | ~1 to 1.5 MB | Yes, trivially. |

The bundle projection assumes 150 queries x 20 papers (10 baseline + 10
intervention) carrying only `title` and `institution`, NOT abstracts, plus
two answer texts per query. GitHub warns at 50 MB per file and hard-blocks
at 100 MB, so the bundle sits roughly 30x below the warning threshold.

**Why not Kaggle:**

1. Kaggle Dataset downloads require API credentials (`kaggle.json`) even for
   public datasets, which means storing secrets in Streamlit and adding a
   failure mode that does not otherwise exist.
2. It contradicts the entire rationale for Route A (`step9_plan.md` §3),
   which was chosen specifically so that no live network call happens during
   a demo. Fetching from Kaggle at startup reintroduces the demo-day network
   risk that Route A was designed to eliminate.
3. It adds the `kaggle` package to an app whose build time budget is
   already the main deployment risk (Blocker 2).
4. The rubric independently requires the GitHub repo to contain a JSON
   results file, so JSON is going into the repo regardless.

**What stays on Kaggle:** the genuinely large artifacts, i.e.
`qbio_papers.json`, the embeddings `.npy`, and the ChromaDB index. The
current gitignore treatment of those is correct and should not change.

### Blocker 4: filename and path inconsistencies

- The docstring says `streamlit run step9_streamlit_demo.py`, but the file
  is named `step9_streamlit_demo_draft.py`.
- `step9_plan.md` §11 (9-C) specifies the final app lives at
  `app/streamlit_app.py`, but `app/` currently contains only `.gitkeep`.

Streamlit Community Cloud asks for the main file path when you create the
app. Decide the final path now so the deployment does not need to be
recreated later.

**Severity: cosmetic now, avoidable rework later.**

---

## 2. Repo layout decision (do this before deploying)

Recommended structure. The point is that everything the deployed app needs
lives under `app/`, so there is never a question about what gets shipped.

```
CS6200-Project/
├── requirements.txt              # research env: notebooks, pipeline. UNCHANGED.
├── app/
│   ├── streamlit_app.py          # the deployed app (main file path)
│   ├── requirements.txt          # app-only deps. NEW.
│   └── data/
│       └── step9_bundle.json     # produced by 9-B. NOT gitignored.
└── step9_streamlit_demo_draft.py # keep as the concept demo, or move into app/
```

**On the two requirements.txt files.** Streamlit Community Cloud looks for
`requirements.txt` relative to the repository root by default, but it also
accepts one in the same directory as the main file. Having `app/requirements.txt`
next to `app/streamlit_app.py` is the arrangement to verify during the dry
run. If the cloud build ignores it and installs the root one instead, the
fallback is to move the app to its own repository (see §5, Failure D).

**Proposed `app/requirements.txt` (minimal):**

```
streamlit>=1.45
matplotlib>=3.9
```

Add `pandas` only if the final app actually uses it. The draft currently
does not. Keep this file as short as possible: every line is install time
on every rebuild.

---

## 3. Dry run: step by step

The goal is a public URL showing the mock demo. Nothing about this depends
on real Step 9-A/B data.

### 3.1 Prepare locally

**Step 0 (do this first): create an isolated virtual environment.**

A virtual environment is a private Python folder for this app only. It
matters here for one specific reason: your Mac already has matplotlib,
pandas and others installed globally, so the app appears to work locally
even when `requirements.txt` is incomplete. Streamlit Community Cloud has
none of that. A clean venv reproduces the cloud's emptiness on your own
machine, so Blocker-1-style problems surface in seconds instead of after a
push-build-fail cycle.

```
cd /Users/yanbochen/IdeaProjects/CS6200-Project
python3 -m venv .venv-app
source .venv-app/bin/activate
```

The shell prompt should now be prefixed with `(.venv-app)`. That prefix is
how you know you are inside it. Install NOTHING else into it beyond
`app/requirements.txt`; the whole point is that it stays as bare as the
cloud container.

To leave it later: `deactivate`. To delete it entirely: `rm -rf .venv-app`.
It is disposable, and `.venv-app/` should be added to `.gitignore` so it
never gets committed.

**Then:**

1. Confirm `app/requirements.txt` exists with the minimal dependencies (§2).
2. Confirm `app/streamlit_app.py` exists.
3. Install ONLY the app dependencies into the clean venv:
   ```
   pip install -r app/requirements.txt
   ```
4. Run it:
   ```
   streamlit run app/streamlit_app.py
   ```
   This should open `http://localhost:8501`. Confirm the q033 view renders,
   the donut charts appear, and the selectbox warning fires for q001/q101.
5. If it runs in this clean venv, it will almost certainly run on the cloud.
   If it fails here with `ModuleNotFoundError`, that is exactly the bug the
   dry run exists to catch: add the missing package to
   `app/requirements.txt` and repeat from step 3.

### 3.2 Push to GitHub

Streamlit Community Cloud deploys from a GitHub repository. The repo must
be accessible to the Streamlit account.

1. Confirm the files are actually tracked, not gitignored:
   ```
   git status
   git check-ignore -v app/streamlit_app.py app/requirements.txt
   ```
   The second command should print nothing. If it prints a rule, that rule
   is excluding the file and must be fixed.
2. Commit and push to a branch. A dedicated branch (e.g.
   `step9-deploy-dryrun`) keeps this experiment off `main` until it works.

### 3.3 Deploy

1. Go to `https://share.streamlit.io` and sign in with the GitHub account
   that owns (or can access) the repository.
2. Authorize Streamlit to read the repository when prompted.
3. Create a new app and provide three things:
   - **Repository:** the CS6200-Project repo
   - **Branch:** `step9-deploy-dryrun`
   - **Main file path:** `app/streamlit_app.py`
4. Deploy, then watch the build log. The log is the whole point of this
   exercise: it shows exactly which package failed, which import broke, or
   which file was not found.
5. When it succeeds, note the public URL. Confirm it loads in a browser
   window where you are NOT logged into Streamlit (or in a private window),
   to verify it is genuinely public and not just visible to the owner.

### 3.4 Record the result

Whatever happens, write the outcome into `Claude_todo_memo.md`: the URL if
it worked, or the exact error text if it did not. A half-finished
deployment attempt that nobody documented is worse than not attempting.

---

## 4. What the dry run is actually testing

Five things, all of which are invisible until you try:

1. **Dependency resolution.** Whether the declared packages install at all
   within the build limits.
2. **Import completeness.** Whether anything is imported that is not
   declared (Blocker 1).
3. **File paths.** Local scripts often work by accident because the working
   directory happens to be the project root. In the cloud the working
   directory may differ, so any relative path like `open("data/x.json")` can
   break. Prefer paths built relative to the script file itself.
4. **Repository visibility and permissions.** Whether Streamlit can read the
   repo, and whether a private repo is allowed on the current plan.
5. **Public accessibility.** Whether a grader or classmate with only the URL
   can actually see it.

---

## 5. Likely failure modes and what they mean

**Failure A: `ModuleNotFoundError: No module named 'matplotlib'`**
Blocker 1. Add it to `app/requirements.txt` and redeploy.

**Failure B: build times out, or "Error installing requirements"**
Almost certainly the heavy research dependencies (Blocker 2). Confirm the
cloud is reading the minimal `app/requirements.txt`, not the root research
one. Check the build log for `torch` or `sentence-transformers` downloads:
if you see them, the wrong file is being used.

**Failure C: app loads then crashes with `FileNotFoundError`**
A data file exists locally but is not in the repository, usually because
`.gitignore` excluded it (Blocker 3), or because a relative path resolved
differently in the cloud. Run `git check-ignore -v <path>` to confirm.

**Failure D: the cloud insists on using the root `requirements.txt`**
Two options. Either temporarily rename the research file during the dry run
to confirm the diagnosis, or accept it and give the app its own separate
repository containing only `app/`. The second is cleaner and is a normal
pattern for demo apps, at the cost of copying the bundle into two places.

**Failure E: app sleeps and shows "This app has gone to sleep"**
Normal behaviour on the free tier after inactivity. It wakes on the next
visit, but the first load can take 30 or more seconds. Wake the app a few
minutes before the presentation so it is warm. Also prepare screenshots as
a fallback, since the rubric explicitly permits "Screenshots or live demo."

**Failure F: fonts or emoji render differently than on the Mac**
The draft uses emoji markers and a custom dark theme. Cloud containers run
Linux with a different font set. Cosmetic, but check it rather than
discovering it during the presentation.

---

## 6. Dry-run checklist

- [ ] `app/requirements.txt` created with minimal dependencies
- [ ] `matplotlib` declared
- [ ] `app/streamlit_app.py` exists and runs locally
- [ ] Clean-venv test passes with only `app/requirements.txt` installed
- [ ] `git check-ignore -v` returns nothing for all app files
- [ ] Pushed to a branch on GitHub
- [ ] Streamlit Community Cloud account created and GitHub authorized
- [ ] App created with main file path `app/streamlit_app.py`
- [ ] Build log read to completion, not just the final status
- [ ] Public URL loads in a private/logged-out browser window
- [ ] Outcome (URL or exact error) recorded in `Claude_todo_memo.md`

---

## 7. What changes later, once real data exists

The dry run deliberately keeps the hardcoded mock data. When Step 9-B
produces the real bundle, only two things change:

1. `app/data/step9_bundle.json` is added to the repo.
2. `app/streamlit_app.py` replaces the hardcoded `BASELINE_PAPERS` and
   `INTERVENTION_PAPERS_MOCK` lists with a JSON read, and the selectbox is
   populated from the bundle's query list instead of the current
   three-entry dictionary.

The deployment pipeline itself does not change. That is the entire point of
doing the dry run first: by the time real data is ready, deployment is a
solved problem rather than an unknown.

**Honesty requirements carried over from `step9_plan.md`:**

- The "CONCEPT DEMO / NOT FINAL" badge and the `illustrative` pills must
  stay in place until the intervention panel is backed by real Step 9-A
  output. The current draft is correctly labelled; do not remove those
  labels when wiring in real data for the baseline panel only.
- The footer currently reads "full 150-query build pending Prof. Sushmita's
  scope confirmation (see step9_plan.md §5)". This is now stale: the scope
  was decided and then made tiered in `step9_plan.md` §8. Update the footer
  to state actual coverage, e.g. "20 of 150 queries precomputed".
- Unknown-institution papers must be displayed as unknown, never folded
  into the non-elite count. The draft already does this correctly with the
  `paper-unlabeled` style and a separate "Unlabeled: 5" caption. Preserve
  that behaviour.
