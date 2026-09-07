# Huffman Image Compression and LSB Steganography

Lossless image compression with Huffman coding, then a secret message hidden in the image with seeded LSB steganography.

![Demo: compressing jellyfish.bmp and recovering a hidden message](docs/demo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Raw images take a lot of space, and sometimes an image also has to carry a message that only one receiver can read. This project answers both needs with two small Python scripts: one compresses a file losslessly with Huffman coding and decompresses it back byte for byte, the other hides a text message in the least significant bits of pixels chosen by a secret seed. It was written for the Algorithm Design course at Shiraz University (Fall 2022). The assignment and the accompanying article, co-written with Pardis Basiri, are in `docs/`.

## Features

- Lossless Huffman compression of any file, with the decompressed output verified identical to the input.
- Huffman code table saved to a text file, one `byte -> code` line per symbol.
- Compression ratio (CR) printed after every run.
- LSB steganography keyed by a seed: pixel positions come from a seeded random permutation, so the message cannot be located without the seed.
- Separate decoder script for the receiver, who only needs the image, the seed, and the message length.

## How it works

**Compression (`src/Huffman.py`).** The image file is read as bytes and the frequency of each byte value is counted. A min-heap repeatedly merges the two least frequent nodes until one tree remains; walking the tree assigns shorter codes to more frequent bytes. The file is rewritten as a stream of these codes, padded to a whole number of bytes. The first byte of the compressed file records how many padding bits were added. Decompression reads that header, strips the padding, and matches prefix codes bit by bit to rebuild the original bytes.

**Steganography (`src/steganography.py`, `src/steganographyDecode.py`).** The message is converted to bits. The seed initialises Python's random generator, which shuffles the list of all pixel indices. Each message bit replaces the least significant bit of the red channel of the next pixel in that order. The result is saved as PNG so the bits survive. The receiver repeats the shuffle with the same seed and reads the bits back.

## Results

Run on `examples/jellyfish.bmp` (800 x 450, RGB, uncompressed):

| Item | Value |
|---|---|
| Original size | 1,080,054 bytes |
| Compressed size (`jellyfish_compressed.bin`) | 457,734 bytes |
| Compression ratio | 2.36 |
| Decompressed file | identical to original (`cmp` reports no difference) |
| Distinct byte values / codes | 254, code lengths 1 to 15 bits |

The dark background means a few byte values dominate, which is exactly what Huffman exploits. On an already compressed input such as a JPEG the ratio drops to about 1.0, because JPEG has removed that redundancy itself.

Hiding the 24-character message `Hello Shiraz University!` with seed `12345`:

| Item | Value |
|---|---|
| Message length | 192 bits |
| Pixels changed | 93 out of 360,000 |
| Largest change per channel | 1 |
| Output | `examples/jellyfish_stego.png`, decodes back to the exact message |

## Getting started

Prerequisites: Python 3.9 or newer and git.

```bash
git clone https://github.com/matinmonshizadeh/Image-Compression-Huffman-coding-technique.git
cd Image-Compression-Huffman-coding-technique
python -m venv .venv
.venv\Scripts\activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Compress and decompress the sample image (under a second):

```bash
python src/Huffman.py
```

This writes `jellyfish_compressed.bin`, `jellyfish_decompressed.bmp`, and `huffman_codes.txt` into `examples/` and prints the CR. To try another image, save it as BMP in `examples/` and change `INPUT_IMAGE` at the top of the script.

Hide a message. The script asks for the input image, output image, message, and seed, then prints the message length in bits, which the receiver needs:

```bash
python src/steganography.py
```

Recover the message with the image, the length, and the seed:

```bash
python src/steganographyDecode.py
```

## Project structure

```
.
├── src/
│   ├── Huffman.py               # compress, save code table, decompress, print CR
│   ├── steganography.py         # hide a message (LSB, seeded)
│   └── steganographyDecode.py   # receiver side
├── examples/
│   ├── jellyfish.bmp            # sample input (uncompressed)
│   ├── jellyfish_compressed.bin # sample compressed output
│   ├── huffman_codes.txt        # sample code table
│   └── jellyfish_stego.png      # sample image with hidden message
├── docs/                        # assignment PDF, article PDF, demo image
├── requirements.txt
└── LICENSE
```

## Limitations and future work

- Huffman works on raw file bytes, so it only pays off for uncompressed formats such as BMP. On JPEG or PNG input the ratio is about 1.0. Decoding the pixels first would make it format independent.
- The compression script has a fixed input path, and the steganography scripts accept only RGB images, a message no longer than the pixel count, and crash instead of reporting a wrong seed or length.
- The code table is not stored inside the compressed file, so decompression only works in the same run that built the tree. A standalone decompressor would need the table written as a header.

## License

MIT. See [LICENSE](LICENSE).
