# Color codes for better logging
class Colors:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def log_info(message: str, color: str = Colors.CYAN):
    """Log info message with color"""
    print(f"{color}ℹ️  {message}{Colors.END}")


def log_success(message: str):
    """Log success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def log_error(message: str):
    """Log error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def log_warning(message: str):
    """Log warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def log_header(message: str):
    """Log header message with emphasis"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}🚀 {message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'=' * 60}{Colors.END}\n")


def plural(count: int, singular: str, plural_form: str | None = None) -> str:
    """Format a count with its noun, using the plural form unless there is exactly one"""
    if count == 1:
        return f"{count} {singular}"
    return f"{count} {plural_form or singular + 's'}"
