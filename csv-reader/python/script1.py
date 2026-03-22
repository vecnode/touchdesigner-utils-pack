# TouchDesigner Text DAT: load project python/test.csv into Table DAT csv_table

from __future__ import annotations

import csv
from pathlib import Path

CSV_REL = Path("python") / "test.csv"


def csv_path() -> Path:
    return Path(project.folder).resolve() / CSV_REL


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open(mode="r", newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def fill_table(tab, rows: list[list[str]]) -> None:
    tab.clear()
    for row in rows:
        tab.appendRow(row)


def main() -> None:
    path = csv_path()
    if not path.is_file():
        raise tdError("CSV not found: {}".format(path))

    tab = op("csv_table")
    if tab is None:
        raise tdError('Table DAT "csv_table" not found.')

    fill_table(tab, read_csv_rows(path))


main()
