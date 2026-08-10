"""Consistent step logging for the RAG pipeline."""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Iterator


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def step(logger: logging.Logger, area: str, message: str, **fields: object) -> None:
    extras = " ".join(f"{key}={value!r}" for key, value in fields.items())
    if extras:
        logger.info("[STEP] %s | %s | %s", area, message, extras)
    else:
        logger.info("[STEP] %s | %s", area, message)


@contextmanager
def timed_step(
    logger: logging.Logger,
    area: str,
    message: str,
    **fields: object,
) -> Iterator[None]:
    step(logger, area, f"START {message}", **fields)
    started = time.perf_counter()
    try:
        yield
    except Exception as exc:
        step(
            logger,
            area,
            f"FAIL {message}",
            duration_s=round(time.perf_counter() - started, 3),
            error=str(exc),
        )
        raise
    else:
        step(
            logger,
            area,
            f"DONE {message}",
            duration_s=round(time.perf_counter() - started, 3),
            **fields,
        )
