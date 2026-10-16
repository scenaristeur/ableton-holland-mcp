"""List the .adg drum kits whose name matches a vibe keyword, with their URI."""
import prep_mona_ia as p

items = p.must("get_browser_items", {"path": "drums", "item_type": "all"}).get("items", [])
kits = [i for i in items if str(i.get("name", "")).lower().endswith(".adg")]
print(f"total kits .adg = {len(kits)}")

KEYWORDS = ("lofi", "lo-fi", "lo fi", "warm", "dry session", "hybrid", "gen purpose", "selector")
for k in kits:
    nm = k["name"]
    if any(m in nm.lower() for m in KEYWORDS):
        print(f"  {nm:54s} {k.get('uri', '')}")
