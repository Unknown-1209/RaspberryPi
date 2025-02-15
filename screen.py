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

# Menu Structure
menu_tree = {
    "Start": None,
    "Settings": ["Brightness", "Volume", "Back"],
    "Info": ["Version: 1.1.5", "Credits", "Back"],
    "Exit": None
}

main_menu = list(menu_tree.keys())
submenu = []
order_66_unlocked = False
roger_roger_unlocked = False

# Menu State Tracking
current_menu = main_menu
menu_index_top = 0
menu_index_bottom = 1 if len(main_menu) > 1 else 0
in_submenu = False
rotary_turns = 0  # Track rotary turns
button_clicks = 0 # Track the total button pushes

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Rotary Encoder State
clk_last_state = GPIO.input(CLK)
last_turn_time = time.time()  # Tracks last movement time
debounce_interval = 0.2  # Increase to make encoder less sensitive

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

def write_lcd(line1, line2):
    """Write text to the LCD, clearing previous text."""
    send_command(0x80)  # Move to first line
    for i in range(16):
        send_data(ord(line1[i]) if i < len(line1) else ord(' '))
    send_command(0xC0)  # Move to second line
    for i in range(16):
        send_data(ord(line2[i]) if i < len(line2) else ord(' '))

def update_display():
    """Update LCD with the current menu selection."""        
    
    line1 = current_menu[menu_index_top]
    line2 = current_menu[menu_index_bottom] if menu_index_bottom < len(current_menu) else ""
    write_lcd(line1, line2)
    print(f"[DISPLAY] {line1} / {line2}")



def check_unlocks():
    """Checks and unlocks any Easter eggs based on conditions."""
    global order_66_unlocked, main_menu, menu_tree

    # Unlock "Order 66" if the rotary encoder turns 66 times
    if rotary_turns == 5 and not order_66_unlocked:
        order_66_unlocked = True
        main_menu.append("Order 66")
        menu_tree["Order 66"] = ["End the Jedi", "Back"]
        print("[SECRET] Order 66 Unlocked!")


def read_rotary():
    """Reads rotary encoder input with reduced sensitivity."""
    global menu_index_top, menu_index_bottom, clk_last_state, last_turn_time, rotary_turns, order_66__unlocked, roger_roger_unlocked
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
    global current_menu, submenu, menu_index_top, menu_index_bottom, in_submenu, button_clicks

    if GPIO.input(SW) == GPIO.LOW:
        selected_item = current_menu[menu_index_top]
        button_clicks += 1
        
        if in_submenu:
            if selected_item == "Back":
                current_menu = main_menu
                in_submenu = False
                menu_index_top = 0
                menu_index_bottom = 1 if len(main_menu) > 1 else 0
                print(f"[NAVIGATION] Returning to Main Menu | Button Count: {button_clicks}")
            else:
                print(f"[ACTION] Selected {selected_item} in submenu | Button Count: {button_clicks}")
        else:
            if menu_tree.get(selected_item):  # Check if it has a submenu
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
    print("[EXIT] Cleanup and Shutdown...")

