import time
import requests
from plyer import notification
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)
# Configuration
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")
LABEL = os.getenv("LABEL")
POLL_INTERVAL = 60  # in seconds

# GitHub API URL
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
LABEL_PARAM = requests.utils.quote(LABEL)  # URL encode the label

# Track already seen issue IDs
seen_issues = set()


def fetch_issues():
    url = f"{BASE_URL}?labels={LABEL_PARAM}&state=open"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []


def notify_new_issue(issue):
    title = issue["title"]
    url = issue["html_url"]
    message = f"✅ New 💎 Bounty: {title}\n{url}"

    try:
        # Slack notification
        response = client.chat_postMessage(channel="#all-test", text=message)
        print("Slack message sent:", response["ts"])
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")


def monitor():
    print(f"Watching for new issues labeled '{LABEL}' in {REPO_OWNER}/{REPO_NAME}...")
    while True:
        issues = fetch_issues()
        for issue in issues:
            if issue["id"] not in seen_issues:
                notify_new_issue(issue)
                seen_issues.add(issue["id"])
        time.sleep(POLL_INTERVAL)
        print(f"Checked for new issues at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    monitor()
