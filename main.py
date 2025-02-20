import RPi.GPIO as GPIO
import LCD1602
import file_1 as menu
import file_3 as motion  # Import the motion detection module

if __name__ == "__main__":
    try:
        # Wait for motion to occur once before proceeding
        motion.wait_for_motion()
        print("Motion detected! Initiating startup sequence...")
        
        # Once motion is detected, start the main menu loop
        menu.start_up()

        while True:
            menu.menu()  # Keep running menu indefinitely

    except KeyboardInterrupt:
        menu.shutdown()

