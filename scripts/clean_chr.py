import logging
import os
import subprocess
import sys

logging.basicConfig(format='%(levelname)s | %(message)s', level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

def is_valid_utf8(s):
    try:
        s.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def count_lines(file_path):
    result = subprocess.run(["wc", "-l", file_path], capture_output=True, text=True)
    return int(result.stdout.strip().split()[0])

def main():

    chr_file_folder = sys.argv[1]
    chr_files = [bed for bed in os.listdir(chr_file_folder) if bed.endswith(".bed")]

    size_file_path = sys.argv[2]

    with open(size_file_path, "r") as f:
        chr_sizes = f.readlines()

    # chromosomes in hg38 ref
    hg38_chrs = {line.strip().split("\t")[0] for line in chr_sizes}
    # chromosomes in hg38 ref without "chr" prefix
    hg38_chrs.update({chr.replace("chr", "") for chr in hg38_chrs})

    for chr in hg38_chrs:
        if not chr.startswith("chr"):
            assert f"chr{chr}" in hg38_chrs

    out_of_hg38 = 0
    relocated = 0
    renamed = 0

    deleted_regions = 0
    corrected_regions = 0

    unvalid = 0

    for bed in chr_files:
        if not is_valid_utf8(bed):
            unvalid += 1
            os.remove(os.path.join(chr_file_folder, bed))
            continue

        chr_name = bed.replace(".bed", "")
        if chr_name not in hg38_chrs:
            line_count = count_lines(os.path.join(chr_file_folder, bed))
            _LOGGER.warning(
                f"{chr_name}({line_count} regions)is not included in hg38 references, {bed} is deleted."
            )
            deleted_regions += line_count
            os.remove(os.path.join(chr_file_folder, bed))
            out_of_hg38 += 1
        else:
            if not chr_name.startswith("chr"):
                line_count = count_lines(os.path.join(chr_file_folder, bed))
                target_file_name = f"chr{bed}"
                if os.path.exists(os.path.join(chr_file_folder, target_file_name)):
                    target_mode = "a"
                    relocated += 1
                else:
                    target_mode = "w"
                    renamed += 1

                _LOGGER.info(f"Write {line_count} regions from {bed} into {target_file_name}")
                with open(os.path.join(chr_file_folder, bed), "r") as source, open(
                    os.path.join(chr_file_folder, target_file_name), target_mode
                ) as target:
                    for region in source.readlines():
                        fields = region.strip().split("\t")
                        if len(fields) >= 3:
                            fields[0] = f"chr{fields[0].lstrip('chr')}"
                            target.write("\t".join(fields) + "\n")
                os.remove(os.path.join(chr_file_folder, bed))
                corrected_regions += line_count


    _LOGGER.info(f"{out_of_hg38} files not in hg38 references are deleted.")
    _LOGGER.info(f"{relocated} files merged with files with the correct name.")
    _LOGGER.info(f"{renamed} files renamed to correct name.")
    _LOGGER.info(f"{deleted_regions} regions are deleted.")
    _LOGGER.info(f"{corrected_regions} regions are corrected with chromosome names in hg38 reference.")
    _LOGGER.info(f"{unvalid} files names have invalid characters.")

if __name__ == "__main__":
    main()