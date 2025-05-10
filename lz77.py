import math
import time
import re


def bits_to_bytes(bits):
    """Преобразует список битов в массив байтов."""
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            byte.extend([0] * (8 - len(byte)))
        byte_value = int(''.join(map(str, byte)), 2)
        byte_array.append(byte_value)
    return byte_array


def bytes_to_bits(byte_array):
    """Преобразует массив байтов в список битов."""
    bits = []
    for byte in byte_array:
        bits.extend([int(b) for b in bin(byte)[2:].zfill(8)])
    return bits


def lz77_compress(text, window_size, buffer_size):
    """
    Сжимает текст с помощью алгоритма LZ77.
    Возвращает: словарь с массивом байтов сжатого текста, читаемой последовательностью и статистикой.
    """
    start_time = time.time()

    compressed_bits = []
    triples = []
    encoded_sequence = []
    i = 0

    offset_bits_count = math.ceil(math.log2(window_size)) if window_size > 0 else 1
    length_bits_count = math.ceil(math.log2(buffer_size + 1)) if buffer_size > 0 else 1

    while i < len(text):
        best_length = 0
        best_offset = 0
        best_char = text[i] if i < len(text) else ''

        window_start = max(0, i - window_size)
        window = text[window_start:i]

        for j in range(len(window)):
            length = 0
            while (length < buffer_size and
                   i + length < len(text) and
                   j + length < len(window) and
                   window[j + length] == text[i + length]):
                length += 1

            if length > best_length:
                best_length = length
                best_offset = i - (j + window_start)
                best_char = text[i + length] if i + length < len(text) else ''

        if best_length > 0:
            compressed_bits.append(1)
            offset_bits = bin(best_offset)[2:].zfill(offset_bits_count)
            compressed_bits.extend(map(int, offset_bits))
            length_bits = bin(best_length)[2:].zfill(length_bits_count)
            compressed_bits.extend(map(int, length_bits))
            if best_char:
                char_bits = bin(ord(best_char))[2:].zfill(8)
                compressed_bits.extend(map(int, char_bits))
            triples.append((best_offset, best_length, best_char))
            encoded_sequence.append(f"({best_offset},{best_length},{best_char})")
            i += best_length + 1
        else:
            compressed_bits.append(0)
            char_bits = bin(ord(best_char))[2:].zfill(8)
            compressed_bits.extend(map(int, char_bits))
            triples.append((0, 0, best_char))
            encoded_sequence.append(f"(0,0,{best_char})")
            i += 1

    while len(compressed_bits) % 8 != 0:
        compressed_bits.append(0)

    compressed_bytes = bits_to_bytes(compressed_bits)

    end_time = time.time()
    compression_time = (end_time - start_time) * 1000

    # Вычисляем статистику
    original_size = len(text.encode('utf-8'))
    compressed_size = len(compressed_bytes)
    compression_ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0

    return {
        'compressed_bytes': compressed_bytes,
        'encoded_sequence': " ".join(encoded_sequence),
        'original_size': original_size,
        'compressed_size': compressed_size,
        'compression_ratio': compression_ratio,
        'compression_time': compression_time
    }


def lz77_decompress(compressed_bytes, window_size, buffer_size):
    """
    Декомпрессирует данные, сжатые алгоритмом LZ77.
    Аргументы:
        compressed_bytes: массив байтов сжатого текста
        window_size: размер окна поиска
        buffer_size: размер буфера предпросмотра
    Возвращает: словарь с восстановленным текстом и статистикой.
    """
    start_time = time.time()

    bits = bytes_to_bits(compressed_bytes)

    offset_bits_count = math.ceil(math.log2(window_size)) if window_size > 0 else 1
    length_bits_count = math.ceil(math.log2(buffer_size + 1)) if buffer_size > 0 else 1

    output = []
    bit_index = 0

    while bit_index < len(bits):
        flag = bits[bit_index]
        bit_index += 1

        if flag == 1:
            if bit_index + offset_bits_count > len(bits):
                break
            offset_bits = bits[bit_index:bit_index + offset_bits_count]
            offset = int(''.join(map(str, offset_bits)), 2)
            bit_index += offset_bits_count

            if bit_index + length_bits_count > len(bits):
                break
            length_bits = bits[bit_index:bit_index + length_bits_count]
            length = int(''.join(map(str, length_bits)), 2)
            bit_index += length_bits_count

            next_char = ''
            if bit_index + 8 <= len(bits):
                char_bits = bits[bit_index:bit_index + 8]
                char_code = int(''.join(map(str, char_bits)), 2)
                next_char = chr(char_code) if char_code != 0 else ''
                bit_index += 8

            if length > 0:
                start = len(output) - offset
                for i in range(length):
                    if start + i < len(output):
                        output.append(output[start + i])
                    else:
                        break
            if next_char:
                output.append(next_char)

        else:
            if bit_index + 8 > len(bits):
                break
            char_bits = bits[bit_index:bit_index + 8]
            char_code = int(''.join(map(str, char_bits)), 2)
            output.append(chr(char_code))
            bit_index += 8

    decompressed_text = ''.join(output)
    end_time = time.time()
    decompression_time = end_time - start_time

    # Вычисляем статистику
    compressed_size = len(compressed_bytes)
    decompressed_size = len(decompressed_text.encode('utf-8'))

    return {
        'decompressed_text': decompressed_text,
        'decompression_time': decompression_time,
        'compressed_size': compressed_size,
        'decompressed_size': decompressed_size
    }


def lz77_decompress_from_sequence(sequence: str, window_size: int, buffer_size: int):
    import time
    start_time = time.time()

    pattern = r'\((\d+),(\d+),([^\)]*)\)'
    matches = re.findall(pattern, sequence)

    if not matches:
        raise ValueError("Формат последовательности некорректен")

    result = ''
    for offset, length, symbol in matches:
        offset = int(offset)
        length = int(length)

        if offset > len(result):
            raise ValueError(f"Offset {offset} выходит за пределы результата длиной {len(result)}")

        start = len(result) - offset
        for _ in range(length):
            result += result[start]
            start += 1

        result += symbol

    return {
        'decompressed_text': result,
        'decompression_time': (time.time() - start_time) * 1000,
        'compressed_size': len(sequence.encode('utf-8')),
        'decompressed_size': len(result.encode('utf-8')),
    }
