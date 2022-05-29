import io
import sys
import folium
import tkinter as tk
from tkhtmlview import HTMLLabel


class Ui:
    def __init__(self, client, root):
        self.root = root
        self.client = client

        # Setting up the GUI
        self.root.title('Territory Editor')
        # self.root.iconphoto(False, tk.PhotoImage(file='./jess.png'))

        self.frame = tk.Frame(self.root, width=1280, height=720, bg='black')
        self.frame.pack()

        m = folium.Map(
            location=[45.5236, -122.6750], tiles="Stamen Toner", zoom_start=13
        )
        data = io.BytesIO()
        m.save(data, close_file=False)
        self.map = HTMLLabel(self.frame, html=data.getvalue().decode())
        self.map.pack(fill="both", expand=True)

