import tkinter as tk
from tkinter import messagebox, ttk
from basic_server import basic_server


class active_clients(basic_server):
    def __init__(self, parent, controller):
        basic_server.__init__(self, parent, controller)
        self.init_window()

    def init_window(self, button_bg='#E0E0E0', button_fg='#000000', label_bg='#303030', label_txt='black',
                    txt_color='#00FF41', text_widget_width=60):
        # return home
        return_frame = tk.Frame(master=self, bg="#050505")
        return_frame.pack(side=tk.TOP, expand=0)
        return_frame.place(x=20, y=20)
        tk.Grid.columnconfigure(return_frame, 0, weight=1)
        tk.Button(return_frame, text="Return", width=15, bg=button_bg, fg=button_fg,
                  font=self.controller.button_text_font,
                  command=lambda: self.controller.show_frame("open_server")).grid(row=0, column=0)


        # ACTIVE CLIENTS
        tk.Label(master=self, text='Active clients', bg=self["bg"], fg=label_txt, font=self.controller.title_font).pack(
            side=tk.TOP, anchor='n')

        address_pool_viewer_frame = tk.Frame(master=self, bg='#d4d4d4')
        address_pool_viewer_frame.pack(side=tk.BOTTOM, expand=1)
        address_pool_viewer_frame.place(x=100, y=180)
        address_pool_viewer_label = tk.LabelFrame(address_pool_viewer_frame, bg=label_bg, fg='black',font=self.controller.text_label_title)
        address_pool_viewer_label.grid(row=1, column=0)
        self.ip_address_pool_text = tk.Text(address_pool_viewer_label, height=20, width=70, bg="#f0f0f0", fg='black')
        self.ip_address_pool_text.config(state='disabled')
        ip_address_pool_scroll_x = tk.Scrollbar(address_pool_viewer_label, command=self.ip_address_pool_text.xview, orient='horizontal')
        ip_address_pool_scroll_y = tk.Scrollbar(address_pool_viewer_label, command=self.ip_address_pool_text.yview, orient='vertical')
        self.ip_address_pool_text['xscrollcommand'] = ip_address_pool_scroll_x.set
        self.ip_address_pool_text['yscrollcommand'] = ip_address_pool_scroll_y.set
        self.ip_address_pool_text.grid(row=0, column=0, sticky=tk.N + tk.S)
        ip_address_pool_scroll_x.grid(row=1, columnspan=2, sticky=tk.N + tk.E + tk.W)
        ip_address_pool_scroll_y.grid(row=0, column=2, sticky=tk.N + tk.S + tk.W)
        self.ip_address_pool_text.tag_configure('text', font=('Ariel, 10'))
