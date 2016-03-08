import wx, rompanel

h2i = lambda i: int(i, 16)

carry = 0
                
class DialoguePanel(rompanel.ROMPanel):
    
    frameTitle = "Dialogue/Text Editor"
    
    def init(self):
        
        self.curBankIdx = 0
        self.curLineIdx = 0
        
        self.broken = False
        
        #inst = wx.StaticText(self, -1, "Edit the text used by cutscenes, NPCs, and map/battle events.\n(Note: The lines are loaded when you click on a bank, so it may take a few seconds to populate the lines box.)")
        #inst.Wrap(inst.GetClientSize()[0])
        
        sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Lines"), wx.HORIZONTAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Edit"), wx.VERTICAL)
        
        # -----------------------
        
        """self.bankList = wx.ListBox(self, wx.ID_ANY, size=(120,300))
        self.bankList.AppendItems([b.name for b in self.rom.data["dialogue"]])
        
        self.addHelpText(self.bankList, 
            "Text Bank List", 
            "List of text banks used by the dialogue font.  Each of these banks contains 64 lines of text from the game.  Click on a bank to populate the list on the right.")"""
        
        self.lineList = wx.ListBox(self, wx.ID_ANY, size=(350,300))
        self.addHelpText(self.lineList, 
            "Line List", 
            "List of lines in the currently selected bank.  Click on a line to edit it in the editbox below.")
        
        #sbs1.Add(self.bankList, 0, wx.EXPAND | wx.ALL, 10)
        sbs1.Add(self.lineList, 0, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------
        
        self.editBox = wx.TextCtrl(self, wx.ID_ANY, size=(470,60), style=wx.TE_MULTILINE)
        self.editBox.SetFont(self.parent.editFont)
        self.addHelpText(self.editBox,
            "Line Edit Box",
            "Edit the line here. Special Codes:\n" + 
            "{NAME/#/LEADER/SPELL/ITEM/CLASS} = Insert pre-loaded data, " + 
            "{NAME:#} = Insert force member name #, " +
            "{N} = Newline, "+
            "{CLEAR} = Clear textbox, " +
            "{W1/W2} = Wait for user input, " +
            "{D1/D2/D3} = Delay for a short time")
        
        self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(470,42), style=wx.TE_MULTILINE)
        self.addHelpText(self.symbolsBox,
            "Code Box",
            "This box contains the hex value for the data you're currently editing. When you save the ROM, this data is inserted.")
            
        sbs2.Add(self.editBox, 0, wx.EXPAND | wx.ALL, 10)
        sbs2.Add(self.symbolsBox, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)
        
        # ------------------------
        
        #self.sizer.Add(inst, pos=(0,0), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(sbs1, pos=(0,0), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs2, pos=(1,0), flag=wx.EXPAND)
        
        self.editBox.Enable(False)
        
        # ------------------------
        
        #wx.EVT_LISTBOX(self, self.bankList.GetId(), self.OnSelectBank)
        wx.EVT_LISTBOX(self, self.lineList.GetId(), self.OnSelectLine)
        wx.EVT_TEXT(self, self.editBox.GetId(), self.OnEditText)
        
    def OnSelectBank(self, evt):
        
        self.changeBank(evt.GetSelection())
    
    def changeBank(self, num):
        
        self.curBankIdx = bank = num
        
        if not self.curBank.loaded:
            self.rom.getDialogue(bank)
        
        self.lineList.Clear()
        
        for i,line in enumerate(self.curBank.lines):
            self.lineList.Append("%03x: %s" % (i + bank*64, line.text))
        
        self.editBox.Enable(False)
        
        #self.lineList.AppendItems(zip(*self.rom.data["dialogue"][bank])[0])
        #print `bankAddr`
        
    def OnSelectLine(self, evt):
        
        self.curLineIdx = evt.GetSelection()
        self.changeLine(self.curLineIdx)
        
        #print line
        #print data
        
    def OnEditText(self, evt):
        
        text = evt.GetString()
        self.lineList.SetString(self.curLineIdx, "%03x: %s" % (self.curLineIdx + self.curBankIdx*64, text))
        
        line = self.curLine
        line.text = text
        self.broken = False
        
        symbols = line.hexlify(self.rom, check=True)
        
        #self.broken = symbols.startswith("IMPOSSIBLE STRING")
        self.broken = line.broken
        
        if text != line.originalText:
            self.curBank.modified = True
            self.modify()
        
        if self.broken:
            self.editBox.SetBackgroundColour("#FFB0B0")
            #self.symbolsBox.SetBackgroundColour("#FFB0B0")
        else:
            self.editBox.SetBackgroundColour("#FFFFFF")
            #self.symbolsBox.SetBackgroundColour("#FFFFFF")
        
        self.editBox.Refresh()
        self.symbolsBox.SetValue(symbols)
    
    def changeLine(self, num):

        line = self.curLine
        self.editBox.SetValue(line.text)
        
        symbols = line.hexlify(self.rom)
        self.symbolsBox.SetValue(symbols)
        
        if not self.editBox.IsEnabled():
            self.editBox.Enable(True)
        
        self.updateModifiedIndicator(self.getCurrentData().modified)
        
        #print line.symbols
        #print line.raw_bytes
        #print line.originalText
        
    def getCurrentData(self):
        if self.curBank.loaded:
            return self.curLine
        return None
    
    changeSelection = changeBank
    
    curBank = property(lambda self: self.rom.data["dialogue"][self.curBankIdx])
    curLine = property(lambda self: self.curBank.lines[self.curLineIdx])