from PIL import Image

img = Image.open("test_pdf_page.png")
w, h = img.size
print(f"PNG Image size: {w} x {h}")

# Top permit block crop
top_block = img.crop((0, 0, w, int(h * 0.48)))
top_block.save("top_block_crop.png")

# Bottom permit block crop
bottom_block = img.crop((0, int(h * 0.48), w, h))
bottom_block.save("bottom_block_crop.png")

print("Saved top_block_crop.png and bottom_block_crop.png")
