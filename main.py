from gui import DHCP_Server_GUI

def start_gui():
    app = DHCP_Server_GUI()
    app.geometry("800x700")
    app.mainloop()

def main():
    start_gui()

if __name__ == '__main__':
    main()