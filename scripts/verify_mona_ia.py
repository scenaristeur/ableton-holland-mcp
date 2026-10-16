"""Read-only state dump for the Mon IA Lisa build. Prints one line per track/slot."""
import prep_mona_ia as p

info = p.must("get_session_info", {})
print(f"tempo={info['tempo']} sig={info['signature_numerator']}/{info['signature_denominator']} "
      f"tracks={info['track_count']} returns={info['return_track_count']} "
      f"playing={info['is_playing']}")

for i in range(int(info["track_count"])):
    t = p.must("get_track_info", {"track_index": i})
    devs = ", ".join(f"{d['index']}:{d['name']}" for d in t.get("devices", [])) or "-"
    kind = "AUDIO" if t.get("is_audio_track") else "MIDI"
    print(f"\n[{i}] {t['name']} ({kind}) devices: {devs}")
    for s in t.get("clip_slots", []):
        if not s["has_clip"]:
            continue
        c = s["clip"]
        try:
            notes = p.must("get_clip_notes", {"track_index": i, "clip_index": s["index"]})
            nn = notes.get("note_count", len(notes.get("notes", [])))
        except Exception as e:
            nn = f"ERR {e}"
        flag = " <<< UNNAMED" if not c["name"] else ""
        print(f"    slot {s['index']:2d}  {c['name'] or '(vide)':22s} len={c['length']:5.1f} "
              f"notes={nn} playing={c['is_playing']}{flag}")

rt = p.must("get_return_tracks", {})
for r in rt.get("return_tracks", []):
    devs = ", ".join(f"{d['index']}:{d['name']}" for d in r.get("devices", [])) or "-"
    print(f"\n[ret {r['index']}] {r['name']} vol={r['volume']:.2f} devices: {devs}")
