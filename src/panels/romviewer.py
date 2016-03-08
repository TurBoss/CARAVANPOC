import wx, rompanel
import wx.grid as grid

import os, pickle
import layout

h2i = lambda i: int(i, 16)

class ROMViewerPanel(rompanel.ROMPanel):
    
    def init(self):
        
        inst = wx.StaticText(self, -1, "Edit ROM layout.")
        inst.Wrap(inst.GetClientSize()[0])
        
        self.curSectionIdx = 0
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Sections"), wx.VERTICAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Section Content"), wx.VERTICAL)
        sbs3 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Data Properties"), wx.VERTICAL)
        sbs4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Misc"), wx.VERTICAL)
        
        # -----------------------
        
        #self.sectionList = wx.ListBox(self, wx.ID_ANY, size=(150,300))
        
        self.sectionGrid = grid.Grid(self, wx.ID_ANY, size=(340,200))
        self.sectionGrid.SetRowLabelSize(35)
        self.sectionGrid.SetColLabelSize(20)
        self.sectionGrid.CreateGrid(10,4)
        self.sectionGrid.SetMargins(0,0)
        
        #w,h = self.sectionGrid.GetSize()
        #self.sectionGrid.SetSize((w+15,h))
            
        self.sectionGrid.SetColLabelValue(0, "Segment")
        self.sectionGrid.SetColLabelValue(1, "Type")
        self.sectionGrid.SetColLabelValue(2, "Start")
        self.sectionGrid.SetColLabelValue(3, "End")
        #self.sectionGrid.SetColLabelValue(4, "Comments")
        
        self.sectionGrid.SetColSize(0, 120)
        self.sectionGrid.SetColSize(1, 60)
        self.sectionGrid.SetColSize(2, 50)
        self.sectionGrid.SetColSize(3, 50)
        #self.sectionGrid.SetColSize(4, 200)
        
        leftColAttr = grid.GridCellAttr()
        fnt = self.sectionGrid.GetCellFont(0,0)
        fnt.SetWeight(wx.BOLD)
        leftColAttr.SetFont(fnt)

        self.sectionGrid.SetColAttr(0, leftColAttr)
        
        # -------------------------
        
        self.tempInsertButton = wx.Button(self, wx.ID_ANY, "Insert Section")
        self.tempDeleteButton = wx.Button(self, wx.ID_ANY, "Delete Section")
        self.tempShortenButton = wx.Button(self, wx.ID_ANY, "Shorten Section")
        self.tempExpandButton = wx.Button(self, wx.ID_ANY, "Expand Section")
        
        self.tempAddrCtrl = wx.TextCtrl(self, wx.ID_ANY)
        self.tempAddrButton = wx.Button(self, wx.ID_ANY, "Set Address")
        
        self.parseButton = wx.Button(self, wx.ID_ANY, "Parse Step")
        
        self.tempLoadButton = wx.Button(self, wx.ID_ANY, "Load")
        self.tempSaveButton = wx.Button(self, wx.ID_ANY, "Save")
        
        sbs1.Add(self.sectionGrid, 0, wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempInsertButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempDeleteButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempShortenButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempExpandButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempLoadButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempSaveButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempAddrCtrl, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.tempAddrButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        sbs1.Add(self.parseButton, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)        
        
        # -----------------------
        
        self.sectionContentCtrl = rompanel.HexListBox(self, wx.ID_ANY, size=(440,200))
    
        sbs2.Add(self.sectionContentCtrl, 0, wx.EXPAND | wx.ALL, 5)
        
        # ------------------------
        
        sbs3propSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizeText = wx.StaticText(self, wx.ID_ANY, "Data Size")
        self.sizeCtrl = wx.SpinCtrl(self, wx.ID_ANY, min=1, max=8)
        
        sbs3propSizer.Add(sizeText, 0, wx.RIGHT, 3)
        sbs3propSizer.Add(self.sizeCtrl, 0)
        
        sbs3.Add(sbs3propSizer, 0, wx.ALL, 5)
        
        # ------------------------
        
        """self.colorText = wx.StaticText(self, -1, "Color %02i" % self.color)
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
        
        # ------------------------ """
        
        self.descCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(440,200), style=wx.TE_MULTILINE)
        
        sbs4.Add(self.descCtrl, 1, wx.EXPAND | wx.ALL, 10)
        
        # ------------------------
        
        self.sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(sbs1, pos=(1,0), span=(2,1), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs2, pos=(1,1), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs4, pos=(1,2), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs3, pos=(2,1), flag=wx.EXPAND)
        #self.sizer.AddSizer(sbs4, pos=(3,0), span=(1,2), flag=wx.EXPAND)
        #self.sizer.Add(sbs2, pos=(2,0), flag=wx.EXPAND)
        
        self.updateSectionGrid()
        
        """self.changePalette(0)
        self.changeEditColor(0)
        self.updateSymbols()
        
        # ------------------------
        
        wx.EVT_COMBOBOX(self, self.paletteList.GetId(), self.OnSelectPalette)
        #wx.EVT_TEXT(self, self.paletteList.GetId(), self.OnRenamePalette)
        
        wx.EVT_SLIDER(self, -1, self.OnChangeColor)
        wx.EVT_SPINCTRL(self, -1, self.OnChangeColor)
        
        wx.EVT_BUTTON(self, self.copyButton.GetId(), self.OnCopyColor)
        wx.EVT_BUTTON(self, self.pasteButton.GetId(), self.OnPasteColor)
        
        #wx.EVT_LISTBOX(self, self.bankList.GetId(), self.OnSelectBank)
        #wx.EVT_LISTBOX(self, self.lineList.GetId(), self.OnSelectLine)
        #wx.EVT_TEXT(self, self.editBox.GetId(), self.OnEditText)"""
        
        wx.EVT_BUTTON(self, self.tempInsertButton.GetId(), self.OnTempInsert)
        wx.EVT_BUTTON(self, self.tempDeleteButton.GetId(), self.OnTempDelete)
        wx.EVT_BUTTON(self, self.tempShortenButton.GetId(), self.OnTempShorten)
        wx.EVT_BUTTON(self, self.tempExpandButton.GetId(), self.OnTempExpand)
        wx.EVT_BUTTON(self, self.parseButton.GetId(), self.OnStep)
        wx.EVT_BUTTON(self, self.tempAddrButton.GetId(), self.OnTempAddrSet)
        wx.EVT_BUTTON(self, self.tempLoadButton.GetId(), self.OnTempLoad)
        wx.EVT_BUTTON(self, self.tempSaveButton.GetId(), self.OnTempSave)
    
        wx.EVT_SPINCTRL(self, self.sizeCtrl.GetId(), self.OnChangeDataSize)
        
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.OnCellChange) 
        self.Bind(grid.EVT_GRID_CMD_CELL_CHANGE, self.OnCellEdit) 
        
        self.TempLoad()
        
    def OnCellChange(self, evt):
        
        self.curSectionIdx = evt.GetRow()
        self.updateSectionContents()
        
        evt.Skip()
    
    def OnCellEdit(self, evt):
        
        col = evt.GetCol()
        row = evt.GetRow()
        obj = evt.GetEventObject()
        sect = self.rom.currentLayout.sections[row]
        val = obj.GetCellValue(row, col)
        
        if col == 0:        # changed section name
            sect.name = val
        elif col == 1:
            sect.type = val
        elif col == 2:
            bank,addr = int(val[:2], 16) * 0x10000, int(val[3:], 16)
            sect.start = bank+addr
            self.rom.currentLayout.sortSections()
        elif col == 3:
            bank,addr = int(val[:2], 16) * 0x10000, int(val[3:], 16)
            sect.end = bank+addr
            self.rom.currentLayout.sortSections()
        
        self.updateSectionGrid()
        
        evt.Skip()
        
    def OnStep(self, evt):
        
        self.rom.parseGen.next()
        
        self.updateSectionGrid()
    
    def OnTempInsert(self, evt):
        self.rom.currentLayout.addNewSection(None, None)
        self.updateSectionGrid()
    
    def OnTempDelete(self, evt):
        self.rom.currentLayout.sections.pop(self.curSectionIdx)
        self.updateSectionGrid()
    
    def OnTempExpand(self, evt):
        sect = self.rom.currentLayout.sections[self.curSectionIdx]
        after = self.rom.currentLayout.sections[self.curSectionIdx+1]
        size = sect.params.get("size", 1)
        sect.end += size
        after.start += size
        self.updateSectionGrid()
        self.sectionContentCtrl.ScrollLines(self.sectionContentCtrl.Count)

    def OnTempShorten(self, evt):
        sect = self.rom.currentLayout.sections[self.curSectionIdx]
        after = self.rom.currentLayout.sections[self.curSectionIdx+1]
        size = sect.params.get("size", 1)
        sect.end -= size
        after.start -= size
        self.updateSectionGrid()
        self.sectionContentCtrl.ScrollLines(self.sectionContentCtrl.Count)
        
    def OnTempAddrSet(self, evt):
        self.rom.currentLayout.addrOff = int(self.tempAddrCtrl.GetValue(), 16)
        self.OnStep(evt)
    
    def OnTempLoad(self, evt):
    
        self.TempLoad()
    
    def TempLoad(self):
        
        self.rom.currentLayout.clearContent()
        
        # NONPICKLING 
        
        """
        
        f = file("layout.dat", "r")
        fileStr = f.readlines()
        f.close()

        self.rom.currentLayout.sections = []
        
        for l in fileStr:
            name, typ, start, end = l.split(", ")
            self.rom.currentLayout.addNewSection(name, typ, int(start), int(end))
        
        """
        
        # --------------------
        
        # PICKLING
        
        f = file("layout_pickled.dat", "rb")
        self.rom.currentLayout = pickle.load(f)
        self.rom.currentLayout.updatePickledObj(self.rom)
        
        self.updateSectionGrid()

        if hasattr(self.rom.currentLayout, "lastSelected"):
            self.curSectionIdx = self.rom.currentLayout.lastSelected
            self.sectionGrid.SetGridCursor(self.curSectionIdx, 0)
            self.sectionGrid.MakeCellVisible(self.curSectionIdx, 0)
        
    def OnTempSave(self, evt):
        
        self.rom.currentLayout.clearContent()
        self.rom.currentLayout.lastSelected = self.curSectionIdx
        
        # NONPICKLING
        
        fileStr = "\n".join(["%s, %s, %i, %i" % (s.name, s.type, s.start, s.end) for s in self.rom.currentLayout.sections])
        
        #dlg = wx.FileDialog(self, "Save Current ROM Layout", "", "", "*.*", wx.SAVE)
        
        #if dlg.ShowModal() == wx.ID_OK:
            
        #f = file(dlg.GetPath(), "w")
        
        f = file("layout.dat", "w")
        f.writelines(fileStr)
        f.close()
        
        # -------------------------------
        
        # PICKLING
        
        f = file("layout_pickled_temp.dat", "wb")
        pickle.dump(self.rom.currentLayout, f, -1)
        #pickle.dump(self.curSection.content[0], f, -1)
        f.close()
        
        try:
            os.remove("layout_pickled.dat")
        except:
            pass
            
        os.rename("layout_pickled_temp.dat", "layout_pickled.dat")
    
    def OnChangeDataSize(self, evt):
        
        self.curSection.setParam("size", self.sizeCtrl.GetValue())
        self.updateSectionGrid()
        
    def updateSectionGrid(self):
        
        rows, cols = self.sectionGrid.GetNumberRows(), self.sectionGrid.GetNumberCols()

        for i,s in enumerate(self.rom.currentLayout.sections):
            
            if i >= rows:
                self.sectionGrid.AppendRows()
            self.sectionGrid.SetCellValue(i, 0, s.name)
            self.sectionGrid.SetCellValue(i, 1, s.type)
            self.sectionGrid.SetCellValue(i, 2, "%02x:%04x" % (s.start/0x10000, s.start%0x10000))
            self.sectionGrid.SetCellValue(i, 3, "%02x:%04x" % (s.end/0x10000, s.end%0x10000))
            
            self.Refresh()
        
        if rows > len(self.rom.currentLayout.sections):
            self.sectionGrid.DeleteRows(len(self.rom.currentLayout.sections), rows - len(self.rom.currentLayout.sections))
            
        self.sectionGrid.Layout()
        
        self.updateSectionContents()
        
        #self.sectionList.Clear()
        #for s in self.rom.currentLayout.sections:
        #    self.sectionList.Append(s.name)
    
    def updateSectionContents(self):
        
        text = "\n".join(self.curSection.getContentRepr(self.rom))
        
        self.sectionContentCtrl.SetContents(text)
        
        self.sizeCtrl.SetValue(self.curSection.params.get("size", 1))
        
        self.descCtrl.Clear()
        descCtrlText = ""
        
        """if self.curSection.type == "Code":
            for i in self.curSection.content:
                if i.params.has_key("dest") and i.params["dest"].isAddr:
                    print `i.params["dest"].val()`
                    sect = self.rom.currentLayout.getContainingSection(i.params["dest"].val())
                    descCtrlText += `i` + " points to %s + %i\n" % (sect.name, i.params["dest"].val() - sect.start)"""
        
        self.descCtrl.SetValue(descCtrlText)
        
    curSection = property(lambda self: self.rom.currentLayout.sections[self.curSectionIdx])
        