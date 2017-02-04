import sys

sys.path.append("lib")

# uhhh..... this is only here because it fixes that Common Controls bug in wxpython 2.8.  what the hell.
# from PIL import Image

import wxversion
wxversion.select('2.8')

import wx, os, traceback, pickle
import wx.aui
import wx.lib.dialogs
import wx.lib.filebrowsebutton as fbb

app = wx.App()
icon = wx.Icon("caravan.ico", wx.BITMAP_TYPE_ICO)

import asm, settings
import rom, panellist, changelog, window, consts, layouttree, util, temp, layout
from panels import rompanel


def error(etype, value, tb):
    global mw

    l = traceback.format_exception(etype, value, tb)
    mw.showError("".join(l))


def pathjoin(*args):
    s = os.path.join(*args)
    if s[2] != "\\":
        s = s[:2] + "\\" + s[2:]
    return s


#sys.excepthook = error

ID = {}
ID_NEXT = 0

redo = []
undo = []


def addID(id):
    global ID, ID_NEXT
    ID[id] = ID_NEXT
    ID_NEXT += 1
    return ID[id]


# ORDER
# - event functions
# - menu operations, in order of menus
# - utility
# - misc

class MainFrame(window.CaravanParentFrame):
    def __init__(self, parent, id, app):

        window.CaravanParentFrame.__init__(self, parent, id)

        # s = self.GetClientSize()
        # self.WarpPointer(s[0]/2, s[1])

        self.app = app

        self.rom = None
        self.settings = settings.init("caravan.cfg")

        self.filename = ""
        self.dirname = ""
        self.datafilename = ""
        self.datadirname = ""

        self.initialPanel = "romviewer"  # for testing purposes only

        self.dataFile = None

        self.curPanelID = None

        self.panels = {}
        self.frames = []

        self.stored = {}

        self.pendingCancel = False
        self.isErring = False

        self.headerFont = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Verdana")
        self.editFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False,
                                "Courier New")
        self.subFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Verdana")

        self.tempUndoStack = {}
        self.tempRedoStack = {}

        self.SetMinSize((600, 450))

        # print "\n".join(dir(wx.RadioButton))

        # print "\n".join(filter(lambda s: s.startswith("EVT"), dir(wx)))

        # --------------------------

        menuBar = wx.MenuBar()

        # ----

        self.newFileMenu = newFileMenu = wx.Menu()

        newFileMenu.Append(addID("NEW_PROJECT"), "&New Project...\tCtrl-N", " Create a new project.")
        newFileMenu.Append(addID("OPEN_PROJECT"), "&Open Project...\tCtrl-O", " Open a project.")
        newFileMenu.Append(addID("SAVE_PROJECT"), "&Save Project\tCtrl-S", " Save the currently loaded project.")
        newFileMenu.Append(addID("SAVE_PROJECT_AS"), "&Save Project As...\tCtrl-Shift-S",
                           " Save the currently loaded project under a different filename.")
        newFileMenu.AppendSeparator()
        newFileMenu.Append(addID("IMPORT_GAME"), "&Import Game Settings...", " Open a project.")

        newFileMenu.AppendSeparator()

        # fileMenu.Append(addID("OPENDATA"), "&Open External Data...\tCtrl-1"," Open an external data file")
        # fileMenu.Append(addID("SAVEDATA"), "&Save External Data\tCtrl-2"," Save the currently loaded external data file")
        # fileMenu.Append(addID("SAVEDATAAS"), "&Save External Data As...\tCtrl-3"," Save the currently loaded external data file under a different filename")
        # fileMenu.AppendSeparator()

        # fileMenu.Append(addID("CLOSE"), "&Close ROM\tCtrl-X", " Close the currently loaded Shining Force II ROM")
        # fileMenu.Append(addID("CLOSEDATA"), "&Close External Data\tCtrl-0", " Close the currently loaded external data file")
        # fileMenu.AppendSeparator()

        # fileMenu.Append(addID("LAST"), "Open Previous ROM/Data\tCtrl-Shift-O", " for testing only, should eventually be replaced with a Recent menu")
        # fileMenu.AppendSeparator()

        # fileMenu.Append(addID("EXIT"), "E&xit\tCtrl-Q", " Exit The Caravan")"""

        newFileMenu.Enable(ID["SAVE_PROJECT"], False)
        newFileMenu.Enable(ID["SAVE_PROJECT_AS"], False)
        # fileMenu.Enable(ID["CLOSE"], False)

        # fileMenu.Enable(ID["OPENDATA"], False)
        # fileMenu.Enable(ID["SAVEDATA"], False)
        # fileMenu.Enable(ID["SAVEDATAAS"], False)
        # fileMenu.Enable(ID["CLOSEDATA"], False)


        # ----

        self.fileMenu = fileMenu = wx.Menu()

        fileMenu.Append(addID("OPEN"), "&Open ROM...\tCtrl-O", " Open a Shining Force 2 ROM (.BIN only)")
        fileMenu.Append(addID("SAVE"), "&Save ROM\tCtrl-S", " Save the currently loaded Shining Force II ROM")
        fileMenu.Append(addID("SAVEAS"), "&Save ROM As...\tCtrl-Shift-S",
                        " Save the currently loaded Shining Force II ROM under a different filename (.BIN only)")
        fileMenu.AppendSeparator()

        # fileMenu.Append(addID("OPENDATA"), "&Open External Data...\tCtrl-1"," Open an external data file")
        # fileMenu.Append(addID("SAVEDATA"), "&Save External Data\tCtrl-2"," Save the currently loaded external data file")
        # fileMenu.Append(addID("SAVEDATAAS"), "&Save External Data As...\tCtrl-3"," Save the currently loaded external data file under a different filename")
        # fileMenu.AppendSeparator()

        fileMenu.Append(addID("CLOSE"), "&Close ROM\tCtrl-X", " Close the currently loaded Shining Force II ROM")
        # fileMenu.Append(addID("CLOSEDATA"), "&Close External Data\tCtrl-0", " Close the currently loaded external data file")
        fileMenu.AppendSeparator()

        # FUTURE: maybe make it a list of last opened, and with projects not roms.
        """fileMenu.Append(addID("OPEN_LAST"), "Open Previous ROM/Data\tCtrl-Shift-O", " for testing only, should eventually be replaced with a Recent menu")
        fileMenu.AppendSeparator()"""
        # /FUTURE

        fileMenu.Append(addID("EXIT"), "E&xit\tCtrl-Q", " Exit The Caravan")
        # DEBUG: fileMenu.Append(addID("EEXIT"), "Emergency Exit", " Exit The Caravan instantly")

        fileMenu.Enable(ID["SAVE"], False)
        fileMenu.Enable(ID["SAVEAS"], False)
        fileMenu.Enable(ID["CLOSE"], False)

        # fileMenu.Enable(ID["OPENDATA"], False)
        # fileMenu.Enable(ID["SAVEDATA"], False)
        # fileMenu.Enable(ID["SAVEDATAAS"], False)
        # fileMenu.Enable(ID["CLOSEDATA"], False)

        # ----

        self.editMenu = editMenu = wx.Menu()

        editMenu.Append(addID("UNDO"), "&Undo\tCtrl-Z", " Undo previous action.")
        editMenu.Append(addID("REDO"), "&Redo\tCtrl-Y", " Redo next action.")

        # ----

        self.toolsMenu = toolsMenu = wx.Menu()

        # toolsMenu.Enable(ID["PREVIEW

        # ----

        self.miscMenu = miscMenu = wx.Menu()

        miscMenu.Append(addID("INSERT"), "Insert Bytes (Test Shift)\tF1", "")
        miscMenu.Append(addID("ANALYZE"), "Analyze 68k Command\tF2", "")
        miscMenu.AppendSeparator()
        miscMenu.Append(addID("STUFF"), "Do Temp Stuff", "")
        miscMenu.AppendSeparator()
        miscMenu.Append(addID("DELCFG"), "Delete Settings", "")
        miscMenu.AppendSeparator()
        miscMenu.Append(addID("EXPORTIMAGE"), "Export Image Test", "")
        miscMenu.Append(addID("EXPORTALL"), "Export All Images Test", "")

        # ----

        self.helpMenu = helpMenu = wx.Menu()

        helpMenu.Append(addID("CHANGELOG"), "Changelog", " View The Caravan's changelog.")

        # ----

        # FUTURE: menuBar.Append(newFileMenu, "&NewFile")
        menuBar.Append(fileMenu, "&File")
        # menuBar.Append(editMenu, "&Edit")
        # menuBar.Append(toolsMenu, "&Tools")
        # DEBUG: menuBar.Append(miscMenu, "&Misc")
        # menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)

        # ---------------------------

        self.initLayoutTree()

        # ---------------------------

        wx.EVT_MENU(self, ID["NEW_PROJECT"], self.OnNewProject)

        wx.EVT_MENU(self, ID["OPEN"], self.OnOpen)
        wx.EVT_MENU(self, ID["SAVE"], self.OnSave)
        wx.EVT_MENU(self, ID["SAVEAS"], self.OnSaveAs)
        wx.EVT_MENU(self, ID["CLOSE"], self.OnClose)

        # FUTURE: wx.EVT_MENU(self, ID["OPEN_LAST"], self.OnOpenLast)

        wx.EVT_MENU(self, ID["EXIT"], self.OnExit)
        # DEBUG: wx.EVT_MENU(self, ID["EEXIT"], self.emergencyExit)
        wx.EVT_CLOSE(self, self.OnExit)

        # ----

        wx.EVT_MENU(self, ID["UNDO"], self.OnUndo)
        wx.EVT_MENU(self, ID["REDO"], self.OnRedo)

        # ----

        # tools

        # ----

        wx.EVT_MENU(self, ID["INSERT"], self.TempInsert)
        wx.EVT_MENU(self, ID["ANALYZE"], self.TempAnalyze)
        wx.EVT_MENU(self, ID["STUFF"], self.TempStuff)
        wx.EVT_MENU(self, ID["DELCFG"], self.TempDeleteSettings)
        wx.EVT_MENU(self, ID["EXPORTIMAGE"], self.TempExportImage)
        wx.EVT_MENU(self, ID["EXPORTALL"], self.TempExportAll)

        # ----

        wx.EVT_MENU(self, ID["CHANGELOG"], self.OnChangelog)

    # -----------------------------------------------------------------
    # event functions

    def OnOpenLast(self, evt):
        self.OnOpen(evt, True)

    def OnNewProject(self, evt):

        dlg = NewProjectDialog(self)
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            # if 1:

            fn = str(dlg.romCtrl.GetValue())
            paths = fn.split("\\")
            self.dirname = "\\".join(paths[:-1])
            self.filename = paths[-1]

            specfn = None

            # FUTURE: add these back in.
            """if dlg.gameSpecCheck.GetValue():
                
                spec = dlg.gameSpecCtrl.GetString(dlg.gameSpecCtrl.GetSelection())
                specfn = self.settings.games[spec]
                
                # start new project from existing game spec
                self.project = layout.loadProject(specfn)"""
            # /FUTURE

            if 0:
                pass
            else:
                self.project = layout.Project("Untitled Project")

            if self.settings.history["ROMs"].count(fn):
                self.settings.history["ROMs"].remove(fn)
            self.settings.history["ROMs"].insert(0, fn)

            self.initNewProject(fn)

            # while :
            #    pass

    def OnOpen(self, evt, hack=False):

        if self.rom:
            success = self.confirmClose()

        dlg = wx.FileDialog(self, "Open Shining Force 2 ROM (.BIN)", "", "", "*.bin", wx.OPEN)
        datadlg = wx.FileDialog(self, "Open External Data File", "", "", "*.txt;*.dat", wx.OPEN)

        validROM = False
        validDF = False

        # -----------------------------

        while not validROM:

            if dlg.ShowModal() == wx.ID_OK:

                if self.rom:

                    if success == wx.ID_NO:
                        self.closeROM()
                    else:
                        return

                self.filename = dlg.GetFilename()
                self.dirname = dlg.GetDirectory()

                fn = pathjoin(self.dirname, self.filename)
                file = open(pathjoin(self.dirname, self.filename), 'rb')
                file.seek(0x150)
                verify = file.read(15)

                datafile = None

                if verify == "SHINING FORCE 2":

                    validROM = True

                    self.project = layout.Project("Untitled Project")

                    if self.settings.history["ROMs"].count(fn):
                        self.settings.history["ROMs"].remove(fn)
                    self.settings.history["ROMs"].insert(0, fn)

                    if not self.dataFile:

                        decision = None

                        while not validDF and decision != wx.ID_CANCEL:

                            decision = datadlg.ShowModal()

                            if decision == wx.ID_OK:

                                self.datadirname = datadlg.GetDirectory()
                                self.datafilename = datadlg.GetFilename()

                                datafile = open(pathjoin(self.datadirname, self.datafilename), 'r')
                                success, result = self.parseDataFile(datafile)

                                if success:

                                    validDF = True

                                else:

                                    datafile.close()
                                    error = wx.MessageDialog(self,
                                                             "The file you selected is not a valid external data file.",
                                                             self.baseTitle, wx.OK | wx.ICON_ERROR).ShowModal()

                    else:

                        datafile = open(pathjoin(self.datadirname, self.datafilename), 'r')

                    self.dataFile = datafile

                    # self.settings.history["lastFiles"] = [fn, pathjoin(self.datadirname,self.datafilename)]

                    # ------------------------------------
                    # expand ROM to 4mb if not done

                    romSize = os.path.getsize(fn)

                    if romSize == 0x200000:

                        warning = wx.MessageDialog(self,

                                                   "You have opened a 2mb SF2 ROM.\n\n" + \
 \
                                                   "This version of the Caravan, along with all future versions until a theoretical 2.0 release,\n" + \
                                                   "only edits a 4mb expanded SF2 ROM. This expanded ROM can be created from the ROM you opened\n" + \
                                                   "now. If the ROM you chose was previously changed in any way, please note that the expanded\n" + \
                                                   "ROM created might not work properly.\n\n" + \
 \
                                                   "Create the 4mb expanded SF2 ROM now?",

                                                   self.baseTitle, wx.YES | wx.NO | wx.ICON_WARNING).ShowModal()

                        if warning != wx.ID_YES:
                            return

                        warning = wx.MessageDialog(self,

                                                   "Please select a location to save the file.",

                                                   self.baseTitle, wx.OK | wx.ICON_QUESTION).ShowModal()

                        dlg = wx.FileDialog(self, "Save Shining Force 2 ROM (.BIN) As", "", "", "*.bin", wx.SAVE)

                        if dlg.ShowModal() != wx.ID_OK:
                            return

                        fn = dlg.GetFilename()
                        dn = dlg.GetDirectory()
                        path = pathjoin(dn, fn)

                        warning = wx.MessageDialog(self,

                                                   "Now creating the 4mb expanded SF2 ROM.\n\n" + \
 \
                                                   "This will take at least a few seconds.  The program may appear unresponsive during this time.",

                                                   self.baseTitle, wx.OK | wx.ICON_INFORMATION).ShowModal()

                        file.seek(0)
                        self.rom = rom.ROM(file)
                        self.rom.expandROM(path)

                        warning = wx.MessageDialog(self,

                                                   "The 4mb expanded SF2 ROM has been created.\n\n" + \
 \
                                                   "You may now open the ROM you just created for editing.",

                                                   self.baseTitle, wx.OK | wx.ICON_INFORMATION).ShowModal()



                        # finish up and reload or something

                    # ------------------------------------

                    else:

                        self.initNewProject(fn, datafile)

                    # OLD: now taken care of by initNewProject?
                    """self.createMainPanel()
                    
                    dlg = self.createLoadingDialog("Loading ROM...")
                    
                    self.rom.initData()
                    
                    dlg.Destroy()
                    
                    self.mainPanel.Show()
                    self.mainPanel.SetSize(self.GetClientSize())
                    
                    self.SetTitle(self.baseTitle + " - [ " + self.dirname + "\\" + self.filename + " ]")
                    
                    self.newFileMenu.Enable(ID["SAVEAS"], True)
                    self.fileMenu.Enable(ID["CLOSE"], True)
                    
                    self.toolsMenu.Enable(ID["MAPVIEWER"], True)"""
                    # /OLD

                else:

                    file.close()
                    error = wx.MessageDialog(self,
                                             "The file you selected is not a valid Shining Force 2 ROM in .BIN format.",
                                             self.baseTitle, wx.OK | wx.ICON_ERROR).ShowModal()

            else:

                # validROM = True
                break

        dlg.Destroy()

    def OnUndo(self, evt):

        if self.curUndoStack:
            if not self.curRedoStack:
                self.tempRedoStack[self.subPanel] = []
            action = self.curUndoStack.pop()
            self.curRedoStack.append(action)

            obj = self.subPanel.getCurrentSpriteObject()
            obj.raw_pixels = action[0][0]
            if len(action[0]) > 1:
                obj.raw_pixels2 = action[0][1]
                obj.rearrangePixels(obj.raw_pixels + obj.raw_pixels2)
                self.subPanel.editPanel.refreshSprite([obj.pixels, obj.pixels2][self.subPanel.frame])
            else:
                obj.rearrangePixels(obj.raw_pixels, False)
                self.subPanel.editPanel.refreshSprite(obj.pixels)
            self.subPanel.editPanel.Refresh()
        self.updateUndoRedo()

    def OnRedo(self, evt):

        if self.curRedoStack:
            if not self.curUndoStack:
                self.tempUndoStack[self.subPanel] = []
            action = self.curRedoStack.pop()
            self.curUndoStack.append(action)

            obj = self.subPanel.getCurrentSpriteObject()

            obj.raw_pixels = action[1][0]
            if len(action[0]) > 1:
                obj.raw_pixels2 = action[1][1]
                obj.rearrangePixels(obj.raw_pixels + obj.raw_pixels2)
                self.subPanel.editPanel.refreshSprite([obj.pixels, obj.pixels2][self.subPanel.frame])
            else:
                obj.rearrangePixels(obj.raw_pixels, False)
                self.subPanel.editPanel.refreshSprite(obj.pixels)
            self.subPanel.editPanel.Refresh()
        self.updateUndoRedo()

    # ---------------------------------------------------------------
    # menu functions

    # Temp

    def TempStuff(self, evt):

        temp.doTempStuff()

    def TempDeleteSettings(self, evt):

        os.remove("caravan.cfg")
        self.settings = settings.init("caravan.cfg")

    def TempExportImage(self, evt):

        d = self.GetActiveChild().contentPanel.editPanel.bmp

        dlg = wx.FileDialog(self, "Export Image As", "", "", "*.png", wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:

            fn = dlg.GetFilename()
            if not fn.endswith(".png"):
                fn += ".png"
            dn = dlg.GetDirectory()
            path = pathjoin(dn, fn)

            d.SaveFile(path, wx.BITMAP_TYPE_PNG)

    def TempExportAll(self, evt):

        dlg = wx.DirDialog(self, "Export Images To", sys.path[0], wx.DD_DEFAULT_STYLE)
        panel = self.GetActiveChild().contentPanel

        if dlg.ShowModal() == wx.ID_OK:

            path = dlg.GetPath()

            cnt = 0
            iter = panel.iterateData()
            notDone = True

            try:
                while True:
                    idx = iter.next()
                    d = panel.editPanel.bmp
                    d.SaveFile("%s\%s.png" % (path, "_".join([str(i) for i in idx])), wx.BITMAP_TYPE_PNG)
            except StopIteration, e:
                pass

            """fn = dlg.GetFilename()
            if not fn.endswith(".png"):
                fn += ".png"
            dn = dlg.GetDirectory()
            path = pathjoin(dn,fn)
            
            d.SaveFile(path, wx.BITMAP_TYPE_PNG)"""

    def TempInsert(self, evt):

        self.rom.startWriteProcess()

        dlg = wx.TextEntryDialog(self, "Number of bytes (hex):", self.baseTitle)
        dlg.ShowModal()
        num = int(dlg.GetValue(), 16)

        dlg = wx.TextEntryDialog(self, "Insert location (hex):", self.baseTitle)
        dlg.ShowModal()
        addr = int(dlg.GetValue(), 16)

        for n in range(num):
            self.rom.writeBytes(addr, "ff", True)
            if not n % 1000:
                print n

        wx.MessageDialog(self, "Old %x: %s\nNew %x: %s" % (
        addr, self.rom.getBytes(addr, num), addr, self.rom.getPendingBytes(addr, num)), self.baseTitle,
                         style=wx.OK).ShowModal()

        self.modify()

    def TempAnalyze(self, evt):

        dlg = wx.TextEntryDialog(self, "Number of commands:", self.baseTitle)
        dlg.ShowModal()
        num = int(dlg.GetValue())

        dlg = wx.TextEntryDialog(self, "Analyze location:", self.baseTitle)
        dlg.ShowModal()
        addr = int(dlg.GetValue(), 16)

        nb = 10
        for n in range(num):
            bstr = util.bin(int(self.rom.getBytes(addr, nb), 16), nb * 8)
            inst = asm.main.getInstruction(bstr)
            print "%s: %s, %s, %i" % (hex(addr), inst.type.xmlElements["repr"], inst.type.opcode, inst.length)
            addr += inst.length

            # wx.MessageDialog(self, "Old %x: %s\nNew %x: %s" % (addr, self.rom.getBytes(addr, num), addr, self.rom.getPendingBytes(addr, num)), self.baseTitle, style=wx.OK).ShowModal()

            # self.modify()

    # ----------------------------
    # utility

    def updateUndoRedo(self):

        us, rs = self.tempUndoStack, self.tempRedoStack

        undoEnable = len(self.curUndoStack)
        redoEnable = len(self.curRedoStack)

        self.editMenu.Enable(ID["UNDO"], undoEnable)
        self.editMenu.Enable(ID["REDO"], redoEnable)

    def showError(self, text):

        if not self.isErring:

            self.isErring = True

            dlg = wx.MessageDialog(self, text + "\nCopy the error to the clipboard?", self.baseTitle,
                                   wx.YES_NO | wx.ICON_ERROR)
            error = dlg.ShowModal()

            self.isErring = False

            if error == wx.ID_YES:

                res = wx.TheClipboard.Open()

                if res:
                    wx.TheClipboard.SetData(wx.TextDataObject(text))
                    wx.TheClipboard.Close()
                else:
                    wx.MessageDialog(self, "Copy failed.", self.baseTitle + " -- Error",
                                     wx.OK | wx.ICON_ERROR).ShowModal()

    # -------------------------------
    # misc

    curUndoStack = property(lambda self: self.tempUndoStack.get(self.subPanel, []))
    curRedoStack = property(lambda self: self.tempRedoStack.get(self.subPanel, []))

    # OLD
    """def OnOpen(self, evt, hack=False):
        
        if self.rom:
            
            success = self.confirmClose()
                
        dlg = wx.FileDialog(self, "Open Shining Force 2 ROM (.BIN)", "", "", "*.bin", wx.OPEN)
        datadlg = wx.FileDialog(self, "Open External Data File", "", "", "*.txt;*.dat", wx.OPEN)
        
        validROM = False
        validDF = False
        
        # -----------------------------
        # HACKS FOR LAST FILES OPENED
        
        if hack:
            
            try:
                
                lastFile = open("lastfiles.dat", 'rb')
                lastFileLines = lastFile.readlines()
                
                found = False
                
                while not found:
                    
                    print "Trying..."
                    
                    lines = [l.strip() for l in lastFileLines[:4]]
                    lastFileLines = lastFileLines[5:]
                    
                    if len(lines) == 4:
                        
                        self.dirname, self.filename, self.datadirname, self.datafilename = lines
                        
                        self.dataFile = open(pathjoin(self.datadirname,self.datafilename), 'r')
                        success, result = self.parseDataFile(self.dataFile)
                        
                        try:
                            file = open(pathjoin(self.dirname,self.filename), 'rb')
                            file.seek(0x150)
                            verify = file.read(15)
                        except:
                            continue
                        
                        if verify == "SHINING FORCE 2":
                            
                            validROM = True
                            found = True
                            self.rom = rom.ROM(file)
                                
                        if success:
                            
                            self.rom.dataFile = self.dataFile
                            self.rom.names = result 
                            validDF = True                
                            
                        self.createMainPanel()
                        
                        dlg = self.createLoadingDialog("Loading ROM...")
                        
                        self.rom.initData()
                        
                        dlg.Destroy()
                        
                        #self.mainPanel.Show()
                        #self.mainPanel.SetSize(self.GetClientSize())
                        
                        self.SetTitle(self.baseTitle + " - [ " + self.dirname + "\\" + self.filename + " ]")
                        
                        self.newFileMenu.Enable(ID["SAVEAS"], True)
                        self.fileMenu.Enable(ID["CLOSE"], True)
                        
                        self.toolsMenu.Enable(ID["MAPVIEWER"], True)

                        #if self.initialPanel:
                        #    self.switchPanels(self.tree.nodes[self.initialPanel])
                            
                    lastFile.close()
            
            except IOError, e:
                pass
            
        # -----------------------------
        
        while not validROM:
            
            if dlg.ShowModal() == wx.ID_OK:
                
                if self.rom:
                    
                    if success == wx.ID_NO:
                        self.closeROM()
                    else:
                        return
                
                self.filename=dlg.GetFilename()
                self.dirname=dlg.GetDirectory()
                    
                file = open(pathjoin(self.dirname,self.filename), 'rb')
                file.seek(0x150)
                verify = file.read(15)
                
                if verify == "SHINING FORCE 2":
                    
                    validROM = True
                    self.rom = rom.ROM(file)
                    
                    if not self.dataFile:
                        
                        decision = None
                        
                        while not validDF and decision != wx.ID_CANCEL:
                            
                            decision = datadlg.ShowModal()
                            
                            if decision == wx.ID_OK:
                                
                                self.datadirname = datadlg.GetDirectory()
                                self.datafilename = datadlg.GetFilename()
                                
                                self.dataFile = open(pathjoin(self.datadirname,self.datafilename), 'r')
                                success, result = self.parseDataFile(self.dataFile)
                                
                                if success:
                                    
                                    self.rom.dataFile = self.dataFile
                                    self.rom.names = result
                                    
                                    validDF = True
                                    
                                else:
                                    
                                    self.dataFile.close()
                                    error = wx.MessageDialog(self, "The file you selected is not a valid external data file.", self.baseTitle, wx.OK | wx.ICON_ERROR).ShowModal()
                    
                    else:
                        
                        self.dataFile = open(pathjoin(self.datadirname,self.datafilename), 'r')
                        self.rom.dataFile = self.dataFile
                        self.rom.names = self.parseDataFile(self.dataFile)[1]
                        
                    self.createMainPanel()
                    
                    dlg = self.createLoadingDialog("Loading ROM...")
                    
                    self.rom.initData()
                    
                    dlg.Destroy()
                    
                    self.mainPanel.Show()
                    self.mainPanel.SetSize(self.GetClientSize())
                    
                    self.SetTitle(self.baseTitle + " - [ " + self.dirname + "\\" + self.filename + " ]")
                    
                    self.newFileMenu.Enable(ID["SAVEAS"], True)
                    self.fileMenu.Enable(ID["CLOSE"], True)
                    
                    self.toolsMenu.Enable(ID["MAPVIEWER"], True)
                    
                else:
                    
                    file.close()
                    error = wx.MessageDialog(self, "The file you selected is not a valid Shining Force 2 ROM in .BIN format.", self.baseTitle, wx.OK | wx.ICON_ERROR).ShowModal()
                
            else:
                
                validROM = True
            
        dlg.Destroy()"""

    def OnSave(self, evt):
        self.saveFile()

    def OnSaveAs(self, evt):

        dlg = wx.FileDialog(self, "Save Shining Force 2 ROM (.BIN) As", "", self.filename, "*.bin", wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:

            fn = dlg.GetFilename()
            dn = dlg.GetDirectory()
            path = pathjoin(dn, fn)

            savingSucceeded = self.saveFile(path)

            if savingSucceeded:
                self.filename = fn
                self.dirname = dn

                self.SetTitle(self.baseTitle + " - [ " + self.dirname + "\\" + self.filename + " ]")

                self.rom.file.close()
                self.rom.file = open(pathjoin(self.dirname, self.filename), 'rb')

    def OnClose(self, evt):

        success = self.confirmClose()

        if success == wx.ID_NO:

            if self.rom.dataFile:

                dlg = wx.MessageDialog(self, "Close external data file '%s' as well?" % pathjoin(self.datadirname,
                                                                                                 self.datafilename),
                                       self.baseTitle, wx.YES | wx.NO | wx.CANCEL | wx.ICON_QUESTION)
                success = dlg.ShowModal()

                if success == wx.ID_YES:
                    self.dataFile.close()
                    self.dataFile = None
                    self.datadirname = ""
                    self.datafilename = ""
                    success = wx.ID_NO

            if success == wx.ID_NO:
                self.closeROM()

                self.fileMenu.Enable(ID["SAVE"], False)
                self.fileMenu.Enable(ID["SAVEAS"], False)

    def OnExit(self, evt):

        success = self.confirmClose()

        if success == wx.ID_NO:

            if self.rom:
                self.closeROM()
            self.settings.save()
            self.app.Exit()

    def OnChangelog(self, evt):

        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, changelog.changeLog, self.baseTitle + " - Changelog")
        dlg.SetSize((400, 300))
        dlg.ShowModal()

    # --------------------

    def initNewProject(self, romfn, datafile=None):

        # new project code goes here

        self.loadROM(romfn, datafile)

        # self.modifiedPanel = rompanel.ColorPanel(self, -1, "#00FF00", (15,15), enable=False)
        self.layoutTree.init()

        self.updateTitle()

        # TEMP
        # frm = SectionFrame(self, -1, "test")

    def loadROM(self, romfn, datafile=None):

        f = open(romfn, "rb")
        self.rom = rom.ROM(f)

        dlg = self.createLoadingDialog("Loading ROM...")

        if datafile:
            self.dataFile = datafile
            self.rom.dataFile = datafile
            self.rom.names = self.parseDataFile(datafile)[1]

        self.rom.initData()

        dlg.Destroy()

        # self.mainPanel.Show()
        # self.mainPanel.SetSize(self.GetClientSize())

        # self.SetTitle(self.baseTitle + " - [ " + romfn + " ]")

        self.newFileMenu.Enable(ID["SAVE_PROJECT_AS"], True)
        self.fileMenu.Enable(ID["CLOSE"], True)

        # OLD self.toolsMenu.Enable(ID["MAPVIEWER"], True)

        # if self.initialPanel:
        #    self.switchPanels(self.tree.nodes[self.initialPanel])

    def initLayoutTree(self):

        # Create AUI stuff here.
        self.aui = aui = wx.aui.AuiManager(self)

        self.layoutTree = tree = layouttree.LayoutTree(self, -1)
        pane = aui.AddPane(tree,
                           wx.aui.AuiPaneInfo().Caption('Layout Tree').CloseButton(False).MinSize((130, -1)).Floatable(
                               False))

        aui.Update()

    def saveFile(self, path=""):

        gen = self.rom.writeAllData()
        texts, pieces = gen.next()

        # ----

        """warning = wx.MessageDialog(self, "WARNING:\n\nSaving changes to the ROM is most likely to corrupt another part of the ROM, especially when talking about graphical data. The reason for this is that most graphics in the game are compressed, and altering them in a significant way will change the length of the compressed data. If this new length is longer, it will overwrite data after it. This will be fixed later.\n\nIn other words, I HIGHLY RECOMMEND MAKING BACKUPS OF YOUR ROM BEFORE SAVING.\n\nContinue saving anyway?", self.baseTitle, wx.YES | wx.NO | wx.ICON_WARNING).ShowModal()
        
        if warning == wx.ID_NO:
            return"""

        # ----

        dlg = wx.Dialog(self, wx.ID_ANY, "Saving...", size=(350, 280))
        # dlg.SetMinSize((300,400))
        dlg.SetIcon(icon)
        dlg.CenterOnScreen()

        dlgSizer = wx.BoxSizer(wx.VERTICAL)
        dlgMainSizer = wx.BoxSizer(wx.VERTICAL)
        dlgText1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        dlgText2Sizer = wx.BoxSizer(wx.HORIZONTAL)

        dlgSubSavingText = wx.StaticText(dlg, -1, "Saving...")
        dlgSubSavingText.SetFont(self.subFont)
        dlgSubPercentText = wx.StaticText(dlg, -1, "0%", style=wx.ALIGN_RIGHT)
        dlgSubPercentText.SetFont(self.headerFont)

        dlgText1Sizer.Add(dlgSubSavingText, 1, wx.ALIGN_BOTTOM)
        dlgText1Sizer.Add(dlgSubPercentText, 0, wx.EXPAND)

        dlgSubGauge = wx.Gauge(dlg, wx.ID_ANY)

        dlgActionText = wx.StaticText(dlg, -1, "", style=wx.ALIGN_CENTER)
        dlgActionText.SetFont(self.subFont)

        dlgSavingText = wx.StaticText(dlg, -1, "")
        dlgSavingText.SetFont(self.subFont)
        dlgPercentText = wx.StaticText(dlg, -1, "0%", style=wx.ALIGN_RIGHT)
        dlgPercentText.SetFont(self.headerFont)

        dlgText2Sizer.Add(dlgSavingText, 1, wx.ALIGN_BOTTOM)
        dlgText2Sizer.Add(dlgPercentText, 0, wx.EXPAND)

        dlgGauge = wx.Gauge(dlg, wx.ID_ANY)

        dlgCancelButton = wx.Button(dlg, wx.ID_ANY, "Cancel", size=(80, 30))
        dlgCancelButton.SetFont(self.subFont)
        dlgCancelButton.dlg = dlg

        wx.EVT_BUTTON(dlg, dlgCancelButton.GetId(), self.cancelSaving)

        dlgMainSizer.AddSizer(dlgText2Sizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        dlgMainSizer.Add(dlgGauge, 0, wx.EXPAND | wx.BOTTOM, 15)
        dlgMainSizer.AddSizer(dlgText1Sizer, 0, wx.EXPAND | wx.BOTTOM, 5)
        dlgMainSizer.Add(dlgSubGauge, 0, wx.EXPAND | wx.BOTTOM, 10)
        dlgMainSizer.Add(dlgActionText, 0, wx.EXPAND | wx.BOTTOM, 30)
        dlgMainSizer.Add(dlgCancelButton, 0, wx.ALIGN_CENTER)

        dlgSizer.AddSizer(dlgMainSizer, 1, wx.EXPAND | wx.ALL, 10)

        dlg.SetSizer(dlgSizer)

        # ----

        dlgSubSavingText.SetLabel("Saving %s..." % texts[0])
        dlgSavingText.SetLabel("Section %i of %i..." % (1, len(pieces)))

        dlg.MakeModal()
        dlg.EnableCloseButton(False)

        dlg.Layout()
        dlg.Show()
        dlg.Update()

        sectionsToUpdate = filter(lambda a: a > 0, pieces)

        result = gen.next()

        if len(sectionsToUpdate) == 0:
            percentPerPiece = 100.0
        else:
            percentPerPiece = 100.0 / len(sectionsToUpdate)

        succeeded = True

        allPieces = 0

        for cur in range(len(pieces)):

            curPiece = 0
            pieceProgress = 0

            dlgSubSavingText.SetLabel("Saving %s..." % texts[cur])
            dlgSavingText.SetLabel("Section %i of %i..." % (cur + 1, len(pieces)))

            dlg.Layout()
            dlg.Show()
            dlg.Update()

            if pieces[cur]:

                percentPerEntry = 100.0 / pieces[cur]

                # dlgGauge.SetValue(progressToSection + 50)

                while result is not None:

                    if self.pendingCancel:
                        break

                    if result == "Moving on...":

                        curPiece += 1
                        allPieces += 1
                        pieceProgress = 0

                    elif isinstance(result, (float, int)):

                        pieceProgress = result

                    else:

                        dlgActionText.SetLabel(result)

                    print `result`

                    progressSub = percentPerEntry * curPiece + percentPerEntry * pieceProgress / 100
                    progress = percentPerPiece * allPieces / 100.0 + progressSub * percentPerPiece / 100.0

                    dlgSubGauge.SetValue(progressSub)
                    dlgSubPercentText.SetLabel("%i%%" % int(progressSub))
                    dlgGauge.SetValue(progress)
                    dlgPercentText.SetLabel("%i%%" % int(progress))
                    dlgSizer.Layout()

                    wx.Yield()

                    result = gen.next()

            if self.pendingCancel:
                break

        # return

        dlg.MakeModal(False)
        dlg.EnableCloseButton(True)

        if not self.pendingCancel:

            fileStr = gen.next()

            dlgSubGauge.SetValue(100)
            dlgSubPercentText.SetLabel("100%")
            dlgGauge.SetValue(100)
            dlgPercentText.SetLabel("100%")

            dlgSubSavingText.SetLabel("Done!")
            dlgSavingText.SetLabel("%i of %i section%s saved properly." % (
            len(sectionsToUpdate), len(sectionsToUpdate), ["", "s"][len(sectionsToUpdate) > 1]))
            dlgActionText.SetLabel("")

            dlgCancelButton.SetLabel("OK")
            dlgSizer.Layout()

            # ----

            if path:
                outfile = open(path, 'wb')
            else:
                outfile = open(pathjoin(self.dirname, self.filename), 'wb')

            outfile.write(fileStr)
            outfile.flush()
            outfile.close()

            self.modify(False)
            self.rom.massModify(False)

            wx.MessageDialog(self, "File saved successfully.", self.baseTitle, wx.OK | wx.ICON_INFORMATION).ShowModal()

            for i in self.layoutTree.allItems:
                self.layoutTree.modify(i, False)

        else:

            succeeded = False
            wx.MessageDialog(self, "Saving cancelled.", self.baseTitle, wx.OK | wx.ICON_WARNING).ShowModal()

            # pop up cancel dialog

        dlg.MakeModal(False)

        self.pendingCancel = False

        dlg.Destroy()

        return succeeded

    def cancelSaving(self, evt):

        self.pendingCancel = True

        dlg = evt.GetEventObject().dlg

        if dlg.IsModal():
            dlg.EndModal(wx.ID_OK)

    def confirmClose(self):

        success = wx.ID_NO

        if self.rom and self.rom.modified:

            dlg = wx.MessageDialog(self, "Save changes to '%s'?" % pathjoin(self.dirname, self.filename),
                                   self.baseTitle, wx.YES | wx.NO | wx.CANCEL | wx.ICON_QUESTION)
            success = dlg.ShowModal()

            if success == wx.ID_YES:
                self.saveFile()
                success = wx.ID_NO

        return success

    def emergencyExit(self, evt):
        self.app.Exit()

    # ----

    def parseDataFile(self, datafile):

        valid = True
        data = {}
        curSection = ""

        datafile.seek(0)

        for line in datafile.xreadlines():

            if line.strip(" ") == "\n":
                continue

            segments = line.split("=")

            if len(segments) < 2:
                valid = False
                break

            key = segments[0].strip()
            value = "=".join(segments[1:]).lstrip().rstrip()

            if key == "section":
                curSection = value
                if curSection not in data.keys():
                    data[curSection] = {}

            elif key.isdigit():

                if not curSection:
                    valid = False
                    break

                data[curSection][int(key)] = value

            elif key.find(",") != -1:

                args = key.replace(" ", "").split(",")

                key = int(args[0])
                subkey = int(args[1])

                if not data[curSection].has_key(key):
                    data[curSection][key] = {}

                if len(args) == 3:
                    subkey2 = int(args[2])

                    if not data[curSection][key].has_key(subkey):
                        data[curSection][key][subkey] = {}

                    data[curSection][key][subkey][subkey2] = value

                else:

                    data[curSection][key][subkey] = value

            else:
                valid = False
                break

        return valid, data

    # ----

    def createInitialSubPanel(self):

        panel = wx.Panel(self.rightPanel, -1)

        sbox = wx.StaticBox(panel, -1, " Instructions")
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sbox.SetForegroundColour("#000000")
        sbox.SetFont(self.subFont)

        text = wx.StaticText(panel, -1,
                             "Double-click an entry in the tree to the left to edit that section of Shining Force II.")

        png = wx.Image("caravan.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        png = wx.StaticBitmap(panel, -1, png, (png.GetWidth(), png.GetHeight()))

        sbs.Add(text, 0, wx.EXPAND | wx.ALL ^ wx.TOP, 10)

        sizer.Add(png, 0, wx.RIGHT, 10)
        sizer.AddSizer(sbs)

        panel.SetSizer(sizer)

        return panel

    def updateTitle(self, modified=False):

        modifiedStr = ["", "* "][modified]

        self.SetTitle(self.baseTitle + " - [ " + modifiedStr + self.dirname + "\\" + self.filename + " ]")
        # FUTURE: self.SetTitle(self.baseTitle + " - [ " + self.project.name + " ]")

    def modify(self, modified=True):

        if self.rom.modified is not modified:
            self.rom.modified = modified
            self.updateTitle(modified)
            self.newFileMenu.Enable(ID["SAVE_PROJECT"], modified)
            self.fileMenu.Enable(ID["SAVE"], modified)
            self.fileMenu.Enable(ID["SAVEAS"], modified)

    def closeROM(self):

        self.rom.close()
        del self.rom
        self.rom = None

        self.filename = ""
        self.dirname = ""

        self.SetTitle(self.baseTitle)

        self.layoutTree.clear()

        for f in self.frames:
            f.Destroy()
            del f
        self.frames = []

        for k, v in self.panels.iteritems():
            v.Destroy()
            del v
        self.panels = {}

        self.newFileMenu.Enable(ID["SAVE_PROJECT"], False)
        self.newFileMenu.Enable(ID["SAVE_PROJECT_AS"], False)
        self.fileMenu.Enable(ID["CLOSE"], False)

        # OLD self.toolsMenu.Enable(ID["MAPVIEWER"], False)

        # self.mainPanel.Destroy()
        # del self.mainPanel

    def createMainPanel(self):

        # OLD: this is the old way, with the attached panel and help space etc.
        """self.mainPanel = mainPanel = wx.Panel(self, -1)
        self.mainPanel.Hide()
        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
    
        # --------------------------
        
        #self.leftPanel = leftPanel = wx.Panel(mainPanel, -1)
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.tree = tree = self.createTree()
        
        choicePanel = wx.Panel(mainPanel, -1)
        cpSizer = wx.BoxSizer(wx.HORIZONTAL)
        radio1 = wx.RadioButton(choicePanel, addID("RADIO_DEC"), "Dec", style=wx.RB_GROUP)
        radio2 = wx.RadioButton(choicePanel, addID("RADIO_HEX"), "Hex")
        radio3 = wx.RadioButton(choicePanel, addID("RADIO_BIN"), "Bin")
        cpSizer.Add(radio1, 0, wx.RIGHT, 5)
        cpSizer.Add(radio2, 0, wx.RIGHT, 5)
        cpSizer.Add(radio3, 0, wx.RIGHT)
        #choicePanel.SetSizer(cpSizer)
        
        #text = wx.StaticText(mainPanel, -1, "Represent numbers in:")
        
        self.helpPanel = wx.Panel(mainPanel, -1)
        helpSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.helpHeader = wx.StaticText(self.helpPanel, -1, "Item Details")
        self.helpHeader.SetFont(self.editFont)
        self.helpText = wx.StaticText(self.helpPanel, -1, "Move the mouse over an item in the interface for a detailed message describing its function.")
        
        helpSizer.Add(self.helpHeader, 0, wx.EXPAND | wx.BOTTOM, 5)
        helpSizer.Add(self.helpText, 0, wx.EXPAND)
        
        self.helpPanel.SetSizer(helpSizer)
        
        disableHelpCheck = wx.CheckBox(mainPanel, wx.ID_ANY, " Disable Help")
        wx.EVT_CHECKBOX(mainPanel, disableHelpCheck.GetId(), self.OnToggleHelp)
        
        leftSizer.Add(tree, 4, wx.EXPAND | wx.RIGHT, 5)
        leftSizer.Add(self.helpPanel, 2, wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM, 15)
        leftSizer.Add(disableHelpCheck, 0, wx.BOTTOM | wx.LEFT, 15)
    
        self.helpText.Wrap(tree.GetClientSize()[0])
        
        #leftSizer.Add(text, 0, wx.TOP | wx.ALIGN_CENTER, 10)
        #leftSizer.Add(choicePanel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        #leftPanel.SetSizer(leftSizer)
        
        # --------------------------
        
        self.rightPanel = rightPanel = wx.Panel(mainPanel, -1)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.header = wx.StaticText(rightPanel, -1, "Welcome to the Caravan")
        self.header.SetFont(self.headerFont)
        
        #self.subPanel = self.createInitialSubPanel()
        
        rightPanel.modifiedPanel = rompanel.ColorPanel(rightPanel, -1, "#00FF00", (15,15), enable=False)
        
        headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        headerSizer.Add(self.header, 1, wx.EXPAND)
        headerSizer.Add(rightPanel.modifiedPanel, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 15)
        
        rightSizer.AddSizer(headerSizer, 0, wx.EXPAND)
        rightSizer.Add(wx.StaticLine(rightPanel, -1, (0,0), (10000, 1)), 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT, 10)
        rightSizer.Add(self.subPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        #rightSizer.Add(wx.Panel(rightPanel), 1, wx.EXPAND)
        
        rightPanel.SetSizer(rightSizer)
        
        # ---------------------------
        
        mainSizer.Add(leftSizer, 0, wx.EXPAND | wx.RIGHT, 5)
        mainSizer.Add(rightPanel, 1, wx.EXPAND | wx.ALL, 5)
        
        mainPanel.SetSizer(mainSizer) """
        # /OLD

        frm = SectionFrame(self, -1, "test")
        # frm = wx.MDIChildFrame(self, -1, "test")

    def resetHelpText(self):
        self.helpHeader.SetLabel("Item Details")
        self.helpText.SetLabel(
            "Move the mouse over an item in the interface for a detailed message describing its function.")
        self.helpText.Wrap(self.helpPanel.GetSize()[0])

    def OnToggleHelp(self, evt):
        self.helpPanel.Enable(not evt.GetSelection())

    def createLoadingDialog(self, name):

        dlg = wx.Dialog(self, -1, self.baseTitle, size=(400, 110))
        dlgSizer = wx.BoxSizer(wx.VERTICAL)

        dlgText = wx.StaticText(dlg, -1, name, style=wx.ALIGN_CENTER)
        dlgText.SetFont(self.editFont)

        dlgSizer.Add(dlgText, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 30)

        dlg.SetSizer(dlgSizer)

        dlg.Show()

        wx.Yield()

        return dlg


# TEMP: now handles creation of plugin windows, but not as plugins yet
class SectionFrame(wx.MDIChildFrame):
    def __init__(self, parent, id, title, *args, **kwargs):
        wx.MDIChildFrame.__init__(self, parent, -1, "test")

        self.parent = parent

        self.createTree()
        self.SetMinSize((-1, 500))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        sizer.Add(self.tree, 1, wx.EXPAND)
        sizer.Fit(self)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivateTreeItem)

    def createTree(self):

        self.tree = tree = wx.TreeCtrl(self, addID("TREE"), size=(200, 200))

        tree.nodes = {}

        tree.nodes["root"] = tree.AddRoot("Editable Content")

        tree.nodes["data"] = tree.AppendItem(tree.nodes["root"], "Data")
        tree.nodes["chars"] = tree.AppendItem(tree.nodes["data"], "Characters")
        tree.nodes["classes"] = tree.AppendItem(tree.nodes["data"], "Classes")
        tree.nodes["promos"] = tree.AppendItem(tree.nodes["data"], "Promotions")
        tree.nodes["monsters"] = tree.AppendItem(tree.nodes["data"], "Monsters")
        tree.nodes["spells"] = tree.AppendItem(tree.nodes["data"], "Spells")
        tree.nodes["items"] = tree.AppendItem(tree.nodes["data"], "Items")
        tree.nodes["shops"] = tree.AppendItem(tree.nodes["data"], "Shops")
        tree.nodes["values"] = tree.AppendItem(tree.nodes["data"], "Gameplay Values")

        tree.nodes["scripting"] = tree.AppendItem(tree.nodes["root"], "Scripting")
        # tree.nodes["scenes"] = tree.AppendItem(tree.nodes["scripting"], "Scenes")
        tree.nodes["dialogue"] = tree.AppendItem(tree.nodes["scripting"], "Dialogue")
        tree.nodes["battles"] = tree.AppendItem(tree.nodes["scripting"], "Battles")
        # tree.nodes["mapevent"] = tree.AppendItem(tree.nodes["scripting"], "Map Events")
        # tree.nodes["othertext"] = tree.AppendItem(tree.nodes["scripting"], "Other Text")

        tree.nodes["resources"] = tree.AppendItem(tree.nodes["root"], "Resources")
        tree.nodes["palettes"] = tree.AppendItem(tree.nodes["resources"], "Palettes")
        tree.nodes["sprites"] = tree.AppendItem(tree.nodes["resources"], "Sprites")
        tree.nodes["battlespr"] = tree.AppendItem(tree.nodes["resources"], "Battle Sprites")
        tree.nodes["weaponspr"] = tree.AppendItem(tree.nodes["resources"], "Weapon Sprites")
        tree.nodes["spellanims"] = tree.AppendItem(tree.nodes["resources"], "Spell Animations")
        tree.nodes["battlebg"] = tree.AppendItem(tree.nodes["resources"], "Battle Backgrounds")
        tree.nodes["battlefloors"] = tree.AppendItem(tree.nodes["resources"], "Battle Floors")
        tree.nodes["itemicons"] = tree.AppendItem(tree.nodes["resources"], "Item/Spell Icons")
        tree.nodes["menuicons"] = tree.AppendItem(tree.nodes["resources"], "Menu Icons")
        tree.nodes["portraits"] = tree.AppendItem(tree.nodes["resources"], "Portraits")
        tree.nodes["mapdef"] = tree.AppendItem(tree.nodes["resources"], "Map Definitions")
        tree.nodes["maptiles"] = tree.AppendItem(tree.nodes["resources"], "Map Tiles")
        tree.nodes["fonts"] = tree.AppendItem(tree.nodes["resources"], "Fonts")
        # tree.nodes["menugfx"] = tree.AppendItem(tree.nodes["resources"], "Menu Graphics")
        # tree.nodes["images"] = tree.AppendItem(tree.nodes["resources"], "Other Images")
        # tree.nodes["sounds"] = tree.AppendItem(tree.nodes["resources"], "Sounds")

        """tree.nodes["code"] = tree.AppendItem(tree.nodes["root"], "Code")
        tree.nodes["general"] = tree.AppendItem(tree.nodes["code"], "General Functions")
        tree.nodes["menus"] = tree.AppendItem(tree.nodes["code"], "Menus")
        tree.nodes["mapparse"] = tree.AppendItem(tree.nodes["code"], "Map Parsing")
        tree.nodes["resourceload"] = tree.AppendItem(tree.nodes["code"], "Resource Loading")
        tree.nodes["textbox"] = tree.AppendItem(tree.nodes["code"], "Textbox")
        tree.nodes["spell_effects"] = tree.AppendItem(tree.nodes["code"], "Spell Effects")
        tree.nodes["item_effects"] = tree.AppendItem(tree.nodes["code"], "Item Effects")
        tree.nodes["ai"] = tree.AppendItem(tree.nodes["code"], "AI")"""

        tree.nodes["other"] = tree.AppendItem(tree.nodes["root"], "Other")
        tree.nodes["romviewer"] = tree.AppendItem(tree.nodes["other"], "ROM Viewer")
        # tree.nodes["header"] = tree.AppendItem(tree.nodes["other"], "Header")
        # tree.nodes["tables"] = tree.AppendItem(tree.nodes["other"], "Address Tables")

        tree.Expand(tree.nodes["root"])

        for k in tree.nodes.keys():

            addID(k)

            item = tree.nodes[k]
            name = tree.GetItemText(item)
            isParent = tree.GetChildrenCount(item)

            if not isParent and name not in panellist.panelList.keys():
                tree.SetItemTextColour(item, "#808080")

        return tree

    def spawnPluginWindow(self, item):

        name = self.tree.GetItemText(item)

        # if self.curPanelID:
        #    self.tree.SetItemBold(self.curPanelID, False)

        self.tree.SetItemBold(item, True)

        # self.header.SetLabel(name)
        # self.curPanelID = item
        # self.subPanel.Hide()

        if window.mapViewer.inited:
            window.mapViewer.updateContext(consts.VC_NOTHING)

        """if name in self.panels.keys():
            self.subPanel = self.panels[name]
            data = self.subPanel.getCurrentData()
            if data:
                self.subPanel.updateModifiedIndicator(data.modified)
            self.subPanel.Show()"""

        # else:
        pc = panellist.getPanelClass(name)

        dlg = self.parent.createLoadingDialog("Loading %s Section..." % name)

        # self.subPanel = pc(self.rightPanel, -1, self.rom)
        # self.panels[name] = self.subPanel
        # self.rightPanel.GetSizer().Add(self.subPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        # self.subPanel.updateModifiedIndicator(False)

        frame = rompanel.ROMFrame(self.parent, -1, pc)
        frame.SetIcon(icon)
        # frame.createPanel(pc)

        """frame.parent = self.parent
        
        panel = wx.Panel(frame, -1)
        panel.parent = frame.parent
        
        cpanel = pc(panel, -1, self.parent.rom)
        cpanel.updateModifiedIndicator(False)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        sizer.Add(cpanel, 0, wx.ALL, 10)
        sizer.Fit(panel)
        #panel.SetMaxSize(cpanel.GetSize())

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        frame.SetSizer(sizer2)
        sizer2.Add(panel, 1, wx.EXPAND)
        #sizer2.Add(panel)
        sizer2.Fit(frame)
        frame.bestSize = frame.GetSize()
        frame.SetMaxSize(frame.bestSize)"""

        # frame.Bind(wx.EVT_MAXIMIZE,

        dlg.Destroy()

        # self.parent.updateUndoRedo()

    def OnActivateTreeItem(self, evt):

        item = evt.GetItem()
        isParent = self.tree.GetChildrenCount(item)

        # print '\n'.join(dir(self.tree))

        if not isParent:
            # spawn plugin panel
            self.spawnPluginWindow(item)
            pass


class NewProjectDialog(wx.Dialog):
    def __init__(self, parent):

        wx.Dialog.__init__(self, parent, title="Create New Project")

        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)

        st1 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "ROM Info"), wx.VERTICAL)
        self.romCtrl = romCtrl = fbb.FileBrowseButtonWithHistory(self, wx.ID_ANY, size=(400, -1),
                                                                 labelText="ROM File: ",
                                                                 dialogTitle="Select a ROM File (.bin)",
                                                                 fileMask="*.bin")
        self.romCtrl.SetHistory(self.parent.settings.history["ROMs"], 0)

        st1platformSizer = wx.BoxSizer(wx.HORIZONTAL)
        platformText = wx.StaticText(self, wx.ID_ANY, "Platform: ")
        self.platformCtrl = platformCtrl = wx.Choice(self, wx.ID_ANY)
        st1platformSizer.Add(platformText, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        st1platformSizer.Add(platformCtrl)

        # FUTURE: add these back in.
        """st2 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Project Settings"), wx.VERTICAL)
        self.gameSpecCheck = gameSpecCheck = wx.CheckBox(self, wx.ID_ANY, " Use existing game specification.")
        self.gameSpecCtrl = gameSpecCtrl = wx.ListBox(self, wx.ID_ANY, size=(200,150))        
        self.gameSpecAddBtn = gameSpecAddBtn = wx.Button(self, wx.ID_ANY, "Add...")
        self.gameSpecRemoveBtn = gameSpecRemoveBtn = wx.Button(self, wx.ID_ANY, "Remove")
        
        st2gameSpecBtnSizer = wx.BoxSizer(wx.VERTICAL)
        st2gameSpecBtnSizer.Add(self.gameSpecAddBtn, 0)
        st2gameSpecBtnSizer.Add(self.gameSpecRemoveBtn, 0)
        
        st2gameSpecSizer = wx.BoxSizer(wx.HORIZONTAL)
        st2gameSpecSizer.Add(self.gameSpecCtrl, 1, wx.RIGHT, 5)
        st2gameSpecSizer.AddSizer(st2gameSpecBtnSizer)
        
        self.cacheCheck = cacheCheck = wx.CheckBox(self, wx.ID_ANY, " Cache loaded data (reduces loading times)")"""
        # /FUTURE

        self.okBtn = okBtn = wx.Button(self, wx.ID_ANY, "OK")
        self.cancelBtn = cancelBtn = wx.Button(self, wx.ID_ANY, "Cancel")
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        # ----

        sizer.AddSizer(st1, 0, wx.ALL | wx.EXPAND, 5)
        st1.Add(romCtrl, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)
        st1.AddSizer(st1platformSizer, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)

        # FUTURE: add these back in.
        """sizer.AddSizer(st2, 0, wx.ALL | wx.EXPAND, 5)
        st2.Add(gameSpecCheck, 0, wx.ALL, 5)
        st2.Add(st2gameSpecSizer, 0, wx.LEFT | wx.EXPAND, 20)
        st2.AddSpacer(5)
        st2.Add(cacheCheck, 0, wx.ALL, 5)"""
        # /FUTURE

        sizer.AddSizer(btnSizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 10)
        btnSizer.Add(okBtn, 0, wx.RIGHT, 10)
        btnSizer.Add(cancelBtn, 0)

        self.SetSizer(sizer)
        self.SetInitialSize()
        okBtn.SetFocus()

        # ----

        # DISABLED: platform selection, force to Genesis
        self.platformCtrl.AppendItems(["Sega Genesis"])
        self.platformCtrl.SetSelection(0)
        self.platformCtrl.Enable(False)

        # FUTURE: add these back in.
        """self.repopulateGameSpecList()
        if self.gameSpecCtrl.GetCount():
            self.gameSpecCheck.SetValue(True)
            
        self.refreshGameSpecList()"""
        # /FUTURE

        # ----

        self.Bind(wx.EVT_BUTTON, self.OnConfirm, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.cancelBtn)

        # FUTURE: add these back in.
        """self.Bind(wx.EVT_BUTTON, self.OnAddGameSpec, self.gameSpecAddBtn)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveGameSpec, self.gameSpecRemoveBtn)
        
        self.Bind(wx.EVT_CHECKBOX, self.OnToggleGameSpec, self.gameSpecCheck)
        
        self.Bind(wx.EVT_LISTBOX, self.OnSelectGameSpec, self.gameSpecCtrl)"""
        # /FUTURE

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def repopulateGameSpecList(self):

        self.gameSpecCtrl.Clear()
        self.gameSpecCtrl.AppendItems(self.parent.settings.games.keys())

    def refreshGameSpecList(self):

        isEnabled = self.gameSpecCheck.GetValue()
        self.gameSpecCtrl.Enable(isEnabled)

        if self.gameSpecCtrl.GetCount():
            self.gameSpecCtrl.SetSelection(isEnabled - 1)
        else:
            self.gameSpecCtrl.SetSelection(-1)

        self.gameSpecAddBtn.Enable(isEnabled)
        self.gameSpecRemoveBtn.Enable(self.gameSpecCtrl.GetSelection() != -1)

    def OnToggleGameSpec(self, evt):

        self.refreshGameSpecList()

    def OnSelectGameSpec(self, evt):

        self.refreshGameSpecList()

    def OnAddGameSpec(self, evt):

        dlg = wx.FileDialog(self, "Select a Caravan Game Specification File (.caravan-game)", "", "", "*.caravan-game",
                            wx.OPEN)

        while True:

            if dlg.ShowModal() == wx.ID_OK:

                filename = dlg.GetFilename()
                dirname = dlg.GetDirectory()

                path = pathjoin(dirname, filename)
                file = open(path, 'rb')

                try:

                    # TODO: check authenticity of file
                    obj = pickle.load(file)
                    res = wx.ID_YES

                    if self.parent.settings.games.has_key(obj.name):
                        res = wx.MessageDialog(self,
                                               "A Game Specification with the name '%s' is already loaded.  Change its file to %s?" % (
                                               obj.name, path), self.parent.baseTitle,
                                               wx.YES | wx.NO | wx.ICON_QUESTION).ShowModal()

                    if res == wx.ID_YES:
                        self.parent.settings.games[obj.name] = filename
                        self.parent.settings.save()
                        self.repopulateGameSpecList()
                        self.refreshGameSpecList()

                        wx.MessageDialog(self, "Added '%s'." % obj.name, self.parent.baseTitle,
                                         wx.OK | wx.ICON_INFORMATION).ShowModal()

                    break

                except EOFError, e:
                    wx.MessageDialog(self, "%s is not a valid Caravan Game Specification File." % path,
                                     self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()

            else:
                break

    def OnRemoveGameSpec(self, evt):

        name = self.gameSpecCtrl.GetString(self.gameSpecCtrl.GetSelection())
        res = wx.MessageDialog(self, "Are you sure you want to remove '%s'?" % name, self.parent.baseTitle,
                               wx.YES | wx.NO | wx.ICON_QUESTION).ShowModal()

        if res == wx.ID_YES:
            del self.parent.settings.games[name]
            self.parent.settings.save()
            self.repopulateGameSpecList()
            self.refreshGameSpecList()

            wx.MessageDialog(self, "Removed '%s'." % name, self.parent.baseTitle,
                             wx.OK | wx.ICON_INFORMATION).ShowModal()

    def OnConfirm(self, evt):

        try:
            f = file(self.romCtrl.GetValue(), "rb")
        except IOError, e:
            wx.MessageDialog(self, "Invalid ROM file.", self.parent.baseTitle + " -- Error",
                             wx.OK | wx.ICON_ERROR).ShowModal()
            return

        # FUTURE: add these back in.
        """needsGameSpec = self.gameSpecCtrl.GetSelection() == -1 and self.gameSpecCheck.GetValue()
        
        if needsGameSpec:
            wx.MessageDialog(self, "Select a Game Specification File.", self.parent.baseTitle + " -- Error", wx.OK | wx.ICON_ERROR).ShowModal()
            return"""
        # /FUTURE

        self.SetReturnCode(wx.ID_OK)
        self.EndModal(self.GetReturnCode())

    def OnClose(self, evt):
        self.EndModal(self.GetReturnCode())


class AppFrame(wx.aui.AuiMDIParentFrame):
    def __init__(self, app, parent, id, title):
        wx.aui.AuiMDIParentFrame.__init__(self, parent, id, title, size=(600, 400), style=wx.DEFAULT_FRAME_STYLE)


mw = MainFrame(None, -1, app)
mw.Show(True)

app.SetTopWindow(mw)
app.MainLoop()
