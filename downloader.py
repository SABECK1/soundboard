import os
import re
from tkinter import messagebox, StringVar
from pydub import AudioSegment
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
    'outtmpl': f"{ydl_path}" + r"/%(title)s.%(ext)s",
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192', }],
    'restrictfilenames': True,
    'forcefilename': True
}


class Downloader:
    WIDTH = 300
    HEIGHT = 140

    def __init__(self):
        def on_focus_in_link(event):
            self.input_link.set("")

        def on_focus_in_timeframe_start(event):
            self.input_timeframe_start.set("")

        def on_focus_in_timeframe_stop(event):
            self.input_timeframe_stop.set("")

        self.starttime_str = "Starttime in Seconds"
        self.stoptime_str = "Stoptime in Seconds"
        self.input_link = StringVar()
        self.input_timeframe_start = StringVar()
        self.input_timeframe_start.set(self.starttime_str)
        self.input_timeframe_stop = StringVar()
        self.input_timeframe_stop.set(self.stoptime_str)

        self.download_win = customtkinter.CTkToplevel()
        self.download_win.title("Download a Sound")
        self.download_win.resizable(False, False)
        self.download_win.attributes("-toolwindow", True)
        self.input_link.set(self.download_win.clipboard_get())
        self.download_win.geometry(f"{Downloader.WIDTH}x{Downloader.HEIGHT}")
        self.download_win.columnconfigure(0, weight=1)
        self.download_win.columnconfigure(1, weight=1)
        customtkinter.CTkLabel(master=self.download_win, text="Post your downloadlink (FFMPEG required)").grid(row=0,
                                                                                                               column=0,
                                                                                                               columnspan=2)
        customtkinter.CTkLabel(master=self.download_win, text="and optionally a timeframe to download").grid(row=3,
                                                                                                             column=0,
                                                                                                             columnspan=2)
        self.link = customtkinter.CTkEntry(master=self.download_win, textvariable=self.input_link)
        self.link.grid(row=1, column=0, sticky="NEWS",
                       columnspan=2)

        self.start_timeframe = customtkinter.CTkEntry(master=self.download_win, textvariable=self.input_timeframe_start)
        self.start_timeframe.grid(row=4, column=0, sticky="NEWS")

        self.stop_timeframe = customtkinter.CTkEntry(master=self.download_win, textvariable=self.input_timeframe_stop)
        self.stop_timeframe.grid(row=4, column=1, sticky="NEWS")
        customtkinter.CTkButton(master=self.download_win, text="Confirm",
                                border_width=1, border_color="black",
                                corner_radius=0, command=self.confirm).grid(row=5, column=0, sticky="NEWS")

        customtkinter.CTkButton(master=self.download_win, text="Cancel",
                                border_width=1, border_color="black",
                                corner_radius=0, command=self.cancel).grid(row=5, column=1, sticky="NEWS")

        self.link.bind("<FocusIn>", on_focus_in_link)
        self.start_timeframe.bind("<FocusIn>", on_focus_in_timeframe_start)
        self.stop_timeframe.bind("<FocusIn>", on_focus_in_timeframe_stop)

    def cancel(self):
        self.download_win.destroy()

    def confirm(self):
        def on_focus_in(event):
            self.input_timeframe_start.set("")

        self.link.get()
        if not re.match("^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))"
                        "(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$", self.link.get()):
            messagebox.showerror("Enter a Youtube link", "This doesn't look like a Youtubelink!"
                                                         " Post a real link.")
            return
        start_time = None
        stop_time = None
        if self.input_timeframe_start.get() is not None and self.input_timeframe_start.get() != self.starttime_str:
            if not self.input_timeframe_start.get().isdigit():
                messagebox.showerror("That is not a number", "The timeframe you specified doesn't seem to be a number!")
                return
            else:
                start_time = int(self.input_timeframe_start.get()) * 1000

        if self.input_timeframe_stop.get() and self.input_timeframe_stop.get() != self.stoptime_str:
            if not self.input_timeframe_stop.get().isdigit():
                messagebox.showerror("That is not a number", "The timeframe you specified doesn't seem to be a number!")
                return
            else:
                stop_time = int(self.input_timeframe_stop.get()) * 1000

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link.get()])
                result = ydl.extract_info(str(self.link.get()), download=False)  #
                filename = ydl.prepare_filename(result)
                filename = f"{filename[:-4]}wav"  # prepare filename uses webm format https://github.com/ytdl-org/youtube-dl/issues/13750#issuecomment-466048967 doesnt fix problem
        except:
            messagebox.showerror("Error", "Download failed. It seems you haven't installed FFMPEG")
        print(filename)
        if os.path.exists(filename):
            sound = AudioSegment.from_wav(filename)
            if not start_time and not stop_time:
                sound_chunk = sound
            elif not start_time:
                sound_chunk = sound[:stop_time]
            elif not stop_time:
                sound_chunk = sound[start_time:]
            else:
                sound_chunk = sound[start_time:stop_time]
            sound_chunk.export(filename, format="wav")
        else:
            messagebox.showerror("Something went wrong!",
                                 "Something went wrong when cutting the audio! Try again.")
        self.download_win.destroy()
