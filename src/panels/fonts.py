import wx, rompanel

h2i = lambda i: int(i, 16)

class FontPanel(rompanel.ROMPanel):
    
    frameTitle = "Font Editor"
    
    def init(self):
        
        self.font = None
        self.letter = " "
        self.palette = self.rom.getDataByName("palettes", "Sprite & UI Palette")
        self.mode = 0
        
        self.color_left = 1
        self.color_right = 0
        
        inst = wx.StaticText(self, -1, "Edit font graphics.")
        inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "1. Select a font."), wx.VERTICAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "2. Select a letter."), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "3. Edit the letter."), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        self.fontList = wx.ComboBox(self, wx.ID_ANY, size=(200,-1))
        self.fontList.AppendItems([f.name for f in self.rom.data["fonts"]])
        self.fontList.SetSelection(0)
        
        sbs1.Add(self.fontList, 0, wx.ALL, 10)
        
        leftSizer.AddSizer(sbs1, 0)
        
        # -----------------------
        
        glyphSizer = wx.FlexGridSizer(9,9)
        self.glyphPanels = []
        
        for g in self.rom.fontOrder:
            sp = rompanel.SpritePanel(self, wx.ID_ANY, 16, 15, self.palette, scale=2, func=self.OnChooseGlyph)
            sp.glyph = g
            self.glyphPanels.append(sp)
            glyphSizer.Add(sp, 0)
        
        sbs2.AddSizer(glyphSizer, 0, wx.ALL, 10)
        
        # -----------------------
        
        text1 = wx.StaticText(self, -1, "Left-Click to set, Right-Click to clear.")
        
        self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 16, 15, self.palette, scale=12, func="edit")
        
        sbs3.Add(text1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        sbs3.Add(self.editPanel, 1, wx.BOTTOM | wx.ALIGN_CENTER, 10)

        leftSizer.AddSizer(sbs3, 0, wx.TOP | wx.EXPAND, 10)
        
        # ------------------------
        
        self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        sbs4.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------
        
        self.Sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(leftSizer, pos=(1,0))
        self.sizer.AddSizer(sbs2, pos=(1,1), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs4, pos=(2,0), span=(1,2), flag=wx.EXPAND)
        
        self.changeFont(0)
        self.changeEditGlyph(self.rom.fontOrder[0])
        
        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        #wx.EVT_TEXT(self, self.paletteList.GetId(), self.OnRenamePalette)
        
        #wx.EVT_SLIDER(self, -1, self.OnChangeColor)
        #wx.EVT_SPINCTRL(self, -1, self.OnChangeColor)
        
        #wx.EVT_BUTTON(self, self.copyButton.GetId(), self.OnCopyColor)
        #wx.EVT_BUTTON(self, self.pasteButton.GetId(), self.OnPasteColor)
        
        #wx.EVT_LISTBOX(self, self.bankList.GetId(), self.OnSelectBank)
        #wx.EVT_LISTBOX(self, self.lineList.GetId(), self.OnSelectLine)
        #wx.EVT_TEXT(self, self.editBox.GetId(), self.OnEditText)

    def OnChooseGlyph(self, evt):
        
        self.changeEditGlyph(evt.GetEventObject().glyph)
        
    def refreshPixels(self):
        
        idx = self.rom.fontOrder.index(self.letter)
            
        self.glyphPanels[idx].refreshSprite(self.font.glyphs[self.letter].pixels)
        self.glyphPanels[idx].Refresh()
        self.font.glyphs[self.letter].recalculateWidth()
        self.symbolsBox.SetValue(self.font.glyphs[self.letter].hexlify())
    
    def changeFont(self, key):
            
        self.font = self.rom.data["fonts"][key]

        for i,g in enumerate(self.rom.fontOrder):
            self.glyphPanels[i].refreshSprite(self.font.glyphs[g].pixels)
        
    def changeEditGlyph(self, glyph):
        self.letter = glyph
        realGlyph = self.font.glyphs[self.letter]
        self.editPanel.refreshSprite(realGlyph.pixels)
        self.editPanel.Refresh()
        
        self.symbolsBox.SetValue(realGlyph.hexlify())
        
    def getCurrentData(self):
        return self.font
        
    def getCurrentSpriteObject(self):
        return self.font.glyphs[self.letter]