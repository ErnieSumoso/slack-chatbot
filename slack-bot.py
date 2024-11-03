import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from slackeventsapi import SlackEventAdapter

# Reading the env file from the project
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Setting up the Flask application server running and the event adapter
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/chat', app
)

# Setting up the slack web client and our bot unique user ID
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

# Post verification required from the Slack API
@app.route("/", methods=['POST'])
def slack_post_verification():
    return request.json['challenge']

# Method to execute when any user types a message in the slack channels
@slack_event_adapter.on('message')
def message(payload):

    # Get the required data from the event (channel and user IDs, and text)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    # If the bot was not tagged or the message was sent but the same bot then stop processing
    bot_tag = f"<@{BOT_ID}>"
    if  bot_tag not in text or BOT_ID == user_id:
        return
    
    # Otherwise, check if the message has a question mark to echo the question
    if '?' in text:
        bot_answer = "Echoing question: " + text
        client.chat_postMessage(channel = channel_id, text = bot_answer)
    else:
        bot_answer = "That is not a question. Please ask me a question."
        client.chat_postMessage(channel = channel_id, text = bot_answer)

if __name__ == "__main__":
    app.run(debug=True)
