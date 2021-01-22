import tkinter as tk
from tkinter import font as tkfont
from DHCP_server import DHCP_Server
from active_clients import active_clients
from configuration_server import configuration_server
from dhcp_res import dhcp_res
from open_server import open_server
import threading 

class DHCP_Server_GUI(tk.Tk):
    def __init__(self, *args, **wargs):
        tk.Tk.__init__(self, *args, **wargs)
        self.title_font = tkfont.Font(family='Times', size=20)
        self.text_label_title = tkfont.Font(family='Arial', size=10)
        self.button_text_font = tkfont.Font(family='Arial', size=10)
        self.title("DHCP SERVER")
        container = tk.Frame(self)
        container.pack(side="top", fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.dhcp_server = DHCP_Server(self)
        for x in [open_server, configuration_server, active_clients, dhcp_res]:
            page_name = x.__name__
            frame = x(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.frames['open_server'].set_other_page(self.frames['configuration_server'])
        self.frames['configuration_server'].set_other_page(self.frames['open_server'])
        self.show_frame("open_server")

    def start_server(self):
        self.server_thread = threading.Thread(target=self.dhcp_server.startServer)
        self.server_thread.daemon = True
        self.dhcp_server.setFlag(True)
        self.server_thread.start()

    def stop_server(self):
        self.dhcp_server.setFlag(False)


    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def gui_exit(self):
        self.dhcp_server.debug('Stopping Server')
        self.dhcp_server.setFlag(1)
        exit()