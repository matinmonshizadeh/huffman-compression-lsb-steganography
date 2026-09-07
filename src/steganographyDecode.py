# import argparse
import binascii
import random
import numpy as np
from PIL import Image


args = (input("Input image:"), input("lenght of message:"), input("Seed:"))

input_image = args[0]
len_message = int(args[1])
seed = args[2]


# Read input image
img = Image.open(input_image)
width, height = img.size
pixels = img.load()


# Convert seed to binary
seed = bin(int(seed))[2:].zfill(32)

# Convert seed to integer
seed = int(seed, 2)

# Initialize random number generator
random.seed(seed)

# Generate random permutation
permutation = np.arange(width * height)
random.shuffle(permutation)

# Extract message from image
message = ''
for i in range(len_message):
    # Get pixel coordinates
    x = permutation[i] % width
    y = permutation[i] // width

    # Get pixel value
    pixel = pixels[x, y][0]

    # Convert pixel value to binary
    pixel = bin(pixel)[2:].zfill(24)

    # Extract message
    message += pixel[-1]

# Convert message to integer
message = int(message, 2)

# Convert message to hex
message = hex(message)[2:]

# Convert message to bytes
message = binascii.unhexlify(message)

# Convert message to string
message = message.decode('utf-8')

# Print message
print(message)