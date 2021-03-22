"""
Zip Files Reader

@author Gustavo Sampaio (github.com/14mPr0gr4mm3r)
"""

import zlib
from zipfile import _get_decompressor as get_decompressor
import argparse
from typing import Union, Optional
from dataclasses import dataclass
from enum import Enum

FILE_HEADER_SIGNAT = 0x04034b50
DATA_DESCRIPTOR_SIGNAT = 0x08074b50
CENTRAL_DIR_FH_SIGNAT = 0x02014b50
END_OF_CENTRAL_DIR_SIGNAT = 0x06054b50


class StreamLikeCharSequence():
    def __init__(self, base_sequence: Union[str, bytes]):
        self.__charseq = base_sequence

    def __repr__(self):
        return repr(self.__charseq)

    def read(self, length: int = -1) -> str:
        value = self.__charseq[:length]

        self.__charseq = self.__charseq[length:]

        return value


class ZipCompressionMethod(Enum):
    STORED = 0
    DEFLATE = 8


@dataclass
class ZipLocalFileHeader():
    signature: int
    version: int
    gp_bit_flag: int
    compression_method: ZipCompressionMethod
    last_modified_time: int
    last_modified_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    filename_length: int
    extra_field_length: int
    filename: Union[str, bytes]
    extra_field: Union[str, bytes]


@dataclass
class ZipCentralDirFileHeader():
    signature: int
    version_made_by: int
    version: int
    gp_bit_flag: int
    compression_method: ZipCompressionMethod
    last_modification_time: int
    last_modification_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    filename_length: int
    extra_field_length: int
    file_comment_length: int
    disk_number: int
    internal_file_attributes: int
    external_file_attributes: int
    file_offset: int
    filename: Union[str, bytes]
    extra_field: Union[str, bytes]
    file_comment: Union[str, bytes]


@dataclass
class ZipEOCD():
    signature: int
    disk_number: int
    central_directory_start_disk_number: int
    central_directory_record_count_on_disk: int
    central_directory_total_record_count: int
    central_directory_size: int
    central_directory_start_offset_on_archive: int
    comment_length: int
    comment: Union[str, bytes]


class ZipCompressedFile():
    def __init__(self,
                 local_header: ZipLocalFileHeader,
                 compressed_data: bytes,
                 crc32: int,
                 compressed_size: int,
                 uncompressed_size: int):

        self.local_header = local_header
        self.compressed_data = compressed_data
        self.crc32 = crc32
        self.compressed_size = compressed_size
        self.uncompressed_size = uncompressed_size

        if self.local_header.compression_method == ZipCompressionMethod.DEFLATE.value:
            self._decompress_data()

            try:
                self.content = self.uncompressed_data.decode()
            except UnicodeDecodeError:
                self.content = self.uncompressed_data
        else:
            self.content = self.compressed_data

        self._validate_data()

    def _decompress_data(self):
        decompressor = get_decompressor(self.local_header.compression_method)

        self.uncompressed_data = decompressor.decompress(self.compressed_data)

    def _validate_data(self):
        assert len(
            self.compressed_data) == self.compressed_size, f'compressed data length is {len(self.compressed_data)}, while the annotated uncompressed data length was {self.compressed_size}'

        if self.local_header.compression_method == ZipCompressionMethod.DEFLATE.value or hasattr(self, 'uncompressed_data'):
            assert len(
                self.uncompressed_data) == self.uncompressed_size, f'uncompressed data length is {len(self.uncompressed_data)}, while the annotated uncompressed data length was {self.uncompressed_size}'

            uncompressed_data_crc32 = zlib.crc32(self.uncompressed_data)
            assert uncompressed_data_crc32 == self.crc32, f'CRC32 does not match: expected {self.crc32}, received {uncompressed_data_crc32}'


def get_eocd(content: Union[str, bytes]):
    signature_offset = content.find(
        END_OF_CENTRAL_DIR_SIGNAT.to_bytes(4, "little"))

    footer_content = StreamLikeCharSequence(content[signature_offset:])

    signature = int.from_bytes(footer_content.read(4), "little")
    disk_number = int.from_bytes(footer_content.read(2), "little")
    cd_start_disk_number = int.from_bytes(footer_content.read(2), "little")
    cd_record_count_on_disk = int.from_bytes(footer_content.read(2), "little")
    total_cd_record_count = int.from_bytes(footer_content.read(2), "little")
    cd_size = int.from_bytes(footer_content.read(4), "little")
    cd_start_archive_offset = int.from_bytes(footer_content.read(4), "little")
    comment_length = int.from_bytes(footer_content.read(2), "little")
    comment = footer_content.read(comment_length)

    return ZipEOCD(signature, disk_number, cd_start_disk_number,
                   cd_record_count_on_disk, total_cd_record_count, cd_size,
                   cd_start_archive_offset, comment_length, comment)


def get_central_directory_file_header(content, signature_offset: Optional[int] = None):
    if signature_offset is None:
        signature_offset = content.find(
            CENTRAL_DIR_FH_SIGNAT.to_bytes(4, "little"))

    header_content = StreamLikeCharSequence(content[signature_offset:])

    signature = int.from_bytes(header_content.read(4), "little")
    version_made_by = header_content.read(2)
    version = int.from_bytes(header_content.read(2), "little")
    gp_bit_flag = int.from_bytes(header_content.read(2), "little")
    compression_method = int.from_bytes(header_content.read(2), "little")
    last_modification_time = int.from_bytes(header_content.read(2), "little")
    last_modification_date = int.from_bytes(header_content.read(2), "little")
    crc32 = int.from_bytes(header_content.read(4), "little")
    compressed_size = int.from_bytes(header_content.read(4), "little")
    uncompressed_size = int.from_bytes(header_content.read(4), "little")
    filename_length = int.from_bytes(header_content.read(2), "little")
    extra_field_length = int.from_bytes(header_content.read(2), "little")
    file_comment_length = int.from_bytes(header_content.read(2), "little")
    disk_number = int.from_bytes(header_content.read(2), "little")
    int_file_attributes = int.from_bytes(header_content.read(2), "little")
    ext_file_attributes = int.from_bytes(header_content.read(4), "little")
    file_offset = int.from_bytes(header_content.read(4), "little")
    filename = header_content.read(filename_length)
    extra_field = header_content.read(extra_field_length)
    file_comment = header_content.read(file_comment_length)

    return ZipCentralDirFileHeader(signature, version_made_by, version,
                                   gp_bit_flag, compression_method, last_modification_time,
                                   last_modification_date, crc32, compressed_size,
                                   uncompressed_size, filename_length, extra_field_length,
                                   file_comment_length, disk_number, int_file_attributes,
                                   ext_file_attributes, file_offset, filename,
                                   extra_field, file_comment), 46 + filename_length + extra_field_length + file_comment_length


def get_local_file_header(f):
    file_header_signature = int.from_bytes(f.read(4), "little")

    assert file_header_signature == FILE_HEADER_SIGNAT

    version = int.from_bytes(f.read(2), "little")
    gp_bit_flag = int.from_bytes(f.read(2), "little")
    compres_method = int.from_bytes(f.read(2), "little")
    last_modif_time = int.from_bytes(f.read(2), "little")
    last_modif_date = int.from_bytes(f.read(2), "little")
    crc32 = int.from_bytes(f.read(4), "little")
    compres_size = int.from_bytes(f.read(4), "little")
    uncompres_size = int.from_bytes(f.read(4), "little")
    filename_len = int.from_bytes(f.read(2), "little")
    extra_len = int.from_bytes(f.read(2), "little")
    filename = f.read(filename_len)
    extra_field = f.read(extra_len)

    return (ZipLocalFileHeader(file_header_signature, version, gp_bit_flag,
                               compres_method, last_modif_time, last_modif_date,
                               crc32, compres_size, uncompres_size,
                               filename_len, extra_len, filename,
                               extra_field), 30 + filename_len + extra_len)


def get_file_of_central_directory(central_dir_file_header: ZipCentralDirFileHeader, content):
    stream = StreamLikeCharSequence(
        content[central_dir_file_header.file_offset:])
    local_header, _read_chunk_len = get_local_file_header(stream)

    gp_bit_flag = local_header.gp_bit_flag
    crc32, compres_size, uncompres_size = local_header.crc32, local_header.compressed_size, local_header.uncompressed_size

    if gp_bit_flag & 0x08:
        compressed_data = stream.read(central_dir_file_header.compressed_size)

        chunk = stream.read(4)
        chunk_is_signature = chunk == DATA_DESCRIPTOR_SIGNAT.to_bytes(
            4, "little")

        crc32 = int.from_bytes(stream.read(
            4) if chunk_is_signature else chunk, "little")
        compres_size, uncompres_size = int.from_bytes(stream.read(
            4), "little"), int.from_bytes(stream.read(4), "little")
    else:
        compressed_data = stream.read(compres_size)

    return ZipCompressedFile(local_header, compressed_data, crc32, compres_size, uncompres_size)


def show_file_of_central_directory(file: ZipCompressedFile, tabs=0):
    print('\033[32m')

    print('\t'*tabs, 'File Header Signature:',
          hex(file.local_header.signature))
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


def expand_zip_file(file_path: str):
    with open(file_path, "rb") as zip_file:
        file_content = zip_file.read()
        eocd = get_eocd(file_content)
        offset = eocd.central_directory_start_offset_on_archive
        central_directory_records_offsets = [offset]

        print(f'\033[34m{str(eocd)}\033[m')

        for _ in range(eocd.central_directory_total_record_count):
            central_directory_file_header, central_directory_length = get_central_directory_file_header(
                file_content, offset)
            central_directory_file = get_file_of_central_directory(
                central_directory_file_header, file_content)

            print(f'\n{offset} |\033[31m',
                  central_directory_file_header, end='\033[m\n\n')
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
