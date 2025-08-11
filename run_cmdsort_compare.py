import argparse
import os

import pypiper
from pypiper.manager import pipeline_filepath


def main():
    parser = argparse.ArgumentParser(description="Process BED files.")
    parser.add_argument("bed_folder", type=str, help="Input BED folder")
    parser.add_argument("output_folder", type=str, help="Output folder")
    parser.add_argument(
        "--clean", action="store_true", help="Clean temporary files after processing"
    )

    args = parser.parse_args()

    bed_folder = args.bed_folder
    output_folder = args.output_folder
    clean = args.clean

    os.makedirs(output_folder, exist_ok=True)
    pm = pypiper.PipelineManager(name="cmd_merge_sort", outfolder=output_folder)

    combined_bed_path = os.path.join(output_folder, "combined_unsort.bed")
    merge_command = f"find {bed_folder} -type f -name '*.bed' -print0 | xargs -0 cat > {combined_bed_path}"
    pm.run(merge_command, combined_bed_path)

    sorted_bed_path = os.path.join(output_folder, "combined_chrsort.bed")
    sort_command = f"sort -k1,1V -k2,2n {combined_bed_path} > {sorted_bed_path}"
    pm.run(sort_command, sorted_bed_path)

    if clean:
        pm.clean_add(pipeline_filepath(pm, "*unsort*"))
    pm.stop_pipeline()


if __name__ == "__main__":
    main()
