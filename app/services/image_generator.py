import hashlib
import io

from PIL import Image, ImageDraw, ImageFont


def generate_png(prompt: str, width: int, height: int) -> bytes:
    """Create a deterministic abstract PNG based on a prompt.

    This adapter can later be replaced with an Azure OpenAI/DALL-E or other model
    provider without changing the HTTP route.
    """
    digest = hashlib.sha256(prompt.encode("utf-8")).digest()
    start, end, accent = (tuple(digest[i : i + 3]) for i in (0, 3, 6))
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(round(start[c] * (1 - ratio) + end[c] * ratio) for c in range(3))
        draw.line((0, y, width, y), fill=color)

    for index in range(8):
        x = ((digest[9 + index] / 255) * width)
        y = ((digest[17 + index] / 255) * height)
        radius = max(20, digest[(25 + index) % len(digest)] / 255 * min(width, height) / 4)
        alpha_color = tuple(min(255, channel + 45) for channel in accent)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=alpha_color, width=4)

    label = prompt[:60]
    font = ImageFont.load_default()
    text_box = draw.textbbox((0, 0), label, font=font)
    text_width = text_box[2] - text_box[0]
    draw.rounded_rectangle((16, height - 42, min(width - 16, text_width + 32), height - 16), radius=8, fill=(0, 0, 0))
    draw.text((24, height - 34), label, fill=(255, 255, 255), font=font)

    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
