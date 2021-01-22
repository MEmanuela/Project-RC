import tkinter as tk

class basic_server(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#d4d4d4")
        self.controller = controller
        self.other_page = None

    def set_other_page(self, other_page):
        self.other_page = other_page

