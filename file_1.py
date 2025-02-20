#!/usr/bin/env python3

import LCD1602
import RPi.GPIO as GPIO
import time
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

# GPIO Mode Setup
GPIO.setmode(GPIO.BCM)

# Rotary Encoder GPIO Pins
CLK = 17  # A
DT = 18   # B
SW = 27   # Button


# Prompt Tree
prompt_tree = {
    "What are you?": {  # "B1_I_wish_I_was_a_g_series.mp3"
        "Imperial junk": {
            "Still active?": {},  # "B1_I'm_ready_for_anything.mp3"
            "Follow orders": {}, 
            "Arm yourself": {}, 
            },
        "Circuits fried?": {  # "B1_Huh.mp3"
                "Memory intact": {},
                "Too damaged": {},  # "B1_This_isn't_going_as_planned.mp3"
                "Last mission": {},
            },
        "Junk now?": {
                "You're worthless": {}, # "B1_It's_my_programming.mp3"
                "Trade for parts": {},
                "Leave you here": {}, 
            },
        },
    "Stop slacking": {  # "B1_Miss_all_the_good_battles.mp3"
            "Directives now!": { # "B1_I_forgot_my_orders.mp3"
                "I'm leaving": {}, 
                "Jawa's now": {},  
                "Srap bucket": {}, 
            },
            "Dumb droid": {  # "B1_im_putting_you_on_report.mp3"
                "Tin can": {},  
                "Not if I shoot u": {},  # "B1_This_is_not_good.mp3"
                "You're worthless": {}, 
            },
            "Scrapped unit?": {  # "B1_Don't_even_think_about_it.mp3"
                "Scavengers it is": {},  
                "operational?": {},  # "B1_I_think_we_have_a_problem.mp3"
                "Alright": {},
            },
        },
    "Jawas do this?": { # "B1_yes.mp3"
        "Stupid scavengers": {
                "One less droid": {},  # "B1_I_hate_this_job.mp3"
                "Not in the slightest": {}, 
                "Still worth much?": {},  # "B1_This_isn't_going_as_planned.mp3"
            },
        "They fix you?": {  # "B1_no.mp3"
                "B1 shutdwon": {},
                "Faulty repairs": {},  
                "Useless now": {},  
            },
        "You can say that": { 
            "Find your unit": {}, 
            "Scrap you later": {}, 
            "You give up?": {},  # "B1_I_need_servicing.mp3"
        },
    },
}

# Menu Structure
menu_tree = {
    "Dev Team": ["JS-730", "KDQ-959", "L419", "SMB-177", "Back"],
    "Info": ["Version: 3.20.6", "Name: B1-CS45", "Back"],
    "Galactic Logs": ["SW 4: 1977", "SW 5: 1980", "SW 6: 1999", "SW 3: 2002", "ERROR: SITH", "Back"],
    "Prompts": prompt_tree,
}

# Global variables
main_menu = list(menu_tree.keys())
submenu = []
prompt_history = []
current_directory = os.getcwd()


# Booleans 
lightsabers_unlock = False
order_66_unlock = False
rebels_unlock = False
roger_roger_unlock = False
rat_unlock = False
sith_path_unlock = False
jedi_path_unlock = False
sarlacc_unlock = False


# Menu State Tracking
current_menu = main_menu
menu_index_top = 0
menu_index_bottom = 1 if len(main_menu) > 1 else 0
in_submenu = False
rotary_turns = 0  # Track rotary turns
button_clicks = 0  # Track the total button pushes

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Rotary Encoder State
clk_last_state = GPIO.input(CLK)
last_turn_time = time.time()  # Tracks last movement time
debounce_interval = 0.5  # Increase to make encoder less sensitive

"""-------------------------LED LOGIC-------------------------"""

# GPIO Pin Setup for RGB LEDs
LED_PINS = {
    "LED1": {"red": 10, "green": 9, "blue": 11},  # GPIO pins for LED1
    "LED2": {"red": 5, "green": 6, "blue": 13},    # GPIO pins for LED2
    "LED3": {"red": 23, "green": 24, "blue": 25},  # GPIO pins for LED3
}

# GPIO Pin Setup for Touch Sensors
TOUCH_SENSORS = {
    "SENSOR1": 16,  # GPIO pin for Sensor 1 (paired with LED1)
    "SENSOR2": 20,  # GPIO pin for Sensor 2 (paired with LED2)
    "SENSOR3": 21,  # GPIO pin for Sensor 3 (paired with LED3)
}

# Colors to cycle through
COLORS = [
    (1, 0, 0),  # Red
    (0, 1, 0),  # Green
    (0, 0, 1),  # Blue
    (1, 0, 1),  # Purple
]

# Setup LED pins as outputs
for led, pins in LED_PINS.items():
    for color, pin in pins.items():
        GPIO.setup(pin, GPIO.OUT, initial = GPIO.LOW)  # Turn off all LEDs initially

# Setup touch sensor pins as inputs with pull-up resistors
for sensor, pin in TOUCH_SENSORS.items():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to set LED color
def set_led_color(led, red, green, blue):
    GPIO.output(LED_PINS[led]["red"], red)
    GPIO.output(LED_PINS[led]["green"], green)
    GPIO.output(LED_PINS[led]["blue"], blue)

# Dictionary to track the current color state for each LED
color_states = {"LED1": 1, "LED2": 1, "LED3": 1}  # Start with all LEDs off but set to green

# Dictionary to track the previous state of each sensor
sensor_states = {sensor: GPIO.LOW for sensor in TOUCH_SENSORS}

# Function to toggle color for a specific LED
def toggle_led_color(led):
    color_states[led] = (color_states[led] + 1) % len(COLORS)
    set_led_color(led, *COLORS[color_states[led]])

def check_led_states():
    """Check if the states of the LEDs."""
    global sith_path_unlock, jedi_path_unlock, roger_roger_unlock

    if (COLORS[color_states["LED1"]] == (1, 0, 0) and
        COLORS[color_states["LED2"]] == (1, 0, 0) and
        COLORS[color_states["LED3"]] == (1, 0, 0)):
        sith_path_unlock = True

    
    if (COLORS[color_states["LED1"]] == (0, 0, 1) and  # Blue is (0, 0, 1)
        COLORS[color_states["LED2"]] == (0, 1, 0) and  # Green is (0, 1, 0)
        COLORS[color_states["LED3"]] == (1, 0, 1)):    # Purple is (1, 0, 1)
        jedi_path_unlock = True


    if (COLORS[color_states["LED1"]] == (1, 0, 0) and # Red + Red = Red
        COLORS[color_states["LED2"]] == (1, 0, 0) and # Red + Green = Yellow
        COLORS[color_states["LED3"]] == (0, 1, 0)) and jedi_path_unlock and sith_path_unlock:
        roger_roger_unlock = True


    check_unlocks()


# Main loop
def check_sensor():
    # Check each sensor and update its corresponding LED
    for sensor, pin in TOUCH_SENSORS.items():
        current_state = GPIO.input(pin)
        if current_state != sensor_states[sensor]:  # Sensor state has changed
            sensor_states[sensor] = current_state  # Update the sensor state
            if current_state == GPIO.LOW:  # Sensor is pressed (LOW)
                led = f"LED{sensor[-1]}"  # Match sensor to LED (e.g., SENSOR1 -> LED1)
                toggle_led_color(led)
    check_led_states()


"""-------------------------MENU LOGIC-------------------------"""

def update_display():
    """Update LCD with the current menu selection."""
    global current_menu, menu_index_top, menu_index_bottom

    # Ensure menu_index_top and menu_index_bottom are within bounds
    if not current_menu:
        # If current_menu is empty, reset to main menu
        current_menu = main_menu
        menu_index_top = 0
        menu_index_bottom = 1 if len(current_menu) > 1 else 0

    menu_index_top = menu_index_top % len(current_menu)  # Wrap around if out of bounds
    menu_index_bottom = (menu_index_top + 1) % len(current_menu)  # Wrap around if out of bounds

    line1 = current_menu[menu_index_top]
    line2 = current_menu[menu_index_bottom] if len(current_menu) > 1 else ""
    LCD1602.write_lcd(line1, line2)
    print(f"[DISPLAY] {line1} / {line2}")


def check_prompts():
    """Navigate the nested prompt tree based on user selection."""
    global current_menu, menu_tree, prompt_history, menu_index_top, menu_index_bottom, in_submenu

    if in_submenu and current_menu == list(prompt_tree.keys()):
        # Get the selected prompt key
        selected_prompt = current_menu[menu_index_top]
        print(f"[DEBUG] Selected prompt: {selected_prompt}")

        # Navigate deeper into the prompt tree
        if selected_prompt in prompt_tree:
            new_prompts = prompt_tree[selected_prompt]

            if new_prompts is None:  # Handle "Back" button
                print("[NAVIGATION] Returning to Main Menu...")
                current_menu = main_menu  # Reset to main menu
                in_submenu = False
                prompt_history = []  # Clear history
            else:
                prompt_history.append(selected_prompt)  # Save the selected key (string) to history
                current_menu = list(new_prompts.keys())  # Move deeper into prompts

            # Update display and reset selection
            menu_index_top = 0
            menu_index_bottom = 1 if len(current_menu) > 1 else 0
            update_display()  # Update the display immediately

            # Play voice line for the selected prompt (will wait for audio to finish)
            play_voice_line(selected_prompt)

        else:
            print("[DEBUG] No new responses available.")

    elif in_submenu and current_menu != list(prompt_tree.keys()):
        # Handle navigation within nested prompts
        selected_prompt = current_menu[menu_index_top]
        print(f"[DEBUG] Selected nested prompt: {selected_prompt}")

        # Find the current nested dictionary
        current_dict = prompt_tree
        for key in prompt_history:  # Traverse the history to get to the current level
            current_dict = current_dict[key]

        if selected_prompt in current_dict:
            new_prompts = current_dict[selected_prompt]

            if new_prompts is None:  # Handle "Back" button
                if prompt_history:
                    # Go back to the p"Kylo Ren"revious menu
                    prompt_history.pop()  # Remove the last key from history
                    if prompt_history:
                        # Rebuild current_menu based on the updated history
                        current_dict = prompt_tree
                        for key in prompt_history:
                            current_dict = current_dict[key]
                        current_menu = list(current_dict.keys())
                    else:
                        # Return to the main menu
                        current_menu = main_menu
                        in_submenu = False
                    menu_index_top = 0
                    menu_index_bottom = 1 if len(current_menu) > 1 else 0
                    print("[NAVIGATION] Going back to previous menu...")
                else:
                    # Return to the main menu
                    current_menu = main_menu
                    in_submenu = False
                    print("[NAVIGATION] Returning to Main Menu...")
            else:
                # Move deeper into the nested prompts
                if new_prompts:  # Check if there are further prompts
                    prompt_history.append(selected_prompt)  # Save the selected key (string) to history
                    current_menu = list(new_prompts.keys())
                    menu_index_top = 0
                    menu_index_bottom = 1 if len(current_menu) > 1 else 0
                    print(f"[NAVIGATION] Entering deeper into prompt tree: {selected_prompt}")
                else:
                    # No further prompts, return to main menu
                    current_menu = main_menu
                    in_submenu = False
                    prompt_history = []
                    print("[NAVIGATION] No further prompts, returning to Main Menu...")

            # Update display and reset selection
            update_display()  # Update the display immediately

            # Play voice line for the selected prompt (will wait for audio to finish)
            play_voice_line(selected_prompt)

        else:
            print("[DEBUG] No new responses available.")

    else:
        print("[DEBUG] Not inside the Prompts submenu.")

def play_voice_line(prompt):
    """Play a voice line using pygame and wait for it to finish."""
    current_directory = os.getcwd()
    voice_lines = {

        # Prompts
        "What are you?": os.path.join(current_directory, "AUDIO_FILES/B1_I_wish_I_was_a_g_series.mp3"),
        "Still active?": os.path.join(current_directory, "AUDIO_FILES/B1_I'm_read_for_anything.mp3"),
        "Circuits fried?": os.path.join(current_directory, "AUDIO_FILES/B1_huh.mp3"),
        "Too damaged": os.path.join(current_directory, "AUDIO_FILES/B1_this_isn't_going_as_planned.mp3"),
        "You're worthless": os.path.join(current_directory, "AUDIO_FILES/B1_it's_my_programming.mp3"),
        "Stop slacking": os.path.join(current_directory, "AUDIO_FILES/B1_miss_all_the_good_battles.mp3"),
        "Directives now!": os.path.join(current_directory, "AUDIO_FILES/B1_I_forgot_my_orders.mp3"),
        "Dumb droid":  os.path.join(current_directory, "AUDIO_FILES/B1_im_putting_you_on_report.mp3"),
        "Not if I shoot u": os.path.join(current_directory, "AUDIO_FILES/B1_this_is_not_good.mp3"),
        "Scrapped unit?": os.path.join(current_directory, "AUDIO_FILES/B1_don't_even_think_about_it.mp3"),
        "operational?": os.path.join(current_directory, "AUDIO_FILES/B1_I_think_we_have_a_problem.mp3"),
        "Jawas do this?": os.path.join(current_directory, "AUDIO_FILES/B1_yes.mp3"),
        "One less droid": os.path.join(current_directory, "AUDIO_FILES/B1_I_hate_this_job.mp3"),
        "They fix you?": os.path.join(current_directory, "AUDIO_FILES/B1_no.mp3"),
        "You give up?": os.path.join(current_directory, "AUDIO_FILES/B1_I_need_servicing.mp3"),

        # Galactic Logs
        "SW 4: 1977": os.path.join(current_directory, "AUDIO_FILES/one_in_a_million_shot.mp3"),
        "ERROR: SITH": os.path.join(current_directory, "AUDIO_FILES/sith_theme.mp3"),
        "Rebels": os.path.join(current_directory, "AUDIO_FILES/Kanan_Jarrus_death.mp3"),


        # Ligtsabers
        "0xFF0000": os.path.join(current_directory, "AUDIO_FILES/Darth_Vader_lightsaber.mp3"),
        "0x00FF00": os.path.join(current_directory, "AUDIO_FILES/lightsaber_ignition.mp3"),

        # Sith Path
        "Kylo Ren": os.path.join(current_directory, "AUDIO_FILES/Kylo_Ren.mp3"),

        # Jedi Path
        "Yoda": os.path.join(current_directory, "AUDIO_FILES/Yoda_do_or_do_not.mp3"),

        # Roger Roger 
        "More More!": os.path.join(current_directory, "AUDIO_FILES/more_more.mp3"),
        "Yoda Death": os.path.join(current_directory, "AUDIO_FILES/Yoda_death.mp3"),
        "Roger Roger": os.path.join(current_directory, "AUDIO_FILES/B1_roger_roger.mp3"),
    }

    if prompt in voice_lines:
        try:
            # Initialize pygame mixer
            pygame.mixer.init()
            # Load and play the audio file
            pygame.mixer.music.load(voice_lines[prompt])
            pygame.mixer.music.play()
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                continue
        except Exception as e:
            print(f"[ERROR] Failed to play voice line: {e}")
    else:
        print(f"[DEBUG] No voice line for prompt: {prompt}")

def check_unlocks():
    """Checks and unlocks any Easter eggs based on conditions."""
    global  main_menu, menu_tree, rat_unlock, lightsabers_unlock, \
            rebels_unlock, order_66_unlock, roger_roger_unlock, sarlacc_unlock


    if rotary_turns >= 20 and button_clicks >= 9 and not lightsabers_unlock:
        lightsabers_unlock = True
        main_menu.append("Lightsabers")
        menu_tree["Lightsabers"] = ["0xFF00FF", "0x00FF00", "0xFF0000", "0x0000FF","0xFFFF00" ,"Back" ]
        print("[SECRET] Lightsabers unlocked!")

    if rotary_turns == 66 and not order_66_unlock:
        order_66_unlock = True
        main_menu.append("Order 66")
        menu_tree["Order 66"] = ["Eliminate all", "The Jedi", "Back"]
        print("[SECRET] Order 66 Unlocked!")

    if rotary_turns == -8 and button_clicks == 16 and not rat_unlock:
        rat_unlock = True
        main_menu.append("Rat")
        menu_tree["Rat"] = ["A wild Rat", "Has appeared", "Back"]
        print("[SECRET] Rat Unlocked!")

    if sith_path_unlock and "Sith Path" not in main_menu:
        main_menu.append("Sith Path")
        menu_tree["Sith Path"] = ["Darth Sidious","Darth Vader", "Darth Maul", "Kylo Ren", "Back"]
        print("[SECRET] Sith path Unlocked!")

    if jedi_path_unlock and "Jedi Path" not in main_menu:
        main_menu.append("Jedi Path")
        menu_tree["Jedi Path"] = ["Luke Skywalker", "Yoda", "Mace Windu", "Back"]
        print("[SECRET] Jedi path Unlocked!")

    if roger_roger_unlock and "Roger Roger" not in main_menu:
        main_menu.append("Roger Roger")
        menu_tree["Roger Roger"] = ["More More!", "Yoda Death", "Roger Roger", "Back"]
        print("[SECRET Roger Roger Unlocked!]")


    if order_66_unlock and lightsabers_unlock and not rebels_unlock:
        rebels_unlock = True
        menu_tree["Galactic Logs"].insert(4,"Rebels")
        print("[SECRET] Rebels unlocked!")

    if order_66_unlock and lightsabers_unlock and rebels_unlock and jedi_path_unlock and sith_path_unlock and roger_roger_unlock \
        and not sarlacc_unlock:

        sarlacc_unlock = True
        main_menu.append("Sarclacc Pit")
        menu_tree["Sarclacc Pit"] = ["*Boba Fett" , "has fallen into", "the Pit*", "Back"]
        print("[SECRET] Sarlacc Pit Unlocked!")


def read_rotary():
    """Reads rotary encoder input with reduced sensitivity."""
    global menu_index_top, menu_index_bottom, clk_last_state, last_turn_time, rotary_turns
    clk_state = GPIO.input(CLK)
    dt_state = GPIO.input(DT)
    current_time = time.time()

    if clk_state != clk_last_state and (current_time - last_turn_time) > debounce_interval:
        if dt_state != clk_state:
            menu_index_top = (menu_index_top + 1) % len(current_menu)
            menu_index_bottom = (menu_index_top + 1) % len(current_menu)
            rotary_turns += 1
        else:
            menu_index_top = (menu_index_top - 1) % len(current_menu)
            menu_index_bottom = (menu_index_top + 1) % len(current_menu)
            rotary_turns -= 1

        # Check for unlocks
        check_unlocks()

        print(f"[ROTARY] Turn Count: {rotary_turns}")
        last_turn_time = current_time
        update_display()
    clk_last_state = clk_state

def check_button():
    """Check if the encoder button is pressed."""
    global current_menu, submenu, menu_index_top, menu_index_bottom, in_submenu, button_clicks, prompt_history

    if GPIO.input(SW) == GPIO.LOW:
        selected_item = current_menu[menu_index_top]
        button_clicks += 1

        if in_submenu:
            if selected_item == "Back":
                if prompt_history:
                    prompt_history.pop()
                    if prompt_history:
                        current_dict = prompt_tree
                        for key in prompt_history:
                            current_dict = current_dict[key]
                        current_menu = list(current_dict.keys())
                    else:
                        current_menu = main_menu
                        in_submenu = False
                    menu_index_top = 0
                    menu_index_bottom = 1 if len(current_menu) > 1 else 0
                    print(f"[NAVIGATION] Going back to previous menu | Button Count: {button_clicks}")
                else:
                    current_menu = main_menu
                    in_submenu = False
                    menu_index_top = 0
                    menu_index_bottom = 1 if len(main_menu) > 1 else 0
                    print(f"[NAVIGATION] Returning to Main Menu | Button Count: {button_clicks}")
            else:
                # Play voice line if a submenu item matches
                if selected_item in menu_tree.get("Jedi Path", {}) or \
                selected_item in menu_tree.get("Sith Path", {}) or \
                selected_item in menu_tree.get("Galactic Logs", {}) or \
                selected_item in menu_tree.get("Lightsabers", {}) or \
                selected_item in menu_tree.get("Roger Roger", {}):
                    play_voice_line(selected_item)
                else:
                    check_prompts()  # For other menu options

        else:
            if selected_item == "Prompts":
                current_menu = list(prompt_tree.keys())
                in_submenu = True
                menu_index_top = 0
                menu_index_bottom = 1 if len(current_menu) > 1 else 0
                print(f"[NAVIGATION] Entering {selected_item} submenu | Button Count: {button_clicks}")
            elif selected_item in menu_tree:  # Check for dynamically added Jedi/Sith paths
                submenu = menu_tree[selected_item]
                
                # If the submenu is a dictionary, get the keys; otherwise, assume it's a list
                if isinstance(submenu, dict):
                    current_menu = list(submenu.keys())
                else:
                    current_menu = submenu  # Handle simple list-based submenus
                in_submenu = True
                menu_index_top = 0
                menu_index_bottom = 1 if len(current_menu) > 1 else 0
                print(f"[NAVIGATION] Entering {selected_item} submenu | Button Count: {button_clicks}")
            else:
                print(f"[ACTION] Selected {selected_item} | Button Count: {button_clicks}")

        update_display()
        time.sleep(0.3)  # Basic debounce


# Initialize LCD
def start_up():
    LCD1602.init_lcd()
    update_display()

def menu():
    read_rotary()
    check_button()
    check_sensor()  # Check touch sensors and update LEDs
    time.sleep(0.01)  # Small delay to reduce CPU usage

def shutdown():
    GPIO.cleanup()
    LCD1602.send_command(0x01)  # Clear LCD
    print("\n[EXIT] Cleanup and Shutdown...")
