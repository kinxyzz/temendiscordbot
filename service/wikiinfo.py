import requests
import re
from dotenv import load_dotenv # type: ignore
import os
from bs4 import BeautifulSoup

load_dotenv()

def convert_to_discord_format(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    images = []

    for skills_div in soup.find_all('div', class_='skills'):
        skills_div.decompose()

    for li_tag in soup.find_all('li'):
        if li_tag.get_text(strip=True).startswith("Also see:"):
            nested_ul = li_tag.find('ul')
            if nested_ul:
                links = []
                for nested_li in nested_ul.find_all('li', recursive=False):
                    a_tag = nested_li.find('a')
                    if a_tag:
                        text = a_tag.get_text(strip=True)
                        href = a_tag.get('href')
                        links.append(f"[{text}]({os.environ.get('wikiurl')}{href})")
                li_tag.clear()
                li_tag.append(f"**Also see:**\n" + "\n".join(links))

    for strong_tag in soup.find_all('strong'):
        text = strong_tag.get_text(strip=True)
        strong_tag.replace_with(f"**{text}**")

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href and href != 'javascript:;':
            text = a_tag.get_text(strip=True)
            a_tag.replace_with(f"[{text}]({os.environ.get('wikiurl')}{href})")

    for img_tag in soup.find_all('img'):
        if img_tag.get('src'):
            images.append(img_tag['src'])  # Collect image URLs
            img_tag.replace_with(f"![]({img_tag['src']})")

    discord_content = soup.get_text("\n", strip=True)
    cleaned_content = clean_discord_output(discord_content)

    return {
        "discordEmbed": cleaned_content,
        "images": images
    }

def clean_discord_output(discord_content):
    discord_content = re.sub(r'\n-\s*\n', '\n', discord_content)
    discord_content = re.sub(r'\n{2,}', '\n', discord_content)
    discord_content = re.sub(r'(?m)^-\s*$', '', discord_content)
    discord_content = re.sub(r'(?m)^-\s*\[-', '- [', discord_content)
    discord_content = re.sub(r'\s*\.\s*$', '', discord_content)

    lines = discord_content.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() and not (line.strip() == '-' or line.strip() == '.' or (line.strip().startswith('-') and len(line.strip()) <= 2)):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def format_to_slug(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


# Ambil halaman dari URL dan konversi
def get_page_content_and_convert(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        page_content = soup.find(id='page-content')
        if page_content:
            return convert_to_discord_format(str(page_content))
    return None

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
    
    @staticmethod
    def get_detail_search(name):
        url = f"{os.environ.get('wikiurl')}/{format_to_slug(name)}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_content = soup.find(id='page-content')
                if page_content:
                    return get_page_content_and_convert(url)
            return None
            
        except requests.RequestException as e:
            print(f"Error saat melakukan request: {e}")
            return None

if __name__ == "__main__":
    query = "Icy Naval Commander"
    results = AQWWikiScraper.get_detail_search(query)
    print(results)
