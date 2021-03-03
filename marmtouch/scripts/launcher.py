from marmtouch.scripts.transfer_files import bulk_transfer_files

import tkinter as tk
from pathlib import Path
from functools import partial
import time

import click
import yaml


button_params = dict(height=3, width=20, relief=tk.FLAT, bg="gray99", fg="purple3", font="Dosis")

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class Launcher:
    def __init__(self,config_directory):
        self._init()
        self.config_directory = Path(config_directory)
        self.buttons = []
        self.job_selector()
        self.root.mainloop()
    
    def _recycle_buttons(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []
    
    def _add_button(self, text, command):
        button = tk.Button(self.scframe.interior, text=text, command=command, **button_params)
        button.pack(padx=10, pady=5, side=tk.TOP)
        self.buttons.append(button)

    def _init(self):
        self.root = tk.Tk()
        self.root.title("marmtouch launcher")
        self.root.geometry("300x700+0+0")
        self.root.configure(background="gray99")
        self.scframe = VerticalScrolledFrame(self.root)
        self.scframe.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
    
    def job_selector(self):
        self._recycle_buttons()
        jobs = [
            dict(text='Transfer', command=bulk_transfer_files),
            dict(text='Camera preview', command=self.preview_camera),
            dict(text='Tasks', command=self.task_selector),
            dict(text='Exit', command=self.exit)
        ]
        for job in jobs:
            self._add_button(**job)

    def preview_camera(self):
        from picamera import PiCamera
        camera = PiCamera()
        camera.start_preview()
        time.sleep(30)
        camera.stop_preview()

    def task_selector(self):
        self._recycle_buttons()
        task_list = [f for f in self.config_directory.iterdir() if f.is_dir()]
        for task in task_list:
            self._add_button(text=task.name, command=partial(self.config_selector, task))
        self._add_button(text='<<', command=self.job_selector)

    def config_selector(self, task):
        self._recycle_buttons()
        config_list = list(task.glob('*.yaml'))
        for config in config_list:
            self._add_button(text=config.stem, command=partial(self.run, task=task, config=config))
        self._add_button(text='<<', command=self.task_selector)

    def run(self, task, config):
        params = yaml.safe_load(open(config))
        session = time.strftime("%Y-%m-%d_%H-%M-%S")
        data_dir = Path('/home/pi/Touchscreen', session)
        if task.name in ['basic','random']:
            from marmtouch.experiments.basic import Basic
            Basic(data_dir, params).run()
        elif task.name in ['memory','cued']:
            from marmtouch.experiments.memory import Memory
            Memory(data_dir, params).run()
        self.exit()

    def exit(self):
        self.root.destroy()

default_config_directory = '/home/pi/configs/'
@click.command()
def launch():
    Launcher(default_config_directory)