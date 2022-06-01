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

        self.mainMap = None
        self.menuBar = None
        self.features = None

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
        loadItem = fileMenu.Append(wx.ID_OPEN, "&Load...\tCtrl-L", "Load a JSON file")
        newItem = fileMenu.Append(wx.ID_NEW, "&New", "Blank page")
        saveItem = fileMenu.Append(wx.ID_SAVE, "&Save\tCtrl-S", "Save as a JSON file")
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        editMenu = wx.Menu()
        editPolyItem = editMenu.Append(wx.ID_EDIT, "&Edit Poly", "Edit a polygon (coordinates)")
        editParamItem = editMenu.Append(wx.ID_PROPERTIES, "&Edit Parameters", "Edit a polygon (parameters)")
        stopEditItem = editMenu.Append(wx.ID_APPLY, "&Stop Edition", "Close edition mode")
        fileMenu.AppendSeparator()
        createItem = editMenu.Append(wx.ID_ADD, "&Create", "Create a polygon")
        deleteItem = editMenu.Append(wx.ID_REMOVE, "&Delete", "Delete a polygon")

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT, "", " ")

        self.menuBar = wx.MenuBar()
        self.menuBar.Append(fileMenu, "&File")
        self.menuBar.Append(editMenu, "&Edit")
        self.menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(self.menuBar)

        self.Bind(wx.EVT_MENU, self.OnLoad, loadItem)
        self.Bind(wx.EVT_MENU, self.OnNew, newItem)
        self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnEditPoly,  editPolyItem)
        self.Bind(wx.EVT_MENU, self.OnEditParam,  editParamItem)
        self.Bind(wx.EVT_MENU, self.OnStopEdit,  stopEditItem)
        self.Bind(wx.EVT_MENU, self.OnCreatePoly,  createItem)
        self.Bind(wx.EVT_MENU, self.OnDeletePoly,  deleteItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

        self.menuBar.Enable(id=wx.ID_EDIT, enable=False)
        self.menuBar.Enable(id=wx.ID_PROPERTIES, enable=False)
        self.menuBar.Enable(id=wx.ID_APPLY, enable=False)
        self.menuBar.Enable(id=wx.ID_ADD, enable=False)
        self.menuBar.Enable(id=wx.ID_REMOVE, enable=False)

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
                self.mainMap = folium.Map(
                    location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
                )
                with open(pathname, 'r') as f:
                    self.features = json.load(f)['features']
                fg = folium.FeatureGroup(name=pathname.split('/')[-1].split(".")[0].capitalize())
                for feature in self.features:
                    if feature['geometry']['type'] == 'Polygon':
                        folium.Polygon(locations=[[x[1], x[0]] for x in feature['geometry']['coordinates'][0]],
                                       color="black",
                                       weight=1,
                                       fill=True,
                                       fill_color="#" + feature['properties']['TerritoryTypeColor'],
                                       fill_opacity=0.6,
                                       tooltip=feature['properties']['name']).add_to(fg)
                fg.add_to(self.mainMap)
                # folium.LayerControl().add_to(self.mainMap)

                dataLoad = io.BytesIO()
                self.mainMap.save(dataLoad, close_file=False)
                frm.browser.SetPage(dataLoad.getvalue().decode(), '')

                self.menuBar.Enable(id=wx.ID_EDIT, enable=True)
                self.menuBar.Enable(id=wx.ID_PROPERTIES, enable=True)
                self.menuBar.Enable(id=wx.ID_APPLY, enable=False)
                self.menuBar.Enable(id=wx.ID_ADD, enable=True)
                self.menuBar.Enable(id=wx.ID_REMOVE, enable=True)

            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)

    def OnSave(self, event):
        wx.MessageBox("Not implemented yet",
                      "",
                      wx.OK | wx.ICON_INFORMATION)

    def OnNew(self, event):
        wx.MessageBox("Not implemented yet",
                      "",
                      wx.OK | wx.ICON_INFORMATION)

    def OnEditPoly(self, event):
        number = wx.GetNumberFromUser("Which territory would you like to edit?", "Number: ", "Territory Number", 1, min=0, max=1000)
        if number != '' and number != -1:
            self.menuBar.Enable(id=wx.ID_EDIT, enable=False)
            self.menuBar.Enable(id=wx.ID_PROPERTIES, enable=False)
            self.menuBar.Enable(id=wx.ID_APPLY, enable=True)
            self.menuBar.Enable(id=wx.ID_ADD, enable=False)
            self.menuBar.Enable(id=wx.ID_REMOVE, enable=False)

            feature = next((f for f in self.features if f['properties']['TerritoryNumber'] == str(number)), None)
            if feature is not None:
                draw = plugins.Draw(draw_options={'polyline': False,
                                                  'polygon': False,
                                                  'rectangle': False,
                                                  'circle': False,
                                                  'marker': False,
                                                  'circlemarker': False},
                                    edit_options={'remove': False,
                                                  'feature': json.dumps(feature)},
                                    export=True)
                draw.add_to(self.mainMap)
                dataEditPoly = io.BytesIO()
                self.mainMap.save(dataEditPoly, close_file=False)
                frm.browser.SetPage(dataEditPoly.getvalue().decode(), '')

                # Add to draw.py before "options.edit.featureGroup = drawnItems;"
                #######################################################################################################
                # if ("feature" in options.edit){
                #     var feature = JSON.parse(options.edit.feature);
                #     var latlngs = [];
                #     for (var c of feature.geometry.coordinates[0]){
                #         latlngs.push([c[1], c[0]]);
                #     }
                #     L.polygon(latlngs, {color: "#000000",
                #                         weight: 1,
                #                         fillColor: "#" + feature.properties.TerritoryTypeColor,
                #                         fillOpacity: 0.6}).addTo(drawnItems);
                # }
                #######################################################################################################
            else:
                wx.MessageBox("There is no territory number " + str(number),
                              "",
                              wx.OK | wx.ICON_INFORMATION)
                return
        else:
            return

    def OnEditParam(self, event):
        number = wx.GetNumberFromUser("Which territory would you like to edit?", "Number: ", "Territory Number", 1, min=0, max=1000)

    def OnStopEdit(self, event):
        confirm = wx.MessageBox("You are going to stop editing. Would you like to merge your work?",
                                "Stop Edition Mode and Merging", wx.YES_NO | wx.CANCEL)
        if confirm == wx.CANCEL:
            return
        if confirm == wx.YES:

            # TODO check if export file, read it, delete it, make changes in $features
            pass

        self.mainMap = folium.Map(
            location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
        )
        fg = folium.FeatureGroup()
        for feature in self.features:
            if feature['geometry']['type'] == 'Polygon':
                folium.Polygon(locations=[[x[1], x[0]] for x in feature['geometry']['coordinates'][0]],
                               color="black",
                               weight=1,
                               fill=True,
                               fill_color="#" + feature['properties']['TerritoryTypeColor'],
                               fill_opacity=0.6,
                               tooltip=feature['properties']['name']).add_to(fg)
        fg.add_to(self.mainMap)
        dataStop = io.BytesIO()
        self.mainMap.save(dataStop, close_file=False)
        frm.browser.SetPage(dataStop.getvalue().decode(), '')

        self.menuBar.Enable(id=wx.ID_EDIT, enable=True)
        self.menuBar.Enable(id=wx.ID_PROPERTIES, enable=True)
        self.menuBar.Enable(id=wx.ID_APPLY, enable=False)
        self.menuBar.Enable(id=wx.ID_ADD, enable=True)
        self.menuBar.Enable(id=wx.ID_REMOVE, enable=True)

    def OnCreatePoly(self, event):
        wx.MessageBox("Not implemented yet",
                      "",
                      wx.OK | wx.ICON_INFORMATION)

    def OnDeletePoly(self, event):
        wx.MessageBox("Not implemented yet",
                      "",
                      wx.OK | wx.ICON_INFORMATION)

    def OnAbout(self, event):
        wx.MessageBox("Version: 1.0.1 (development state)"
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
    frm.mainMap = folium.Map(
        location=[48.559400, 7.683222], tiles="OpenStreetMap", zoom_start=13
    )
    data = io.BytesIO()
    frm.mainMap.save(data, close_file=False)
    frm.browser.SetPage(data.getvalue().decode(), '')
    frm.Show()
    app.MainLoop()
