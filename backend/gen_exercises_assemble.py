#!/usr/bin/env python3
"""Assemble all exercise parts into a single JSON file."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from gen_exercises_part1 import get_skill1_exercises
from gen_exercises_part2 import get_skill2_exercises
from gen_exercises_part3 import get_skill3_exercises
from gen_exercises_part4 import get_skill4_exercises
from gen_exercises_part5 import get_skill5_exercises
from gen_exercises_part6 import get_skill6_exercises

def main():
    all_micro_skills = []
    all_micro_skills.extend(get_skill1_exercises())
    all_micro_skills.extend(get_skill2_exercises())
    all_micro_skills.extend(get_skill3_exercises())
    all_micro_skills.extend(get_skill4_exercises())
    all_micro_skills.extend(get_skill5_exercises())
    all_micro_skills.extend(get_skill6_exercises())

    full_data = {
        "schema_version": "1.0",
        "metadata": {
            "description": "Exercices Numération CM2 — Tous les skills",
            "author": "Sitou",
            "created_date": "2026-02-28",
            "grade": "CM2",
            "subject": "Mathématiques",
            "domain": "Numération"
        },
        "exercises": all_micro_skills
    }

    # Validate
    total_exercises = sum(len(ms["exercises"]) for ms in all_micro_skills)
    print(f"Total micro-skills: {len(all_micro_skills)}")
    print(f"Total exercises: {total_exercises}")

    # Validate exercise IDs are sequential
    all_ids = []
    for ms in all_micro_skills:
        for ex in ms["exercises"]:
            all_ids.append(ex["exercise_id"])

    expected_ids = [f"EX{str(i).zfill(3)}" for i in range(1, 121)]
    if all_ids == expected_ids:
        print("Exercise IDs: OK (EX001-EX120 sequential)")
    else:
        print("Exercise IDs: MISMATCH!")
        for i, (got, exp) in enumerate(zip(all_ids, expected_ids)):
            if got != exp:
                print(f"  Position {i}: got {got}, expected {exp}")
        if len(all_ids) != len(expected_ids):
            print(f"  Count mismatch: got {len(all_ids)}, expected {len(expected_ids)}")

    # Validate micro-skill IDs
    ms_ids = [ms["micro_skill_external_id"] for ms in all_micro_skills]
    print(f"Micro-skill IDs: {ms_ids}")

    # Validate exercise types variety per micro-skill
    for ms in all_micro_skills:
        types = [ex["type"] for ex in ms["exercises"]]
        unique = set(types)
        if len(unique) < 2:
            print(f"  WARNING: {ms['micro_skill_external_id']} uses only 1 exercise type: {types}")

    # Validate difficulty progression
    for ms in all_micro_skills:
        diffs = [ex["difficulty"] for ex in ms["exercises"]]
        print(f"  {ms['micro_skill_external_id']}: {diffs}")

    # Check required fields
    required_common = ["exercise_id", "type", "difficulty", "text", "correct_answer",
                       "explanation", "hint", "points", "time_limit_seconds",
                       "bloom_level", "ilma_level", "tags", "common_mistake_targeted"]
    for ms in all_micro_skills:
        for ex in ms["exercises"]:
            for field in required_common:
                if field not in ex:
                    print(f"  MISSING {field} in {ex['exercise_id']} ({ms['micro_skill_external_id']})")

    # Write file
    output_path = os.path.join(os.path.dirname(__file__), "exercices_cm2_numeration.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path)
    print(f"\nFile written: {output_path}")
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

if __name__ == "__main__":
    main()
