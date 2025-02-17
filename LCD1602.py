"""
    Author: Unknown-1209
    More than likely has bugs but it does it's job
    Created: 02/01/2025
"""

#!/usr/bin/env python3

import time
import smbus2 as smbus

# I2C Address for 1602 LCD
LCD_ADDR = 0x27
BUS = smbus.SMBus(1)

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

