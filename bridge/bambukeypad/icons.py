"""Key icons: small line drawings rendered as SVG, sent base64-encoded.

Logi Plugin Service renders SVG on the keys, and about 80 px suits them. Each icon
is a few strokes on an 80×80 grid, drawn light on the key's dark background, with
Bambu green for the two keys that lead to a print.
"""

from __future__ import annotations

import base64

INK = "#EDEDED"
ACCENT = "#00AE42"

# SVG body elements per icon, drawn with the stroke set on the <g> below.
_SHAPES: dict[str, str] = {
    "import": '<path d="M40 14v34M27 35l13 13 13-13"/><path d="M16 50v14h48V50"/>',
    "slice": '<path d="M16 58h48M16 46h48M16 34h48M16 22h48" stroke="{accent}"/>',
    "print": '<rect x="18" y="14" width="44" height="36" rx="4"/><path d="M40 22v16"/>'
             '<path d="M30 50v8h20v-8"/><path d="M14 66h52" stroke="{accent}"/>',
    "arrange": '<rect x="14" y="14" width="22" height="22" rx="3"/><rect x="44" y="14" width="22" height="22" rx="3"/>'
               '<rect x="14" y="44" width="22" height="22" rx="3"/><rect x="44" y="44" width="22" height="22" rx="3"/>',
    "orient": '<path d="M40 12l22 38H18z"/><path d="M14 66h52"/>',
    "layflat": '<path d="M22 20l36 10-6 22-36-10z"/><path d="M12 66h56"/><path d="M40 54v6"/>',
    "edit": '<path d="M18 62l6-18 26-26 12 12-26 26z"/><path d="M44 24l12 12"/>',
    "move": '<path d="M40 12v56M12 40h56"/><path d="M32 20l8-8 8 8M32 60l8 8 8-8M20 32l-8 8 8 8M60 32l8 8-8 8"/>',
    "rotate": '<path d="M62 40a22 22 0 1 1-8-17"/><path d="M56 12v12H44"/>',
    "scale": '<rect x="14" y="34" width="32" height="32" rx="3"/><path d="M38 14h28v28"/><path d="M66 14L44 36"/>',
    "cut": '<path d="M12 40h56" stroke-dasharray="6 6"/><rect x="24" y="16" width="32" height="48" rx="4"/>',
    "clone": '<rect x="14" y="24" width="30" height="30" rx="3"/><rect x="36" y="16" width="30" height="30" rx="3"/>',
    "select": '<rect x="14" y="14" width="52" height="52" rx="3" stroke-dasharray="8 6"/>',
    "undo": '<path d="M24 30h26a14 14 0 0 1 0 28H30"/><path d="M32 20L22 30l10 10"/>',
    "redo": '<path d="M56 30H30a14 14 0 0 0 0 28h20"/><path d="M48 20l10 10-10 10"/>',
    "view": '<path d="M10 40s12-20 30-20 30 20 30 20-12 20-30 20-30-20-30-20z"/><circle cx="40" cy="40" r="8"/>',
    "fit": '<path d="M14 28V14h14M52 14h14v14M66 52v14H52M28 66H14V52"/><rect x="30" y="30" width="20" height="20"/>',
    "iso": '<path d="M40 12l24 14v28L40 68 16 54V26z"/><path d="M40 40l24-14M40 40L16 26M40 40v28"/>',
    "top": '<rect x="18" y="18" width="44" height="44" rx="3"/><path d="M40 4v10M34 8l6 6 6-6"/>',
    "front": '<path d="M16 30l12-12h36v34L52 64"/><rect x="16" y="30" width="36" height="34"/>',
    "left": '<rect x="34" y="18" width="30" height="44"/><path d="M34 18L18 30v32l16 0"/>',
    "right": '<rect x="16" y="18" width="30" height="44"/><path d="M46 18l16 12v32H46"/>',
    "default": '<path d="M14 40L40 16l26 24"/><path d="M22 34v30h36V34"/>',
    "overhang": '<path d="M14 66h52"/><path d="M20 66V40h20l26-16"/><path d="M44 30v8M52 26v10M60 22v12" stroke="{accent}"/>',
    "file": '<path d="M20 12h26l14 14v42H20z"/><path d="M46 12v14h14"/>',
    "save": '<path d="M16 16h40l8 8v40H16z"/><rect x="26" y="16" width="24" height="14"/><rect x="24" y="44" width="32" height="20"/>',
    "saveas": '<path d="M16 16h32l8 8v18M16 16v48h26"/><path d="M50 66l4-12 12-12 8 8-12 12z"/>',
    "export": '<path d="M40 50V14M27 27l13-13 13 13"/><path d="M16 50v14h48V50"/>',
    "gcode": '<path d="M28 22L14 40l14 18M52 22l14 18-14 18"/><path d="M44 18L36 62"/>',
    "stl": '<path d="M40 12l24 14v28L40 68 16 54V26z"/><path d="M16 26l48 28M64 26L16 54"/>',
    "open": '<path d="M12 24h20l6 6h30v34H12z"/>',
    "new": '<path d="M20 12h26l14 14v42H20z"/><path d="M40 34v20M30 44h20"/>',
    "folder": '<path d="M12 24h20l6 6h30v34H12z"/><path d="M34 46h14M42 40l6 6-6 6"/>',
    "home": '<path d="M14 40L40 16l26 24"/><path d="M22 34v30h36V34"/>',
    "back": '<path d="M48 18L26 40l22 22"/>',
    "more": '<path d="M32 18l22 22-22 22"/>',
    "offline": '<circle cx="40" cy="40" r="26"/><path d="M22 22l36 36"/>',
}

NAMES = frozenset(_SHAPES)


def svg(name: str) -> str:
    shapes = _SHAPES[name].replace("{accent}", ACCENT)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">'
        f'<g fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
        f"{shapes}</g></svg>"
    )


def image(name: str) -> str | None:
    """The icon as base64 SVG, or None for an unknown name (a text-only key)."""
    if name not in _SHAPES:
        return None
    return base64.b64encode(svg(name).encode("utf-8")).decode("ascii")
