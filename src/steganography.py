"""LSB image steganography with a secret seed.

hide:   reads an image (normally the decompressed image from Huffman.py),
        writes each bit of a message into the least significant bit of the
        red channel of pixels chosen by a seeded random order, and saves
        the result as PNG so the bits survive.
reveal: repeats the same seeded order and reads the bits back. Without the
        seed the pixel order is unknown, so the message cannot be recovered.
"""

import random
from PIL import Image

LENGTH_BITS = 32  # the first 32 hidden bits store the message length in bits


def pixel_order(width, height, seed):
    """Return all pixel indices shuffled deterministically by the seed."""
    order = list(range(width * height))
    random.seed(seed)
    random.shuffle(order)
    return order


def to_bits(data):
    return ''.join(f"{byte:08b}" for byte in data)


def from_bits(bits):
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def hide(image_path, output_path, message, seed):
    """Hide the message in the image and save the result as PNG."""
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()

    payload = message.encode('utf-8')
    bits = f"{len(payload) * 8:0{LENGTH_BITS}b}" + to_bits(payload)
    if len(bits) > width * height:
        raise ValueError(f"message needs {len(bits)} pixels but the image has {width * height}")

    for index, bit in zip(pixel_order(width, height, seed), bits):
        x, y = index % width, index // width
        r, g, b = pixels[x, y]
        pixels[x, y] = ((r & ~1) | int(bit), g, b)

    img.save(output_path, 'PNG')
    return len(bits)


def reveal(image_path, seed):
    """Return the hidden message, or None if the seed is wrong."""
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()
    order = pixel_order(width, height, seed)

    def read_bits(start, count):
        return ''.join(str(pixels[i % width, i // width][0] & 1) for i in order[start:start + count])

    length = int(read_bits(0, LENGTH_BITS), 2)
    if length == 0 or length % 8 != 0 or length > width * height - LENGTH_BITS:
        return None
    try:
        return from_bits(read_bits(LENGTH_BITS, length)).decode('utf-8')
    except UnicodeDecodeError:
        return None


def main():
    mode = input("Mode (hide/reveal): ").strip().lower()
    if mode == 'hide':
        image = input("Input image: ")
        output = input("Output image (PNG): ")
        message = input("Message to hide: ")
        seed = input("Seed (secret key): ")
        used = hide(image, output, message, seed)
        print(f"Message hidden in {output} using {used} pixels.")
    elif mode == 'reveal':
        image = input("Input image: ")
        seed = input("Seed (secret key): ")
        message = reveal(image, seed)
        if message is None:
            print("No message found. Wrong seed or no hidden message.")
        else:
            print(message)
    else:
        print("Unknown mode. Type hide or reveal.")


if __name__ == '__main__':
    main()
