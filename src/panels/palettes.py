import wx, rompanel

h2i = lambda i: int(i, 16)

class PalettePanel(rompanel.ROMPanel):
    
    frameTitle = "Palette Editor"
    
    def init(self):
        
        self.curPaletteIdx = 0
        self.color = 0
        
        #inst = wx.StaticText(self, -1, "Edit color palettes.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Colors"), wx.VERTICAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Maps using this palette"), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        sbs2.StaticBox.SetForegroundColour("#000000")
        sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        #self.paletteList = wx.ComboBox(self, wx.ID_ANY, size=(150, -1), style=wx.CB_DROPDOWN)
        #self.paletteList.AppendItems([p.name for p in self.rom.data["palettes"]])
        #self.paletteList.SetSelection(0)
        
        self.colorPanels = []
        for p in range(16):
            self.colorPanels.append(rompanel.ColorPanel(self, wx.ID_ANY, "#000000", num=p))
        
        self.changeColors()
        
        colorSizer = wx.FlexGridSizer(2,16)
        for i in range(16):
            colorSizer.Add(wx.StaticText(self, -1, str(i).zfill(2)), 0, wx.ALIGN_CENTER)
        colorSizer.AddMany(self.colorPanels)
        
        #self.bankList = wx.ListBox(self, wx.ID_ANY, size=(120,100))
        #self.bankList.AppendItems(bankNames) #, "u2", "yay")
        
        #self.lineList = wx.ListBox(self, wx.ID_ANY, size=(350,100))
        
        sbs1.AddSizer(colorSizer, 0, wx.ALL, 10)
        #sbs1.Add(self.paletteList, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        #sbs1.Add(self.lineList, 0, wx.EXPAND | wx.ALL, 10)
        #sbs1.Add(rompanel.ColorPanel(self, wx.ID_ANY, "#FF0000"), 0, wx.LEFT, 15)
        
        # -----------------------
        
        text1 = wx.StaticText(self, -1, "(if applicable)")
        
        self.mapList = wx.ListBox(self, wx.ID_ANY, size=(120,140))
        
        sbs2.Add(text1, 0, wx.ALL | wx.ALIGN_CENTER)
        sbs2.Add(self.mapList, 1, wx.ALL, 10)
    
        # ------------------------
        
        self.colorText = wx.StaticText(self, -1, "Color %02i" % self.color)
        self.colorText.SetFont(self.GetTopLevelParent().editFont)
        
        sbs3left = wx.BoxSizer(wx.VERTICAL)
        
        text2 = wx.StaticText(self, -1, "Edit")
        
        self.editPanel = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", enable=False)
        self.editPanel.SetSize((60,60))
        
        sbs3left.Add(text2, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, 10)
        sbs3left.Add(self.editPanel, 0, wx.TOP | wx.ALIGN_CENTER, 5)
        
        sbs3mid = wx.FlexGridSizer(3,3)
        
        self.sliderRed = wx.Slider(self, wx.ID_ANY, 0, 0, 15, size=(90, 25), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.sliderGreen = wx.Slider(self, wx.ID_ANY, 0, 0, 15, size=(90, 25), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        self.sliderBlue = wx.Slider(self, wx.ID_ANY, 0, 0, 15, size=(90, 25), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
        #self.sliderBlue.SetScrollbar(wx.VERTICAL, 0, 100, 0)
        
        self.spinRed = wx.SpinCtrl(self, wx.ID_ANY, "", size=(45,20))
        self.spinRed.SetRange(0,15)
        self.spinRed.SetValue(0)
        self.spinGreen = wx.SpinCtrl(self, wx.ID_ANY, "", size=(45,20))
        self.spinGreen.SetRange(0,15)
        self.spinGreen.SetValue(0)
        self.spinBlue = wx.SpinCtrl(self, wx.ID_ANY, "", size=(45,20))
        self.spinBlue.SetRange(0,15)
        self.spinBlue.SetValue(0)
        
        sbs3mid.Add(rompanel.ColorPanel(self, -1, "#FF0000", (20,20)), 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sbs3mid.Add(self.sliderRed, 1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        sbs3mid.Add(self.spinRed, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sbs3mid.Add(rompanel.ColorPanel(self, -1, "#00FF00", (20,20)), 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sbs3mid.Add(self.sliderGreen, 1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        sbs3mid.Add(self.spinGreen, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sbs3mid.Add(rompanel.ColorPanel(self, -1, "#0000FF", (20,20)), 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sbs3mid.Add(self.sliderBlue, 1, flag=wx.EXPAND | wx.ALIGN_CENTER)
        sbs3mid.Add(self.spinBlue, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sbs3right = wx.BoxSizer(wx.VERTICAL)
        
        text3 = wx.StaticText(self, -1, "Clipboard")
        
        self.copyPanel = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", enable=False)
        self.copyPanel.SetSize((60,60))
        
        sbs3right.Add(text3, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, 10)
        sbs3right.Add(self.copyPanel, 0, wx.TOP | wx.ALIGN_CENTER, 5)
        
        self.copyButton = wx.Button(self, wx.ID_ANY, "Copy")
        self.pasteButton = wx.Button(self, wx.ID_ANY, "Paste")
        self.pasteButton.Enable(False)
        sbs3main = wx.FlexGridSizer(2,3)
        
        sbs3main.AddSizer(sbs3left, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        sbs3main.AddSizer(sbs3mid, 1, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 15)
        sbs3main.AddSizer(sbs3right, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        sbs3main.Add(self.copyButton, 0, wx.ALIGN_CENTER)
        sbs3main.Add(self.colorText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sbs3main.Add(self.pasteButton, 0, wx.ALIGN_CENTER)
        
        sbs3.AddSizer(sbs3main, 0)
        
        # ------------------------
        
        self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        sbs4.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # ------------------------
        
        #self.sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(sbs1, pos=(0,0), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs2, pos=(0,1), span=(2,1), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs3, pos=(1,0), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs4, pos=(2,0), span=(1,2), flag=wx.EXPAND)
        #self.sizer.Add(sbs2, pos=(2,0), flag=wx.EXPAND)
        
        self.changePalette(0)
        self.changeEditColor(0)
        self.updateSymbols()
        
        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        #wx.EVT_TEXT(self, self.paletteList.GetId(), self.OnRenamePalette)
        
        wx.EVT_SLIDER(self, -1, self.OnChangeColor)
        wx.EVT_SPINCTRL(self, -1, self.OnChangeColor)
        
        wx.EVT_BUTTON(self, self.copyButton.GetId(), self.OnCopyColor)
        wx.EVT_BUTTON(self, self.pasteButton.GetId(), self.OnPasteColor)
        
        #wx.EVT_LISTBOX(self, self.bankList.GetId(), self.OnSelectBank)
        #wx.EVT_LISTBOX(self, self.lineList.GetId(), self.OnSelectLine)
        #wx.EVT_TEXT(self, self.editBox.GetId(), self.OnEditText)
    
    def changeColors(self):
        
        palette = self.curPalette
        
        for c in range(len(self.colorPanels)):
            self.colorPanels[c].SetBackgroundColour(palette.colors[c])
            self.colorPanels[c].Refresh()
    
    def OnSelectPalette(self, evt):
        
        self.changePalette(evt.GetSelection())
        
    def changePalette(self, num):
    
        self.curPaletteIdx = num
        
        imp = self.curPalette.isMapPalette
        self.mapList.Enable(imp)
        self.mapList.Clear()
        
        if imp:
            mapsUsing = [m.name for m in filter(lambda obj: obj.paletteIdx == self.curPaletteIdx, self.rom.data["maps"])]
            self.mapList.AppendItems(mapsUsing)
            
        self.changeColors()
        self.changeEditColor(0)
        self.updateSymbols()
    
    def OnRenamePalette(self, evt):
        #s = .GetString()
        sel = self.paletteList.GetSelection()
        #self.paletteList.SetString(sel, s)
    
    def changeEditColor(self, num):
        self.color = num
        self.colorText.SetLabel("Color %02i" % num)
        c = self.rom.data["palettes"][self.curPaletteIdx].colors[num]
        self.editPanel.SetBackgroundColour(c)
        self.editPanel.Refresh()
        self.setColor(c)
        
    def setColor(self, c):
        r, g, b = int(c[1], 16), int(c[3], 16), int(c[5], 16)
        self.sliderRed.SetValue(int(r))
        self.spinRed.SetValue(int(r))
        self.sliderGreen.SetValue(int(g))
        self.spinGreen.SetValue(int(g))
        self.sliderBlue.SetValue(int(b))
        self.spinBlue.SetValue(int(b))
        
    def updateSymbols(self):
        self.symbolsBox.SetValue(self.rom.data["palettes"][self.curPaletteIdx].hexlify())
        
    def OnChangeColor(self, evt):
        id = evt.GetId()
        
        if id == self.sliderRed.GetId():
            self.spinRed.SetValue(self.sliderRed.GetValue())
        elif id == self.sliderGreen.GetId():
            self.spinGreen.SetValue(self.sliderGreen.GetValue())
        elif id == self.sliderBlue.GetId():
            self.spinBlue.SetValue(self.sliderBlue.GetValue())
        elif id == self.spinRed.GetId():
            self.sliderRed.SetValue(self.spinRed.GetValue())
        elif id == self.spinGreen.GetId():
            self.sliderGreen.SetValue(self.spinGreen.GetValue())
        elif id == self.spinBlue.GetId():
            self.sliderBlue.SetValue(self.spinBlue.GetValue())
        
        r = hex(self.spinRed.GetValue())[2:]
        g = hex(self.spinGreen.GetValue())[2:]
        b = hex(self.spinBlue.GetValue())[2:]
        c = "#%s%s%s" % (r*2, g*2, b*2)
        
        self.editPanel.SetBackgroundColour(c)
        self.colorPanels[self.color].SetBackgroundColour(c)
        self.editPanel.Refresh()
        self.colorPanels[self.color].Refresh()
        
        self.modify()
        
        self.updateSymbols()
        
        self.rom.data["palettes"][self.curPaletteIdx].colors[self.color] = c
        
    def OnCopyColor(self, evt):
        c = self.rom.data["palettes"][self.curPaletteIdx].colors[self.color]
        self.copyPanel.SetBackgroundColour(c)
        self.copyPanel.Refresh()
        self.copyPanel.copyColor = c
        self.pasteButton.Enable(True)
        
    def OnPasteColor(self, evt):
        c = self.copyPanel.copyColor
        self.editPanel.SetBackgroundColour(c)
        self.colorPanels[self.color].SetBackgroundColour(c)
        self.editPanel.Refresh()
        self.colorPanels[self.color].Refresh()
        
        self.updateSymbols()
        
        self.curPalette.colors[self.color] = c
        
        self.setColor(c)
        
    def getCurrentData(self):
        return self.curPalette
    
    changeSelection = changePalette
    
    curPalette = property(lambda self: self.rom.data["palettes"][self.curPaletteIdx])