"""Validate all content JSON files against expected schemas.

Usage:
    python -m app.scripts.validate_content
"""
import json
import pathlib
import sys

_CONTENT_DIR = pathlib.Path(__file__).resolve().parents[2] / "content"
_PROGRAMME_DIR = _CONTENT_DIR / "benin" / "cm2" / "programme"
_EXERCICES_DIR = _CONTENT_DIR / "benin" / "cm2" / "exercices"
_EPREUVES_DIR = _CONTENT_DIR / "benin" / "cm2" / "epreuves"

VALID_QUESTION_TYPES = {
    "mcq", "true_false", "fill_blank", "numeric_input", "short_answer",
    "ordering", "matching", "error_correction", "contextual_problem",
    "guided_steps", "justification", "tracing",
    # Uppercase variants (used in admin import)
    "MCQ", "TRUE_FALSE", "FILL_BLANK", "NUMERIC_INPUT", "SHORT_ANSWER",
    "ORDERING", "MATCHING", "ERROR_CORRECTION", "CONTEXTUAL_PROBLEM",
    "GUIDED_STEPS", "JUSTIFICATION", "TRACING",
}

VALID_DIFFICULTIES = {"easy", "medium", "hard", "EASY", "MEDIUM", "HARD"}


class ValidationError:
    def __init__(self, file: str, path: str, message: str):
        self.file = file
        self.path = path
        self.message = message

    def __str__(self) -> str:
        return f"  [{self.file}] {self.path}: {self.message}"


def validate_programme_v2(data: dict, filename: str) -> list[ValidationError]:
    """Validate a v2.0 programme file."""
    errors: list[ValidationError] = []

    if data.get("schema_version") != "2.0":
        errors.append(ValidationError(filename, "schema_version", f"Expected '2.0', got {data.get('schema_version')!r}"))
        return errors

    # Grade
    grade = data.get("grade")
    if not grade or not isinstance(grade, dict):
        errors.append(ValidationError(filename, "grade", "Missing or invalid 'grade' object"))
    else:
        for field in ("name", "slug"):
            if not grade.get(field):
                errors.append(ValidationError(filename, f"grade.{field}", "Required field missing"))

    # Subjects
    subjects = data.get("subjects")
    if not subjects or not isinstance(subjects, list):
        errors.append(ValidationError(filename, "subjects", "Missing or empty 'subjects' list"))
        return errors

    seen_skill_ids: set[str] = set()
    seen_ms_ids: set[str] = set()

    for si, subj in enumerate(subjects):
        for field in ("name", "slug"):
            if not subj.get(field):
                errors.append(ValidationError(filename, f"subjects[{si}].{field}", "Required field missing"))

        for di, dom in enumerate(subj.get("domains", [])):
            for field in ("name", "slug"):
                if not dom.get(field):
                    errors.append(ValidationError(filename, f"subjects[{si}].domains[{di}].{field}", "Required field missing"))

            for ski, skill in enumerate(dom.get("skills", [])):
                path = f"subjects[{si}].domains[{di}].skills[{ski}]"
                if not skill.get("name"):
                    errors.append(ValidationError(filename, f"{path}.name", "Required field missing"))

                ext_id = skill.get("external_id")
                if ext_id:
                    if ext_id in seen_skill_ids:
                        errors.append(ValidationError(filename, f"{path}.external_id", f"Duplicate skill ID: {ext_id}"))
                    seen_skill_ids.add(ext_id)

                for msi, ms in enumerate(skill.get("micro_skills", [])):
                    ms_path = f"{path}.micro_skills[{msi}]"
                    if not ms.get("name"):
                        errors.append(ValidationError(filename, f"{ms_path}.name", "Required field missing"))
                    ms_ext_id = ms.get("external_id")
                    if not ms_ext_id:
                        errors.append(ValidationError(filename, f"{ms_path}.external_id", "Required field missing"))
                    elif ms_ext_id in seen_ms_ids:
                        errors.append(ValidationError(filename, f"{ms_path}.external_id", f"Duplicate micro-skill ID: {ms_ext_id}"))
                    else:
                        seen_ms_ids.add(ms_ext_id)

    return errors


def validate_exercise_v1(data: dict, filename: str) -> list[ValidationError]:
    """Validate a v1.0 exercise file."""
    errors: list[ValidationError] = []

    if data.get("schema_version") != "1.0":
        errors.append(ValidationError(filename, "schema_version", f"Expected '1.0', got {data.get('schema_version')!r}"))

    exercises = data.get("exercises")
    if not exercises or not isinstance(exercises, list):
        errors.append(ValidationError(filename, "exercises", "Missing or empty 'exercises' list"))
        return errors

    seen_ids: set[str] = set()
    for bi, block in enumerate(exercises):
        ms_ext_id = block.get("micro_skill_external_id")
        if not ms_ext_id:
            errors.append(ValidationError(filename, f"exercises[{bi}].micro_skill_external_id", "Required field missing"))

        for ei, ex in enumerate(block.get("exercises", [])):
            path = f"exercises[{bi}].exercises[{ei}]"

            ex_id = ex.get("exercise_id")
            if not ex_id:
                errors.append(ValidationError(filename, f"{path}.exercise_id", "Required field missing"))

            # Unique compound ID
            compound_id = f"{ms_ext_id}::{ex_id}" if ms_ext_id and ex_id else None
            if compound_id:
                if compound_id in seen_ids:
                    errors.append(ValidationError(filename, f"{path}", f"Duplicate exercise ID: {compound_id}"))
                seen_ids.add(compound_id)

            ex_type = ex.get("type")
            if not ex_type:
                errors.append(ValidationError(filename, f"{path}.type", "Required field missing"))
            elif ex_type not in VALID_QUESTION_TYPES:
                errors.append(ValidationError(filename, f"{path}.type", f"Invalid type: {ex_type!r}"))

            if "correct_answer" not in ex:
                errors.append(ValidationError(filename, f"{path}.correct_answer", "Required field missing"))

            if not ex.get("text"):
                errors.append(ValidationError(filename, f"{path}.text", "Required field missing"))

            difficulty = ex.get("difficulty")
            if difficulty and difficulty not in VALID_DIFFICULTIES:
                errors.append(ValidationError(filename, f"{path}.difficulty", f"Invalid difficulty: {difficulty!r}"))

            # MCQ must have choices
            if ex_type in ("mcq", "MCQ") and not ex.get("choices"):
                errors.append(ValidationError(filename, f"{path}.choices", "MCQ must have choices"))

    return errors


def validate_epreuve_cep(data: dict, filename: str) -> list[ValidationError]:
    """Validate a CEP exam file."""
    errors: list[ValidationError] = []

    for field in ("title", "year", "subject"):
        if not data.get(field):
            errors.append(ValidationError(filename, field, "Required field missing"))

    items = data.get("items")
    if not items or not isinstance(items, list):
        errors.append(ValidationError(filename, "items", "Missing or empty 'items' list"))
        return errors

    for ii, item in enumerate(items):
        ipath = f"items[{ii}]"
        if "item_number" not in item:
            errors.append(ValidationError(filename, f"{ipath}.item_number", "Required field missing"))
        if not item.get("domain"):
            errors.append(ValidationError(filename, f"{ipath}.domain", "Required field missing"))

        for si, sq in enumerate(item.get("sub_questions", [])):
            sqpath = f"{ipath}.sub_questions[{si}]"
            for field in ("sub_label", "text", "correct_answer"):
                if not sq.get(field) and sq.get(field) != 0:
                    errors.append(ValidationError(filename, f"{sqpath}.{field}", "Required field missing"))

    return errors


def main() -> None:
    total_errors = 0
    total_files = 0

    # Validate programme files (v2.0)
    print("═══ Programme files (v2.0) ═══")
    programme_files = []
    math_dir = _PROGRAMME_DIR / "mathematiques"
    if math_dir.exists():
        programme_files.extend(sorted(math_dir.glob("*.json")))
    if _PROGRAMME_DIR.exists():
        programme_files.extend(sorted(_PROGRAMME_DIR.glob("*.json")))

    for f in programme_files:
        total_files += 1
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        errs = validate_programme_v2(data, f.name)
        if errs:
            total_errors += len(errs)
            for e in errs:
                print(e)
        else:
            print(f"  ✓ {f.name}")

    # Validate exercise files (v1.0)
    print("\n═══ Exercise files (v1.0) ═══")
    if _EXERCICES_DIR.exists():
        for f in sorted(_EXERCICES_DIR.rglob("*.json")):
            total_files += 1
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            errs = validate_exercise_v1(data, f.name)
            if errs:
                total_errors += len(errs)
                for e in errs:
                    print(e)
            else:
                print(f"  ✓ {f.name}")

    # Validate CEP exam files
    print("\n═══ CEP exam files ═══")
    if _EPREUVES_DIR.exists():
        for f in sorted(_EPREUVES_DIR.rglob("*.json")):
            total_files += 1
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            errs = validate_epreuve_cep(data, f.name)
            if errs:
                total_errors += len(errs)
                for e in errs:
                    print(e)
            else:
                print(f"  ✓ {f.name}")

    # Summary
    print(f"\n{'═' * 40}")
    print(f"Files validated: {total_files}")
    print(f"Errors found: {total_errors}")

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
