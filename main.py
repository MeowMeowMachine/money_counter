import json
import os
import ctypes
import time
import csv
import math
import os
from datetime import datetime
import ctypes

try: 
    import pygame
    import keyboard
    import sdl2

except ImportError as e:
    print(f"[CRITICAL ERROR] \n\n Please install the following dependencies:\n\n - pygame\n - keyboard\n - PySDL2\n\n Error: {e}")
    print("You can install them using pip install pygame keyboard PySDL2")
    exit(0)

def load_config(*keys, default=None):
    """
    Dynamically load nested config values from config.json using any number of keys.
    If the value is not found, returns 'default' if provided, else raises KeyError.
    """
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    if default is not None:
                        return default
                    raise KeyError(f"Config path {' -> '.join(map(str, keys))} not found in config.json")
            return current
    except FileNotFoundError:
        print("[CRITICAL ERROR]\n\n Error whilst loading config.json. Please ensure the file exists and is formatted correctly.\n\n")
        exit(1)
goal = load_config("goal")

def money_calculation(elapsed_time, moneyperhour):
    """
    Calculate the money earned based on elapsed time and money per hour.
    """
    money_per_second = moneyperhour / 3600  # Convert money per hour to money per second
    return round(elapsed_time * money_per_second, 2)

def save_progresss( elapsed_time, money):
    """
    Save the progress to a CSV file.
    """
    global goal
    date = datetime.now().strftime("%m/%d//%#I:%M %p")
    try:
        with open('progress.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            rows = list(reader)
            if rows and len(rows) >= 1:
                last_row = rows[-1]
                progress = float(last_row[1]) + money
            else:
                progress = money
    except FileNotFoundError:
        print("[CRITICAL ERROR] \n\n Error whilst loading progress.csv. Please ensure the file exists and is formatted correctly.\n\n")
        exit(1)
    hours_worked = math.floor(elapsed_time / 3600)
    minutes_worked = math.floor((elapsed_time % 3600) / 60)
    formatted_time = f"{hours_worked}H {minutes_worked}M"
    remaining = goal - progress
    with open('progress.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if os.stat('progress.csv').st_size == 0:  # Check if the file is empty
            writer.writerow(['date', 'progress', 'time', 'made', 'remaining', 'percentage'])  # Write header
        writer.writerow([date, progress, formatted_time, money, remaining, round((progress / goal) * 100, 2)])
    print(f"[INFO] Progress saved: {date}, {progress}, {formatted_time}, {money}, {remaining}, {round((progress / goal) * 100, 2)}%")

# load configs
Currency = load_config("currency") # EUR
Start_key = load_config("Keys", "StartStopSession")
active = False
last_dollar = 0
start_time = 0
accumulated_time = 0
fps = 60
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{load_config('GUI', 'Layout', 'PositionX', default=0)},{load_config('GUI', 'Layout', 'PositionY', default=0)}"
pygame.init()
clock = pygame.time.Clock()
color_hex = load_config("GUI", "Formatting", "Color")
rgb_color = pygame.Color(color_hex)[:3]
box_width = load_config("GUI", "Layout", "Width", default=100)
box_height = load_config("GUI", "Formatting", "FontSize", default=36) + 20  # padding
topmost_interval = 2  # Seconds
last_topmost_time = 0
screen = pygame.display.set_mode((box_width, box_height))
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

def set_pygame_window_always_on_top():
    info = pygame.display.get_wm_info()
    # try common keys for native handle
    hwnd = info.get("window") or info.get("hwnd") or info.get("window_handle")
    if not hwnd:
        return False

    # create SDL_Window* from native window handle
    sdl_window = sdl2.SDL_CreateWindowFrom(ctypes.c_void_p(hwnd))
    if not sdl_window:
        return False

    # set always on top
    res = sdl2.SDL_SetWindowAlwaysOnTop(sdl_window, sdl2.SDL_TRUE)
    # NOTE: do NOT destroy the sdl_window returned by SDL_CreateWindowFrom,
    # because it wraps the existing native window.
    return res == 0
pygame.display.set_caption(load_config("GUI", "Layout", "Title"))

font = pygame.font.SysFont(load_config("GUI", "Formatting", "Font"), load_config("GUI", "Formatting", "FontSize"))
current_balance = f"{Currency} 0.00"
pygame.mixer.init()
# Start listening
print(f"[INFO] Program activated; Listening for '{Start_key}' key to start counting.")
while True:
    elapsed_time = accumulated_time + (time.perf_counter() - start_time if active else 0)
    time.sleep(0.1)  # Add a small delay to reduce CPU usage
    
    # Overlapping loop

    if keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt gr'):
        print("[INFO] CTRL + AltGr pressed. Exiting program.")
        pygame.quit()
        exit(0)
    if keyboard.is_pressed(Start_key):
        active = not active
        if active:
            # Starting or resuming: reset start_time to now
            start_time = time.perf_counter()
            print(f"[INFO] '{Start_key}' key pressed; Starting count...")
        else:
            # Pausing: add elapsed time to accumulated_time
            elapsed = time.perf_counter() - start_time
            accumulated_time += elapsed
            start_time = 0
            print(f"[INFO] '{Start_key}' key pressed; Pausing count. Elapsed this session: {elapsed:.2f} seconds. Total accumulated: {accumulated_time:.2f} seconds.")

        # Wait for key release to avoid multiple toggles
        while keyboard.is_pressed(Start_key):
            pass
    if keyboard.is_pressed(load_config("Keys", "SaveProgress")):
        active = False
        elapsed_time = accumulated_time + (time.perf_counter() - start_time if active else 0)
        print(f"[INFO] Progress saved. Elapsed time: {elapsed_time:.2f} seconds.\n [INFO] Money earned: {Currency} {money_calculation(elapsed_time, load_config('income')):.2f}")
        start_time = 0
        save_progresss(elapsed_time, money_calculation(elapsed_time, load_config('income')))
        exit(0)
        while keyboard.is_pressed(load_config("Keys", "SaveProgress")):
            pass
    
    if active:
        
        time.sleep(0.1)  # Add a small delay to reduce CPU usage
        print(time.perf_counter() - start_time, end="\r")
        # print money
        current_balance = f"{Currency} {money_calculation(elapsed_time, load_config('income')):.2f}"
        print(f"[INFO] Current balance: {current_balance}", end="\r")
        print(f"[INFO] Progress: {round((money_calculation(elapsed_time, load_config('income')) / goal) * 100, 2)}%")
        # Play dollar sound when making a dollar or even more dollars
        def play_priority_sound(dollar_triggered, even_more_triggered):
            # If even_more_triggered: always interrupt and play that sound
            if even_more_triggered:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                sound_path = load_config("Sounds", "evenmoredollarsound")
                print(f"You've earned {load_config('Sounds', 'trigger', 'evenmoredollars')} dollars!")
                try:
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play()
                except pygame.error as e:
                    print(f"[ERROR] Failed to load sound: {e}")
                return

            # If dollar_triggered and no even more sound playing, play dollar sound if no sound is playing
            if dollar_triggered:
                if not pygame.mixer.music.get_busy():  # Only play if nothing is playing
                    sound_path = load_config("Sounds", "Dollarsound")
                    if load_config("Sounds", "trigger", "Dollar") == 1: print("You've earned a dollar!")
                    else: print(f"You've earned {load_config('Sounds', 'trigger', 'Dollar')} dollars!")
                    
                    try:
                        pygame.mixer.music.load(sound_path)
                        pygame.mixer.music.play()
                    except pygame.error as e:
                        print(f"[ERROR] Failed to load sound: {e}")
                else:
                    # even_more sound might be playing or another sound, so skip playing dollar sound
                    pass
                
            # If neither triggered, do nothing

            





        money_calculation(elapsed_time, load_config('income'))

        current_money = math.floor(money_calculation(elapsed_time, load_config('income')))
        dollar_trigger = load_config("Sounds", "trigger", "Dollar")
        even_more_trigger = load_config("Sounds", "trigger", "evenmoredollars")
        dollar_triggered = last_dollar != current_money and current_money % dollar_trigger == 0
        even_more_triggered = last_dollar != current_money and current_money % even_more_trigger == 0

        if dollar_triggered or even_more_triggered:
            last_dollar = current_money
            play_priority_sound(dollar_triggered, even_more_triggered)
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

       # Set box width and height from config (window size = box size)
    # Remove position offsets, box_x and box_y are zero now
    box_x, box_y = 0, 0

    # Set your screen size to box size BEFORE your main loop

    
    hwnd = pygame.display.get_wm_info()['window']
    ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, box_width, box_height, 0x0001 | 0x0002)  # SWP_NOMOVE | SWP_NOZORDER

    # Parse box color and border color
    box_color = pygame.Color(load_config("GUI", "Formatting", "Color", default="#FFFFFF"))[:3]
    border_color = (0, 0, 0)  # black border

    # Inside your main loop:

    # Fill the entire window with box color (no background)
    screen.fill(box_color)

    # Draw border around the window edges (box)
    pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2)

    # Render current balance text, center in window
    # Prepare progress percentage and worktime counter
    elapsed_time = accumulated_time + (time.perf_counter() - start_time if active else 0)
    # Calculate progress percent using accumulated progress from progress.csv
    try:
        with open('progress.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            rows = list(reader)
            if rows and len(rows) >= 1:
                last_row = rows[-1]
                accumulated_progress = float(last_row[1])
            else:
                accumulated_progress = 0
    except FileNotFoundError:
        accumulated_progress = 0

    current_money = money_calculation(elapsed_time, load_config('income'))
    total_progress = accumulated_progress + current_money
    progress_percent = round((total_progress / goal) * 100, 2)
    hours_worked = math.floor(elapsed_time / 3600)
    minutes_worked = math.floor((elapsed_time % 3600) / 60)
    worktime_str = f"{hours_worked}H {minutes_worked}M"

    # Combine balance, progress %, and worktime
    display_text = f"{current_balance} | {progress_percent}% | {worktime_str}"

    # Blinking logic for inactive state
    if not active:
        blink_color = (255, 0, 0) if int(time.time()) % 2 == 0 else (0, 0, 0)
        text_surface = font.render(display_text, True, blink_color)
    else:
        text_surface = font.render(display_text, True, border_color)

    text_rect = text_surface.get_rect(center=(box_width // 2, box_height // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    if load_config("GUI", "Layout", "Overlapping", default=False):
        if time.time() - last_topmost_time > topmost_interval:
            set_pygame_window_always_on_top()
    clock.tick(fps)


# pygame