from datetime import datetime, timedelta
import calendar
from .parser import CronExpression, CronField, Parser
from typing import Set

class Calculator:
    """
    Calculates the next execution time for a given cron expression.
    """

    @staticmethod
    def get_next_run_time(expression: str, base_time: datetime) -> datetime:
        """
        Calculate the next run time after the base_time.

        Args:
            expression (str): The cron expression.
            base_time (datetime): The starting time.

        Returns:
            datetime: The next execution time.
        """
        cron = Parser.parse(expression)

        # Start looking from 1 minute after base_time
        current = base_time.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Limit the search to 5 years to avoid infinite loops with impossible expressions
        end_time = current + timedelta(days=365 * 5)

        while current < end_time:
            if current.month not in cron.month.values:
                # Skip to next month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1, day=1, hour=0, minute=0)
                else:
                    current = current.replace(month=current.month + 1, day=1, hour=0, minute=0)
                continue

            # Day matching (DOM and DOW)
            # Standard cron: if both are restricted, it matches if EITHER matches.
            # But if one is * or ?, it must match the other.
            dom_match = Calculator._match_dom(cron.day_of_month, current)
            dow_match = Calculator._match_dow(cron.day_of_week, current)

            # If both are restricted (not * and not ?), then OR logic
            both_restricted = cron.day_of_month.raw_value not in ("*", "?") and \
                             cron.day_of_week.raw_value not in ("*", "?")

            if both_restricted:
                day_match = dom_match or dow_match
            else:
                day_match = dom_match and dow_match

            if not day_match:
                current += timedelta(days=1)
                current = current.replace(hour=0, minute=0)
                continue

            if current.hour not in cron.hour.values:
                current += timedelta(hours=1)
                current = current.replace(minute=0)
                continue

            if current.minute not in cron.minute.values:
                current += timedelta(minutes=1)
                continue

            return current

        raise ValueError("Could not find next execution time within 5 years.")

    @staticmethod
    def _match_dom(field: CronField, dt: datetime) -> bool:
        """
        Checks if the day of month matches.

        Args:
            field (CronField): The DOM field.
            dt (datetime): Current time being checked.

        Returns:
            bool: True if it matches.
        """
        if field.raw_value in ("*", "?"):
            return True

        if dt.day in field.values:
            return True

        last_day = calendar.monthrange(dt.year, dt.month)[1]

        if field.special_char == "L":
            return dt.day == last_day

        if field.w_flag is not None:
            target_day = field.w_flag
            # Closest weekday to target_day
            actual_target = Calculator._get_closest_weekday(dt.year, dt.month, target_day)
            return dt.day == actual_target

        return False

    @staticmethod
    def _match_dow(field: CronField, dt: datetime) -> bool:
        """
        Checks if the day of week matches.

        Args:
            field (CronField): The DOW field.
            dt (datetime): Current time being checked.

        Returns:
            bool: True if it matches.
        """
        if field.raw_value in ("*", "?"):
            return True

        # datetime.weekday() is 0-6 (Mon-Sun), our cron is 0-6 (Sun-Sat)
        cron_dow = (dt.weekday() + 1) % 7

        if cron_dow in field.values:
            return True

        if field.l_flag:
             if field.special_char and field.special_char.endswith("L"):
                 if field.special_char == "L":
                      # In DOW, "L" usually means Saturday (6)
                      target_dow = 6
                 else:
                      target_dow = int(field.special_char.replace("L", ""))

                 if cron_dow == target_dow:
                     last_day = calendar.monthrange(dt.year, dt.month)[1]
                     # Is this the last such day in the month?
                     return dt.day + 7 > last_day

        if field.hash_val:
            target_dow, nth = field.hash_val
            if cron_dow == target_dow:
                return (dt.day - 1) // 7 + 1 == nth

        return False

    @staticmethod
    def _get_closest_weekday(year: int, month: int, day: int) -> int:
        """
        Finds the closest weekday to a given day in a month.

        Args:
            year (int): Year.
            month (int): Month.
            day (int): Target day.

        Returns:
            int: The actual day.
        """
        last_day = calendar.monthrange(year, month)[1]
        target_day = min(day, last_day)
        dt = datetime(year, month, target_day)
        dow = dt.weekday() # 0=Mon, 6=Sun

        if dow < 5: # Mon-Fri
            return target_day

        if dow == 5: # Sat
            if target_day > 1:
                return target_day - 1
            else:
                return target_day + 2 # Must be in the same month
        else: # Sun
            if target_day < last_day:
                return target_day + 1
            else:
                return target_day - 2
