import os
import re
from tkinter import messagebox, StringVar

import customtkinter
import yaml
import youtube_dl

with open(r"bin\config.yaml", "r") as r:
    data = yaml.load(r, Loader=yaml.FullLoader)
    ydl_path = data["settings"]["path"]
    directory = ydl_path
    if not os.path.exists(directory):
        os.makedirs(directory)

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f"{ydl_path}" + r"\%(title)s-%(id)s.%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
}


class Downloader:
    WIDTH = 350
    HEIGHT = 60

    def __init__(self):
        def on_focus_in(event):
            self.input.set("")

        self.input = StringVar()

        self.download_win = customtkinter.CTkToplevel()
        self.input.set(self.download_win.clipboard_get())
        # self.download_win.geometry(f"{Downloader.WIDTH}x{Downloader.HEIGHT}")
        self.download_win.columnconfigure(0, weight=1)
        customtkinter.CTkLabel(master=self.download_win, text="Post your downloadlink (FFMPEG required)").grid(row=0,
                                                                                                          column=0,
                                                                                                          columnspan=2)
        self.link = customtkinter.CTkEntry(master=self.download_win, textvariable=self.input)
        self.link.grid(row=1, column=0, sticky="NEWS",
                       columnspan=2)
        customtkinter.CTkButton(master=self.download_win, text="Confirm",
                                border_width=1, border_color="black",
                                corner_radius=0, command=self.confirm).grid(row=2, column=0)

        customtkinter.CTkButton(master=self.download_win, text="Cancel",
                                border_width=1, border_color="black",
                                corner_radius=0, command=self.cancel).grid(row=2, column=1)

        self.link.bind("<FocusIn>", on_focus_in)

    def cancel(self):
        self.download_win.destroy()

    def confirm(self):
        self.link.get()
        if not re.match("^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
                        "(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$", self.link.get()):
            messagebox.showerror("Enter a Youtube link", "This doesn't look like a Youtubelink!"
                                                         " Post a real link.")
            return

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link.get()])
        except:
            messagebox.showerror("Error", "Download failed. It seems you haven't installed FFMPEG")
        self.download_win.destroy()