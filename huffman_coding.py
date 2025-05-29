import heapq
from collections import Counter
from bitstring import BitArray
from huffman_node import HuffmanNode


def build_huffman_tree(freq_map):
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]


def build_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        build_codes(node.left, prefix + "0", codebook)
        build_codes(node.right, prefix + "1", codebook)
    return codebook


def compress(input_file, output_file):
    # Чтение входного текста
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    if not text:
        with open(output_file, 'wb') as file:
            file.write(b'')
        return

    # Построение частот и дерева Хаффмана
    freq_map = Counter(text)
    huffman_tree = build_huffman_tree(freq_map)
    codebook = build_codes(huffman_tree)

    # Канонические коды: сортируем по длине кода и символу
    sorted_chars = sorted(codebook.keys(), key=lambda char: (len(codebook[char]), char))
    code_lengths = {char: len(codebook[char]) for char in sorted_chars}

    # Проверка максимальной длины кода
    max_code_length = max(code_lengths.values()) if code_lengths else 0
    if max_code_length > 31:
        raise ValueError(f"Длина кода Хаффмана ({max_code_length}) превышает максимум 31 бит.")

    # Закодированный текст
    encoded_text = ''.join(codebook[char] for char in text)

    # Формируем битовый поток
    output = BitArray()
    # Количество символов (16 бит)
    output.append(f'uint:16={len(codebook)}')
    # Символы и длины кодов
    for char in sorted_chars:
        output.append(f'uint:16={ord(char)}')  # Символ (Unicode, 16 бит)
        output.append(f'uint:5={code_lengths[char]}')  # Длина кода (5 бит, до 31 бит)
    # Длина закодированного текста (32 бита)
    output.append(f'uint:32={len(encoded_text)}')
    # Сам закодированный текст
    output.append(f'bin={encoded_text}')

    # Запись в файл
    with open(output_file, 'wb') as file:
        output.tofile(file)


def decompress(input_file, output_file):
    # Чтение битового потока
    with open(input_file, 'rb') as file:
        bits = BitArray(file.read())

    if not bits:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write('')
        return

    pos = 0
    # Чтение количества символов
    codebook_size = bits[pos:pos+16].uint
    pos += 16

    # Чтение символов и длин кодов
    code_lengths = {}
    sorted_chars = []
    for _ in range(codebook_size):
        char = chr(bits[pos:pos+16].uint)
        pos += 16
        length = bits[pos:pos+5].uint  # Чтение 5 бит вместо 4
        pos += 5
        if length > 0:  # Игнорируем нулевые длины
            code_lengths[char] = length
            sorted_chars.append(char)

    # Восстановление канонических кодов
    codebook = {}
    current_code = 0
    sorted_chars.sort(key=lambda c: (code_lengths[c], c))
    max_length = max(code_lengths.values()) if code_lengths else 0
    for char in sorted_chars:
        length = code_lengths[char]
        code = bin(current_code)[2:].zfill(length)
        codebook[code] = char
        current_code = (current_code + 1) << (max_length - length)
        current_code >>= (max_length - length)

    # Чтение длины закодированного текста
    encoded_text_length = bits[pos:pos+32].uint
    pos += 32

    # Чтение и декодирование текста
    encoded_text = bits[pos:pos+encoded_text_length].bin
    decoded_text = []
    current_code = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in codebook:
            decoded_text.append(codebook[current_code])
            current_code = ""

    # Запись результата
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(''.join(decoded_text))