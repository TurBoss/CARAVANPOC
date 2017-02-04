import sys
sys.path.insert(0, '../')

import wx, rompanel, binascii, window
import consts

h2i = lambda i: int(i, 16)

class MapPanel(rompanel.ROMPanel):
    
    frameTitle = "Map Definition Editor"
    
    def init(self):
        
        self.palette = self.rom.data["palettes"][0]
        #self.side = 0
        #self.frame = 0
        self.mode = 0
        
        self.curEditBlock = 0
        self.curListBlockLeft = 0
        self.curListBlockRight = 1
        
        self.curEditBlockPage = 0
        self.curListBlockPage = 0
        
        self.curLeftTile = 0x100
        self.curRightTile = 0x100
        
        self.curInterFlag = 0xc000
        
        self.curViewMode = 0
        self.viewAll = False
        
        self.curMapIdx = 0
        
        self.curTilesetIdx = 0
        self.curAnimTSIdx = 0
        
        self.curEventIdx = 0
        self.curEventType = 0
        
        self.blockEditMode = 0
        
        self.map = self.rom.data["maps"][0]
        
        # -------------------------------
        
        #self.rom.data["sprites"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit maps.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        #sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "1. Select a map."), wx.HORIZONTAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "2. Select a tile to edit."), wx.VERTICAL)
        #sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Change Tile Layout"), wx.VERTICAL)
        #sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "2. Edit the tile."), wx.HORIZONTAL)
        #sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Preview Animation"), wx.VERTICAL)
        #sbs5.StaticBox.SetSize((0,0))
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        """self.mapList = wx.ComboBox(self, wx.ID_ANY, size=(200,-1))
        self.mapList.AppendItems([s.name for s in self.rom.data["maps"]])
        self.mapList.SetSelection(0)
        
        self.mapViewButton = wx.Button(self, wx.ID_ANY, "View Map")
        
        sbs1.Add(self.mapList, 0, wx.ALL, 10)
        sbs1.Add(self.mapViewButton, 0, wx.ALL ^ wx.LEFT, 10)
        #sbs1.AddSizer(radioSizer, 0, wx.LEFT | wx.EXPAND, 35)
        sbs1.Add((0,10))"""
        
        # --------------------------------
        
        # START OF SUB PAGES
        
        self.mainNotebook = sbs2notebook = wx.Notebook(self, -1, size=(500, -1))
        
        genWindow = wx.Window(sbs2notebook, -1)
        self.blockWindow = blockWindow = wx.Window(sbs2notebook, -1)
        layoutWindow = wx.Window(sbs2notebook, -1)
        configWindow = wx.Window(sbs2notebook, -1)
        eventWindow = wx.Window(sbs2notebook, -1)
        animWindow = wx.Window(sbs2notebook, -1)
        #tempWindow = wx.Window(sbs2notebook, -1)
        
        genWndSizer = wx.BoxSizer(wx.VERTICAL)
        blockWndSizer = wx.BoxSizer(wx.VERTICAL)
        layoutWndSizer = wx.BoxSizer(wx.HORIZONTAL)
        configWndSizer = wx.BoxSizer(wx.VERTICAL)
        eventWndSizer = wx.BoxSizer(wx.VERTICAL)
        animWndSizer = wx.BoxSizer(wx.VERTICAL)
        #tempWndSizer = wx.BoxSizer(wx.VERTICAL)
        
        # --------------------------------
        
        sbs2paletteBS = wx.StaticBoxSizer(wx.StaticBox(genWindow, -1, "Palette"), wx.VERTICAL)
        
        self.paletteList = wx.ComboBox(genWindow, wx.ID_ANY, size=(150, -1), style=wx.CB_DROPDOWN)
        self.paletteList.AppendItems([p.name for p in self.rom.data["palettes"] if p.isMapPalette])
        self.paletteList.SetSelection(0)
        
        self.colorPanels = []
        for p in range(16):
            self.colorPanels.append(rompanel.ColorPanel(genWindow, wx.ID_ANY, "#000000", num=p))
        
        colorSizer = wx.FlexGridSizer(2,16)
        for i in range(16):
            colorSizer.Add(wx.StaticText(genWindow, -1, str(i).zfill(2)), 0, wx.ALIGN_CENTER)
        colorSizer.AddMany(self.colorPanels)
        
        #self.bankList = wx.ListBox(self, wx.ID_ANY, size=(120,100))
        #self.bankList.AppendItems(bankNames) #, "u2", "yay")
        
        #self.lineList = wx.ListBox(self, wx.ID_ANY, size=(350,100))
        
        sbs2paletteBS.AddSizer(colorSizer, 0, wx.ALL, 10)
        sbs2paletteBS.Add(self.paletteList, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        
        #sbs1.Add(self.lineList, 0, wx.EXPAND | wx.ALL, 10)
        #sbs1.Add(rompanel.ColorPanel(self, wx.ID_ANY, "#FF0000"), 0, wx.LEFT, 15)

        # ----
        
        """sbs2sizeBS = wx.StaticBoxSizer(wx.StaticBox(genWindow, -1, "Size"), wx.VERTICAL)
        sbs2sizeBSSizer = wx.FlexGridSizer(2, 2)
        
        widthText = wx.StaticText(genWindow, -1, "Width: ")
        heightText = wx.StaticText(genWindow, -1, "Height: ")
        self.mapWidthCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, size=(45,20), min=0, max=64)
        self.mapHeightCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, size=(45,20), min=0, max=64)
        
        sbs2sizeBSSizer.Add(widthText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sbs2sizeBSSizer.Add(self.mapWidthCtrl, 0, wx.TOP | wx.BOTTOM, 3)
        sbs2sizeBSSizer.Add(heightText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sbs2sizeBSSizer.Add(self.mapHeightCtrl, 0, wx.TOP | wx.BOTTOM, 3)
        
        sbs2sizeBS.AddSizer(sbs2sizeBSSizer, 1, wx.EXPAND | wx.ALL, 5)"""
        
        # ----
        
        sbs2tilesetBS = wx.StaticBoxSizer(wx.StaticBox(genWindow, -1, "Tilesets"), wx.VERTICAL)
        sbs2tilesetBSSizer = wx.FlexGridSizer(6, 2)
        
        self.layerChecks = []
        self.tilesetLists = []
        
        ltt = wx.StaticText(genWindow, -1, "Tileset")
        
        sbs2tilesetBSSizer.AddSpacer(0)
        sbs2tilesetBSSizer.Add(ltt, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER, 5)

        for i in range(5):
        
            self.layerChecks.append(wx.CheckBox(genWindow, wx.ID_ANY, " %i" % (i+1)))
            
            # ---
            
            names = [ts.name for ts in self.rom.data["tilesets"]]
            
            tl = wx.ComboBox(genWindow, wx.ID_ANY, size=(150, -1), style=wx.CB_DROPDOWN)
            tl.AppendItems(names)
            tl.SetSelection(0)
            
            self.tilesetLists.append(tl)
            
            # ---
            
            sbs2tilesetBSSizer.Add(self.layerChecks[i], 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            sbs2tilesetBSSizer.Add(self.tilesetLists[i], 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        
            self.layerChecks[i].Enable(False)
        
        sbs2tilesetBS.AddSizer(sbs2tilesetBSSizer, 1, wx.EXPAND)
        
        # ----

        sbs2areaBS = wx.StaticBoxSizer(wx.StaticBox(genWindow, -1, "Areas"), wx.VERTICAL)
        sbs2areaPropSizer = wx.FlexGridSizer(5, 5)
        
        areaListText = wx.StaticText(genWindow, -1, "Area: ")
        self.areaList = wx.ComboBox(genWindow, wx.ID_ANY)
        self.areaAddButton = wx.Button(genWindow, wx.ID_ANY, "Add", size=(40,20))
        self.areaDelButton = wx.Button(genWindow, wx.ID_ANY, "Del", size=(40,20))
        
        sbs2areaTopSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2areaTopSizer.Add(areaListText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        sbs2areaTopSizer.Add(self.areaList, 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sbs2areaTopSizer.Add(self.areaAddButton, 0, wx.ALIGN_CENTER_VERTICAL)
        sbs2areaTopSizer.Add(self.areaDelButton, 0, wx.ALIGN_CENTER_VERTICAL)
        
        self.areaLayer2Check = wx.CheckBox(genWindow, wx.ID_ANY, " Layer 2: ")
        self.areaLayer2ForeRadio = wx.RadioButton(genWindow, wx.ID_ANY, "Foreground", style=wx.RB_GROUP)
        self.areaLayer2BackRadio = wx.RadioButton(genWindow, wx.ID_ANY, "Background")

        self.areaLayer2ForeRadio.context2 = 0
        self.areaLayer2BackRadio.context2 = 255
        
        sbs2areaMidSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2areaMidSizer.Add(self.areaLayer2Check, 1, wx.RIGHT, 5)
        sbs2areaMidSizer.Add(self.areaLayer2ForeRadio, 1, wx.RIGHT, 5)
        sbs2areaMidSizer.Add(self.areaLayer2BackRadio, 1)
        
        areaTLText = wx.StaticText(genWindow, -1, "Top-Left")
        areaBRText = wx.StaticText(genWindow, -1, "Bot-Right")
        areaParaText = wx.StaticText(genWindow, -1, "Parallax")
        areaScrText = wx.StaticText(genWindow, -1, "Scroll")
        
        areaLayer1XText = wx.StaticText(genWindow, -1, "Layer 1 X:")
        areaLayer1YText = wx.StaticText(genWindow, -1, "Layer 1 Y:")
        areaLayer2XText = wx.StaticText(genWindow, -1, "Layer 2 X:")
        areaLayer2YText = wx.StaticText(genWindow, -1, "Layer 2 Y:")
        
        self.areaLayer1X1Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer1Y1Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer1X2Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer1Y2Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer1ParaXCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=2048, size=(54,20))
        self.areaLayer1ParaYCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=2048, size=(54,20))
        self.areaLayer1ScrXCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=-128, max=127, size=(54,20))
        self.areaLayer1ScrYCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=-128, max=127, size=(54,20))
        self.areaLayer2X1Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer2Y1Ctrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=64, size=(42,20))
        self.areaLayer2ParaXCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=2048, size=(54,20))
        self.areaLayer2ParaYCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=0, max=2048, size=(54,20))
        self.areaLayer2ScrXCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=-128, max=127, size=(54,20))
        self.areaLayer2ScrYCtrl = wx.SpinCtrl(genWindow, wx.ID_ANY, min=-128, max=127, size=(54,20))
        
        sbs2areaPropSizer.AddSpacer(0)
        sbs2areaPropSizer.Add(areaTLText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        sbs2areaPropSizer.Add(areaBRText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        sbs2areaPropSizer.Add(areaParaText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        sbs2areaPropSizer.Add(areaScrText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        
        sbs2areaPropSizer.Add(areaLayer1XText, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sbs2areaPropSizer.Add(self.areaLayer1X1Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1X2Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1ParaXCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1ScrXCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        
        sbs2areaPropSizer.Add(areaLayer1YText, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sbs2areaPropSizer.Add(self.areaLayer1Y1Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1Y2Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1ParaYCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer1ScrYCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        
        sbs2areaPropSizer.Add(areaLayer2XText, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sbs2areaPropSizer.Add(self.areaLayer2X1Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.AddSpacer(0)
        sbs2areaPropSizer.Add(self.areaLayer2ParaXCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer2ScrXCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        
        sbs2areaPropSizer.Add(areaLayer2YText, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sbs2areaPropSizer.Add(self.areaLayer2Y1Ctrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.AddSpacer(0)
        sbs2areaPropSizer.Add(self.areaLayer2ParaYCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        sbs2areaPropSizer.Add(self.areaLayer2ScrYCtrl, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER, 2)
        
        areaMusicText = wx.StaticText(genWindow, wx.ID_ANY, " Music: ")
        self.areaMusicList = wx.ComboBox(genWindow, wx.ID_ANY, size=(200,-1))
        self.areaMusicList.AppendItems([m.name for m in self.rom.data["music"]])
        self.areaMusicList.SetSelection(0)
        
        sbs2areaBotSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2areaBotSizer.Add(areaMusicText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        sbs2areaBotSizer.Add(self.areaMusicList, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        sbs2areaBSSizer = wx.BoxSizer(wx.VERTICAL)
        
        sbs2areaBSSizer.AddSizer(sbs2areaTopSizer, 0, wx.BOTTOM | wx.EXPAND, 5)
        sbs2areaBSSizer.AddSizer(sbs2areaBotSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
        sbs2areaBSSizer.AddSizer(sbs2areaMidSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
        sbs2areaBSSizer.AddSizer(sbs2areaPropSizer, 0, wx.ALIGN_CENTER, 5)
        
        sbs2areaBS.AddSizer(sbs2areaBSSizer, 1, wx.ALL | wx.EXPAND, 5)
        
        self.areaAddButton.Enable(False)
        self.areaDelButton.Enable(False)
        
        # --------------------------------

        sbs2blockTSListBS = wx.StaticBoxSizer(wx.StaticBox(blockWindow, -1, "Tilesets used by this map"), wx.VERTICAL)
        
        self.blockTSList = wx.ComboBox(blockWindow, wx.ID_ANY, size=(200,-1))
        
        sbs2blockTSListBS.Add(self.blockTSList, 0, wx.EXPAND | wx.ALL, 5)
        
        # -----
        
        sbs2blockEditorBS = wx.StaticBoxSizer(wx.StaticBox(blockWindow, -1, "2. Edit the block."), wx.VERTICAL)
        
        self.blockPanel = rompanel.SpritePanel(blockWindow, wx.ID_ANY, 24, 24, self.palette, scale=3, bg=16, func=self.OnChangeBlockTile, edit=True)
        
        sbs2blockEditorBS.Add(self.blockPanel, 0, wx.ALL, 5)
        
        # -----
        
        sbs2blockTSBS = wx.StaticBoxSizer(wx.StaticBox(blockWindow, -1, "Tileset"), wx.HORIZONTAL)
        tsScroll = wx.lib.scrolledpanel.ScrolledPanel(blockWindow, -1, size=(250,120))
        tsScroll.SetupScrolling()
        tsScroll.SetScrollRate(1,1)
        
        self.tilesetPanel = rompanel.SpritePanel(tsScroll, wx.ID_ANY, 128, 64, self.palette, scale=3, bg=16, func=self.OnClickBlockTilesetPanel, edit=True, grid=8)
        
        editTileSizer = wx.BoxSizer(wx.VERTICAL)
        
        text1 = wx.StaticText(blockWindow, -1, "Left-Click")
        text2 = wx.StaticText(blockWindow, -1, "Right-Click")
        
        self.blockEditLeftPanel = rompanel.SpritePanel(blockWindow, wx.ID_ANY, 8, 8, self.palette, scale=6, bg=16, func=None)
        self.blockEditRightPanel = rompanel.SpritePanel(blockWindow, wx.ID_ANY, 8, 8, self.palette, scale=6, bg=16, func=None)
        
        editTileSizer.Add(text1, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        editTileSizer.Add(self.blockEditLeftPanel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        editTileSizer.Add(text2, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        editTileSizer.Add(self.blockEditRightPanel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        
        tsScrollSizer = wx.BoxSizer(wx.VERTICAL)
        tsScrollSizer.Add(self.tilesetPanel)
        
        tsScroll.SetSizer(tsScrollSizer)
        tsScroll.Layout()
        tsScroll.Fit()
        
        sbs2blockTSBS.Add(tsScroll, 0, wx.ALL | wx.EXPAND, 5)
        sbs2blockTSBS.Add(editTileSizer, 0, wx.LEFT, 10)
        
        # -----

        sbs2blockListBS = wx.StaticBoxSizer(wx.StaticBox(blockWindow, -1, "1. Select a block."), wx.HORIZONTAL)
        #self.blockEditScroll = blockEditScroll = wx.lib.scrolledpanel.ScrolledPanel(blockWindow, -1, size=(100,200))
        #blockEditScroll.SetupScrolling(scroll_x = False)
        #blockEditScroll.SetScrollRate(0,77)
        
        self.blockEditSlider = wx.Slider(blockWindow, wx.ID_ANY, 0, 0, 15, style=wx.SL_VERTICAL)
        self.blockEditSlider.SetPageSize(1)
        
        self.blockEditPosText = wx.StaticText(blockWindow, -1, "0")
        self.blockEditMaxText = wx.StaticText(blockWindow, -1, "0")
        
        #self.blockEditNextButton = wx.Button(blockWindow, wx.ID_ANY, "Next", size=(40,20))
        self.blockEditAddButton = wx.Button(blockWindow, wx.ID_ANY, "Add", size=(40,20))
        self.blockEditDelButton = wx.Button(blockWindow, wx.ID_ANY, "Delete", size=(40,20))
        self.blockEditAddButton.Enable(False)
        self.blockEditDelButton.Enable(False)
        
        self.blockEditSlider.context = "edit"
        
        self.blockEditPanels = []
        self.blockEditText = []
        
        self.blockEditListSizer = blockEditListSizer = wx.BoxSizer(wx.VERTICAL)
        
        for idx in range(0, 3):
            
            p = rompanel.SpritePanel(blockWindow, wx.ID_ANY, 24, 24, self.palette, scale=2, bg=None, xpad=4, ypad=4, func=self.OnClickBlockEditPanel)
            p.index = idx
            self.blockEditPanels.append(p)
            
            t = wx.StaticText(blockWindow, -1, `idx`)
            self.blockEditText.append(t)
        
            blockEditListSizer.Add(t, 0, wx.ALIGN_CENTER)
            blockEditListSizer.Add(p, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
            
        #print "\n".join(dir(blockEditScroll))
        
        self.blockEditListSelSizer = blockEditListSelSizer = wx.BoxSizer(wx.VERTICAL)
        blockEditListSelSizer.Add(self.blockEditPosText, 0, wx.ALIGN_CENTER)
        blockEditListSelSizer.Add(self.blockEditSlider, 1, wx.ALIGN_CENTER)
        blockEditListSelSizer.Add(self.blockEditMaxText, 0, wx.ALIGN_CENTER)
        
        blockEditListSizer.AddSizer(self.blockEditAddButton, 0, wx.ALL | wx.ALIGN_CENTER)
        blockEditListSizer.AddSizer(self.blockEditDelButton, 0, wx.ALL | wx.ALIGN_CENTER)
        
        sbs2blockListBS.AddSizer(blockEditListSelSizer, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        sbs2blockListBS.AddSizer(blockEditListSizer, 1, wx.EXPAND | wx.RIGHT, 5)
        
        # --------------------------------
        
        
        # -----
        
        #layoutWindowSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        #layoutWindow.SetSizer(layoutWindowSizer)
        
        #self.mapEditScroll = mapEditScroll = wx.lib.scrolledpanel.ScrolledPanel(mapWindow, -1, size=(100,200))
        #mapEditScroll.SetupScrolling(scroll_x = False)
        #mapEditScroll.SetScrollRate(0,77)
        
        self.blockListSlider = wx.Slider(layoutWindow, wx.ID_ANY, 0, 0, 15, style=wx.SL_HORIZONTAL)
        
        self.blockListPosText = wx.StaticText(layoutWindow, -1, "0")
        self.blockListMaxText = wx.StaticText(layoutWindow, -1, "0")
        
        self.blockListSlider.context = "list"
        
        self.blockListPanels = []
        self.blockListText = []
        
        self.blockListSizer = blockListSizer = wx.FlexGridSizer(7,8)

        self.blockListLeftText = wx.StaticText(layoutWindow, -1, "L (0)")
        self.blockListRightText = wx.StaticText(layoutWindow, -1, "R (0)")
        
        self.blockListLeftPanel = rompanel.SpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1.5, bg=17, func=self.OnClickBlockSelPanel)
        self.blockListRightPanel = rompanel.SpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1.5, bg=18, func=self.OnClickBlockSelPanel)
        
        self.blockListOverText = wx.StaticText(layoutWindow, -1, "Block 000")
        self.blockListOverText.SetFont(self.GetTopLevelParent().editFont)
        
        self.blockListSliderSizer = blockListSliderSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        blockListSliderSizer.Add(self.blockListPosText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        blockListSliderSizer.Add(self.blockListSlider, 1)
        blockListSliderSizer.Add(self.blockListMaxText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        blockListSliderSizer.Add(self.blockListOverText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.LEFT, 10)
        
        numC = blockListSizer.GetCols()
        numR = blockListSizer.GetRows()
        
        for idx in range(0, numC*numR, numC):
            
            #for c in range(0, numC):
            #    t = wx.StaticText(layoutWindow, -1, `idx+c`)
            #    self.blockListText.append(t)
            #    blockListSizer.Add(t, 0, wx.ALIGN_CENTER)

            for c in range(0, numC):
                
                p = rompanel.SpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1.5, bg=16, func=self.OnClickBlockListPanel, edit=True, grid=24)
                p.index = idx+c
                self.blockListPanels.append(p)
                blockListSizer.Add(p, 0, wx.ALIGN_CENTER)
            
        #print "\n".join(dir(mapEditScroll))
        
        layoutWindowSizer2 = wx.StaticBoxSizer(wx.StaticBox(layoutWindow, -1, "Block List"), wx.HORIZONTAL)
        layoutBlockListSizer = wx.BoxSizer(wx.VERTICAL)
        
        layoutBlockListSizer.AddSizer(blockListSizer, 1, wx.EXPAND)
        layoutBlockListSizer.AddSizer(blockListSliderSizer, 0, wx.EXPAND | wx.ALIGN_CENTER)
        
        #layoutWindowSizer2.AddSizer(blockListSelSizer, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)
        layoutWindowSizer2.AddSizer(layoutBlockListSizer, 0, wx.ALL, 5)
    
        #layoutWindowSizer.Layout()
        
        # -
        
        layoutWindowSizer = wx.BoxSizer(wx.VERTICAL)
        
        layoutWindowSubSizer = wx.BoxSizer(wx.VERTICAL)
        
        layoutWindow.SetSizer(layoutWindowSizer)
        
        layoutInterBlockSizer = wx.StaticBoxSizer(wx.StaticBox(layoutWindow, -1, "Selected Blocks"), wx.VERTICAL)
        layoutInterObsSizer = wx.StaticBoxSizer(wx.StaticBox(layoutWindow, -1, "Movement Data"), wx.VERTICAL)
        layoutInterEventSizer = wx.StaticBoxSizer(wx.StaticBox(layoutWindow, -1, "Event Data"), wx.VERTICAL)
        
        layoutInterObsGrid = wx.GridBagSizer()
        layoutInterEventGrid = wx.GridBagSizer()
        
        radios = [None] * 12
        texts = ["Obstructed", "* Stairs", "Warp", "Trigger", 
        "Table/Desk", "Chest", "Barrel", "Vase", 
        "Searchable", "Perm Copy", "Temp Copy", "Undo Copy"]

        self.interBlockRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "Graphical Block", style=wx.RB_GROUP)
        self.interBlockRadio.context = 0x03ff
        
        radios[0] = self.interObsRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[1] = self.interStairsRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[2] = self.interWarpRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[3] = self.interTriggerRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[4] = self.interTableRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[5] = self.interChestRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[6] = self.interBarrelRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[7] = self.interVaseRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[8] = self.interSearchRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[9] = self.interCopyRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[10] = self.interShowRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        radios[11] = self.interHideRadio = wx.RadioButton(layoutWindow, wx.ID_ANY, "")
        
        masks = [0xc000, 0x4000, 0x1000, 0x1400, 0x2800, 0x1800, 0x3000, 0x2c00, 0x1c00,  0x0400, 0x0800, 0x0c00]
        
        layoutInterObsGrid.SetVGap(1)
        layoutInterEventGrid.SetVGap(1)

        layoutInterObsGrid.AddGrowableCol(1, 1)
        layoutInterEventGrid.AddGrowableCol(1, 1)
        #layoutInterObsGrid.SetFlexibleDirection(wx.HORIZONTAL)
        
        for i in range(len(masks)):
            
            mask = masks[i]
            radios[i].SetLabel(texts[i])
            radios[i].context = mask
            if i%2:
                radios[i].SetLayoutDirection(wx.Layout_RightToLeft)
                
            if i < 2:
                sizer = layoutInterObsGrid
                ofs = 0
            else:
                sizer = layoutInterEventGrid
                ofs = 2
        
            flag = [wx.ALIGN_LEFT, wx.ALIGN_RIGHT][i%2]
            flag2 = [wx.RIGHT, wx.LEFT][i%2]
            
            p = rompanel.SpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1, bg=None, func=None, draw=self.drawMapData)
            p.special = mask
                
            sizer.Add(p, flag=flag2 | wx.ALIGN_CENTER_VERTICAL, border=5, pos=(i / 2 * 2 - ofs, (i%2) * 2), span=(2,1))
            sizer.Add(radios[i], flag=wx.ALIGN_CENTER_VERTICAL | flag, pos=(i - ofs, 1))
        
        layoutInterObsSizer.AddSizer(layoutInterObsGrid, 0)#1, wx.EXPAND)
        layoutInterEventSizer.AddSizer(layoutInterEventGrid, 0)#1, wx.EXPAND)

        self.blockListSelSizer = blockListSelSizer = wx.FlexGridSizer(2,2)
        
        blockListSelSizer.Add(self.blockListLeftText, 1, wx.ALIGN_CENTER)
        blockListSelSizer.Add(self.blockListRightText, 1, wx.ALIGN_CENTER)
        blockListSelSizer.Add(self.blockListLeftPanel, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 10)
        blockListSelSizer.Add(self.blockListRightPanel, 1, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 10)
        
        layoutInterBlockSizer.Add(self.interBlockRadio, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        layoutInterBlockSizer.AddSizer(blockListSelSizer, 1, wx.ALIGN_CENTER)
        
        layoutWindowSubSizer.AddSizer(layoutInterBlockSizer, 0, wx.ALL ^ wx.BOTTOM | wx.EXPAND | wx.ALIGN_CENTER, 5)
        layoutWindowSubSizer.AddSizer(layoutInterObsSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER, 5)
        layoutWindowSubSizer.AddSizer(layoutInterEventSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER, 5)
        
        layoutWndSizer.AddSizer(layoutWindowSubSizer, 0, wx.LEFT, 10)
        layoutWndSizer.AddSizer(layoutWindowSizer2, 0, wx.ALL, 5)
        #layoutSizer.Layout()
        
        #layoutInterObsGrid.RecalcSizes()
        #print "\n".join(dir(layoutInterObsGrid))
        #print `layoutInterObsGrid.GetRowHeights()`
        #raw_input()
        
        # --------------------------------
        
        sbs2eventSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sbs2eventCol1Sizer = wx.BoxSizer(wx.VERTICAL)
        
        #eventSetupBS = wx.StaticBoxSizer(wx.StaticBox(eventWindow, -1, "Select setup, if applicable."), wx.VERTICAL)
        
        #eventSetupPropSizer = wx.FlexGridSizer(2,2)
        
        #self.eventConfigNameText = wx.StaticText(eventWindow, -1, "Name:")
        #self.eventConfigFlagCheck = wx.CheckBox(eventWindow, wx.ID_ANY, " Flag:")
        
        #self.eventConfigNameCtrl = wx.TextCtrl(eventWindow, wx.ID_ANY)
        #self.eventConfigFlagCtrl = wx.SpinCtrl(eventWindow, wx.ID_ANY, min=0, max=2047, size=(55,20))
        
        #eventSetupPropSizer.Add(self.eventConfigNameText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        #eventSetupPropSizer.Add(self.eventConfigNameCtrl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        #eventSetupPropSizer.Add(self.eventConfigFlagCheck, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        #eventSetupPropSizer.Add(self.eventConfigFlagCtrl, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        #eventSetupBS.Add(eventSetupPropSizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
        
        # ----
        
        self.eventTypeBS = eventTypeBS = wx.StaticBoxSizer(wx.StaticBox(eventWindow, -1, "Event Type"), wx.VERTICAL)
        
        eventTypeRow1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.eventTypeList = wx.ComboBox(eventWindow, wx.ID_ANY, size=(160,-1))
        
        self.eventTypeList.AppendItems(
            [
                "Warps", 
                "Block Copies",
                "Obtainable Items", 
                "NPCs",
                "Scene Triggers",
                "Books, Signs, Etc.",
            ])
            
        self.eventTypeList.SetSelection(0)

        self.eventConfigBS = eventConfigBS = wx.StaticBoxSizer(wx.StaticBox(eventWindow, -1, "Configuration (if applicable)"), wx.VERTICAL)
        
        self.eventConfigList = wx.ListBox(eventWindow, wx.ID_ANY, size=(160,58))
        
        self.eventConfigAddButton = wx.Button(eventWindow, wx.ID_ANY, "Add", size=(50,20))
        self.eventConfigCopyButton = wx.Button(eventWindow, wx.ID_ANY, "Copy", size=(50,20))
        self.eventConfigDelButton = wx.Button(eventWindow, wx.ID_ANY, "Delete", size=(50,20))
        
        eventConfigButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        eventConfigButtonSizer.Add(self.eventConfigAddButton, 0)
        eventConfigButtonSizer.Add(self.eventConfigCopyButton, 0)
        eventConfigButtonSizer.Add(self.eventConfigDelButton, 0)
        
        self.eventBS = eventBS = wx.StaticBoxSizer(wx.StaticBox(eventWindow, -1, "Event"), wx.VERTICAL)
        
        self.eventList = wx.ListBox(eventWindow, wx.ID_ANY, size=(160,82))
        
        #self.eventSelectCtrl = wx.SpinCtrl(eventWindow, wx.ID_ANY, min=0, max=20, size=(45,20))
        
        eventTypeRow1Sizer.Add(self.eventTypeList, 1, wx.RIGHT | wx.LEFT, 5)
        #ventTypeRow1Sizer.Add(self.eventSelectCtrl, 0)

        eventConfigBS.Add(self.eventConfigList, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        eventConfigBS.AddSizer(eventConfigButtonSizer, 0, wx.ALIGN_CENTER)
        
        self.eventAddButton = wx.Button(eventWindow, wx.ID_ANY, "Add", size=(50,20))
        self.eventCopyButton = wx.Button(eventWindow, wx.ID_ANY, "Copy", size=(50,20))
        self.eventDelButton = wx.Button(eventWindow, wx.ID_ANY, "Delete", size=(50,20))
        
        eventListButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        eventListButtonSizer.Add(self.eventAddButton, 0)
        eventListButtonSizer.Add(self.eventCopyButton, 0)
        eventListButtonSizer.Add(self.eventDelButton, 0)
        
        eventTypeBS.Add(eventTypeRow1Sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        #eventConfigBS.AddSizer(eventConfigSizer, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        eventBS.Add(self.eventList, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        eventBS.AddSizer(eventListButtonSizer, 0, wx.ALIGN_CENTER)
        
        self.eventPropBox = eventPropBox = wx.StaticBox(eventWindow, -1, "Event Properties")
        self.eventPropBS = eventPropBS = wx.StaticBoxSizer(eventPropBox, wx.VERTICAL)
        
        eventNameText = wx.StaticText(eventWindow, -1, "Name:")
        self.eventNameCtrl = wx.TextCtrl(eventWindow, wx.ID_ANY, size=(240,-1))
        
        eventPropNameSizer = wx.BoxSizer(wx.HORIZONTAL)
        eventPropNameSizer.Add(eventNameText, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        eventPropNameSizer.Add(self.eventNameCtrl, 1)
        
        eventPropBS.AddSizer(eventPropNameSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.BOTTOM, 5)
        
        # ----
        
        self.eventPropWarp = wx.Panel(eventWindow, -1)
        
        eventPropWarpSizer = wx.BoxSizer(wx.VERTICAL)
        
        warpFromCoordGrid = wx.FlexGridSizer(2,2)
        
        self.eventPropWarpXCheck = wx.CheckBox(self.eventPropWarp, wx.ID_ANY, " Trigger X:")
        self.eventPropWarpYCheck = wx.CheckBox(self.eventPropWarp, wx.ID_ANY, " Trigger Y:")        
        self.eventPropWarpXCtrl = wx.SpinCtrl(self.eventPropWarp, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropWarpYCtrl = wx.SpinCtrl(self.eventPropWarp, wx.ID_ANY, min=0, max=64, size=(45,20))
        
        warpFromCoordGrid.Add(self.eventPropWarpXCheck, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        warpFromCoordGrid.Add(self.eventPropWarpXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        warpFromCoordGrid.Add(self.eventPropWarpYCheck, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        warpFromCoordGrid.Add(self.eventPropWarpYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        
        warpDestMapSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.eventPropWarpChangeCheck = wx.CheckBox(self.eventPropWarp, wx.ID_ANY, " Change map to:")
        self.eventPropWarpMapList = wx.ComboBox(self.eventPropWarp, wx.ID_ANY, size=(200,-1))
        self.eventPropWarpMapList.AppendItems([s.name for s in self.rom.data["maps"]])
        self.eventPropWarpMapList.SetSelection(0)
        
        warpDestMapSizer.Add(self.eventPropWarpChangeCheck, 0, wx.LEFT | wx.EXPAND, 0)
        warpDestMapSizer.AddSpacer(3)
        warpDestMapSizer.Add(self.eventPropWarpMapList, 0, wx.LEFT | wx.EXPAND, 20)
        
        warpToCoordSizer = wx.BoxSizer(wx.HORIZONTAL)
        warpToCoordGrid = wx.FlexGridSizer(2,2)

        self.eventPropWarpDestXCheck = wx.CheckBox(self.eventPropWarp, wx.ID_ANY, " New X: ")
        self.eventPropWarpDestYCheck = wx.CheckBox(self.eventPropWarp, wx.ID_ANY, " New Y: ")
        
        self.eventPropWarpDestXCtrl = wx.SpinCtrl(self.eventPropWarp, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropWarpDestYCtrl = wx.SpinCtrl(self.eventPropWarp, wx.ID_ANY, min=0, max=64, size=(45,20))
        
        warpToCoordGrid.Add(self.eventPropWarpDestXCheck, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        warpToCoordGrid.Add(self.eventPropWarpDestXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        warpToCoordGrid.Add(self.eventPropWarpDestYCheck, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        warpToCoordGrid.Add(self.eventPropWarpDestYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.warpFacingUpRadio = wx.RadioButton(self.eventPropWarp, wx.ID_ANY, "", style=wx.RB_GROUP)
        self.warpFacingLeftRadio = wx.RadioButton(self.eventPropWarp, wx.ID_ANY, "")
        self.warpFacingRightRadio = wx.RadioButton(self.eventPropWarp, wx.ID_ANY, "")
        self.warpFacingDownRadio = wx.RadioButton(self.eventPropWarp, wx.ID_ANY, "")
        
        self.warpFacingUpRadio.context = 1
        self.warpFacingLeftRadio.context = 2
        self.warpFacingRightRadio.context = 0
        self.warpFacingDownRadio.context = 3
        
        self.warpFacingRadios = [self.warpFacingRightRadio, self.warpFacingUpRadio, self.warpFacingLeftRadio, self.warpFacingDownRadio]
        
        warpFacingFacingMidSizer = wx.BoxSizer(wx.HORIZONTAL)
        warpFacingFacingMidSizer.Add(self.warpFacingLeftRadio, 1, wx.RIGHT, 5)
        warpFacingFacingMidSizer.Add(self.warpFacingRightRadio, 1, wx.LEFT, 5)
        
        warpFacingText = wx.StaticText(self.eventPropWarp, -1, "Facing")
        
        warpFacingSizer = wx.BoxSizer(wx.VERTICAL)
        
        warpFacingSizer.Add(warpFacingText, 0, wx.ALIGN_CENTER | wx.BOTTOM, 3)
        warpFacingSizer.Add(self.warpFacingUpRadio, 0, wx.ALIGN_CENTER)
        warpFacingSizer.AddSizer(warpFacingFacingMidSizer, 0, wx.ALIGN_CENTER | wx.EXPAND)
        warpFacingSizer.Add(self.warpFacingDownRadio, 0, wx.ALIGN_CENTER | wx.BOTTOM, 3)
        
        warpToCoordSizer.AddSizer(warpToCoordGrid, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 20)
        warpToCoordSizer.AddSizer(warpFacingSizer, 0, wx.EXPAND, 5)
        
        eventPropWarpSizer.AddSizer(warpFromCoordGrid, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropWarpSizer.AddSizer(warpDestMapSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropWarpSizer.AddSizer(warpToCoordSizer, 0, wx.ALIGN_CENTER)
        
        eventPropWarpSizer.Layout()
        self.eventPropWarp.SetSizer(eventPropWarpSizer)
        
        # add: dest x/y, facing, mystery value

        # ----
        
        self.eventPropCopy = wx.Panel(eventWindow, -1)
        
        eventPropCopySizer = wx.BoxSizer(wx.VERTICAL)
        
        copyCoordGrid = wx.FlexGridSizer(2,2)
        copyCoordGrid2 = wx.FlexGridSizer(2,6)
        
        copyTrigXText = wx.StaticText(self.eventPropCopy, -1, "Trigger X: ")
        copyTrigYText = wx.StaticText(self.eventPropCopy, -1, "Trigger Y: ")
        copyWidthText = wx.StaticText(self.eventPropCopy, -1, "Width: ")
        copyHeightText = wx.StaticText(self.eventPropCopy, -1, "Height: ")
        copySrcXText = wx.StaticText(self.eventPropCopy, -1, "From X: ")
        copySrcYText = wx.StaticText(self.eventPropCopy, -1, "From Y: ")
        copyDestXText = wx.StaticText(self.eventPropCopy, -1, "To X: ")
        copyDestYText = wx.StaticText(self.eventPropCopy, -1, "To Y: ")
        
        self.eventPropCopyTrigXCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopyTrigYCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopyWidthCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopyHeightCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopySrcXCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopySrcYCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopyDestXCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropCopyDestYCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0, max=64, size=(45,20))

        copyCoordGrid.Add(copyTrigXText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid.Add(self.eventPropCopyTrigXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        copyCoordGrid.Add(copyTrigYText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid.Add(self.eventPropCopyTrigYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        
        copyCoordGrid2.Add(copySrcXText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopySrcXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        copyCoordGrid2.Add(copyDestXText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopyDestXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        copyCoordGrid2.Add(copyWidthText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopyWidthCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)        
        copyCoordGrid2.Add(copySrcYText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopySrcYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        copyCoordGrid2.Add(copyDestYText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopyDestYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)        
        copyCoordGrid2.Add(copyHeightText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        copyCoordGrid2.Add(self.eventPropCopyHeightCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)        
        
        copyRadioSizer = wx.BoxSizer(wx.VERTICAL)
        self.eventPropCopyFlagRadio = wx.RadioButton(self.eventPropCopy, wx.ID_ANY, " If flag is set (story/progress-based)", style=wx.RB_GROUP)
        self.eventPropCopyPermRadio = wx.RadioButton(self.eventPropCopy, wx.ID_ANY, " Step-Triggered (doors, switches)")
        self.eventPropCopyTempRadio = wx.RadioButton(self.eventPropCopy, wx.ID_ANY, " Temporary Step-Triggered (roofs)")
        
        self.eventPropCopyFlagRadio.context = 0
        self.eventPropCopyPermRadio.context = 1
        self.eventPropCopyTempRadio.context = 2
        
        self.eventPropCopyFlagCtrl = wx.SpinCtrl(self.eventPropCopy, wx.ID_ANY, min=0.0, max=65535.0, size=(65,20))
        
        copyRadioSizer.Add(self.eventPropCopyFlagRadio, 0)
        copyRadioSizer.Add(self.eventPropCopyFlagCtrl, 0, wx.LEFT, 18)
        copyRadioSizer.Add(self.eventPropCopyPermRadio, 0, wx.UP | wx.BOTTOM, 5)
        copyRadioSizer.Add(self.eventPropCopyTempRadio, 0, wx.BOTTOM, 5)
        
        copyWarningText = wx.StaticText(self.eventPropCopy, -1, "(Note: Permanent block copies are undone upon changing maps; temporary copies are undone by stepping on a block with the \"undo copy\" flag set.)")
        
        self.eventPropCopyBlankCheck = wx.CheckBox(self.eventPropCopy, wx.ID_ANY, "Copy blank blocks")
        
        eventPropCopySizer.AddSizer(copyCoordGrid, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropCopySizer.Add(self.eventPropCopyBlankCheck, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropCopySizer.AddSizer(copyCoordGrid2, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropCopySizer.AddSizer(copyRadioSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropCopySizer.Add(copyWarningText, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        
        eventPropCopySizer.Layout()
        self.eventPropCopy.SetSizer(eventPropCopySizer)

        copyWarningText.Wrap(250)
        
        # ----
        
        self.eventPropItem = wx.Panel(eventWindow, -1)
        
        eventPropItemSizer = wx.BoxSizer(wx.VERTICAL)
        
        itemCoordGrid = wx.FlexGridSizer(2,4)
        
        itemXText = wx.StaticText(self.eventPropItem, -1, "X: ")
        itemYText = wx.StaticText(self.eventPropItem, -1, "Y: ")
        itemFlagText = wx.StaticText(self.eventPropItem, -1, "Flag: ")
        
        self.eventPropItemXCtrl = wx.SpinCtrl(self.eventPropItem, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropItemYCtrl = wx.SpinCtrl(self.eventPropItem, wx.ID_ANY, min=0, max=64, size=(45,20))
        self.eventPropItemFlagCtrl = wx.SpinCtrl(self.eventPropItem, wx.ID_ANY, min=0, max=255, size=(50,20))
        
        itemCoordGrid.Add(itemXText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        itemCoordGrid.Add(self.eventPropItemXCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        itemCoordGrid.Add(itemFlagText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        itemCoordGrid.Add(self.eventPropItemFlagCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)
        itemCoordGrid.Add(itemYText, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        itemCoordGrid.Add(self.eventPropItemYCtrl, 0, wx.ALIGN_CENTER_VERTICAL, 5)

        itemListSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.eventPropItemItemRadio = wx.RadioButton(self.eventPropItem, wx.ID_ANY, "Item: ", style=wx.RB_GROUP)
        self.eventPropItemGoldRadio = wx.RadioButton(self.eventPropItem, wx.ID_ANY, "Gold: ")
        self.eventPropItemNoneRadio = wx.RadioButton(self.eventPropItem, wx.ID_ANY, "Nothing")
        
        self.eventPropItemList = wx.ComboBox(self.eventPropItem, wx.ID_ANY, size=(160,-1))
        self.eventPropItemGoldCtrl = wx.SpinCtrl(self.eventPropItem, wx.ID_ANY, min=10, max=65535, size=(60,20))
        
        self.eventPropItemList.AppendItems([i.name for i in self.rom.data["items"][:-1]])
        self.eventPropItemList.SetSelection(0)
        
        self.eventPropItemItemRadio.context = 0
        self.eventPropItemList.context = 0
        self.eventPropItemGoldRadio.context = 1
        self.eventPropItemGoldCtrl.context = 1
        self.eventPropItemNoneRadio.context = 2
        
        itemListSizer.Add(self.eventPropItemItemRadio, 0)
        itemListSizer.Add(self.eventPropItemList, 0, wx.LEFT, 15)
        itemListSizer.Add(self.eventPropItemGoldRadio, 0, wx.UP, 5)
        itemListSizer.Add(self.eventPropItemGoldCtrl, 0, wx.LEFT, 15)
        itemListSizer.Add(self.eventPropItemNoneRadio, 0, wx.UP, 5)
        
        self.eventPropItemChestCheck = wx.CheckBox(self.eventPropItem, wx.ID_ANY, "Item is in a chest (graphic purposes only)")
        
        itemGoldWarningText = wx.StaticText(self.eventPropItem, -1, "(Note: Due to a restriction in the way the ROM is laid out, the maximum amount of gold that can be found is 130.)")
        
        eventPropItemSizer.AddSizer(itemCoordGrid, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropItemSizer.AddSizer(itemListSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropItemSizer.Add(self.eventPropItemChestCheck, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        eventPropItemSizer.Add(itemGoldWarningText, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        
        eventPropItemSizer.Layout()
        self.eventPropItem.SetSizer(eventPropItemSizer)
        
        itemGoldWarningText.Wrap(200)
        
        # ----
        
        #self.eventPropWarp.Show(False)
        self.eventPropCopy.Show(False)
        self.eventPropItem.Show(False)
        
        eventPropBS.Add(self.eventPropWarp, 0, wx.ALL | wx.EXPAND, 5)
        eventPropBS.Add(self.eventPropCopy, 0, wx.ALL | wx.EXPAND, 5)
        eventPropBS.Add(self.eventPropItem, 0, wx.ALL | wx.EXPAND, 5)
        
        self.curEventProps = self.eventPropWarp
        
        #sbs2eventCol1Sizer.AddSizer(eventSetupBS, 0)
        sbs2eventCol1Sizer.AddSizer(eventTypeBS, 0)
        sbs2eventCol1Sizer.AddSizer(eventConfigBS, 0, wx.TOP | wx.BOTTOM, 5)
        sbs2eventCol1Sizer.AddSizer(eventBS, 0)
        
        sbs2eventSizer.AddSizer(sbs2eventCol1Sizer)
        sbs2eventSizer.AddSizer(eventPropBS, 0, wx.ALL ^ wx.TOP | wx.EXPAND, 5)
        
        #layoutEventWndSizer.Layout()
        
        # -------------------------------
        
        sbs2animSizer = wx.BoxSizer(wx.VERTICAL)
        
        animListSizer = wx.StaticBoxSizer(wx.StaticBox(animWindow, -1, "Select animation."), wx.VERTICAL)
        
        self.animList = wx.ListBox(animWindow, wx.ID_ANY, size=(120,100))
        self.animAddButton = wx.Button(animWindow, wx.ID_ANY, "Add", size=(40,20))
        self.animCopyButton = wx.Button(animWindow, wx.ID_ANY, "Copy", size=(40,20))
        self.animDelButton = wx.Button(animWindow, wx.ID_ANY, "Del", size=(40,20))
        
        animButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        animButtonSizer.Add(self.animAddButton, 0)
        animButtonSizer.Add(self.animCopyButton, 0)
        animButtonSizer.Add(self.animDelButton, 0)
        
        animListSizer.Add(self.animList, 0, wx.ALL ^ wx.BOTTOM, 5)
        animListSizer.AddSizer(animButtonSizer, 0, wx.ALL ^ wx.TOP | wx.EXPAND, 5)
        
        # ----
        
        animPropSizer = wx.StaticBoxSizer(wx.StaticBox(animWindow, -1, "Animation Properties"), wx.VERTICAL)
        
        animNameText = wx.StaticText(animWindow, -1, "Name: ")
        self.animNameCtrl = wx.TextCtrl(animWindow, wx.ID_ANY, size=(200,-1))
        
        animPropNameSizer = wx.BoxSizer(wx.HORIZONTAL)
        animPropNameSizer.Add(animNameText, 0, wx.ALIGN_CENTER_VERTICAL)
        animPropNameSizer.Add(self.animNameCtrl, 1)
        
        animText = wx.StaticText(animWindow, wx.ID_ANY, "Tileset")
        
        self.animTSList = wx.ComboBox(animWindow, wx.ID_ANY, size=(200,-1))
        self.animStart = wx.SpinCtrl(animWindow, wx.ID_ANY, min=0, max=128, size=(50,20))
        self.animEnd = wx.SpinCtrl(animWindow, wx.ID_ANY, min=0, max=128, size=(50,20))
        self.animDest = wx.SpinCtrl(animWindow, wx.ID_ANY, min=0, max=0x37f, size=(50,20))
        self.animDelay = wx.SpinCtrl(animWindow, wx.ID_ANY, min=0, max=255, size=(50,20))
        
        animPropRow1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        animPropRow1Sizer.Add(animText, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT, 5)
        animPropRow1Sizer.Add(self.animTSList, 0, wx.ALIGN_CENTER_VERTICAL)
        
        animPropRow2Sizer = wx.BoxSizer(wx.HORIZONTAL)
        animPropRow2Sizer.Add(wx.StaticText(animWindow, wx.ID_ANY, "Start"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(self.animStart, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(wx.StaticText(animWindow, wx.ID_ANY, "End"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(self.animEnd, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(wx.StaticText(animWindow, wx.ID_ANY, "Dest"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(self.animDest, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(wx.StaticText(animWindow, wx.ID_ANY, "Delay"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        animPropRow2Sizer.Add(self.animDelay, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        
        animPropSizer.AddSizer(animPropNameSizer, 0, wx.ALL ^ wx.RIGHT, 5)
        animPropSizer.AddSizer(animPropRow1Sizer, 0, wx.LEFT | wx.BOTTOM, 5)
        animPropSizer.AddSizer(animPropRow2Sizer, 0, wx.LEFT | wx.BOTTOM, 5)
        
        sbs2animRow1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2animRow1Sizer.AddSizer(animListSizer, 0, wx.ALL, 5)
        sbs2animRow1Sizer.AddSizer(animPropSizer, 0, wx.ALL, 5)
        
        animPreviewSizer = wx.StaticBoxSizer(wx.StaticBox(animWindow, -1, "Preview", size=(200,-1)), wx.VERTICAL)
        
        animPreviewText = wx.StaticText(animWindow, -1, "Not implemented.")
        animPreviewSizer.Add(animPreviewText)
        
        animTSSizer = wx.StaticBoxSizer(wx.StaticBox(animWindow, -1, "Tileset"), wx.VERTICAL)

        tsScroll2 = wx.lib.scrolledpanel.ScrolledPanel(animWindow, -1, size=(330,120))
        tsScroll2.SetupScrolling()
        tsScroll2.SetScrollRate(1,1)
        
        self.animTSPanel = rompanel.SpritePanel(tsScroll2, wx.ID_ANY, 8*16, 8*8, self.palette, scale=3, bg=16, func=self.OnClickAnimTSPanel, edit=True, grid=8)

        tsScroll2Sizer = wx.BoxSizer(wx.VERTICAL)
        tsScroll2Sizer.Add(self.animTSPanel)
        
        tsScroll2.SetSizer(tsScroll2Sizer)
        tsScroll2.Layout()
        tsScroll2.Fit()
        
        animTSSizer.Add(tsScroll2, 0, wx.ALL, 5)
        
        sbs2animRow2Sizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2animRow2Sizer.AddSizer(animPreviewSizer, 0, wx.ALL ^ wx.TOP, 5)
        sbs2animRow2Sizer.AddSizer(animTSSizer, 0, wx.ALL ^ wx.TOP, 5)
        
        sbs2animSizer.AddSizer(sbs2animRow1Sizer)
        sbs2animSizer.AddSizer(sbs2animRow2Sizer)
        
        sbs2animSizer.Layout()
        
        # --------------------------------
        
        """sbs2tempSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.testCtrl = wx.TextCtrl(tempWindow, wx.ID_ANY, size=(150,275), style=wx.TE_MULTILINE)
        self.testAreaBox = wx.ListBox(tempWindow, wx.ID_ANY)
        #self.testCtrl2 = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        
        self.testBtn = wx.Button(tempWindow, wx.ID_ANY, "hexlify test")
        
        sbs2tempSizer.Add(self.testCtrl, 0, wx.ALL | wx.EXPAND, 5)
        sbs2tempSizer.Add(self.testAreaBox, 0, wx.ALL | wx.EXPAND, 5)
        sbs2tempSizer.Add(self.testBtn, 0, wx.ALL | wx.EXPAND, 5)
        sbs2tempSizer.Layout()"""
        
        # --------------------------------
        
        genWndSizerRow1 = wx.BoxSizer(wx.HORIZONTAL)
        #genWndSizerRow1.AddSizer(sbs2sizeBS, 0, wx.EXPAND | wx.RIGHT, 5)
        genWndSizerRow1.AddSizer(sbs2paletteBS, 0, wx.EXPAND)
        
        genWndSizerRow2 = wx.BoxSizer(wx.HORIZONTAL)
        genWndSizerRow2.AddSizer(sbs2tilesetBS, 0, wx.EXPAND, 5)
        genWndSizerRow2.AddSizer(sbs2areaBS, 0, wx.EXPAND, 5)
        
        genWndSizer.AddSizer(genWndSizerRow1, 0, wx.EXPAND | wx.ALL, 5)
        genWndSizer.AddSizer(genWndSizerRow2, 0, wx.EXPAND | wx.ALL, 5)
        
        # ----
        
        sbs2blockSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs2blockCol1Sizer = wx.BoxSizer(wx.VERTICAL)
        sbs2blockRow1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sbs2blockRow1Sizer.AddSizer(sbs2blockTSListBS, 1, wx.EXPAND | wx.ALL ^ wx.RIGHT, 5)
        sbs2blockRow1Sizer.AddSizer(sbs2blockEditorBS, 0, wx.ALL, 5)
        
        sbs2blockCol1Sizer.AddSizer(sbs2blockRow1Sizer, 0, wx.ALL, 5)
        sbs2blockCol1Sizer.AddSizer(sbs2blockTSBS, 1, wx.ALL ^ wx.TOP | wx.EXPAND, 5)
        
        sbs2blockSizer.AddSizer(sbs2blockCol1Sizer, 0, wx.RIGHT | wx.EXPAND, 5)
        sbs2blockSizer.AddSizer(sbs2blockListBS, 0, wx.EXPAND)
        
        blockWndSizer.AddSizer(sbs2blockSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # ----
        
        #sbs2layoutSizer = wx.BoxSizer(wx.HORIZONTAL)
        #sbs2layoutSizer.AddSizer(sbs2layoutViewSizer, 0, wx.EXPAND | wx.ALL, 5)
        #sbs2layoutSizer.AddSizer(self.layoutPropBook, 0, wx.EXPAND)
        #layoutWndSizer.AddSizer(sbs2layoutSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # ----
        
        eventWndSizer.AddSizer(sbs2eventSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # ----
        
        animWndSizer.AddSizer(sbs2animSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # ----
        
        #tempWndSizer.AddSizer(sbs2tempSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --------------------------------
        
        self.mapViewer = window.MapViewer(self, wx.ID_ANY, self.parent)
        self.mapViewer.init(None, None)
        
        # --------------------------------

        genWindow.SetSizer(genWndSizer)
        genWndSizer.Layout()
        blockWindow.SetSizer(blockWndSizer)
        blockWndSizer.Layout()
        layoutWindow.SetSizer(layoutWndSizer)
        layoutWndSizer.Layout()
        configWindow.SetSizer(configWndSizer)
        configWndSizer.Layout()
        eventWindow.SetSizer(eventWndSizer)
        eventWndSizer.Layout()
        #tempWindow.SetSizer(tempWndSizer)
        #tempWndSizer.Layout()
        
        sbs2notebook.AddPage(genWindow, "General")
        sbs2notebook.AddPage(blockWindow, "Blocks")
        sbs2notebook.AddPage(layoutWindow, "Layout")
        sbs2notebook.AddPage(configWindow, "Setups")
        sbs2notebook.AddPage(eventWindow, "Interaction")
        sbs2notebook.AddPage(animWindow, "Animations")
        #sbs2notebook.AddPage(tempWindow, "Other")
        
        sbs2.Add(sbs2notebook, 1, wx.EXPAND | wx.ALL, 5)
        
        # -----------------------
        
        #midSizer = wx.BoxSizer(wx.HORIZONTAL)
        #midRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        #midSizer.AddSizer(sbs4, 0, flag=wx.EXPAND)
        #midRightSizer.AddSizer(sbs5, 1, flag=wx.EXPAND)
        #midRightSizer.AddSizer(sbs3, 1, flag=wx.EXPAND)
        #midSizer.AddSizer(midRightSizer, 1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        #self.sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        #self.sizer.AddSizer(sbs1, pos=(1,0), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs2, pos=(0,0), flag=wx.EXPAND)
        self.sizer.Add(self.mapViewer, pos=(0,1), border=0)
        
        #self.sizer.Add(self.testCtrl, pos=(4,0))
        #self.sizer.Add(self.testCtrl2, pos=(4,1))
        
        #self.sizer.AddSizer(sbs2, pos=(1,1), flag=wx.EXPAND)
        #self.sizer.AddSizer(midSizer, pos=(2,0), span=(1,2))
        #self.sizer.AddSizer(sbs6, pos=(3,0), span=(1,2), flag=wx.EXPAND)
        
        #self.changeEditGlyph(self.rom.fontOrder[0])

        self.sizer.Layout()
        
        self.changeMap(0)
            
        # ------------------------
        
        # main section
        
        # OLD wx.EVT_BUTTON(self, self.mapViewButton.GetId(), self.OnClickViewMapButton)
        
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, self.mainNotebook.GetId(), self.OnChangePage)
        
        # map properties
        
        #wx.EVT_COMBOBOX(self, self.mapList.GetId(), self.OnSelectMap)
        wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        
        for tsl in self.tilesetLists:
            wx.EVT_COMBOBOX(self, tsl.GetId(), self.OnSelectTileset)
        
        #    area props
        
        wx.EVT_COMBOBOX(self, self.areaList.GetId(), self.OnSelectArea)
        wx.EVT_COMBOBOX(self, self.areaMusicList.GetId(), self.OnSelectAreaMusic)
        
        wx.EVT_CHECKBOX(self, self.areaLayer2Check.GetId(), self.OnToggleAreaLayer2Check)
        wx.EVT_RADIOBUTTON(self, self.areaLayer2ForeRadio.GetId(), self.OnSelectAreaLayer2Type)
        wx.EVT_RADIOBUTTON(self, self.areaLayer2BackRadio.GetId(), self.OnSelectAreaLayer2Type)
        
        wx.EVT_SPINCTRL(self, self.areaLayer1X1Ctrl.GetId(), self.OnSelectAreaLayer1X1)
        wx.EVT_SPINCTRL(self, self.areaLayer1Y1Ctrl.GetId(), self.OnSelectAreaLayer1Y1)
        wx.EVT_SPINCTRL(self, self.areaLayer1X2Ctrl.GetId(), self.OnSelectAreaLayer1X2)
        wx.EVT_SPINCTRL(self, self.areaLayer1Y2Ctrl.GetId(), self.OnSelectAreaLayer1Y2)
        wx.EVT_SPINCTRL(self, self.areaLayer1ParaXCtrl.GetId(), self.OnSelectAreaLayer1XParallax)
        wx.EVT_SPINCTRL(self, self.areaLayer1ParaYCtrl.GetId(), self.OnSelectAreaLayer1YParallax)
        wx.EVT_SPINCTRL(self, self.areaLayer1ScrXCtrl.GetId(), self.OnSelectAreaLayer1XScroll)
        wx.EVT_SPINCTRL(self, self.areaLayer1ScrYCtrl.GetId(), self.OnSelectAreaLayer1YScroll)        
        
        wx.EVT_SPINCTRL(self, self.areaLayer2X1Ctrl.GetId(), self.OnSelectAreaLayer2X1)
        wx.EVT_SPINCTRL(self, self.areaLayer2Y1Ctrl.GetId(), self.OnSelectAreaLayer2Y1)
        wx.EVT_SPINCTRL(self, self.areaLayer2ParaXCtrl.GetId(), self.OnSelectAreaLayer2XParallax)
        wx.EVT_SPINCTRL(self, self.areaLayer2ParaYCtrl.GetId(), self.OnSelectAreaLayer2YParallax)
        wx.EVT_SPINCTRL(self, self.areaLayer2ScrXCtrl.GetId(), self.OnSelectAreaLayer2XScroll)
        wx.EVT_SPINCTRL(self, self.areaLayer2ScrYCtrl.GetId(), self.OnSelectAreaLayer2YScroll)        
        
        # block edit tab
        
        wx.EVT_COMBOBOX(self, self.blockTSList.GetId(), self.OnSelectBlockTileset)
        
        wx.EVT_SLIDER(self, wx.ID_ANY, self.OnChangeBlockPage)
        
        # layout tab
        
        wx.EVT_RADIOBUTTON(self, wx.ID_ANY, self.OnClickLayoutInterRadio)
        
        # interaction tab
        
        wx.EVT_LISTBOX(self, self.eventList.GetId(), self.OnSelectEvent)
        
        wx.EVT_COMBOBOX(self, self.eventTypeList.GetId(), self.OnSelectEventType)
        
        wx.EVT_TEXT(self, self.eventNameCtrl.GetId(), self.OnChangeEventName)
        
        #    warp props
        
        wx.EVT_SPINCTRL(self, self.eventPropWarpXCtrl.GetId(), self.OnChangeWarpXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropWarpYCtrl.GetId(), self.OnChangeWarpYCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropWarpDestXCtrl.GetId(), self.OnChangeWarpDestXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropWarpDestYCtrl.GetId(), self.OnChangeWarpDestYCtrl)
        
        wx.EVT_CHECKBOX(self, self.eventPropWarpXCheck.GetId(), self.OnToggleWarpLineCheck)
        wx.EVT_CHECKBOX(self, self.eventPropWarpYCheck.GetId(), self.OnToggleWarpLineCheck)
        wx.EVT_CHECKBOX(self, self.eventPropWarpDestXCheck.GetId(), self.OnToggleWarpDestLineCheck)
        wx.EVT_CHECKBOX(self, self.eventPropWarpDestYCheck.GetId(), self.OnToggleWarpDestLineCheck)
        wx.EVT_CHECKBOX(self, self.eventPropWarpChangeCheck.GetId(), self.OnToggleWarpChangeCheck)
        
        wx.EVT_COMBOBOX(self, self.eventPropWarpMapList.GetId(), self.OnSelectWarpMap)
        
        for r in self.warpFacingRadios:
            wx.EVT_RADIOBUTTON(self, r.GetId(), self.OnSelectWarpFacing)
            
        #    copy props
        
        wx.EVT_CHECKBOX(self, self.eventPropCopyBlankCheck.GetId(), self.OnToggleCopyBlankCheck)
        
        wx.EVT_SPINCTRL(self, self.eventPropCopyTrigXCtrl.GetId(), self.OnChangeCopyTrigXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopyTrigYCtrl.GetId(), self.OnChangeCopyTrigYCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopySrcXCtrl.GetId(), self.OnChangeCopySrcXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopySrcYCtrl.GetId(), self.OnChangeCopySrcYCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopyDestXCtrl.GetId(), self.OnChangeCopyDestXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopyDestYCtrl.GetId(), self.OnChangeCopyDestYCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopyWidthCtrl.GetId(), self.OnChangeCopyWidthCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropCopyHeightCtrl.GetId(), self.OnChangeCopyHeightCtrl)    
        
        wx.EVT_RADIOBUTTON(self, self.eventPropCopyFlagRadio.GetId(), self.OnClickCopyTypeRadio)
        wx.EVT_RADIOBUTTON(self, self.eventPropCopyPermRadio.GetId(), self.OnClickCopyTypeRadio)
        wx.EVT_RADIOBUTTON(self, self.eventPropCopyTempRadio.GetId(), self.OnClickCopyTypeRadio)
        
        wx.EVT_SPINCTRL(self, self.eventPropCopyFlagCtrl.GetId(), self.OnChangeCopyFlagCtrl)
        
        #    item props

        wx.EVT_SPINCTRL(self, self.eventPropItemXCtrl.GetId(), self.OnChangeItemXCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropItemYCtrl.GetId(), self.OnChangeItemYCtrl)
        wx.EVT_SPINCTRL(self, self.eventPropItemFlagCtrl.GetId(), self.OnChangeItemFlagCtrl)
        
        wx.EVT_RADIOBUTTON(self, self.eventPropItemItemRadio.GetId(), self.OnSelectItemType)
        wx.EVT_COMBOBOX(self, self.eventPropItemList.GetId(), self.OnSelectItemType)
        wx.EVT_RADIOBUTTON(self, self.eventPropItemGoldRadio.GetId(), self.OnSelectItemType)
        wx.EVT_SPINCTRL(self, self.eventPropItemGoldCtrl.GetId(), self.OnSelectItemType)
        wx.EVT_RADIOBUTTON(self, self.eventPropItemNoneRadio.GetId(), self.OnSelectItemType)
        
        wx.EVT_CHECKBOX(self, self.eventPropItemChestCheck.GetId(), self.OnToggleItemChestCheck)
        
        # animations tab
        
        wx.EVT_LISTBOX(self, self.animList.GetId(), self.OnChangeAnim)
        
        wx.EVT_COMBOBOX(self, self.animTSList.GetId(), self.OnSelectAnimTS)
        
        wx.EVT_SPINCTRL(self, self.animStart.GetId(), self.OnChangeAnimStart)
        wx.EVT_SPINCTRL(self, self.animEnd.GetId(), self.OnChangeAnimEnd)
        wx.EVT_SPINCTRL(self, self.animDest.GetId(), self.OnChangeAnimDest)
        wx.EVT_SPINCTRL(self, self.animDelay.GetId(), self.OnChangeAnimDelay)
        
        # other tab
        
        #wx.EVT_BUTTON(self, self.testBtn.GetId(), self.testHexlify)
    
    def OnShow(self, evt):
        for p in range(16):
            self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
            self.colorPanels[p].Refresh()
        self.updateMapViewerContext()
        #self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        #self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        #self.selectedColorLeft.Refresh()
        #self.selectedColorRight.Refresh()
    
    def testHexlify(self, evt):
        #self.map.layoutData = self.rom.mapLayoutSubroutine(self.map.raw_hexlify(self.map.sectionAddrs[1], True), 0)
        #self.map.blocks = self.rom.mapBlockSubroutine(self.map.raw_hexlify(self.map.sectionAddrs[0])[0], 0, self.map)
        self.map.reorderByBlock()
        self.refreshPixels()

    def OnChangePage(self, evt):
        
        self.updateMapViewerContext()
    
    def updateMapViewerContext(self):
        
        if self.mapViewer.inited:
            
            pg = self.mainNotebook.GetSelection()
            
            #if self.mapViewer.map == self.map or not self.mapViewer.mapList.IsEnabled() or pg == 3:
                
            if pg == 0: # general properties
                self.mapViewer.updateContext(consts.VC_AREA)
            elif pg == 2: # layout
                self.mapViewer.updateContext(self.vcsBlock[self.blockEditMode])
            elif pg == 4:   # interaction
                self.mapViewer.updateContext(self.vcsEvent[min(len(self.vcsEvent), self.curEventType)])
            else:
                self.mapViewer.updateContext(consts.VC_NOTHING)
                    
            #else:
            #    self.mapViewer.updateContext(consts.VC_NOTHING)
            
            self.mapViewer.refreshMapView()
    
    # OLD: when map viewer was a frame    
    """def OnClickViewMapButton(self, evt):
        self.createMapViewer()
        
    def createMapViewer(self, show=True):
        self.GetTopLevelParent().createMapViewer(self.map, self.palette, show)"""
    # /OLD
    
    def OnClickLayoutInterRadio(self, evt):
        
        obj = evt.GetEventObject()
        
        if hasattr(obj, "context"):
        
            if obj.context == 0x3ff:
                self.blockEditMode = 0
            else:
                self.blockEditMode = 1
            
            self.updateMapViewerContext()
            self.curInterFlag = obj.context
            
            # specific radio button event handlers here
        
        evt.Skip()
        
    def OnChangeLayoutPage(self, evt):
        
        oldVM = self.curViewMode
        self.curViewMode = evt.GetSelection() != 0
        
        #if self.curViewMode != oldVM and not self.viewAll:
        #    self.refreshMapView()
    
    def OnCheckViewAll(self, evt):
        self.viewAll = evt.GetSelection()
        #self.refreshMapView()
        
    def TimerTest(self, evt):
        
        self.animFrame ^= 1
        self.changeAnimSprite()
        
        #if not self.printed:
        #    print "\n".join(dir(evt))
        #    self.printed = True
    
    def OnClickBlockTilesetPanel(self, evt):
        
        obj = evt.GetEventObject()
        x = evt.GetX()/obj.scale/8
        y = evt.GetY()/obj.scale/8
        
        tsSel = self.blockTSList.GetSelection()
        ofs = 0
        for i in range(len(self.map.tilesetIdxes)):
            if i <= tsSel and self.map.tilesetIdxes[i] == 255:
                ofs += 1
        tsSel += ofs
        
        if evt.LeftIsDown():
            self.curLeftTile = 0x100 + tsSel * 0x80 + y*16 + x
            self.refreshTilePanels()
        elif evt.RightIsDown():
            self.curRightTile = 0x100 + tsSel * 0x80 + y*16 + x
            self.refreshTilePanels()
        
        
        
    def OnSelectBlockTileset(self, evt):
        self.updateTileset()
        self.refreshPixels()
    
    def OnChangeBlockPage(self, evt):
        obj = evt.GetEventObject()
        
        if hasattr(obj, "context"):
            
            if obj.context == "edit":
                
                self.curEditBlockPage = obj.GetValue()
                self.changeBlockEditList()
            
            elif obj.context == "list":
                
                self.curListBlockPage = obj.GetValue()
                self.changeBlockList()
    
        evt.Skip()

    def OnClickBlockSelPanel(self, evt):
        
        tmp = self.curListBlockLeft
        self.curListBlockLeft = self.curListBlockRight
        self.curListBlockRight = tmp
        self.blockListLeftPanel.refreshSprite(self.map.blocks[self.curListBlockLeft].pixels)
        self.blockListLeftPanel.Refresh()
        self.blockListRightPanel.refreshSprite(self.map.blocks[self.curListBlockRight].pixels)
        self.blockListRightPanel.Refresh()
        self.blockListSizer.Layout()
    
        evt.Skip()
        
    def changeBlockEditList(self):
        
        #self.blockEditListSizer.Clear()
        blockWindow = self.blockWindow
        
        maxPages = len(self.map.blocks) / len(self.blockEditPanels)
        
        self.blockEditSlider.SetRange(0, maxPages)
        self.blockEditPosText.SetLabel(`self.curEditBlockPage`)
        self.blockEditMaxText.SetLabel(`maxPages`)
        self.blockEditListSelSizer.Layout()
        
        for idx in range(0, len(self.blockEditPanels)): #len(self.map.blocks)):
            
            realIdx = self.curEditBlockPage * len(self.blockEditPanels) + idx
            p = self.blockEditPanels[idx]
            t = self.blockEditText[idx]
            
            if realIdx < len(self.map.blocks):
                
                p.index = realIdx
                p.refreshSprite(self.map.blocks[realIdx].pixels)
                
                if realIdx == self.curEditBlock:
                    p.bg = 17
                else:
                    p.bg = None
                    
                p.Refresh()
                
                t.SetLabel(`realIdx`)
        
            else:
                
                p.refreshSprite([])
                p.Refresh()
                
                p.bg = None
                
                t.SetLabel("")
        
        self.blockEditListSizer.Layout()
        
    def changeBlockList(self):
        
        #self.blockEditListSizer.Clear()
        
        maxPages = len(self.map.blocks) / len(self.blockListPanels)
        
        self.blockListSlider.SetRange(0, maxPages)
        self.blockListPosText.SetLabel(`self.curEditBlockPage`)
        self.blockListMaxText.SetLabel(`maxPages`)
        self.blockListSliderSizer.Layout()
        
        for idx in range(0, len(self.blockListPanels)): #len(self.map.blocks)):
            
            realIdx = self.curListBlockPage * len(self.blockListPanels) + idx
            p = self.blockListPanels[idx]
            #t = self.blockListText[idx]
            
            if realIdx < len(self.map.blocks):
                
                p.index = realIdx
                p.refreshSprite(self.map.blocks[realIdx].pixels)
                    
                p.Refresh()
                
                #t.SetLabel(`realIdx`)
        
            else:
                
                p.index = None
                p.refreshSprite([])
                p.Refresh()
                
                #t.SetLabel("")
        
        self.refreshBlockListSelPanels()
        
    def changeColors(self, num):
        palette = self.rom.data["palettes"][num]
        for c in range(len(self.colorPanels)):
            self.colorPanels[c].SetBackgroundColour(palette.colors[c])
            self.colorPanels[c].Refresh()
        self.blockPanel.palette = palette
        for c in range(len(self.blockEditPanels)):
            self.blockEditPanels[c].palette = palette
        for c in range(len(self.blockListPanels)):
            self.blockListPanels[c].palette = palette
        #for c in range(len(self.mapViewPanels)):
        #    self.mapViewPanels[c].palette = palette
        #self.mapViewPanel.palette = palette
        self.tilesetPanel.palette = palette
        self.blockEditLeftPanel.palette = palette
        self.blockEditRightPanel.palette = palette
        self.blockListLeftPanel.palette = palette
        self.blockListRightPanel.palette = palette
        
    def refreshPixels(self):
        
        tsIdx = self.curTilesetIdx
        if not self.tileset.loaded:
            self.rom.getTilesets(tsIdx, tsIdx)
        
        self.tilesetPanel.pixels = []
        for tRow in range(8):
            for pRow in range(8):
                row = "".join([self.tileset.tiles[tRow*16+to].pixels[pRow] for to in range(16)])
                self.tilesetPanel.pixels.append(row)
        
        # -----
        
        tsAnimIdx = self.curAnimTSIdx
        if not self.animTileset.loaded:
            self.rom.getTilesets(tsAnimIdx, tsAnimIdx)
        
        self.animTSPanel.pixels = []
        for tRow in range(8):
            for pRow in range(8):
                row = "".join([self.animTileset.tiles[tRow*16+to].pixels[pRow] for to in range(16)])
                self.animTSPanel.pixels.append(row)

        # -----

        self.blockPanel.refreshSprite(self.map.blocks[self.curEditBlock].pixels)
        self.blockPanel.Refresh()
        self.tilesetPanel.refreshSprite()
        self.tilesetPanel.Refresh()
        self.animTSPanel.refreshSprite()
        self.animTSPanel.Refresh()
        
        # -----
        
        self.refreshTilePanels()
        #self.refreshMapView()

    def refreshTilePanels(self):
        
        ts, idx = (self.curLeftTile - 0x100) / 0x80, self.curLeftTile % 0x80
        self.blockEditLeftPanel.refreshSprite(self.rom.data["tilesets"][self.map.tilesetIdxes[ts]].tiles[idx].pixels)
        ts, idx = (self.curRightTile - 0x100) / 0x80, self.curRightTile % 0x80
        self.blockEditRightPanel.refreshSprite(self.rom.data["tilesets"][self.map.tilesetIdxes[ts]].tiles[idx].pixels)
        
        self.blockEditLeftPanel.Refresh()
        self.blockEditRightPanel.Refresh()

    def OnSelectMode(self, evt):

        l = [self.modePixel.GetId(), self.modeFill.GetId(), self.modeReplace.GetId()]
        self.mode = l.index(evt.GetId())
        
    def OnSelectMap(self, evt):
        self.changeMap(evt.GetSelection())

    def OnChangeBlockTile(self, evt):
    
        obj = evt.GetEventObject()
        
        x = evt.GetX()/obj.scale/8
        y = evt.GetY()/obj.scale/8
        blk = self.map.blocks[self.curEditBlock]
        
        tile = None
        
        if evt.ShiftDown():
            
            if evt.LeftDown():
                self.curLeftTile = (blk.tileIdxes[y*3+x] & 0x7ff)
                #print hex(self.curLeftTile)
                self.blockEditLeftPanel.refreshSprite(self.rom.data["tilesets"][self.map.tilesetIdxes[self.curLeftTile/0x80]].tiles[self.curLeftTile%0x80].pixels)
                self.blockEditLeftPanel.Refresh()
            elif evt.RightDown():
                self.curRightTile = (blk.tileIdxes[y*3+x] & 0x7ff)
                
                self.blockEditRightPanel.refreshSprite(self.rom.data["tilesets"][self.map.tilesetIdxes[self.curRightTile/0x80]].tiles[self.curRightTile%0x80].pixels)
                self.blockEditRightPanel.Refresh()                
            else:
                return

            return
        
        elif self.curEditBlock > 2:
            
            if evt.ControlDown() and evt.LeftDown():
                blk.tileIdxes[y*3+x] ^= 0x8000
                
            else:
                
                if evt.LeftDown():
                    tile = self.curLeftTile
                elif evt.RightDown():
                    tile = self.curRightTile
                else:
                    return
                
                blk = self.map.blocks[self.curEditBlock]
                idx = y*3 + x
                
                oldBot = blk.tileIdxes[idx] & 0x7ff
                newBot = tile
                
                if oldBot == newBot:
                    top = blk.tileIdxes[idx] & 0x1800
                    order = [0x0000, 0x0800, 0x1800, 0x1000]
                    newTop = order[(order.index(top)+1) % len(order)]
                    blk.tileIdxes[idx] = blk.tileIdxes[idx] & 0x8000 | newTop | newBot
                else:
                    blk.tileIdxes[idx] = blk.tileIdxes[idx] & 0x9800 | newBot
                    blk.tiles[idx] = self.rom.data["tilesets"][self.map.tilesetIdxes[(tile-0x100)/0x80]].tiles[tile%0x80]
        
        else:
            return
            
        blk.createPixelArray()
        self.modify()
        self.blockPanel.refreshSprite(blk.pixels)
        
        if self.mapViewer.inited and self.mapViewer.map == self.map:
            self.mapViewer.mapViewPanel.updateBlockBMPs(self.curEditBlock)
        
        if self.curEditBlock / len(self.blockListPanels) == self.curListBlockPage:
            self.blockListPanels[self.curEditBlock % len(self.blockListPanels)].refreshSprite(blk.pixels)
        
        for p in self.blockEditPanels:
            if p.index == self.curEditBlock:
                p.refreshSprite(blk.pixels)
                p.Refresh()
                break
                
        obj.Refresh()
        
    def OnClickBlockEditPanel(self, evt):
        obj = evt.GetEventObject()
        self.blockPanel.refreshSprite(self.map.blocks[obj.index].pixels)
        self.blockPanel.Refresh()
        
        self.curEditBlock = obj.index
        
        for p in self.blockEditPanels:
            p.bg = None
            p.Refresh()
        
        if obj.index == self.curEditBlock:
            self.blockEditPanels[obj.index % len(self.blockEditPanels)].bg = 17
            self.blockEditPanels[obj.index % len(self.blockEditPanels)].Refresh()
        
    def OnClickBlockListPanel(self, evt):
        
        obj = evt.GetEventObject()
        
        if obj.index is not None:
            
            if evt.LeftDown():
                self.curListBlockLeft = obj.index
                    
            elif evt.RightDown():
                self.curListBlockRight = obj.index
        
            elif int(self.blockListOverText.GetLabel()[5:]) != obj.index:
                self.blockListOverText.SetLabel("Block %03i" % obj.index)
                self.blockListSliderSizer.Layout()
                evt.Skip()
                return
        
            else:
                evt.Skip()
                return
                
            self.refreshBlockListSelPanels()
    
    def refreshBlockListSelPanels(self):
        
        self.blockListLeftPanel.refreshSprite(self.map.blocks[self.curListBlockLeft].pixels)
        self.blockListLeftPanel.Refresh()
        self.blockListLeftText.SetLabel("L (%i)" % self.curListBlockLeft)
    
        self.blockListRightPanel.refreshSprite(self.map.blocks[self.curListBlockRight].pixels)
        self.blockListRightPanel.Refresh()
        self.blockListRightText.SetLabel("R (%i)" % self.curListBlockRight)
        
        self.blockListSelSizer.Layout()
        self.blockListSizer.Layout()
            
    def changeMap(self, num=None):
        
        if not self.rom.data["maps"][num].loaded:
            self.rom.getMaps(num, num)
        else:
            pass
            #print `self.rom.data["maps"][num].paletteIdx`
            #print `self.rom.data["maps"][num].tilesetIdxes`
        
        self.curMapIdx = num
        
        self.map = self.rom.data["maps"][num]
        self.updateModifiedIndicator(self.map.modified)
        
        #if num == 42:
        #    self.map.layoutData = self.rom.mapLayoutSubroutine(self.map.raw_hexlify(self.map.sectionAddrs[1]), 0)
        
        for i in range(5):
            isUsed = self.map.tilesetIdxes[i] != 255
            self.layerChecks[i].SetValue(isUsed)
            self.tilesetLists[i].Enable(isUsed)
            
            if isUsed:
                self.tilesetLists[i].SetSelection(self.map.tilesetIdxes[i])
        
        #self.mapWidthCtrl.SetValue(self.map.width)
        #self.mapHeightCtrl.SetValue(self.map.height)
        self.changePalette(self.map.paletteIdx)
        
        self.areaList.Clear()
        self.areaList.AppendItems([a.name for a in self.map.areas])
        self.areaList.SetSelection(0)
        
        self.changeArea(0)
        
        # -----
        
        #self.mapViewBarX.SetScrollbar(0, self.viewPageWidth*2, self.map.width, self.viewPageWidth)
        #self.mapViewBarY.SetScrollbar(0, self.viewPageHeight*2, self.map.height, self.viewPageHeight)
        #self.setViewPos(0, 0)
        
        self.updateBlockTSList()
        self.blockTSList.SetSelection(0)
        
        self.curLeftTile = 0x100
        self.curRightTile = 0x100
        
        self.curListBlockLeft = 0
        self.curListBlockRight = 0
        self.curListBlockPage = 0
        self.blockListSlider.SetValue(0)
        
        self.curEditBlock = 0
        self.curEditBlockPage = 0
        self.blockEditSlider.SetValue(0)
        
        self.changeBlockEditList()
        self.changeBlockList()
        
        #self.tileList.Clear()
        #self.tileList.AppendItems([t.name for t in self.tileset.tiles])
        #self.tileList.SetSelection(0)
        
        #self.changeTile()
                    
        #self.testCtrl.SetValue(self.map.raw_bytes)
        
        #self.testCtrl2.SetValue("\n\n".join(["\n".join(t.pixels) for t in self.tileset.tiles]))
        
        self.updateTileset()
        
        #if self.mapViewer.IsShown():
            #if self.mapViewer.mapList.IsEnabled():
            #    self.updateMapViewerContext()
            #    self.mapViewer.refreshMapView()
            #else:
        self.mapViewer.changeMap(self.map, self.palette)
                
        
        # ----
        
        self.changeSetupList()
        self.changeEventType(self.curEventType)
        
        # ----
        
        self.animList.Clear()
        self.animList.AppendItems([a.name for a in self.map.anims])
        
        self.updateAnimTSList()
        self.changeAnim(0)
        
        if self.animTSList.GetSelection() is not None:
            self.updateAnimTileset()
        
        # ----
        
        self.refreshPixels()
        
        #self.mapViewPanel.changeMap(self.map, self.palette)
        #self.mapViewPanel.curViewX = 0
        #self.mapViewPanel.curViewY = 0
        #self.mapViewPanel.Refresh()

    # -------------------
    
    def OnSelectArea(self, evt):
        self.changeArea(evt.GetSelection())
    
    def changeArea(self, num):
        
        self.areaList.SetSelection(num)
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        
    def updateAreaProps(self):
        
        area = self.curArea
        hasLayer2 = area.hasLayer2
        
        self.areaLayer2Check.SetValue(hasLayer2)
        self.areaLayer2ForeRadio.Enable(hasLayer2)
        self.areaLayer2BackRadio.Enable(hasLayer2)
        
        self.areaLayer2X1Ctrl.Enable(hasLayer2)
        self.areaLayer2Y1Ctrl.Enable(hasLayer2)
        self.areaLayer2ParaXCtrl.Enable(hasLayer2)
        self.areaLayer2ParaYCtrl.Enable(hasLayer2)
        self.areaLayer2ScrXCtrl.Enable(hasLayer2)
        self.areaLayer2ScrYCtrl.Enable(hasLayer2)
        
        [self.areaLayer2ForeRadio, self.areaLayer2BackRadio][area.layerType>0].SetValue(True)
        
        self.areaLayer1X1Ctrl.SetValue(area.l1x1)
        self.areaLayer1Y1Ctrl.SetValue(area.l1y1)
        self.areaLayer1X2Ctrl.SetValue(area.l1x2)
        self.areaLayer1Y2Ctrl.SetValue(area.l1y2)
        self.areaLayer1ParaXCtrl.SetValue(area.l1xp)
        self.areaLayer1ParaYCtrl.SetValue(area.l1xp)
        self.areaLayer1ScrXCtrl.SetValue(area.l1xs)
        self.areaLayer1ScrYCtrl.SetValue(area.l1ys)

        self.areaLayer2X1Ctrl.SetValue(area.l2x)
        self.areaLayer2Y1Ctrl.SetValue(area.l2y)
        self.areaLayer2ParaXCtrl.SetValue(area.l2xp)
        self.areaLayer2ParaYCtrl.SetValue(area.l2yp)
        self.areaLayer2ScrXCtrl.SetValue(area.l2xs)
        self.areaLayer2ScrYCtrl.SetValue(area.l2ys)
        
        if area.music != 255:
            self.areaMusicList.SetSelection(area.music)
    
    def OnSelectAreaMusic(self, evt):
        self.changeAreaMusic(evt.GetSelection())
        self.modify()
        
    def changeAreaMusic(self, num):
        self.curArea.music = num
    
    def OnToggleAreaLayer2Check(self, evt):
        self.curArea.hasLayer2 = evt.GetEventObject().GetValue()
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
    
    def OnSelectAreaLayer2Type(self, evt):
        self.curArea.layerType = evt.GetEventObject().context2
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
        
    def OnSelectAreaLayer1X1(self, evt):        self.changeAreaLayer1X1(evt.GetEventObject().GetValue())
    def OnSelectAreaLayer1Y1(self, evt):        self.changeAreaLayer1Y1(evt.GetEventObject().GetValue())
    def OnSelectAreaLayer1X2(self, evt):        self.changeAreaLayer1X2(evt.GetEventObject().GetValue())
    def OnSelectAreaLayer1Y2(self, evt):        self.changeAreaLayer1Y2(evt.GetEventObject().GetValue())
    
    def OnSelectAreaLayer1XParallax(self, evt):
        self.curArea.l1xp = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer1YParallax(self, evt):
        self.curArea.l1yp = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer1XScroll(self, evt):
        self.curArea.l1xs = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer1YScroll(self, evt):
        self.curArea.l1ys = evt.GetEventObject().GetValue()
        self.modify()    
        
    def OnSelectAreaLayer2X1(self, evt):        self.changeAreaLayer2X1(evt.GetEventObject().GetValue())
    def OnSelectAreaLayer2Y1(self, evt):        self.changeAreaLayer2Y1(evt.GetEventObject().GetValue())

    def OnSelectAreaLayer2XParallax(self, evt):
        self.curArea.l2xp = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer2YParallax(self, evt):
        self.curArea.l2yp = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer2XScroll(self, evt):
        self.curArea.l2xs = evt.GetEventObject().GetValue()
        self.modify()
    def OnSelectAreaLayer2YScroll(self, evt):
        self.curArea.l2ys = evt.GetEventObject().GetValue()
        self.modify()
        
    def changeAreaLayer1X1(self, num):
        self.curArea.l1x1 = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
    def changeAreaLayer1Y1(self, num):
        self.curArea.l1y1 = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
    def changeAreaLayer1X2(self, num):
        self.curArea.l1x2 = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
    def changeAreaLayer1Y2(self, num):
        self.curArea.l1y2 = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()

    def changeAreaLayer2X1(self, num):
        self.curArea.l2x = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()
    def changeAreaLayer2Y1(self, num):
        self.curArea.l2y = num
        self.updateAreaProps()
        self.mapViewer.refreshMapView()
        self.modify()        
        
    # -------------------------
    
    def updateBlockTSList(self):
        num = self.blockTSList.GetSelection()
        self.blockTSList.Clear()
        self.blockTSList.AppendItems([ts.name for ts in [self.rom.data["tilesets"][idx] for idx in self.map.tilesetIdxes if idx < len(self.rom.data["tilesets"])]])
        self.blockTSList.SetSelection(num)
        
    def changeSetupList(self):
        
        self.eventConfigList.Clear()
        self.eventConfigList.AppendItems([s.name for s in self.map.setups])
        
        if len(self.map.setups):
            self.changeSetup(0)
    
    def updateSetupList(self):
        
        enabled = self.curEventType in [3,4,5]
        
        self.eventNameCtrl.Enable(True)
        self.eventConfigList.Enable(enabled)
        #self.eventConfigNameText.Enable(enabled)
        #self.eventConfigNameCtrl.Enable(enabled)
        #self.eventConfigFlagCheck.Enable(enabled)
        #self.eventConfigFlagCtrl.Enable(enabled)
        self.eventConfigAddButton.Enable(enabled)
        self.eventConfigCopyButton.Enable(enabled)
        self.eventConfigDelButton.Enable(enabled)
    
    def changeSetup(self, num):
        
        setup = self.map.setups[num]
        #self.eventConfigNameCtrl.SetValue(setup.getIndexedName())
        
        #self.eventConfigFlagCtrl.SetValue(0)
        
        """if setup.flag is not None:
            self.eventConfigFlagCheck.SetValue(True)
            self.eventConfigFlagCtrl.Enable(True)
            self.eventConfigFlagCtrl.SetValue(setup.flag)
        else:
            self.eventConfigFlagCheck.SetValue(False)
            self.eventConfigFlagCtrl.Enable(False)"""
            
        self.eventConfigList.SetSelection(num)
    
    def OnSelectEventType(self, evt):
        self.changeEventType(evt.GetSelection())
        
    def changeEventType(self, num):
        
        self.eventTypeList.SetSelection(num)
        self.curEventType = num
        
        if num < len(self.vcsEvent) and self.mainNotebook.GetSelection() == 4:
            self.mapViewer.updateContext(self.vcsEvent[num])
        
        self.updateSetupList()
                
        #self.eventPropBS.Detach(self.curEventProps)
        if self.curEventProps:
            self.curEventProps.Show(False)
        
        if self.curEventType == 0:
            self.curEventProps = self.eventPropWarp
        elif self.curEventType == 1:
            self.curEventProps = self.eventPropCopy
        elif self.curEventType == 2:
            self.curEventProps = self.eventPropItem
        else:
            self.curEventProps = None
        
        if self.curEventProps:
            self.curEventProps.Enable(True)
            self.curEventProps.Show()
        
        #self.eventPropBS.AddSizer(self.curEventProps)
        #self.curEventProps.Show(True)
        self.eventPropBS.RecalcSizes()
        self.eventPropBS.Layout()
        
        self.updateEventList()
        
        self.mapViewer.refreshMapView()
        
    def updateEventList(self):
        
        items = self.getCurrentEventList()
        
        self.eventList.Clear()

        if items:
            self.eventList.AppendItems([i.name for i in items])
            self.changeEvent(0)
        else:
            self.eventNameCtrl.SetValue("")
            self.eventNameCtrl.Enable(False)
            if self.curEventProps is not None:
                self.curEventProps.Enable(False)
    
    def OnSelectEvent(self, evt):
        self.changeEvent(evt.GetSelection())
        
    def changeEvent(self, num):
        
        self.eventList.SetSelection(num)
        self.curEventIdx = num
        t = self.curEventType
        
        self.eventNameCtrl.SetValue(self.getCurrentEvent().getIndexedName())
        
        if t == 0:  # warp event
            self.updateWarpProps()
        
        elif t == 1:  # block copy
            self.updateCopyProps()
            
        elif t == 2:  # obtainable items
            self.updateItemProps()
            
        
        self.mapViewer.refreshMapView()
    
    # ------------------------
    
    def updateWarpProps(self):
        
        obj = self.map.warps[self.curEventIdx]
        
        self.eventPropWarpXCtrl.Enable(True)
        self.eventPropWarpYCtrl.Enable(True)
        self.eventPropWarpXCtrl.SetValue(obj.x)
        self.eventPropWarpYCtrl.SetValue(obj.y)
        self.eventPropWarpYCheck.Enable(True)
        self.eventPropWarpXCheck.Enable(True)
        self.eventPropWarpYCheck.SetValue(False)
        self.eventPropWarpXCheck.SetValue(False)
        
        self.eventPropWarpXCtrl.Enable(not obj.sameX)
        self.eventPropWarpXCheck.SetValue(not obj.sameX)
            
        self.eventPropWarpYCtrl.Enable(not obj.sameY)
        self.eventPropWarpYCheck.SetValue(not obj.sameY)
        
        self.eventPropWarpDestXCheck.SetValue(not obj.sameDestX)
        self.eventPropWarpDestXCtrl.Enable(not obj.sameDestX)
        
        self.eventPropWarpDestYCheck.SetValue(not obj.sameDestY)
        self.eventPropWarpDestYCtrl.Enable(not obj.sameDestY)
        
        if obj.sameMap:
            self.eventPropWarpChangeCheck.SetValue(False)
            self.eventPropWarpMapList.Enable(False)
        else:
            self.eventPropWarpChangeCheck.SetValue(True)
            self.eventPropWarpMapList.Enable(True)
            self.eventPropWarpMapList.SetSelection(obj.destmap)
            
        self.eventPropWarpDestXCtrl.SetValue(obj.destx)
        self.eventPropWarpDestYCtrl.SetValue(obj.desty)
        
        self.warpFacingRadios[obj.destfacing].SetValue(True)

        # ------------------------
        # get center view point
            
        if self.mainNotebook.GetSelection() == 4:
            
            if obj.sameX:
                viewX = self.map.width / 2
            else:
                viewX = obj.x
            
            if obj.sameY:
                viewY = self.map.height / 2
            else:
                viewY = obj.y
            
            #if obj.sameMap:
            #    self.mapViewer.centerViewPos((obj.destx + viewX) / 2 * 24 + 12, (obj.desty + viewY) / 2 * 24 + 12)
            
            self.mapViewer.centerViewPos(viewX * 24 + 12, viewY * 24 + 12)

    
    def OnChangeWarpXCtrl(self, evt):
        self.changeWarpX(evt.GetSelection())
        
    def changeWarpX(self, num):
        evt = self.getCurrentEvent()
        evt.x = num
        self.eventPropWarpXCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeWarpYCtrl(self, evt):
        self.changeWarpY(evt.GetSelection())
        
    def changeWarpY(self, num):
        evt = self.getCurrentEvent()
        evt.y = num
        self.eventPropWarpYCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def changeWarpMap(self, num):
        
        event = self.getCurrentEvent()
        diffMap = self.curMapIdx != num
        
        event.destmap = num
        event.sameMap = not diffMap
        
        self.eventPropWarpMapList.SetSelection(num)
        self.eventPropWarpChangeCheck.SetValue(diffMap)
        self.eventPropWarpMapList.Enable(diffMap)
        
        self.mapViewer.refreshMapView()
        self.modify()
        
    def OnChangeWarpDestXCtrl(self, evt):
        self.changeWarpDestX(evt.GetSelection())
        
    def changeWarpDestX(self, num):
        evt = self.getCurrentEvent()
        evt.destx = num
        self.eventPropWarpDestXCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeWarpDestYCtrl(self, evt):
        self.changeWarpDestY(evt.GetSelection())
        
    def changeWarpDestY(self, num):
        evt = self.getCurrentEvent()
        evt.desty = num
        self.eventPropWarpDestYCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()
    
    def OnToggleWarpLineCheck(self, evt):
        
        event = self.getCurrentEvent()
        obj = evt.GetEventObject()
        wasSet = obj.GetValue()
        
        colWasUnset = obj == self.eventPropWarpXCheck and not wasSet
        rowWasUnset = obj == self.eventPropWarpYCheck and not wasSet
        colSet = rowWasUnset or self.eventPropWarpXCheck.GetValue()
        rowSet = colWasUnset or self.eventPropWarpYCheck.GetValue()
        
        event.sameX = not colSet
        event.sameY = not rowSet
        
        self.eventPropWarpXCheck.SetValue(colSet)
        self.eventPropWarpYCheck.SetValue(rowSet)
        
        self.eventPropWarpXCtrl.Enable(colSet)
        self.eventPropWarpYCtrl.Enable(rowSet)
        
        self.mapViewer.refreshMapView()
        self.modify()
            
    def OnToggleWarpChangeCheck(self, evt):
        event = self.getCurrentEvent()
        event.sameMap = evt.GetSelection()
        self.eventPropWarpMapList.Enable(evt.GetSelection())
        self.mapViewer.refreshMapView()
        self.modify()

    def OnSelectWarpMap(self, evt):
        self.changeWarpMap(evt.GetEventObject().GetSelection())
        
    def OnToggleWarpDestLineCheck(self, evt):
        
        event = self.getCurrentEvent()
        obj = evt.GetEventObject()
        wasSet = obj.GetValue()
        
        colSet = obj = self.eventPropWarpDestXCheck.GetValue()
        rowSet = obj = self.eventPropWarpDestYCheck.GetValue()
        
        event.sameDestX = not colSet
        event.sameDestY = not rowSet
        
        self.eventPropWarpDestXCtrl.Enable(colSet)
        self.eventPropWarpDestYCtrl.Enable(rowSet)
        
        self.mapViewer.refreshMapView()
        self.modify()
        
    def OnSelectWarpFacing(self, evt):
        obj = evt.GetEventObject()
        self.map.warps[self.curEventIdx].destfacing = obj.context
        self.modify()
        
    # ----------------
    
    def updateCopyProps(self):
        
        obj = self.map.copies[self.curEventIdx]
        
        [self.eventPropCopyFlagRadio, self.eventPropCopyPermRadio, self.eventPropCopyTempRadio][obj.copyType].SetValue(True)
        self.eventPropCopyFlagCtrl.SetValue(obj.flag)
        self.eventPropCopyFlagCtrl.Enable(obj.copyType==0)
        
        self.eventPropCopyTrigXCtrl.Enable(obj.copyType!=0)
        self.eventPropCopyTrigYCtrl.Enable(obj.copyType!=0)
        
        self.eventPropCopyTrigXCtrl.SetValue(obj.x)
        self.eventPropCopyTrigYCtrl.SetValue(obj.y)
        self.eventPropCopyWidthCtrl.SetValue(obj.width)
        self.eventPropCopyHeightCtrl.SetValue(obj.height)
        self.eventPropCopyDestXCtrl.SetValue(obj.destx)
        self.eventPropCopyDestYCtrl.SetValue(obj.desty)

        self.eventPropCopyBlankCheck.SetValue(obj.copyBlank)
        self.eventPropCopySrcXCtrl.Enable(not obj.copyBlank)
        self.eventPropCopySrcYCtrl.Enable(not obj.copyBlank)
        
        if not obj.copyBlank:
            self.eventPropCopySrcXCtrl.SetValue(obj.srcx)
            self.eventPropCopySrcYCtrl.SetValue(obj.srcy)

        # ------------------------
        # get center view point
            
        if self.mainNotebook.GetSelection() == 4:

            if obj.copyType == 0:
                viewX = obj.srcx * 24 + obj.width * 12
                viewY = obj.srcy * 24 + obj.height * 12
            else:
                viewX = obj.x * 24
                viewY = obj.y * 24
            
            self.mapViewer.centerViewPos(viewX, viewY)
    
    def OnToggleCopyBlankCheck(self, evt):
        self.setCopyBlank(evt.GetSelection())
        
    def setCopyBlank(self, val=True):
        evt = self.getCurrentEvent()
        evt.copyBlank = val
        
        self.eventPropCopySrcXCtrl.Enable(not val)
        self.eventPropCopySrcYCtrl.Enable(not val)
        
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopyTrigXCtrl(self, evt):
        self.changeCopyTrigX(evt.GetSelection())
        
    def changeCopyTrigX(self, num):
        evt = self.getCurrentEvent()
        evt.x = num
        self.eventPropCopyTrigXCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopyTrigYCtrl(self, evt):
        self.changeCopyTrigY(evt.GetSelection())
        
    def changeCopyTrigY(self, num):
        evt = self.getCurrentEvent()
        evt.y = num
        self.eventPropCopyTrigYCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopySrcXCtrl(self, evt):
        self.changeCopySrcX(evt.GetSelection())
        
    def changeCopySrcX(self, num):
        evt = self.getCurrentEvent()
        evt.srcx = num
        self.eventPropCopySrcXCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopySrcYCtrl(self, evt):
        self.changeCopySrcY(evt.GetSelection())
        
    def changeCopySrcY(self, num):
        evt = self.getCurrentEvent()
        evt.srcy = num
        self.eventPropCopySrcYCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()
        
    def OnChangeCopyDestXCtrl(self, evt):
        self.changeCopyDestX(evt.GetSelection())
        
    def changeCopyDestX(self, num):
        evt = self.getCurrentEvent()
        evt.destx = num
        self.eventPropCopyDestXCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopyDestYCtrl(self, evt):
        self.changeCopyDestY(evt.GetSelection())
        
    def changeCopyDestY(self, num):
        evt = self.getCurrentEvent()
        evt.desty = num
        self.eventPropCopyDestYCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopyWidthCtrl(self, evt):
        self.changeCopyWidth(evt.GetSelection())
        
    def changeCopyWidth(self, num):
        evt = self.getCurrentEvent()
        evt.width = num
        self.eventPropCopyWidthCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeCopyHeightCtrl(self, evt):
        self.changeCopyHeight(evt.GetSelection())
        
    def changeCopyHeight(self, num):
        evt = self.getCurrentEvent()
        evt.height = num
        self.eventPropCopyHeightCtrl.SetValue(num)
        self.mapViewer.refreshMapView()
        self.modify()
    
    def OnClickCopyTypeRadio(self, evt):
        self.changeCopyType(evt.GetEventObject().context)
    
    def changeCopyType(self, num):
        
        evt = self.getCurrentEvent()
        evt.copyType = num
        
        [self.eventPropCopyFlagRadio, self.eventPropCopyPermRadio, self.eventPropCopyTempRadio][num].SetValue(True)
        
        self.eventPropCopyTrigXCtrl.Enable(num != 0)
        self.eventPropCopyTrigYCtrl.Enable(num != 0)
        self.eventPropCopyFlagCtrl.Enable(num == 0)
        
        self.mapViewer.refreshMapView()
        self.modify()
    
    def OnChangeCopyFlagCtrl(self, evt):
        self.changeCopyFlag(evt.GetSelection())
        
    def changeCopyFlag(self, num):
        evt = self.getCurrentEvent()
        evt.flag = num
        self.eventPropCopyFlagCtrl.SetValue(num)
        self.modify()
    
    # ----------------------
    
    def updateItemProps(self):
        
        obj = self.map.items[self.curEventIdx]
        
        self.eventNameCtrl.Enable(False)
        
        self.eventPropItemXCtrl.SetValue(obj.x)
        self.eventPropItemYCtrl.SetValue(obj.y)
        self.eventPropItemFlagCtrl.SetValue(obj.flag)
        
        itemIdx = obj.itemIdx
        isItem = obj.itemIdx < 127
        isNothing = obj.itemIdx == 127
        isGold = obj.itemIdx > 127
        
        self.eventPropItemList.Enable(isItem)
        self.eventPropItemGoldCtrl.Enable(isGold)
        
        if obj.itemIdx >= 128:
            self.eventPropItemGoldRadio.SetValue(True)
            gold = min(130, (obj.itemIdx-127) * 10)
            self.eventPropItemGoldCtrl.SetValue(gold)
            self.eventNameCtrl.SetValue("%i Gold" % gold)
        elif obj.itemIdx == 127:
            self.eventPropItemNoneRadio.SetValue(True)
            self.eventNameCtrl.SetValue(self.rom.data["items"][itemIdx].getIndexedName())
        else:
            self.eventPropItemItemRadio.SetValue(True)
            self.eventPropItemList.SetSelection(itemIdx)
            self.eventNameCtrl.SetValue(self.rom.data["items"][itemIdx].getIndexedName())
        
        self.eventPropItemChestCheck.SetValue(obj.isChest)

        # ------------------------
        # get center view point
            
        if self.mainNotebook.GetSelection() == 4:

            viewX = obj.x * 24 + 12
            viewY = obj.y * 24 + 12
            self.mapViewer.centerViewPos(viewX, viewY)
            
    def OnChangeItemXCtrl(self, evt):
        self.changeItemX(evt.GetEventObject().GetValue())
        
    def changeItemX(self, num):
        event = self.getCurrentEvent()
        event.x = num
        self.updateItemProps()
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeItemYCtrl(self, evt):
        self.changeItemY(evt.GetEventObject().GetValue())
        
    def changeItemY(self, num):
        event = self.getCurrentEvent()
        event.y = num
        self.updateItemProps()
        self.mapViewer.refreshMapView()
        self.modify()

    def OnChangeItemFlagCtrl(self, evt):
        self.changeItemFlag(evt.GetEventObject().GetValue())
        
    def changeItemFlag(self, num):
        event = self.getCurrentEvent()
        event.flag = num
        self.updateItemProps()
        self.modify()
    
    def OnSelectItemType(self, evt):
        obj = evt.GetEventObject()
        
        if obj.context == 0:  # item
            self.changeItemType(self.eventPropItemList.GetSelection())
        elif obj.context == 1:  # gold
            
            self.changeItemType(self.eventPropItemGoldCtrl.GetValue() / 10 + 127)
        elif obj.context == 2:  # nothing
            self.changeItemType(127)
            
    def changeItemType(self, num):
        event = self.getCurrentEvent()
        event.itemIdx = num
        self.updateItemProps()
        self.mapViewer.refreshMapView()
        self.modify()

    def OnToggleItemChestCheck(self, evt):
        self.curEvent.isChest = evt.GetEventObject().GetValue()
        self.modify()

    # -----------------------
    
    def OnChangeAnim(self, evt):
        self.changeAnim(evt.GetSelection())
    
    def OnClickAnimTSPanel(self, evt):

        if self.curAnimIdx is not None:
            
            obj = evt.GetEventObject()
            x = evt.GetX()/obj.scale/8
            y = evt.GetY()/obj.scale/8
            sel = y*16 + x
            
            if evt.LeftIsDown():
            
                if not evt.ShiftDown():
                    self.changeAnimStart(sel)
                else:
                    self.changeAnimEnd(sel+1)
                    
                self.modify()
    
    def OnSelectAnimTS(self, evt):
        num = evt.GetSelection()
        self.map.animTSIdx = num
        self.updateAnimTileset()
        self.refreshPixels()
        self.modify()
        
    def OnChangeAnimStart(self, evt):
        self.changeAnimStart(evt.GetSelection())
    def OnChangeAnimEnd(self, evt):
        self.changeAnimEnd(evt.GetSelection())
    def OnChangeAnimDest(self, evt):
        self.changeAnimDest(evt.GetSelection())
    def OnChangeAnimDelay(self, evt):
        self.changeAnimDelay(evt.GetSelection())
        
    def changeAnim(self, num):
        
        if num < len(self.map.anims):
            self.curAnimIdx = num
        else:
            self.curAnimIdx = None
            
        self.updateAnimProps()
    
    def changeAnimStart(self, val):
        self.animStart.SetValue(val)
        self.map.anims[self.curAnimIdx].start = val
        self.modify()
    def changeAnimEnd(self, val):
        self.animEnd.SetValue(val)
        self.map.anims[self.curAnimIdx].end = val
        self.modify()
    def changeAnimDest(self, val):
        self.animDest.SetValue(val)
        self.map.anims[self.curAnimIdx].dest = val
        self.modify()
    def changeAnimDelay(self, val):
        self.animDelay.SetValue(val)
        self.map.anims[self.curAnimIdx].delay = val
        self.modify()
        
    def updateAnimProps(self):
        
        self.animNameCtrl.SetValue("")
        
        self.animTSList.SetSelection(0)
        
        self.animStart.SetValue(0)
        self.animEnd.SetValue(0)
        self.animDest.SetValue(0)
        self.animDelay.SetValue(0)
        
        # ----
        
        hasAnim = self.curAnimIdx is not None
        
        self.animNameCtrl.Enable(hasAnim)
        
        self.animTSList.Enable(hasAnim)
        
        self.animStart.Enable(hasAnim)
        self.animEnd.Enable(hasAnim)
        self.animDest.Enable(hasAnim)
        self.animDelay.Enable(hasAnim)
        
        self.animTSPanel.Enable(hasAnim)
        
        if hasAnim:
            
            anim = self.map.anims[self.curAnimIdx]
            
            self.animList.SetSelection(self.curAnimIdx)
            
            self.animNameCtrl.SetValue(anim.name)
            
            self.animTSList.SetSelection(self.map.animTSIdx)
            
            self.animStart.SetValue(anim.start)
            self.animEnd.SetValue(anim.end)
            self.animDest.SetValue(anim.dest)
            self.animDelay.SetValue(anim.delay)
            
    def updateAnimTSList(self):
        
        num = self.animTSList.GetSelection()
        self.animTSList.Clear()
        self.animTSList.AppendItems([ts.name for ts in self.rom.data["tilesets"]])
        self.animTSList.SetSelection(num)
            
    def updateAnimTileset(self):
        
        tsList = self.animTSList
        tsSelect = tsList.GetSelection()
        self.animTileset = self.rom.data["tilesets"][tsSelect]
        self.curAnimTSIdx = tsSelect
        
    # -----------------------
    
    def getCurrentEventList(self):
        
        if self.curEventType == 0:
            return self.map.warps
        elif self.curEventType == 1:
            return self.map.copies
        elif self.curEventType == 2:
            return self.map.items
        
        return None
        
    def getCurrentEvent(self):
        
        lst = self.getCurrentEventList()
        
        if lst:
            return lst[self.curEventIdx]
        
        return None
    
    # general prop methods
    
    def OnChangeEventName(self, evt):
        
        event = self.getCurrentEvent()
        if event:
            event.setIndexedName(evt.GetString())
            self.eventList.SetString(self.curEventIdx, "%i: %s" % (self.curEventIdx, evt.GetString()))
    
    # item methods
    

        
    # ----
    
    def drawMapData(self, obj, dc):
        
        spec = None
        if hasattr(obj, "special"):
            spec = obj.special
            
        if (self.curViewMode and not self.viewAll) or spec:
            dc.SetBrush(obj.darkBGBrush)
            dc.SetPen(obj.transPen)
            dc.DrawRectangle(0, 0, 24, 24)
        
        if self.curViewMode or self.viewAll or spec:
            
            dc.SetBrush(obj.transBrush)
            
            if spec is None:
                
                x = self.curViewX + (obj.id % self.viewWidth)
                y = self.curViewY + (obj.id / self.viewWidth)
                
                blk = self.map.layoutData[y*64+x]
            
            else:
                
                blk = spec
                
            mask = blk & 0x3c00
            obsMask = blk & 0xc000
            
            noObs = False
            noEvt = False

            if obsMask == 0xc000:
                dc.SetPen(obj.obsPen)
                dc.DrawLine(4, 4, 20, 20)
                dc.DrawLine(20, 4, 4, 20)
            elif obsMask == 0x8000:
                dc.SetPen(obj.stairsPen)
                dc.DrawLine(20, 4, 4, 20)
            elif obsMask == 0x4000:
                dc.SetPen(obj.stairsPen)
                dc.DrawLine(4, 4, 20, 20)
            else:
                noObs = True
                
            if mask == 0x1000:
                dc.SetPen(obj.zonePen)
                dc.DrawRectangle(4, 4, 16, 16)
            elif mask == 0x1400:
                dc.SetPen(obj.eventPen)
                dc.DrawRectangle(4, 4, 16, 16)
            elif mask == 0x1800:
                dc.SetPen(obj.chestPen)
                dc.DrawCircle(12, 4, 1)
                dc.DrawCircle(20, 12, 1)
                dc.DrawCircle(12, 20, 1)
                dc.DrawCircle(4, 12, 1)
            elif mask == 0x1c00:
                dc.SetPen(obj.floorPen)
                dc.DrawCircle(12, 4, 1)
                dc.DrawCircle(20, 12, 1)
                dc.DrawCircle(12, 20, 1)
                dc.DrawCircle(4, 12, 1)
            elif mask == 0x2c00:
                dc.SetPen(obj.vasePen)
                dc.DrawCircle(12, 4, 1)
                dc.DrawCircle(20, 12, 1)
                dc.DrawCircle(12, 20, 1)
                dc.DrawCircle(4, 12, 1)
            elif mask == 0x3000:
                dc.SetPen(obj.barrelPen)
                dc.DrawCircle(12, 4, 1)
                dc.DrawCircle(20, 12, 1)
                dc.DrawCircle(12, 20, 1)
                dc.DrawCircle(4, 12, 1)
            elif mask == 0x2800:
                dc.SetPen(obj.tablePen)
                dc.DrawLine(4, 12, 20, 12)
                dc.DrawLine(12, 4, 12, 20)
            elif mask == 0x0800:
                dc.SetPen(obj.roofPen1)
                dc.DrawCircle(12, 12, 8)
            elif mask == 0x0c00:
                dc.SetPen(obj.roofPen2)
                dc.DrawCircle(12, 12, 8)
            elif mask == 0x0400:
                dc.SetPen(obj.roofPen3)
                dc.DrawCircle(12, 12, 8)
            else:
                noEvt = True

            if blk & 0xfc00 and noObs and noEvt:
                dc.SetPen(obj.otherPen)
                dc.DrawCircle(12, 12, 8)

    def receiveClickReport(self, evt, data):
        pass
    
    def getCurrentEventCoords(self):
        
        
        if self.mapViewer.viewerContext == consts.VC_EVENT_WARP:
            
            obj = self.getCurrentEvent()
            
            x, y = obj.x, obj.y
            
            if obj.sameX:
                x = 0
                w = self.map.width
            else:
                w = 1
            
            if obj.sameY:
                y = 0
                h = self.map.height
            else:
                h = 1
                
            return x,y,w,h
        
        elif self.mapViewer.viewerContext == consts.VC_AREA:
            
            obj = self.curArea
            
            x, y, w, h = obj.l1x1, obj.l1y1, obj.l1x2 - obj.l1x1, obj.l1y2 - obj.l1y1
            return x,y,w,h
            
        else:
            
            obj = self.getCurrentEvent()
            
            return obj.x, obj.y, 1, 1
                
    def updateTileset(self):
        
        tsSelect = self.blockTSList.GetSelection()
        for i in range(5):
            if i <= tsSelect and self.map.tilesetIdxes[i] == 255:
                tsSelect += 1
                
        tsIdx = self.map.tilesetIdxes[tsSelect]
        self.tileset = self.rom.data["tilesets"][tsIdx]
        self.curTilesetIdx = tsIdx
        self.curTilesetSel = tsSelect
        
    def OnSelectPalette(self, evt):
        
        num = evt.GetSelection()
        self.map.paletteIdx = num
        self.changePalette(num)
        self.modify()
        
        if self.mapViewer.inited:
            self.mapViewer.mapViewPanel.palette = self.palette
            self.mapViewer.mapViewPanel.updateBlockBMPs()
            self.mapViewer.refreshMapView()
    
    def OnSelectTileset(self, evt):
        
        num = evt.GetSelection()
        obj = evt.GetEventObject()
        
        for i,tsl in enumerate(self.tilesetLists):
            if obj is tsl:
                self.map.tilesetIdxes[i] = num
                
                if not self.rom.data["tilesets"][num].loaded:
                    self.rom.getTilesets(num, num)
            
                for b in self.map.blocks:
                    if i in b.uniqueTilesetIdxes:
                        for n,tsi in enumerate(b.tilesetIdxes):
                            if tsi == i:
                                b.tiles[n] = self.rom.data["tilesets"][num].tiles[b.tileIdxes[n] % 128]
                        b.createPixelArray()
                        
                self.updateBlockTSList()
                self.updateTileset()
                self.changeBlockList()
                self.changeBlockEditList()
                self.updateAnimTSList()
                self.updateAnimTileset()
                self.refreshPixels()
                self.modify()
                self.mapViewer.mapViewPanel.updateBlockBMPs()#refreshMapView()
                break
        
    def changePalette(self, num):
    
        self.paletteList.SetSelection(num)
        self.palette = self.rom.data["palettes"][num]
        self.changeColors(num)
        
    def getCurrentData(self):
        return self.map

    def createMapViewer(self, map=None, palette=None, show=True):
        
        window.MapViewer.init(map, palette)
        
        if not window.mapViewer.IsShown():
            window.mapViewer.Show()
        if show:
            window.mapViewer.SetFocus()
            window.mapViewer.Raise()
            
    changeSelection = changeMap
    
    vcsBlock = [consts.VC_BLOCKS, consts.VC_FLAGS]
    vcsEvent = [consts.VC_EVENT_WARP, consts.VC_EVENT_COPY, consts.VC_EVENT_ITEM]
    
    #curMapIdx = property(lambda self: self.mapList.GetSelection())
    curAreaIdx = property(lambda self: self.areaList.GetSelection())
        
    curArea = property(lambda self: self.map.areas[self.curAreaIdx])
    curEvent = property(lambda self: self.getCurrentEvent())
    