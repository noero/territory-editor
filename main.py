#!/usr/bin/env python
import io
import json
import wx
import folium
import branca
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

        editMenu = wx.Menu()

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, "", " ")

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(editMenu, "&Edit")
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnLoad, loadItem)
        self.Bind(wx.EVT_MENU, self.OnExport, exportItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        self.Close(True)

    def OnLoad(self, event):
        if wx.MessageBox("Current content will be overwritten!", "Please confirm",
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
                    features = json.load(f)['features']
                fg = folium.FeatureGroup(name=pathname.split('/')[-1].split(".")[0].capitalize())
                for feature in features:
                    if feature['geometry']['type'] == 'Polygon':
                        folium.Polygon(locations=[[x[1], x[0]] for x in feature['geometry']['coordinates'][0]],
                                       color="black",
                                       weight=1,
                                       fill=True,
                                       fill_color="#" + feature['properties']['TerritoryTypeColor'],
                                       fill_opacity=0.6,
                                       tooltip=feature['properties']['name'],
                                       popup=self.customPopup(feature)).add_to(fg)
                fg.add_to(m)
                folium.LayerControl().add_to(m)
                # draw = plugins.Draw(draw_options={'polyline': False,
                #                                   'rectangle': False,
                #                                   'circle': False,
                #                                   'marker': False,
                #                                   'circlemarker': False})
                #                     # edit_options={'json': json.dumps(features)})

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

                # draw.add_to(m)

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

    def customPopup(self, feature):
        name = feature['properties']['name']
        terType = feature['properties']["TerritoryType"]
        color = feature['properties']["TerritoryTypeColor"]
        number = feature['properties']["TerritoryNumber"]
        notes = feature['properties']["TerritoryNotes"] or ""
        coordinates = feature['geometry']['coordinates']
        style = """
            <style>
                :root {
                    --input-color: #99A3BA;
                    --input-border: #CDD9ED;
                    --input-background: #fff;
                    --input-placeholder: #CBD1DC;
                
                    --input-border-focus: #275EFE;
                
                    --group-color: var(--input-color);
                    --group-border: var(--input-border);
                    --group-background: #EEF4FF;
                
                    --group-color-focus: #fff;
                    --group-border-focus: var(--input-border-focus);
                    --group-background-focus: #678EFE;
                
                }
                
                .form-field {
                    display: block;
                    width: 100%;
                    padding: 8px 16px;
                    line-height: 25px;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: inherit;
                    border-radius: 6px;
                    -webkit-appearance: none;
                    color: var(--input-color);
                    border: 1px solid var(--input-border);
                    background: var(--input-background);
                    transition: border .3s ease;
                }
                
                .form-field:focus {
                    outline: none;
                    border-color: var(--input-border-focus);
                }
                
                .form-group {
                    position: relative;
                    display: flex;
                    width: 100%;
                }
                .form-group .form-field {
                    position: relative;
                    z-index: 1;
                    flex: 1 1 auto;
                    width: 1%;
                    margin-top: 0;
                    margin-bottom: 0;
                }
                .form-group > span, .form-field {
                    # white-space: nowrap;
                    display: block;
                }
                .form-group > span:not(:first-child):not(:last-child), .form-group .form-field:not(:first-child):not(:last-child) {
                    border-radius: 0;
                }
                .form-group > span:first-child, .form-group .form-field:first-child {
                    border-radius: 6px 0 0 6px;
                }
                .form-group > span:last-child, .form-group .form-field:last-child {
                    border-radius: 0 6px 6px 0;
                }
                .form-group > span:not(:first-child), .form-group .form-field:not(:first-child) {
                    margin-left: -1px;
                }
                .form-group > span {
                    text-align: center;
                    padding: 8px 12px;
                    font-size: 14px;
                    line-height: 25px;
                    color: var(--group-color);
                    background: var(--group-background);
                    border: 1px solid var(--group-border);
                    transition: background .3s ease, border .3s ease, color .3s ease;
                }
                .form-group:focus-within > span {
                    color: var(--group-color-focus);
                    background: var(--group-background-focus);
                    border-color: var(--group-border-focus);
                }
                
                html {
                    box-sizing: border-box;
                    -webkit-font-smoothing: antialiased;
                }
                
                * {
                    box-sizing: inherit;
                }
                
                *:before, *:after {
                    box-sizing: inherit;
                }
                
                #html5colorpicker {
                    cursor: pointer;
                    height: 44px;
                    padding: 0;
                }
                
                body {
                    min-height: 90vh;
                    font-family: 'Mukta Malar', Arial;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }
                
                body .form-group {
                    max-width: 360px;
                }
                
                body .form-group:not(:last-child) {
                    margin-bottom: 8px;
                }
                
                button-group {
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  flex-direction: row;
                  width: 100%;
                }
                button {
                  background-color: #5591fa;
                  color: white;
                  border: none;
                  padding: 5px;
                  font-size: 31px;
                  height: 48px;
                  width: 48px;
                  box-shadow: 0 2px 4px darkslategray;
                  cursor: pointer;
                  transition: all 0.2s ease;
                  border-radius: 70%;
                }
                
                button:active {
                  background-color: #4386fa;
                  box-shadow: 0 0 2px darkslategray;
                  transform: translateY(2px);
                }
            </style>
        """
        html = """
            <h2>{0}</h2>
            <div class="form-group">
                <span>Zone:</span>
                <input class="form-field" type="text" value="{1}">
            </div>
            <div class="form-group">
                <span>Color:</span>
                <input class="form-field" type="color" id="html5colorpicker" value="#{2}">
            </div>
            <div class="form-group">
                <span>Number:</span>
                <input class="form-field" type="text" value="{3}">
            </div>
            <div class="form-group">
                <span>Notes:</span>
                <textarea class="form-field" type="text">{4}</textarea>
            </div>
            <div class="button-group">
                <button id="edit" onClick=onEdit({3})>&#9998;</button>
                <button id="save">&#10003;</button>
            </div>
        """
        html = style + html.format(name, terType, color, number, notes)
        iframe = branca.element.IFrame(html=html, width=350, height=400)
        popup = folium.Popup(iframe, max_width=2650)
        return popup


if __name__ == '__main__':
    app = wx.App()
    frm = MapFrame(None, title='Territory Editor')
    m = folium.Map(
        location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
    )
    data = io.BytesIO()
    m.save(data, close_file=False)
    frm.browser.SetPage(data.getvalue().decode(), '')
    frm.Show()
    app.MainLoop()
