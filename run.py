import argparse
import logging
import os

import pypiper
from pypiper.manager import pipeline_filepath

logging.basicConfig(format="%(levelname)s | %(message)s", level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

SCRIPTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")

def main():
    parser = argparse.ArgumentParser(description="Process BED files.")
    parser.add_argument("bed_folder", type=str, help="Input BED folder")
    parser.add_argument("output_folder", type=str, help="Output folder")
    parser.add_argument(
        "chrom_size_ref_path", type=str, help="Chrom size reference file"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean temporary files after processing"
    )

    args = parser.parse_args()

    bed_folder = args.bed_folder
    output_folder = args.output_folder
    chrom_ref_path = args.chrom_size_ref_path
    clean = args.clean

    os.makedirs(output_folder, exist_ok=True)
    pm = pypiper.PipelineManager(
        name="merge_sort_large_scale_bed_files", outfolder=output_folder
    )

    # Step 1. Extract first 3 columns (chr, start, end) from all input beds)
    # step1_target = os.path.join(output_folder, "files_rows_total.out")
    step1_script_path = os.path.join(SCRIPTS_FOLDER, "get_chr_start_end.sh")
    step1_commands = [
        f"chmod +x {step1_script_path}",
        # f"./scripts/get_chr_start_end.sh {bed_folder} {output_folder} > {step1_target}",
        f"{step1_script_path} {bed_folder} {output_folder}",
    ]

    pm.run(step1_commands, os.path.join(output_folder, "lock.max"))

    # Step 2.
    step2_script_path = os.path.join(SCRIPTS_FOLDER, "group_by_chr.sh")
    step2_commands = [
        f"chmod +x {step2_script_path}",
        f"{step2_script_path} {os.path.join(output_folder, 'chr_start_end')}",
    ]

    # pm.run(step2_commands, target=step2_target)
    pm.run(step2_commands, os.path.join(output_folder, "lock.max"))

    # check intermediate file
    if clean:
        pm.clean_add(pipeline_filepath(pm, "chr_start_end/*.bed"))
        pm.clean_add(pipeline_filepath(pm, "chr_start_end"))

    # Step 3. Clean chromosomes
    step3_script_path = os.path.join(SCRIPTS_FOLDER, "clean_chr.py")
    step3_command = f"python {step3_script_path} {os.path.join(output_folder, 'by_chromosomes')} {chrom_ref_path}"
    pm.run(step3_command, os.path.join(output_folder, "lock.max"))

    # Step 4. Sort each chromosome's file
    step4_script_path = os.path.join(SCRIPTS_FOLDER, "sort_each_chr.sh")
    step4_commands = [
        f"chmod +x {step4_script_path}",
        f"{step4_script_path} {os.path.join(output_folder, 'by_chromosomes')}",
    ]

    pm.run(step4_commands, os.path.join(output_folder, "lock.max"))

    # check intermediate file
    if clean:
        pm.clean_add(pipeline_filepath(pm, "by_chromosomes/*.bed"))
        pm.clean_add(pipeline_filepath(pm, "by_chromosomes"))

    # Step 5. Merge
    sorted_file = os.path.join(output_folder, "combined_chrsort.bed")
    step5_commands = [
        f"find {os.path.join(output_folder, 'by_chromosomes_sorted')} -maxdepth 1 -name '*.sorted' | sort -V | xargs cat > {sorted_file}",
        f'echo "$(wc -l < {sorted_file}) start-end sorted in total"',
    ]

    pm.run(step5_commands, sorted_file)

    # check intermediate file
    if clean:
        pm.clean_add(pipeline_filepath(pm, "by_chromosomes_sorted/*.bed.sorted"))
        pm.clean_add(pipeline_filepath(pm, "by_chromosomes_sorted"))

    pm.stop_pipeline()


if __name__ == "__main__":
    main()
