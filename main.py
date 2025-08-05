#######
# Enter your income per hour below
income = 15 # Income per hour

########


















try: income = int(income)
except ValueError:
    print("Invalid input for income. Please enter a numeric value.")
    exit(1)

try: 
    import pygame
except ImportError as e:
    print(f"[CRITICAL ERROR] \n\n Please install pygame to run this program. \n\n Error: {e}")


