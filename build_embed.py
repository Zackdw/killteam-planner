"""Build a single self-contained index.html with data.json inlined for iframe embedding."""

import json
from pathlib import Path

DIR = Path(__file__).parent

def build():
    # Read data.json
    data_path = DIR / "data.json"
    if not data_path.exists():
        print("Error: data.json not found. Run build_data.py first.")
        return

    data = data_path.read_text(encoding="utf-8")

    # Read template
    html_path = DIR / "index.html"
    html = html_path.read_text(encoding="utf-8")

    # Replace the fetch call with inline data
    old_load = """async function loadData() {
  const resp = await fetch('data.json');
  DATA = await resp.json();
  populateTeams();
  renderScoring();
}"""

    new_load = f"""async function loadData() {{
  DATA = {data};
  populateTeams();
  renderScoring();
}}"""

    if old_load not in html:
        print("Error: Could not find loadData function to replace.")
        return

    html = html.replace(old_load, new_load)

    out_path = DIR / "embed.html"
    out_path.write_text(html, encoding="utf-8")
    size_kb = out_path.stat().st_size / 1024
    print(f"Built {out_path} ({size_kb:.0f} KB) - fully self-contained")


if __name__ == "__main__":
    build()
