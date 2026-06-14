import re

def sanitize_string(text: str) -> str:
    """
    Remove basic HTML tags and javascript protocol sequences to mitigate XSS injections.
    """
    if not text:
        return ""
    # Strip HTML tags
    cleaned = re.sub(r'<[^>]*>', '', text)
    # Strip script tags or javascript protocols
    cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
    # Strip event handlers (e.g. onerror, onload, onclick)
    cleaned = re.sub(r'on\w+\s*=', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()
