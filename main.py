import scripts.lib as lib
import os
import threading
import time
from sys import platform

import scripts.pre_download
import scripts.user_interface as ui
import scripts.lib
import util

import downloader.cover_images
import downloader.metadata
import downloader.start_download

#ui.print_colored('Starting AniWorld Downloader...', 'gray')

os.system('clear' if platform == 'darwin' else 'cls')

DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')


if not scripts.lib.check_aniworld_connection():
    ui.print_colored(['Error: ', 'Could not connect to AniWorld. Check your Network connection or try a VPN.'], ['red', 'gray'])
    exit()


if os.listdir(DOWNLOAD_DIR):
    i = input(f'{ui.COLOR_MAP.yellow}Warn: {ui.COLOR_MAP.gray}The download Directory is not empty. Do you want to delete its contents? {ui.COLOR_MAP.white}[{ui.COLOR_MAP.green}yes{ui.COLOR_MAP.white}, no]{ui.COLOR_MAP.green}')
    if i:
        if i not in ['yes', 'no']:
            ui.print_colored(['Error: ', 'Please pass in a valid argument (yes, no)'], ['red', 'gray'])
            exit()
        if i == 'no':
            exit()
    
    if not i or i == 'yes':
        for file in os.listdir(DOWNLOAD_DIR):
            os.remove(os.path.join(DOWNLOAD_DIR, file))
    

# Set important variables
anime_url = input(f'{ui.COLOR_MAP.gray}Enter the Anime URL: {ui.COLOR_MAP.green}')
if anime_url.endswith('/'): anime_url = anime_url[:-1]
print(ui.COLOR_MAP.reset, end='\r')
anime_name = scripts.lib.get_anime_name_from_url(anime_url)
anime_season_data = scripts.lib.get_season_data_from_url(anime_url)


# prefered language selection and database update
if not 'prefered_language' in list(util.read_json_file().keys()):
    db = util.read_json_file()
    db['prefered_language'] = 'de'
    util.write_json_file(db)

prefered_language = util.read_json_file()['prefered_language']
prefered_language_selected = input(f'{ui.COLOR_MAP.gray}Prefered Language {ui.COLOR_MAP.white}[{(ui.COLOR_MAP.green + "de" + ui.COLOR_MAP.white) if prefered_language == "de" else "de"}, {(ui.COLOR_MAP.green + "jp-en" + ui.COLOR_MAP.white) if prefered_language == "jp-en" else "jp-en"}, {(ui.COLOR_MAP.green + "jp-de" + ui.COLOR_MAP.white) if prefered_language == "jp-de" else "jp-de"}]{ui.COLOR_MAP.gray}: {ui.COLOR_MAP.green}')
print(ui.COLOR_MAP.reset, end='\r')

if prefered_language_selected:
    if prefered_language_selected not in ['de', 'jp-en', 'jp-de']:
        ui.print_colored(['Error: ', 'Please pass in a valid language (de, jp-en, jp-de)'], ['red', 'gray'])
        exit()
    if prefered_language != prefered_language_selected:
        prefered_language = prefered_language_selected
        db = util.read_json_file()
        db['prefered_language'] = prefered_language
        util.write_json_file(db)


# prefered language selection and database update
if not 'prefered_language_fallback' in list(util.read_json_file().keys()):
    db = util.read_json_file()
    db['prefered_language_fallback'] = 'jp-de' if prefered_language != 'jp-de' else 'jp-en'
    util.write_json_file(db)

prefered_language_fallback = util.read_json_file()['prefered_language_fallback']
prefered_language_fallback_options = ['de', 'jp-en', 'jp-de']
prefered_language_fallback_options.remove(prefered_language)
prefered_language_fallback_selected = input(f'{ui.COLOR_MAP.gray}Prefered Language for Fallback {ui.COLOR_MAP.white}[{ui.COLOR_MAP.green if prefered_language_fallback_options[0] == prefered_language_fallback else ui.COLOR_MAP.white}{prefered_language_fallback_options[0]}{ui.COLOR_MAP.white}, {ui.COLOR_MAP.green if prefered_language_fallback_options[1] == prefered_language_fallback else ui.COLOR_MAP.white}{prefered_language_fallback_options[1]}{ui.COLOR_MAP.white}]:{ui.COLOR_MAP.green} ')
print(ui.COLOR_MAP.reset, end='\r')

if prefered_language_fallback_selected:
    if prefered_language_fallback_selected not in prefered_language_fallback_options:
        ui.print_colored(['Error: ', f'Please pass in a valid language ({", ".join(prefered_language_fallback_options)})'], ['red', 'gray'])
        exit()
    if prefered_language_fallback != prefered_language_fallback_selected:
        prefered_language = prefered_language_fallback_selected
        db = util.read_json_file()
        db['prefered_language_fallback'] = prefered_language_fallback
        util.write_json_file(db)



ui.print_colored(['Name: ', anime_name], ['gray', 'green'])

anime_episode_data: dict = {}
for season in anime_season_data:
    if season == 0:
        episode_count = scripts.lib.get_episode_count_from_url(f'{anime_url}/filme') # type: ignore
    else:
        episode_count = scripts.lib.get_episode_count_from_url(f"{anime_url}/staffel-{season}") # type: ignore
    anime_episode_data[season] = episode_count

ui.print_colored(['Prefered Language: ', 'German, no subtitles' if prefered_language == 'de' else 'Japanese, German subtitles' if prefered_language == 'jp-de' else 'Japanese, English subtitles'], ['gray', 'green'])
ui.print_colored(['Prefered Fallback Language: ', 'German, no subtitles' if prefered_language_fallback == 'de' else 'Japanese, German subtitles' if prefered_language_fallback == 'jp-de' else 'Japanese, English subtitles'], ['gray', 'green'])

ui.print_colored(['Seasons: ', ', '.join([('Season ' + str(elem) if elem != 0 else 'Films') for elem in list(anime_episode_data.keys())])], ['gray', 'green'])

range_str = ''
ui.print_colored('Please Wait ...', 'gray', end='\r')
fetched_data = scripts.pre_download.fetch_anime_data(anime_url, anime_episode_data, prefered_language)
print('               ', end='\r')



while True:
    episode_data_detailled = scripts.pre_download.parse_range_string(anime_episode_data, range_str)
    scripts.pre_download.process_anime(anime_episode_data, episode_data_detailled, fetched_data)
    range_str = input(f'{ui.COLOR_MAP.gray}Please pass in a range String. Leaving this empty will continue with you selection. {ui.COLOR_MAP.green}')
    print(ui.COLOR_MAP.reset, end='\r')

    if not range_str:
        break


# select download mode: strict / flexible
if not 'download_mode' in list(util.read_json_file().keys()):
    db = util.read_json_file()
    db['download_mode'] = 'strict'
    util.write_json_file(db)

download_mode = util.read_json_file()['download_mode']
download_mode_selected = input(f'{ui.COLOR_MAP.gray}Download Mode {ui.COLOR_MAP.white}[{(ui.COLOR_MAP.green + "strict" + ui.COLOR_MAP.white) if download_mode == "strict" else "strict"}, {(ui.COLOR_MAP.green + "flexible" + ui.COLOR_MAP.white) if download_mode == "flexible" else "flexible"}]{ui.COLOR_MAP.gray}: {ui.COLOR_MAP.green}')
print(ui.COLOR_MAP.reset, end='\r')

if download_mode_selected:
    if download_mode_selected not in ['strict', 'flexible']:
        ui.print_colored(['Error: ', 'Please pass in a valid download Mode (strict, flexible)'], ['red', 'gray'])
        exit()
    if download_mode != download_mode_selected:
        download_mode = download_mode_selected
        db = util.read_json_file()
        db['download_mode'] = download_mode
        util.write_json_file(db)


# create_nfo_files
if not 'create_nfo_files' in list(util.read_json_file().keys()):
    db = util.read_json_file()
    db['create_nfo_files'] = True
    util.write_json_file(db)

create_nfo_files = util.read_json_file()['create_nfo_files']
create_nfo_files_selected = input(f'{ui.COLOR_MAP.gray}Create NFO Files {ui.COLOR_MAP.white}[{(ui.COLOR_MAP.green + "yes" + ui.COLOR_MAP.white) if create_nfo_files else "yes"}, {(ui.COLOR_MAP.green + "no" + ui.COLOR_MAP.white) if not create_nfo_files else "no"}]{ui.COLOR_MAP.gray}: {ui.COLOR_MAP.green}')
print(ui.COLOR_MAP.reset, end='\r')

if create_nfo_files_selected:
    if create_nfo_files_selected not in ['yes', 'no']:
        ui.print_colored(['Error: ', 'Please pass in a valid argument (yes, no)'], ['red', 'gray'])
        exit()
    if create_nfo_files != create_nfo_files_selected:
        if create_nfo_files_selected == 'yes':
            create_nfo_files = True
        else:
            create_nfo_files = False

        db = util.read_json_file()
        db['create_nfo_files'] = create_nfo_files
        util.write_json_file(db)


# download_cover_images
if not 'download_cover_images' in list(util.read_json_file().keys()):
    db = util.read_json_file()
    db['download_cover_images'] = True
    util.write_json_file(db)

download_cover_images = util.read_json_file()['download_cover_images']
download_cover_images_selected = input(f'{ui.COLOR_MAP.gray}Download Cover Images {ui.COLOR_MAP.white}[{(ui.COLOR_MAP.green + "yes" + ui.COLOR_MAP.white) if download_cover_images else "yes"}, {(ui.COLOR_MAP.green + "no" + ui.COLOR_MAP.white) if not download_cover_images else "no"}]{ui.COLOR_MAP.gray}: {ui.COLOR_MAP.green}')
print(ui.COLOR_MAP.reset, end='\r')

if download_cover_images_selected:
    if download_cover_images_selected not in ['yes', 'no']:
        ui.print_colored(['Error: ', 'Please pass in a valid argument (yes, no)'], ['red', 'gray'])
        exit()
    if download_cover_images != download_cover_images_selected:
        if download_cover_images_selected == 'yes':
            download_cover_images = True
        else:
            download_cover_images = False

        db = util.read_json_file()
        db['download_cover_images'] = download_cover_images
        util.write_json_file(db)


input(f'{ui.COLOR_MAP.gray}Press Enter to start Download {ui.COLOR_MAP.reset}')

if download_cover_images:
    # download cover image
    ui.print_colored('Downloading Cover Image ... ', 'gray', end='\r')
    downloader.cover_images.download_anime_thumbnail(anime_url)
    ui.print_colored(['Downloading Cover Image ... ', 'Done'], ['gray', 'green'])

    # download background image
    ui.print_colored('Downloading Background Image ... ', 'gray', end='\r')
    i = downloader.cover_images.download_anime_backdrop(anime_url)
    if i:
        ui.print_colored(['Downloading Background Image ... ', 'Done'], ['gray', 'green'])
    else:
        ui.print_colored(['Downloading Background Image ... ', 'Not Found'], ['gray', 'yellow'])

if create_nfo_files:
    # create nfo file (for entire anime)
    ui.print_colored('Creating Anime NFO File ... ', 'gray', end='\r')
    downloader.metadata.fetch_metadata_and_create_anime_nfo_file(anime_url)
    ui.print_colored(['Creating Anime NFO File ... ', 'Done'], ['gray', 'green'])

LANGUAGE_MAP = {'de': 1, 'jp-de': 3, 'jp-en': 2}



for season in list(anime_episode_data.keys()):
    for episode in range(1, anime_episode_data[season] + 1):
        skip_download = False

        with open('download_progress.txt', 'w', encoding='utf-8') as f:
            f.write('')

        print()

        file_name = f's{str(season).zfill(2)}e{str(episode).zfill(2)}.mp4'
        ui.print_colored([f'Downloading {("Season " + str(season)) if season > 0 else ""} {"Episode" if season > 0 else "Film"} {episode} ', f'({file_name})'], ['gray', 'white'])

        
        # download anime
        download_success = '?'
        ui.print_colored('  Downloading Episode ... ', 'gray', end='\r')
        for hoster in ['Vidmoly', 'VOE']:
            if download_success == 'yes':
                break
            if skip_download:
                break
            
            
            episode_url = anime_url + (f'/staffel-{season}/episode-{episode}' if season != 0 else f'/filme/film-{episode}')
            
            available_langs = scripts.lib.get_available_langs_from_url(episode_url)
            
            if prefered_language not in available_langs and download_mode == 'strict':
                print(f'{ui.COLOR_MAP.gray}  Skipping the Download process of {ui.COLOR_MAP.white}{("Season" + str(season) + ", ") if season > 0 else ""}{"Episode" if season > 0 else "Film"} {episode} {ui.COLOR_MAP.gray}because of strict download Mode.')
                skip_download = True
                continue
            
            final_lang = prefered_language
            if prefered_language not in available_langs and prefered_language_fallback in available_langs:
                language_alternative = 'jp-de' if 'jp-de' in available_langs else 'jp-en'
                print(f'{ui.COLOR_MAP.gray}  Prefered Language is not available for this {"Film" if season == 0 else "Episode"}. Falling back to {ui.COLOR_MAP.white} {prefered_language_fallback}{ui.COLOR_MAP.reset}')
                final_lang = prefered_language_fallback

            elif prefered_language not in available_langs and prefered_language_fallback not in available_langs:
                final_lang = ['de', 'jp-en', 'jp-de']
                final_lang.remove(prefered_language)
                final_lang.remove(prefered_language_fallback)
                final_lang = final_lang[0]
                print(f'{ui.COLOR_MAP.gray}  Prefered Language and Prefered Fallback Language are not available for this {"Film" if season == 0 else "Episode"}. Falling back to {ui.COLOR_MAP.white} {final_lang}{ui.COLOR_MAP.reset}')
            
            else:
                print(f'{ui.COLOR_MAP.gray}  Prefered Language {ui.COLOR_MAP.white}({prefered_language}){ui.COLOR_MAP.gray} is available for this {"Film" if season == 0 else "Episode"}{ui.COLOR_MAP.reset}')
            
            available_hosters = scripts.lib.list_available_hosters(episode_url, LANGUAGE_MAP[final_lang])
            if hoster not in available_hosters:
                print(f'{ui.COLOR_MAP.gray}  Hoster {ui.COLOR_MAP.white}{hoster}{ui.COLOR_MAP.gray} is not available for this {"Film" if season == 0 else "Episode"}. Skipping.')
                continue
            
            redirect_url = scripts.lib.get_redirect_url_from_hoster(episode_url, hoster, LANGUAGE_MAP[final_lang])
            #ui.print_colored(['  Fetching ',f'"{episode_url}"'], ['gray', 'white'])
            ui.print_colored([f'  Using {ui.COLOR_MAP.white}{hoster}{ui.COLOR_MAP.gray} with URL: ', f'"{redirect_url}"'], ['gray', 'white'])
            
            threading.Thread(target=downloader.start_download.run_command_and_capture_percentage, args=[hoster.lower() + '.py', redirect_url, file_name], daemon=True).start()
            
            wait_iteration = 0
            while True:
                progress = ''
                with open('download_progress.txt', 'r', encoding='utf-8') as f:
                    progress = f.read().strip()
                if not progress:
                    ui.print_colored(['  Downloading Episode ... ', 'Waiting     '], ['gray', 'yellow'], end='\r')
                    wait_iteration += 1
                    if wait_iteration > 150: # 30 secs ig
                        print()
                        ui.print_colored(['  Warn: ', 'Waiting for the download to start took too long. Skipping this Hoster.'], ['yellow', 'gray'])
                        download_success = 'no'
                        break
                else:
                    progress = float(progress)
                    ui.print_colored(['  Downloading Episode ... ', 'Running     ' if progress != 100 else 'Done   '], ['gray', 'cyan' if progress != 100 else 'green'])
                    ui.print_smooth_progress_bar(progress)
                    
                    if progress == 100:
                        download_success = 'yes'
                        break
                    
                    util.cursor_up(1)
                    
                time.sleep(0.2)
                    
            if download_success == 'no':
                continue
            
        time.sleep(5)
        while True:
            try:
                # move and rename mp4 file
                DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads') 
                CURRENT_DIR = os.path.join(DOWNLOAD_DIR, 'current')
                for file in os.listdir(CURRENT_DIR):
                    if file.endswith('.mp4'):
                        os.rename(os.path.join(CURRENT_DIR, file), os.path.join(DOWNLOAD_DIR, file_name))
                time.sleep(2)
                break
            except (FileExistsError, FileNotFoundError):
                for file in os.listdir(CURRENT_DIR):
                    os.remove(os.path.join(CURRENT_DIR, file))
                break
            except PermissionError:
                continue
        
        if create_nfo_files and not skip_download:
            # create nfo file (for episode)
            ui.print_colored('  Creating Episode NFO File ... ', 'gray', end='\r')
            downloader.metadata.create_episode_nfo(episode_url, prefered_language, file_name.replace('.mp4', ''))
            ui.print_colored(['  Creating Episode NFO File ... ', 'Done        '], ['gray', 'green'])

url_name = anime_url.split('/')[-1]
try:
    os.remove(os.path.join(os.getcwd(), 'downloads', 'current'))
except PermissionError:
    print(f'{ui.COLOR_MAP.yellow}Warn: {ui.COLOR_MAP.gray}Cant delete "current" folder in downloads. Please do that manually.{ui.COLOR_MAP.reset}')
os.makedirs(os.path.join(os.getcwd(), url_name))
for file in os.listdir(os.path.join(os.getcwd(), 'downloads')):
    os.rename(os.path.join(os.getcwd(), 'downloads', file), os.path.join(os.getcwd(), url_name, file))