import requests
import os
import difflib
from typing import Literal
from html import unescape




def list_available_hosters(url: str, prefered_data_lang_key: int = 1) -> list[str]: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1/episode-1 -> ["VOE", "Vidoza", "Streamtape", "SpeedFiles", "Doodstream"]
    response = requests.get(url)
    hoster_list = []
    html_content = response.text.split("\n")
    for l, line in enumerate(html_content):
        if "icon " in line and "Hoster " in line and (f'data-lang-key="{prefered_data_lang_key}"' in html_content[l - 3] or f'data-lang-key="{prefered_data_lang_key}"' in html_content[l - 6]):
            if line.split("Hoster ")[1].split('">')[0] not in hoster_list:
                hoster_list.append(line.split("Hoster ")[1].split('">')[0])
    return hoster_list


def get_redirect_url_from_hoster(url: str, hoster: str, data_lang_key: int = 1) -> str | None: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1/episode-1 -> https://aniworld.to/redirect/123456
    response = requests.get(url)
    data = response.text.split("\n")
    for l in range(len(data)):
        if 'href="/redirect/' in data[l]:
            if "Hoster " + hoster in data[l + 1]:
                if f'data-lang-key="{data_lang_key}"' in data[l - 2]:
                    return "https://aniworld.to" + data[l].split('href="')[1].split('"')[0]
                


def get_anime_name_from_url(url: str) -> str:
    response = requests.get(url)
    html_content_in_lines = response.text.split("\n")
    for line in html_content_in_lines:
        if '<meta name="description" content="' in line:
            return line.split(' von ')[1].split(' und ')[0]
    return ''


def get_url_name_from_url(url: str, detailled = False) -> str | None: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow -> the-eminence-in-shadow
    if not "staffel" in url and not "episode" in url:
        return url.split("/")[-1]
    elif "staffel" in url and not "episode" in url:
        return url.split("/")[-2]
    elif "staffel" in url and "episode" in url:
        if not detailled:
            return url.split("/")[-3]
        else:
            return url.split('/')[-3] + f'-S{url.split('staffel-')[1].split('/')[0]}-E{url.split('episode-')[1].split('/')[0]}'


def get_episode_count_from_url(url: str) -> int: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1 -> 20
    response = requests.get(url)
    episode_count = 0
    type = 'movie' if 'film' in url else 'normal'
    l = 0
    while True:
        l += 1
        if (f"Folge {l}" in response.text and type == 'normal') or (f"Film {l}" in response.text and type == 'movie'):
            episode_count += 1
        else:
            break
    return episode_count


def get_season_data_from_url(url: str) -> list[int]: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow -> 2
    response = requests.get(url)
    s = [] if not 'Alle Filme' in response.text else [0]
    idx = 0
    while True:
        idx += 1
        if f"Staffel {idx}" in response.text:
            s.append(idx)
        else:
            break
    return s

def get_season_id_from_url(url: str) -> int: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1 -> 1
    return int(url.split("staffel-")[1])

def get_episode_id_from_url(url: str) -> int: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1/episode-1 -> 1
    return int(url.split("episode-")[1])

def get_episode_name_from_url(url: str, lan: Literal['de', 'en']) -> str: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1/episode-1 -> Der verhasste Klassenkamerad
    response = requests.get(url)
    html_content_in_lines = response.text.split("\n")
    for line in html_content_in_lines:
        if lan == "de":
            if '<span class="episodeGermanTitle">' in line:
                i = line.split('<span class="episodeGermanTitle">')[1].split('</span>')[0].strip()
                return unescape(unescape(i))
        elif lan == "en":
            if '<small class="episodeEnglishTitle">' in line:
                i = line.split('<small class="episodeEnglishTitle">')[1].split('</small>')[0].strip()
                return unescape(unescape(i))  # Unescape HTML entities
    return ''

def get_available_langs_from_url(url: str) -> list[str]: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow/staffel-1/episode-1 -> ["german no subtitles", "japanese english subtitles", "japanese german subtitles"]
    response = requests.get(url)
    html_content_in_lines = response.text.split("\n")
    available_langs = []
    for line in html_content_in_lines:
        if 'class="changeLanguageBox"' in line:
            if 'data-lang-key="1"' in line:
                available_langs.append("de")
            if 'data-lang-key="2"' in line:
                available_langs.append("jp-en")
            if 'data-lang-key="3"' in line:
                available_langs.append("jp-de")
    return available_langs

def check_aniworld_connection() -> bool:
    try:
        requests.get('https://www.aniworld.to')
        return True
    except requests.exceptions.ConnectionError:
        return False

def search_anime(query, max_results=10):
    with open(os.path.join(os.getcwd(), 'anime_database.db'), "r", encoding="utf-8") as file:
        anime_list = [[line[:300].strip(), line[300:].strip()] for line in file]  # Extract title & URL pairs

    # Exact or partial match
    matches = [pair for pair in anime_list if query.lower() in pair[0].lower()]

    # Fuzzy search if no direct match
    if not matches:
        closest_titles = difflib.get_close_matches(query, [pair[0] for pair in anime_list], n=max_results, cutoff=0.5)
        matches = [pair for pair in anime_list if pair[0] in closest_titles]

    return matches[:max_results]  # Return top results

def extract_se_ep_name(name: str) -> str | None: #e.g. Solo.Leveling.S01E02.English.Subbed.720p.AAC.WebRip.x264-GSD_SS.mp4 -> s01e02
    for s in range(20):
        for e in range(200):
            if f's{str(s).zfill(2)}e{str(e + 1).zfill(2)}' in name.lower() or f's{s}e{e + 1}' in name.lower():
                return f's{str(s).zfill(2)}e{str(e + 1).zfill(2)}'



def get_simple_redirect(url: str) -> str:
    return requests.get(url, allow_redirects=True).url

if __name__ == "__main__":
    i = check_aniworld_connection()
    print(i)