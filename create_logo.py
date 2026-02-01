#!/usr/bin/env python3
"""Utworz proste logo Palo Alto"""
from PIL import Image, ImageDraw, ImageFont

# Utworz logo 200x60
img = Image.new('RGB', (200, 60), color='white')
draw = ImageDraw.Draw(img)

# Czerwony pasek Palo Alto
draw.rectangle([0, 0, 200, 60], fill='#FF3B30')

# Bialy tekst
try:
    font = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()

text = "PALO ALTO"
# Centruj tekst
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (200 - text_width) / 2
y = (60 - text_height) / 2

draw.text((x, y), text, fill='white', font=font)

img.save('icons/paloalto.png')
print("✅ Logo utworzone: icons/paloalto.png")
