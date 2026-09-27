from pathlib import Path
import tempfile

from PIL import Image

from app.services.identity_guard import prepare_working_image


def test_prepare_working_image_uses_qwen_safe_dimensions():
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "source.png"
        output = Path(tmp) / "working.png"
        Image.new("RGB", (1001, 701), "white").save(source)

        width, height = prepare_working_image(source, output)

        assert width <= 1024
        assert height <= 1024
        assert width % 16 == 0
        assert height % 16 == 0
        assert output.exists()
