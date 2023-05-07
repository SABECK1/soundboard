import pygame
import yaml
from pynput import keyboard


class Tracker:
    listening = False
    save = set()
    hotkey = ""
    with open(r"bin\config.yaml", "r") as r:
        data = yaml.load(r, Loader=yaml.FullLoader)
    try:
        pygame.mixer.init(devicename=data["settings"]["device"])
        print("INIT SUCCESSFUL")
    except:
        print("Error Initialization")
        pass

    def __init__(self):
        pygame.mixer.init()
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()

    @staticmethod
    def on_press(key):
        if Tracker.listening:
            try:
                Tracker.save.add(key.char)
            except AttributeError:
                Tracker.save.add(str(key))
            try:
                Tracker.hotkey = (" + ".join(sorted(Tracker.save)))
            except TypeError:
                pass

            config_keys = Tracker.getpath(Tracker.data, Tracker.hotkey)
            if config_keys:
                soundX = config_keys[1]

                pygame.mixer.music.load(Tracker.data["sounds"][soundX]["path"])
                pygame.mixer.music.play()

    @staticmethod
    def on_release(key):
        if Tracker.listening:
            try:
                Tracker.save.remove(key.char)
            except (AttributeError, KeyError):
                Tracker.save.clear()

    @staticmethod
    def start_hotkey():
        Tracker.listening = True

    @staticmethod
    def stop_hotkey():
        Tracker.listening = False

    @staticmethod
    def getpath(nested_dict, value, prepath=()):
        for k, v in nested_dict.items():
            path = prepath + (k,)
            if v == value:  # found value
                return path
            elif hasattr(v, 'items'):  # v is a dict
                p = Tracker.getpath(v, value, path)  # recursive call
                if p is not None:
                    return p
