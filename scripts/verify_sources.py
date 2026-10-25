"""Optional audit of supplied PDFs. Run from repository root after installing .[dev]."""
import hashlib
from pathlib import Path

from pypdf import PdfReader
from equitylens.data import DATA_DIR, load_data


def main():
    data, sources = load_data()
    root = DATA_DIR.parent
    for source in sources.itertuples():
        path = root / source.local_path
        if not path.is_file():
            raise SystemExit(f"Missing report: {path}. Restore the supplied PDF to audit it.")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source.sha256:
            raise SystemExit(f"Report hash mismatch: {path}")
        count = len(PdfReader(path).pages)
        pages = data.loc[(data.source_id == source.source_id) & data.value.notna(), "source_page"]
        if not pages.between(1, count).all():
            raise SystemExit(f"Page reference outside report: {source.source_id}")
        print(f"OK {source.source_id}: hash matches; {len(pages)} references within {count} pages")
    print("File identity and page bounds verified. Financial meaning still requires reviewing the cited tables.")


if __name__ == "__main__":
    main()
