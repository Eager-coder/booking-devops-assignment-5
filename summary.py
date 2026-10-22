"""Validate a numeric CSV column and report descriptive statistics."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median, stdev


def summarize(path, column):
    """Reject missing/nonfinite values; require two observations for sample SD."""
    values = []
    with Path(path).open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or column not in reader.fieldnames:
            raise ValueError(f'Column not found: {column}')
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError('Duplicate column names')
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f'Extra fields at row {row_number}')
            try:
                value = float(row[column])
            except (TypeError, ValueError) as error:
                raise ValueError(f'Invalid number at row {row_number}') from error
            if not math.isfinite(value):
                raise ValueError(f'Nonfinite number at row {row_number}')
            values.append(value)
    if len(values) < 2:
        raise ValueError('At least two observations are required')
    result = dict(n=len(values), mean=mean(values), median=median(values),
                  minimum=min(values), maximum=max(values),
                  sample_sd=stdev(values))
    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError('Statistics exceed numeric range')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--column', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError('Input and output paths must differ')
        result = summarize(args.input, args.column)
        payload = dict(input_sha256=hashlib.sha256(
            args.input.read_bytes()).hexdigest(), column=args.column,
            statistics=result)
        args.output.write_text(json.dumps(payload, indent=2, allow_nan=False)
                               + '\n', encoding='utf-8')
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    main()
