#!/usr/bin/env python3

import time
import smbus2 as smbus
import RPi.GPIO as GPIO

# I2C Address for 1602 LCD
LCD_ADDR = 0x27
BUS = smbus.SMBus(1)

# Rotary Encoder GPIO Pins
CLK = 17  # A
DT = 18   # B
SW = 27   # Button

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Rotary Encoder State
clk_last_state = GPIO.input(CLK)
last_turn_time = time.time()  # Tracks last movement time
debounce_interval = 0.75  # Increase to make encoder less sensitive


def write_word(data):
    """Write a byte to the I2C LCD with backlight control."""
    try:
        BUS.write_byte(LCD_ADDR, data | 0x08)  # Backlight ON
    except Exception as e:
        print(f"[ERROR] LCD Write Failed: {e}")

def send_command(command):
    """Send a command to the LCD."""
    write_word(command & 0xF0)
    write_word((command & 0xF0) | 0x04)
    write_word(command & 0xF0)
    write_word((command << 4) & 0xF0)
    write_word(((command << 4) & 0xF0) | 0x04)
    write_word((command << 4) & 0xF0)
    time.sleep(0.002)

def send_data(data):
    """Send a character to the LCD."""
    write_word((data & 0xF0) | 0x01)
    write_word(((data & 0xF0) | 0x05))
    write_word((data & 0xF0) | 0x01)
    write_word(((data << 4) & 0xF0) | 0x01)
    write_word((((data << 4) & 0xF0) | 0x05))
    write_word(((data << 4) & 0xF0) | 0x01)
    time.sleep(0.002)

def init_lcd():
    """Initialize LCD in 4-bit mode."""
    time.sleep(0.05)
    send_command(0x33)
    send_command(0x32)
    send_command(0x28)
    send_command(0x0C)
    send_command(0x01)
    time.sleep(0.1)

def write_lcd(text):
    """Write text to the LCD, clearing previous text."""
    send_command(0x80)
    for i in range(16):
        send_data(ord(text[i]) if i < len(text) else ord(' '))

def update_display():
    """Update LCD with the current menu selection."""
    write_lcd(current_menu[menu_index])
    if in_submenu:
        print(f"[SUBMENU] Now in: {current_menu[menu_index]}")
    else:
        print(f"[MENU] Now in: {current_menu[menu_index]}")


turn_count = 0 # Global variable to store total turns

def read_rotary():
    """Reads rotary encoder input with reduced sensitivity."""
    global menu_index, clk_last_state, last_turn_time, turn_count
    clk_state = GPIO.input(CLK)
    dt_state = GPIO.input(DT)
    current_time = time.time()

    if clk_state != clk_last_state and (current_time - last_turn_time) > debounce_interval:
        if dt_state != clk_state:
            menu_index = (menu_index + 1) % len(current_menu)  # Scroll down
            turn_count += 1 # Increment total turns
            print(f"[ROTARY] Moved DOWN: {current_menu[menu_index]} | Turns: {turn_count}")
        else:
            menu_index = (menu_index - 1) % len(current_menu)  # Scroll up
            turn_count -= 1 # Decrement total turns
            print(f"[ROTARY] Moved UP: {current_menu[menu_index]} | Turns: {turn_count}")
        
        last_turn_time = current_time  # Update last turn time
        update_display()
    
    clk_last_state = clk_state

def check_button():
    """Check if the encoder button is pressed."""
    global current_menu, submenu, menu_index, in_submenu

    if GPIO.input(SW) == GPIO.LOW:
        selected_item = current_menu[menu_index]
        
        if in_submenu:
            if selected_item == "Back":
                current_menu = main_menu
                in_submenu = False
                menu_index = 0
                print(f"[NAVIGATION] Returning to Main Menu")
            else:
                print(f"[ACTION] Selected {selected_item} in submenu")
        else:
            if menu_tree[selected_item]:  # Check if it has a submenu
                submenu = menu_tree[selected_item]
                current_menu = submenu
                in_submenu = True
                menu_index = 0
                print(f"[NAVIGATION] Entering {selected_item} submenu")
            else:
                print(f"[ACTION] Selected {selected_item}")

        update_display()
        time.sleep(0.1)  # Basic debounce




# Menu Structure
menu_tree = {
    "Start": None,
    "Settings": ["Brightness: 100", "Volume: 0", "Back"],
    "Info": ["Version: 1.0.5", "Back"],
    "Secret Menu": ["Hello", ("World")],
    "Exit": None
}

main_menu = list(menu_tree.keys())
submenu = []

# Menu State Tracking
current_menu = main_menu
menu_index = 0
in_submenu = False

# Initialize LCD
init_lcd()
update_display()

try:
    while True:
        read_rotary()
        check_button()
        time.sleep(0.01)  # Small delay to reduce CPU usage
except KeyboardInterrupt:
    GPIO.cleanup()
    send_command(0x01)  # Clear LCD
    print("\n[EXIT] Cleanup and Shutdown...")

