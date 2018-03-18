from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()
load_dotenv(find_dotenv(".env.local"))

TOGGL_TOKEN = os.getenv("TOGGL_TOKEN")
