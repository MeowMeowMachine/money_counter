import json

def load_config(config, Value=None, Value2=None):
    try:
        with open('config.json', 'r') as file:
            data = json.load(file)
            print(data)
            # Check if the specified config exists in the loaded data
            if config in data:
                if Value is not None:
                    # If a default value is provided, return it if the config is not found
                    if Value2 is not None:
                        return data[config].get(Value, Value2)
                    else:
                        return data[config].get(Value, None)
                return data[config]
            else:
                # If the config is not found and no default value is provided, raise an error
                raise KeyError(f"Config '{config}' not found in config.json")
    except FileNotFoundError:
        print("[CRITICAL ERROR]\n\n Error whilst loading config.json. Please ensure the file exists and is formatted correctly.\n\n")
        exit(1)
import time
try: 
    import pygame
    import keyboard

except ImportError as e:
    print(f"[CRITICAL ERROR] \n\n Please install pygame & keyboard to run this program. \n\n Error: {e}")

def 



# load configs
Currency = load_config("currency") # EUR
Start_key = load_config("Keys", "StartStopSession")
active = False
# Start listening
print(f"[INFO] Program activated; Listening for '{Start_key}' key to start counting.")
while True:
    if keyboard.is_pressed(Start_key):
        active = not active
        print(f"[INFO] '{Start_key}' key pressed; {'Starting' if active else 'Stopping'} count...")
        # Wait for key release to avoid multiple toggles
        while keyboard.is_pressed(Start_key):
            pass
    
    if active:
        time.sleep(0.1)  # Add a small delay to reduce CPU usage
        