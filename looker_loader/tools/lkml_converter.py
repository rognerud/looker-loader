import lkml
import logging

def fix_multiline_indentation(text, indent_size=2):
    lines = text.split('\n')
    fixed_lines = []
    inside_multiline = False
    current_indent = ""

    for line in lines:
        stripped = line.lstrip()

        if not inside_multiline:
            fixed_lines.append(line)
            if stripped.endswith('html: "'):
                inside_multiline = True
                current_indent = ' ' * (len(line) - len(stripped) + indent_size)
        else:
            fixed_lines.append(current_indent + stripped)
            if stripped.endswith('" ;;'):
                inside_multiline = False

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

def convert_to_lkml(data):
    """Convert a dictionary to a LookML string."""
        
    python_r = []
    for thing in data:
        python_r.append(remove_empty_from_dict(thing.dict(exclude_none=True)))

    dumpfile = {
        "views": python_r,
    }

    lk = lkml.dump(dumpfile)
    indention_fixed = fix_multiline_indentation(lk)

    return indention_fixed