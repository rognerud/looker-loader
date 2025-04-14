class CliError(Exception):
    """Base exception for CLI errors"""
    pass


class NotImplementedError(CliError):
    pass
