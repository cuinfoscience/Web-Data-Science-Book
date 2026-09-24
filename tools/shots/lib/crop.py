"""Turn a recipe's `crop:` into a clip rectangle, in CSS pixels.

    crop: {window: true}                     the whole window (the default)
    crop: {full_page: true}                  the whole scrolling page
    crop: {top: 0, height: 610}              a band; left/width default to the window
    crop: {selector: "#wm-ipp-base", pad: 8} an element's box, padded
    crop: {selector: "...", height: 240}     an element's box, height overridden
"""


class CropError(Exception):
    pass


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
        pad = crop.get("pad", 0)
        x, y = max(0, box["x"] - pad), max(0, box["y"] - pad)
        rect = {"x": x, "y": y, "width": crop.get("width", box["width"] + 2 * pad),
                "height": crop.get("height", box["height"] + 2 * pad)}
    else:
        x, y = crop.get("left", 0), crop.get("top", 0)
        rect = {"x": x, "y": y, "width": crop.get("width", width - x),
                "height": crop.get("height", height - y)}
    if rect["width"] <= 0 or rect["height"] <= 0:
        raise CropError(f"crop is empty: {rect}")
    return rect, False
