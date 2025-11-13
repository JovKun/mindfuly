from fastapi import Depends
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy

logger = logging.getLogger('uvicorn.error')