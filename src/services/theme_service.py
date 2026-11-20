from pathlib import Path

from config import THEME_FILE


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend(color: str, target: tuple[int, int, int], factor: float) -> str:
    r, g, b = _hex_to_rgb(color)
    tr, tg, tb = target
    nr = int(r + (tr - r) * factor)
    ng = int(g + (tg - g) * factor)
    nb = int(b + (tb - b) * factor)
    return _rgb_to_hex((nr, ng, nb))


def build_stylesheet(accent: str) -> str:
    if not THEME_FILE.exists():
        return ""
    template = Path(THEME_FILE).read_text(encoding="utf-8")
    accent_dim = _blend(accent, (30, 30, 30), 0.45)
    accent_bg = _blend(accent, (30, 30, 30), 0.75)
    return (
        template
        .replace("{{ACCENT}}", accent)
        .replace("{{ACCENT_DIM}}", accent_dim)
        .replace("{{ACCENT_BG}}", accent_bg)
    )