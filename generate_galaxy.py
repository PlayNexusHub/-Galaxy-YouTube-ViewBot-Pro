from PIL import Image, ImageDraw
import random

# Create a new image with black background
width, height = 1000, 700
img = Image.new('RGB', (width, height), 'black')
draw = ImageDraw.Draw(img)

# Generate stars
for _ in range(1000):
    x = random.randint(0, width)
    y = random.randint(0, height)
    size = random.randint(1, 3)
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(150, 255))
    draw.ellipse([x-size, y-size, x+size, y+size], fill=color)

# Generate nebula-like structures
for _ in range(50):
    x = random.randint(0, width)
    y = random.randint(0, height)
    size = random.randint(50, 100)
    color = (random.randint(50, 150), random.randint(0, 100), random.randint(100, 200))
    draw.ellipse([x-size, y-size, x+size, y+size], fill=color)

# Save as GIF
img.save('galaxy.gif', 'GIF', save_all=True, duration=1000, loop=0)
