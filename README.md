# zip-reader

A weak implementation of a "ZIP reader", using the standard structures definitions

## Example

To see it working, you can run:

```shell
python3 read_zip_files.py example.zip
```

And you'll see some output:

```shell
ZipEOCD(signature=101010256, disk_number=0, central_directory_start_disk_number=0, central_directory_record_count_on_disk=2, central_directory_total_record_count=2, central_directory_size=182, central_directory_start_offset_on_archive=189, comment_length=0, comment=b'')

189 | ZipCentralDirFileHeader(signature=33639248, version_made_by=b'\x14\x03', version=20, gp_bit_flag=0, compression_method=0, last_modification_time=21251, last_modification_date=21110, crc32=0, compressed_size=0, uncompressed_size=0, filename_length=9, extra_field_length=32, file_comment_length=0, disk_number=0, internal_file_attributes=0, external_file_attributes=1106051072, file_offset=0, filename=b'zip-test/', extra_field=b'UT\r\x00\x07v\x9aX`v\x9aX`v\x9aX`ux\x0b\x00\x01\x04\xf5\x01\x00\x00\x04\x14\x00\x00\x00', file_comment=b'')


	 File Header Signature: 0x4034b50
	 GP Bit Flag: 0
	 Compress. Method: 0
	 Last Modified Time: 21251
	 Last Modified Date: 21110
	 Filename: b'zip-test/'
	 Extra Field: b'UT\r\x00\x07v\x9aX`v\x9aX`v\x9aX`ux\x0b\x00\x01\x04\xf5\x01\x00\x00\x04\x14\x00\x00\x00'
	 CRC32: 0x0
	 Compressed Size: 0
	 Uncompressed Size: 0


276 | ZipCentralDirFileHeader(signature=33639248, version_made_by=b'\x14\x03', version=20, gp_bit_flag=0, compression_method=8, last_modification_time=18795, last_modification_date=21110, crc32=2673768754, compressed_size=39, uncompressed_size=39, filename_length=17, extra_field_length=32, file_comment_length=0, disk_number=0, internal_file_attributes=0, external_file_attributes=2175008768, file_offset=71, filename=b'zip-test/file.txt', extra_field=b'UT\r\x00\x07k\x89X`w\x9aX`v\x9aX`ux\x0b\x00\x01\x04\xf5\x01\x00\x00\x04\x14\x00\x00\x00', file_comment=b'')


	 File Header Signature: 0x4034b50
	 GP Bit Flag: 0
	 Compress. Method: 8
	 Last Modified Time: 18795
	 Last Modified Date: 21110
	 Filename: b'zip-test/file.txt'
	 Extra Field: b'UT\r\x00\x07k\x89X`w\x9aX`v\x9aX`ux\x0b\x00\x01\x04\xf5\x01\x00\x00\x04\x14\x00\x00\x00'
	 CRC32: 0x9f5e7932
	 Compressed Size: 39
	 Uncompressed Size: 39
	 Data:
	 Hello, World! This is a message, right?


```
