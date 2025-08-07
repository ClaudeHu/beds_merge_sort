#!/bin/bash

SOURCE_DIR="$1"
WORK_DIR=$(dirname "$1")

DEST_DIR="$WORK_DIR/by_chromosomes"

mkdir -p "$DEST_DIR"


# Process each file
for file in "$SOURCE_DIR"/*; do
  [ -f "$file" ] || continue

  # Optional: Skip binary or corrupt files
  if ! head -c 1000 "$file" | grep -q "[[:print:]]"; then
    echo "Skipping binary or corrupt file: $file" >&2
    continue
  fi

  # Process and buffer lines by chromosome, then write them out at once
  awk -v out_dir="$DEST_DIR" '
    substr($0,1,1) != "#" {
      chr = $1
      gsub(/[^a-zA-Z0-9_.-]/, "_", chr)
      out_file = out_dir "/" chr ".bed"
      data[out_file] = data[out_file] $0 "\n"
    }
    END {
      for (f in data) {
        printf "%s", data[f] >> f
      }
    }
  ' "$file"

  # Update progress bar
done
