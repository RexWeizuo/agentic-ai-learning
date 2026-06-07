"""
FSRS word memory scheduler.
Usage: python fsrs.py due    — list words due for review today
       python fsrs.py add WORD RATING  — record a review result
       python fsrs.py stats  — show memory stats
"""
import json, sys
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "memory" / "word_progress.json"

# Simplified FSRS parameters
DEFAULT_STABILITY = 1       # days
DEFAULT_DIFFICULTY = 0.5    # 0..1
STABILITY_MULTIPLIER = {"1": 0.5, "2": 1.3, "3": 2.5, "4": 4.5}
MAX_INTERVAL = 365

def load():
    return json.loads(DB.read_text(encoding="utf-8"))

def save(data):
    DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def next_review_date(stability_days):
    return (date.today() + timedelta(days=max(1, int(stability_days)))).isoformat()

def add_word(word, rating_str, difficulty=None):
    """Record a review for a word. rating: 1=Again, 2=Hard, 3=Good, 4=Easy"""
    data = load()
    rating = str(rating_str)
    today = date.today().isoformat()

    if word not in data["words"]:
        # New word
        if difficulty is None:
            difficulty = DEFAULT_DIFFICULTY
        stability = DEFAULT_STABILITY
        history = []
        state = 1  # Learning
    else:
        w = data["words"][word]
        stability = w.get("stability", DEFAULT_STABILITY)
        difficulty = w.get("difficulty", DEFAULT_DIFFICULTY)
        history = w.get("history", [])
        state = w.get("state", 1)

    # Update difficulty based on rating
    if rating in ("1", "2"):  # Again/Hard → more difficult
        difficulty = min(1.0, difficulty + 0.1)
    elif rating == "4":  # Easy → less difficult
        difficulty = max(0.0, difficulty - 0.05)

    # Update stability
    mult = STABILITY_MULTIPLIER.get(rating, 2.5)
    stability = max(0.5, stability * mult)
    stability = min(stability, MAX_INTERVAL)

    # Determine new state
    if rating == "1":  # Again
        state = 3  # Relearning
        stability = 0.5
    elif rating == "2":  # Hard
        state = 1  # Learning (stay cautious)
    else:  # Good / Easy
        state = 2  # Review

    next_date = next_review_date(stability)

    history.append({
        "date": today,
        "rating": int(rating),
        "stability": round(stability, 1),
        "difficulty": round(difficulty, 2),
        "new_state": state,
    })

    data["words"][word] = {
        "stability": round(stability, 1),
        "difficulty": round(difficulty, 2),
        "state": state,
        "reviews": len(history),
        "next_review": next_date,
        "last_review": today,
        "history": history[-20:],  # Keep last 20 reviews
    }

    # Update stats
    words = data["words"]
    data["stats"]["total_studied"] = len([w for w in words if words[w]["reviews"] > 0])
    data["stats"]["in_learning"] = len([w for w in words if words[w]["state"] == 1])
    data["stats"]["in_review"] = len([w for w in words if words[w]["state"] == 2])
    data["stats"]["mastered"] = len([w for w in words if words[w]["state"] == 2 and words[w]["stability"] >= 30])
    data["stats"]["last_session"] = today

    save(data)
    return data["words"][word]

def due_words():
    """Return words due for review today."""
    data = load()
    today = date.today().isoformat()
    due = []
    for word, w in data["words"].items():
        if w.get("next_review", "2000-01-01") <= today:
            due.append((word, w))
    # Sort: lower stability first (more urgent)
    due.sort(key=lambda x: x[1].get("stability", 0))
    return due

def not_seen_words():
    """Return words that have never been studied."""
    data = load()
    return set(data["words"].keys())

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "due":
        due = due_words()
        if due:
            print(f"{len(due)} words due for review:")
            for word, w in due[:30]:
                state_name = {0: "New", 1: "Learning", 2: "Review", 3: "Relearning"}
                s = state_name.get(w.get("state", 0), "?")
                print(f"  {word} | S={w.get('stability',0):.0f}d D={w.get('difficulty',0):.1f} | {s} | next={w.get('next_review','?')}")
        else:
            print("No words due (start adding new words!)")

    elif cmd == "add":
        if len(sys.argv) < 4:
            print("Usage: python fsrs.py add <word> <rating(1-4)>")
        else:
            word = sys.argv[2]
            rating = sys.argv[3]
            result = add_word(word, rating)
            state_name = {0: "New", 1: "Learning", 2: "Review", 3: "Relearning"}
            print(f"  {word} → {state_name[result['state']]} | S={result['stability']}d | next review: {result['next_review']}")

    elif cmd == "stats":
        data = load()
        s = data["stats"]
        print(f"Words tracked: {len(data['words'])}")
        print(f"Studied: {s['total_studied']}")
        print(f"In Learning: {s['in_learning']}")
        print(f"In Review: {s['in_review']}")
        print(f"Mastered (S≥30d): {s['mastered']}")
        print(f"Last session: {s['last_session']}")

    elif cmd == "init":
        # Initialize a word as New
        if len(sys.argv) > 2:
            word = sys.argv[2]
            data = load()
            if word not in data["words"]:
                data["words"][word] = {
                    "stability": DEFAULT_STABILITY,
                    "difficulty": DEFAULT_DIFFICULTY,
                    "state": 0,  # New
                    "reviews": 0,
                    "next_review": date.today().isoformat(),
                    "last_review": None,
                    "history": [],
                }
                save(data)
                print(f"  {word} initialized (New)")
            else:
                print(f"  {word} already exists (state={data['words'][word]['state']})")

    else:
        print("Commands: due | add | stats | init")
