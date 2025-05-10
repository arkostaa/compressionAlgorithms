import heapq
from collections import Counter
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
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    freq_map = Counter(text)
    huffman_tree = build_huffman_tree(freq_map)
    codebook = build_codes(huffman_tree)

    encoded_text = ''.join(codebook[char] for char in text)

    with open(output_file, 'wb') as file:
        file.write(len(codebook).to_bytes(4, 'big'))
        for char, code in codebook.items():
            char_bytes = char.encode('utf-8')
            file.write(len(char_bytes).to_bytes(1, 'big'))
            file.write(char_bytes)
            file.write(len(code).to_bytes(1, 'big'))
            file.write(int(code, 2).to_bytes((len(code) + 7) // 8, 'big'))
        file.write(len(encoded_text).to_bytes(4, 'big'))
        file.write(int(encoded_text, 2).to_bytes((len(encoded_text) + 7) // 8, 'big'))


def decompress(input_file, output_file):
    with open(input_file, 'rb') as file:
        codebook_size = int.from_bytes(file.read(4), 'big')
        codebook = {}
        for _ in range(codebook_size):
            char_length = int.from_bytes(file.read(1), 'big')
            char_bytes = file.read(char_length)
            char = char_bytes.decode('utf-8')
            code_length = int.from_bytes(file.read(1), 'big')
            code = bin(int.from_bytes(file.read((code_length + 7) // 8), 'big'))[2:].zfill(code_length)
            codebook[code] = char
        encoded_text_length = int.from_bytes(file.read(4), 'big')
        encoded_text = bin(int.from_bytes(file.read((encoded_text_length + 7) // 8), 'big'))[2:].zfill(
            encoded_text_length)

    decoded_text = []
    current_code = ""
    for bit in encoded_text:
        current_code += bit
        if current_code in codebook:
            decoded_text.append(codebook[current_code])
            current_code = ""

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(''.join(decoded_text))
