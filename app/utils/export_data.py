from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve()
APP_DIR = CURRENT_DIR.parents[1]

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.load_data import load_final_dataset


def export_final_dataset():
    df = load_final_dataset()

    output_dir = APP_DIR / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "final_dataset.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"Datasetul final a fost salvat în: {output_file}")


if __name__ == "__main__":
    export_final_dataset()