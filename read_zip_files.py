"""
Zip Files Reader

@author Gustavo Sampaio (github.com/14mPr0gr4mm3r)
"""

import argparse
import os

from resources.parsers import get_eocd, get_central_directory_file_header
from resources.parsers import get_file_of_central_directory

from resources.util import show_file_of_central_directory, show_eocd
from resources.util import show_central_directory_file_header


def expand_zip_file(file_path: str):
    file_path = os.path.realpath(file_path)

    with open(file_path, "rb") as zip_file:
        file_content = zip_file.read()
        eocd = get_eocd(file_content)
        offset = eocd.central_directory_start_offset_on_archive
        central_directory_records_offsets = [offset]

        show_eocd(eocd)

        for _ in range(eocd.central_directory_total_record_count):
            central_directory_file_header, central_directory_length = get_central_directory_file_header(
                file_content, offset)
            central_directory_file = get_file_of_central_directory(
                central_directory_file_header, file_content)

            show_central_directory_file_header(
                central_directory_file_header, offset)
            show_file_of_central_directory(central_directory_file, tabs=1)

            offset += central_directory_length
            central_directory_records_offsets.append(offset)

        last_offset = 0
        size = 0

        for offs in central_directory_records_offsets:
            if last_offset != 0:
                size += offs - last_offset

            last_offset = offs

        assert size == eocd.central_directory_size


def main():
    parser = argparse.ArgumentParser(prog="read_zip_files")

    parser.add_argument(
        'ZIP_FILE', help="The .zip file to read and give informations about")

    args = parser.parse_args()

    expand_zip_file(args.ZIP_FILE)


if __name__ == '__main__':
    main()
