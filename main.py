#!/usr/bin/env python
import io
import json

import wx
import folium
import wx.html2
from folium import plugins


class MapFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MapFrame, self).__init__(*args, **kw)

        self.SetSize((1280, 720))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        sizer.Add(self.browser, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.makeMenuBar()
        self.CreateStatusBar()
        self.SetStatusText("")

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """
        fileMenu = wx.Menu()
        loadItem = fileMenu.Append(-1, "&Load...\tCtrl-L",
                                   "Load a JSON file")
        exportItem = fileMenu.Append(-1, "&Export...\tCtrl-S",
                                     "Export as a JSON file")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, "", " ")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnLoad, loadItem)
        self.Bind(wx.EVT_MENU, self.OnExport, exportItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close(True)

    def OnLoad(self, event):
        if wx.MessageBox("Current content will be overwritten! Proceed?", "Please confirm",
                         wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
            return

        with wx.FileDialog(self, "Open GeoJSON file", wildcard="GeoJSON files (*.json;*.geojson)|*.json;*.geojson",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                m = folium.Map(
                    location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
                )
                with open(pathname, 'r') as f:
                    fg = json.load(f)['features']
                draw = plugins.Draw(draw_options={'polyline': False,
                                                  'rectangle': False,
                                                  'circle': False,
                                                  'marker': False,
                                                  'circlemarker': False},
                                    edit_options={'json': json.dumps(fg)})

                # Added to draw.py before "options.edit.featureGroup = drawnItems;"
                #######################################################################################################
                # if ("json" in options.edit){
                #     var geojson = JSON.parse(options.edit.json);
                #     for (var feature of geojson) {
                #         var latlngs = [];
                #         for (var c of feature.geometry.coordinates[0]){
                #             latlngs.push([c[1], c[0]]);
                #         }
                #         L.polygon(latlngs, {color: "#000000",
                #                             weight: 1,
                #                             fillColor: "#" + feature.properties.TerritoryTypeColor,
                #                             fillOpacity: 0.6}).addTo(drawnItems)
                #     }
                # }
                #######################################################################################################
                draw.add_to(m)
                data = io.BytesIO()
                m.save(data, close_file=False)
                frm.browser.SetPage(data.getvalue().decode(), '')
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def OnExport(self, event):
        wx.MessageBox("Not implemented yet",
                      "",
                      wx.OK | wx.ICON_INFORMATION)

    def OnAbout(self, event):
        wx.MessageBox("Version: 1.0 (development state)"
                      "\nGitHub : https://github.com/noero/Territory_Editor.git"
                      "\nCreator: Romain Damiano",
                      "About Territory Editor",
                      wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wx.App()
    frm = MapFrame(None, title='Territory Editor')
    m = folium.Map(
        location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
    )
    data = io.BytesIO()
    m.save(data, close_file=False)
    frm.browser.SetPage(data.getvalue().decode(), 'https://noero.fr')
    frm.Show()
    app.MainLoop()
