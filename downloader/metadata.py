from datetime import datetime
import pycountry
import requests
import os

from util import read_json_file
from scripts.lib import get_episode_name_from_url

DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
DESTINATION_DIR = read_json_file()['destination_directory']

def get_url_name(url: str, detailled = False) -> str | None:
    if not "staffel" in url and not "episode" in url:
        return url.split("/")[-1]
    else:
        raise ValueError('Please only pass in anime urls, no season or episode urls.')


def get_anime_name(url: str) -> str:
    response = requests.get(url)
    html_content_in_lines = response.text.split("\n")
    for line in html_content_in_lines:
        if '<meta name="description" content="' in line:
            return line.split(' von ')[1].split(' und ')[0]
    return ''


def get_anime_description(anime_url: str) -> str | None:
    response = requests.get(anime_url)
    anime_description = ''
    for line in response.text.split('\n'):
        if 'data-full-description="' in line:
            anime_description = line.split('data-full-description="')[1].split('">')[0]
            return anime_description


def get_anime_regisseurs(anime_url: str) -> list | None:
    response = requests.get(anime_url)
    anime_regisseurs = []
    for line in response.text.split('\n'):
        if 'itemprop="director"' in line:
            anime_regisseurs = line.split('itemprop="name">')[1:]
            break
    
    anime_regisseurs = [elem.split('</span>')[0] for elem in anime_regisseurs]
    return anime_regisseurs


def get_anime_actors(anime_url: str) -> list | None:
    response = requests.get(anime_url)
    anime_actors = []
    for line in response.text.split('\n'):
        if 'itemprop="actor"' in line:
            anime_actors = line.split('itemprop="name">')[1:]
            break
    
    anime_actors = [elem.split('</span>')[0] for elem in anime_actors]
    return anime_actors


def get_anime_producers(anime_url: str) -> list | None:
    response = requests.get(anime_url)
    anime_producers = []
    for line in response.text.split('\n'):
        if 'itemprop="creator"' in line:
            anime_producers = line.split('itemprop="name">')[1:]
            break
    
    anime_producers = [elem.split('</span>')[0] for elem in anime_producers]
    return anime_producers


def get_anime_countries(anime_url: str) -> list | None:
    response = requests.get(anime_url)
    anime_countries = []
    for line in response.text.split('\n'):
        if 'itemprop="countryOfOrigin"' in line:
            anime_countries = line.split('itemprop="name">')[1:]
            break
    
    anime_countries = [elem.split('</span>')[0] for elem in anime_countries]
    return anime_countries


def get_anime_genres(anime_url: str) -> list | None:
    response = requests.get(anime_url)
    anime_genres = []
    for line in response.text.split('\n'):
        if 'itemprop="genre">' in line:
            genre = line.split('itemprop="genre">')[1].split('</a>')[0]
            anime_genres.append(genre)

    BANNED_GENRES = ['Ger', 'GerSub', 'Eng', 'EngSub']
    
    anime_genres = [elem for elem in anime_genres if not elem in BANNED_GENRES]
    return anime_genres


def get_anime_rating(anime_url: str) -> int | None:
    response = requests.get(anime_url)
    anime_rating = 0
    for line in response.text.split('\n'):
        if 'span itemprop="ratingValue">' in line:
            try:
                anime_rating = int(line.split('span itemprop="ratingValue">')[1].split('</span>')[0])
                break
            except ValueError:
                return
    return anime_rating * 2


def get_anime_fsk(anime_url: str) -> int | None:
    response = requests.get(anime_url)
    anime_fsk = 0
    for line in response.text.split('\n'):
        if 'data-fsk=' in line:
            try:
                anime_fsk = int(line.split('data-fsk="')[1].split('"')[0])
                break
            except ValueError:
                return
    return anime_fsk


def get_anime_start_and_end_date(anime_url: str) -> list[int] | None:
    response = requests.get(anime_url)
    anime_start_date = 0
    anime_end_date = 0
    for line in response.text.split('\n'):
        if '<span itemprop="startDate">' in line:
            try:
                anime_start_date = int(line.split('<span itemprop="startDate">')[1].split('">')[1].split('</a>')[0])
                anime_end_date = int(line.split('<span itemprop="endDate">')[1].split('">')[1].split('</a>')[0])
                break
            except ValueError:
                return
    return [anime_start_date, anime_end_date]



def create_anime_nfo_file(description: str, title: str, url_name: str, rating: int, fsk: int, country: str, start_and_end_date: list[int], genres: list[str], producers: list[str], actors: list[str]):
    
    country_obj = pycountry.countries.get(name=country)
    country = country_obj.alpha_2 # type: ignore
    
    start_date, end_date = None, None
    if start_and_end_date:
        start_date, end_date = start_and_end_date
    
    if not genres: genres = []
    if not producers: producers = []
    
    
    nfo_file_blueprint: list[str] = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<tvshow>',
        f'  <plot>{description}</plot>' if description else '',
        f'  <outline>{description}</outline>' if description else '',
        '  <lockdata>true</lockdata>',
        '  <lockedfields>Runtime|Tags</lockedfields>',
        f'  <dateadded>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</dateadded>',
        f'  <title>{title}</title>' if title else '',
        f'  <rating>{rating}</rating>' if rating else '',
        f'  <mpaa>FSK {fsk}</mpaa>' if fsk else '',
        f'  <countrycode>{country}</countrycode>' if country else '',
        f'  <premiered>{start_date}-01-01</premiered>' if start_date else '',
        f'  <releasedate>{start_date}-01-01</releasedate>' if start_date else '',
        f'  <enddate>{end_date}-01-01</enddate>' if end_date else '',
    ] + \
    [ f'  <genre>{genre}</genre>' for genre in genres ] + \
    [ f'  <studio>{producer}</studio>' for producer in producers ] + \
    [
        '  <art>',
        f'    <poster>{os.path.join(DESTINATION_DIR, url_name, "cover.png").replace("/", "\\")}</poster>',
        f'    <fanart>{os.path.join(DESTINATION_DIR, url_name, "backdrop.png").replace("/", "\\")}</fanart>',
        '  </art>'
    ]
    nfo_file_blueprint += [
        line
        for actor in actors
        for line in [
            '  <actor>',
            f'    <name>{actor}</name>',
            '    <type>Actor</type>',
            '  </actor>'
        ]
    ]
    
    nfo_file_blueprint += [
        '  <season>-1</season>',
        '  <episode>-1</episode>',
        '</tvshow>'
    ]
    
    
    with open(os.path.join(DOWNLOAD_DIR, 'tvshow.nfo'), 'w', encoding='utf-8') as file:
        file.write('\n'.join(nfo_file_blueprint))






def fetch_metadata_and_create_anime_nfo_file(anime_url: str) -> None:    
    description = get_anime_description(anime_url)
    title = get_anime_name(anime_url)
    url_name = get_url_name(anime_url)
    rating = get_anime_rating(anime_url)
    fsk = get_anime_fsk(anime_url)
    country = get_anime_countries(anime_url)
    if country: country = country[0]
    start_and_end_date = get_anime_start_and_end_date(anime_url)
    genres = get_anime_genres(anime_url)
    producers = get_anime_producers(anime_url)
    actors = get_anime_actors(anime_url)
    
    create_anime_nfo_file(description, title, url_name, rating, fsk, country, start_and_end_date, genres, producers, actors) # type: ignore




def create_episode_nfo(url: str, prefered_language: str, file_name: str):
    title = get_episode_name_from_url(url, 'de' if prefered_language == 'de' else 'en')
    
    content = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<episodedetails>',
        f'  <title>{title}</title>',
        '</episodedetails>'
    ]

    with open(os.path.join(DOWNLOAD_DIR, f'{file_name}.nfo'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))