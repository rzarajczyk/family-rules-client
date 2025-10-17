from PIL import Image

def resize_to_64x64_png(input, output):
    img = Image.open(input)
    img = img.resize((64, 64), resample=Image.Resampling.LANCZOS)
    img.save(output, 'png')

def img_size(input):
    img = Image.open(input)
    return img.size