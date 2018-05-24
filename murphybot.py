#!/usr/bin/env python
import os
import time
import re
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
murphybot_id = None

RTM_READ_DELAY = 1
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@|[WU].+?)(.*)"

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
