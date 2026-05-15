#!/usr/bin/python3

import datetime
from datetime import date
from pathlib import Path
import subprocess
import curses

from curses_week_picker import date_picker
from typst_planner_template import typst_planner_template

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

TYPST_TEMPLATE = typst_planner_template


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

    @property
    def typst(self):
        self.friday = self.monday + datetime.timedelta(days=4)
        self.header_range = (
            f"{self.monday.strftime('%-m/%-d')} -- {self.friday.strftime('%-m/%-d')}"
        )

        days_dates = [
            f'  ("{day.strftime("%A")}", "{day.strftime("%-m/%-d")}"),'
            for day in self.schedule_dates
        ]
        days_dates_code = "\n".join(days_dates)

        typ_file_code = TYPST_TEMPLATE.replace("!!COURSE!!", self.course)
        typ_file_code = typ_file_code.replace("!!DATE_RANGE!!", self.header_range)
        typ_file_code = typ_file_code.replace("!!DAYS_DATES!!", days_dates_code)

        return typ_file_code


class WeekPlanIO:
    def __init__(
        self,
        week_planner: WeekPlanner,
    ):
        self.week_planner = week_planner
        self.compilation_subfolder = Path("./typ_output/")
        self.compilation_subfolder.mkdir(exist_ok=True)
        self.typst_file = Path(
            "planner_"
            + week_planner.course.lower().replace(" ", "_")
            + "_"
            + week_planner.monday.isoformat()
            + ".typ"
        )
        self.typst_file_path = self.compilation_subfolder / self.typst_file

    def save_typst(self):
        # Write the .typ file
        with open(self.typst_file_path, "w", encoding="utf-8") as typ_file:
            typ_file.write(self.week_planner.typst + "\n")

    def compile_typst(self):
        if not Path.exists(self.typst_file_path):
            self.save_typst()

        print(f"Compiling {self.typst_file}...")

        # 1. COMPILE with typstmk
        try:
            subprocess.run(
                [
                    "typst",
                    "compile",
                    self.typst_file_path,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            print("  -> Success!")

        except subprocess.CalledProcessError:
            print(f"  -> Error compiling {self.typst_file_path}")


if __name__ == "__main__":
    day_in_week = curses.wrapper(date_picker)

    for course in COURSES.keys():
        planner = WeekPlanner(course, COURSES[course], day_in_week)
        WeekPlanIO(planner).compile_typst()
