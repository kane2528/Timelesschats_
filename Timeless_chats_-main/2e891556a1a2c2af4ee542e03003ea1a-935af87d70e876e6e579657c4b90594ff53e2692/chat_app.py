from uuid import uuid4
import pandas as pd
from nicegui import ui

messages = []

df = pd.read_csv("profanity_en.csv")
profanity_list = df['profanities'].tolist()

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
    for user_id, avatar, message_text in messages:
        ui.chat_message(avatar=avatar, text=message_text, sent=user_id == own_id)

@ui.page('/')
def index():
    global text

    def send():
        global messages
        filtered_message = profanity_filter.filter_text(text.value)
        messages.append((user, avatar, filtered_message))
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
