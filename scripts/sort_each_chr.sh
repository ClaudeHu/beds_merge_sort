#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

chr_dir="$1"
sorted_dir="${chr_dir}_sorted"
mkdir -p "$sorted_dir"

for chr_file in "$chr_dir"/*.bed; do
  chr_name="$(basename "$chr_file")"
  awk 'BEGIN{OFS="\t"}{print $1,$2,$3}' "$chr_file" | \
    sort -t $'\t' -k2,2n > "$sorted_dir/${chr_name%.bed}.sorted.bed"
done
