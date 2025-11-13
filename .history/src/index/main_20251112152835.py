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

@ui.page("/login")
async def login_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('Login Page').classes('text-2xl font-bold mb-4')
        ui.input('Username').classes('mb-2')
        ui.input('Password', password=True).classes('mb-4')
        ui.button('Login', on_click=lambda: ui.notify('Login Clicked! TODO: Implement login functionality')).classes('mt-4')

@ui.page("/signup")
async def signup_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('Signup Page').classes('text-2xl font-bold mb-4')
        ui.input('Username').classes('mb-2')
        ui.input('Email').classes('mb-2')
        ui.input('Password', password=True).classes('mb-4')
        ui.button('Signup', on_click=lambda: ui.notify('Signup Clicked!')).classes('mt-4')

@ui.page('/')
async def root_page(): ui.navigate.to('/home') # Redirect root to home page