import wx, rompanel, binascii
import sys
sys.path.insert(0, '../')
import data

from PIL import Image

h2i = lambda i: int(i, 16)

class WeaponSpritePanel(rompanel.ROMPanel):
    
    frameTitle = "Weapon Sprite Editor"
    
    def init(self):
        
        self.palette = self.rom.getDataByName("palettes", "Sprite & UI Palette")
        self.side = 0
        self.frame = 0
        self.mode = 0
        
        self.color_left = 0
        self.color_right = 0
        
        self.curFrameIdx = 0
        self.curPaletteIdx = 0
        
        # -------------------------------
        
        #self.rom.data["weapon_sprites"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit weapon sprite graphics.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        #sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "1. Select a weapon sprite."), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Chars/scenes using this weapon sprite"), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Change Animation"), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Palette and Frame"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.HORIZONTAL)
        #sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Preview Animation"), wx.VERTICAL)
        #sbs5.StaticBox.SetSize((0,0))
        #sbs6 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        """self.weaponSpriteList = wx.ComboBox(self, wx.ID_ANY, size=(200,-1))
        self.weaponSpriteList.AppendItems([bs.name for bs in self.rom.data["weapon_sprites"]])
        self.weaponSpriteList.SetSelection(0)

        sbs1.Add(self.weaponSpriteList, 0, wx.ALL, 10)
        sbs1.Add((0,10))"""
        
        # -----------------------
        
        #self.charList = wx.ListBox(self, wx.ID_ANY, size=(200,40))
        
        #sbs2.Add(self.charList, 1, wx.ALL, 10)
        
        self.frameList = wx.ComboBox(self, wx.ID_ANY, size=(100,-1))
        self.paletteList = wx.ComboBox(self, wx.ID_ANY, size=(100,-1))
        
        sbs3.Add(self.frameList, 0, wx.LEFT | wx.TOP, 5)
        sbs3.Add(self.paletteList, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 5)

        # -----------------------
        
        """animButtonSizer = wx.FlexGridSizer(3,2)
        self.animButtons = []
        for i,bt in enumerate(["Walk", "Run", "Nod", "Shake", "Shock", "Jump"]):
            b = wx.Button(self, wx.ID_ANY, bt, size=(40,20))
            if i > 1:
                b.Enable(False)
            self.animButtons.append(b)
            animButtonSizer.Add(b, flag=wx.ALL, border=5)
            
        sbs3.AddSizer(animButtonSizer, 0)"""
        
        # -----------------------
        
        text1 = wx.StaticText(self, -1, "Colors")
        text2 = wx.StaticText(self, -1, "Sprite (Color 0 = trans)")
        """text3 = wx.StaticText(self, -1, "Left-Click")
        text4 = wx.StaticText(self, -1, "Right-Click")
        text5 = wx.StaticText(self, -1, "Mode")"""
        
        self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 8*8, 8*8, self.palette, scale=3, bg=16, func="edit")
        #self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 96, 96, self.palette, scale=2, bg=16, func="edit")
        
        #self.testPanel.refreshSprite([]
        #self.testPanel.Refresh()
        
        self.colorPanels = []
        for p in range(16):
            self.colorPanels.append(rompanel.ColorPanel2(self, wx.ID_ANY, "#000000", num=p))
        
        self.changeColors()
        
        self.importButton = wx.Button(self, wx.ID_ANY, "Import", size=(40,20))
        self.exportButton = wx.Button(self, wx.ID_ANY, "Export", size=(40,20))
        
        self.importButton.Enable(False)
        
        #self.commandText = wx.TextCtrl(self, wx.ID_ANY, size=(150,200), style=wx.TE_MULTILINE)
        
        sbs4left = wx.BoxSizer(wx.VERTICAL)
        
        colorSizer = wx.FlexGridSizer(8,2)
        colorSizer.AddMany(self.colorPanels)
        
        sbs4left.Add(text1, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4left.AddSizer(colorSizer, 0)
        sbs4left.Add(self.importButton, 0, wx.TOP | wx.ALIGN_CENTER, 5)
        sbs4left.Add(self.exportButton, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)
            
        #self.rbBut = wx.Button(self, wx.ID_ANY, "rb")
        #self.hexBut = wx.Button(self, wx.ID_ANY, "hex")
        
        sbs4mid = wx.BoxSizer(wx.VERTICAL)
        
        sbs4mid.Add(text2, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4mid.Add(self.editPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        #sbs4mid.Add(self.rbBut, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        #sbs4mid.Add(self.hexBut, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        #sbs4mid.Add(self.testPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        
        """sbs4right = wx.BoxSizer(wx.VERTICAL)
        
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
        sbs4right.Add(self.modeReplace, 0, wx.LEFT | wx.BOTTOM, 5)"""
        
        sbs4.AddSizer(sbs4left, 0, wx.ALL ^ wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        sbs4.AddSizer(sbs4mid, 1, wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        #sbs4.AddSizer(sbs4right, 0, wx.ALL ^ wx.LEFT | wx.ALIGN_CENTER | wx.ALIGN_TOP | wx.EXPAND, 10)
        
        # ------------------------

        """self.animList = wx.ComboBox(self, wx.ID_ANY, size=(100,-1))
        self.animList.AppendItems(["Idle", "Attack", "Defend"])
        self.animList.SetSelection(0)
        
        self.animPanel = rompanel.SpritePanel(self, wx.ID_ANY, 96, 96, self.palette, scale=1, bg=None, edit=False)
        #self.animPanel.buffer = wx.EmptyBitmap(*self.animPanel.GetSize())
        #self.animPanel.refreshSprite(self.rom.data["battle_sprites"][0].pixels
        #self.animPanel.Refresh()
    
        self.animDelays = [250, 150, 50, 50, 50, 50]
        self.animFrame = 0
        self.animCur = 0
        
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.changeAnim(0)
        
        sbs5.Add(self.animPanel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sbs5.Add(self.animList, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # ------------------------
        
        animSpdText = wx.StaticText(self, -1, "Anim Speed")
        mystText = wx.StaticText(self, -1, "???")
        
        self.animSpdCtrl = wx.SpinCtrl(self, wx.ID_ANY, size=(65,20), min=0)
        self.mystCtrl = wx.SpinCtrl(self, wx.ID_ANY, size=(65,20), min=0, max=65535)
        
        sbs2.Add(animSpdText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        sbs2.Add(self.animSpdCtrl, 0, wx.ALIGN_CENTER | wx.TOP, 3)
        sbs2.Add(mystText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        sbs2.Add(self.mystCtrl, 0, wx.ALIGN_CENTER | wx.TOP, 3)
        sbs2.Add((0,5))"""
        
        # ------------------------
        
        #self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        #sbs6.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------
        
        midSizer = wx.BoxSizer(wx.HORIZONTAL)
        midRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        midSizer.AddSizer(sbs4, 0, flag=wx.EXPAND)
        midRightSizer.AddSizer(sbs3, 0, flag=wx.EXPAND)
        #midRightSizer.AddStretchSpacer(1)
        #midRightSizer.AddSizer(sbs5, 0, flag=wx.EXPAND)
        #midRightSizer.AddStretchSpacer(1)
        #midRightSizer.AddSizer(sbs2, 0, flag=wx.EXPAND)
        midSizer.AddSizer(midRightSizer, 1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        #self.Sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        #self.sizer.AddSizer(sbs1, pos=(1,0))
        #self.sizer.AddSizer(sbs2, pos=(0,0), flag=wx.EXPAND)
        self.sizer.AddSizer(midSizer, pos=(0,0), span=(1,2))
        #self.sizer.AddSizer(sbs6, pos=(3,0), span=(1,2), flag=wx.EXPAND)
        
        #self.changeEditGlyph(self.rom.fontOrder[0])
        
        self.changeWeaponSprite(0)
        
        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.weaponSpriteList.GetId(), self.OnSelectWeaponSprite)
        wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        wx.EVT_COMBOBOX(self, self.frameList.GetId(), self.OnSelectFrame)
        
        """wx.EVT_RADIOBUTTON(self, self.modePixel.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeFill.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeReplace.GetId(), self.OnSelectMode)"""

        wx.EVT_BUTTON(self, self.importButton.GetId(), self.OnImportImage)
        wx.EVT_BUTTON(self, self.exportButton.GetId(), self.OnExportImage)
        
        #wx.EVT_BUTTON(self, wx.ID_ANY, self.OnChangeAnim)

        #wx.EVT_BUTTON(self, self.rbBut.GetId(), self.printrb)
        #wx.EVT_BUTTON(self, self.hexBut.GetId(), self.printhex)
        
        #wx.EVT_TIMER(self, self.timer.GetId(), self.TimerTest)
        
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

    def printrb(self, evt):
        rb = self.curFrame.raw_bytes.split("\n")
        hx = self.curFrame.hexlify().split("\n")
        
        for i in range(max(len(rb), len(hx))):
            
            line1 = ""
            line2 = ""
            
            if i < len(rb):
                line1 = rb[i]
            
            if i < len(hx):
                line2 = hx[i]
            
            if line1 and line2:
                print ["Different!!!","Same"][line1==line2]
                
            if not line1:
                line1 = "No line"
            if not line2:
                line2 = "No line"
                
            print line1
            print line2
            print ""
            
        #print self.weaponSprite.raw_bytes

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
                    
                    cols = ["#%02x%02x%02x" % (imgpal[i]/16*17, imgpal[i+1]/16*17, imgpal[i+2]/16*17) for i in range(0, 48, 3)]
                    pal = data.Palette()
                    pal.init(cols)
                    self.editPanel.palette = pal
                    self.palette = pal
                    
                    self.weaponSprite.palettes[self.curPaletteIdx] = pal
                    
                    imgdata = list(img.getdata())
                    pixels = "".join(["%x" % d for d in imgdata])
                    pixels = [pixels[i:i+size[0]] for i in range(0, size[0]*size[1], size[0])]
                        
                    self.curFrame.convertFromPixelRows(pixels)
                    
                    newtiles = [None]*len(self.curFrame.tiles)
                    order = self.curFrame.getTileOrder(imgw/8, imgh/8)
                    for i in range(len(newtiles)):
                        newtiles[order[i]] = self.curFrame.tiles[i]
                    self.curFrame.tiles = newtiles
                
                    # ------------------
                    
                    self.changeWeaponSprite()
                    
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
            
    """def OnShow(self, evt):
        for p in range(16):
            self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
            self.colorPanels[p].Refresh()
        self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        self.selectedColorLeft.Refresh()
        self.selectedColorRight.Refresh()"""
        
    def TimerTest(self, evt):
        
        self.animFrame ^= 1
        #self.changeAnimWeaponSprite()
        
        #if not self.printed:
        #    print "\n".join(dir(evt))
        #    self.printed = True
            
    def changeColors(self):
        palette = self.palette
        for c in range(len(self.colorPanels)):
            self.colorPanels[c].SetBackgroundColour(palette.colors[c])
            self.colorPanels[c].Refresh()

    def OnSelectPalette(self, evt):
        
        self.curPaletteIdx = evt.GetSelection()
        self.changeWeaponSprite()
        
    def OnSelectFrame(self, evt):
        
        self.curFrameIdx = evt.GetSelection()
        self.changeWeaponSprite()        
        
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
        
        """h = self.curFrame.hexlify()
        self.symbolsBox.SetValue(h)
        
        h = h.strip(":").strip()
        b = self.curFrame.raw_bytes.strip(":").strip()
        
        sizeOrig = len(b)/2
        sizeCur = len(h)/2
        
        self.sizeOrigText.SetLabel("Original: %i" % (len(b)/2))
        self.sizeCurText.SetLabel("Current:  %i" % (len(h)/2))
        
        if sizeOrig >= sizeCur:
            self.sizeOrigText.SetForegroundColour("#008800")
            self.sizeCurText.SetForegroundColour("#008800")
            self.sizeText.SetLabel("It is safe to save this piece of data.")
        else:
            self.sizeOrigText.SetForegroundColour("#880000")
            self.sizeCurText.SetForegroundColour("#880000")
            self.sizeText.SetLabel("It is NOT safe to save this piece of data.\nTry making it less \"complicated\".")"""
            
        #f = open("spr_in.txt", "wb")
        #f.write(self.weaponSprite.raw_bytes)
        #f.close()
    
        #f = open("spr_out.txt", "wb")
        #f.write(h)
        #f.close()
        
        #self.charList.Clear()
        #self.charList.Append(hex(self.rom.tables["weapon_sprites"][int(self.weaponSprite.name.split(" ")[1])*3 + self.side]))
        #self.charList.Append(`len(self.weaponSprite.raw_bytes)`)
        #self.charList.Append(`len(h)`)
        
        #h = h.replace("\n","").replace(" ","").replace(":","")
        
        #f = open("%s %i.txt" % (self.weaponSprite.name, self.side), "wb")
        #f.write(binascii.unhexlify(h))
        #f.close()
        
        #if self.frame == 0:
        #    self.testPanel.refreshSprite(self.rom.portraitSubroutine(h).pixels
        #else:
        #    self.testPanel.refreshSprite(self.rom.portraitSubroutine(h).pixels2
        #self.testPanel.Refresh()
    
        pass
        
    def OnChangeAnim(self, evt):
        
        button = None
        for i,b in enumerate(self.animButtons):
            if b.GetId() == evt.GetId():
                button = i
                break
                
        if button is None:
            return
        
        self.changeAnim(button)

    def OnSelectMode(self, evt):

        l = [self.modePixel.GetId(), self.modeFill.GetId(), self.modeReplace.GetId()]
        self.mode = l.index(evt.GetId())
        
    def OnSelectWeaponSprite(self, evt):
        self.changeWeaponSprite(evt.GetSelection())
    
    def OnSwitchFrame(self, evt):
        self.frame ^= 1
        self.changeWeaponSprite(self.weaponSpriteList.GetSelection())
        
    def changeWeaponSprite(self, num=None):
        
        if num is not None:
            
            if not self.rom.data["weapon_sprites"][num].loaded:
                self.rom.getWeaponSprites(num, num)
            
            self.curPaletteIdx = 0
            self.curFrameIdx = 0
            
            self.weaponSprite = self.rom.data["weapon_sprites"][num]
            
            self.editPanel.width = 64
            self.editPanel.height = 64
            
            self.frameList.Clear()
            self.frameList.AppendItems(["Frame %i" % i for i,p in enumerate(self.weaponSprite.frames)])
            self.frameList.SetSelection(self.curFrameIdx)
            
            self.paletteList.Clear()
            self.paletteList.AppendItems(["Palette %i" % i for i,p in enumerate(self.weaponSprite.palettes)])
            self.paletteList.SetSelection(self.curPaletteIdx)
            
        self.palette = self.curPalette
        self.editPanel.palette = self.palette
        self.changeColors()
        
        pixels = []
        
        tw = self.editPanel.width / 8
        th = self.editPanel.height / 8
        
        order = self.curFrame.getTileOrder(tw, th)
        
        tiles = [self.curFrame.tiles[t] for t in order]
        
        for tRow in range(th):
            for pRow in range(8):
                row = "".join([tiles[tRow*tw+to].pixels[pRow] for to in range(tw)])
                pixels.append(row)
        self.editPanel.refreshSprite(pixels, force=True)
        
        self.updateModifiedIndicator(self.weaponSprite.modified)
        
        self.editPanel.Refresh()
        self.refreshPixels()
    
    def changeAnim(self, num):
        self.animCur = num
        self.timer.Start(self.animDelays[num])
        
    def changeAnimWeaponSprite(self):

        if self.animFrame == 0:
            self.animPanel.refreshSprite(self.curFrame.pixels)
        else:
            self.animPanel.refreshSprite(self.curFrame.pixels2)
            
        self.animPanel.Refresh()
        
    def getCurrentSpriteObject(self):
        return self.weaponSprite
        
    def getCurrentData(self):
        return self.weaponSprite
    
    changeSelection = changeWeaponSprite
    
    curFrame = property(lambda self: self.weaponSprite.frames[self.curFrameIdx])
    curPalette = property(lambda self: self.weaponSprite.palettes[self.curPaletteIdx])