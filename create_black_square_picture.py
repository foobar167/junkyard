# Create plain black square picture
from PIL import Image

img = Image.new('RGB', (225, 225), color='black')
img.save('temp/black_square.png')
