from fastapi import Depends
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy

logger = logging.getLogger('uvicorn.error')

@ui.page('/home')
async def home_page():
    with ui.column().classes('mx-auto mt-32 w-80')