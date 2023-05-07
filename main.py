import configparser
import os
import threading
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox, ttk

import customtkinter
import pygame
import pygame._sdl2 as sdl2
import pygame._sdl2.audio as sdl2_audio
import yaml
from PIL import Image, ImageTk
from pynput import keyboard
from tracker import Tracker
from downloader import Downloader
from wav_converter import convert_to_wav

pygame.init()

is_capture = False
device_names = list(sdl2_audio.get_audio_device_names(False))
print(device_names)
pygame.quit()


def open_yaml():
    with open(r"bin\config.yaml", "r") as r:
        data = yaml.load(r, Loader=yaml.FullLoader)
        return data

def dump_yaml(data):
    with open(r"bin\config.yaml", "w") as w:
        yaml.dump(data, w)


data = open_yaml()
sounddevice = data["settings"]["device"]

if sounddevice is None:
    with open(r"bin\config.yaml", "w") as w:
        data["settings"]["device"] = device_names[0]
        yaml.dump(data, w)

pygame.mixer.init(devicename=open_yaml()["settings"]["device"])






class SoundBoard:
    WIDTH = 600
    HEIGHT = 300

    def __init__(self):
        self.sound_path = None
        self.hotkey = None
        self.config = configparser.ConfigParser()
        self.root = customtkinter.CTk()
        self.root.geometry(f"{SoundBoard.WIDTH}x{SoundBoard.HEIGHT}")
        self.root.title("Soundboard by Ventior")
        self.root.resizable(False, False)
        status = StringVar()
        status.set("Paused")
        self.root.frame_left = customtkinter.CTkFrame(master=self.root,
                                                      width=180,
                                                      corner_radius=0)
        self.root.frame_left.grid(row=0, column=0, sticky="nswe", rowspan=2)

        # Config of frame_right and Scrollbar
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", background="#292929", bordercolor="#292929", arrowcolor="#292929",
                        troughcolor="#292929")
        self.root.frame_canvas = customtkinter.CTkFrame(master=self.root, corner_radius=0)#, background="#292929")
        self.root.frame_canvas.grid(row=0, column=2, pady=20, sticky="NEWS")

        self.canvas = Canvas(self.root.frame_canvas, highlightthickness=1, highlightbackground="#292929")
        self.canvas.grid(row=0, column=0, sticky="NEWS")

        self.scrollbar = ttk.Scrollbar(self.root.frame_canvas, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=4, sticky="NS")
        self.canvas.configure(yscrollcommand=self.scrollbar.set, bg="#292929")
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.root.frame_right = customtkinter.CTkFrame(master=self.canvas,highlightthickness=3,
                                                       highlightbackground="#292929", corner_radius=0)

        self.root.frame_right.grid(row=0, column=0)
        self.root.frame_right.bind("<Configure>", self.reset_scrollregion)

        self.canvas.create_window((0, 0), window=self.root.frame_right, anchor="nw")

        # Bottom Frame
        self.root.frame_bottom = customtkinter.CTkFrame(master=self.root, height=20, corner_radius=0)
        self.root.frame_bottom.grid(row=1, column=1, sticky="EW", columnspan=3)

        # All used pictures
        open_folder_png = ImageTk.PhotoImage(Image.open(r"bin\folder.png").convert("RGBA"))
        add_sound_png = ImageTk.PhotoImage(Image.open(r"bin\plus.png").convert("RGBA"))
        remove_sound_png = ImageTk.PhotoImage(Image.open(r"bin\minus.png").convert("RGBA"))
        settings_png = ImageTk.PhotoImage(Image.open(r"bin\settings-cogwheel-button.png").convert("RGBA"))
        download_png = ImageTk.PhotoImage(Image.open(r"bin\download.png").convert("RGBA"))
        converting_png = ImageTk.PhotoImage(Image.open(r"bin\converting.png").convert("RGBA"))
        stop_png = ImageTk.PhotoImage(Image.open(r"bin\stop-button.png").convert("RGBA"))
        info_png = ImageTk.PhotoImage(Image.open(r"bin\information.png").convert("RGBA"))
        self.play_png = ImageTk.PhotoImage(Image.open(r"bin\play-button.png").convert("RGBA"))
        self.delete_png = ImageTk.PhotoImage(Image.open(r"bin\delete.png").convert("RGBA"))

        customtkinter.CTkButton(master=self.root.frame_bottom, text="", height=30, width=30, image=self.play_png,
                                command=lambda: [Tracker.start_hotkey(), status.set("Running")]).grid(column=1, row=0,
                                                                                                      sticky="EN")

        customtkinter.CTkButton(master=self.root.frame_bottom, text="", height=30, width=30, image=stop_png,
                                command=lambda: [Tracker.stop_hotkey(), status.set("Paused")]).grid(column=2, row=0,
                                                                                                    sticky="EN")

        customtkinter.CTkLabel(master=self.root.frame_bottom, textvariable=status).grid(column=0, row=0)

        customtkinter.CTkButton(master=self.root.frame_left,
                                text="Open Folder",
                                image=open_folder_png,
                                command=self.open_folder,
                                corner_radius=0).grid(row=0, column=0, pady=5, columnspan=2, sticky="EW")

        customtkinter.CTkButton(master=self.root.frame_left,
                                text="Add Sound",
                                image=add_sound_png,
                                command=self.add_sound,
                                corner_radius=0).grid(row=1, column=0, pady=5, columnspan=2, sticky="EW")

        customtkinter.CTkButton(master=self.root.frame_left,
                                text="Delete Sound",
                                image=remove_sound_png,
                                command=self.remove_sound,
                                corner_radius=0).grid(row=2, column=0, pady=5, columnspan=2, sticky="EW")

        customtkinter.CTkButton(master=self.root.frame_left,
                                image=download_png, text="Download",
                                compound="left",
                                command=Downloader,
                                corner_radius=0).grid(row=3, column=0, pady=5, columnspan=2, sticky="EW")

        customtkinter.CTkButton(master=self.root.frame_left,
                                image=converting_png, text="Convert",
                                compound="left",
                                command=convert_to_wav,
                                corner_radius=0).grid(row=4, column=0, pady=5, columnspan=2, sticky="EW")

        customtkinter.CTkButton(master=self.root.frame_left,
                                image=settings_png, text="Settings",
                                compound="left",
                                command=self.open_settings,
                                corner_radius=0,
                                border_width=1,
                                border_color="black").grid(row=6, column=1, sticky="EWS")

        customtkinter.CTkButton(master=self.root.frame_left,
                                image=info_png, text="",
                                command=lambda: [webbrowser.open("https://github.com/VENTIOR")],
                                width=30,
                                corner_radius=0,
                                border_width=1,
                                border_color="black"
                                ).grid(row=6, column=0, sticky="WES")

        self.stop_btn = customtkinter.CTkButton(master=self.root.frame_canvas,
                                                image=stop_png,
                                                text="",
                                                command=pygame.mixer.music.stop)
        self.soundbar()
        self.table()
        self.change_mode()
        self.configure()

    def soundbar(self):
        data = open_yaml()

        def set_volume(value):
            pygame.mixer.music.set_volume(round(value) / 100)  # Arbeitet von 0 bis 1
            print(round(value) / 100)
            with open(r"bin\config.yaml", "w") as w:
                data["settings"]["volume"] = round(value) / 100
                yaml.dump(data, w)

        volume_var = IntVar()
        volume_var.set(data["settings"]["volume"] * 100)
        # Kann nur Ganze Zahlen weswegen from 0 to 1 nur 2 Steps besitzt
        soundbar = customtkinter.CTkSlider(master=self.root, orient="vertical", from_=0, to=100, command=set_volume,
                                           variable=volume_var)
        soundbar.grid(column=1, row=0, padx=10)

    def configure(self):
        self.root.frame_left.grid_rowconfigure(6, minsize=60, weight=1)
        self.root.frame_left.grid_columnconfigure(1, weight=1)
        self.root.frame_left.grid_columnconfigure(0, weight=1)
        self.root.frame_bottom.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.frame_canvas.rowconfigure(tuple(range(60)), weight=1)
        self.root.frame_canvas.columnconfigure(tuple(range(60)), weight=1)

    def table(self):
        data = open_yaml()

        SoundLabel = customtkinter.CTkLabel(master=self.root.frame_right,
                                            text="Sounds",
                                            width=20,
                                            height=25,
                                            fg_color="#3373B8",
                                            text_color="white",
                                            corner_radius=16)
        SoundLabel.grid(row=0, column=0, sticky="N", padx=26)
        HotkeyLabel = customtkinter.CTkLabel(master=self.root.frame_right,
                                             text="Hotkey",
                                             width=20,
                                             height=25,
                                             fg_color="#3373B8",
                                             text_color="white",
                                             corner_radius=16)
        HotkeyLabel.grid(row=0, column=1, sticky="N", padx=26)
        if len(data["sounds"]) < 9:
            self.scrollbar.grid_forget()
            self.stop_btn.place(relx=.92, width=30, height=30, rely=.87)
        else:
            self.scrollbar.grid(row=0, column=4, sticky="NS")
            self.stop_btn.place(x=350, width=30, height=30, rely=.87)

        def play_sound(idx):

            try:
                pygame.mixer.music.load(data["sounds"][f"sound0{idx}"]["path"])
                pygame.mixer.music.play()
            except (pygame.error, KeyError):
                messagebox.showerror("Corrupted or missing file",
                                     "For some reason this file cannot be played. Try another file!")
                return

        def delete_sound(idx):
            data = open_yaml()
            if data["settings"]["ignore_message"] == False:
                if not messagebox.askyesno("Attention",
                                           "This will delete the sound!\n(This message can be turned off via the settings menu!)"):
                    return
            name_of_sound_to_delete = self.sound_entry[idx].get()
            key_of_sound_to_delete = Tracker.getpath(data, name_of_sound_to_delete)[1]

            del data["sounds"][key_of_sound_to_delete]
            dump_yaml(data)
            self.update()

        self.name_row = dict()
        self.sound_entry = dict()
        self.hotkey_row = dict()
        self.hotkey_entry = dict()
        self.play_btn = dict()
        self.delete_btn = dict()
        try:

            length = data["sounds"].keys()
            for i, val in enumerate(length):
                try:
                    # data sounds als Liste um egal ob bspw Sound11 oben steht dieser auch herausgegriffen wird, da sonst sound{i} bspw nur bis 3 geht
                    # da die Länge 3 beträgt aber Sound11 und Sound1/2 drin sind
                    current_sound = list(data["sounds"])[i]
                    i += 1  # Erst hier +1 um row richtig zu formatieren aber auch das 0-te Element der Liste abgreifen zu können

                    self.name_row[i] = StringVar()
                    self.name_row[i].set(data["sounds"][current_sound]["name"])

                    self.sound_entry[i] = customtkinter.CTkEntry(master=self.root.frame_right, height=21,
                                                                 corner_radius=0,
                                                                 textvariable=self.name_row[i],
                                                                 state="disabled")
                    self.sound_entry[i].grid(row=i, column=0, sticky="W")
                    self.hotkey_row[i] = StringVar()
                    self.hotkey_row[i].set(data["sounds"][current_sound]["hotkey"])

                    self.hotkey_entry[i] = customtkinter.CTkEntry(master=self.root.frame_right, height=21,
                                                                  corner_radius=0,
                                                                  textvariable=self.hotkey_row[i],
                                                                  state="disabled")
                    self.hotkey_entry[i].grid(row=i, column=1, sticky="W")

                    self.play_btn[i] = customtkinter.CTkButton(master=self.root.frame_right, corner_radius=0,
                                                               image=self.play_png, width=21, height=20, border_width=1,
                                                               border_color="black",
                                                               command=lambda i=i: play_sound(i), text="")
                    self.play_btn[i].grid(row=i, column=2, padx=4)

                    self.delete_btn[i] = customtkinter.CTkButton(master=self.root.frame_right, corner_radius=0,
                                                                 image=self.delete_png, width=21, height=20,
                                                                 border_width=1,
                                                                 border_color="black", text="",
                                                                 command=lambda i=i: delete_sound(i))
                    self.delete_btn[i].grid(row=i, column=3, padx=4)


                except KeyError:
                    continue
        except (TypeError, IndexError, AttributeError):
            print("No Sound yet added")

    def open_settings(self):
        def ask_folder_settings():
            path = data["settings"]["path"]
            self.file_directory = filedialog.askdirectory(initialdir=path)
            self.settings_win.lift()

        data = open_yaml()
        device = data["settings"]["device"]
        ignore_message = data["settings"]["ignore_message"]
        lightmode = data["settings"]["lightmode"]

        self.settings_win = customtkinter.CTkToplevel()
        self.settings_win.title("Settings")
        self.settings_win.attributes("-toolwindow", True)

        customtkinter.CTkButton(master=self.settings_win,
                                command=ask_folder_settings,
                                text="Set Default Directory").grid(row=1, column=0, padx=10, pady=5, columnspan=2,
                                                                   sticky="W")

        self.dropdownvar = StringVar()

        self.dropdownvar.set(device)


        OptionMenu(self.settings_win, self.dropdownvar, *device_names).grid(row=0, column=1, padx=10, pady=5)

        customtkinter.CTkLabel(master=self.settings_win, text="Restart needed when\nchanging this setting").grid(row=0,
                                                                                                                 column=0)

        self.message = customtkinter.CTkSwitch(master=self.settings_win,
                                               text="Disable Warningmessage when deleting sound")
        self.message.grid(row=3, column=0, padx=10, pady=5, columnspan=2, sticky="W")

        self.mode = customtkinter.CTkSwitch(master=self.settings_win, text="Light Mode", command=self.change_mode)
        self.mode.grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky="W")

        if lightmode == 1:
            self.mode.toggle()

        if ignore_message == 1:
            self.message.toggle()

        self.settings_win.protocol("WM_DELETE_WINDOW", self.write_config_settings)

    def add_sound(self):
        self.path_var = StringVar()
        self.path_var.set("Path to Sound")
        key_combination = StringVar()
        current = set()
        save = set()

        def sound_path():

            data = open_yaml()
            path = data["settings"]["path"]
            self.sound_path = filedialog.askopenfilename(initialdir=path)
            self.add_sounds_win.lift()
            self.path_var.set(self.sound_path)

        def on_press(key):
            try:
                current.add(key.char)
                save.add(key.char)
            except AttributeError:
                current.add(str(key)[4:])
                save.add(str(key))
            try:
                self.hotkey = (" + ".join(sorted(save)))
                key_combination.set(" + ".join(sorted(current)))
            except TypeError:
                key_combination.set("#ERROR")

        def on_release(key):
            current.clear()
            save.clear()
            for thread in threading.enumerate():
                print(thread)

            if key == keyboard.Key.esc:
                # Stop listener
                return False

        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)

        def focus_out(event):
            self.add_sounds_win.focus()

        self.add_sounds_win = customtkinter.CTkToplevel()
        self.add_sounds_win.title("Add a Sound")
        self.add_sounds_win.attributes("-toolwindow", True)
        self.add_sounds_win.frame = customtkinter.CTkFrame(master=self.add_sounds_win,
                                                           width=self.add_sounds_win.winfo_width(),
                                                           height=self.add_sounds_win.winfo_height())
        self.sound_name = customtkinter.CTkEntry(master=self.add_sounds_win,
                                                 corner_radius=0)
        self.sound_name.grid(row=0, column=0, columnspan=3, sticky="EW")
        self.sound_name.bind("<Return>", focus_out)

        self.sound_path_entry = customtkinter.CTkEntry(master=self.add_sounds_win,
                                                       corner_radius=0, state=DISABLED,
                                                       textvariable=self.path_var).grid(row=1,
                                                                                        column=0, columnspan=3,
                                                                                        sticky="EW")
        customtkinter.CTkLabel(master=self.add_sounds_win, corner_radius=0,
                               text="Sound Name").grid(row=0, column=3, columnspan=3, sticky="EW")

        customtkinter.CTkEntry(master=self.add_sounds_win,
                               corner_radius=0, state=DISABLED, textvariable=key_combination).grid(row=2,
                                                                                                   column=0,
                                                                                                   columnspan=4,
                                                                                                   sticky="EW")
        customtkinter.CTkButton(master=self.add_sounds_win, corner_radius=0, text="...",
                                command=sound_path, border_width=1, border_color="black").grid(row=1, column=3,
                                                                                               columnspan=3,
                                                                                               sticky="EW")

        customtkinter.CTkButton(master=self.add_sounds_win, corner_radius=0, border_width=1, border_color="black",
                                text="Set Hotkey", command=listener.start).grid(row=2, column=4)

        customtkinter.CTkButton(master=self.add_sounds_win, corner_radius=0, border_width=1, border_color="black",
                                text="Confirm Hotkey", command=listener.stop).grid(row=2, column=5)

        customtkinter.CTkButton(master=self.add_sounds_win, corner_radius=0, border_width=1, border_color="black",
                                text="Confirm Sound", command=self.write_config_sounds).grid(row=3, column=0,
                                                                                             columnspan=3, sticky="NWE")

        customtkinter.CTkButton(master=self.add_sounds_win, corner_radius=0, border_width=1, border_color="black",
                                text="Cancel", command=self.add_sounds_win.destroy).grid(row=3, column=3, columnspan=3,
                                                                                         sticky="NEW")

        self.add_sounds_win.protocol("WM_DELETE_WINDOW", self.write_config_sounds)

    def remove_sound(self):
        self.remove_sound_win = customtkinter.CTkToplevel()
        self.remove_sound_win.attributes("-toolwindow", True)
        self.remove_sound_win.title("Remove Sound")
        customtkinter.CTkLabel(master=self.remove_sound_win, text="Name of Sound to Remove:").grid(row=0)
        self.sound_to_remove = customtkinter.CTkEntry(master=self.remove_sound_win)
        self.sound_to_remove.grid(row=1)
        customtkinter.CTkButton(master=self.remove_sound_win, text="Confirm",
                                command=self.write_config_remove).grid(row=2, pady=2)

    @staticmethod
    def open_folder():
        data = open_yaml()
        path = data["settings"]["path"]
        os.startfile(path)

    def write_config_settings(self):
        data = open_yaml()
        try:
            data["settings"]["path"] = self.file_directory
        except AttributeError:
            data["settings"]["path"] = "sounds_default"
            print("No path given")

        if self.dropdownvar.get() == "Preferred Audio Device":
            data["settings"]["device"] = device_names[0]
        else:
            data["settings"]["device"] = self.dropdownvar.get()

        if self.message.get() == 1:
            data["settings"]["ignore_message"] = True
        else:
            data["settings"]["ignore_message"] = False

        data["settings"]["lightmode"] = self.mode.get()
        dump_yaml(data)

        self.settings_win.destroy()

    def write_config_sounds(self):
        sound_path = self.sound_path

        if sound_path == "":
            messagebox.showerror("Necessary information missing", "You did not choose a path for your sound!")
            self.path_var.set("Path to Sound")
            self.add_sounds_win.lift()
            return
        if sound_path is None:  # For some reason or None didnt work
            messagebox.showerror("Necessary information missing", "You did not choose a path for your sound!")
            self.path_var.set("Path to Sound")
            self.add_sounds_win.lift()
            return
        if not os.path.splitext(sound_path)[1] == ".wav":
            print(sound_path)
            messagebox.showerror("That is not a sound file", "It seems that the file you've given is not a wav!")
            self.add_sounds_win.lift()
            return

        if not self.sound_name.get():
            sound_name = os.path.basename(self.sound_path)
        else:
            sound_name = self.sound_name.get()

        data = open_yaml()
        sounds = data['sounds']

        new_sound = dict(path=sound_path, name=sound_name, hotkey=self.hotkey)

        try:
            result1 = any(sound_name in d.values() for d in sounds.values())
            result2 = any(self.hotkey in d.values() for d in sounds.values())

            if result1:
                messagebox.showerror("Sound already added!",
                                     "It seems you accidentally added a sound with the same name!")
                return

            if result2 and self.hotkey is not None:
                messagebox.showerror("Sound already added!",
                                     "It seems you accidentally added a sound with the same hotkey!")
                return

        except AttributeError:
            print("No Sounds yet added")

        idx = 0
        while True:
            idx += 1
            if idx < 10:
                key = f'sound0{idx}'
            else:
                key = f'sound{idx}'

            try:
                if key not in sounds:
                    print(key)
                    sounds[key] = new_sound
                    print(sounds[key])
                    break
            except TypeError:  # if
                data["sounds"] = {f'sound{idx}': new_sound}
                break
        dump_yaml(data)
        Tracker.data = open_yaml()  # After writing a sound, data needs to be renewed

        self.add_sounds_win.destroy()
        self.update()

    def write_config_remove(self):
        data = open_yaml()

        try:
            del data["sounds"][
                Tracker.getpath(data, self.sound_to_remove.get())[1]]  # Get Sound[x] of name and delete it
        except TypeError:
            messagebox.showerror("Unknown Sound!", "Are you sure you got the name of the Sound right?")
            self.remove_sound_win.lift()
            return

        dump_yaml(data)
        self.remove_sound_win.destroy()
        self.update()

    def change_mode(self):
        # Reagiert auf sofortige Änderungen die nicht der config sofort zugeschrieben werden (lightmode ohne schreiben der config)
        try:
            if self.mode.get() == 1:
                self.canvas.configure(bg="#FFFFFF", highlightbackground="#FFFFFF")
                self.root.frame_canvas.configure(fg_color="#FFFFFF")
                self.root.frame_right.configure(highlightbackground="#FFFFFF")
                customtkinter.set_appearance_mode("light")
            else:
                customtkinter.set_appearance_mode("dark")
                self.canvas.configure(bg="#292929", highlightbackground="#292929")
                self.root.frame_canvas.configure(fg_color="#292929")
                self.root.frame_right.configure(highlightbackground="#292929")
        except AttributeError:
            data = open_yaml()
            self.lightmode = data["settings"]["lightmode"]
            if self.lightmode == 1:
                self.canvas.configure(bg="#FFFFFF", highlightbackground="#FFFFFF")
                self.root.frame_canvas.configure(fg_color="#FFFFFF")
                self.root.frame_right.configure(highlightbackground="#FFFFFF")
                customtkinter.set_appearance_mode("light")
            else:
                self.canvas.configure(bg="#292929", highlightbackground="#292929")
                self.root.frame_right.configure(highlightbackground="#292929")
                customtkinter.set_appearance_mode("dark")

    def reset_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update(self):
        for i in range(1, len(self.name_row) + 1):  # Delete all textvariables and according widgets/entries
            try:
                self.sound_entry[i].destroy()
                self.hotkey_entry[i].destroy()
                self.play_btn[i].destroy()
                self.delete_btn[i].destroy()
            except KeyError:
                continue
        self.table()
        self.root.update()

    def start(self):
        Tracker()
        self.root.mainloop()


if __name__ == "__main__":
    app = SoundBoard()
    app.start()
