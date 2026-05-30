import argparse
from datetime import date, timedelta
import storage
import display


def cmd_add(args):
    entry, goal = storage.add_entry(note=args.note or "")
    display.print_added(entry, goal)
    today_entries = storage.get_entries_for_date(date.today())
    if goal and len(today_entries) >= goal:
        print(f"  *** You've reached your daily goal of {goal} cups! ***\n")


def cmd_today(args):
    entries = storage.get_entries_for_date(date.today())
    goal = storage.get_goal()
    display.print_today(entries, goal)


def cmd_history(args):
    days = args.days
    end = date.today()
    start = end - timedelta(days=days - 1)
    entries_by_day = storage.get_entries_for_range(start, end)
    display.print_history(entries_by_day)


def cmd_goal(args):
    cups = args.cups
    if cups < 1:
        print("\n  Goal must be at least 1 cup.\n")
        return
    storage.set_goal(cups)
    display.print_goal_set(cups)


def cmd_delete(args):
    success = storage.delete_entry(args.id)
    if success:
        display.print_deleted(args.id)
    else:
        display.print_not_found(args.id)


def main():
    parser = argparse.ArgumentParser(
        prog="coffee_tracker",
        description="Track how many cups of coffee you drink."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # add
    add_parser = subparsers.add_parser("add", help="Log a cup of coffee")
    add_parser.add_argument("--note", type=str, help="Optional note (e.g. 'Latte')")
    add_parser.set_defaults(func=cmd_add)

    # today
    today_parser = subparsers.add_parser("today", help="Show today's log")
    today_parser.set_defaults(func=cmd_today)

    # history
    history_parser = subparsers.add_parser("history", help="Show recent history")
    history_parser.add_argument("--days", type=int, default=7, help="Number of days to show (default: 7)")
    history_parser.set_defaults(func=cmd_history)

    # goal
    goal_parser = subparsers.add_parser("goal", help="Set your daily cup goal")
    goal_parser.add_argument("cups", type=int, help="Number of cups per day")
    goal_parser.set_defaults(func=cmd_goal)

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a logged entry by its ID")
    delete_parser.add_argument("id", type=int, help="The ID of the entry to delete")
    delete_parser.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
