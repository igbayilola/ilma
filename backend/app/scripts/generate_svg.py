"""Generate SVG illustrations for exercises with auto_generate media_references.

Reads all exercise files, finds media_references with auto_generate=true,
generates an SVG based on shape type and dimensions extracted from the text,
writes the SVG file to the media directory, and updates the URL in the JSON.

Usage:
    python -m app.scripts.generate_svg
"""
import json
import pathlib
import re
import xml.etree.ElementTree as ET

_CONTENT_DIR = pathlib.Path(__file__).resolve().parents[2] / "content"
_EXERCICES_DIR = _CONTENT_DIR / "benin" / "cm2" / "exercices"
_MEDIA_DIR = pathlib.Path(__file__).resolve().parents[2] / "static" / "media" / "svg" / "geometry"

# ── SVG generation helpers ──────────────────────────────────────

COLORS = {
    "stroke": "#1F2937",
    "fill": "#FEF3C7",
    "fill_light": "#FFFBEB",
    "accent": "#D97706",
    "text": "#374151",
    "dim": "#6B7280",
    "grid": "#E5E7EB",
    "right_angle": "#3B82F6",
}


def _svg_root(width=300, height=200):
    svg = ET.Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "viewBox": f"0 0 {width} {height}",
        "width": str(width),
        "height": str(height),
        "role": "img",
    })
    # Light background
    ET.SubElement(svg, "rect", {
        "width": str(width), "height": str(height),
        "fill": "white", "rx": "8",
    })
    return svg


def _label(svg, x, y, text, size=12, color=None, bold=False):
    el = ET.SubElement(svg, "text", {
        "x": str(x), "y": str(y),
        "font-family": "Inter, sans-serif",
        "font-size": str(size),
        "fill": color or COLORS["text"],
        "text-anchor": "middle",
        "dominant-baseline": "middle",
    })
    if bold:
        el.set("font-weight", "bold")
    el.text = text


def _dim_label(svg, x, y, text):
    """Dimension label with accent color."""
    _label(svg, x, y, text, size=11, color=COLORS["accent"], bold=True)


def _right_angle_mark(svg, cx, cy, size=10, rotation=0):
    """Small square at a vertex to indicate 90°."""
    ET.SubElement(svg, "rect", {
        "x": str(cx), "y": str(cy - size),
        "width": str(size), "height": str(size),
        "fill": "none", "stroke": COLORS["right_angle"],
        "stroke-width": "1.5",
        "transform": f"rotate({rotation},{cx},{cy})",
    })


# ── Shape generators ────────────────────────────────────────────

def gen_triangle(params, text):
    """Generate a triangle SVG. Extracts vertices, sides, angles from text."""
    svg = _svg_root(300, 220)
    dims = _extract_dims(text)
    angles = _extract_angles(text)
    vertices = _extract_vertices(text, "triangle")
    is_right = "rectangle" in text.lower() or "angle droit" in text.lower() or 90 in angles

    # Default triangle coordinates
    if is_right:
        ax, ay = 60, 170
        bx, by = 240, 170
        cx, cy = 60, 40
    else:
        ax, ay = 50, 180
        bx, by = 250, 180
        cx, cy = 150, 30

    points = f"{ax},{ay} {bx},{by} {cx},{cy}"
    ET.SubElement(svg, "polygon", {
        "points": points,
        "fill": COLORS["fill"],
        "stroke": COLORS["stroke"],
        "stroke-width": "2",
        "stroke-linejoin": "round",
    })

    # Vertex labels
    v = vertices if len(vertices) >= 3 else ["A", "B", "C"]
    _label(svg, ax - 12, ay + 14, v[0], bold=True)
    _label(svg, bx + 12, by + 14, v[1], bold=True)
    _label(svg, cx, cy - 12, v[2], bold=True)

    # Dimension labels on sides
    if len(dims) >= 1:
        _dim_label(svg, (ax + bx) // 2, ay + 18, f"{dims[0]} cm")
    if len(dims) >= 2:
        _dim_label(svg, (ax + cx) // 2 - 20, (ay + cy) // 2, f"{dims[1]} cm")
    if len(dims) >= 3:
        _dim_label(svg, (bx + cx) // 2 + 20, (by + cy) // 2, f"{dims[2]} cm")

    # Right angle mark
    if is_right:
        _right_angle_mark(svg, ax, ay, 12)

    # Angle labels
    if angles and not is_right:
        _label(svg, ax + 25, ay - 15, f"{angles[0]}°", size=10, color=COLORS["dim"])

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_rectangle(params, text):
    svg = _svg_root(300, 200)
    dims = _extract_dims(text)
    vertices = _extract_vertices(text, "rectangle")
    v = vertices if len(vertices) >= 4 else ["A", "B", "C", "D"]

    rx, ry = 40, 40
    rw, rh = 220, 120

    ET.SubElement(svg, "rect", {
        "x": str(rx), "y": str(ry), "width": str(rw), "height": str(rh),
        "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2", "rx": "2",
    })

    _label(svg, rx - 10, ry - 8, v[0], bold=True)
    _label(svg, rx + rw + 10, ry - 8, v[1], bold=True)
    _label(svg, rx + rw + 10, ry + rh + 12, v[2], bold=True)
    _label(svg, rx - 10, ry + rh + 12, v[3], bold=True)

    if len(dims) >= 1:
        _dim_label(svg, rx + rw // 2, ry + rh + 18, f"{dims[0]} cm")
    if len(dims) >= 2:
        _dim_label(svg, rx - 22, ry + rh // 2, f"{dims[1]} cm")

    _right_angle_mark(svg, rx, ry, 10)

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_carre(params, text):
    svg = _svg_root(240, 240)
    dims = _extract_dims(text)
    vertices = _extract_vertices(text, "carré")
    v = vertices if len(vertices) >= 4 else ["A", "B", "C", "D"]
    side = dims[0] if dims else "?"

    sx, sy, ss = 40, 40, 160
    ET.SubElement(svg, "rect", {
        "x": str(sx), "y": str(sy), "width": str(ss), "height": str(ss),
        "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2",
    })
    _label(svg, sx - 10, sy - 8, v[0], bold=True)
    _label(svg, sx + ss + 10, sy - 8, v[1], bold=True)
    _label(svg, sx + ss + 10, sy + ss + 12, v[2], bold=True)
    _label(svg, sx - 10, sy + ss + 12, v[3], bold=True)
    _dim_label(svg, sx + ss // 2, sy + ss + 18, f"{side} cm")
    _right_angle_mark(svg, sx, sy, 10)

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_cercle(params, text):
    svg = _svg_root(260, 260)
    dims = _extract_dims(text)
    r_label = dims[0] if dims else "r"

    cx, cy, r = 130, 130, 90
    ET.SubElement(svg, "circle", {
        "cx": str(cx), "cy": str(cy), "r": str(r),
        "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2",
    })
    # Center dot
    ET.SubElement(svg, "circle", {"cx": str(cx), "cy": str(cy), "r": "3", "fill": COLORS["accent"]})
    _label(svg, cx, cy - 10, "O", bold=True)
    # Radius line
    ET.SubElement(svg, "line", {
        "x1": str(cx), "y1": str(cy), "x2": str(cx + r), "y2": str(cy),
        "stroke": COLORS["accent"], "stroke-width": "1.5", "stroke-dasharray": "4,3",
    })
    _dim_label(svg, cx + r // 2, cy + 14, f"r = {r_label} cm")

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_pave(params, text):
    """3D rectangular prism (pavé droit)."""
    svg = _svg_root(300, 220)
    dims = _extract_dims(text)

    # Front face
    fx, fy, fw, fh = 40, 60, 160, 120
    ET.SubElement(svg, "rect", {
        "x": str(fx), "y": str(fy), "width": str(fw), "height": str(fh),
        "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2",
    })
    # Offset for 3D
    ox, oy = 50, -35
    # Top face
    top = f"{fx},{fy} {fx+ox},{fy+oy} {fx+fw+ox},{fy+oy} {fx+fw},{fy}"
    ET.SubElement(svg, "polygon", {"points": top, "fill": COLORS["fill_light"], "stroke": COLORS["stroke"], "stroke-width": "1.5"})
    # Right face
    right = f"{fx+fw},{fy} {fx+fw+ox},{fy+oy} {fx+fw+ox},{fy+fh+oy} {fx+fw},{fy+fh}"
    ET.SubElement(svg, "polygon", {"points": right, "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "1.5"})

    if len(dims) >= 1:
        _dim_label(svg, fx + fw // 2, fy + fh + 16, f"L={dims[0]} cm")
    if len(dims) >= 2:
        _dim_label(svg, fx - 18, fy + fh // 2, f"l={dims[1]} cm")
    if len(dims) >= 3:
        _dim_label(svg, fx + fw + ox + 10, fy + oy + fh // 2, f"h={dims[2]} cm")

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_cylindre(params, text):
    svg = _svg_root(240, 260)
    dims = _extract_dims(text)

    cx, cy, rx, ry_ellipse = 120, 60, 70, 20
    height = 150

    # Bottom ellipse
    ET.SubElement(svg, "ellipse", {
        "cx": str(cx), "cy": str(cy + height), "rx": str(rx), "ry": str(ry_ellipse),
        "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2",
    })
    # Side lines
    ET.SubElement(svg, "line", {"x1": str(cx - rx), "y1": str(cy), "x2": str(cx - rx), "y2": str(cy + height), "stroke": COLORS["stroke"], "stroke-width": "2"})
    ET.SubElement(svg, "line", {"x1": str(cx + rx), "y1": str(cy), "x2": str(cx + rx), "y2": str(cy + height), "stroke": COLORS["stroke"], "stroke-width": "2"})
    # Top ellipse
    ET.SubElement(svg, "ellipse", {
        "cx": str(cx), "cy": str(cy), "rx": str(rx), "ry": str(ry_ellipse),
        "fill": COLORS["fill_light"], "stroke": COLORS["stroke"], "stroke-width": "2",
    })

    if len(dims) >= 1:
        _dim_label(svg, cx, cy - ry_ellipse - 10, f"r={dims[0]} cm")
    if len(dims) >= 2:
        _dim_label(svg, cx + rx + 18, cy + height // 2, f"h={dims[1]} cm")

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_cube(params, text):
    svg = _svg_root(260, 260)
    dims = _extract_dims(text)
    side = dims[0] if dims else "a"

    s = 130
    fx, fy = 40, 70
    ox, oy = 45, -40

    # Front
    ET.SubElement(svg, "rect", {"x": str(fx), "y": str(fy), "width": str(s), "height": str(s), "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2"})
    # Top
    top = f"{fx},{fy} {fx+ox},{fy+oy} {fx+s+ox},{fy+oy} {fx+s},{fy}"
    ET.SubElement(svg, "polygon", {"points": top, "fill": COLORS["fill_light"], "stroke": COLORS["stroke"], "stroke-width": "1.5"})
    # Right
    right = f"{fx+s},{fy} {fx+s+ox},{fy+oy} {fx+s+ox},{fy+s+oy} {fx+s},{fy+s}"
    ET.SubElement(svg, "polygon", {"points": right, "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "1.5"})

    _dim_label(svg, fx + s // 2, fy + s + 16, f"a = {side} cm")

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_segment(params, text):
    svg = _svg_root(300, 100)
    dims = _extract_dims(text)
    vertices = _extract_vertices(text, "segment")
    v = vertices if len(vertices) >= 2 else ["A", "B"]

    x1, y1, x2, y2 = 40, 50, 260, 50
    ET.SubElement(svg, "line", {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), "stroke": COLORS["stroke"], "stroke-width": "2.5"})
    for x in (x1, x2):
        ET.SubElement(svg, "circle", {"cx": str(x), "cy": str(y1), "r": "4", "fill": COLORS["accent"]})
    _label(svg, x1, y1 + 18, v[0], bold=True)
    _label(svg, x2, y2 + 18, v[1], bold=True)
    if dims:
        _dim_label(svg, (x1 + x2) // 2, y1 - 14, f"{dims[0]} cm")

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_parallelogramme(params, text):
    svg = _svg_root(300, 200)
    dims = _extract_dims(text)
    offset = 40
    pts = f"60,160 {60+offset},40 {240+offset},40 240,160"
    ET.SubElement(svg, "polygon", {"points": pts, "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2"})
    _label(svg, 48, 172, "A", bold=True)
    _label(svg, 88, 28, "B", bold=True)
    _label(svg, 292, 28, "C", bold=True)
    _label(svg, 252, 172, "D", bold=True)
    if dims:
        _dim_label(svg, 150, 175, f"{dims[0]} cm")
    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_losange(params, text):
    svg = _svg_root(260, 260)
    dims = _extract_dims(text)
    pts = "130,20 240,130 130,240 20,130"
    ET.SubElement(svg, "polygon", {"points": pts, "fill": COLORS["fill"], "stroke": COLORS["stroke"], "stroke-width": "2"})
    _label(svg, 130, 8, "A", bold=True)
    _label(svg, 252, 130, "B", bold=True)
    _label(svg, 130, 255, "C", bold=True)
    _label(svg, 8, 130, "D", bold=True)
    if dims:
        _dim_label(svg, 130, 135, f"d={dims[0]} cm")
    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


def gen_droite(params, text):
    return gen_segment(params, text)


# ── Text parsing helpers ────────────────────────────────────────

def _extract_dims(text):
    """Extract numeric dimensions (cm) from text."""
    matches = re.findall(r'(\d+(?:[.,]\d+)?)\s*(?:cm|m(?!a)|mm)', text)
    return [m.replace(",", ".") for m in matches]


def _extract_angles(text):
    matches = re.findall(r'(\d+)\s*°', text)
    return [int(m) for m in matches]


def _extract_vertices(text, shape):
    """Extract vertex names like ABC from 'triangle ABC' or 'rectangle ABCD'."""
    pattern = rf'{shape}\s+([A-Z]{{2,6}})'
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return list(m.group(1))
    return []


# ── Generator dispatch ──────────────────────────────────────────

GENERATORS = {
    "triangle": gen_triangle,
    "rectangle": gen_rectangle,
    "carré": gen_carre,
    "cercle": gen_cercle,
    "pavé": gen_pave,
    "cylindre": gen_cylindre,
    "cube": gen_cube,
    "segment": gen_segment,
    "droite": gen_droite,
    "parallélogramme": gen_parallelogramme,
    "losange": gen_losange,
}


def main():
    _MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    skipped = 0
    errors = 0

    for f in sorted(_EXERCICES_DIR.rglob("*.json")):
        d = json.load(open(f))
        modified = False

        for block in d.get("exercises", []):
            for ex in block.get("exercises", []):
                for mr in (ex.get("media_references") or []):
                    if not mr.get("auto_generate"):
                        continue

                    params = mr.get("params", {})
                    shapes = params.get("shapes", [])
                    text = ex.get("text", "")

                    if not shapes:
                        skipped += 1
                        continue

                    shape_name = shapes[0]["shape"]
                    gen_fn = GENERATORS.get(shape_name)
                    if not gen_fn:
                        skipped += 1
                        continue

                    try:
                        svg_content = gen_fn(params, text)
                    except Exception:
                        errors += 1
                        continue

                    # Write SVG file
                    fig_id = mr.get("id", f"fig_{generated}")
                    filename = f"{fig_id}.svg"
                    svg_path = _MEDIA_DIR / filename
                    svg_path.write_text(svg_content, encoding="utf-8")

                    # Update media_reference URL
                    mr["url"] = f"/static/media/svg/geometry/{filename}"
                    mr["auto_generate"] = False  # Mark as generated
                    generated += 1
                    modified = True

        if modified:
            with open(f, "w", encoding="utf-8") as out:
                json.dump(d, out, ensure_ascii=False, indent=2)
                out.write("\n")

    print(f"Generated: {generated} SVGs")
    print(f"Skipped: {skipped} (no shape or unknown generator)")
    print(f"Errors: {errors}")
    print(f"Output dir: {_MEDIA_DIR}")


if __name__ == "__main__":
    main()
