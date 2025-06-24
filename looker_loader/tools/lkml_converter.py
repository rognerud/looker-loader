import lkml
import logging
import re

def fix_multiline_indentation(text, indent_size=2):
    lines = text.split('\n')
    fixed_lines = []

    multiline_keys = ['html', 'sql', 'description']  # add more keys as needed
    inside_multiline = False
    current_indent = ""

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        leading_spaces = ' ' * (len(line) - len(stripped))

        # Check if starting a multiline field
        if not inside_multiline:
            fixed_lines.append(line)

            for key in multiline_keys:
                if re.match(rf'^{key}:\s*<[^>]*>?$', stripped) or stripped.startswith(f"{key}:") and not stripped.endswith(';;'):
                    inside_multiline = True
                    current_indent = leading_spaces + ' ' * indent_size
                    break

        else:
            # Check if the multiline block has ended
            if stripped.strip().endswith(';;'):
                fixed_lines.append(current_indent + stripped)
                inside_multiline = False
            else:
                fixed_lines.append(current_indent + stripped)

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