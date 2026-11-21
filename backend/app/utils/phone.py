import re

def normalize_phone_number(raw_phone: str) -> str:
    """
    Validates and normalizes phone number to international E.164-compatible standard.
    Supports formats:
    - 9876543210 (10 digits -> defaults to +91 Indian format for public hospital context)
    - 09876543210 -> +919876543210
    - +919876543210
    - +14155552671
    - Strips spaces, dashes, parentheses.
    Raises ValueError on invalid phone numbers.
    """
    if not raw_phone or not isinstance(raw_phone, str):
        raise ValueError("Phone number is required.")

    cleaned = re.sub(r"[\s\-\(\)\.]", "", raw_phone.strip())

    if not cleaned:
        raise ValueError("Phone number cannot be empty.")

    # Starts with '+' followed by 10 to 15 digits
    if cleaned.startswith("+"):
        digits = cleaned[1:]
        if not digits.isdigit() or len(digits) < 10 or len(digits) > 15:
            raise ValueError("International phone number must contain 10 to 15 digits after '+'.")
        return cleaned

    # Starts with '0' followed by 10 digits (e.g. 09876543210)
    if cleaned.startswith("0") and len(cleaned) == 11 and cleaned.isdigit():
        return f"+91{cleaned[1:]}"

    # 10 digits without country code (default to +91)
    if len(cleaned) == 10 and cleaned.isdigit():
        return f"+91{cleaned}"

    # 12 digits starting with 91 (e.g. 919876543210)
    if len(cleaned) == 12 and cleaned.startswith("91") and cleaned.isdigit():
        return f"+{cleaned}"

    raise ValueError("Invalid phone number format. Please provide a valid 10-digit mobile number or full international format (e.g. +919876543210).")


def mask_phone_number(phone: str) -> str:
    """
    Masks phone number for privacy in public API responses.
    Example: '+919876543210' -> '+91 ******3210'
    """
    if not phone or len(phone) < 6:
        return "****"
    prefix = phone[:3] if phone.startswith("+") else ""
    last_four = phone[-4:]
    return f"{prefix} ******{last_four}"
