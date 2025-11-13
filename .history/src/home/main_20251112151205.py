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
        ui.label('Welcome to the Home Page').classes('text-2xl font-bold')
        ui.button('Click Me', on_click=lambda: ui.notify('Button Clicked!')).classes('mt-4')

@ui.page('/')
async def root_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('This is the Root Page').classes('text-2xl font-bold')
        ui.button('Go to Home', on_click=lambda: ui.open('/home')).classes('mt-4')