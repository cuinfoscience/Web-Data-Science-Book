"""Turn a recipe's `crop:` into a clip rectangle, in CSS pixels.

    crop: {window: true}                     the whole window (the default)
    crop: {full_page: true}                  the whole scrolling page
    crop: {top: 0, height: 610}              a band; left/width default to the window
    crop: {selector: "#wm-ipp-base", pad: 8} an element's box, padded
    crop: {selector: "...", height: 240}     an element's box, height overridden
    crop: {selector: "...", pad: [13, 0, 0, 18], width: 560, height: 595}
                                             padding as top, right, bottom, left, and a
                                             fixed size measured from the padded corner
"""


class CropError(Exception):
    pass


def pads(crop):
    """A crop's `pad` as (top, right, bottom, left): one number, or four as in CSS."""
    pad = crop.get("pad", 0)
    if isinstance(pad, (int, float)):
        return (pad,) * 4
    if isinstance(pad, list) and len(pad) == 4:
        return tuple(pad)
    raise CropError(f"`pad` is a number or [top, right, bottom, left], not {pad!r}")


def around(box, crop):
    """The crop around an element's box (x, y, width, height): padded, and sized if the recipe says."""
    top, right, bottom, left = pads(crop)
    return (box[0] - left, box[1] - top,
            crop.get("width", box[2] + left + right), crop.get("height", box[3] + top + bottom))


def clip(page, fig):
    """Return (clip or None, full_page)."""
    crop = fig.get("crop") or {"window": True}
    width, height = fig["window"]
    if crop.get("full_page"):
        return None, True
    if crop.get("window"):
        return {"x": 0, "y": 0, "width": width, "height": height}, False
    if "selector" in crop:
        box = page.locator(crop["selector"]).first.bounding_box()
        if not box:
            raise CropError(f"crop selector {crop['selector']!r} matched nothing visible")
        x, y, w, h = around((box["x"], box["y"], box["width"], box["height"]), crop)
        rect = {"x": max(0, x), "y": max(0, y), "width": w, "height": h}
    else:
        x, y = crop.get("left", 0), crop.get("top", 0)
        rect = {"x": x, "y": y, "width": crop.get("width", width - x),
                "height": crop.get("height", height - y)}
    if rect["width"] <= 0 or rect["height"] <= 0:
        raise CropError(f"crop is empty: {rect}")
    return rect, False
