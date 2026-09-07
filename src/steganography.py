# import argparse
import binascii
import random
import numpy as np
from PIL import Image


args = (input("Input image:"), input("Output image:"), input("Message to hide:"), input("Seed:"))

input_image = args[0]
output_image = args[1]
message = args[2]
seed = args[3]


# Read input image
img = Image.open(input_image)
width, height = img.size
pixels = img.load()

# Read message
message = message
message = message.encode('utf-8')
message = binascii.hexlify(message)
message = message.decode('utf-8')

# Convert message to binary
message = bin(int(message, 16))[2:].zfill(len(message) * 4)

# Convert seed to binary
seed = bin(int(seed))[2:].zfill(32)

# Convert seed to integer
seed = int(seed, 2)

# Initialize random number generator
random.seed(seed)

# Generate random permutation
permutation = np.arange(width * height)
random.shuffle(permutation)

# Hide message in image
for i in range(len(message)):
    # Get pixel coordinates
    x = permutation[i] % width
    y = permutation[i] // width

    # Get pixel value
    pixel = pixels[x, y][0]

    
    # Convert pixel value to binary
    pixel = bin(pixel)[2:].zfill(24)

    # Modify pixel value
    pixel = pixel[:-1] + message[i]

    # Convert pixel value to integer
    pixel = int(pixel, 2)

    # Set pixel value
    pixels[x, y] = (pixel, pixels[x, y][1], pixels[x, y][2])

# Save output image
new_image = Image.new(img.mode, img.size)
for i in range(width):
    for j in range(height):
        new_image.putpixel((i, j), pixels[i, j])
new_image.save(f'{output_image}', 'PNG')

len_mesaage = len(message)

print(len_mesaage)

# ----------------------------------------------------------------------------------------
# Extract message from image
message = ''
for i in range(len_mesaage):
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