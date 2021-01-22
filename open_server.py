
import tkinter as tk
from tkinter import *
from basic_server import basic_server
import threading


class open_server(basic_server):
    def __init__(self, parent, controller):
        basic_server.__init__(self, parent, controller)
        self.init_window()

    def init_window(self, button_bg='#B0C4DE', button_fg='#000000', label_bg='#B0C4DE', label_txt='black', txt_color='#00FF41', text_widget_width=60):
        # DHCP OPT
        frame_configuration = tk.Frame(master=self, bg="#3d3d3d")
        frame_configuration.pack(side = tk.LEFT)
        tk.Button(frame_configuration, text="DHCP-OPT", width=25, bg=button_bg, fg=button_fg, command=lambda: self.controller.show_frame("configuration_server")).grid(row=0, column=0, padx=1, pady=1)
        frame_configuration.place(x=100, y=90)

        #CLIENTS
        frame_clients = tk.Frame(master=self, bg="#3d3d3d")
        tk.Button(frame_clients, text="CLIENTS", width=25, bg=button_bg, fg=button_fg, command=self.show_clients).grid(row=1, column=0, padx=1, pady=1)
        frame_clients.place(x=100, y=580)

        # DHCP-RES
        frame_res = tk.Frame(master=self, bg="#3d3d3d")
        tk.Button(frame_res, text="DHCP-RES", width=25, bg=button_bg, fg=button_fg,command=lambda: self.controller.show_frame("dhcp_res")).grid(row=1, column=2, padx=1, pady=1)
        frame_res.place(x=500, y=580)

        # DHCP-START
        frame_ss = tk.Frame(master=self, bg="#3d3d3d")
        frame_ss.place(x=500, y=90)
        self.start_button =  tk.Button(frame_ss, text="START",  width=22, bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.start_server).grid(row=1, column=2, padx=1, pady=1)

        #DHCP-STOP
        frame_ss = tk.Frame(master=self, bg="#3d3d3d")
        frame_ss.place(x=500, y=120)
        self.stop_button = tk.Button(frame_ss, text="STOP",  width=22, bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.stop_server).grid(row=1, column=2, padx=1, pady=1)

        #Server status
        status_viewer_frame = tk.Frame(master=self, bg='#d4d4d4')
        status_viewer_frame.pack(side=tk.BOTTOM, expand=1)
        status_viewer_frame.place(x=100, y=180)
        status_viewer_frame_label = tk.LabelFrame(status_viewer_frame, bg=label_bg, fg='black',  font=self.controller.text_label_title)
        status_viewer_frame_label.grid(row=1, column=0)
        self.status_viewer_pool_text = tk.Text(status_viewer_frame_label, height=20, width=70, bg="#f0f0f0", fg='black')
        #self.status_viewer_pool_text.config(state='disabled')
        status_viewer_pool_scroll_x = tk.Scrollbar(status_viewer_frame_label, command=self.status_viewer_pool_text.xview, orient = 'horizontal')
        status_viewer_pool_scroll_y = tk.Scrollbar(status_viewer_frame_label, command=self.status_viewer_pool_text.yview, orient ='vertical')
        self.status_viewer_pool_text['xscrollcommand'] = status_viewer_pool_scroll_x.set
        self.status_viewer_pool_text['yscrollcommand'] = status_viewer_pool_scroll_y.set
        self.status_viewer_pool_text.grid(row=0, column=0, sticky=tk.N + tk.S)
        status_viewer_pool_scroll_x.grid(row=1, columnspan=2, sticky=tk.N + tk.E + tk.W)
        status_viewer_pool_scroll_y.grid(row=0, column=2, sticky=tk.N + tk.S + tk.W)
        self.status_viewer_pool_text.tag_configure('text', font=('Ariel, 10'))

    def start_server(self):
        self.controller.start_server()

    def activate_start_button(self):
        while self.controller.dhcp_server.shut_down is not True:
            pass

    def stop_server(self):
        self.controller.stop_server()
        activate_btn_thread = threading.Thread(target=self.activate_start_button)
        activate_btn_thread.daemon = True
        activate_btn_thread.start()

    def show_clients(self):
        self.controller.dhcp_server.savePool()
        self.controller.dhcp_server.debug("Check pool.json")