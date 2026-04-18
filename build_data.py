"""Build a single data.json from the operative-cards library indexes and text files."""

import json
import os
from pathlib import Path

LIBRARY_BASE = Path(__file__).parent.parent / "operative-cards"

SOURCES = {
    "faction_rules": LIBRARY_BASE / "library_faction_rules",
    "strategy_ploys": LIBRARY_BASE / "library_strategy_ploys",
    "firefight_ploys": LIBRARY_BASE / "library_firefight_ploys",
    "equipment": LIBRARY_BASE / "library_faction_equipment",
}


def read_text_file(base_dir: Path, rel_path: str) -> str:
    fp = base_dir / rel_path.replace("\\", os.sep)
    if fp.exists():
        return fp.read_text(encoding="utf-8", errors="replace").strip()
    return ""


def build():
    teams_set: set[str] = set()
    output: dict = {
        "teams": [],
        "faction_rules": {},
        "strategy_ploys": {},
        "firefight_ploys": {},
        "equipment": {},
    }

    for key, src_dir in SOURCES.items():
        index_path = src_dir / "library_index.json"
        if not index_path.exists():
            print(f"Warning: {index_path} not found, skipping")
            continue

        with open(index_path, encoding="utf-8") as f:
            entries = json.load(f)

        for entry in entries:
            team = entry["team"]
            teams_set.add(team)
            title = entry["title"]

            # Read text content
            if "text_file" in entry:
                text = read_text_file(src_dir, entry["text_file"])
                texts = [text] if text else []
            elif "text_files" in entry:
                texts = [
                    read_text_file(src_dir, tf)
                    for tf in entry["text_files"]
                    if read_text_file(src_dir, tf)
                ]
            else:
                texts = []

            item = {"title": title, "texts": texts}

            # Flag equipment that can only be used once per game
            if key == "equipment" and any("Once a game" in t for t in texts):
                item["onceAGame"] = True

            if team not in output[key]:
                output[key][team] = []
            output[key][team].append(item)

    output["teams"] = sorted(teams_set)

    out_path = Path(__file__).parent / "data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Built {out_path} with {len(output['teams'])} teams")


if __name__ == "__main__":
    build()
