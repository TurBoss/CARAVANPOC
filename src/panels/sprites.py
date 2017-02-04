import wx, rompanel, binascii
import sys
sys.path.insert(0, '../')
import data

from PIL import Image

h2i = lambda i: int(i, 16)

class SpritePanel(rompanel.ROMPanel):
    
    frameTitle = "Sprite Editor"
    
    def init(self):
        
        self.palette = self.rom.getDataByName("palettes", "Sprite & UI Palette")
        self.side = 0
        self.frame = 0
        self.mode = 0
        
        self.color_left = 0
        self.color_right = 0
        
        self.curSpriteIdx = 0
        
        # -------------------------------
        
        #self.rom.data["sprites"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit sprite graphics.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Direction"), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Chars/scenes using this sprite"), wx.VERTICAL)
        #sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Data Length"), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Change Animation"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.HORIZONTAL)
        sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Preview Animation"), wx.VERTICAL)
        sbs5.StaticBox.SetSize((0,0))
        #sbs6 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        #self.spriteList = wx.ComboBox(self, wx.ID_ANY, size=(200,-1))
        #self.spriteList.AppendItems([self.rom.data["sprites"][s*3].name for s in range(len(self.rom.data["sprites"])/3)]) #, "u2", "yay")
        #self.spriteList.SetSelection(0)
        
        radioSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.facingRadioUp = wx.RadioButton(self, wx.ID_ANY, "Up", style=wx.RB_GROUP)
        self.facingRadioSide = wx.RadioButton(self, wx.ID_ANY, "Left/Right")
        self.facingRadioDown = wx.RadioButton(self, wx.ID_ANY, "Down")
        
        radioSizer.Add(self.facingRadioUp, 0, wx.RIGHT, 5)
        radioSizer.Add(self.facingRadioSide, 0, wx.RIGHT, 5)
        radioSizer.Add(self.facingRadioDown, 0)
        
        #sbs1.Add(self.spriteList, 0, wx.ALL, 10)
        sbs1.AddSizer(radioSizer, 0, wx.LEFT | wx.EXPAND)
        sbs1.Add((0,10))
        
        # -----------------------
        
        #self.charList = wx.ListBox(self, wx.ID_ANY, size=(200,40))
        
        #sbs2.Add(self.charList, 1, wx.ALL, 10)
        
        """self.sizeOrigText = wx.StaticText(self, wx.ID_ANY, "")
        self.sizeCurText = wx.StaticText(self, wx.ID_ANY, "")
        self.sizeOrigText.SetFont(self.GetTopLevelParent().editFont)
        self.sizeCurText.SetFont(self.GetTopLevelParent().editFont)
        self.sizeText = wx.StaticText(self, -1, "It is safe to save this piece of data.")
        
        sbs2.Add(self.sizeOrigText, 0, wx.LEFT, 5)
        sbs2.Add(self.sizeCurText, 0, wx.LEFT, 5)
        sbs2.Add(self.sizeText, 0, wx.LEFT, 5)"""

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
        
        # -----------------------
        
        text1 = wx.StaticText(self, -1, "Colors")
        text2 = wx.StaticText(self, -1, "Sprite (Color 0 = trans)")
        text3 = wx.StaticText(self, -1, "Left-Click")
        text4 = wx.StaticText(self, -1, "Right-Click")
        text5 = wx.StaticText(self, -1, "Mode")
        
        self.editPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=8, bg=16, func="edit")
        
        #self.testPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=8)
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
            
        #self.rbBut = wx.Button(self, wx.ID_ANY, "rb")
        #self.hexBut = wx.Button(self, wx.ID_ANY, "hex")
        
        sbs4mid = wx.BoxSizer(wx.VERTICAL)
        
        sbs4mid.Add(text2, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        sbs4mid.Add(self.editPanel, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER, 5)
        #sbs4mid.Add(self.rbBut, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
        #sbs4mid.Add(self.hexBut, 0, wx.BOTTOM | wx.ALIGN_CENTER, 10)
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
        #self.animPanel.refreshSprite(self.rom.data["sprites"][0].pixels
        #self.animPanel.Refresh()
    
        self.animDelays = [250, 150, 50, 50, 50, 50]
        self.animFrame = 0
        self.animCur = 0
        
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.changeAnim(0)
        
        sbs5.Add(self.animPanel, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        # ------------------------
        
        #self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        #sbs6.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------
        
        midSizer = wx.BoxSizer(wx.HORIZONTAL)
        midRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        midSizer.AddSizer(sbs4, 0, flag=wx.EXPAND)
        midRightSizer.AddSizer(sbs5, 1, flag=wx.EXPAND)
        midRightSizer.AddSizer(sbs3, 1, flag=wx.EXPAND)
        midSizer.AddSizer(midRightSizer, 1, flag=wx.EXPAND | wx.LEFT, border=5)
        
        #self.Sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(sbs1, pos=(0,0))
        #self.sizer.AddSizer(sbs2, pos=(1,1), flag=wx.EXPAND)
        self.sizer.AddSizer(midSizer, pos=(1,0), span=(1,2))
        #self.sizer.AddSizer(sbs6, pos=(2,0), span=(1,2), flag=wx.EXPAND)
        
        #self.changeEditGlyph(self.rom.fontOrder[0])
        
        self.changeSprite(0)
        
        # ------------------------
        
        #wx.EVT_COMBOBOX(self, self.spriteList.GetId(), self.OnSelectSprite)
        
        wx.EVT_RADIOBUTTON(self, self.facingRadioUp.GetId(), self.OnSelectFacing)
        wx.EVT_RADIOBUTTON(self, self.facingRadioSide.GetId(), self.OnSelectFacing)
        wx.EVT_RADIOBUTTON(self, self.facingRadioDown.GetId(), self.OnSelectFacing)
        
        wx.EVT_RADIOBUTTON(self, self.modePixel.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeFill.GetId(), self.OnSelectMode)
        wx.EVT_RADIOBUTTON(self, self.modeReplace.GetId(), self.OnSelectMode)
        
        wx.EVT_BUTTON(self, wx.ID_ANY, self.OnChangeAnim)
        
        wx.EVT_BUTTON(self, self.importButton.GetId(), self.OnImportImage)
        wx.EVT_BUTTON(self, self.exportButton.GetId(), self.OnExportImage)
        
        wx.EVT_BUTTON(self, self.switchButton.GetId(), self.OnSwitchFrame)

        #wx.EVT_BUTTON(self, self.rbBut.GetId(), self.printrb)
        #wx.EVT_BUTTON(self, self.hexBut.GetId(), self.printhex)
        
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

    def printrb(self, evt):
        rb = self.sprite.raw_bytes.split("\n")
        hx = self.sprite.hexlify().split("\n")
        
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
            
        #print self.sprite.raw_bytes

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
                        self.sprite.pixels = pixels
                        self.sprite.raw_pixels = "".join(self.sprite.convertFromPixelRows(pixels))
                    else:
                        self.sprite.pixels2 = pixels
                        self.sprite.raw_pixels2 = "".join(self.sprite.convertFromPixelRows(pixels))
                    
                    """if self.frame == 0:
                        self.sprite.pixels = pixels
                    else:
                        self.sprite.pixels2 = pixels"""
                        
                    #self.sprite.convertFromPixelRows(pixels)
                    
                    """newtiles = [None]*len(self.curFrame.tiles)
                    order = self.curFrame.getTileOrder(imgw/8, imgh/8)
                    for i in range(len(newtiles)):
                        newtiles[order[i]] = self.curFrame.tiles[i]
                    self.curFrame.tiles = newtiles"""
                    
                    # ------------------
                    
                    self.changeSprite()
                    
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
            
            
    def OnShow(self, evt):
        for p in range(16):
            self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
            self.colorPanels[p].Refresh()
        self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        self.selectedColorLeft.Refresh()
        self.selectedColorRight.Refresh()
        
    def TimerTest(self, evt):
        
        self.animFrame ^= 1
        self.changeAnimSprite()
        
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
        
        #h = self.sprite.hexlify()
        #self.symbolsBox.SetValue(h)
        
        """h = h.replace(":","").replace(" ","").replace("\n","")
        b = self.sprite.raw_bytes.replace(":","").replace(" ","").replace("\n","")
        
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
        
        #f = open("%s %i.txt" % (self.sprite.name, self.side), "wb")
        #f.write(binascii.unhexlify(h))
        #f.close()
        
        #if self.frame == 0:
        #    self.testPanel.refreshSprite(self.rom.spriteSubroutine(h).pixels
        #else:
        #    self.testPanel.refreshSprite(self.rom.spriteSubroutine(h).pixels2
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
        
        evt.Skip()
            
        
    def OnSelectFacing(self, evt):

        l = [self.facingRadioUp.GetId(), self.facingRadioSide.GetId(), self.facingRadioDown.GetId()]
        self.side = l.index(evt.GetId())
        self.changeSprite(self.curSpriteIdx)

    def OnSelectMode(self, evt):

        l = [self.modePixel.GetId(), self.modeFill.GetId(), self.modeReplace.GetId()]
        self.mode = l.index(evt.GetId())
        
    def OnSelectSprite(self, evt):
        self.changeSprite(evt.GetSelection() * 3)
    
    def OnSwitchFrame(self, evt):
        self.frame ^= 1
        self.changeSprite(self.curSpriteIdx)
        
    def changeSprite(self, num=None):
        
        if num is not None:
            
            self.curSpriteIdx = num
            
            if not self.rom.data["sprites"][num].loaded:
                self.rom.getSprites(num, num+2)
                
            self.sprite = self.rom.data["sprites"][num+self.side]
            
        if self.frame == 0:
            self.editPanel.refreshSprite(self.sprite.pixels)
        else:
            self.editPanel.refreshSprite(self.sprite.pixels2)
        
        self.updateModifiedIndicator(self.sprite.modified)
        
        self.GetTopLevelParent().tempUndoStack = {}
        self.GetTopLevelParent().tempRedoStack = {}
        
        self.editPanel.Refresh()
        self.refreshPixels()
    
    def changeAnim(self, num):
        self.animCur = num
        self.timer.Start(self.animDelays[num])
        
    def changeAnimSprite(self):

        if self.animFrame == 0:
            self.animPanel.refreshSprite(self.sprite.pixels)
        else:
            self.animPanel.refreshSprite(self.sprite.pixels2)
            
        self.animPanel.Refresh()
        
    def getCurrentSpriteObject(self):
        return self.sprite
        
    def getCurrentData(self):
        return self.sprite
        
    changeSelection = changeSprite