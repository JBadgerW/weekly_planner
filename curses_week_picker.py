import curses
import calendar
import datetime

PADDING_LEFT = 3
PADDING_TOP = 1


def date_picker(stdscr):
    calendar.setfirstweekday(calendar.SUNDAY)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, -1)
    stdscr.bkgd(" ", curses.color_pair(1))

    if curses.COLORS >= 256:
        curses.init_pair(2, 8, -1)
        curses.init_pair(3, 8, curses.COLOR_WHITE)
        gray_unselected = curses.color_pair(2)
        gray_selected = curses.color_pair(3)
    else:
        curses.init_pair(2, curses.COLOR_WHITE, -1)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        gray_unselected = curses.color_pair(2) | curses.A_DIM
        gray_selected = curses.color_pair(3) | curses.A_DIM

    today = datetime.date.today()
    year, month = today.year, today.month
    cal_obj = calendar.Calendar(firstweekday=calendar.SUNDAY)

    cal = cal_obj.monthdatescalendar(year, month)
    selected_week = next((i for i, week in enumerate(cal) if today in week), 0)

    while True:
        # Use erase() instead of clear() to prevent flickering
        stdscr.erase()

        cal = cal_obj.monthdatescalendar(year, month)
        selected_week = min(selected_week, len(cal) - 1)

        header = f"{calendar.month_name[month]} {year}"
        stdscr.addstr(0 + PADDING_TOP, PADDING_LEFT, header.center(20), curses.A_BOLD)
        stdscr.addstr(1 + PADDING_TOP, PADDING_LEFT, "Su Mo Tu We Th Fr Sa")

        for i, week in enumerate(cal):
            is_selected_week = i == selected_week

            if is_selected_week:
                # Draws the highlight bar across the full width
                stdscr.addstr(
                    2 + i + PADDING_TOP,
                    PADDING_LEFT,
                    " " * 20,
                    curses.color_pair(1) | curses.A_REVERSE,
                )

            for j, day_date in enumerate(week):
                is_current_month = day_date.month == month

                if is_current_month:
                    attr = (
                        curses.color_pair(1) | curses.A_REVERSE
                        if is_selected_week
                        else curses.color_pair(1)
                    )
                else:
                    attr = gray_selected if is_selected_week else gray_unselected

                stdscr.addstr(
                    2 + i + PADDING_TOP, j * 3 + PADDING_LEFT, f"{day_date.day:2}", attr
                )

        stdscr.refresh()
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
            return cal[selected_week][1]


if __name__ == "__main__":
    result = curses.wrapper(date_picker)
    print(f"You selected the week starting on Monday: {result}")
