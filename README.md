# PFT scoring (PFT_new)

Scores phonemic (letter) fluency task trials word-by-word against the
Leslie code system. Default target letter is **P**.

Given a participant's spoken words, each word is assigned one code:

| Code | Meaning |
|---|---|
| `C` | Correct — on-target real word, not a repeat |
| `OTH` | Off-target speech (wrong first letter), real or not |
| `N` | Nonword that does start with the target letter |
| `PN` | Proper noun (person or country name) |
| `R` | Exact repeat of an earlier correct word |
| `SIM` | Morphological variant / synonym of an earlier correct word |
| `F` | Filled pause (`um`, `er`, ...) |

See [`docs/pft_new_scoring.md`](docs/pft_new_scoring.md) for the full rule
hierarchy and how each rule decides.

## Setup

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('wordnet'); nltk.download('words')"
```

Optional — install as an editable package so `import dementia_speech`
works from any directory:

```bash
pip install -e .
```

## Quick start

### Score a directory of transcripts (recommended)

`score_directory.py` scans a folder, scores every `.txt` **and** `.TextGrid`
file in it (one trial per file), and writes the results to CSV:

```bash
python score_directory.py data/raw/transcripts
```

```
scored example1.txt  (7 words)
scored example2.txt  (13 words)
scored example3.TextGrid  (9 words)

3 trial(s) scored
wrote data/processed/pft_words.csv
wrote data/processed/pft_metrics.csv
```

- `data/processed/pft_words.csv` — one row per word, all trials stacked,
  with a `source_file` column (and `start`/`end`/`duration`/`iwi` filled in
  for TextGrid trials, blank for plain-text ones).
- `data/processed/pft_metrics.csv` — one row per trial: `total_words`, the
  per-code counts (`C, OTH, N, PN, R, SIM, F`), and `errors`.

Options: `--letter p` sets the target letter for the whole directory;
`--outdir data/processed` chooses where the CSVs go.

### Score a single plain-text transcript

```bash
python example_run.py data/raw/transcripts/example1.txt
```

```
    word classification
      um              F
   paint              C
   paint              R
painting            SIM
   peter             PN
  banana            OTH
   xyzzy            OTH

{'total_words': 7, 'C': 1, 'OTH': 2, 'N': 0, 'PN': 1, 'R': 1, 'SIM': 1, 'F': 1, 'errors': 3}
```

## Using it in your own code

```python
from dementia_speech.io.text import load_words_from_txt       # plain-text transcript
from dementia_speech.io.textgrid import load_word_tier        # Praat TextGrid (has timing)
from dementia_speech.tasks.PFT_new.scoring import score_trial, compute_metrics

df = load_words_from_txt("path/to/transcript.txt")   # one row per word
scored = score_trial(df, target_letter="p")          # adds a 'classification' column
metrics = compute_metrics(scored)                    # per-code counts for the trial
```

Both loaders expect **only the participant's spoken words** — no speaker
labels, timestamps, or interviewer turns. `score_trial` only reads the
`word` column, so you can also build that DataFrame yourself.
`score_directory.py` is the reference implementation of looping this over
a corpus.

## Input files

`data/raw/transcripts/` holds the example inputs:

- `example1.txt`, `example2.txt` — plain text: whitespace-separated words,
  participant only.
- `example3.TextGrid` — a Praat TextGrid with a `transcript/word` tier,
  one interval per spoken token. Bracketed annotations (`[cough]`, `[laugh]`)
  and empty intervals are dropped on load. Requires `praatio` (in
  `requirements.txt`).

Point `score_directory.py` at your own folder of `.txt` / `.TextGrid`
files the same way.

## Reference data

`data/raw/reference/babynames1996to2025.xlsx` (ONS baby-name
registrations) is used for person-name detection and must stay in place.
It is resolved relative to the repo, so the package works from any
working directory.

## Not included / not implemented

- No participant/diagnosis metadata join — `score_directory.py` keys
  output by `source_file` only. Merge in your own metadata afterwards.
- Leslie codes `SC_CORR, LP, FRAG, SC_ERR, SC_META, META, TG` are not
  implemented; wrong-letter words are folded into `OTH` rather than kept
  as `L`.
- No automated test suite.
