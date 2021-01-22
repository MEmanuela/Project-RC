import tkinter as tk
from tkinter import messagebox, ttk
from basic_server import basic_server
import re


class dhcp_res(basic_server):
    def __init__(self, parent, controller):
        basic_server.__init__(self, parent, controller)
        self.init_window()

    def init_window(self, button_bg='#E0E0E0', button_fg='#000000', label_bg='#f0f0f0', label_txt='black',
                    txt_color='#000000', text_widget_width=60):
        # return home
        return_frame = tk.Frame(master=self, bg="#050505")
        return_frame.pack(side=tk.TOP, expand=0)
        return_frame.place(x=20, y=20)
        tk.Grid.columnconfigure(return_frame, 0, weight=1)
        tk.Button(return_frame, text="Return", width=15, bg=button_bg, fg=button_fg,
                  font=self.controller.button_text_font,
                  command=lambda: self.controller.show_frame("open_server")).grid(row=0, column=0)


        # Reservations
        tk.Label(master=self, text='', bg=self["bg"], fg=label_txt, font=self.controller.title_font).pack(
            side=tk.TOP, anchor='n')
        
        configuration_frame = tk.Frame(master=self, bg = "#d4d4d4")
        configuration_frame.pack(side=tk.LEFT)
        configuration_frame.place(x=180, y=100)

        ip_address_frame = tk.LabelFrame(configuration_frame,text = 'Reservation', bg=label_bg, fg=label_txt,  font=self.controller.text_label_title)
        ip_address_frame.grid(row=2, column=0, padx=0, pady=0)
        tk.Label(ip_address_frame, text='IP Address', fg=txt_color, font=self.controller.button_text_font).grid(row=2,  column=0)
        self.ip_address_entry = tk.Entry(ip_address_frame, width=50)
        self.ip_address_entry.grid(row=2, column=10,  padx=10, pady=10)
        tk.Label(ip_address_frame, text='MAC', fg=txt_color, font=self.controller.button_text_font).grid(row=4,  column=0)
        self.mac_entry = tk.Entry(ip_address_frame, width=50)
        self.mac_entry.grid(row=4, column=10,  padx=10, pady=10)
        tk.Button(ip_address_frame, text='Add reservation', bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.addReservation).grid(row=10, columnspan=12)


        address_pool_viewer_frame = tk.Frame(master=self, bg='#d4d4d4')
        address_pool_viewer_frame.pack(side=tk.BOTTOM, expand=1)
        address_pool_viewer_frame.place(x=100, y=250)
        address_pool_viewer_label = tk.LabelFrame(address_pool_viewer_frame, bg=label_bg, fg='black',
                                                  font=self.controller.text_label_title)
        address_pool_viewer_label.grid(row=1, column=0)
        self.ip_address_pool_text = tk.Text(address_pool_viewer_label, height=20, width=70, bg="#f0f0f0", fg='black')
        #self.ip_address_pool_text.config(state='disabled')
        ip_address_pool_scroll_x = tk.Scrollbar(address_pool_viewer_label, command=self.ip_address_pool_text.xview,
                                                orient='horizontal')
        ip_address_pool_scroll_y = tk.Scrollbar(address_pool_viewer_label, command=self.ip_address_pool_text.yview,
                                                orient='vertical')
        self.ip_address_pool_text['xscrollcommand'] = ip_address_pool_scroll_x.set
        self.ip_address_pool_text['yscrollcommand'] = ip_address_pool_scroll_y.set
        self.ip_address_pool_text.grid(row=0, column=0, sticky=tk.N + tk.S)
        ip_address_pool_scroll_x.grid(row=1, columnspan=2, sticky=tk.N + tk.E + tk.W)
        ip_address_pool_scroll_y.grid(row=0, column=2, sticky=tk.N + tk.S + tk.W)
        self.ip_address_pool_text.tag_configure('text', font=('Ariel, 10'))


    def addReservation(self):
        ip = self.ip_address_entry.get()
        dict = self.controller.dhcp_server.pool
        if ip not in dict:
            messagebox.showinfo("Error", "IP not in DHCP Server Address Pool")
            return
        if dict[ip]['mac'] is not None:
            messagebox.showinfo("Error", "IP {} is already taken".format(ip))
            return   
        macU = (self.mac_entry.get()).lower()
        macCheck = lambda mac: re.match("([0-9a-f]{2}[:]){5}([0-9a-f]{2})", mac)
        if macCheck(macU) is None:
            messagebox.showinfo("Error", "MAC format is xx:xx:xx:xx:xx:xx where x in [0-9 a-f]")
            return
        if any(macU in ip_info.values() for ip_info in self.controller.dhcp_server.pool.values()):
            messagebox.showinfo("Error", "This MAC already holds an IP address")
            return
        self.controller.dhcp_server.pool.update({ip: {'mac': macU, 'time': None}})
        self.controller.dhcp_server.reserved.update({ip: macU})
        self.controller.dhcp_server.debug("Static allocation for mac {}".format(macU))
        self.ip_address_pool_text.delete(1.0, tk.END)
        self.ip_address_pool_text.insert(tk.END, "IP : {}\n".format(ip))
        self.ip_address_pool_text.insert(tk.END, "\tMAC : {}\n".format(macU))