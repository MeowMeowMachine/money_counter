####### All changed jnto a contigater
# Enter your income per hour below
income = 15 # Income per hour
goal = 3100
progress = 300 # Load from config later
Autoprogressload = true
Moneysound = "C:foo"
goalsound = "D;Boo"
prosound = "L;moo"
Key_start_stop = "AltF4"
key_ProjEnd = "F18"

########


















try: income = int(income)
except ValueError:
    print("Invalid input for income. Please enter a numeric value.")
    exit(1)

try: 
    import pygame
except ImportError as e:
    print(f"[CRITICAL ERROR] \n\n Please install pygame to run this program. \n\n Error: {e}")


