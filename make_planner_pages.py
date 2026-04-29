import datetime
import subprocess
import os  # Added for path operations (if needed)

template = r"""\documentclass[letterpaper, landscape]{article}
\usepackage[margin=0in]{geometry}
\usepackage{tikz}
\usetikzlibrary{calc}

\newcommand{\daywidth}{2.2}
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

% Vertical lines (Spacers between days)
\draw ($(origin) + (1*\daywidth in, 0 in)$) -- ($(origin) + (1*\daywidth in, \classline in)$);
\draw ($(origin) + (2*\daywidth in, 0 in)$) -- ($(origin) + (2*\daywidth in, \classline in)$);
\draw ($(origin) + (3*\daywidth in, 0 in)$) -- ($(origin) + (3*\daywidth in, \classline in)$);
\draw ($(origin) + (4*\daywidth in, 0 in)$) -- ($(origin) + (4*\daywidth in, \classline in)$);

% Horizontal lines
\draw ($(origin) + (0 in, \classline in)$) -- ($(origin) + (11 in, \classline in)$);
\draw ($(origin) + (0 in, \weekdayline in)$) -- ($(origin) + (11 in, \weekdayline in)$);
\draw ($(origin) + (0 in, \hwline in)$) -- ($(origin) + (11 in, \hwline in)$);
\draw ($(origin) + (0 in, \notesline in)$) -- ($(origin) + (11 in, \notesline in)$);

% Days of the week labels
\node[anchor=south west] at ($(origin)+(0 in, \weekdayline in)$) {
  \makebox[2.1in][s]{\Huge Monday \large !!MONDAY!!}};
\node[anchor=south west] at ($(origin)+(1*\daywidth in, \weekdayline in)$) {
  \makebox[2.1in][s]{\Huge Tuesday \large !!TUESDAY!!}};
\node[anchor=south west] at ($(origin)+(2*\daywidth in, \weekdayline in)$) {
  \makebox[2.1in][s]{\Huge Wednesday \large !!WEDNESDAY!!}};
\node[anchor=south west] at ($(origin)+(3*\daywidth in, \weekdayline in)$) {
  \makebox[2.1in][s]{\Huge Thursday \large !!THURSDAY!!}};
\node[anchor=south west] at ($(origin)+(4*\daywidth in, \weekdayline in)$) {
  \makebox[2.1in][s]{\Huge Friday \large !!FRIDAY!!}};

% Class headline and week
\node[anchor=south west] at ($(origin)+(0in,\classline in)$) {
  \makebox[0.98\textwidth][s]{\Huge \textsc{Weekly Plan \hfill !!DATE_RANGE!! \hfill \class}}
};

% HW labels
\node[anchor=north west] at ($(origin)+(0 in, \hwline in)$) {\Large HW};
\node[anchor=north west] at ($(origin)+(1*\daywidth in, \hwline in)$) {\Large HW};
\node[anchor=north west] at ($(origin)+(2*\daywidth in, \hwline in)$) {\Large HW};
\node[anchor=north west] at ($(origin)+(3*\daywidth in, \hwline in)$) {\Large HW};
\node[anchor=north west] at ($(origin)+(4*\daywidth in, \hwline in)$) {\Large HW};

% Notes labels
\node[anchor=north west] at ($(origin)+(0 in, \notesline in)$) {\Large Notes};
\node[anchor=north west] at ($(origin)+(1*\daywidth in, \notesline in)$) {\Large Notes};
\node[anchor=north west] at ($(origin)+(2*\daywidth in, \notesline in)$) {\Large Notes};
\node[anchor=north west] at ($(origin)+(3*\daywidth in, \notesline in)$) {\Large Notes};
\node[anchor=north west] at ($(origin)+(4*\daywidth in, \notesline in)$) {\Large Notes};

\end{tikzpicture}

\end{document}
"""


courses = [
    "Humanities IV",
    "Geometry",
    "Advanced Math",
    "Computer Science",
]

date_labels = [
    "!!MONDAY!!",
    "!!TUESDAY!!",
    "!!WEDNESDAY!!",
    "!!THURSDAY!!",
    "!!FRIDAY!!",
]

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

for course in courses:
    tex_file_code = template

    tex_file_code = tex_file_code.replace("!!COURSE!!", course)
    tex_file_code = tex_file_code.replace("!!DATE_RANGE!!", header_range)

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
