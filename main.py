import json
from tracemalloc import start
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
import time
import csv
import math
import os
try: 
    import pygame
    import keyboard
    from datetime import datetime

except ImportError as e:
    print(f"[CRITICAL ERROR] \n\n Please install pygame & keyboard to run this program. \n\n Error: {e}")

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
                print("DEBUG; PROGRESS DETECTED;    ", progress)
            else:
                progress = money
                print("DEBUG; NO PROGRESS DETECTED;    ", progress)
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

pygame.mixer.init()
# Start listening
print(f"[INFO] Program activated; Listening for '{Start_key}' key to start counting.")
while True:
    if keyboard.is_pressed(Start_key):
        active = not active
        print(f"[INFO] '{Start_key}' key pressed; {'Starting' if active else 'Stopping'} count...")
        if active and start_time == 0:
            start_time = time.perf_counter()
        else:
            elapsed_time = time.perf_counter() - start_time
            print(f"[INFO] Session stopped. Elapsed time: {elapsed_time:.2f} seconds.")
        # Wait for key release to avoid multiple toggles
        while keyboard.is_pressed(Start_key):
            pass
    if keyboard.is_pressed(load_config("Keys", "SaveProgress")):
        active = False
        elapsed_time = time.perf_counter() - start_time
        print(f"[INFO] Progress saved. Elapsed time: {elapsed_time:.2f} seconds.\n [INFO] Money earned: {Currency} {money_calculation(elapsed_time, load_config('income')):.2f}")
        start_time = 0
        save_progresss(elapsed_time, money_calculation(elapsed_time, load_config('income')))
        exit(0)
        while keyboard.is_pressed(load_config("Keys", "SaveProgress")):
            pass
    
    if active:
        time.sleep(0.1)  # Add a small delay to reduce CPU usag
        print(time.perf_counter() - start_time, end="\r")
        # print money
        current_balance = f"{Currency} {money_calculation(time.perf_counter() - start_time, load_config('income')):.2f}"
        print(f"[INFO] Current balance: {current_balance}", end="\r")
        print(f"[INFO] Progress: {round((money_calculation(time.perf_counter() - start_time, load_config('income')) / goal) * 100, 2)}%")
        # Play dollar sound when making a dollar or even more dollars
        def play_priority_sound(dollar_triggered, even_more_triggered):
            # Stop any currently playing sound
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            # Higher dollar, higher priority
            if even_more_triggered:
                sound_path = load_config("Sounds", "evenmoredollarsound")
                print("You've earned even more dollars!")
            elif dollar_triggered:
                sound_path = load_config("Sounds", "Dollarsound")
                print("You've earned a dollar!")
            else:
                return
            try:
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            except pygame.error as e:
                print(f"[ERROR] Failed to load sound: {e}")
                return
            

        current_money = math.floor(money_calculation(time.perf_counter() - start_time, load_config('income')))
        dollar_trigger = load_config("Sounds", "trigger", "Dollar")
        even_more_trigger = load_config("Sounds", "trigger", "evenmoredollars")
        dollar_triggered = last_dollar != current_money and current_money % dollar_trigger == 0
        even_more_triggered = last_dollar != current_money and current_money % even_more_trigger == 0

        if dollar_triggered or even_more_triggered:
            last_dollar = current_money
            play_priority_sound(dollar_triggered, even_more_triggered)
            