import base64
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

LOGO = "logo.png"      
AVATAR = "avatar.png"  

icons = Path("static/icons")
icons.mkdir(parents=True, exist_ok=True)
Path("static/profile_pics").mkdir(parents=True, exist_ok=True)


with Image.open(AVATAR) as im:
    im = ImageOps.exif_transpose(im)
    im = ImageOps.fit(im, (300, 300), Image.Resampling.LANCZOS).convert("RGB")
    im.save("static/profile_pics/default.jpg", "JPEG", quality=85)


with Image.open(LOGO) as im:
    im = ImageOps.exif_transpose(im).convert("RGBA")
    square = ImageOps.fit(im, (512, 512), Image.Resampling.LANCZOS)

    for name, size in [("icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
        square.resize((size, size), Image.Resampling.LANCZOS).save(icons / name)

    square.save(icons / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # icon.svg: a real SVG file that embeds a PNG
    buf = BytesIO()
    square.resize((256, 256), Image.Resampling.LANCZOS).save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    (icons / "icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" width="256" height="256" '
        'viewBox="0 0 256 256">'
        f'<image width="256" height="256" xlink:href="data:image/png;base64,{b64}"/>'
        "</svg>"
    )

print("Done")