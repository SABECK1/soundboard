import os
from tkinter import messagebox
import yaml
from pydub import AudioSegment


def convert_to_wav():
    answer = messagebox.askyesno("Proceed?",
                                 "Do you wish to proceed? (FFMPEG required)\nThis will convert all .mp3 files in the default directory"
                                 " to .wav! This may also override files.")
    if not answer:
        return
    with open(r"bin\config.yaml", "r") as r:
        data = yaml.load(r, Loader=yaml.FullLoader)
        directory = data["settings"]["path"]
    for filename in os.listdir(directory):

        f = os.path.join(directory, filename).replace("\\", "/")
        # checking if it is a file
        if os.path.isfile(f) and os.path.splitext(f)[1] == ".mp3":
            try:
                print(f, os.path.splitext(f)[1])
                sound = AudioSegment.from_file(f)
                sound.export(os.path.splitext(f)[0] + ".wav", format="wav")
                os.remove(f)
            except FileNotFoundError:
                messagebox.showerror("Missing FFMPEG", "Please install FFMPEG, otherwise this feature will not work.")
                raise FileNotFoundError("FFMPEG IS NOT INSTALLED")

    messagebox.showinfo("Finished", "All files should be converted to wav now!")

