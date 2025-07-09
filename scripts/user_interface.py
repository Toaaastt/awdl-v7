from typing import Literal
from colorama import Fore, Style




class COLOR_MAP:
    red = Fore.RED
    green = Fore.GREEN
    blue = Fore.BLUE
    yellow = Fore.YELLOW
    cyan = Fore.CYAN
    magenata = Fore.MAGENTA
    white = Fore.WHITE
    gray = Fore.LIGHTBLACK_EX
    black = Fore.BLACK
    reset = Style.RESET_ALL


def print_colored(text,
                  color: Literal['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'white', 'gray', 'black'] | list[Literal['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'white', 'gray', 'black']],
                  end='\n'
                  ):
    
    color_map_dict = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'cyan': Fore.CYAN,
        'magenta': Fore.MAGENTA,
        'white': Fore.WHITE,
        'gray': Fore.LIGHTBLACK_EX,
        'black': Fore.BLACK
    }
    
    if isinstance(text, list):
        print_text = ''
        for p, part in enumerate(text):
            print_text += color_map_dict[color[p]] + part + Style.RESET_ALL
        print(print_text, end=end)
    else:
        print(color_map_dict[color] + text + Style.RESET_ALL, end=end) # type: ignore
            

def print_smooth_progress_bar(percent, length=60):

    percent = max(0, min(percent, 100))
    total_blocks = length

    blocks = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']

    full_block_count = int(percent / 100 * total_blocks)
    partial_block_fraction = (percent / 100 * total_blocks) - full_block_count

    partial_block_index = int(partial_block_fraction * (len(blocks) - 1))

    bar = '█' * full_block_count
    if full_block_count < total_blocks:
        bar += blocks[partial_block_index]
        bar += ' ' * (total_blocks - full_block_count - 1)

    print(f"  {COLOR_MAP.white if percent != 100 else COLOR_MAP.gray}|{bar}| {COLOR_MAP.green}{percent:.2f}%{COLOR_MAP.reset}", end='\r' if percent != 100 else '\n')
