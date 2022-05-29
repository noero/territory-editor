import tkinter as tk


class Ui:
    def __init__(self, client, root):
        self.root = root
        self.client = client

        # Setting up the GUI
        self.root.title('Territory Editor')
        # self.root.iconphoto(False, tk.PhotoImage(file='./jess.png'))

        self.frame = tk.Frame(self.root, highlightthickness=0)
        self.frame.place(relwidth=1, relheight=1)

        self.canvas = tk.Canvas(self.frame, bg='black', highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
