def escape_like_value(value):
    """Escape SQL LIKE wildcard and escape characters for literal searches."""
    return value.replace("!", "!!").replace("%", "!%").replace("_", "!_")
