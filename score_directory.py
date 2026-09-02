"""Score every PFT transcript in a directory.

Handles both input formats in the same run:
  - Praat TextGrids (*.TextGrid) -- loaded with timing
  - plain-text transcripts (*.txt) -- one whitespace-separated word list,
    participant's speech only

Each file is treated as one PFT trial. Two CSVs are written to --outdir:
  - pft_words.csv    one row per word, all trials stacked, with source_file
  - pft_metrics.csv  one row per trial: per-code counts (C, OTH, N, PN, R,
                     SIM, F) plus total_words and errors

Setup (once):
    pip install -r requirements.txt
    python -c "import nltk; nltk.download('wordnet'); nltk.download('words')"

Usage:
    python score_directory.py data/raw/transcripts
    python score_directory.py <dir> --letter p --outdir data/processed
"""
import argparse
import sys
from pathlib import Path

# Make the package importable when running this script directly, without
# having to install it first.
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd

from dementia_speech.io.text import load_words_from_txt
from dementia_speech.io.textgrid import load_word_tier
from dementia_speech.tasks.PFT_new.scoring import score_trial, compute_metrics

TEXTGRID_SUFFIXES = {".textgrid"}
TEXT_SUFFIXES = {".txt"}
SUPPORTED_SUFFIXES = TEXTGRID_SUFFIXES | TEXT_SUFFIXES


def load_trial(path: Path) -> pd.DataFrame:
    """Load one transcript file into a one-row-per-word DataFrame."""
    suffix = path.suffix.lower()
    if suffix in TEXTGRID_SUFFIXES:
        return load_word_tier(path)
    if suffix in TEXT_SUFFIXES:
        return load_words_from_txt(path)
    raise ValueError(f"Unsupported file type: {path.name}")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing .TextGrid and/or .txt transcripts",
    )
    parser.add_argument(
        "--letter",
        default="p",
        help="Target letter for every trial in the directory (default: p)",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("data/processed"),
        help="Directory to write the output CSVs into (default: data/processed)",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        parser.error(f"Not a directory: {args.input_dir}")

    paths = sorted(
        p for p in args.input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not paths:
        parser.error(f"No .TextGrid or .txt files found in {args.input_dir}")

    all_words = []
    all_metrics = []
    for path in paths:
        words = load_trial(path)
        scored = score_trial(words, target_letter=args.letter)
        scored.insert(0, "source_file", path.name)
        all_words.append(scored)
        all_metrics.append({
            "source_file": path.name,
            "target_letter": args.letter,
            **compute_metrics(scored),
        })
        print(f"scored {path.name}  ({len(scored)} words)")

    args.outdir.mkdir(parents=True, exist_ok=True)
    words_csv = args.outdir / "pft_words.csv"
    metrics_csv = args.outdir / "pft_metrics.csv"
    pd.concat(all_words, ignore_index=True).to_csv(words_csv, index=False)
    pd.DataFrame(all_metrics).to_csv(metrics_csv, index=False)

    print(f"\n{len(paths)} trial(s) scored")
    print(f"wrote {words_csv}")
    print(f"wrote {metrics_csv}")


if __name__ == "__main__":
    main()
