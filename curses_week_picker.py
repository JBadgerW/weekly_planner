import curses
import calendar
import datetime


def date_picker(stdscr):
    curses.curs_set(0)  # Hide cursor
    today = datetime.date.today()
    year, month = today.year, today.month

    # Initialize the selected week based on today's date
    cal = calendar.monthcalendar(year, month)
    selected_week = 0
    for i, week in enumerate(cal):
        if today.day in week:
            selected_week = i
            break

    while True:
        stdscr.clear()
        cal = calendar.monthcalendar(year, month)

        # Clamp selected_week in case the new month has fewer weeks
        selected_week = min(selected_week, len(cal) - 1)

        # Draw Header
        header = f"{calendar.month_name[month]} {year}"
        stdscr.addstr(0, max(0, (20 - len(header)) // 2), header, curses.A_BOLD)
        stdscr.addstr(1, 0, "Mo Tu We Th Fr Sa Su")

        # Draw Calendar Weeks
        for i, week in enumerate(cal):
            attr = curses.A_REVERSE if i == selected_week else curses.A_NORMAL
            week_str = "".join("   " if day == 0 else f"{day:2} " for day in week)
            stdscr.addstr(2 + i, 0, week_str.rstrip(), attr)

        stdscr.refresh()

        # Handle Navigation
        key = stdscr.getch()

        if key in [curses.KEY_UP, ord("k")]:
            selected_week = (selected_week - 1) % len(cal)
        elif key in [curses.KEY_DOWN, ord("j")]:
            selected_week = (selected_week + 1) % len(cal)
        elif key in [curses.KEY_LEFT, ord("h")]:
            month -= 1
            if month == 0:
                month, year = 12, year - 1
        elif key in [curses.KEY_RIGHT, ord("l")]:
            month += 1
            if month == 13:
                month, year = 1, year + 1
        elif key in [10, 13, curses.KEY_ENTER]:
            # Find a valid day in the highlighted week to calculate its Monday
            valid_day = next(day for day in cal[selected_week] if day != 0)
            selected_date = datetime.date(year, month, valid_day)

            # Subtract the weekday index (Monday is 0) to get the exact Monday
            monday = selected_date - datetime.timedelta(days=selected_date.weekday())
            return monday


# Example usage:
if __name__ == "__main__":
    result = curses.wrapper(date_picker)
    print(f"You selected the week starting on Monday: {result}")
