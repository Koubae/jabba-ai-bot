import json
import logging
import os
import sys
from typing import Any

from src.settings import Settings

GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

emitter_logger = logging.getLogger("emitter")
IS_CONTAINER = os.environ.get("IS_CONTAINER", "false").lower() == "true"


class DynamicExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)

        if hasattr(record, "extra"):

            try:
                extra_formatted = json.dumps(getattr(record, "extra"), indent=2)
            except (ValueError, AttributeError, json.JSONDecodeError):
                extras = [f"{k}={v!r}" for k, v in getattr(record, "extra").items()]
                extra_formatted = ""
                if extras:
                    extra_formatted = "{" + ", ".join(extras) + "}"

            if extra_formatted:
                message += f"\n{extra_formatted}"

        if hasattr(record, "tls_message"):
            tls_message = getattr(record, "tls_message")
            if tls_message:
                message += f"{YELLOW}\n📡\tTransmission start ...\t📡\n{RESET}"
                message += f"\t\t{GREEN}>> {tls_message} <<{RESET}"
                message += f"{YELLOW}\n📡\tTransmission end      \t📡\n{RESET}"

        return message


class OverwriteStreamHandler(logging.StreamHandler):
    def __init__(self, stream: Any | None = None) -> None:
        super().__init__(stream)
        self.counter = 0
        self.progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        stream = self.stream

        # Add a spinner character
        spinner = self.progress_chars[self.counter % len(self.progress_chars)]
        self.counter += 1
        msg = f"{spinner} {msg}"

        if IS_CONTAINER:
            # In Docker... the cool trick to re-write in the current line doesn't work sadly
            stream.write(msg + "\n")
        else:
            # Normal terminal mode with line overwriting
            # \r moves cursor to start of line
            # end='' prevents additional newline
            stream.write("\r" + msg)

            # \033[1A moves cursor up one line
            # \r moves cursor to start of line
            # stream.write("\033[1A\r" + msg)

        stream.flush()


def setup_logger(settings: Settings) -> None:
    level = logging.getLevelName(settings.log_level)
    logging.basicConfig(
        level=level,
    )

    _formatter = DynamicExtraFormatter(
        fmt=settings.log_format, datefmt="%Y-%m-%d %H:%M:%S"
    )
    for handler in logging.getLogger().handlers:
        handler.setFormatter(_formatter)

    _setup_emitter()


def _setup_emitter() -> None:
    handler = OverwriteStreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    emitter_logger.handlers.clear()
    emitter_logger.propagate = False
    emitter_logger.addHandler(handler)
