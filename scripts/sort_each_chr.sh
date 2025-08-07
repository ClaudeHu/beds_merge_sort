#!/bin/bash

chr_dir="$1"

sorted_dir="${chr_dir}_sorted"

mkdir -p "$sorted_dir"

# Get all .bed files
chr_files=("$chr_dir"/*.bed)


for chr_file in "${chr_files[@]}"; do
    chr_name=$(basename "$chr_file")  # Get filename with .bed extension

    paste <(awk -F'\t' '{print $1}' "$chr_file") \
      <(awk -F'\t' '{print $2}' "$chr_file" | sort -n)  > "$sorted_dir/$chr_name.sorted"

done
