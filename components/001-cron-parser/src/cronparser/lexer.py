from typing import List

class Lexer:
    """
    Lexer for cron expressions.
    Splits the expression into its component fields.
    """

    def __init__(self, expression: str):
        """
        Initialize the lexer with a cron expression.

        Args:
            expression (str): The cron expression to tokenize.
        """
        self.expression = expression.strip()

    def tokenize(self) -> List[str]:
        """
        Tokenize the cron expression into its 5 fields.

        Returns:
            List[str]: A list of 5 strings, each representing a cron field.

        Raises:
            ValueError: If the expression does not contain exactly 5 fields.
        """
        if not self.expression:
            raise ValueError("Cron expression cannot be empty.")

        fields = self.expression.split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron expression: '{self.expression}'. Expected 5 fields, got {len(fields)}.")

        return fields
