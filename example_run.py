"""Example: score a single plain-text PFT transcript and print the result.

To score a whole directory of transcripts (.txt and/or .TextGrid) and save
the results to CSV, use score_directory.py instead.

Setup (once):
    pip install -r requirements.txt
    python -c "import nltk; nltk.download('wordnet'); nltk.download('words')"

Usage:
    python example_run.py data/raw/transcripts/example1.txt
"""
import sys
from pathlib import Path

# Make the package importable when running this script directly, without
# having to install it first.
sys.path.insert(0, str(Path(__file__).parent))

from dementia_speech.io.text import load_words_from_txt
from dementia_speech.tasks.PFT_new.scoring import score_trial, compute_metrics


def main():
    txt_path = Path(sys.argv[1])
    df = load_words_from_txt(txt_path)
    scored = score_trial(df, target_letter="p")

    print(scored[["word", "classification"]].to_string(index=False))
    print()
    print(compute_metrics(scored))


if __name__ == "__main__":
    main()
