import struct
import zlib
from io import BufferedReader
from typing import Generator

from .proto import Blob, BlobHeader

__all__ = ["read_blocks"]


def read_blocks(f: BufferedReader) -> Generator[bytes, None, None]:
    """Return a generator of blocks of bytes from the given file.

    This corresponds to the fileformat part in the protobuf definitions.
    """
    while size_header := f.read(4):
        blob_header_size: int
        blob_header_size, *_ = struct.unpack("!L", size_header)

        blob: Blob = Blob.FromString(
            f.read(BlobHeader.FromString(f.read(blob_header_size)).datasize)
        )
        yield zlib.decompress(blob.zlib_data)
