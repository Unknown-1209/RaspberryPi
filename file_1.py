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
    "Hello there": {
        "What happened?": {
            "It's a long story.": {
                "I have time.": {},
                "Never mind.": {},
            },
        },
        "Get out of the sand!": {
            "I'm stuck.": {
                "Need help?": {},
                "You're on your own.": {},
            },
        },
        "Stop slacking!": {
            "I'm not slacking!": {
                "Then get up.": {},
                "Fine, I'll leave.": {},
            },
        },
    },
    "Are you okay?": {
        "I need repairs.": {
            "I’ll fix you.": {},
            "Find a mechanic.": {},
        },
        "I'm fine, thanks!": {},
    },
    "Can I help?": {
        "Yes, please!": {
            "What do you need?": {},
        },
        "Find a mechanic.": {},
    },
}

# Menu Structure
menu_tree = {
    "Dev Team": ["JS-730", "KDQ-959", "L419", "SMB-177", "Back"],
    "Info": ["Version: 1.13.3", "Back"],
    "[REDACTED]": None,
    "[LOREM]": ["SW 4: 1977", "SW 5: 1980", "SW 6: 1999", "SW 3: 2002", "ERROR: SITH", "Back"],
    "Prompts": prompt_tree,
}

# Global variables
main_menu = list(menu_tree.keys())
submenu = []
prompt_history = []
order_66_unlocked = False
roger_roger_unlocked = False
rat_unlocked = False

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
color_states = {"LED1": -1, "LED2": -1, "LED3": -1}  # Start with all LEDs off

# Dictionary to track the previous state of each sensor
sensor_states = {sensor: GPIO.LOW for sensor in TOUCH_SENSORS}

# Function to toggle color for a specific LED
def toggle_led_color(led):
    color_states[led] = (color_states[led] + 1) % len(COLORS)
    set_led_color(led, *COLORS[color_states[led]])


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
                    # Go back to the previous menu
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
        "Hello there": os.path.join(current_directory, "AUDIO_FILES/B1_hold_it.mp3"),
        "What happened?": "audio/what_happened.wav",
        "Never mind.": "audio/never_mind.wav",
        # Add more prompts and corresponding audio files here
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
    global order_66_unlocked, main_menu, menu_tree, rat_unlocked

    # Unlock "Order 66" if the rotary encoder turns 66 times
    if rotary_turns == 10 and not order_66_unlocked:
        order_66_unlocked = True
        main_menu.append("Order 66")
        menu_tree["Order 66"] = ["Eliminate all", "The Jedi", "Back"]
        print("[SECRET] Order 66 Unlocked!")

    if rotary_turns == -8 and button_clicks == 16 and not rat_unlocked:
        rat_unlocked = True
        main_menu.append("Rat")
        menu_tree["Rat"] = ["A wild Rat", "Has appeared", "Back"]
        print("[SECRET] Rat Unlocked!")

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
                    # Go back to the previous menu
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
                    print(f"[NAVIGATION] Going back to previous menu | Button Count: {button_clicks}")
                else:
                    # Return to the main menu
                    current_menu = main_menu
                    in_submenu = False
                    menu_index_top = 0
                    menu_index_bottom = 1 if len(main_menu) > 1 else 0
                    print(f"[NAVIGATION] Returning to Main Menu | Button Count: {button_clicks}")
            else:
                # Handle navigation within the prompt tree
                check_prompts()
        else:
            if selected_item == "Prompts":
                # Enter the Prompts submenu
                current_menu = list(prompt_tree.keys())  # Set current_menu to the list of prompt keys
                in_submenu = True
                menu_index_top = 0
                menu_index_bottom = 1 if len(current_menu) > 1 else 0
                print(f"[NAVIGATION] Entering {selected_item} submenu | Button Count: {button_clicks}")
            elif menu_tree.get(selected_item):  # Check if it has a submenu
                submenu = menu_tree[selected_item]
                current_menu = submenu
                in_submenu = True
                menu_index_top = 0
                menu_index_bottom = 1 if len(submenu) > 1 else 0
                print(f"[NAVIGATION] Entering {selected_item} submenu | Button Count: {button_clicks}")
            else:
                print(f"[ACTION] Selected {selected_item} | Button Count: {button_clicks}")

        update_display()
        time.sleep(0.3)  # Basic debounce



# Initialize LCD
LCD1602.init_lcd()
update_display()

try:
    while True:
        read_rotary()
        check_button()
        check_sensor()  # Check touch sensors and update LEDs
        time.sleep(0.01)  # Small delay to reduce CPU usage

except KeyboardInterrupt:
    GPIO.cleanup()
    LCD1602.send_command(0x01)  # Clear LCD
    print("[EXIT] Cleanup and Shutdown...")
