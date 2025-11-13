from fastapi import Depends
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy

logger = logging.getLogger('uvicorn.error')


@ui.page('/home')
async def home_page():
    with ui.column().classes('mx-auto'):
        with ui.row().classes('w-full justify-center items-center px-4 mb-4'):
            ui.label('Mindfuly').classes('text-2xl font-bold')

        with ui.row().classes('w-full justify-between items-center mt-32 gap-4'):
            ui.button('Login', on_click=lambda: ui.navigate.to('/login')).classes('bg-blue-500')
            ui.button('Signup', on_click=lambda: ui.navigate.to('/signup')).classes('bg-blue-500')


@ui.page("/login")
async def login_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('Login Page').classes('text-2xl font-bold mb-4')
        username_input = ui.input('Username').classes('mb-2')
        password_input = ui.input('Password', password=True).classes('mb-4')
        ui.button('Login', on_click=lambda: ui.notify('Login Clicked! TODO: Implement login functionality')).classes('mt-4')

        # """ Redirect to the user's main page """
        #
        # ui.button('Login', on_click=handle_login).classes('mt-4')
        #
        # async def handle_login():
        #   if authenticate_user(username_input.value, password_input.value):
        #       ui.navigate.to('/{username}/overview')


@ui.page("/signup")
async def signup_page():
    with ui.column().classes('mx-auto mt-32 w-80'):
        ui.label('Signup Page').classes('text-2xl font-bold mb-4')
        username_input = ui.input('Username').classes('mb-2')
        email_input = ui.input('Email').classes('mb-2')
        password_input = ui.input('Password').classes('mb-4') # password=False for visibility when signing up
        ui.button('Signup', on_click=lambda: ui.notify('Signup Clicked! TODO: Implement signup functionality')).classes('mt-4')

        # """ Create new user and redirect to login page """
        # 
        # ui.button('Signup', on_click=handle_signup).classes('mt-4') 
        # 
        # async def handle_signup():
        #   create_user(username_input.value, email_input.value, password_input.value)
        #   ui.navigate.to('/login')


@ui.page('/')
async def root_page(): ui.navigate.to('/home') # Redirect root to home page