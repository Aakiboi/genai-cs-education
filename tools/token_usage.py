"""Phase 5: parse Claude Code transcripts into per-request token usage (Deliverable #4).

Reads ~/.claude/projects/d--SpecialTopics-Project2/*.jsonl (exact API usage per request) and labels
each request with the activity/phase active at that time from logs/sessions.jsonl.
Output: site/data/tokens.js (window.TOKENS = {...})
"""
import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = Path(os.environ.get("CLAUDE_TRANSCRIPTS",
                                  Path.home() / ".claude" / "projects" / "d--SpecialTopics-Project2"))
FIELDS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def load_labels():
    path = ROOT / "logs" / "sessions.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return sorted(rows, key=lambda r: parse_ts(r["ts"]))


def label_for(ts, labels):
    """Latest label whose start time is <= ts (labels mark when an activity began)."""
    cur = None
    for lab in labels:
        if parse_ts(lab["ts"]) <= ts:
            cur = lab
        else:
            break
    return cur or {"phase": None, "activity": "unlabeled", "practice": None}


def parse_transcript(path):
    """Yield one record per API request (deduplicated by requestId) plus compaction events."""
    seen, out, events = set(), [], []
    session = path.stem
    for line in path.open(encoding="utf-8"):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("isCompactSummary") or o.get("subtype") == "compact_boundary":
            events.append({"ts": o.get("timestamp"), "session": session, "event": "compact"})
        if o.get("type") != "assistant" or o.get("isSidechain"):
            continue
        msg = o.get("message") or {}
        usage = msg.get("usage")
        rid = o.get("requestId") or msg.get("id")
        if not usage or rid in seen:
            # Later content blocks of the same request repeat usage; still collect tool names.
            if out and rid in seen:
                out[-1]["tools"] += [c.get("name") for c in msg.get("content", []) if c.get("type") == "tool_use"]
            continue
        seen.add(rid)
        out.append({"ts": o["timestamp"], "session": session, "model": msg.get("model"),
                    **{k: usage.get(k, 0) or 0 for k in FIELDS},
                    "web_search": (usage.get("server_tool_use") or {}).get("web_search_requests", 0) or 0,
                    "tools": [c.get("name") for c in msg.get("content", []) if c.get("type") == "tool_use"]})
    return out, events


def build():
    labels = load_labels()
    requests_, events = [], []
    for f in sorted(TRANSCRIPTS.glob("*.jsonl")):
        r, e = parse_transcript(f)
        requests_ += r
        events += e
    requests_.sort(key=lambda r: r["ts"])
    sessions = {}
    for r in requests_:
        lab = label_for(parse_ts(r["ts"]), labels)
        r.update(phase=lab.get("phase"), activity=lab.get("activity"))
        r["total"] = sum(r[k] for k in FIELDS)
        s = sessions.setdefault(r["session"], {"session": r["session"], "start": r["ts"], "requests": 0,
                                               **{k: 0 for k in FIELDS}})
        s["end"] = r["ts"]
        s["requests"] += 1
        for k in FIELDS:
            s[k] += r[k]
    for lab in labels:  # attach how each session started (fresh / after clear / after compact)
        if lab["session_id"] in sessions and "practice" not in sessions[lab["session_id"]]:
            sessions[lab["session_id"]]["practice"] = lab["practice"]
    for e in events:
        if e["ts"]:
            events_lab = label_for(parse_ts(e["ts"]), labels)
            e["activity"] = events_lab.get("activity")
    return {"generated": datetime.now().astimezone().isoformat(timespec="seconds"),
            "fields": FIELDS, "requests": requests_, "sessions": list(sessions.values()),
            "events": events, "labels": labels}


def main():
    out = build()
    (ROOT / "site" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "site" / "data" / "tokens.js").write_text("window.TOKENS = " + json.dumps(out) + ";\n",
                                                      encoding="utf-8")
    tot = sum(r["total"] for r in out["requests"])
    print(f"tokens: {len(out['requests'])} requests, {len(out['sessions'])} sessions, {tot:,} total tokens")


if __name__ == "__main__":
    main()
