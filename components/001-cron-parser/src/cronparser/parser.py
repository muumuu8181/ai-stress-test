from typing import Set, List, Dict, Optional, Tuple
import re

class CronField:
    """
    Represents a single field in a cron expression.

    Attributes:
        name (str): Name of the field (e.g., 'minute').
        min_val (int): Minimum valid value for the field.
        max_val (int): Maximum valid value for the field.
        raw_value (str): The raw string value of the field.
        values (Set[int]): Set of allowed integer values for this field.
        special_char (Optional[str]): Stores special characters like 'L', '15W', '5#2'.
        l_flag (bool): True if 'L' is present in the field.
        w_flag (Optional[int]): Target day for 'W' character.
        hash_val (Optional[Tuple[int, int]]): (weekday, nth) for '#' character.
    """
    def __init__(self, name: str, min_val: int, max_val: int, value: str):
        """
        Initialize the CronField.

        Args:
            name (str): Field name.
            min_val (int): Min value.
            max_val (int): Max value.
            value (str): Raw string value.
        """
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.raw_value = value
        self.values: Set[int] = set()
        self.special_char: Optional[str] = None
        self.l_flag: bool = False
        self.w_flag: Optional[int] = None
        self.hash_val: Optional[Tuple[int, int]] = None # (weekday, nth)
        self.parse()

    def parse(self) -> None:
        """
        Parses the raw value and populates the values set.

        Raises:
            ValueError: If the field is empty or contains invalid values.
        """
        if not self.raw_value:
             raise ValueError(f"Field {self.name} cannot be empty.")

        if self.raw_value == "*" or self.raw_value == "?":
            self.values = set(range(self.min_val, self.max_val + 1))
            return

        parts = self.raw_value.split(",")
        for part in parts:
            self._parse_part(part)

    def _parse_part(self, part: str) -> None:
        """
        Parses a single part of a comma-separated field value.

        Args:
            part (str): A part of the field value.
        """
        if "/" in part:
            range_part, step_part = part.split("/")
            step = int(step_part)
            if range_part == "*":
                start, end = self.min_val, self.max_val
            elif "-" in range_part:
                start, end = map(int, range_part.split("-"))
            else:
                start, end = int(range_part), self.max_val

            self._add_range(start, end, step)
        elif "-" in part:
            start, end = map(int, part.split("-"))
            self._add_range(start, end, 1)
        elif "L" in part:
            self.l_flag = True
            if self.name == "day_of_week":
                if part == "L":
                    self.special_char = "L"
                else:
                    # Handle 5L, 6L etc.
                    val_str = part.replace("L", "")
                    if not val_str: # Should not happen with current logic but for safety
                         self.special_char = "L"
                    else:
                         val = int(val_str)
                         if self.min_val <= val <= self.max_val:
                             self.special_char = f"{val}L"
                         else:
                             raise ValueError(f"Invalid L value in {self.name}")
            elif self.name == "day_of_month" and part == "L":
                 self.special_char = "L"
            else:
                raise ValueError(f"L character not supported for field {self.name}")
        elif "W" in part:
            if self.name != "day_of_month":
                raise ValueError(f"W character only supported for day_of_month")
            day = int(part.replace("W", ""))
            self.w_flag = day
            self.special_char = f"{day}W"
        elif "#" in part:
             if self.name != "day_of_week":
                 raise ValueError(f"# character only supported for day_of_week")
             dow, nth = map(int, part.split("#"))
             self.hash_val = (dow, nth)
             self.special_char = f"{dow}#{nth}"
        else:
            try:
                val = int(part)
                if self.min_val <= val <= self.max_val:
                    self.values.add(val)
                else:
                    raise ValueError(f"Value {val} out of range for {self.name}")
            except ValueError:
                if not any(c in part for c in "LW#"):
                    raise

    def _add_range(self, start: int, end: int, step: int) -> None:
        """
        Adds a range of values to the field's allowed values.

        Args:
            start (int): Start of range.
            end (int): End of range.
            step (int): Increment step.
        """
        if start < self.min_val or end > self.max_val or start > end:
            raise ValueError(f"Range {start}-{end} invalid for {self.name}")
        for i in range(start, end + 1, step):
            self.values.add(i)

class CronExpression:
    """
    Represents a full cron expression with 5 fields.
    """
    def __init__(self, minute: str, hour: str, day_of_month: str, month: str, day_of_week: str):
        """
        Initialize the CronExpression with field strings.

        Args:
            minute (str): Minute field.
            hour (str): Hour field.
            day_of_month (str): Day of month field.
            month (str): Month field.
            day_of_week (str): Day of week field.
        """
        self.minute = CronField("minute", 0, 59, minute)
        self.hour = CronField("hour", 0, 23, hour)
        self.day_of_month = CronField("day_of_month", 1, 31, day_of_month)
        self.month = CronField("month", 1, 12, month)
        self.day_of_week = CronField("day_of_week", 0, 6, day_of_week)

    def __repr__(self):
        return f"CronExpression(min={self.minute.raw_value}, hour={self.hour.raw_value}, dom={self.day_of_month.raw_value}, month={self.month.raw_value}, dow={self.day_of_week.raw_value})"

class Parser:
    """
    Parser that uses Lexer to tokenize and then creates CronExpression.
    """
    @staticmethod
    def parse(expression: str) -> CronExpression:
        """
        Parses a cron expression string.

        Args:
            expression (str): The cron expression string.

        Returns:
            CronExpression: The parsed expression object.
        """
        from .lexer import Lexer
        lexer = Lexer(expression)
        tokens = lexer.tokenize()
        return CronExpression(*tokens)
