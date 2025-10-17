import pytest

def test_image_manipulation_works():
    from PilLite import Image
    img = Image.open("resources/icon.png")
    img = img.resize((64, 64), Image.Resampling.LANCZOS)
    img.save("/tmp/output.png")

    img = Image.open("/tmp/output.png")
    w, h = img.size

    assert w == 64
    assert h == 64
