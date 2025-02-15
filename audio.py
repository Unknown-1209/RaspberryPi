from pygame import mixer
import os
user = os.getlogin()
user_home = os.path.expanduser(f'~{user}')

mixer.init()

def main():
    mixer.music.load(f'{user_home}/Music/B1 hold it.mp3')
    mixer.music.set_volume(0.9)
    mixer.music.play()
    while True:
        pass# Don't do anything.

def destroy():
    mixer.music.stop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
