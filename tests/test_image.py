import io
from pathlib import Path

import pytest
from image import resize_to_64x64_png, img_size
import tempfile
import os

inputs = [
    "tests/resources/icon.ico",
    "tests/resources/icon.png",
    "tests/resources/icon.icns",
    "tests/resources/icon.tiff",
    Path("tests") / "resources" / "icon.ico",
    Path("tests") / "resources" / "icon.icns",
    Path("tests") / "resources" / "icon.png",
    Path("tests") / "resources" / "icon.tiff",
]

@pytest.mark.parametrize("input", inputs)
def test_image_resize_from_path(input):
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "output.png")

        resize_to_64x64_png(input, out_path)
        w, h = img_size(out_path)

        assert w == 64
        assert h == 64

@pytest.mark.parametrize("input", inputs)
def test_image_resize_from_BytesIO(input):
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "output.png")
        with open(input, "rb") as f:
            data = f.read()
        resize_to_64x64_png(io.BytesIO(data), out_path)
        w, h = img_size(out_path)

        assert w == 64
        assert h == 64