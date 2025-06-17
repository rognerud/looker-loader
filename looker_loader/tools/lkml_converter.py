import lkml
import logging
import re

def fix_multiline_indentation(text, indent_size=2):
    lines = text.split('\n')
    fixed_lines = []
    inside_multiline_string = False
    current_indent = ""

    for line in lines:
        stripped = line.lstrip()
        leading_spaces = ' ' * (len(line) - len(stripped))

        # If not currently inside a multiline string
        if not inside_multiline_string:
            fixed_lines.append(line)
            # Check if a string starts but does not end on the same line
            quote_starts = stripped.count('"') % 2 == 1
            if quote_starts:
                inside_multiline_string = True
                current_indent = leading_spaces + (' ' * indent_size)
        else:
            # Inside a multiline string
            fixed_lines.append(current_indent + stripped)
            # Check if string ends on this line
            if stripped.count('"') % 2 == 1:
                inside_multiline_string = False

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