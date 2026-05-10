"""One-shot migration: convert v1.4.0 math programme files to v2.0 format in-place.

Usage:
    python -m app.scripts.migrate_v14_to_v20
"""
import json
import pathlib

from app.scripts.convert_legacy_json import convert

_CONTENT_DIR = pathlib.Path(__file__).resolve().parents[2] / "content"
_MATH_PROGRAMME_DIR = _CONTENT_DIR / "benin" / "cm2" / "programme" / "mathematiques"


def main() -> None:
    if not _MATH_PROGRAMME_DIR.exists():
        print(f"Directory not found: {_MATH_PROGRAMME_DIR}")
        return

    for json_file in sorted(_MATH_PROGRAMME_DIR.glob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        version = data.get("schema_version", "")
        if version == "2.0":
            print(f"  [skip] {json_file.name} — already v2.0")
            continue

        if version not in ("1.4.0", "1.3.0", "1.0"):
            print(f"  [skip] {json_file.name} — unknown version {version!r}")
            continue

        print(f"  [convert] {json_file.name} (v{version} → v2.0)")
        v2_data = convert(data)

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(v2_data, f, ensure_ascii=False, indent=2)
            f.write("\n")

        # Verify round-trip
        with open(json_file, encoding="utf-8") as f:
            check = json.load(f)
        assert check["schema_version"] == "2.0", f"Round-trip check failed for {json_file.name}"
        skill_count = sum(
            len(d.get("skills", []))
            for s in check.get("subjects", [])
            for d in s.get("domains", [])
        )
        ms_count = sum(
            len(sk.get("micro_skills", []))
            for s in check.get("subjects", [])
            for d in s.get("domains", [])
            for sk in d.get("skills", [])
        )
        print(f"           → {skill_count} skills, {ms_count} micro-skills")

    print("\nDone.")


if __name__ == "__main__":
    main()
