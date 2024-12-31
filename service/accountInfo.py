import requests
import re
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

class AccountInfo:
    @staticmethod
    def get_ccid(message: str) -> str:
        base_url = os.environ.get("charpageurl")
        query_url = f"{base_url}?id={message.replace(' ', '+')}"

        try:
            response = requests.get(query_url)
            response.raise_for_status()
            match = re.search(r'var\s+ccid\s*=\s*(\d+);', response.text)
            if match:
                return match.group(1)
            else:
                return None
        except requests.RequestException as e:
            print(f"Error retrieving ccid: {e}")
            return None

    @staticmethod
    def get_badges(ccid: str):
        badges_url = f"{os.environ.get('charpageurl')}/Badges?ccid={ccid}"
        
        try:
            response = requests.get(badges_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error retrieving badges: {e}")
            return None
