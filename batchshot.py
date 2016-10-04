#!/usr/bin/env python3

import argparse
import atexit
import os
import shutil
import subprocess
import tempfile

from tkinter import *
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

WIDTH, HEIGHT = 640, 360

OUTPUT_WIDTH, OUTPUT_HEIGHT = 1280, 720


class App:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack()

        self.master = master

        self.counter = 0

        self.label = Label(self.frame)
        self.label.pack(side=TOP)

        self.image_label = Label(self.frame)
        self.image_label.pack(side=TOP)

        self.set_image(None)

        # Initialize buttons
        btns = []
        btns.append(Button(self.frame, text="Next selection", command=self.next))
        btns.append(Button(self.frame, text="Undo", command=self.undo))
        btns.append(Button(self.frame, text="Save and exit", command=self.save))
        btns.append(Button(self.frame, text="Cancel", command=self.cancel))

        for index, b in enumerate(btns):
            b.pack(side=LEFT)

        self.tmpdir = tempfile.TemporaryDirectory()


    def set_image(self, imagefile):
        # Create blank background image
        background = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 0))

        # if imagefile
        if imagefile:
            img = Image.open(imagefile)

            # resize
            img_ratio = img.size[0] / img.size[1]
            if img_ratio > WIDTH/HEIGHT:
                new_size = (WIDTH, int(WIDTH/img_ratio))
            else:
                new_size = (int(HEIGHT*img_ratio), HEIGHT)
            img = img.resize(new_size, Image.ANTIALIAS)

            background.paste(img, ((WIDTH - img.size[0]) // 2, (HEIGHT - img.size[1]) // 2))


        self.img = ImageTk.PhotoImage(background)


        # Update text and image labels
        self.label.configure(text="Screenshots: " + str(self.counter))
        self.image_label.configure(image=self.img)


    def counter_to_string(self, index):
        return ("0000" + str(index))[-5:]


    def get_image_name(self, index):
        return os.path.join(self.tmpdir.name, self.counter_to_string(index) + ".png")


    def get_current_image_name(self):
        return self.get_image_name(self.counter)


    def refresh_image(self):
        if self.counter == 0:
            self.set_image(None)
        else:
            self.set_image(self.get_image_name(self.counter - 1))


    def next(self):
        self.master.withdraw()

        temp = tempfile.NamedTemporaryFile(suffix=".png")
        subprocess.run(["gm", "import", temp.name])

        gm_size = "%dx%d" % (OUTPUT_WIDTH, OUTPUT_HEIGHT)
        subprocess.run(["convert", temp.name, "-gravity", "center",
            "-resize", gm_size, "-extent", gm_size,
            self.get_current_image_name()])


        self.master.deiconify()

        self.counter += 1
        self.refresh_image()



    def undo(self):
        if self.counter == 0:
            messagebox.showinfo(message="Cannot undo because you have not made any selections yet.")
        else:
            self.counter -= 1
            os.remove(self.get_current_image_name())
            self.refresh_image()


    def save(self):
        savedir = filedialog.askdirectory()

        # If no directory chosen
        if not savedir:
            return

        destdir = os.path.join(savedir, "_batchshot_images")

        shutil.copytree(self.tmpdir.name, destdir)

        messagebox.showinfo(message="Saved to: %s" % destdir)
        self.frame.quit()

    def cancel(self):
        if messagebox.askyesno(message="Are you sure? No screenshots will be saved."):
            self.frame.quit()


root = Tk()
app = App(root)


@atexit.register
def cleanup():
    print("cleaning up")
    app.tmpdir.cleanup()


def main():
    root.mainloop()

if __name__ == "__main__":
    main()
