"""Generate SVG illustrations for exercises: diagrams, charts, tables, scenes, etc.

Phase 1: Tag exercises with media_references based on text analysis
Phase 2: Generate SVG files for each tagged exercise

Usage:
    python -m app.scripts.generate_illustrations
"""
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET
from collections import Counter

_CONTENT_DIR = pathlib.Path(__file__).resolve().parents[2] / "content"
_EXERCICES_DIR = _CONTENT_DIR / "benin" / "cm2" / "exercices"
_MEDIA_DIR = pathlib.Path(__file__).resolve().parents[2] / "static" / "media" / "svg" / "illustrations"

C = {
    "bg": "white",
    "stroke": "#1F2937",
    "fill1": "#FEF3C7",  # amber-100
    "fill2": "#DBEAFE",  # blue-100
    "fill3": "#D1FAE5",  # green-100
    "fill4": "#FCE7F3",  # pink-100
    "fill5": "#E0E7FF",  # indigo-100
    "accent": "#D97706",
    "text": "#374151",
    "dim": "#6B7280",
    "grid": "#E5E7EB",
    "bar_colors": ["#D97706", "#3B82F6", "#10B981", "#EF4444", "#8B5CF6", "#EC4899"],
}

FILLS = [C["fill1"], C["fill2"], C["fill3"], C["fill4"], C["fill5"]]


def _svg(w=320, h=220):
    svg = ET.Element("svg", {"xmlns": "http://www.w3.org/2000/svg", "viewBox": f"0 0 {w} {h}", "width": str(w), "height": str(h), "role": "img"})
    ET.SubElement(svg, "rect", {"width": str(w), "height": str(h), "fill": C["bg"], "rx": "8"})
    return svg


def _text(svg, x, y, txt, size=11, color=None, bold=False, anchor="middle"):
    el = ET.SubElement(svg, "text", {"x": str(x), "y": str(y), "font-family": "Inter,sans-serif", "font-size": str(size), "fill": color or C["text"], "text-anchor": anchor, "dominant-baseline": "middle"})
    if bold:
        el.set("font-weight", "bold")
    el.text = str(txt)


def _to_svg(svg):
    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


# ── Bar chart ───────────────────────────────────────────────

def gen_bar_chart(labels, values, unit="", title=""):
    n = len(labels)
    w = max(300, n * 60 + 80)
    h = 220
    svg = _svg(w, h)

    if title:
        _text(svg, w // 2, 16, title, size=12, bold=True)

    mx, my, mw, mh = 55, 30, w - 75, h - 65
    max_val = max(values) if values else 1

    # Y axis
    steps = 5
    for i in range(steps + 1):
        val = round(max_val / steps * i)
        yy = my + mh - (i / steps) * mh
        ET.SubElement(svg, "line", {"x1": str(mx), "y1": str(int(yy)), "x2": str(mx + mw), "y2": str(int(yy)), "stroke": C["grid"], "stroke-width": "0.5"})
        _text(svg, mx - 8, int(yy), str(val), size=9, color=C["dim"], anchor="end")

    # Bars
    bar_w = min(35, mw // n - 8)
    gap = (mw - bar_w * n) / (n + 1)
    for i, (label, val) in enumerate(zip(labels, values)):
        bx = mx + gap + i * (bar_w + gap)
        bh = (val / max_val) * mh if max_val else 0
        by = my + mh - bh
        color = C["bar_colors"][i % len(C["bar_colors"])]
        ET.SubElement(svg, "rect", {"x": str(int(bx)), "y": str(int(by)), "width": str(bar_w), "height": str(int(bh)), "fill": color, "rx": "2"})
        _text(svg, int(bx + bar_w / 2), int(by - 8), f"{val}{unit}", size=9, color=color, bold=True)
        _text(svg, int(bx + bar_w / 2), my + mh + 12, label[:8], size=9)

    # Axes
    ET.SubElement(svg, "line", {"x1": str(mx), "y1": str(my), "x2": str(mx), "y2": str(my + mh), "stroke": C["stroke"], "stroke-width": "1.5"})
    ET.SubElement(svg, "line", {"x1": str(mx), "y1": str(my + mh), "x2": str(mx + mw), "y2": str(my + mh), "stroke": C["stroke"], "stroke-width": "1.5"})

    return _to_svg(svg)


# ── Pie / semi-circular chart ───────────────────────────────

def gen_pie_chart(labels, values, semi=False, title=""):
    w, h = 320, 260 if not semi else 200
    svg = _svg(w, h)
    if title:
        _text(svg, w // 2, 16, title, size=12, bold=True)

    cx, cy, r = 130, (h // 2 + 10), 75
    total = sum(values) if values else 1

    angle_start = -90 if not semi else 180
    angle_range = 360 if not semi else 180

    for i, (label, val) in enumerate(zip(labels, values)):
        pct = val / total
        sweep = pct * angle_range
        a1 = math.radians(angle_start)
        a2 = math.radians(angle_start + sweep)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        large = 1 if sweep > 180 else 0
        d = f"M {cx},{cy} L {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 {x2:.1f},{y2:.1f} Z"
        color = C["bar_colors"][i % len(C["bar_colors"])]
        ET.SubElement(svg, "path", {"d": d, "fill": color, "stroke": "white", "stroke-width": "2"})

        # Label
        mid_a = math.radians(angle_start + sweep / 2)
        lx, ly = cx + (r + 30) * math.cos(mid_a), cy + (r + 30) * math.sin(mid_a)
        _text(svg, int(lx), int(ly), f"{label} ({round(pct*100)}%)", size=9, color=color, bold=True)

        angle_start += sweep

    return _to_svg(svg)


# ── Data table ──────────────────────────────────────────────

def gen_data_table(headers, rows, title=""):
    cols = len(headers)
    col_w = max(70, min(120, 400 // cols))
    w = cols * col_w + 20
    row_h = 28
    h = (len(rows) + 1) * row_h + 50
    svg = _svg(w, h)

    if title:
        _text(svg, w // 2, 16, title, size=12, bold=True)

    sx, sy = 10, 32

    # Header
    for j, hdr in enumerate(headers):
        x = sx + j * col_w
        ET.SubElement(svg, "rect", {"x": str(x), "y": str(sy), "width": str(col_w), "height": str(row_h), "fill": C["fill1"], "stroke": C["grid"]})
        _text(svg, x + col_w // 2, sy + row_h // 2, hdr[:12], size=10, bold=True)

    # Rows
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            x = sx + j * col_w
            y = sy + (i + 1) * row_h
            ET.SubElement(svg, "rect", {"x": str(x), "y": str(y), "width": str(col_w), "height": str(row_h), "fill": C["bg"], "stroke": C["grid"]})
            _text(svg, x + col_w // 2, y + row_h // 2, str(cell)[:12], size=10)

    return _to_svg(svg)


# ── Number line ─────────────────────────────────────────────

def gen_number_line(start, end, marks=None, title=""):
    w, h = 400, 100
    svg = _svg(w, h)
    if title:
        _text(svg, w // 2, 16, title, size=12, bold=True)

    mx, my, mw = 40, 50, 320
    ET.SubElement(svg, "line", {"x1": str(mx), "y1": str(my), "x2": str(mx + mw), "y2": str(my), "stroke": C["stroke"], "stroke-width": "2"})
    # Arrow
    ET.SubElement(svg, "polygon", {"points": f"{mx+mw},{my} {mx+mw-8},{my-4} {mx+mw-8},{my+4}", "fill": C["stroke"]})

    span = end - start if end != start else 1
    n_ticks = min(10, span)
    step = span / n_ticks

    for i in range(n_ticks + 1):
        val = start + i * step
        x = mx + (i / n_ticks) * mw
        ET.SubElement(svg, "line", {"x1": str(int(x)), "y1": str(my - 6), "x2": str(int(x)), "y2": str(my + 6), "stroke": C["stroke"], "stroke-width": "1.5"})
        display = int(val) if val == int(val) else f"{val:.1f}"
        _text(svg, int(x), my + 18, str(display), size=9)

    if marks:
        for val in marks:
            x = mx + ((val - start) / span) * mw
            ET.SubElement(svg, "circle", {"cx": str(int(x)), "cy": str(my), "r": "5", "fill": C["accent"]})
            _text(svg, int(x), my - 16, str(val), size=10, color=C["accent"], bold=True)

    return _to_svg(svg)


# ── Clock ───────────────────────────────────────────────────

def gen_clock(hour=3, minute=0, title=""):
    w, h = 200, 220
    svg = _svg(w, h)
    if title:
        _text(svg, w // 2, 16, title, size=11, bold=True)

    cx, cy, r = 100, 120, 70
    ET.SubElement(svg, "circle", {"cx": str(cx), "cy": str(cy), "r": str(r), "fill": C["fill1"], "stroke": C["stroke"], "stroke-width": "2"})

    # Hour marks
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x1, y1 = cx + (r - 8) * math.cos(a), cy + (r - 8) * math.sin(a)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        ET.SubElement(svg, "line", {"x1": str(int(x1)), "y1": str(int(y1)), "x2": str(int(x2)), "y2": str(int(y2)), "stroke": C["stroke"], "stroke-width": "2"})
        nx, ny = cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a)
        _text(svg, int(nx), int(ny), str(i if i else 12), size=10, bold=True)

    # Hour hand
    ha = math.radians((hour % 12 + minute / 60) * 30 - 90)
    hx, hy = cx + 40 * math.cos(ha), cy + 40 * math.sin(ha)
    ET.SubElement(svg, "line", {"x1": str(cx), "y1": str(cy), "x2": str(int(hx)), "y2": str(int(hy)), "stroke": C["stroke"], "stroke-width": "3", "stroke-linecap": "round"})

    # Minute hand
    ma = math.radians(minute * 6 - 90)
    mx2, my2 = cx + 55 * math.cos(ma), cy + 55 * math.sin(ma)
    ET.SubElement(svg, "line", {"x1": str(cx), "y1": str(cy), "x2": str(int(mx2)), "y2": str(int(my2)), "stroke": C["accent"], "stroke-width": "2", "stroke-linecap": "round"})

    ET.SubElement(svg, "circle", {"cx": str(cx), "cy": str(cy), "r": "4", "fill": C["accent"]})

    return _to_svg(svg)


# ── Container (cylinder for capacity) ──────────────────────

def gen_container(capacity=None, filled=None, label="", title=""):
    w, h = 200, 240
    svg = _svg(w, h)
    if title:
        _text(svg, w // 2, 16, title, size=11, bold=True)

    cx, cy_top, rx, ry_e = 100, 50, 50, 15
    ch = 140

    # Body
    ET.SubElement(svg, "rect", {"x": str(cx - rx), "y": str(cy_top), "width": str(rx * 2), "height": str(ch), "fill": C["fill2"], "stroke": C["stroke"], "stroke-width": "1.5"})

    # Fill level
    if capacity and filled:
        fill_h = int((filled / capacity) * ch)
        fy = cy_top + ch - fill_h
        ET.SubElement(svg, "rect", {"x": str(cx - rx + 2), "y": str(fy), "width": str(rx * 2 - 4), "height": str(fill_h), "fill": "#93C5FD", "rx": "2"})
        _text(svg, cx + rx + 15, fy + fill_h // 2, f"{filled} L", size=10, color=C["accent"], bold=True)

    # Top ellipse
    ET.SubElement(svg, "ellipse", {"cx": str(cx), "cy": str(cy_top), "rx": str(rx), "ry": str(ry_e), "fill": C["fill2"], "stroke": C["stroke"], "stroke-width": "1.5"})
    # Bottom ellipse
    ET.SubElement(svg, "ellipse", {"cx": str(cx), "cy": str(cy_top + ch), "rx": str(rx), "ry": str(ry_e), "fill": C["fill2"], "stroke": C["stroke"], "stroke-width": "1.5"})

    if label:
        _text(svg, cx, cy_top + ch + 30, label, size=11, bold=True)
    if capacity:
        _text(svg, cx, cy_top + ch + ry_e + 14, f"Capacité: {capacity} L", size=10, color=C["dim"])

    return _to_svg(svg)


# ── Terrain / Field ─────────────────────────────────────────

def gen_terrain(dims=None, shape="rectangle", label="", title=""):
    w, h = 320, 200
    svg = _svg(w, h)
    if title:
        _text(svg, w // 2, 16, title, size=11, bold=True)

    rx, ry, rw, rh = 50, 40, 220, 120
    # Grass fill
    ET.SubElement(svg, "rect", {"x": str(rx), "y": str(ry), "width": str(rw), "height": str(rh), "fill": "#D1FAE5", "stroke": "#059669", "stroke-width": "2", "rx": "4", "stroke-dasharray": "6,3"})
    # Grass pattern lines
    for i in range(5):
        yy = ry + 15 + i * 25
        ET.SubElement(svg, "line", {"x1": str(rx + 5), "y1": str(yy), "x2": str(rx + rw - 5), "y2": str(yy), "stroke": "#6EE7B7", "stroke-width": "0.8"})

    if dims and len(dims) >= 1:
        _text(svg, rx + rw // 2, ry + rh + 16, f"{dims[0]} m", size=11, color=C["accent"], bold=True)
    if dims and len(dims) >= 2:
        _text(svg, rx - 18, ry + rh // 2, f"{dims[1]} m", size=11, color=C["accent"], bold=True)
    if label:
        _text(svg, rx + rw // 2, ry + rh // 2, label, size=12, color="#065F46", bold=True)

    return _to_svg(svg)


# ── Text extraction helpers ─────────────────────────────────

def extract_bar_data(text):
    """Extract label=value pairs for bar charts."""
    pairs = re.findall(r'([A-ZÀ-Ÿa-zà-ÿ]+)\s*[=:]\s*(\d+)', text)
    if len(pairs) >= 2:
        return [p[0] for p in pairs], [int(p[1]) for p in pairs]

    # Try "label (N)" pattern
    pairs2 = re.findall(r'([A-ZÀ-Ÿa-zà-ÿ]+)\s*\((\d+)\)', text)
    if len(pairs2) >= 2:
        return [p[0] for p in pairs2], [int(p[1]) for p in pairs2]

    return None, None


def extract_table_data(text):
    """Extract table from markdown-like syntax in text."""
    rows = re.findall(r'\|([^|]+(?:\|[^|]+)+)\|', text)
    if len(rows) >= 2:
        parsed = [[c.strip() for c in row.split("|") if c.strip()] for row in rows]
        headers = parsed[0]
        data = parsed[1:]
        return headers, data
    return None, None


def extract_number_line_params(text):
    numbers = [int(n) for n in re.findall(r'\b(\d+)\b', text) if 10 <= int(n) <= 1000000]
    if numbers:
        return min(numbers) - 10, max(numbers) + 10, numbers
    return 0, 100, []


def extract_time(text):
    m = re.search(r'(\d{1,2})\s*h\s*(\d{0,2})', text)
    if m:
        return int(m.group(1)), int(m.group(2)) if m.group(2) else 0
    return 3, 0


def extract_dims_m(text):
    return re.findall(r'(\d+(?:[.,]\d+)?)\s*m(?!\w)', text)


def extract_capacity(text):
    caps = re.findall(r'(\d+(?:[.,]\d+)?)\s*(?:litre|L|l)\b', text)
    return [float(c.replace(",", ".")) for c in caps]


# ── Main tagging + generation ───────────────────────────────

DETECT_RULES = [
    ("diagramme_batons", [r"diagramme en bâtons", r"diagramme à bâtons", r"histogramme", r"diagramme.*barres"]),
    ("diagramme_circulaire", [r"diagramme circulaire", r"camembert", r"diagramme semi-circulaire", r"secteur"]),
    ("tableau", [r"complète le tableau", r"tableau des effectifs", r"voici le tableau", r"tableau ci-dessous", r"tableau de proportionnalité"]),
    ("droite_graduee", [r"droite graduée", r"droite numérique", r"place sur la droite", r"axe gradué"]),
    ("horloge", [r"horloge", r"cadran", r"aiguille"]),
    ("contenant", [r"citerne", r"bidon", r"réservoir", r"bassine"]),
    ("terrain", [r"terrain rectangulaire", r"champ de forme", r"parcelle rectangulaire", r"jardin.*forme.*rectangle", r"terrain de.*forme"]),
    ("plan_carte", [r"plan à l.échelle", r"carte à l.échelle"]),
]


def main():
    _MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    stats = Counter()
    file_idx = 0

    for f in sorted(_EXERCICES_DIR.rglob("*.json")):
        d = json.load(open(f))
        modified = False

        for block in d.get("exercises", []):
            for ex in block.get("exercises", []):
                # Skip if already has illustration
                if ex.get("media_references"):
                    existing_urls = [m.get("url", "") for m in ex["media_references"]]
                    if any("/illustrations/" in u for u in existing_urls):
                        continue

                text = ex.get("text", "")
                text_lower = text.lower()
                svg_content = None
                cat = None

                for rule_cat, patterns in DETECT_RULES:
                    if any(re.search(p, text_lower) for p in patterns):
                        cat = rule_cat
                        break

                if not cat:
                    continue

                # Generate SVG based on category
                if cat == "diagramme_batons":
                    labels, values = extract_bar_data(text)
                    if labels and values:
                        svg_content = gen_bar_chart(labels, values)
                    else:
                        svg_content = gen_bar_chart(["A", "B", "C", "D"], [20, 35, 15, 45], title="Diagramme en bâtons")

                elif cat == "diagramme_circulaire":
                    labels, values = extract_bar_data(text)
                    semi = "semi" in text_lower
                    if labels and values:
                        svg_content = gen_pie_chart(labels, values, semi=semi)
                    else:
                        svg_content = gen_pie_chart(["A", "B", "C"], [40, 35, 25], semi=semi, title="Diagramme" + (" semi-circulaire" if semi else " circulaire"))

                elif cat == "tableau":
                    headers, rows = extract_table_data(text)
                    if headers and rows:
                        svg_content = gen_data_table(headers, rows)
                    else:
                        svg_content = gen_data_table(["Élément", "Effectif"], [["A", "?"], ["B", "?"], ["Total", "?"]], title="Tableau")

                elif cat == "droite_graduee":
                    start, end, marks = extract_number_line_params(text)
                    svg_content = gen_number_line(start, end, marks)

                elif cat == "horloge":
                    hour, minute = extract_time(text)
                    svg_content = gen_clock(hour, minute)

                elif cat == "contenant":
                    caps = extract_capacity(text)
                    cap = caps[0] if caps else 100
                    filled = caps[1] if len(caps) > 1 else None
                    svg_content = gen_container(capacity=cap, filled=filled)

                elif cat == "terrain":
                    dims = extract_dims_m(text)
                    svg_content = gen_terrain(dims=dims)

                elif cat == "plan_carte":
                    dims = extract_dims_m(text)
                    svg_content = gen_terrain(dims=dims, label="Plan", title="Plan à l'échelle")

                if not svg_content:
                    continue

                # Write SVG
                file_idx += 1
                fig_id = f"ill_{file_idx:04d}"
                filename = f"{fig_id}.svg"
                (_MEDIA_DIR / filename).write_text(svg_content, encoding="utf-8")

                # Add media_reference
                if not ex.get("media_references"):
                    ex["media_references"] = []
                ex["media_references"].append({
                    "id": fig_id,
                    "type": "svg",
                    "url": f"/static/media/svg/illustrations/{filename}",
                    "alt_text": f"Illustration: {cat.replace('_', ' ')}",
                    "interactive": False,
                    "dimensions": {"width": 320, "height": 220},
                })
                stats[cat] += 1
                modified = True

        if modified:
            with open(f, "w", encoding="utf-8") as out:
                json.dump(d, out, ensure_ascii=False, indent=2)
                out.write("\n")

    print("=" * 55)
    print("  ILLUSTRATIONS GÉNÉRÉES")
    print("=" * 55)
    for cat, count in stats.most_common():
        print(f"  {cat:<25} {count:>4}")
    print(f"  {'TOTAL':<25} {sum(stats.values()):>4}")
    print(f"\n  Output: {_MEDIA_DIR}")


if __name__ == "__main__":
    main()
