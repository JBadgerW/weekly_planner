import datetime
from datetime import date
from pathlib import Path
import subprocess
import curses

from curses_week_picker import date_picker

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


if __name__ == "__main__":
    day_in_week = curses.wrapper(date_picker)

    for course in COURSES.keys():
        planner = WeekPlanner(course, COURSES[course], day_in_week)
        WeekPlanIO(planner).compile_latex()
