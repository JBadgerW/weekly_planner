import datetime
from datetime import date
import subprocess
import os  # Added for path operations (if needed)

# Courses and their meeting days
COURSES = {
    "Humanities IV": "MTWRF",
    "Geometry": "MWF",
    "Advanced Math": "TF",
    "Physical Science": "TRF",
}

DAYS = {
    "U": "Sunday",
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "R": "Thursday",
    "F": "Friday",
    "S": "Saturday",
}

date_labels = [
    "!!MONDAY!!",
    "!!TUESDAY!!",
    "!!WEDNESDAY!!",
    "!!THURSDAY!!",
    "!!FRIDAY!!",
]


class WeekPlanner:
    def __init__(
        self,
        course: str,
        schedule: list | str,  # Either a list of days or a string with, e.g. "MWF"
        date_in_week: date | None,
    ):
        self.course = course
        self.schedule = schedule
        self.date_in_week = (
            datetime.datetime.today() if not date_in_week else date_in_week
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
                if meeting_day not in DAYS.items():
                    raise ValueError(
                        "Invalid schedule. Any days must be days of the week."
                    )
        else:
            raise ValueError(
                "Invalid schedule. Must be a string of day letters (e.g. 'MWF') "
                "or a list of days: (e.g. ['Monday', 'Wednesday', 'Friday'])"
            )

        print(self.schedule)
        breakpoint()


def valid_schedule(schedule: str) -> bool:
    """Assumes a string like 'MWF' or 'MTWRF' or something similar."""
    for letter in schedule.upper():
        if letter not in DAYS.keys():
            allowed_letters = ", ".join(list(DAYS.keys()))
            print(f"Schedule must have only the letters {allowed_letters}.")
            return False

    if len(schedule) != len(set(schedule)):
        multiple_per_day = (
            input(
                "You have multiple classes in one day. Is this okay? (y/n; default = yes): "
            )
            or "yes"
        )
        if multiple_per_day[0].lower() == "n":
            return False
        else:
            return True

    if len(schedule) > 10 or len(schedule) < 1:
        print("This script handles from 1 to 10 columns.")
        return False

    return True


def meeting_days(schedule: str) -> list:
    schedule_days = []

    for day in schedule.upper():
        schedule_days.append(DAYS[day])

    return schedule_days


def vertical_lines_latex(num_columns) -> str:
    latex = []

    column_width = round(11 / num_columns, 3)

    for divider in range(num_columns - 1):
        x_pos = round((divider + 1) * column_width, 3)
        latex.append(
            f"\\draw ($(origin) + ({x_pos} in, 0 in)$) -- ($(origin) + ({x_pos} in, \\classline in)$);"
        )

    return "\n".join(latex)


def dates_of_week(date_in_week: datetime.datetime) -> dict:
    sunday = date_in_week - datetime.timedelta(days=date_in_week.weekday() + 1)

    return {
        "Sunday": sunday + datetime.timedelta(days=0),
        "Monday": sunday + datetime.timedelta(days=1),
        "Tuesday": sunday + datetime.timedelta(days=2),
        "Wednesday": sunday + datetime.timedelta(days=3),
        "Thursday": sunday + datetime.timedelta(days=4),
        "Friday": sunday + datetime.timedelta(days=5),
        "Saturday": sunday + datetime.timedelta(days=6),
    }


def weekday_labels_latex(schedule_days: list, date_in_week: datetime.datetime) -> str:
    latex = []

    column_width = round(11 / len(schedule_days), 3)

    dates_this_week = dates_of_week(date_in_week)

    days_and_dates = [
        (schedule_day, dates_this_week[schedule_day]) for schedule_day in schedule_days
    ]

    for i, day_date in enumerate(days_and_dates):
        label, date = day_date

        x_pos = round(i * column_width, 3)
        latex.append(
            f"\\node[anchor=south west] at ($(origin)+({x_pos} in, \\weekdayline in)$) {{\n"
            f"  \\makebox[2.1in][s]{{\\Huge {label} \\large {date.strftime('%-m/%-d')}}}}};"
        )

    return "\n".join(latex)


def hw_labels(schedule_days: list):
    latex = []

    column_width = round(11 / len(schedule_days), 3)

    for i in range(len(schedule_days)):
        latex.append(
            f"\\node[anchor=north west] at ($(origin)+({round(i * column_width, 3)} in, "
            " \\hwline in)$) {\\Large HW};"
        )

    return "\n".join(latex)


def notes_labels(schedule_days: list):
    latex = []

    column_width = round(11 / len(schedule_days), 3)

    for i in range(len(schedule_days)):
        latex.append(
            f"\\node[anchor=north west] at ($(origin)+({round(i * column_width, 3)} in, "
            "\\notesline in)$) {\\Large Notes};"
        )

    return "\n".join(latex)


# while True:
#    schedule = input("\nEnter a schedule: ")
#
#    if not valid_schedule(schedule):
#        print("Invalid schedule.")
#        continue
#
#    weeks_meeting_days = meeting_days(schedule)
#
#    print(vertical_lines_latex(len(schedule)))
#    print()
#    print(weekday_labels_latex(weeks_meeting_days, datetime.datetime.today()))
#    print()
#    print(hw_labels(weeks_meeting_days))
#    print()
#    print(notes_labels(weeks_meeting_days))
#    print()
#

template = r"""\documentclass[letterpaper, landscape]{article}
\usepackage[margin=0in]{geometry}
\usepackage{tikz}
\usetikzlibrary{calc}

%\newcommand{\daywidth}{2.2}
\newcommand{\classline}{8}
\newcommand{\weekdayline}{7.5}
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
\node[anchor=south west] at ($(origin)+(0in,\classline in)$) {
  \makebox[0.98\textwidth][s]{\Huge \textsc{Weekly Plan \hfill !!DATE_RANGE!! \hfill \class}}
};

% HW labels
!!HW_LABELS!!

% Notes labels
!!NOTES_LABELS!!

\end{tikzpicture}

\end{document}
"""


today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday())
workdays_thisweek = [monday + datetime.timedelta(days=i) for i in range(5)]
workdays_nextweek = [monday + datetime.timedelta(days=i + 7) for i in range(5)]

print("Today:", today)
print("This week's workdays:")
for d in workdays_thisweek:
    print(f"{d.strftime('%-m')}/{d.strftime('%-d')}")

print("\nNext week's workdays:")
for d in workdays_nextweek:
    print(f"{d.strftime('%-m')}/{d.strftime('%-d')}")

plan_week = 1000

while plan_week not in [0, 1]:
    print("\nWhich week do you want to print planning sheets for?")
    print(
        f"0. {workdays_thisweek[0].strftime('%-m')}/{workdays_thisweek[0].strftime('%-d')}"
        f" -- {workdays_thisweek[4].strftime('%-m')}/{workdays_thisweek[4].strftime('%-d')}"
    )
    print(
        f"1. {workdays_nextweek[0].strftime('%-m')}/{workdays_nextweek[0].strftime('%-d')}"
        f" -- {workdays_nextweek[4].strftime('%-m')}/{workdays_nextweek[4].strftime('%-d')}"
    )

    plan_week = input("Week: ")

    try:
        plan_week = int(plan_week)
    except ValueError:
        plan_week = 1000

if plan_week == 0:
    selected_days = workdays_thisweek
    suffix = "this_week"
elif plan_week == 1:
    selected_days = workdays_nextweek
    suffix = "next_week"

header_range = (
    f"{selected_days[0].strftime('%-d %b')} -- {selected_days[4].strftime('%-d %b %Y')}"
)

# Ensure the output directory exists
os.makedirs("./tex_output", exist_ok=True)

for course in COURSES.keys():
    tex_file_code = template
    course_schedule = COURSES[course]

    if not valid_schedule(course_schedule):
        raise ValueError("Invalid schedule.")

    scheduled_days = meeting_days(course_schedule)

    tex_file_code = tex_file_code.replace("!!COURSE!!", course)
    tex_file_code = tex_file_code.replace("!!DATE_RANGE!!", header_range)
    tex_file_code = tex_file_code.replace("!!HW_LABELS!!", hw_labels(scheduled_days))
    tex_file_code = tex_file_code.replace(
        "!!NOTES_LABELS!!", notes_labels(scheduled_days)
    )
    tex_file_code = tex_file_code.replace(
        "!!DAYS_OF_WEEK_LABELS!!",
        weekday_labels_latex(scheduled_days, selected_days[0]),
    )
    tex_file_code = tex_file_code.replace(
        "!!VERTICAL_LINES!!", vertical_lines_latex(len(scheduled_days))
    )

    for label, day in zip(date_labels, selected_days):
        tex_file_code = tex_file_code.replace(
            label, f"{day.strftime('%-m')}/{day.strftime('%-d')}"
        )

    course_file = course.lower().replace(" ", "_")
    filename = f"{course_file}_{suffix}.tex"
    filepath = f"./tex_output/{filename}"

    # Write the .tex file
    with open(filepath, "w", encoding="utf-8") as tex_file:
        tex_file.write(tex_file_code.strip() + "\n")

    print(f"Compiling {filename}...")

    # 1. COMPILE with latexmk
    try:
        subprocess.run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-outdir=./tex_output",
                filepath,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print("  -> Success!")

        # 2. CLEANUP auxiliary files
        # We use latexmk -c to clean up the files it just created
        subprocess.run(
            ["latexmk", "-c", "-outdir=./tex_output", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  -> Cleaned auxiliary files.")

    except subprocess.CalledProcessError:
        print(f"  -> Error compiling {filename}")

if __name__ == "__main__":
    thing = WeekPlanner("Humanities III", "MWF", datetime.datetime.today())
