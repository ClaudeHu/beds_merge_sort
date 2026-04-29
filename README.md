| method       | time   | peak mem  |
|--------------|--------|-----------|
| direct sort  | 1.44 s | 0.2513 GB |
| sort by chr  | 5.49 s | 0.012 GB  |

# beds_merge_sort

Utilities for sorting and merging BED-like interval files with an emphasis on practical performance and memory usage.

This repository contains scripts/experiments for comparing approaches to sorting BED records (e.g., a single direct sort vs sorting by chromosome groups) and producing merge-ready, position-sorted output.

## Requirements

- Python 3.8+ (recommended)
- A POSIX shell environment
- Common Unix CLI tools (e.g., `sort`, `awk`, `grep`)

## Installation

Clone the repository:

```bash
git clone https://github.com/databio/beds_merge_sort.git
cd beds_merge_sort
```

If the repo includes Python dependencies in the future (e.g., `requirements.txt`), you can install them with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
# pip install -r requirements.txt
```

## Usage

The repo is intended to be run from the command line. Specific commands depend on the scripts present in the repository.

### Direct sort (single global sort)

Typical BED sorting keys are chromosome, start, end:

```bash
sort -k1,1 -k2,2n -k3,3n input.bed > sorted.bed
```

### Sort by chromosome groups (reduce peak memory)

A common strategy is:

1. partition rows by chromosome
2. sort each chromosome independently
3. concatenate chromosomes in a defined order

Example outline (adjust to your workflow/scripts):

```bash
# Create an explicit chromosome order (example)
cat > chrom.order << 'EOF'
chr1
chr2
chr3
EOF

# For each chromosome, filter and sort numerically by start/end
while read -r chr; do
  awk -v c="$chr" '$1==c' input.bed | sort -k2,2n -k3,3n
done < chrom.order > sorted.by_chr.bed
```

Notes:
- This can greatly reduce peak memory compared to a single global sort, at the cost of more total time and extra passes over the data.
- For real genomes, use a complete chromosome order list (including `chrX`, `chrY`, `chrM`, etc. as needed).

## Input / Output

### Input

A tab-delimited, BED-like file with at least:

- column 1: chromosome / reference name (string)
- column 2: start coordinate (integer; typically 0-based in BED)
- column 3: end coordinate (integer)

Additional columns are preserved and carried through the sort.

### Output

A file sorted by:

1. chromosome (according to lexicographic order or your explicit chromosome list)
2. start coordinate (numeric ascending)
3. end coordinate (numeric ascending; optional tiebreak)

## Notes & assumptions

- Chromosome ordering matters:
  - Lexicographic order may be undesirable (e.g., `chr10` sorts before `chr2`).
  - Prefer an explicit chromosome order file if you need “natural” genomic ordering.
- Ensure consistent delimiters (tabs/spaces) and valid integer coordinates; malformed lines can break numeric sorting.
- If you plan to merge intervals after sorting, ensure your downstream merge tool expects the same coordinate conventions (0-based vs 1-based).

## Benchmarks

The table at the top of this README summarizes a benchmark comparison between two approaches:

- **direct sort**: one global sort
- **sort by chr**: per-chromosome sorting (often lower peak memory)

To reproduce benchmarks, rerun the scripts/commands in this repo on the same dataset and record:

- wall-clock time
- peak memory usage

If you add benchmark scripts, consider documenting:
- dataset characteristics (rows, file size, number of chromosomes)
- machine specs (CPU, RAM, disk)
- exact command lines used

## Contributing

Issues and pull requests are welcome. If you add or modify scripts, please include:

- what the script does (one paragraph)
- expected input/output format
- a minimal example command
- any performance notes or trade-offs

## License

No license is currently documented in this README. If you intend others to reuse this code, add a `LICENSE` file (e.g., MIT, BSD-2-Clause, Apache-2.0).
