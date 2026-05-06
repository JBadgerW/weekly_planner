import datetime
from datetime import date
from pathlib import Path
import subprocess
import curses

from curses_week_picker import date_picker

# import subprocess
# import os  # Added for path operations (if needed)
LANDSCAPE_WIDTH = 11

# Courses and their meeting days
COURSES = {
    "Humanities IV": "MTWRF",
    "Geometry": "MWF",
    "Advanced Math": "TF",
    "Physical Science": "TRF",
}

DAYS = {
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "R": "Thursday",
    "F": "Friday",
    "S": "Saturday",
    "U": "Sunday",
}

DATE_NUMS = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

LATEX_TEMPLATE = r"""\documentclass[letterpaper, landscape]{article}
\usepackage[margin=0in]{geometry}
\usepackage{tikz}
\usetikzlibrary{calc}

% Horizontal line positions
\newcommand{\classline}{7.75}
\newcommand{\weekdayline}{7.25}
\newcommand{\headlinesheight}{0.5}
\newcommand{\hwline}{2.75}
\newcommand{\notesline}{1.5}

\newcommand{\class}{!!COURSE!!}

\begin{document}
\thispagestyle{empty}

\begin{tikzpicture}[remember picture,overlay]
\path[use as bounding box] (0,0) rectangle (0,0);
% draw relative to bottom-left of page
\coordinate (origin) at (current page.south west);

% vertical lines (spacers between days)
!!VERTICAL_LINES!!

% horizontal lines
\draw ($(origin) + (0 in, \classline in)$) -- ($(origin) + (11 in, \classline in)$);
\draw ($(origin) + (0 in, \weekdayline in)$) -- ($(origin) + (11 in, \weekdayline in)$);
\draw ($(origin) + (0 in, \hwline in)$) -- ($(origin) + (11 in, \hwline in)$);
\draw ($(origin) + (0 in, \notesline in)$) -- ($(origin) + (11 in, \notesline in)$);

% days of the week labels
!!DAYS_OF_WEEK_LABELS!!

% Class headline and week
\node[anchor=south west] at ($(origin)+(0.25in,\classline in)$) {
  \makebox[0.957\textwidth][s]{\Huge \textsc{Weekly Plan \hfill !!DATE_RANGE!! \hfill \class}}
};

% HW labels
!!HW_LABELS!!

% Notes labels
!!NOTES_LABELS!!

\end{tikzpicture}

\end{document}
"""


class WeekPlanner:
    def __init__(
        self,
        course: str,
        schedule: list | str,  # Either a list of days or a string with, e.g. "MWF"
        date_in_week: date | None,
    ):
        self.course = course.strip()
        self.schedule = schedule
        self.date_in_week = (
            datetime.datetime.today().date() if not date_in_week else date_in_week
        )

        if len(self.schedule) < 1 or len(self.schedule) > 10:
            raise ValueError(
                "Invalid schedule. Schedule can only handle between 1 and 10 "
                "class meetings per week."
            )

        if isinstance(self.schedule, str):
            temp_schedule = []

            for letter in self.schedule.upper():
                if letter not in DAYS.keys():
                    valid_letters = ", ".join(DAYS.keys())
                    raise ValueError(
                        "Invalid schedule: letters representing days must be "
                        f"from the following list: {valid_letters}."
                    )
                temp_schedule.append(DAYS[letter])

            self.schedule = temp_schedule
        elif isinstance(self.schedule, list):
            self.schedule = [day.title() for day in self.schedule]
            for meeting_day in self.schedule:
                if meeting_day not in DAYS.values():
                    raise ValueError(
                        "Invalid schedule. Any days must be days of the week."
                    )
        else:
            raise ValueError(
                "Invalid schedule. Must be a string of day letters (e.g. 'MWF') "
                "or a list of days: (e.g. ['Monday', 'Wednesday', 'Friday'])"
            )

        self.monday = self.date_in_week - datetime.timedelta(
            days=date_in_week.weekday()  # type: ignore
        )
        self.schedule_dates = [
            self.monday + datetime.timedelta(days=DATE_NUMS[day])
            for day in self.schedule
        ]

        self.num_columns = len(self.schedule_dates)
        self.column_width = round(LANDSCAPE_WIDTH / self.num_columns, 3)

    @property
    def vertical_lines_latex(self) -> str:
        latex = []

        for divider in range(self.num_columns - 1):
            x_pos = round((divider + 1) * self.column_width, 3)
            latex.append(
                f"\\draw ($(origin) + ({x_pos} in, 0 in)$) -- ($(origin) + ({x_pos} in, \\classline in)$);"
            )

        return "\n".join(latex)

    @property
    def weekday_labels_latex(self) -> str:
        latex = []

        for i, day_date in enumerate(self.schedule_dates):
            label_shift = 0.25 if i == 0 else 0
            x_pos = round(i * self.column_width + label_shift, 3)
            latex.append(
                f"\\node[anchor=south west] at ($(origin)+({x_pos} in, \\weekdayline in)$) {{\n"
                f"  \\huge {day_date.strftime('%A')} \\large {day_date.strftime('%-m/%-d')}}};"
            )

        return "\n".join(latex)

    @property
    def hw_labels_latex(self):
        latex = []

        for i in range(self.num_columns):
            label_shift = 0.25 if i == 0 else 0
            latex.append(
                "\\node[anchor=north west] at ($(origin)+("
                f"{round(i * self.column_width + label_shift, 3)} in, "
                "\\hwline in)$) {\\Large HW};"
            )

        return "\n".join(latex)

    @property
    def notes_labels_latex(self):
        latex = []

        for i in range(self.num_columns):
            label_shift = 0.25 if i == 0 else 0
            latex.append(
                "\\node[anchor=north west] at ($(origin)+("
                f"{round(i * self.column_width + label_shift, 3)} "
                "in, \\notesline in)$) {\\Large Notes};"
            )

        return "\n".join(latex)

    @property
    def latex(self):
        self.friday = self.monday + datetime.timedelta(days=4)
        self.header_range = (
            f"{self.monday.strftime('%-m/%-d')} -- {self.friday.strftime('%-m/%-d')}"
        )

        tex_file_code = LATEX_TEMPLATE.replace("!!COURSE!!", self.course)
        tex_file_code = tex_file_code.replace("!!DATE_RANGE!!", self.header_range)
        tex_file_code = tex_file_code.replace("!!HW_LABELS!!", self.hw_labels_latex)
        tex_file_code = tex_file_code.replace(
            "!!NOTES_LABELS!!", self.notes_labels_latex
        )
        tex_file_code = tex_file_code.replace(
            "!!DAYS_OF_WEEK_LABELS!!", self.weekday_labels_latex
        )
        tex_file_code = tex_file_code.replace(
            "!!VERTICAL_LINES!!", self.vertical_lines_latex
        )

        return tex_file_code


class WeekPlanIO:
    def __init__(
        self,
        week_planner: WeekPlanner,
    ):
        self.week_planner = week_planner
        self.compilation_subfolder = Path("./tex_output/")
        self.compilation_subfolder.mkdir(exist_ok=True)
        self.latex_file = Path(
            "planner_"
            + week_planner.course.lower().replace(" ", "_")
            + "_"
            + week_planner.monday.isoformat()
            + ".tex"
        )
        self.latex_file_path = self.compilation_subfolder / self.latex_file

    def save_latex(self):
        # Write the .tex file
        with open(self.latex_file_path, "w", encoding="utf-8") as tex_file:
            tex_file.write(self.week_planner.latex + "\n")

    def compile_latex(self):
        if not Path.exists(self.latex_file_path):
            self.save_latex()

        print(f"Compiling {self.latex_file}...")

        # 1. COMPILE with latexmk
        try:
            subprocess.run(
                [
                    "latexmk",
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-outdir=./tex_output",
                    self.latex_file_path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print("  -> Success!")

            # 2. CLEANUP auxiliary files
            # We use latexmk -c to clean up the files it just created
            subprocess.run(
                ["latexmk", "-c", "-outdir=./tex_output", self.latex_file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("  -> Cleaned auxiliary files.")

        except subprocess.CalledProcessError:
            print(f"  -> Error compiling {self.latex_file_path}")


# def date_picker(stdscr):
#    curses.curs_set(0)  # Hide cursor
#    today = datetime.date.today()
#    year, month = today.year, today.month
#
#    # Initialize the selected week based on today's date
#    cal = calendar.monthcalendar(year, month)
#    selected_week = 0
#    for i, week in enumerate(cal):
#        if today.day in week:
#            selected_week = i
#            break
#
#    while True:
#        stdscr.clear()
#        cal = calendar.monthcalendar(year, month)
#
#        # Clamp selected_week in case the new month has fewer weeks
#        selected_week = min(selected_week, len(cal) - 1)
#
#        # Draw Header
#        header = f"{calendar.month_name[month]} {year}"
#        stdscr.addstr(0, max(0, (20 - len(header)) // 2), header, curses.A_BOLD)
#        stdscr.addstr(1, 0, "Mo Tu We Th Fr Sa Su")
#
#        # Draw Calendar Weeks
#        for i, week in enumerate(cal):
#            attr = curses.A_REVERSE if i == selected_week else curses.A_NORMAL
#            week_str = "".join("   " if day == 0 else f"{day:2} " for day in week)
#            stdscr.addstr(2 + i, 0, week_str.rstrip(), attr)
#
#        stdscr.refresh()
#
#        # Handle Navigation
#        key = stdscr.getch()
#
#        if key in [curses.KEY_UP, ord("k")]:
#            selected_week = (selected_week - 1) % len(cal)
#        elif key in [curses.KEY_DOWN, ord("j")]:
#            selected_week = (selected_week + 1) % len(cal)
#        elif key in [curses.KEY_LEFT, ord("h")]:
#            month -= 1
#            if month == 0:
#                month, year = 12, year - 1
#        elif key in [curses.KEY_RIGHT, ord("l")]:
#            month += 1
#            if month == 13:
#                month, year = 1, year + 1
#        elif key in [10, 13, curses.KEY_ENTER]:
#            # Find a valid day in the highlighted week to calculate its Monday
#            valid_day = next(day for day in cal[selected_week] if day != 0)
#            selected_date = datetime.date(year, month, valid_day)
#
#            # Subtract the weekday index (Monday is 0) to get the exact Monday
#            monday = selected_date - datetime.timedelta(days=selected_date.weekday())
#            return monday
#

if __name__ == "__main__":
    #    planner = WeekPlanner(
    #    "Test Class", "trf", datetime.datetime.today() + datetime.timedelta(days=7)
    # )

    # thing_io = WeekPlanIO(planner)
    # thing_io.save_latex()
    # thing_io.compile_latex()

    #     week_chooser = (
    #         input("Do you want planners for 'this' week (default) or 'next' week? ")
    #         or "this week"
    #     )
    #     day_in_week = (
    #         datetime.datetime.today() + datetime.timedelta(days=7)
    #         if week_chooser[0].lower() == "n"
    #         else datetime.datetime.today()
    #     )

    day_in_week = curses.wrapper(date_picker)

    for course in COURSES.keys():
        planner = WeekPlanner(course, COURSES[course], day_in_week)
        WeekPlanIO(planner).compile_latex()
