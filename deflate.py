import zlib
import time
import sys


def deflate_compress(text):
    """
    Compress a string using DEFLATE algorithm (zlib).
    Returns a dictionary with compressed bytes and statistics.
    """
    try:
        data = text.encode('utf-8')
        original_size = len(data)

        start_time = time.time()
        compressed_data = zlib.compress(data, level=9)
        compression_time = (time.time() - start_time) * 1000

        compressed_size = len(compressed_data)
        # Исправленная формула для процента сжатия
        compression_ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0

        return {
            'compressed_bytes': compressed_data,
            'compression_time': compression_time,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio
        }

    except Exception as e:
        raise Exception(f"Error during compression: {str(e)}")


def deflate_decompress(compressed_bytes):
    try:
        start_time = time.time()
        decompressed_data = zlib.decompress(compressed_bytes)
        decompression_time = (time.time() - start_time) * 1000

        decompressed_text = decompressed_data.decode('utf-8')
        compressed_size = len(compressed_bytes)
        decompressed_size = len(decompressed_data)

        return {
            'decompressed_text': decompressed_text,
            'decompression_time': decompression_time,
            'compressed_size': compressed_size,
            'decompressed_size': decompressed_size
        }

    except zlib.error:
        raise Exception("Invalid compressed data or not a DEFLATE-compressed file")
    except Exception as e:
        raise Exception(f"Error during decompression: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python deflate.py <input_file> <output_file> [--decompress]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    decompress = len(sys.argv) > 3 and sys.argv[3] == "--decompress"

    if decompress:
        with open(input_file, 'rb') as f:
            compressed_bytes = f.read()
        result = deflate_decompress(compressed_bytes)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['decompressed_text'])
        print(f"Decompression successful: {input_file} -> {output_file}")
        print(f"Compressed size: {result['compressed_size']} bytes")
        print(f"Decompressed size: {result['decompressed_size']} bytes")
    else:
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        result = deflate_compress(text)
        with open(output_file, 'wb') as f:
            f.write(result['compressed_bytes'])
        print(f"Compression successful: {input_file} -> {output_file}")
        print(f"Original size: {result['original_size']} bytes")
        print(f"Compressed size: {result['compressed_size']} bytes")
        print(f"Compression ratio: {result['compression_ratio']:.2f}%")
