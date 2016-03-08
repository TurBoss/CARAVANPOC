import wx
import wx.gizmos as gizmos
import window
import asm, panellist, rompanel

isz = (16,16)
il = wx.ImageList(isz[0], isz[1])
fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
filemodidx  = il.Add(wx.ArtProvider_GetBitmap(wx.ART_WARNING, wx.ART_OTHER, isz))

fldryesidx  = il.Add(wx.ArtProvider_GetBitmap(wx.ART_TICK_MARK, wx.ART_OTHER, isz))
fldrnoidx  = il.Add(wx.ArtProvider_GetBitmap(wx.ART_CROSS_MARK, wx.ART_OTHER, isz))

icon = wx.Icon("caravan.ico", wx.BITMAP_TYPE_ICO)

class LayoutTreeFrame(window.CaravanChildFrame):
    
    def __init__(self, parent, id, *args, **kwargs):
        
        window.CaravanChildFrame.__init__(self, parent, id, "Layout Tree", size=(270,-1), *args, **kwargs)
        
        self.layoutTree = LayoutTree(self, wx.ID_ANY)
        
class LayoutTree(gizmos.TreeListCtrl):
    
    def __init__(self, parent, id, *args, **kwargs):
        
        gizmos.TreeListCtrl.__init__(self, parent, id, size=(250,-1), style=
                                        wx.TR_DEFAULT_STYLE
                                        | wx.TR_HAS_BUTTONS
                                        | wx.TR_TWIST_BUTTONS
                                        #| wx.TR_ROW_LINES
                                        #| wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES 
                                        | wx.TR_FULL_ROW_HIGHLIGHT,
                                        *args, **kwargs)
        
        self.parent = parent
        self.allItems = []
        
        self.SetImageList(il)
        
        self.AddColumn("Item")
        #self.AddColumn("Start")
        #self.AddColumn("End")
        
        self.SetMainColumn(0)
        
        self.SetColumnWidth(0, 220)
        #self.SetColumnWidth(0, 130)
        #self.SetColumnWidth(1, 50)
        #self.SetColumnWidth(2, 50)
        
        self.SetIndent(10)
        
        # ----------
        
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivateTreeItem)
        
        # FUTURE: context menu - self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
    
    def init(self):

        self.root = self.AddRoot("ROM")
        self.Expand(self.root)
        self.SetItemImage(self.root, fldridx, which=wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root, fldropenidx, which=wx.TreeItemIcon_Expanded)
        
        self.refreshTree()
    
    def clear(self):
        
        self.DeleteAllItems()
        self.DeleteRoot()
        
    def refreshTree(self):
        
        proj = self.parent.project
        self.allItems = []
        
        # FUTURE: this is for when romshifting works and it's completely pluginified.
        """for s in proj.layout.sections:
            i = self.AppendItem(self.root, s.name)
            self.SetItemImage(i, fileidx, which=wx.TreeItemIcon_Normal)
            self.SetItemText(i, asm.getBankAddr(s.start), 1)
            self.SetItemText(i, asm.getBankAddr(s.end), 2)"""
        # /FUTURE
        
        # TEMP: add static sections based on normal SF2 layout
        
        # this is a dictionary of tree names to data section keynames
        sections = \
                {
                    "Dialogue": "dialogue",
                    "Sprites": "sprites",
                    "Battle Sprites": "battle_sprites",
                    "Battle Backgrounds": "backgrounds",
                    "Battle Floors": "battle_floors",
                    "Portraits": "portraits",
                    "Map Definitions": "maps",
                    "Palettes": "palettes",
                    "Battles": "battles",
                    "Map Tiles": "tilesets",
                    "Item/Spell Icons": "other_icons",
                    "Menu Icons": "menu_icons",
                    "Weapon Sprites": "weapon_sprites",
                    "Spell Animations": "spell_animations",
                }
        
        nosects = ["Battle Floors", "Spell Animations", "Weapon Sprites"]
        
        for sect in sorted(sections.keys()):
            
            tempFolder = self.AppendItem(self.root, sect)
            
            if sect in nosects:
                self.SetItemImage(tempFolder, fldrnoidx, which=wx.TreeItemIcon_Normal)
            else:
                self.SetItemImage(tempFolder, fldryesidx, which=wx.TreeItemIcon_Normal)
            
            dataName = sections[sect]
            
            if dataName is not None:
                
                cnt = 0
                for i,d in enumerate(self.parent.rom.data[dataName]):
                    
                    if sect != "Sprites" or not i % 3:
                        tempItem = self.AppendItem(tempFolder, d.name)
                        self.SetItemImage(tempItem, fileidx, which=wx.TreeItemIcon_Normal)
                        cnt+=1
                        self.allItems.append(tempItem)
                        
                self.SetItemText(tempFolder, "%s (%i)" % (sect, cnt))
                
        otherFolder = self.AppendItem(self.root, "Other")
        self.SetItemImage(otherFolder, fldryesidx, which=wx.TreeItemIcon_Normal)
        
        fontItem = self.AppendItem(otherFolder, "Dialogue Font")
        self.SetItemImage(fontItem, fileidx, which=wx.TreeItemIcon_Normal)
        self.allItems.append(fontItem)
        
        self.Expand(self.root)
        
    def OnContextMenu(self, evt):
        
        name = self.GetItemText(self.GetSelection())
        
        m = wx.Menu()
        item = wx.MenuItem(m, -1, name)
        m.AppendItem(item)
        m.AppendSeparator()
        
        self.PopupMenu(m)
        
        #print "\n".join(dir(evt))
        #print `evt.GetItem()`
        
    def spawnPluginWindow(self, item):
        
        parent = self.GetItemParent(item)
        name = self.GetItemText(parent)
        
        if name != "Other":

            name = name.split(" (")[0]
        
        else:
            
            name = self.GetItemText(item)

        #if self.curPanelID:
        #    self.tree.SetItemBold(self.curPanelID, False)
        
        #self.SetItemBold(item, True)
        
        #self.header.SetLabel(name)
        #self.curPanelID = item
        #self.subPanel.Hide()
    
        #if window.mapViewer.inited:
        #    window.mapViewer.updateContext(consts.VC_NOTHING)

        """if name in self.panels.keys():
            self.subPanel = self.panels[name]
            data = self.subPanel.getCurrentData()
            if data:
                self.subPanel.updateModifiedIndicator(data.modified)
            self.subPanel.Show()"""
            
        #else:
        pc = panellist.getPanelClass(name)
        
        dlg = self.parent.createLoadingDialog("Loading %s Section..." % name)
        
        #self.subPanel = pc(self.rightPanel, -1, self.rom)
        #self.panels[name] = self.subPanel
        #self.rightPanel.GetSizer().Add(self.subPanel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        #self.subPanel.updateModifiedIndicator(False)
        
        frame = rompanel.ROMFrame(self.parent, -1, pc)
        frame.SetIcon(icon)
        #frame.createPanel(pc)
        
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
        
        #frame.Bind(wx.EVT_MAXIMIZE, 
        
        dlg.Destroy()
        
        #self.parent.updateUndoRedo()
        
        self.parent.frames.append(frame)
        
        return frame
    
    def modify(self, item, modified=True):
        
        icon = [fileidx, filemodidx][modified]
        self.SetItemImage(item, icon, which=wx.TreeItemIcon_Normal)
    
    def OnActivateTreeItem(self, evt):
        
        item = evt.GetItem()
        isParent = self.GetChildrenCount(item)
        
        #print '\n'.join(dir(self.tree))
        
        if not isParent:
            
            section = self.GetItemText(self.GetItemParent(item))
            
            # spawn plugin panel
            frame = self.spawnPluginWindow(item)
            
            
            if section != "Other":

                sel = int(self.GetItemText(item).split(": ")[0])
                
                if section.split(" (")[0] == "Sprites":
                    sel *= 3
                
                frame.contentPanel.changeSelection(sel)
                
            frame.contentPanel.treeItem = item
            frame.SetTitle(frame.contentPanel.frameTitle + " -- " + self.GetItemText(item))
            
        evt.Skip()
        