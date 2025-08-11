#!/bin/bash

SOURCE_DIR="$1"
# WORK_DIR=$(dirname "$1")
WORK_DIR="$2"

DEST_DIR="$WORK_DIR/chr_start_end"
mkdir -p "$DEST_DIR"

# Use mapfile to get all matching files
mapfile -t FILES_ARRAY < <(find "$SOURCE_DIR" -maxdepth 1 -type f \( \
  -name "*.bed" -o \
  -name "*.bed.gz" -o \
  -name "*.bed.bz2" -o \
  -name "*.narrowPeak.gz" -o \
  -name "*.narrowPeak.bz2" -o \
  -name "*.broadPeak.gz" -o \
  -name "*.broadpeak.gz" \
\))

TOTAL_FILES=${#FILES_ARRAY[@]}
COUNT=0
LINE_COUNT=0

# Main processing loop
for FILE_PATH in "${FILES_ARRAY[@]}"; do
    ((COUNT++))

    FILE_NAME=$(basename "$FILE_PATH")

    # Determine decompression
    if [[ "$FILE_NAME" == *.gz ]]; then
        DECOMP_CMD="gunzip -c"
        OUT_NAME="${FILE_NAME%.gz}"
    elif [[ "$FILE_NAME" == *.bz2 ]]; then
        DECOMP_CMD="bunzip2 -c"
        OUT_NAME="${FILE_NAME%.bz2}"
    else
      DECOMP_CMD="cat"
      OUT_NAME="$FILE_NAME"
    fi

    OUTPUT_FILE="$DEST_DIR/$OUT_NAME"

    if $DECOMP_CMD "$FILE_PATH" | awk -v FILENAME="$FILE_NAME" '
        BEGIN { OFS="\t" }
        {
            if ($0 ~ /^#/) next;
            if (NF < 3) next;
            if ($0 ~ /�/) {
                if (!warned++) {
                    print "Warning: invalid UTF-8 in " FILENAME > "/dev/stderr"
                }
                next;
            }
            print $1, $2, $3;
        }
    ' > "$OUTPUT_FILE"; then
        LC=$(wc -l < "$OUTPUT_FILE")
        LINE_COUNT=$((LINE_COUNT + LC))
    else
        echo "ERROR: Failed to process $FILE_NAME" >&2
    fi
done

echo "Successfully processed $COUNT files (with possible skips), $LINE_COUNT regions in total."
