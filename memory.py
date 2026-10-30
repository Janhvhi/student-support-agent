import json
import re
from pathlib import Path


# --------------------------------------------------
# MEMORY CONFIGURATION
# --------------------------------------------------

MEMORY_FILE = Path(__file__).resolve().parent / "data" / "memory.json"

MAX_PREFERENCE_LENGTH = 200
MAX_PREFERENCES = 50


# --------------------------------------------------
# PRIVACY FILTER
# --------------------------------------------------

BLOCKED_TERMS = [
    "password",
    "otp",
    "one-time password",
    "verification code",
    "passcode",
    "medical",
    "diagnosis",
    "bank account",
    "credit card",
    "debit card",
    "social security",
    "aadhaar",
    "pan number",
    "phone number",
    "email address",
    "home address",
    "student id",
    "fee status",
    "scholarship status",
    "date of birth",
]


def is_sensitive(preference):
    """Reject common sensitive information and student identifiers."""

    text = preference.lower()

    # Check blocked words and phrases.
    for term in BLOCKED_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            return True

    # Block student record IDs such as STU001.
    if re.search(r"\bSTU\d+\b", preference, re.IGNORECASE):
        return True

    # Block email addresses.
    if re.search(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        preference,
        re.IGNORECASE,
    ):
        return True

    # Block common phone-number patterns.
    if re.search(r"(?<!\w)(?:\+?\d[\d\s().-]{8,}\d)(?!\w)", preference):
        return True

    return False


# --------------------------------------------------
# LOAD MEMORY
# --------------------------------------------------

def load_memory():
    """Load saved preferences from local JSON storage."""

    try:
        if not MEMORY_FILE.exists():
            return []

        data = json.loads(
            MEMORY_FILE.read_text(encoding="utf-8")
        )

        if not isinstance(data, list):
            return []

        # Return only valid, non-empty strings.
        return [
            item.strip()
            for item in data
            if isinstance(item, str)
            and item.strip()
            and len(item) <= MAX_PREFERENCE_LENGTH
            and not is_sensitive(item)
        ]

    except (OSError, json.JSONDecodeError):
        return []


# --------------------------------------------------
# SAVE PREFERENCE
# --------------------------------------------------

def save_preference(preference):
    """Save a non-sensitive preference across app sessions."""

    if not isinstance(preference, str):
        return "Please enter a valid text preference."

    preference = preference.strip()

    if not preference:
        return "Please provide a preference to remember."

    if len(preference) > MAX_PREFERENCE_LENGTH:
        return (
            f"Please keep the preference under "
            f"{MAX_PREFERENCE_LENGTH} characters."
        )

    if is_sensitive(preference):
        return "This information may be sensitive and was not saved."

    preferences = load_memory()

    # Avoid duplicates regardless of letter case.
    if any(item.casefold() == preference.casefold() for item in preferences):
        return "This preference is already saved."

    if len(preferences) >= MAX_PREFERENCES:
        return "Memory is full. Clear an old preference before adding another."

    preferences.append(preference)

    try:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        MEMORY_FILE.write_text(
            json.dumps(preferences, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return "Preference saved for future sessions."

    except OSError:
        return "I couldn't save the preference to local memory."


# --------------------------------------------------
# CLEAR MEMORY
# --------------------------------------------------

def clear_memory():
    """Remove all saved preferences."""

    try:
        if MEMORY_FILE.exists():
            MEMORY_FILE.unlink()

        return "Saved preferences have been cleared."

    except OSError:
        return "I couldn't clear the saved preferences."