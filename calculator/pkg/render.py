def render(expression, result):
    result_str = str(int(result) if isinstance(result, float) and result.is_integer() else result)
    box_width = max(len(expression), len(result_str)) + 4
    lines = [
        "┌" + "─" * box_width + "┐",
        "│  " + expression + " " * (box_width - len(expression) - 2) + "│",
        "│" + " " * box_width + "│",
        "│  =" + " " * (box_width - 3) + "│",
        "│" + " " * box_width + "│",
        "│  " + result_str + " " * (box_width - len(result_str) - 2) + "│",
        "└" + "─" * box_width + "┘",
    ]
    return "\n".join(lines)
