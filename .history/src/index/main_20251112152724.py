from fastapi import Depends
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy

logger = logging.getLogger('uvicorn.error')

@ui.page('/home')
async def home_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('Mindfuly').classes('text-2xl font-bold mb-4')
        ui.button('Click Me', on_click=lambda: ui.notify('Button Clicked!')).classes('mt-4')

@ui.page("")

@ui.page('/')
async def root_page(): ui.navigate.to('/home') # Redirect root to home page