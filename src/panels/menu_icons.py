import wx, rompanel, binascii
import data

from PIL import Image

h2i = lambda i: int(i, 16)

class MenuIconPanel(rompanel.ROMPanel):
    
    frameTitle = "Menu Icon Editor"
    
    def init(self):
        
        self.palette = self.rom.getDataByName("palettes", "Sprite & UI Palette")
        self.frame = 0
        self.mode = 0
        
        self.color_left = 0
        self.color_right = 0
        
        self.curIconIdx = 0
        
        # -------------------------------
        
        #self.rom.data["icons"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit menu icon graphics.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        #sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "1. Select an icon."), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Menus using this icon"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.HORIZONTAL)
        sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Preview Animation"), wx.VERTICAL)
        sbs5.StaticBox.SetSize((0,0))
        #sbs6 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        """self.iconList = wx.ComboBox(self, wx.ID_ANY, size=(200,-1))
        self.iconList.AppendItems([self.rom.data["menu_icons"][s].name for s in range(len(self.rom.data["menu_icons"]))]) #, "u2", "yay")
        self.iconList.SetSelection(0)
        
        sbs1.Add(self.iconList, 0, wx.ALL, 10)
        sbs1.Add((0,10))"""
        
        # -----------------------
        
        """self.menuList = wx.ListBox(self, wx.ID_ANY, size=(200,40))
        sbs2.Add(self.menuList, 1, wx.ALL, 10)"""
        
        # -----------------------
        
        text1 = wx.StaticText(self, -1, "Colors")
        text2 = wx.StaticText(self, -1, "Icon (Color 0 = trans)")
        text3 = wx.StaticText(self, -1, "Left-Click")
        text4 = wx.StaticText(self, -1, "Right-Click")
        text5 = wx.StaticText(self, -1, "Mode")
        
        self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=8, bg=16, func="edit")
        self.editPanel
        #self.testPanel = rompanel.iconPanel(self, wx.ID_ANY, 24, 24, self.palette, scale=8)
        #self.testPanel.refreshSprite([]
        #self.testPanel.Refresh()
        
        self.colorPanels = []
        for p in range(16):
            self.colorPanels.append(rompanel.ColorPanel2(self, wx.ID_ANY, "#000000", num=p))
        
        self.changeColors()
        
        self.switchButton = wx.Button(self, wx.ID_ANY, "Frame", size=(40,20))
        
        #self.commandText = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        
        sbs4left = wx.BoxSizer(wx.VERTICAL)
        
        colorSizer = wx.FlexGridSizer(8,2)
        colorSizer.AddMany(self.colorPanels)
        
        self.importButton = wx.Button(self, wx.ID_ANY, "Import", size=(40,20))
        self.exportButton = wx.Button(self, wx.ID_ANY, "Export", size=(40,20))
        
        sbs4left.Add(text1, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4left.AddSizer(colorSizer, 0)
        sbs4left.Add(self.importButton, 0, wx.TOP | wx.ALIGN_CENTER, 5)
        sbs4left.Add(self.exportButton, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        sbs4mid = wx.BoxSizer(wx.VERTICAL)
        
        sbs4mid.Add(text2, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4mid.Add(self.editPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        #sbs4mid.Add(self.testPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        sbs4right = wx.BoxSizer(wx.VERTICAL)
        
        self.selectedColorLeft = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", size=(40,40), enable=False)
        self.selectedColorRight = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", size=(40,40), enable=False)
        self.selectedColorLeft.color = 0
        self.selectedColorRight.color = 0

        self.modePixel = wx.RadioButton(self, wx.ID_ANY, "Pixel", style=wx.RB_GROUP)
        self.modeFill = wx.RadioButton(self, wx.ID_ANY, "Floodfill")
        self.modeReplace = wx.RadioButton(self, wx.ID_ANY, "Replace")
        
        sbs4right.Add(text3, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4right.Add(self.selectedColorLeft, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        sbs4right.Add(text4, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4right.Add(self.selectedColorRight, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        sbs4right.Add(text5, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4right.Add(self.modePixel, 0, wx.LEFT | wx.BOTTOM, 5)
        sbs4right.Add(self.modeFill, 0, wx.LEFT | wx.BOTTOM, 5)
        sbs4right.Add(self.modeReplace, 0, wx.LEFT | wx.BOTTOM, 5)
        sbs4right.Add(self.switchButton, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        sbs4.AddSizer(sbs4left, 0, wx.ALL ^ wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        sbs4.AddSizer(sbs4mid, 1, wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        sbs4.AddSizer(sbs4right, 0, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        
        # ------------------------
        
        self.animPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=3, bg=None, edit=False)
        #self.animPanel.buffer = wx.EmptyBitmap(*self.animPanel.GetSize())
        #self.animPanel.refreshSprite(self.rom.data["menu_icons"][0].pixels
        #self.animPanel.Refresh()
    
        self.animDelays = [250]
        self.animFrame = 0
        self.animCur = 0
        
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.changeAnim(0)
        
        sbs5.Add(self.animPanel, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        # ------------------------
        
        """self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        sbs6.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)"""
        
        # -----------------------
        
        midSizer = wx.BoxSizer(wx.HORIZONTAL)
        midRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        midSizer.AddSizer(sbs4, 0, flag=wx.EXPAND)
        midRightSizer.AddSizer(sbs5, 1, flag=wx.EXPAND)
        midSizer.AddSizer(midRightSizer, 1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        #self.Sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        #self.sizer.AddSizer(sbs1, pos=(1,0))
        #self.sizer.AddSizer(sbs2, pos=(1,1), flag=wx.EXPAND)
        self.sizer.AddSizer(midSizer, pos=(0,0), span=(1,2))
        #self.sizer.AddSizer(sbs6, pos=(3,0), span=(1,2), flag=wx.EXPAND)
        
        #self.changeEditGlyph(self.rom.fontOrder[0])
        
        self.changeIcon(0)
        
        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.iconList.GetId(), self.OnSelectIcon)
        
        wx.EVT_RADIOBUTTON(self, self.modePixel.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeFill.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeReplace.GetId(), self.OnSelectMode)

        wx.EVT_BUTTON(self, self.importButton.GetId(), self.OnImportImage)
        wx.EVT_BUTTON(self, self.exportButton.GetId(), self.OnExportImage)
        
        wx.EVT_BUTTON(self, self.switchButton.GetId(), self.OnSwitchFrame)
        
        wx.EVT_TIMER(self, self.timer.GetId(), self.TimerTest)
        
        #wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        #wx.EVT_TEXT(self, self.paletteList.GetId(), self.OnRenamePalette)
        
        #wx.EVT_SLIDER(self, -1, self.OnChangeColor)
        #wx.EVT_SPINCTRL(self, -1, self.OnChangeColor)
        
        #wx.EVT_BUTTON(self, self.copyButton.GetId(), self.OnCopyColor)
        #wx.EVT_BUTTON(self, self.pasteButton.GetId(), self.OnPasteColor)
        
        #wx.EVT_LISTBOX(self, self.bankList.GetId(), self.OnSelectBank)
        #wx.EVT_LISTBOX(self, self.lineList.GetId(), self.OnSelectLine)
        #wx.EVT_TEXT(self, self.editBox.GetId(), self.OnEditText)
        
        self.printed = False
    
    def OnShow(self, evt):
        for p in range(16):
            self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
            self.colorPanels[p].Refresh()
        self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        self.selectedColorLeft.Refresh()
        self.selectedColorRight.Refresh()

    def OnImportImage(self, evt):
        
        size = self.editPanel.bmp.GetSize()
        
        dlg = wx.FileDialog(self, "Import 16-color %ix%i GIF" % (size[0], size[1]), "", "", "*.gif", wx.OPEN)
        
        if dlg.ShowModal() == wx.ID_OK:
            
            fn = dlg.GetPath()
            
            try:
                
                img = Image.open(fn)
                imgw, imgh = img.size
                imgpal = img.getpalette()
                
                if img.size != size:
                    
                    wx.MessageDialog(self, "%s is %ix%i and should be %ix%i." % (fn, imgw, imgh, size[0], size[1]), self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()
                
                elif img.format != "GIF" or imgpal == None:
                    
                    wx.MessageDialog(self, "%s is not a GIF or is improperly formatted." % fn, self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()
                    
                else:
                    
                    imgdata = list(img.getdata())
                    pixels = "".join(["%x" % d for d in imgdata])
                    pixels = [pixels[i:i+size[0]] for i in range(0, size[0]*size[1], size[0])]
                    
                    if self.frame == 0:
                        self.icon.pixels = pixels
                        self.icon.raw_pixels = "".join(self.icon.convertFromPixelRows(pixels))
                    else:
                        self.icon.pixels2 = pixels
                        self.icon.raw_pixels2 = "".join(self.icon.convertFromPixelRows(pixels))
                        
                    
                    
                    """newtiles = [None]*len(self.curFrame.tiles)
                    order = self.curFrame.getTileOrder(imgw/8, imgh/8)
                    for i in range(len(newtiles)):
                        newtiles[order[i]] = self.curFrame.tiles[i]
                    self.curFrame.tiles = newtiles"""
                    
                    # ------------------
                    
                    self.changeIcon()
                    
                    self.changeColors()
                    
                    self.modify()
                    
                del img
                
            except IOError, e:
                
                wx.MessageDialog(self, "%s is not a GIF or is improperly formatted." % fn, self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()

        
    def OnExportImage(self, evt):
        
        size = self.editPanel.bmp.GetSize()
        
        dlg = wx.FileDialog(self, "Export 16-color %ix%i GIF" % (size[0], size[1]), "", "", "*.gif", wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            
            fn = dlg.GetPath()
            
            img = Image.new("P", size)
            img.putdata([int(a, 16) for pr in self.editPanel.pixels for a in pr])

            p = [v for rt in self.editPanel.palette.rgbaTuples() for v in rt[:3]]
            p += [0] * (768 - len(p))
            
            img.putpalette(p)
            img.save(fn, "GIF")
            
    def TimerTest(self, evt):
        
        self.animFrame ^= 1
        self.changeAnimIcon()
        
        #if not self.printed:
        #    print "\n".join(dir(evt))
        #    self.printed = True
            
    def changeColors(self):
        palette = self.palette
        for c in range(len(self.colorPanels)):
            self.colorPanels[c].SetBackgroundColour(palette.colors[c])
            self.colorPanels[c].Refresh()

    def changeEditColor(self, button, num):
        
        if button == 0:
            self.color_left = num
        else:
            self.color_right = num

        button = [self.selectedColorLeft, self.selectedColorRight][button]
        button.color = num
        
        button.SetBackgroundColour(self.palette.colors[num])
        button.Refresh()
        
    def refreshPixels(self):
        
        """h = self.icon.hexlify()
        self.symbolsBox.SetValue(h)"""

        #self.menuList.Clear()
        #self.menuList.Append(`len(self.icon.raw_bytes)`)
        #self.menuList.Append(`len(h)`)
        
        #self.testPanel.refreshSprite(self.rom.iconSubroutine(h).pixels
        #self.testPanel.Refresh()

    def OnSelectMode(self, evt):

        l = [self.modePixel.GetId(), self.modeFill.GetId(), self.modeReplace.GetId()]
        self.mode = l.index(evt.GetId())
        
    def OnSelectIcon(self, evt):
        self.changeIcon(evt.GetSelection())
    
    def OnSwitchFrame(self, evt):
        self.frame ^= 1
        self.changeIcon(self.curIconIdx)
        
    def changeIcon(self, num=None):
        
        if num is not None:
            
            self.curIconIdx = num
            if not self.rom.data["menu_icons"][num].loaded:
                self.rom.getMenuIcons(num, num)
                
            self.icon = self.rom.data["menu_icons"][num]
        
        if self.frame == 0:
            self.editPanel.refreshSprite(self.icon.pixels)
        else:
            self.editPanel.refreshSprite(self.icon.pixels2)
        
        self.updateModifiedIndicator(self.icon.modified)
        
        self.editPanel.Refresh()
        self.refreshPixels()
    
    def changeAnim(self, num):
        self.animCur = num
        self.timer.Start(self.animDelays[num])
        
    def changeAnimIcon(self):

        if self.animFrame == 0:
            self.animPanel.refreshSprite(self.icon.pixels)
        else:
            self.animPanel.refreshSprite(self.icon.pixels2)
            
        self.animPanel.Refresh()
        
    def getCurrentSpriteObject(self):
        return self.icon
        
    def getCurrentData(self):
        return self.icon
        
    changeSelection = changeIcon