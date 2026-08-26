"""A small Flask web app for organizing study sessions."""

import json
import os
from datetime import date
from json import JSONDecodeError
from pathlib import Path

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from sympy import Eq, SympifyError, solve, sympify


BASE_DIR = Path(__file__).parent
EXERCISES_DIR = BASE_DIR / "static" / "exercises"
LOG_FILE = BASE_DIR / "daily_log.json"

app = Flask(__name__)

# Make sure the exercises folder exists, even when no PDFs have been added yet.
EXERCISES_DIR.mkdir(parents=True, exist_ok=True)


def solve_equation_text(equation_text: str) -> str:
    """Convert text into a SymPy equation and return its solutions."""
    equation_text = equation_text.strip().replace("^", "**")

    if not equation_text:
        raise ValueError("Please enter an equation.")
    if equation_text.count("=") > 1:
        raise ValueError("Please use only one equals sign.")

    # Expressions without an equals sign are solved as expression = 0.
    if "=" in equation_text:
        left_side, right_side = equation_text.split("=", maxsplit=1)
        equation = Eq(sympify(left_side), sympify(right_side))
    else:
        equation = Eq(sympify(equation_text), 0)

    # Find the variables in the equation, then ask SymPy to solve it.
    variables = sorted(equation.free_symbols, key=str)
    solutions = solve(equation, variables)
    return str(solutions) if solutions else "No solution was found."


def load_daily_entries() -> list[dict[str, str]]:
    """Read saved study entries from the JSON file."""
    if not LOG_FILE.exists():
        return []

    try:
        entries = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return []

    return entries if isinstance(entries, list) else []


def save_daily_entries(entries: list[dict[str, str]]) -> None:
    """Save study entries in a readable JSON format."""
    LOG_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def get_exercise_files() -> list[str]:
    """Return the PDF filenames currently in the exercises folder."""
    return sorted(
        [
            file_path.name
            for file_path in EXERCISES_DIR.iterdir()
            if file_path.is_file() and file_path.suffix.lower() == ".pdf"
        ],
        key=str.lower,
    )


@app.get("/")
def home():
    """Show the home page."""
    return render_template("home.html")


@app.route("/solver", methods=["GET", "POST"])
def solver():
    """Display the equation form and solve submitted equations."""
    solution = None
    error = None
    equation = ""

    if request.method == "POST":
        equation = request.form.get("equation", "")
        try:
            solution = solve_equation_text(equation)
        except (SympifyError, TypeError, ValueError, NotImplementedError) as exc:
            error = f"Could not solve that equation: {exc}"

    return render_template(
        "solver.html",
        equation=equation,
        solution=solution,
        error=error,
    )


@app.get("/exercises")
def exercises():
    """Show all PDF exercises from the exercises folder."""
    return render_template("exercises.html", exercise_files=get_exercise_files())


@app.get("/exercises/<path:filename>")
def exercise_file(filename: str):
    """Open a PDF exercise from the exercises folder."""
    # Only serve files that are in the displayed list and have a PDF extension.
    if filename not in get_exercise_files() or not filename.lower().endswith(".pdf"):
        abort(404)
    return send_from_directory(str(EXERCISES_DIR), filename)


@app.route("/daily-log", methods=["GET", "POST"])
def daily_log():
    """Add a dated study entry and display previous entries."""
    error = None

    if request.method == "POST":
        entry_text = request.form.get("entry", "").strip()
        if not entry_text:
            error = "Please enter a study note before saving."
        else:
            entries = load_daily_entries()
            entries.append({"date": date.today().isoformat(), "entry": entry_text})
            save_daily_entries(entries)
            return redirect(url_for("daily_log", saved="1"))

    entries = list(reversed(load_daily_entries()))
    return render_template(
        "daily_log.html",
        entries=entries,
        error=error,
        saved=request.args.get("saved") == "1",
    )


if __name__ == "__main__":
    # Replit provides PORT when the app is started by a workflow.
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)