# Coffee Tracker — Feature Specification

## Overview
A simple command-line tool that lets you log, view, and summarize how many cups of coffee you drink each day.

---

## Features

### 1. Log a Cup
- Run a command to record that you just drank a cup of coffee.
- Optionally add a note (e.g., the type of coffee or the time of day).
- Each entry is automatically timestamped.

### 2. View Today's Log
- Display all cups logged today, with timestamps and any notes.
- Show a total count for the day.

### 3. View History
- Show a summary of cups per day for the past 7 days (default) or a custom range.

### 4. Set a Daily Goal
- Allow the user to set a daily cup limit (e.g., 3 cups).
- Warn the user when they reach or exceed their goal.

### 5. Delete an Entry
- Allow the user to remove a mistakenly logged entry by its ID.

---

## File Structure

```
coffee_tracker/
├── coffee_tracker.py     # Main entry point — handles commands and user input
├── storage.py            # Reads and writes data to the JSON file
├── display.py            # Formats and prints output to the terminal
└── data/
    └── coffee_log.json   # Where all logged entries are saved
```

---

## Data Storage

Data is stored in a single JSON file at `data/coffee_log.json`.

### Format

```json
{
  "daily_goal": 3,
  "entries": [
    {
      "id": 1,
      "timestamp": "2026-05-30T08:14:00",
      "note": "Morning espresso"
    },
    {
      "id": 2,
      "timestamp": "2026-05-30T13:22:00",
      "note": ""
    }
  ]
}
```

### Fields

| Field | Type | Description |
|---|---|---|
| `daily_goal` | integer | The user's self-set daily cup limit |
| `entries` | array | List of all logged coffee entries |
| `id` | integer | Unique number for each entry (used to delete entries) |
| `timestamp` | string | Date and time the cup was logged (ISO 8601 format) |
| `note` | string | Optional note; empty string if none provided |

---

## Command Reference (Planned)

| Command | What it does |
|---|---|
| `python coffee_tracker.py add` | Log a cup right now |
| `python coffee_tracker.py add --note "Latte"` | Log a cup with a note |
| `python coffee_tracker.py today` | Show today's entries and total |
| `python coffee_tracker.py history` | Show the last 7 days |
| `python coffee_tracker.py history --days 14` | Show the last 14 days |
| `python coffee_tracker.py goal 3` | Set daily goal to 3 cups |
| `python coffee_tracker.py delete 2` | Delete entry with ID 2 |

---

## Out of Scope (for now)
- A graphical interface or web dashboard
- User accounts or cloud sync
- Calorie or caffeine tracking
