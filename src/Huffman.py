"""Lossless image compression with Huffman coding.

Reads an image file as bytes, builds a Huffman tree from the byte
frequencies, writes the compressed bit stream and the code table, then
decompresses the stream back and reports the compression ratio (CR).
"""

import heapq
import os

# All input/output files live in the repo's examples/ folder.
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'examples')
INPUT_IMAGE = os.path.join(EXAMPLES_DIR, 'jellyfish.bmp')
COMPRESSED_FILE = os.path.join(EXAMPLES_DIR, 'jellyfish_compressed.bin')
DECOMPRESSED_IMAGE = os.path.join(EXAMPLES_DIR, 'jellyfish_decompressed.bmp')
CODES_FILE = os.path.join(EXAMPLES_DIR, 'huffman_codes.txt')


class Node:
    """A node of the Huffman tree. Leaves carry a byte value as symbol."""

    def __init__(self, freq, symbol=None, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def count_frequencies(data):
    """Return {byte_value: number of occurrences} for the given bytes."""
    frequencies = {}
    for byte in data:
        frequencies[byte] = frequencies.get(byte, 0) + 1
    return frequencies


def build_tree(frequencies):
    """Build the Huffman tree with a min-heap and return its root."""
    heap = []
    for symbol, freq in sorted(frequencies.items(), key=lambda item: item[1]):
        heapq.heappush(heap, Node(freq, symbol))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        heapq.heappush(heap, Node(left.freq + right.freq, left=left, right=right))

    return heap[0]


def assign_codes(node, prefix='', codes=None):
    """Walk the tree; left edges add '0', right edges add '1'."""
    if codes is None:
        codes = {}
    if node.left is None and node.right is None:
        codes[node.symbol] = prefix
    else:
        assign_codes(node.left, prefix + '0', codes)
        assign_codes(node.right, prefix + '1', codes)
    return codes


def save_codes(codes, path):
    """Write the code table as one 'byte -> code' line per symbol."""
    with open(path, 'w') as f:
        for symbol, code in codes.items():
            f.write(f"{symbol:08b} -> {code}\n")


def compress(data, codes):
    """Encode bytes with the code table.

    Returns the compressed bytes and the length of the bit stream before
    padding. The first byte of the output stores how many padding bits
    were added to reach a whole number of bytes.
    """
    bits = ''.join(codes[byte] for byte in data)
    pad_length = (8 - len(bits) % 8) % 8
    bits += '0' * pad_length

    output = bytearray([pad_length])
    for i in range(0, len(bits), 8):
        output.append(int(bits[i:i + 8], 2))
    return bytes(output), len(bits) - pad_length


def decompress(compressed, codes):
    """Decode bytes produced by compress() back to the original bytes."""
    pad_length = compressed[0]
    bits = ''.join(f"{byte:08b}" for byte in compressed[1:])
    bits = bits[:len(bits) - pad_length]

    symbol_of = {code: symbol for symbol, code in codes.items()}
    output = bytearray()
    current = ''
    for bit in bits:
        current += bit
        if current in symbol_of:
            output.append(symbol_of[current])
            current = ''
    return bytes(output)


def main():
    with open(INPUT_IMAGE, 'rb') as f:
        original = f.read()

    codes = assign_codes(build_tree(count_frequencies(original)))
    for symbol, code in codes.items():
        print(f"{symbol:08b} -> {code}")
    save_codes(codes, CODES_FILE)

    compressed, compressed_bits = compress(original, codes)
    with open(COMPRESSED_FILE, 'wb') as f:
        f.write(compressed)
    print("CR: ", len(original) * 8 / compressed_bits)

    restored = decompress(compressed, codes)
    with open(DECOMPRESSED_IMAGE, 'wb') as f:
        f.write(restored)


if __name__ == '__main__':
    main()
