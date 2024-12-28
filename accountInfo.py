import requests
import re

class AccountInfo:
    @staticmethod
    def get_ccid(message: str) -> str:
        """
        Mengambil ccid dari halaman web berdasarkan message yang diberikan.
        """
        base_url = "https://account.aq.com/CharPage"
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
        """
        Mengambil data badge berdasarkan ccid.
        """
        badges_url = f"https://account.aq.com/CharPage/Badges?ccid={ccid}"
        
        try:
            response = requests.get(badges_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error retrieving badges: {e}")
            return None
