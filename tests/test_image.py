import pytest

def test_image_manipulation_works():
    from PilLite import Image
    img = Image.open("tests/resources/icon.png")
    img = img.resize((64, 64))
    img.save("/tmp/output.png", 'png')

    img = Image.open("/tmp/output.png")
    w, h = img.size

    assert w == 64
    assert h == 64
