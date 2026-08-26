"""A simple command-line study assistant."""

from sympy import Eq, SympifyError, solve, sympify


def solve_math_equation() -> None:
    """Ask for an equation and solve it with SymPy."""
    equation_text = input(
        "\nEnter an equation (for example, 2*x + 3 = 9): "
    ).strip()

    if not equation_text:
        print("Please enter an equation.")
        return

    try:
        # Accept ^ as a familiar way to write powers.
        equation_text = equation_text.replace("^", "**")

        # If there is no equals sign, treat the input as an expression = 0.
        if "=" in equation_text:
            left_side, right_side = equation_text.split("=", maxsplit=1)
            equation = Eq(sympify(left_side), sympify(right_side))
        else:
            equation = Eq(sympify(equation_text), 0)

        # Find the variables in the equation, then ask SymPy to solve it.
        variables = sorted(equation.free_symbols, key=str)
        solutions = solve(equation, variables)

        if solutions:
            print(f"Solution(s): {solutions}")
        else:
            print("No solution was found.")
    except (SympifyError, TypeError, ValueError) as error:
        print(f"Could not understand that equation: {error}")


def main() -> None:
    """Show the menu and handle the selected option."""
    print("\nStudy Assistant")
    print("1) Solve a math equation")
    print("2) Review saved problems")
    print("3) Show stats")

    choice = input("\nChoose an option (1-3): ").strip()

    if choice == "1":
        solve_math_equation()
    elif choice == "2":
        print("\nReviewing saved problems is not implemented yet.")
    elif choice == "3":
        print("\nStats are not implemented yet.")
    else:
        print("\nInvalid choice. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()