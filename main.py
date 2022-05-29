# from threading import Thread
from ui import *


class ThreadedClient:
    def __init__(self, app):

        # Set up the GUI part
        self.mainGui = Ui(self, app)


if __name__ == '__main__':
    root = tk.Tk()
    client = ThreadedClient(root)
    root.mainloop()
