import brotli
import time
import os


def brotli_compress(input_data):
    """
    Compress input data (string or file) using Brotli algorithm.
    Returns a dictionary with compression statistics.
    """
    start_time = time.time()

    if os.path.isfile(input_data):
        with open(input_data, 'rb') as f:
            data = f.read()
        original_size = os.path.getsize(input_data)
    else:
        data = input_data.encode('utf-8')
        original_size = len(data)

    compressed_data = brotli.compress(data)
    compressed_size = len(compressed_data)

    compression_time = (time.time() - start_time) * 1000
    compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

    return {
        'compressed_bytes': compressed_data,
        'compression_time': compression_time,
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio
    }


def brotli_decompress(compressed_file):
    """
    Decompress a Brotli-compressed file.
    Returns a dictionary with the decompressed text and statistics.
    """
    start_time = time.time()

    with open(compressed_file, 'rb') as f:
        compressed_data = f.read()

    decompressed_data = brotli.decompress(compressed_data)
    decompressed_text = decompressed_data.decode('utf-8')

    decompression_time = (time.time() - start_time) * 1000
    compressed_size = os.path.getsize(compressed_file)
    decompressed_size = len(decompressed_data)

    return {
        'decompressed_text': decompressed_text,
        'decompression_time': decompression_time,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size
    }
