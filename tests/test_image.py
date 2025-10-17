import pytest

def test_image_manipulation_works():
    import tempfile
    import os
    from PilLite import Image

    img = Image.open("tests/resources/icon.png")
    img = img.resize((64, 64))

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "output.png")
        img.save(out_path, 'png')

        img = Image.open(out_path)
        w, h = img.size

        assert w == 64
        assert h == 64
