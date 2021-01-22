import tkinter as tk
from tkinter import messagebox, ttk
from basic_server import basic_server
from DHCP_server import DHCP_Server
import ipaddress
import socket

class configuration_server(basic_server):
    def __init__(self, parent, controller):
        basic_server.__init__(self, parent, controller)
        self.init_window()
    #
    def init_window(self, button_bg='#E0E0E0', button_fg='#000000', label_bg='#f0f0f0',  label_txt='black', txt_color='#000000'):
        tk.Label(master=self, text='DHCP OPTIONS', bg=self["bg"], fg=label_txt, font=self.controller.title_font).pack(side = tk.TOP, anchor = 'n')

              # return home
        return_frame = tk.Frame(master=self, bg="#f0f0f0")
        return_frame.pack(side=tk.TOP, expand=0)
        return_frame.place(x=20, y=20)
        tk.Grid.columnconfigure(return_frame, 0, weight=1)
        tk.Button(return_frame, text="Return", width=15, bg=button_bg, fg=button_fg,
                  font=self.controller.button_text_font,
                  command=lambda: self.controller.show_frame("open_server")).grid(row=0, column=0)

        configuration_frame = tk.Frame(master=self, bg = "#f0f0f0")
        configuration_frame.pack(side=tk.LEFT)
        configuration_frame.place(x=100, y=100)

        #server name setting

        server_name_label = tk.LabelFrame(configuration_frame,  bg=label_bg, fg=label_txt, font=self.controller.text_label_title)
        server_name_label.grid (row=0, column=0, padx=0, pady=0)
        tk.Label(server_name_label , text='Server Name', fg=txt_color, font=self.controller.button_text_font).grid(row=1, column=0)
        self.server_name_entry = tk.Entry(server_name_label, width = 50)
        self.server_name_entry.grid(row=1, column=10,  padx=10, pady=10)
        tk.Button(server_name_label, text='Set Server Name', bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.set_server_name).grid(row=10,  columnspan=12)

        # server lease time setting
        lease_time_frame = tk.LabelFrame(configuration_frame, bg=label_bg, fg=label_txt,font=self.controller.text_label_title)
        lease_time_frame.grid(row=1, column=0, padx=0, pady=0)
        tk.Label(lease_time_frame, text='Lease Time', fg=txt_color, font=self.controller.button_text_font).grid(row=1,column=0)
        self.lease_time_entry = ttk.Combobox(lease_time_frame, state='readonly',  width=50, values=[30, 60, 180, 300])
        self.lease_time_entry.grid(row=1, column=10, padx=10, pady=10)
        tk.Button(lease_time_frame, text='Set Lease Time', bg=button_bg, fg=button_fg,   font=self.controller.text_label_title, command=self.set_server_lease_time).grid(row=10, columnspan=12)
        # 8 zile, 24h, 8h, 1h

        #ip address setting
        ip_address_frame = tk.LabelFrame(configuration_frame,text = 'Pool Address', bg=label_bg, fg=label_txt,  font=self.controller.text_label_title)
        ip_address_frame.grid(row=2, column=0, padx=0, pady=0)
        tk.Label(ip_address_frame, text='IP Address', fg=txt_color, font=self.controller.button_text_font).grid(row=2,  column=0)
        self.ip_address_entry = tk.Entry(ip_address_frame, width=50)
        self.ip_address_entry.grid(row=2, column=10,  padx=10, pady=10)
        tk.Label(ip_address_frame, text='Mask', fg=txt_color, font=self.controller.button_text_font).grid(row=4,  column=0)
        self.mask_entry = ttk.Combobox(ip_address_frame,state='readonly', width=50, values=["/{}".format(str(x)) for x in range(24, 31)])
        self.mask_entry.grid(row=4, column=10,  padx=10, pady=10)
        tk.Button(ip_address_frame, text='Set Pool Address', bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.setPoolAddress).grid(row=10, columnspan=12)

        #adress pool viewer
        address_pool_viewer_frame = tk.Frame(master=self, bg='#d4d4d4')
        address_pool_viewer_frame.pack(side=tk.BOTTOM, expand = 1)
        address_pool_viewer_frame.place(x=100,y=400)
        address_pool_viewer_label = tk.LabelFrame(address_pool_viewer_frame,  bg=label_bg,fg='black', font=self.controller.text_label_title)
        address_pool_viewer_label.grid(row=1, column=0)
        self.ip_address_pool_text = tk.Text(address_pool_viewer_label, height=10, width=50, bg="#f0f0f0", fg='black')
        ip_address_pool_scroll = tk.Scrollbar(address_pool_viewer_label, command=self.ip_address_pool_text.yview)
        self.ip_address_pool_text['yscrollcommand'] = ip_address_pool_scroll.set
        self.ip_address_pool_text.grid(row=0, column=0, sticky=tk.N+tk.S)
        ip_address_pool_scroll.grid(row=0, column=1, sticky=tk.N+tk.S+tk.W)

        tk.Button(ip_address_frame, text='Load Data', bg=button_bg, fg=button_fg, font=self.controller.text_label_title, command=self.loadData()).grid(row=12, columnspan=12)

    def loadData(self):
        #self.controller.dhcp_server.debug("Loading data ...")
        self.controller.dhcp_server.loadPool()
        return

    def set_server_name(self):
        server_name = self.server_name_entry.get()
        if len(server_name) > 64:
            messagebox.showinfo("Server Name too long")
            return
        self.controller.dhcp_server.debug("Setting Server Name: '{}'".format(server_name))
        self.controller.dhcp_server.setServerName(server_name)

    def set_server_lease_time(self):
        lease_time = int(self.lease_time_entry.get())
        self.controller.dhcp_server.debug("Set Lease Time {}".format(lease_time))
        self.controller.dhcp_server.setServerLeaseTime(lease_time)

    def setPoolAddress(self):
        mask = self.mask_entry.get()
        ip = self.ip_address_entry.get()
        print(ip)
        mask_result = self._poolIsCorrect(ip, mask)
        starting_ip = self._getIPNetworkOfIPv4(ip, mask_result)
        self.controller.dhcp_server.debug("Set pool address")
        self.controller.dhcp_server.setAddressPool(starting_ip, mask_result)
        self.poolWidgetFill()

    def poolWidgetFill(self):
        mask = self.mask_entry.get()
        ip = self.ip_address_entry.get()
        self.controller.dhcp_server.debug("View pool address")
        try:
            mask_result = self._poolIsCorrect(ip, mask)
        except OSError:
            messagebox.showinfo("IP Format error", "IP Format: x.x.x.x where x = 0-255")
            return
        starting_ip = self._getIPNetworkOfIPv4(ip, mask_result)
        address_pool, address_pool_broadcast = DHCP_Server.getPool(starting_ip, mask_result)

        self.ip_address_pool_text.delete(1.0, tk.END)
        self.ip_address_pool_text.insert(tk.END, "Net Address : {}\n".format(starting_ip))
        self.ip_address_pool_text.insert(tk.END, "Broadcast Address : {}\n".format(address_pool_broadcast))
        for key, value in address_pool.items():
            self.ip_address_pool_text.insert(tk.END, key + '\n')

    @staticmethod
    def _getIPNetworkOfIPv4(ipv4, mask):
        return str(ipaddress.ip_interface(ipv4 + '/' + str(mask)).network).split('/')[0]

    @staticmethod
    def _poolIsCorrect(ip, mask):
        socket.inet_aton(ip)
        if mask == '':
            raise ValueError
        if mask[0] == '/':
            mask_result = int(mask[1:])
        else:
            mask_result = int(mask)
        if mask_result < 1 or mask_result > 32:
            raise ValueError
        return mask_result