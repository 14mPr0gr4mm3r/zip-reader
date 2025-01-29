"""
Zip Reader - Utility Functions
"""

from .types import ZipCompressedFile, ZipEOCD, ZipCentralDirFileHeader


def show_central_directory_file_header(cd_file_header: ZipCentralDirFileHeader, offset: int):
    print(f'\n{offset} |\033[31m', cd_file_header, end='\033[m\n\n')


def show_eocd(eocd: ZipEOCD):
    print(f'\033[34m{str(eocd)}\033[m')


def show_file_of_central_directory(file: ZipCompressedFile, tabs=0):
    print('\033[32m')

    print('\t'*tabs, 'File Header Signature:', file.local_header.signature)
    print('\t'*tabs, 'Version:', file.local_header.version / 10)
    print('\t'*tabs, 'GP Bit Flag:', file.local_header.gp_bit_flag)
    print('\t'*tabs, 'Compress. Method:', file.local_header.compression_method)
    print('\t'*tabs, 'Last Modified Time:',
          file.local_header.last_modified_time)
    print('\t'*tabs, 'Last Modified Date:',
          file.local_header.last_modified_date)

    print('\t'*tabs, 'Filename:', file.local_header.filename)
    print('\t'*tabs, 'Extra Field:', file.local_header.extra_field)

    print('\t'*tabs, 'CRC32:', hex(file.crc32))
    print('\t'*tabs, 'Compressed Size:', file.compressed_size)
    print('\t'*tabs, 'Uncompressed Size:', file.uncompressed_size)

    if file.compressed_size or file.uncompressed_size:
        print('\t'*tabs, 'Data:')
        print('\t'*tabs, file.content)

    print('\033[m')
