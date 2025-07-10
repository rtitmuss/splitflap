import re

CRONTAB_REGEX = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)$')


def expand_field(field, min_val, max_val):
    """Expands a crontab field to a list of valid values."""
    values = set()

    for part in field.split(","):
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:  # Handle step values (*/5, 10-20/2, etc.)
            range_part, step = part.split("/")
            step = int(step)
            if range_part == "*":
                values.update(range(min_val, max_val + 1, step))
            else:
                start, end = map(int, range_part.split("-"))
                if start > end:  # Handle overnight ranges
                    values.update(range(start, max_val + 1, step))
                    values.update(range(min_val, end + 1, step))
                else:
                    values.update(range(start, end + 1, step))
        elif "-" in part:  # Handle ranges (e.g., 10-20)
            start, end = map(int, part.split("-"))
            if start > end:  # Handle overnight ranges
                values.update(range(start, max_val + 1))
                values.update(range(min_val, end + 1))
            else:
                values.update(range(start, end + 1))
        else:  # Handle single values
            values.add(int(part))

    return sorted(values)


def parse_crontab_line(line):
    """Parses a crontab line into a list of lists containing valid time values and extracts the command."""
    match = CRONTAB_REGEX.match(line)
    if not match:
        raise ValueError("Invalid crontab line format")

    fields = [match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)]
    command = match.group(6)  # Preserve all spaces in the command

    return [
        expand_field(fields[0], 0, 59),  # Minutes
        expand_field(fields[1], 0, 23),  # Hours
        expand_field(fields[2], 1, 31),  # Days
        expand_field(fields[3], 1, 12),  # Months
        expand_field(fields[4], 0, 6),  # Weekdays (0=Sunday, 6=Saturday)
        command
    ]


def matches_crontab(cron_fields, time_tuple):
    """Checks if a given time matches the parsed crontab fields."""
    minute, hour, day, month, weekday = time_tuple
    return (
            minute in cron_fields[0] and
            hour in cron_fields[1] and
            day in cron_fields[2] and
            month in cron_fields[3] and
            weekday in cron_fields[4]
    )


def find_matching_crontab(time_tuple, crontab_lines):
    """Finds the first matching crontab line and returns the command."""
    for line in crontab_lines:
        try:
            cron_fields = parse_crontab_line(line)
            if matches_crontab(cron_fields, time_tuple):
                return cron_fields[5]  # Return the command
        except ValueError:
            continue
    return None  # No matching command found
