import scripts.user_interface
from collections import defaultdict
import re

import scripts.user_interface

import scripts.lib

def check_command_line_args(command_arguments: list[str]) -> bool:
    if '-h' in command_arguments or '--help' in command_arguments:
        scripts.user_interface.print_colored('Arguments:', 'white')
        scripts.user_interface.print_colored(['  -u <url>         The URL of the anime to download. ', 'required'], ['white', 'yellow'])
        scripts.user_interface.print_colored(['  -r <range>       The Range of Titles to download (e.g. s1e1-s1e5).', 'optional'], ['white', 'green'])
        scripts.user_interface.print_colored('  -h               Prints Help', 'white')
        return False
    
    if '-v' in command_arguments or '--version' in command_arguments:
        scripts.user_interface.print_colored(['Version: ', '7.0.1'], ['gray', 'white'])
        return False
    
    if not command_arguments or not '-u' in command_arguments or not len(command_arguments) >= 2:
        scripts.user_interface.print_colored(['Error: ', 'Please pass in an URL as command line argument.'], ['red', 'gray'])
        return False

    match = re.match(r"^https://aniworld\.to/anime/stream/[a-z0-9\-]+/?$", command_arguments[command_arguments.index('-u') + 1])
    
    if not match:
        scripts.user_interface.print_colored(['Error: ', 'The Url you entered is invalid.'], ['red', 'gray'])
        return False
    
    return True



def parse_range_string(anime_episode_data: dict[int, int], range_str):

    def error(msg):
        scripts.user_interface.print_colored(['Error: ', msg], ['red', 'gray'])
        raise ValueError(msg)

    def parse_token(token):
        import re
        match = re.match(r"s(\d+)e(\d+)", token.strip().lower())
        if not match:
            error(f"Invalid format: '{token}' (expected format like s1e5)")
        season = int(match.group(1))  # type: ignore
        episode = int(match.group(2))  # type: ignore

        if season not in anime_episode_data:
            error(f"Season s{season} does not exist.")
        episode_count = anime_episode_data[season]
        if episode < 1 or episode > episode_count:
            error(f"Episode e{episode} is out of range (1–{episode_count}) in s{season}")

        return season, episode

    # Initialize full structure with False (don't download)
    episode_data_detailled = {
        season: {ep: False for ep in range(1, count + 1)}
        for season, count in anime_episode_data.items()
    }

    if not range_str:
        # No range given: mark all episodes for download
        for season in episode_data_detailled:
            for ep in episode_data_detailled[season]:
                episode_data_detailled[season][ep] = True
        return episode_data_detailled

    for part in range_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                s1, e1 = parse_token(start)
                s2, e2 = parse_token(end)
            except ValueError:
                continue  # Error already reported

            if (s1, e1) > (s2, e2):
                error(f"Invalid range: {part} (start > end)")

            for season in range(s1, s2 + 1):
                ep_start = e1 if season == s1 else 1
                ep_end = e2 if season == s2 else anime_episode_data[season]
                for ep in range(ep_start, ep_end + 1):
                    episode_data_detailled[season][ep] = True
        else:
            try:
                season, episode = parse_token(part)
                episode_data_detailled[season][episode] = True
            except ValueError:
                continue

    return episode_data_detailled



def print_titles_in_columns(titles, available_flags, episode_data_detailled=None, season=None):
    num_columns = 3
    num_rows = (len(titles) + num_columns - 1) // num_columns

    columns = [[] for _ in range(num_columns)]
    for idx, (title, available) in enumerate(zip(titles, available_flags)):
        col = idx // num_rows
        row = idx % num_rows
        episode_number = idx + 1
        should_download = True

        if episode_data_detailled is not None and season is not None:
            should_download = episode_data_detailled.get(season, {}).get(episode_number, False)

        columns[col].append((idx, title, available, should_download))

    for col in columns:
        while len(col) < num_rows:
            col.append(None)

    for row in range(num_rows):
        texts = []
        colors = []
        for col in range(num_columns):
            item = columns[col][row]
            if item:
                idx, title, available, should_download = item

                if len(title) > 40:
                    title = title[:37] + '...'

                idx_str = str(idx + 1).zfill(2)
                title_padded = title.ljust(45)

                texts.append(f"    {idx_str}. ")
                if not should_download:
                    colors.append("gray")
                    texts.append(title_padded)
                    colors.append("red")
                else:
                    colors.append("gray")
                    texts.append(title_padded)
                    colors.append("green" if available else "yellow")
            else:
                texts.extend(["", ""])
                colors.extend(["gray", "green"])

        scripts.user_interface.print_colored(texts, colors)

def fetch_anime_data(anime_url, anime_episode_data, prefered_language):
    fetched_data = {}

    for season, episode_count in anime_episode_data.items():
        season_data = []
        for episode in range(1, episode_count + 1):
            episode_url = f"{anime_url}/staffel-{season}/episode-{episode}"

            # Try preferred language first
            episode_name = scripts.lib.get_episode_name_from_url(
                episode_url, 'de' if prefered_language == 'de' else 'en'
            )

            # Fallback to English if German not available
            if not episode_name and prefered_language == 'de':
                episode_name = scripts.lib.get_episode_name_from_url(
                    episode_url, 'en'
                )

            langs = scripts.lib.get_available_langs_from_url(episode_url)
            available = prefered_language in langs

            season_data.append({
                'episode': episode,
                'name': episode_name,
                'available': available
            })

        fetched_data[season] = season_data

    return fetched_data


def process_anime(anime_episode_data, episode_data_detailled=None, fetched_data=None):
    for season, episode_count in anime_episode_data.items():
        print()

        label = 'Films' if season == 0 else f'Season {season}'
        unit = 'films' if season == 0 else 'episodes'
        scripts.user_interface.print_colored([f'{label}: ', str(episode_count), f' {unit}'], ['gray', 'green', 'green'])

        episode_name_list = []
        availability_flags = []

        for data in fetched_data.get(season, []): # type: ignore
            episode_name_list.append(data['name'])
            availability_flags.append(data['available'])

        print_titles_in_columns(
            episode_name_list,
            availability_flags,
            episode_data_detailled=episode_data_detailled,
            season=season
        )
    print()




