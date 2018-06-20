import os
import time
import re
from pymongo import MongoClient
import json
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
murphybot_id = None

RTM_READ_DELAY = 1
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
pipeline = [{"$sample": { "size":1 }}]

def parse_bot_commands(slack_events):
   for event in slack_events:
     if event["type"] == "message" and not "subtype" in event:
       user_id, message = parse_direct_mention(event["text"])
       if user_id == murphybot_id:
         return message, event["channel"]
   return None, None

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    client = MongoClient()
    db = client.murphyslaws
    collection = db.laws
    law = collection.aggregate(pipeline)
    law = list(law)
    law = law[0][u'law']
    response = json.dumps(law)
    
    slack_client.api_call(
      "chat.postMessage",
      channel=channel,
      text=response)

if __name__=="__main__":
    if slack_client.rtm_connect(with_team_state=False):
      print("Murphybot connected and running!")
      murphybot_id = slack_client.api_call("auth.test")["user_id"]
      while True:
        command, channel = parse_bot_commands(slack_client.rtm_read())
        if command:
          handle_command(command, channel)
        time.sleep(RTM_READ_DELAY)
    else:
      print("Connection Failed. Exception traceback printed above.")
