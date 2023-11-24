from uuid import uuid4
import pandas as pd
from nicegui import ui
import sqlite3

# Create an SQLite database connection
conn = sqlite3.connect('chats.db')
cursor = conn.cursor()

# Create a table to store chat messages
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        avatar TEXT,
        message_text TEXT
    )
''')
conn.commit()

class ProfanityFilter:
    def __init__(self, profanity_list):
        self.profanity_list = profanity_list

    def is_profane(self, text):
        return any(phrase.lower() in text.lower() for phrase in self.profanity_list)

    def filter_text(self, text):
        for phrase in self.profanity_list:
            text = text.replace(phrase, '*' * len(phrase))
        return text

@ui.refreshable
def chat_messages(own_id):
    # Retrieve messages from the database
    cursor.execute('SELECT user_id, avatar, message_text FROM messages')
    stored_messages = cursor.fetchall()

    for user_id, avatar, message_text in stored_messages:
        ui.chat_message(avatar=avatar, text=message_text, sent=user_id == own_id)

@ui.page('/')
def index():
    global text

    def send():
        filtered_message = profanity_filter.filter_text(text.value)
        user_id = str(uuid4())
        
        # Save the message to the database
        cursor.execute('INSERT INTO messages (user_id, avatar, message_text) VALUES (?, ?, ?)', (user_id, avatar, filtered_message))
        conn.commit()

        chat_messages.refresh()
        text.value = ''  # Clear the input after sending the message

    user = str(uuid4())
    avatar = f'https://robohash.org/{user}?bgset=bg2'
    
    with ui.column().classes('w-full items-stretch'):
        chat_messages(user)

    with ui.footer().classes('bg-white'):
        with ui.row().classes('w-full items-center'):
            with ui.avatar():
                ui.image(avatar)
            text = ui.input(placeholder='message') \
                .props('rounded outlined').classes('flex-grow') \
                .on('keydown.enter', send)

    return text

# Instantiate ProfanityFilter
profanity_filter = ProfanityFilter(profanity_list)

ui.run()
