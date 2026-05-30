from datetime import datetime


def print_today(entries, goal):
    total = len(entries)
    print(f"\n--- Today's Coffee Log ---")
    if not entries:
        print("  No cups logged yet today.")
    else:
        for e in entries:
            time_str = datetime.fromisoformat(e["timestamp"]).strftime("%I:%M %p")
            note_part = f"  ({e['note']})" if e["note"] else ""
            print(f"  [{e['id']}] {time_str}{note_part}")
    print(f"\n  Total: {total} cup{'s' if total != 1 else ''}")
    if goal:
        remaining = goal - total
        if total >= goal:
            print(f"  Goal: {goal} cups — reached! ({total}/{goal})")
        else:
            print(f"  Goal: {goal} cups — {remaining} more to go ({total}/{goal})")
    print()


def print_history(entries_by_day):
    print(f"\n--- Coffee History ---")
    for day_str, entries in entries_by_day.items():
        count = len(entries)
        bar = "[c]" * count if count > 0 else "(none)"
        date_label = datetime.strptime(day_str, "%Y-%m-%d").strftime("%a %b %d")
        print(f"  {date_label}:  {bar}  ({count})")
    print()


def print_added(entry, goal):
    time_str = datetime.fromisoformat(entry["timestamp"]).strftime("%I:%M %p")
    note_part = f" - {entry['note']}" if entry["note"] else ""
    print(f"\n  Logged cup #{entry['id']} at {time_str}{note_part}")
    if goal:
        print(f"  Daily goal: {goal} cups")
    print()


def print_goal_set(cups):
    print(f"\n  Daily goal set to {cups} cup{'s' if cups != 1 else ''}.\n")


def print_deleted(entry_id):
    print(f"\n  Entry #{entry_id} deleted.\n")


def print_not_found(entry_id):
    print(f"\n  No entry found with ID {entry_id}.\n")
