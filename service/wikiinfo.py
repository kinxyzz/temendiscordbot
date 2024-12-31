import requests
import re
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

class AQWWikiScraper:
    BASE_URL = f"{os.environ.get('wikiurl')}/search:main/fullname/"
    @staticmethod
    def get_list_search(query):
        url = f"{AQWWikiScraper.BASE_URL}{query}"
        try:
            response = requests.get(url)
            response.raise_for_status() 

            matches = re.findall(r'<div class="list-pages-item">(.*?)</div>', response.text, re.DOTALL)
            results = []
            
            for match in matches:
                links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', match)
                for href, text in links:
                    results.append({
                        'text': text.strip(),
                        'href': href
                    })
            return results
        except requests.RequestException as e:
            print(f"Error saat melakukan request: {e}")
            return []
        except Exception as e:
            print(f"Error saat memproses data: {e}")
            return []

