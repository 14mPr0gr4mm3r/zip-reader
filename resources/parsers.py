"""
Zip Reader - Zip File Parsers
"""

from typing import Optional, Union

from .types import StreamLikeCharSequence, ZipEOCD
from .types import ZipCentralDirFileHeader, ZipLocalFileHeader
from .types import ZipCompressedFile

from .types import END_OF_CENTRAL_DIR_SIGNAT, CENTRAL_DIR_FH_SIGNAT
from .types import FILE_HEADER_SIGNAT, DATA_DESCRIPTOR_SIGNAT


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
