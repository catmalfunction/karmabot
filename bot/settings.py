import os
import re

from dotenv import load_dotenv
from slackclient import SlackClient

dotenv_path = ".env"
load_dotenv(dotenv_path)

# Environment variables
KARMABOT_ID = os.environ.get("SLACK_KARMA_BOTUSER")
KARMABOT_NAME = os.environ.get("SLACK_KARMA_BOTNAME")
SLACK_TOKEN = os.environ.get("SLACK_KARMA_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
SLACK_INVITE_TOKEN = os.environ.get("SLACK_KARMA_INVITE_USER_TOKEN")

# Slack
GENERAL_CHANNEL = os.environ.get("GENERAL_CHANNEL")
ADMINS = ("UHAFKUACT")
SLACK_ID_FORMAT = re.compile(r"^<@[^>]+>$")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Karma
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION = re.compile(r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)")
MAX_POINTS = 5
