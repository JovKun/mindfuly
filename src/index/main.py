from fastapi import Depends, HTTPException
from nicegui import ui
from pydantic import parse_obj_as
from contextlib import contextmanager
import logging
import copy
import httpx
import asyncio

from src.mindfuly.routes.users import create_user
from user_service_v2.models.user import UserSchema, get_user_repository_v2, UserRepositoryV2

logger = logging.getLogger('uvicorn.error')

@ui.page('/home')
async def home_page():
    # Custom CSS for gradients and animations
    ui.add_head_html('''
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .card-hover {
                transition: all 0.3s ease;
            }
            .card-hover:hover {
                transform: translateY(-4px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            }
        </style>
    ''')
    
    with ui.column().classes('w-full min-h-screen gradient-bg items-center justify-center p-8'):
        # Hero Section
        with ui.column().classes('max-w-4xl mx-auto items-center text-center'):
            ui.icon('psychology', size='80px').classes('text-white mb-4')
            ui.label('Mindfuly').classes('text-6xl font-bold text-white mb-3')
            ui.label('Your Personal Study Focus Companion').classes('text-2xl text-white opacity-90 mb-12')
            
            # Features showcase
            with ui.row().classes('w-full gap-6 mb-12 flex-wrap justify-center'):
                for icon, title, desc in [
                    ('mood', 'Track Mood', 'Monitor your daily emotions'),
                    ('music_note', 'Focus Music', 'Study playlists & sessions'),
                    ('analytics', 'Insights', 'Understand your patterns'),
                ]:
                    with ui.card().classes('bg-white bg-opacity-20 backdrop-blur p-6 card-hover'):
                        ui.icon(icon, size='48px').classes('text-white mb-3')
                        ui.label(title).classes('text-xl font-bold text-white mb-2')
                        ui.label(desc).classes('text-white opacity-80')
            
            # CTA Buttons
            with ui.row().classes('gap-6 mt-8'):
                ui.button('Login', 
                    on_click=lambda: ui.navigate.to('/login'),
                    icon='login'
                ).classes('px-12 py-4 text-lg bg-white text-purple-700 hover:bg-gray-100 shadow-lg')
                ui.button('Sign Up', 
                    on_click=lambda: ui.navigate.to('/signup'),
                    icon='person_add'
                ).classes('px-12 py-4 text-lg bg-purple-900 text-white hover:bg-purple-800 shadow-lg')


@ui.page("/login")
async def login_page(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    ui.add_head_html('''
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    ''')
    
    with ui.column().classes('w-full min-h-screen gradient-bg items-center justify-center p-8'):
        with ui.card().classes('max-w-md w-full p-8 shadow-2xl'):
            # Header
            with ui.column().classes('items-center mb-8'):
                ui.icon('psychology', size='60px').classes('text-purple-600 mb-3')
                ui.label('Welcome Back').classes('text-3xl font-bold text-gray-800 mb-2')
                ui.label('Log in to continue your focus journey').classes('text-gray-600')
            
            # Form
            with ui.column().classes('w-full gap-4'):
                username_input = ui.input('Username', placeholder='Enter your username').props('outlined').classes('w-full')
                username_input.props('prepend-icon=person')
                
                password_input = ui.input('Password', password=True, placeholder='Enter your password').props('outlined').classes('w-full')
                password_input.props('prepend-icon=lock')

                error_label = ui.label().classes('text-red-500 text-sm')
            error_label.visible = False

            async def handle_login():
                user = await user_repo.get_by_name(username_input.value)

                if user == None:
                    ui.notify('User not found! Please check your username.', color='negative', position='top')
                    return

                if await user_repo.verify_password(user, password_input.value):
                    ui.notify(f'Welcome back, {username_input.value}! 🎉', color='positive', position='top')
                    ui.navigate.to(f"/users/{username_input.value}/home")
                else:
                    error_label.text = "❌ Invalid password. Please try again."
                    error_label.visible = True
                    password_input.value = ""
                    password_input.focus()

                ui.button('Login', 
                    on_click=handle_login,
                    icon='login'
                ).classes('w-full py-3 bg-purple-600 text-white hover:bg-purple-700 text-lg font-semibold')

                password_input.on('keydown.enter', handle_login)
                
                # Divider and signup link
                ui.separator().classes('my-4')
                with ui.row().classes('w-full justify-center gap-2'):
                    ui.label("Don't have an account?").classes('text-gray-600')
                    ui.link('Sign up here', '/signup').classes('text-purple-600 font-semibold no-underline hover:text-purple-800')
                
                # Back button
                ui.button('← Back to Home', 
                    on_click=lambda: ui.navigate.to('/home'),
                    icon='home'
                ).classes('w-full mt-4 bg-gray-100 text-gray-700 hover:bg-gray-200').props('flat')


@ui.page("/signup")
async def signup_page(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    ui.add_head_html('''
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    ''')
    
    with ui.column().classes('w-full min-h-screen gradient-bg items-center justify-center p-8'):
        with ui.card().classes('max-w-md w-full p-8 shadow-2xl'):
            # Header
            with ui.column().classes('items-center mb-8'):
                ui.icon('person_add', size='60px').classes('text-purple-600 mb-3')
                ui.label('Create Account').classes('text-3xl font-bold text-gray-800 mb-2')
                ui.label('Start your mindful study journey today').classes('text-gray-600')
            
            # Form
            with ui.column().classes('w-full gap-4'):
                username_input = ui.input('Username', placeholder='Choose a username').props('outlined').classes('w-full')
                username_input.props('prepend-icon=person')
                
                email_input = ui.input('Email', placeholder='your.email@example.com').props('outlined').classes('w-full')
                email_input.props('prepend-icon=email')
                
                password_input = ui.input('Password', password=True, placeholder='Create a secure password').props('outlined').classes('w-full')
                password_input.props('prepend-icon=lock')
            
            async def handle_signup():
                if not username_input.value or not email_input.value or not password_input.value:
                    ui.notify('⚠️ Please fill in all fields.', color='warning', position='top')
                    return

                result = await user_repo.create(username_input.value, email_input.value, password_input.value, tier=1)
                if not result:
                    ui.notify('❌ User already exists. Please try a different username or email.', color='negative', position='top')
                    return
                    
                ui.notify('✅ Signup Successful! Welcome to Mindfuly!', color='positive', position='top')
                ui.navigate.to('/login')

                ui.button('Create Account', 
                    on_click=handle_signup,
                    icon='check_circle'
                ).classes('w-full py-3 bg-purple-600 text-white hover:bg-purple-700 text-lg font-semibold')
                
                # Divider and login link
                ui.separator().classes('my-4')
                with ui.row().classes('w-full justify-center gap-2'):
                    ui.label("Already have an account?").classes('text-gray-600')
                    ui.link('Log in here', '/login').classes('text-purple-600 font-semibold no-underline hover:text-purple-800')
                
                # Back button
                ui.button('← Back to Home', 
                    on_click=lambda: ui.navigate.to('/home'),
                    icon='home'
                ).classes('w-full mt-4 bg-gray-100 text-gray-700 hover:bg-gray-200').props('flat') 
    


@ui.page('/')
async def root_page(): ui.navigate.to('/home') # Redirect root to home page

@ui.page("/admin/users/")
async def user_overview_page(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    ui.add_head_html('''
        <style>
            body { background: linear-gradient(to bottom, #f8f9fa, #e9ecef); }
            .gradient-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    ''')
    
    # Admin Header
    with ui.header().classes('gradient-purple shadow-lg'):
        with ui.row().classes('w-full max-w-7xl mx-auto justify-between items-center px-6 py-4'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('admin_panel_settings', size='36px').classes('text-white')
                ui.label('Admin Dashboard').classes('text-2xl font-bold text-white')
            ui.button('← Back', on_click=lambda: ui.navigate.to('/home'), icon='home').classes('text-white').props('flat')
    
    with ui.column().classes('w-full max-w-7xl mx-auto p-6 gap-6'):
        # Page Header
        with ui.row().classes('w-full justify-between items-center mb-4'):
            with ui.column():
                ui.label('User Management').classes('text-3xl font-bold text-gray-800')
                ui.label('Manage all registered users').classes('text-gray-600')
            ui.button('Refresh', on_click=lambda: refresh_users(), icon='refresh').classes('bg-purple-600 text-white hover:bg-purple-700 px-6 py-2')
        
        users = await user_repo.get_all()
        
        # Stats Card
        with ui.card().classes('w-full p-6 bg-gradient-to-r from-purple-500 to-purple-700 shadow-xl'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('group', size='48px').classes('text-white')
                with ui.column():
                    ui.label(f'{len(users)}').classes('text-4xl font-bold text-white')
                    ui.label('Total Registered Users').classes('text-lg text-white opacity-90')

        # Users List
        ui.label('All Users').classes('text-xl font-bold text-gray-800 mt-4')
        with ui.column().classes('w-full gap-4 mt-4'):
            for user in users:
                with ui.card().classes('w-full p-6 hover:shadow-lg transition-shadow'):
                    with ui.row().classes('w-full justify-between items-center'):
                        # User Avatar and Info
                        with ui.row().classes('items-center gap-4 flex-1'):
                            ui.icon('account_circle', size='48px').classes('text-purple-600')
                            with ui.column().classes('gap-1'):
                                ui.label(user.name).classes('text-xl font-bold text-gray-800')
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('email', size='16px').classes('text-gray-500')
                                    ui.label(user.email).classes('text-gray-600')
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('badge', size='16px').classes('text-gray-500')
                                    ui.label(f'ID: {user.id}').classes('text-gray-500 text-sm')
                        
                        # Actions
                        with ui.row().classes('gap-2'):
                            ui.button(icon='visibility', on_click=lambda u=user: ui.notify(f'Viewing {u.name}')).props('flat round').classes('text-purple-600')
                            ui.button(icon='edit', on_click=lambda u=user: ui.notify(f'Editing {u.name}')).props('flat round').classes('text-blue-600')

    
                        
    async def refresh_users():
        ui.navigate.reload()


@ui.page("/users/{username}/home")
async def user_home_screen(username: str, user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    
    user = await user_repo.get_by_name(username)
    if not user: 
        return ui.label("User not found.")
    
    # Custom CSS for enhanced styling
    ui.add_head_html('''
        <style>
            body { background: linear-gradient(to bottom, #f8f9fa, #e9ecef); }
            .glass-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            .gradient-purple {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .gradient-blue {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }
        </style>
    ''')
    
    # Modern Navbar
    with ui.header().classes('gradient-purple shadow-lg'):
        with ui.row().classes('w-full max-w-7xl mx-auto justify-between items-center px-6 py-4'):
            with ui.row().classes('items-center gap-3'):
                ui.icon('psychology', size='36px').classes('text-white')
                ui.label('Mindfuly').classes('text-2xl font-bold text-white')
            
            with ui.row().classes("gap-6 items-center"):
                ui.link("📊 Analytics", "#").classes("text-white text-base no-underline hover:text-purple-200 transition-colors")
                ui.link("⚙️ Settings", "#").classes("text-white text-base no-underline hover:text-purple-200 transition-colors")
                with ui.button(icon='logout', on_click=lambda: ui.navigate.to('/home')).props('flat round').classes('text-white'):
                    ui.tooltip('Logout')

    # Welcome Section
    with ui.column().classes('w-full items-center mt-8 mb-6'):
        ui.label(f"Welcome back, {username}! 👋").classes('text-4xl font-bold text-gray-800 text-center')
        ui.label("Track your mood and stay focused").classes('text-lg text-gray-600 text-center mt-2')

    # Main Content Grid
    with ui.column().classes("w-full max-w-7xl mx-auto px-6 gap-6"):
        
        # Top Row - Mood & Music & Summary
        with ui.row().classes("w-full gap-6 flex-wrap"):
            
            # Mood Log Card
            with ui.card().classes("flex-1 min-w-[300px] glass-card p-8 shadow-xl"):
                ui.icon('mood', size='32px').classes('text-purple-600 mb-2')
                ui.label("Today's Mood").classes("text-2xl font-bold mb-2 text-gray-800")
                ui.label("How are you feeling right now?").classes("text-sm text-gray-600 mb-6")
                
                # State variables for mood tracking
                selected_mood = {"value": 3}
                
                # Mood Emojis
                with ui.row().classes("justify-around mb-6 w-full"):
                    for emoji, value in [("😞", 1), ("🙁", 2), ("😐", 3), ("🙂", 4), ("😄", 5)]:
                        mood_btn = ui.label(emoji).classes('text-5xl cursor-pointer hover:scale-110 transition-transform opacity-60 hover:opacity-100')
                        mood_btn.on('click', lambda v=value: selected_mood.update({"value": v}))
                
                # Energy Slider
                ui.label("Energy Level").classes("text-sm font-semibold text-gray-700 mb-2")
                with ui.row().classes("items-center gap-3 w-full"):
                    ui.label("Low").classes("text-xs text-gray-500")
                    slider = ui.slider(min=1, max=10, value=7).classes("flex-1")
                    ui.label("High").classes("text-xs text-gray-500")
                
                # Notes
                ui.label("What's on your mind?").classes("text-sm font-semibold text-gray-700 mb-2 mt-4")
                textarea = ui.textarea(placeholder="Share your thoughts...").props("outlined autogrow").classes("w-full")
                
                async def save_mood():
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                "http://localhost:8200/mood/log",
                                json={
                                    "username": username,
                                    "mood_value": selected_mood["value"],
                                    "energy_level": int(slider.value),
                                    "notes": textarea.value,
                                    "weather": "Sunny"  # Can be fetched from weather API
                                }
                            )
                            if response.status_code == 200:
                                ui.notify("✅ Mood logged successfully!", color='positive')
                                textarea.value = ""
                            else:
                                ui.notify("❌ Failed to save mood log", color='negative')
                    except Exception as e:
                        ui.notify(f"❌ Error: {str(e)}", color='negative')
                
                ui.button("Save Mood Log", 
                    on_click=save_mood,
                    icon='check_circle'
                ).classes("w-full mt-4 bg-purple-600 text-white hover:bg-purple-700 py-3 font-semibold")

            # Music Sessions Card
            with ui.card().classes("flex-1 min-w-[300px] glass-card p-8 shadow-xl"):
                ui.icon('music_note', size='32px').classes('text-blue-600 mb-2')
                ui.label("Focus Music").classes("text-2xl font-bold mb-2 text-gray-800")
                ui.label("Stay concentrated with curated playlists").classes("text-sm text-gray-600 mb-6")
                
                # Spotify Playlists
                playlists_container = ui.column().classes("w-full mb-4")
                
                async def load_playlists():
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get("http://localhost:8200/spotify/playlists/focus")
                            if response.status_code == 200:
                                data = response.json()
                                playlists = data.get('playlists', [])
                                
                                with playlists_container:
                                    playlists_container.clear()
                                    ui.label("Available Playlists").classes("text-sm font-semibold text-gray-700 mb-2")
                                    
                                    for playlist in playlists[:3]:
                                        with ui.card().classes("p-4 hover:shadow-lg transition-all cursor-pointer bg-gradient-to-r from-blue-50 to-cyan-50"):
                                            with ui.row().classes("items-center gap-3 w-full"):
                                                ui.icon('queue_music', size='32px').classes('text-blue-600')
                                                with ui.column().classes("flex-1"):
                                                    ui.label(playlist['name']).classes("font-bold text-gray-800")
                                                    ui.label(playlist['description']).classes("text-xs text-gray-600")
                    except Exception as e:
                        with playlists_container:
                            ui.label("Unable to load playlists").classes("text-sm text-red-500")
                
                # Load playlists on page load
                ui.timer(0.1, load_playlists, once=True)
                
                # Music Player Visual
                with ui.column().classes("items-center w-full mb-6"):
                    with ui.card().classes("gradient-blue p-8 w-full items-center"):
                        ui.icon('album', size='80px').classes('text-white mb-3')
                        ui.label("Deep Focus").classes("text-xl font-bold text-white mb-2")
                        ui.label("Ambient Study Mix").classes("text-sm text-white opacity-90 mb-4")
                        
                        # Playback controls
                        async def log_session(session_type: str, duration: float):
                            try:
                                async with httpx.AsyncClient() as client:
                                    response = await client.post(
                                        "http://localhost:8200/spotify/session/log",
                                        json={
                                            "username": username,
                                            "track_name": "Deep Focus",
                                            "artist_name": "Study Beats",
                                            "duration_minutes": duration,
                                            "session_type": session_type
                                        }
                                    )
                                    if response.status_code == 200:
                                        ui.notify(f"✅ {session_type} session logged!", color='positive')
                            except Exception as e:
                                pass
                        
                        with ui.row().classes("gap-4 items-center"):
                            ui.button(icon='skip_previous').props('flat round').classes('text-white')
                            ui.button(icon='play_arrow', on_click=lambda: ui.notify("▶️ Playing...")).props('fab').classes('bg-white text-blue-600')
                            ui.button(icon='skip_next').props('flat round').classes('text-white')
                
                # Spotify Connect Button
                async def connect_spotify():
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get("http://localhost:8200/spotify/auth")
                            if response.status_code == 200:
                                data = response.json()
                                ui.notify("🎵 Opening Spotify authorization...", color='info')
                                ui.open(data['auth_url'], new_tab=True)
                            else:
                                ui.notify("❌ Spotify not configured", color='warning')
                    except Exception as e:
                        ui.notify("❌ Connection failed", color='negative')
                
                ui.button("🎵 Connect Spotify Account", 
                    on_click=connect_spotify,
                    icon='link'
                ).classes("w-full mb-4 bg-green-600 text-white hover:bg-green-700 py-2")
                
                # Quick Sessions
                ui.label("Quick Sessions").classes("text-sm font-semibold text-gray-700 mb-3")
                with ui.column().classes("gap-2 w-full"):
                    ui.button("🧘 1-Min Mindful Break", 
                        on_click=lambda: asyncio.create_task(log_session("mindful", 1))
                    ).classes("w-full bg-blue-50 text-blue-700 hover:bg-blue-100").props('flat')
                    ui.button("😌 3-Min Calm Down", 
                        on_click=lambda: asyncio.create_task(log_session("calm", 3))
                    ).classes("w-full bg-blue-50 text-blue-700 hover:bg-blue-100").props('flat')
                    ui.button("⚡ 5-Min Energy Boost", 
                        on_click=lambda: asyncio.create_task(log_session("energy", 5))
                    ).classes("w-full bg-blue-50 text-blue-700 hover:bg-blue-100").props('flat')

            # Daily Summary Card  
            with ui.card().classes("flex-1 min-w-[300px] glass-card p-8 shadow-xl"):
                ui.icon('wb_sunny', size='32px').classes('text-orange-500 mb-2')
                ui.label("Daily Summary").classes("text-2xl font-bold mb-2 text-gray-800")
                ui.label("Your wellness snapshot").classes("text-sm text-gray-600 mb-6")
                
                # Weather
                with ui.column().classes("items-center mb-6 bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6"):
                    ui.label("☀️").classes("text-6xl mb-2")
                    ui.label("Partly Cloudy, 72°F").classes("text-lg font-semibold text-gray-700")
                    ui.label("Perfect study weather!").classes("text-sm text-gray-600")
                
                # Stats
                with ui.column().classes("gap-3 w-full"):
                    with ui.row().classes("items-center gap-3 bg-green-50 rounded-lg p-3"):
                        ui.icon('trending_up', size='24px').classes('text-green-600')
                        with ui.column().classes("gap-0"):
                            ui.label("Study Streak").classes("text-xs text-gray-600")
                            ui.label("7 days 🔥").classes("text-base font-bold text-gray-800")
                    
                    with ui.row().classes("items-center gap-3 bg-purple-50 rounded-lg p-3"):
                        ui.icon('timer', size='24px').classes('text-purple-600')
                        with ui.column().classes("gap-0"):
                            ui.label("Today's Focus").classes("text-xs text-gray-600")
                            ui.label("2h 45m ⏱️").classes("text-base font-bold text-gray-800")
                
                # Daily Tip
                with ui.column().classes("bg-yellow-50 rounded-xl border-l-4 border-yellow-400 p-4 mt-4"):
                    ui.label("💡 Daily Tip").classes("font-bold text-gray-800 mb-2")
                    ui.label("Studies show you're most productive on Thursdays. Keep up the momentum!").classes("text-sm text-gray-700")



    


                 