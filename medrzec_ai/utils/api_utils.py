from fastapi import HTTPException

MAX_TEXT_LEN = 4096
MAX_TEXT_LINES = 32


def limit_input_len(text: str) -> None:
    if len(text) > MAX_TEXT_LEN:
        raise HTTPException(
            400, f"Input cannot be longer than {MAX_TEXT_LEN} characters."
        )

    if text.count("\n") >= MAX_TEXT_LINES:
        raise HTTPException(400, f"Input cannot have more than {MAX_TEXT_LINES} lines.")
