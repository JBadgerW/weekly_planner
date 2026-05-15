typst_planner_template = r"""
#set page(
  paper: "us-letter",
  flipped: true,
  margin: 0in,
)
#set text(font: "New Computer Modern")

// ==================================================
// DOCUMENT VARIABLES
// ==================================================
#let class = "Humanities IV"
#let week-of = "5/18 -- 5/22"
#let days = (
  //("Monday",    "5/18"),
  ("Tuesday",   "5/19"),
  //("Wednesday", "5/20"),
  //("Thursday",  "5/21"),
  ("Friday",    "5/22"),
)
#let num-days = days.len()

// ==================================================
// LAYOUT CONSTANTS
// ==================================================
#let header-row-height  = 0.5625in
#let day-label-height   = 0.5in
#let main-row-height    = 4.5in   // classwork area
#let hw-row-height      = 1.25in
#let notes-row-height   = 1.6875in

// ==================================================
// CALENDAR
// ==================================================

// Helper: a cell with padding and specified content
#let cell(column, body, ..args) = rect(
  width: 100%,
  height: 100%,
  stroke: 0.5pt,
  inset: (x: if column == 0 { 0.25in } else { 0.1in }, y: 0.1in),
  ..args,
  body,
)

#grid(
  columns: num-days,
  rows: (header-row-height, day-label-height, main-row-height, hw-row-height, notes-row-height),

  // ── Row 1: full-width header ──────────────────────
  grid.cell(colspan: num-days)[
    #rect(width: 100%, height: 100%, stroke: 0.5pt, inset: (x: 0.25in, y: 0.1in))[
      #align(bottom)[
        #text(size: 24pt, smallcaps("Weekly Plan"))
        #h(1fr)
        #text(size: 24pt, week-of)
        #h(1fr)
        #text(size: 24pt, smallcaps(class))
      ]
    ]
  ],

  // Row 2: days — enumerate() gives you (index, value) pairs
  ..days.enumerate().map(((col, (day, date))) =>
    cell(col, align(bottom)[
      #text(size: 20pt)[#day]
      #h(0.3em)
      #text(size: 11pt)[#date]
    ])
  ),

  // Row 3: range() already gives you the index directly — don't discard it
  ..range(num-days).map(col => cell(col, [])),

  // Row 4: HW
  ..range(num-days).map(col => cell(col,
    text(size: 14pt)[HW]
  )),

  // Row 5: Notes
  ..range(num-days).map(col => cell(col,
    text(size: 14pt)[Notes]
  )),
)
"""
