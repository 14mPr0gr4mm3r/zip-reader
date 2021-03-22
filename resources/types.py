"""
Zip Reader - Zip File Objects Types
"""

import zlib
from zipfile import _get_decompressor as get_decompressor

from typing import Union
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
