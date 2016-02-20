from __future__ import print_function
import boto3
import json
import sys
import time
import telepot
import feedparser
from datetime import datetime, timedelta
from textwrap import dedent


try:
    from Queue import Queue
except ImportError:
    from queue import Queue

"""
$ python2.7 telegram webhook AWS lambda
"""

#TODO: Add messages for empty news sets


bot = telepot.Bot('BOT KEY')


###All the command and chat handlers
def start(chat_id):
	bot.sendMessage(chat_id, text='Hi! I am a Telegram Bot!!')

def unknown(chat_id):
	bot.sendMessage(chat_id, text="Sorry, I didn't understand that command.")

def help(chat_id):
	bot.sendMessage(chat_id, 
		text=dedent('''
			They call me a Telegram Bot. I can help you do stuff.
			'''
		))

def settings(chat_id):
	bot.sendMessage(chat_id, text="I cannot be configured via any settings yet. Check back soon!")

##Function to handle incoming messages and determine what the user is asking for
def handle(msg):
    flavor = telepot.flavor(msg)
    # normal message
    if flavor == 'normal':
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print('Normal Message:', content_type, chat_type, chat_id)
        command = msg['text']
        if command == '/start':
        	start(chat_id)
        elif command == '/help':
        	help(chat_id)
        elif command == '/settings':
        	settings(chat_id)
        else:
        	unknown(chat_id)

        return('Message sent')

        # Do your stuff according to `content_type` ...

    # inline query - need `/setinline`
    elif flavor == 'inline_query':
        query_id, from_id, query_string = telepot.glance2(msg, flavor=flavor)
        print('Inline Query:', query_id, from_id, query_string)

        # Compose your own answers
        articles = [{'type': 'article',
                        'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

        bot.answerInlineQuery(query_id, articles)

    # chosen inline result - need `/setinlinefeedback`
    elif flavor == 'chosen_inline_result':
        result_id, from_id, query_string = telepot.glance2(msg, flavor=flavor)
        print('Chosen Inline Result:', result_id, from_id, query_string)

        # Remember the chosen answer to do better next time

    else:
        raise telepot.BadFlavor(msg)

###AWS LAMBDA HANDLER, NOT FOR LOCAL DEV
# def my_handler(event, context):
#     print("Received event: " + json.dumps(event, indent=2))
#     handle(event['message'])
#     return('Hopefully it sent...')

##FOR LOCAL DEV
def my_handler(event):
    print("Received event: " + json.dumps(event, indent=2))
    handle(event)

bot.notifyOnMessage(my_handler)

print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)