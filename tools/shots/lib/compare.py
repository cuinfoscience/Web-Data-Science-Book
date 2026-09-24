"""Is a new take the same picture as the approved image, allowing for drift?

Live pages drift (capture counts, dates), so pixels never match exactly. A
difference hash compares the layout at low resolution instead: the same
region of the same page scores near 0 out of 64, a different page scores
around 32. Scale does not matter, so a 2x take compares fairly with a 1x
image.
"""
from PIL import Image

SIMILAR = 12        # out of 64 bits
ASPECT = 0.03


def dhash(path, size=8):
    with Image.open(path) as img:
        small = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(small.getdata())
    bits = 0
    for row in range(size):
        for col in range(size):
            left, right = px[row * (size + 1) + col], px[row * (size + 1) + col + 1]
            bits = (bits << 1) | (left > right)
    return bits


def compare(take, approved):
    with Image.open(take) as a, Image.open(approved) as b:
        size_a, size_b = a.size, b.size
    distance = bin(dhash(take) ^ dhash(approved)).count("1")
    aspect = abs(size_a[0] / size_a[1] - size_b[0] / size_b[1])
    return {
        "distance": distance,
        "aspect_difference": round(aspect, 3),
        "take_size": list(size_a),
        "approved_size": list(size_b),
        "similar": distance <= SIMILAR and aspect < ASPECT,
    }
