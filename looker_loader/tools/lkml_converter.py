import lkml
import logging
import re


def fix_multiline_indentation(text, indent_size=2):
    lines = text.split('\n')
    fixed_lines = []

    inside_quoted_multiline = False
    inside_unquoted_multiline = False
    multiline_key = None
    current_indent = ''

    for line in lines:
        stripped = line.lstrip()
        leading_spaces = ' ' * (len(line) - len(stripped))

        # Check if we're inside a quoted multiline string
        if inside_quoted_multiline:
            fixed_lines.append(current_indent + stripped)
            if '"' in stripped:
                # Count quotes to check for closing
                if stripped.count('"') % 2 == 1:
                    inside_quoted_multiline = False
            continue

        # Check if we're inside an unquoted multiline field
        if inside_unquoted_multiline:
            fixed_lines.append(current_indent + stripped)
            if stripped.endswith(';;'):
                inside_unquoted_multiline = False
            continue

        # Check for the start of a quoted multiline field
        match_quoted = re.match(r'^(\w+):\s*"([^"]*)$', stripped)
        if match_quoted:
            multiline_key = match_quoted.group(1)
            fixed_lines.append(line)
            if stripped.count('"') % 2 == 1:
                inside_quoted_multiline = True
                current_indent = leading_spaces + ' ' * indent_size
            continue

        # Check for unquoted multiline fields like html: <a ...>
        match_unquoted = re.match(r'^(\w+):\s*<[^>]*>?$', stripped)
        if match_unquoted and not stripped.endswith(';;'):
            multiline_key = match_unquoted.group(1)
            inside_unquoted_multiline = True
            current_indent = leading_spaces + ' ' * indent_size
            fixed_lines.append(line)
            continue

        # Default case: just keep the line
        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def remove_empty_from_dict(data):
  """Recursively removes keys with None or empty list values from a dictionary.

  Args:
    data: The dictionary to clean.

  Returns:
    A new dictionary with empty values removed.
  """
  if isinstance(data, dict):
    return {
        k: remove_empty_from_dict(v)
        for k, v in data.items()
        if v is not None and (not isinstance(v, list) or len(v) > 0)
    }
  elif isinstance(data, list):
    return [remove_empty_from_dict(item) for item in data if item is not None and (not isinstance(item, list) or len(item) > 0)]
  else:
    return data

def convert_to_lkml(views, explore):
    """Convert a dictionary to a LookML string."""
        
    python_r = []
    for view in views:
        python_r.append(remove_empty_from_dict(view.dict(exclude_none=True)))

    if explore is not None:
      dumpfile = {
        "explore": remove_empty_from_dict(explore),
        "views": python_r,
      }
    else:
      dumpfile = {
          "views": python_r,
      }
    try:
      lk = lkml.dump(dumpfile)
    except TypeError as e:
        logging.error(f"Error converting to LKML: {e}")
        try:
          for view in python_r:
            t = lkml.dump(view)
        except TypeError as e2:
            logging.error(f"Error converting individual view to LKML: {view}")
    indention_fixed = fix_multiline_indentation(lk)

    return indention_fixed