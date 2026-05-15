Weekly Planner
==============

This is a short script designed to create a weekly planner for my classes.

# Requirements

* The Typst compiler.

* [deprecated; there's still a version that works with LaTeX, but the Typst
  version with the template is way more elegant. If you want to use the LaTeX
  version, you'll need...] A LaTeX installation with pdflatex.

* Python

N.b. This was written on a Linux machine. I don't know any reason it shouldn't
work on Windows or MacOS.

# Steps

1. Edit the schedules in 'course_schedules.json'.

2. Run 'python3 weekly_planner.py'.

3. Choose the week you want and press [enter].

4. The planning pages should save and compile in the subfolder ./tex_output/.

