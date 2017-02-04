import wx, rompanel, binascii
import wx.lib.scrolledpanel
import sys
sys.path.insert(0, '../')
import data

from PIL import Image

h2i = lambda i: int(i, 16)

class TilePanel(rompanel.ROMPanel):
    
    frameTitle = "Tileset Editor"
    
    def init(self):
        
        self.palette = self.rom.data["palettes"][0]
        
        #self.side = 0
        #self.frame = 0
        self.mode = 0
        
        self.color_left = 0
        self.color_right = 0
        
        self.tileset = None
        self.tile = None
        self.curTile = 0
        
        # -------------------------------
        
        #self.rom.data["sprites"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit map tile graphics.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Tools"), wx.VERTICAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Maps using this tileset"), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Tile block editor"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.HORIZONTAL)
        sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Tileset"), wx.VERTICAL)
        #sbs5.StaticBox.SetSize((0,0))
        #sbs6 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        """self.tilesetList = wx.ComboBox(self, wx.ID_ANY, size=(150,-1))
        self.tilesetList.AppendItems([s.name for s in self.rom.data["tilesets"]])
        self.tilesetList.SetSelection(0)
        
        sbs1.Add(self.tilesetList, 0, wx.ALL, 10)
        #sbs1.AddSizer(radioSizer, 0, wx.LEFT | wx.EXPAND, 35)
        sbs1.Add((0,10))"""

        # -----------------------
        
        self.mapList = wx.ListBox(self, wx.ID_ANY, size=(150,80))
        sbs2.Add(self.mapList, 1, wx.ALL, 10)

        # -----------------------
        
        """self.charList = wx.ListBox(self, wx.ID_ANY, size=(200,40))
        sbs2.Add(self.charList, 1, wx.ALL, 10)

        # -----------------------
        
        animButtonSizer = wx.FlexGridSizer(3,2)
        self.animButtons = []
        for i,bt in enumerate(["Walk", "Run", "Nod", "Shake", "Shock", "Jump"]):
            b = wx.Button(self, wx.ID_ANY, bt, size=(40,20))
            if i > 1:
                b.Enable(False)
            self.animButtons.append(b)
            animButtonSizer.Add(b, flag=wx.ALL, border=5)
            
        sbs3.AddSizer(animButtonSizer, 0)
        
        # -----------------------"""
        
        text1 = wx.StaticText(self, -1, "Colors")
        text2 = wx.StaticText(self, -1, "Tile (Color 0 = trans)")
        text3 = wx.StaticText(self, -1, "Left-Click")
        text4 = wx.StaticText(self, -1, "Right-Click")
        text5 = wx.StaticText(self, -1, "Mode")
        text6 = wx.StaticText(self, -1, "Palette")
        
        self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 8, 8, self.palette, scale=20, bg=16, func=self.OnEditTile)
        wx.EVT_MOUSE_EVENTS(self.editPanel, self.editPanel.func)
        
        #self.testPanel = rompanel.SpritePanel(self, wx.ID_ANY, 8, 8, self.palette, scale=24, bg=16)
        
        self.colorPanels = []
        for p in range(16):
            self.colorPanels.append(rompanel.ColorPanel2(self, wx.ID_ANY, "#000000", num=p))
        
        self.paletteList = wx.ComboBox(self, wx.ID_ANY, size=(150,-1))
        self.paletteList.AppendItems([s.name for s in self.rom.data["palettes"]])
        self.paletteList.SetSelection(0)
        
        #self.commandText = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        
        sbs4left = wx.BoxSizer(wx.VERTICAL)
        
        colorSizer = wx.FlexGridSizer(8,2)
        colorSizer.AddMany(self.colorPanels)
        
        sbs4left.Add(text1, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4left.AddSizer(colorSizer, 0)
        sbs4left.Add(text6, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        sbs4mid = wx.BoxSizer(wx.VERTICAL)
        
        sbs4mid.Add(text2, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4mid.Add(self.editPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        sbs4mid.Add(self.paletteList, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER | wx.EXPAND, 5)
        #sbs4mid.Add(self.testPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        sbs4right = wx.BoxSizer(wx.VERTICAL)
        
        self.selectedColorLeft = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", size=(40,40))
        self.selectedColorRight = rompanel.ColorPanel(self, wx.ID_ANY, "#000000", size=(40,40))
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
        
        sbs4.AddSizer(sbs4left, 0, wx.ALL ^ wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        sbs4.AddSizer(sbs4mid, 1, wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        sbs4.AddSizer(sbs4right, 0, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        
        # ------------------------
        
        tps = wx.GridSizer(3,3)
        
        self.tilePanels = []
        for p in range(9):
            tp = rompanel.SpritePanel(self, wx.ID_ANY, 8, 8, self.palette, scale=4, bg=16, func=self.OnChangeLayoutTile)
            tp.num = 0
            self.tilePanels.append(tp)
            tps.Add(tp)
        
        sbs3.AddSizer(tps, wx.ALL, 5)
        
        # ------------------------
        
        self.importButton = wx.Button(self, wx.ID_ANY, "Import", size=(40,20))
        self.exportButton = wx.Button(self, wx.ID_ANY, "Export", size=(40,20))
        
        #self.importButton.Enable(False)
        #self.exportButton.Enable(False)
        
        sbs1.Add(self.importButton, 0, wx.TOP | wx.ALIGN_CENTER, 5)
        sbs1.Add(self.exportButton, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        # ------------------------

        #tps2 = wx.GridSizer(8,16)
        #tps2 = wx.GridSizer(1,1)
        
        #scroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(400,250))
        #scroll.SetupScrolling(scroll_x = False)
        #scroll.SetScrollRate(0,1)
        
        self.tilesetPanel = rompanel.SpritePanel(self, wx.ID_ANY, 8*16, 8*8, self.palette, scale=3, bg=16, func=self.OnClickTilesetPanel, grid=8)
        #self.tilesetCheckPanel = rompanel.SpritePanel(self, wx.ID_ANY, 8*16, 8*8, self.palette, scale=3, bg=16, func=self.OnClickTilesetPanel, grid=8)
        #tps2.Add(self.tilesetPanel)
        #self.tilesetPanels = []
        #for p in range(128):
        #    tp = rompanel.SpritePanel(scroll, wx.ID_ANY, 8, 8, self.palette, scale=3, bg=16, func=self.OnClickTilesetPanel, grid=8)
        #    tp.index = p
        #    self.tilesetPanels.append(tp)
        #    tps2.Add(tp)
        
        #scroll.SetSizer(tps2)
        #scroll.Layout()
        #scroll.Fit()
        sbs5.Add(self.tilesetPanel, 1, wx.ALL | wx.EXPAND, 5)
        #sbs5.Add(self.tilesetCheckPanel, 1, wx.ALL | wx.EXPAND, 5)

        # ------------------------
        
        """self.animPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=3, bg=None, edit=False)
        #self.animPanel.buffer = wx.EmptyBitmap(*self.animPanel.GetSize())
        self.animPanel.refreshSprite(self.rom.data["sprites"][0].pixels
        self.animPanel.Refresh()
    
        self.animDelays = [250, 150, 50, 50, 50, 50]
        self.animFrame = 0
        self.animCur = 0
        
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.changeAnim(0)
        
        sbs5.Add(self.animPanel, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        # ------------------------"""
        
        #self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        #sbs6.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------
        
        #self.testCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        #self.testCtrl2 = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        
        # -----------------------
        
        #midSizer = wx.BoxSizer(wx.HORIZONTAL)
        #midRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        #midSizer.AddSizer(sbs4, 0, flag=wx.EXPAND)
        #midRightSizer.AddSizer(sbs5, 1, flag=wx.EXPAND)
        #midRightSizer.AddSizer(sbs3, 1, flag=wx.EXPAND)
        #midSizer.AddSizer(midRightSizer, 1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        topLeftSizer = wx.BoxSizer(wx.VERTICAL)
        #topLeftSizer.AddSizer(sbs1, 0)
        topLeftSizer.AddSizer(sbs2, 1)
        
        topSizer.AddSizer(topLeftSizer, flag=wx.EXPAND | wx.RIGHT, border=5)
        topSizer.Add(sbs4, 0)
        
        bottomSizer.AddSizer(sbs3)
        bottomSizer.AddSizer(sbs5)
        bottomSizer.AddSizer(sbs1)
        
        #self.sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(topSizer, pos=(0,0))
        self.sizer.AddSizer(bottomSizer, pos=(1,0))
        #self.sizer.AddSizer(sbs6, pos=(3,0), flag=wx.EXPAND)
        
        #self.changeEditGlyph(self.rom.fontOrder[0])

        self.changeTileset(0)
        self.changeColors()

        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.tilesetList.GetId(), self.OnSelectTileset)
        wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        #wx.EVT_COMBOBOX(self, self.tileList.GetId(), self.OnSelectTile)
        
        wx.EVT_BUTTON(self, self.importButton.GetId(), self.OnImportImage)
        wx.EVT_BUTTON(self, self.exportButton.GetId(), self.OnExportImage)
        
        #wx.EVT_RADIOBUTTON(self, self.facingRadioUp.GetId(), self.OnSelectFacing)
        #wx.EVT_RADIOBUTTON(self, self.facingRadioSide.GetId(), self.OnSelectFacing)
        #wx.EVT_RADIOBUTTON(self, self.facingRadioDown.GetId(), self.OnSelectFacing)
        
        wx.EVT_RADIOBUTTON(self, self.modePixel.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeFill.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeReplace.GetId(), self.OnSelectMode)
        
        #wx.EVT_BUTTON(self, wx.ID_ANY, self.OnChangeAnim)
        #wx.EVT_BUTTON(self, self.switchButton.GetId(), self.OnSwitchFrame)
        
        #wx.EVT_TIMER(self, self.timer.GetId(), self.TimerTest)
    
    def OnShow(self, evt):
        for p in range(16):
            self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
            self.colorPanels[p].Refresh()
        self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        self.selectedColorLeft.Refresh()
        self.selectedColorRight.Refresh()

    def OnImportImage(self, evt):
        
        size = self.tilesetPanel.bmp.GetSize()
        
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
                    
                    cols = ["#%02x%02x%02x" % (imgpal[i]/16*17, imgpal[i+1]/16*17, imgpal[i+2]/16*17) for i in range(0, 48, 3)]
                    pal = data.Palette()
                    pal.init(cols)
                    self.editPanel.palette = pal
                    self.palette = pal
                    
                    self.tileset.palette = pal
                    
                    imgdata = list(img.getdata())
                    pixels = "".join(["%x" % d for d in imgdata])
                    pixels = [pixels[i:i+size[0]] for i in range(0, size[0]*size[1], size[0])]
                        
                    self.tileset.convertFromPixelRows(pixels)
                    
                    newtiles = [None]*len(self.tileset.tiles)
                    order = self.tileset.getTileOrder(imgw/8, imgh/8)
                    for i in range(len(newtiles)):
                        newtiles[order[i]] = self.tileset.tiles[i]
                    self.tileset.tiles = newtiles
                    
                    # ------------------
                    
                    self.changeTileset()
                    
                    self.changeColors()
                    
                    self.modify()
                    
                del img
                
            except IOError, e:
                
                wx.MessageDialog(self, "%s is not a GIF or is improperly formatted." % fn, self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()

        
    def OnExportImage(self, evt):
        
        size = self.tilesetPanel.bmp.GetSize()
        
        dlg = wx.FileDialog(self, "Export 16-color %ix%i GIF" % (size[0], size[1]), "", "", "*.gif", wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            
            fn = dlg.GetPath()
            
            img = Image.new("P", size)
            img.putdata([int(a, 16) for pr in self.tilesetPanel.pixels for a in pr])

            p = [v for rt in self.editPanel.palette.rgbaTuples() for v in rt[:3]]
            p += [0] * (768 - len(p))
            
            img.putpalette(p)
            img.save(fn, "GIF")
            
    def changeColors(self):
        palette = self.palette
        for c in range(len(self.colorPanels)):
            self.colorPanels[c].SetBackgroundColour(palette.colors[c])
            self.colorPanels[c].Refresh()
        self.editPanel.palette = palette
        self.editPanel.Refresh()
        for c in range(len(self.tilePanels)):
            self.tilePanels[c].palette = palette
        #for c in range(len(self.tilesetPanels)):
        #    self.tilesetPanels[c].palette = palette
        self.tilesetPanel.palette = palette
        self.refreshPixels()

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
        
        #h = self.tileset.hexlify()
        #self.symbolsBox.SetValue(h)
        
        #f = open("spr_in.txt", "wb")
        #f.write(self.sprite.raw_bytes)
        #f.close()
    
        #f = open("spr_out.txt", "wb")
        #f.write(h)
        #f.close()
        
        #self.charList.Clear()
        #self.charList.Append(hex(self.rom.tables["sprites"][int(self.sprite.name.split(" ")[1])*3 + self.side]))
        #self.charList.Append(`len(self.sprite.raw_bytes)`)
        #self.charList.Append(`len(h)`)
        
        #h = h.replace("\n","").replace(" ","").replace(":","")
        
        
        #f = open("%s.txt" % self.tileset.name, "wb")
        #f.write(self.tileset.raw_bytes)
        #f.close()
        
        for p in range(9):
            tp = self.tilePanels[p]
            tp.refreshSprite(self.tileset.tiles[tp.num].pixels)
            tp.Refresh()
        
        self.tilesetPanel.pixels = []
        for tRow in range(8):
            for pRow in range(8):
                row = "".join([self.tileset.tiles[tRow*16+to].pixels[pRow] for to in range(16)])
                self.tilesetPanel.pixels.append(row)
        
        """self.tilesetCheckPanel.pixels = []
        
        for tRow in range(8):
            for pRow in range(8):
                try:
                    row = "".join([self.tsCheck.tiles[tRow*16+to].pixels[pRow] for to in range(16)])
                    self.tilesetCheckPanel.pixels.append(row)
                except IndexError, e:
                    print e"""
        
        #self.tilesetCheckPanel.refreshSprite()
        #self.tilesetCheckPanel.Refresh()
        
        self.tilesetPanel.refreshSprite()
        self.tilesetPanel.Refresh()
            
        #self.testPanel.refreshSprite(self.rom.tilesetSubroutine(h.replace(" ","")).tiles[self.curTile].pixels
        #self.testPanel.Refresh()
    
        pass

    def OnSelectPalette(self, evt):
        self.palette = self.rom.data["palettes"][evt.GetSelection()]
        self.changeColors()
        self.changeEditColor(0, self.color_left)
        self.changeEditColor(1, self.color_right)
        self.refreshPixels()
        
    def OnClickTilesetPanel(self, evt):
        
        obj = evt.GetEventObject()
        
        x = int(evt.GetX() / 8 / obj.scale)
        y = int(evt.GetY() / 8 / obj.scale)
        self.changeTile(y*16+x)
        self.refreshPixels()
    
    def OnEditTile(self, evt):
        
        obj = evt.GetEventObject()
        obj.OnEdit(evt)
        
    def OnSelectMode(self, evt):

        l = [self.modePixel.GetId(), self.modeFill.GetId(), self.modeReplace.GetId()]
        self.mode = l.index(evt.GetId())
        
    def OnSelectTileset(self, evt):
        self.changeTileset(evt.GetSelection())
    
    def OnChangeLayoutTile(self, evt):
        id = evt.GetId()
        for t in self.tilePanels:
            if t.GetId() == id:
                panel = t
                break
        panel.refreshSprite(self.tile.pixels)
        panel.num = self.curTile
        panel.Refresh()
        
    def changeTileset(self, num=None):
        
        if num is not None:
            
            if not self.rom.data["tilesets"][num].loaded:
                self.rom.getTilesets(num, num)
            else:
                #print `self.rom.data["tilesets"][num].tiles[0].pixels`
                pass
                
            self.tileset = self.rom.data["tilesets"][num]
            #print self.tileset.raw_bytes
            #print self.tileset.hexlify()
            self.mapList.Clear()
            mapsUsing = [m.name for m in filter(lambda obj: num in obj.tilesetIdxes, self.rom.data["maps"])]
            self.mapList.AppendItems(mapsUsing)

            #self.tempTileset = self.rom.tilesetSubroutine(self.tileset.hexlify().replace(" ",""))
            
            #self.tileList.Clear()
            #self.tileList.AppendItems([t.name for t in self.tileset.tiles])
            #self.tileList.SetSelection(0)

            for p in range(9):
                tp = self.tilePanels[p]
                tp.num = 0
                tp.Refresh()

        pixels = []
        
        tw = self.tilesetPanel.width / 8
        th = self.tilesetPanel.height / 8
        
        print tw, th
        order = self.tileset.getTileOrder(tw, th)
        
        print len(self.tileset.tiles)
        
        tiles = [self.tileset.tiles[t] for t in order]
        
        for tRow in range(th):
            for pRow in range(8):
                row = "".join([tiles[tRow*tw+to].pixels[pRow] for to in range(tw)])
                pixels.append(row)
        self.tilesetPanel.refreshSprite(pixels, force=True)
        
        self.updateModifiedIndicator(self.tileset.modified)

        self.changeTile()
            
        #self.testCtrl.SetValue(self.tileset.cmdstr)
        #self.testCtrl2.SetValue("\n\n".join(["\n".join(t.pixels) for t in self.tileset.tiles]))
        
    def changeTile(self, num=0):
        
        self.curTile = num
        self.tile = self.tileset.tiles[num]
        
        self.editPanel.refreshSprite(self.tile.pixels)
        self.editPanel.Refresh()
        
        #self.tilesetPanels[num].refreshSprite(self.tile.pixels)
        #self.tilesetPanels[num].Refresh()
        
        self.refreshPixels()
        
        #self.testPanel.refreshSprite(self.tempTileset.tiles[num].pixels
        #self.testPanel.Refresh()
    
    def getCurrentSpriteObject(self):
        return self.tile
    
    def getCurrentData(self):
        return self.tileset
        
    changeSelection = changeTileset