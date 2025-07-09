import requests
import os

DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')

def download_anime_thumbnail(anime_url: str) -> str | None: # e.g. https://aniworld.to/anime/stream/the-eminence-in-shadow -> downloads/cover.png
    response = requests.get(anime_url)
    html_content_in_lines = response.text.split("\n")
    image_url = ""
    for line in html_content_in_lines:
        if "seriesCoverBox" in line:
            image_url = 'https://aniworld.to' + line.split('data-src="')[1].split('"')[0]
            response = requests.get(image_url)
            with open(os.path.join(DOWNLOAD_DIR, 'cover.png'), 'wb') as file:
                file.write(response.content)
            return image_url
    if not image_url:
        raise Exception("Image URL not found!")
    



def download_anime_backdrop(anime_url: str) -> str | None:
    response = requests.get(anime_url)
    html_content_in_lines = response.text.split("\n")
    image_url = ""
    for line in html_content_in_lines:
        if '<div class="backdrop" style="background-image: url(' in line:
            image_url = 'https://aniworld.to' + line.split('<div class="backdrop" style="background-image: url(')[1].split(')"></div>')[0]
            response = requests.get(image_url)
            with open(os.path.join(DOWNLOAD_DIR, 'backdrop.png'), 'wb') as file:
                file.write(response.content)
            return image_url
    


if __name__ == '__main__':
    download_anime_backdrop('https://aniworld.to/anime/stream/astarottes-toy')
    download_anime_thumbnail('https://aniworld.to/anime/stream/astarottes-toy')