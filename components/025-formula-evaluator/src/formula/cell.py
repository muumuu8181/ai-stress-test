from typing import Any, Optional, List, Set

# Error types
ERROR_REF = "#REF!"
ERROR_VALUE = "#VALUE!"
ERROR_DIV0 = "#DIV/0!"
ERROR_NAME = "#NAME?"
ERROR_CIRC = "#CIRC!"
ERROR_NA = "#N/A"

# List of all spreadsheet error constants
ALL_ERRORS = {ERROR_REF, ERROR_VALUE, ERROR_DIV0, ERROR_NAME, ERROR_CIRC, ERROR_NA}

def is_error(value: Any) -> bool:
    """
    Checks if a value is a spreadsheet error.

    Args:
        value: The value to check.

    Returns:
        True if it's a spreadsheet error, False otherwise.
    """
    return isinstance(value, str) and value in ALL_ERRORS

class Cell:
    """
    Represents a single cell in a spreadsheet.
    """

    def __init__(self, address: str) -> None:
        """
        Initialize a cell with its address.

        Args:
            address: The cell address (e.g., 'A1').
        """
        self.address: str = address
        self.raw_value: str = ""
        self.formula: Optional[str] = None
        self.value: Any = None
        self.dependencies: Set[str] = set()
        self.format_str: Optional[str] = None

    def set_value(self, value: str) -> None:
        """
        Set the raw value of the cell. If it starts with '=', it's treated as a formula.

        Args:
            value: The raw input string.
        """
        self.raw_value = value
        if value.startswith("="):
            self.formula = value[1:]
            # Initial state for formula cells could be #ERROR! if it's empty
            if not self.formula.strip():
                self.value = "#ERROR!"
            else:
                self.value = None # To be evaluated
        else:
            self.formula = None
            try:
                # Try to convert to float if it looks like a number
                if value.replace(".", "", 1).isdigit() or (value.startswith("-") and value[1:].replace(".", "", 1).isdigit()):
                    num = float(value)
                    if num.is_integer():
                        self.value = int(num)
                    else:
                        self.value = num
                else:
                    self.value = value
            except ValueError:
                self.value = value

    def get_display_value(self) -> str:
        """
        Returns the formatted string representation of the cell's value.

        Returns:
            The display value.
        """
        if self.value is None:
            return ""

        if is_error(self.value):
            return str(self.value)

        if isinstance(self.value, (int, float)):
            if self.format_str:
                try:
                    return format(self.value, self.format_str)
                except (ValueError, TypeError):
                    pass

            if isinstance(self.value, float):
                if self.value.is_integer():
                    return str(int(self.value))
                # For non-integers, show at least 2 decimal places if they exist, but don't hardcode .2f
                # Actually, standard spreadsheets often show as is or with some limit.
                # Let's use a simpler format for default.
                res = f"{self.value:g}"
                return res
            return str(self.value)

        return str(self.value)
