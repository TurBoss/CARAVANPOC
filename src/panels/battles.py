import wx, rompanel
import wx.lib.scrolledpanel
import wx.grid as grid
import sys

sys.path.insert(0, '../')

import data
import window
import consts

h2i = lambda i: int(i, 16)

icons = []
iconNames = ["lowsky", "plains", "road", "grass", "forest", "hill", "desert", "sky", "water", "blocked"]
for n in iconNames:
    bmp = wx.Bitmap("terrain_%s.ico" % n, wx.BITMAP_TYPE_ICO)
    icons.append(bmp)
        
class BattlePanel(rompanel.ROMPanel):
    
    frameTitle = "Battle Editor"
    
    def init(self):
        
        self.palette = self.rom.getDataByName("palettes", "Sprite & UI Palette")
        self.frame = 0
        
        self.terrainIcons = icons
        
        self.curBattleIdx = 0
        self.curUnitContext = 0
        self.curUnitIdx = 0
        self.curOrderSet = 0
        self.curRegionIdx = 0
        self.curPointIdx = 0
        
        # -------------------------------
        
        #self.rom.data["sprites"][0*3].hexlify()
        
        #inst = wx.StaticText(self, -1, "Edit battle formations, including allies, NPCs, and monsters.")
        #inst.Wrap(inst.GetClientSize()[0])
        
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        #sbs1 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "1. Select a battle."), wx.VERTICAL)
        sbs2 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Entities"), wx.VERTICAL)
        sbs5 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Entity Properties"), wx.VERTICAL)
        sbs6 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Battle Properties"), wx.VERTICAL)
        
        #sbs7 = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Code"), wx.VERTICAL)
        
        #sbs2.StaticBox.SetForegroundColour("#000000")
        #sbs4.StaticBox.SetForegroundColour("#000000")
        
        # -----------------------
        
        """self.battleList = wx.ComboBox(self, wx.ID_ANY, size=(100,-1))
        self.battleList.AppendItems([b.name for b in self.rom.data["battles"]])
        self.battleList.SetSelection(0)

        self.addHelpText(self.battleList,
            "Battle List",
            "A list of all battles in the game. Select a battle from the dropdown list and its properties will be displayed in the various UI elements to be edited.")
            
        sbs1.Add(self.battleList, 0, wx.ALL | wx.EXPAND, 10)"""
        
        # ------------------------
        
        self.scrollWnd = scroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(210, 180))
            
        text4 = wx.StaticText(scroll, -1, "Monsters")
        text5 = wx.StaticText(scroll, -1, "Shining Force Placeholder Entities")
        #text6 = wx.StaticText(scroll, -1, "Allies")
        text7 = wx.StaticText(scroll, -1, "NPCs")
        text8 = wx.StaticText(self, -1, "Add:")
        
        self.monsterSizer = monsterSizer = wx.GridSizer(8,4)
        self.forceSizer = forceSizer = wx.GridSizer(8,4)
        #self.allySizer = allySizer = wx.GridSizer(1,4)
        self.npcSizer = npcSizer = wx.GridSizer(2,4)
        
        self.monsterPanels = []
        self.forcePanels = []
        #self.allyPanels = []
        self.npcPanels = []
        
        self.allGroupSizers = [self.monsterSizer, self.forceSizer, self.npcSizer]
        self.allGroupPanels = [self.monsterPanels, self.forcePanels,self.npcPanels]

        for con in range(len(self.allGroupPanels)):
            
            curPanels = self.allGroupPanels[con]
            curData = self.allGroupData[con]
            curSizer = self.allGroupSizers[con]
            
            for p in range(curSizer.GetRows() * curSizer.GetCols()):
                
                ap = rompanel.SpritePanel(scroll, wx.ID_ANY, 24, 24, self.palette, scale=2, bg=None, func=self.OnClickPanel)
                ap.refreshSprite([])
                ap.context = con
                ap.num = p
                ap.used = False
                curPanels.append(ap)
                
                self.addHelpText(ap,
                    "Battle Roster",
                    "This scrolling window displays the sprite of every combatant in an attempt to simulate what the battle might look like. Click on one to edit its properties.")
                
        self.animDelays = [250, 150, 50, 50, 50, 50]
        self.animFrame = 0
        self.curAnim = 0
        
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.changeAnim(0)

        self.scrollSizer = scrollSizer = wx.BoxSizer(wx.VERTICAL)
        
        scrollSizer.Add(text4)
        scrollSizer.AddSizer(monsterSizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 5)
        scrollSizer.Add(text5)
        scrollSizer.AddSizer(forceSizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 5)
        #scrollSizer.Add(text6)
        #scrollSizer.AddSizer(allySizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 5)
        scrollSizer.Add(text7)
        scrollSizer.AddSizer(npcSizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM, 5)
        #scrollSizer.AddSizer(forceSizer)
        #scrollSizer.AddSizer(forceSizer)
        #scrollSizer.AddSizer(forceSizer)

        scroll.SetupScrolling(scroll_x = False)
        scroll.SetScrollRate(0,12)

        scroll.SetSizer(scrollSizer)
        scroll.Layout()
        #scroll.Fit()
        
        scrollButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.addMonsterButton = wx.Button(self, wx.ID_ANY, "Monster", size=(55,20))
        self.addForceButton = wx.Button(self, wx.ID_ANY, "Member", size=(55,20))
        #self.addAllyButton = wx.Button(self, wx.ID_ANY, "Ally", size=(40,20))
        self.addNPCButton = wx.Button(self, wx.ID_ANY, "NPC", size=(40,20))
        
        self.addHelpText(self.addMonsterButton,
            "Add Monster Button",
            "Click to add an additional monster to the battle.")
        self.addHelpText(self.addMonsterButton,
            "Add Force Slot Button",
            "Click to add an additional Shining Force member slot to the battle.")
        self.addHelpText(self.addMonsterButton,
            "Add NPC Button",
            "Click to add an additional NPC (non-player character) to the battle.")
            
        scrollButtonSizer.Add(text8, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        scrollButtonSizer.Add(self.addMonsterButton, 0)
        scrollButtonSizer.Add(self.addForceButton, 0)
        #scrollButtonSizer.Add(self.addAllyButton, 0)
        scrollButtonSizer.Add(self.addNPCButton, 0)
        
        sbs2.Add(scroll, 1, wx.ALL | wx.EXPAND, 3)
        sbs2.AddSizer(scrollButtonSizer, 0, wx.EXPAND)
        
        # ------------------------
        
        text1 = wx.StaticText(self, -1, "X")
        text2 = wx.StaticText(self, -1, "Y")
        self.unitText = text4 = wx.StaticText(self, -1, "    Unit (temp.)")
        text3 = wx.StaticText(self, -1, "Item")
        
        modifySizer = wx.BoxSizer(wx.HORIZONTAL)
        
        modifyAnimSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.modifyAnimPanel = rompanel.SpritePanel(self, wx.ID_ANY, 24, 24, self.palette, scale=2, bg=None)
        self.addHelpText(self.modifyAnimPanel,
            "Sprite Animation",
            "Displays the sprite of the unit currently being edited.  Changes to the unit type control next to this will be reflected here, so you can see if you have chosen the correct unit.")
        
        self.modifyFacingUpRadio = wx.RadioButton(self, wx.ID_ANY, "", style=wx.RB_GROUP)
        self.modifyFacingLeftRadio = wx.RadioButton(self, wx.ID_ANY, "")
        self.modifyFacingRightRadio = wx.RadioButton(self, wx.ID_ANY, "")
        self.modifyFacingDownRadio = wx.RadioButton(self, wx.ID_ANY, "")
        
        self.addHelpText(self.modifyFacingUpRadio,
            "NPC Facing Button\nUp",
            "When editing an NPC, this button allows you to set its facing to \"up\".")
        self.addHelpText(self.modifyFacingLeftRadio,
            "NPC Facing Button\nLeft",
            "When editing an NPC, this button allows you to set its facing to \"left\".")
        self.addHelpText(self.modifyFacingRightRadio,
            "NPC Facing Button\nRight",
            "When editing an NPC, this button allows you to set its facing to \"right\".")            
        self.addHelpText(self.modifyFacingDownRadio,
            "NPC Facing Button\nDown",
            "When editing an NPC, this button allows you to set its facing to \"down\".")            
            
        self.modifyDeleteButton = wx.Button(self, wx.ID_ANY, "Delete", size=(40,20))
        
        modifyAnimFacingMidSizer = wx.BoxSizer(wx.HORIZONTAL)
        modifyAnimFacingMidSizer.Add(self.modifyFacingLeftRadio, 1, wx.LEFT, 7)
        modifyAnimFacingMidSizer.Add(self.modifyFacingRightRadio, 1, wx.LEFT, 3)
        
        modifyAnimSizer.Add(self.modifyAnimPanel, 0, wx.BOTTOM, 3)
        
        modifyAnimSizer.Add(self.modifyFacingUpRadio, 0, wx.ALIGN_CENTER)
        modifyAnimSizer.AddSizer(modifyAnimFacingMidSizer, 0, wx.ALIGN_CENTER | wx.EXPAND)
        modifyAnimSizer.Add(self.modifyFacingDownRadio, 0, wx.ALIGN_CENTER | wx.BOTTOM, 3)
        
        modifyAnimSizer.Add(self.modifyDeleteButton, 0, wx.EXPAND)
        
        modifyMainSizer = wx.BoxSizer(wx.VERTICAL)
        
        modifyTopSizer = wx.BoxSizer(wx.HORIZONTAL)

        #self.modifyList = wx.ComboBox(self, wx.ID_ANY, size=(120,-1))
        self.modifyList = wx.SpinCtrl(self, wx.ID_ANY, size=(50,20), max=175)
        self.addHelpText(self.modifyList,
            "Unit Chooser",
            "A number control that allows you to change the type of the currently selected unit.\n(Note: Monster data is currently not loaded, so the value doesn't necessarily correspond to the sprite (unless current unit is an NPC).)")
            
        self.modifyItemList = wx.ComboBox(self, wx.ID_ANY, size=(110,-1))
        
        self.modifyXCtrl = wx.SpinCtrl(self, wx.ID_ANY, size=(45,20), max=47)
        self.modifyYCtrl = wx.SpinCtrl(self, wx.ID_ANY, size=(45,20), max=47)
        
        self.addHelpText(self.modifyXCtrl,
            "Unit X Position",
            "Change the starting X coordinate of the currently selected unit.")
        self.addHelpText(self.modifyYCtrl,
            "Unit Y Position",
            "Change the starting Y coordinate of the currently selected unit.")
            
        #self.modifyRestCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(-1,20), style=wx.TE_MULTILINE)
        
        modifyTopSizer.Add(text4, 0, flag=wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        modifyTopSizer.Add(self.modifyList, 0, flag=wx.RIGHT, border=5)
        modifyTopSizer.Add(text3, 0, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        modifyTopSizer.Add(self.modifyItemList, 0, flag=wx.RIGHT, border=5)
        modifyTopSizer.Add(text1, 0, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        modifyTopSizer.Add(self.modifyXCtrl, 0, flag=wx.RIGHT, border=5)
        modifyTopSizer.Add(text2, 0, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=5)
        modifyTopSizer.Add(self.modifyYCtrl, 0)
        
        # ----
        
        blankText = wx.StaticText(self, -1, " ")
        
        self.orderSet1Radio = wx.RadioButton(self, wx.ID_ANY, " Edit Order Set 1", style=wx.RB_GROUP)
        self.orderSet2Radio = wx.RadioButton(self, wx.ID_ANY, " Edit Order Set 2")
        
        self.addHelpText(self.orderSet1Radio,
            "Edit Order Set 1",
            "Check this to edit the first set of orders for this unit.")
        self.addHelpText(self.orderSet2Radio,
            "Edit Order Set 2",
            "Check this to edit the second set of orders for this unit.")
            
        self.targetCheck = wx.CheckBox(self, wx.ID_ANY, " Use trigger region...")
        self.targetList = wx.ComboBox(self, wx.ID_ANY)
        
        self.addHelpText(self.targetCheck,
            "Unit Target Sub-AI",
            "Check this to enable more advanced targeting AI for this unit.")
        
        self.addHelpText(self.targetList,
            "Target List",
            "A list of viable target regions for the unit to use. If a region is selected, the unit will not spring into attack mode until either a) the region contains no other monsters or b) the region is entered by a force member.")
            
        modifyTargetSizer = wx.BoxSizer(wx.VERTICAL)
        
        modifyTargetSizer.Add(self.orderSet1Radio, 0, wx.BOTTOM, 3)
        modifyTargetSizer.Add(self.orderSet2Radio, 0, wx.BOTTOM, 3)
        modifyTargetSizer.Add(blankText, 0, wx.BOTTOM, 3)
        modifyTargetSizer.Add(self.targetCheck, 0, wx.BOTTOM, 3)
        modifyTargetSizer.Add(self.targetList, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)        

        # ----
        
        self.gotoCheck = wx.CheckBox(self, wx.ID_ANY, " Use spec. move order...")
        
        self.gotoForceRadio = wx.RadioButton(self, wx.ID_ANY, " Follow force member...", style=wx.RB_GROUP)
        self.gotoPointRadio = wx.RadioButton(self, wx.ID_ANY, " Move towards point...")
        self.gotoAllyRadio = wx.RadioButton(self, wx.ID_ANY, " Follow ally...")
        
        self.addHelpText(self.gotoCheck,
            "Unit Moving Sub-AI",
            "Check this to enable more advanced movement AI for this unit.")
        
        self.addHelpText(self.gotoForceRadio,
            "Follow Force Member",
            "If checked, the unit will go toward the selected force member slot (in the list below). (For example, if \"Force Member 3\", the unit will go toward whichever character is at position 3 in the current force.")
        self.addHelpText(self.gotoPointRadio,
            "Move to Point",
            "If checked, the unit will move toward the selected point. Points are defined in the battle property window above.")
        self.addHelpText(self.gotoAllyRadio,
            "Follow Fellow Enemy",
            "If checked, the unit will follow one of its allies (the monsters). This is a good option for forcing enemies to travel together to pose a bigger threat to the player.")            
            
        hideRadio = wx.RadioButton(self, -1, "", style=wx.RB_GROUP)
        hideRadio.Hide()
        
        self.gotoList = wx.ComboBox(self, wx.ID_ANY)
        
        self.addHelpText(self.gotoList,
            "Movement Target List",
            "A list of the viable movement targets related to the movement option you've selected. Choose here from available targets.")
            
        modifyGotoSizer = wx.BoxSizer(wx.VERTICAL)
        
        modifyGotoSizer.Add(self.gotoCheck, 0, wx.BOTTOM, 3)
        modifyGotoSizer.Add(self.gotoForceRadio, 0, wx.BOTTOM, 3)
        modifyGotoSizer.Add(self.gotoPointRadio, 0, wx.BOTTOM, 3)
        modifyGotoSizer.Add(self.gotoAllyRadio, 0, wx.BOTTOM, 3)
        modifyGotoSizer.Add(self.gotoList, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # ----
        
        aiText = wx.StaticText(self, -1, "AI:")
        
        modifyAISizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.modifyAICtrl = wx.SpinCtrl(self, wx.ID_ANY, size=(45,20), max=15)
        self.addHelpText(self.modifyAICtrl,
            "Unit AI Chooser",
            "There are 16 AI routines that can be given to an enemy unit that determine the actions it takes and the way it responds to certain events. At the moment, there is no list of what these do.")
        
        modifyAISizer.Add(aiText, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        modifyAISizer.Add(self.modifyAICtrl, 0, wx.RIGHT, 5)
        
        modifyMiscSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.modifyMiscItemBrokenCheck = wx.CheckBox(self, wx.ID_ANY, " Extra item is broken")
        self.modifyMiscReinforceCheck = wx.CheckBox(self, wx.ID_ANY, " Region-triggered spawn")
        self.modifyMiscRespawnCheck = wx.CheckBox(self, wx.ID_ANY, " Continually respawn")
        self.modifyMisc1Check = wx.CheckBox(self, wx.ID_ANY, " ???")
        
        self.addHelpText(self.modifyMiscItemBrokenCheck,
            "Unit Item Broken Check",
            "Check to make the extra item given to this unit broken (using it once more will destroy the item, and its icon appears with cracks).")
        self.addHelpText(self.modifyMiscReinforceCheck,
            "Unit Reinforce Check",
            "Check to make the unit only appear when either of the regions in its orders is entered by a force member.")
        self.addHelpText(self.modifyMiscRespawnCheck,
            "Unit Respawn Check",
            "Check to make the unit respawn when dead.\n(Warning: if checked without reinforce checked, the unit will respawn immediately after it dies, so the only way to win the battle is to kill it last.)")
        self.addHelpText(self.modifyMisc1Check,
            "Unit ??? Check",
            "An unknown property that, by default, is only checked for the GIZMOs in the first battle. Our best guess is that it relates to increased evasion chance.")
            
        modifyMiscSizer.AddSizer(modifyAISizer, 0, wx.BOTTOM, 5)
        modifyMiscSizer.Add(self.modifyMiscItemBrokenCheck, 0, wx.BOTTOM, 3)
        modifyMiscSizer.Add(self.modifyMiscReinforceCheck, 0, wx.BOTTOM, 3)
        modifyMiscSizer.Add(self.modifyMiscRespawnCheck, 0, wx.BOTTOM, 3)
        modifyMiscSizer.Add(self.modifyMisc1Check, 0, wx.BOTTOM, 3)
        
        # ----
        
        modifyBottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        modifyBottomSizer.AddSizer(modifyMiscSizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)
        modifyBottomSizer.AddSizer(modifyTargetSizer, 0, wx.RIGHT | wx.EXPAND, 5)
        modifyBottomSizer.AddSizer(modifyGotoSizer, 0, wx.RIGHT | wx.EXPAND, 5)
        
        # ----
        
        modifyMainSizer.AddSizer(modifyTopSizer, 0, wx.BOTTOM, 5)
        modifyMainSizer.AddSizer(modifyBottomSizer, 1, wx.EXPAND)
        
        modifySizer.AddSizer(modifyAnimSizer, 1, wx.EXPAND)
        modifySizer.AddSizer(modifyMainSizer, 0)

        
        sbs5.AddSizer(modifySizer, 0, wx.ALL ^ wx.RIGHT, 5)
        #sbs5.Add(self.modifyRestCtrl, 0, wx.ALL | wx.EXPAND, 3)
        
        # ------------------------
        
        self.battleNotebook = wx.Notebook(self, -1)
        
        genWindow = wx.Window(self.battleNotebook, -1)
        mapWindow = wx.Window(self.battleNotebook, -1)
        zoneWindow = wx.Window(self.battleNotebook, -1)
        terrainWindow = wx.Window(self.battleNotebook, -1)
        #customWindow = wx.Window(self.battleNotebook, -1)
        
        self.addHelpText(genWindow,
            "Battle: General",
            "Edit various general properties of the battle, such as win condition, battle graphics, cutscenes, etc.")
        self.addHelpText(mapWindow,
            "Battle: Map",
            "Edit battle properties related to the map, such as the camera bounds and the region which, when entered, will retrigger the battle.")
        self.addHelpText(zoneWindow,
            "Battle: AI Zones",
            "Edit the AI zone information of this battle. Regions are zones of the map defined by 4 points used for AI decision making. Points are simply (X,Y) coords that serve as destinations.")
        self.addHelpText(terrainWindow,
            "Battle: Terrain",
            "Edit the terrain of the battle, including obstructions.\n\nNot yet implemented.")
        """self.addHelpText(customWindow,
            "Battle: Customize",
            "Edit other things related to making the battle unique, such as a custom win condition and events.\n\nNot yet implemented.")"""
            
        genWndSizer = wx.BoxSizer(wx.VERTICAL)
        mapWndSizer = wx.BoxSizer(wx.VERTICAL)
        zoneWndSizer = wx.BoxSizer(wx.VERTICAL)
        terrainWndSizer = wx.BoxSizer(wx.VERTICAL)
        #customWndSizer = wx.BoxSizer(wx.VERTICAL)
        
        # ---------

        winCondText = wx.StaticText(genWindow, -1, "Win Condition")
        battleGfxText = wx.StaticText(genWindow, -1, "Battle Graphics")
        
        sbs6winSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs6winLeftSizer = wx.BoxSizer(wx.VERTICAL)
        sbs6winRightSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.winAllRadio = wx.RadioButton(genWindow, wx.ID_ANY, " All enemies", style=wx.RB_GROUP)
        self.winBossRadio = wx.RadioButton(genWindow, wx.ID_ANY, " First enemy (boss)")
        self.winCustomRadio = wx.RadioButton(genWindow, wx.ID_ANY, " Custom condition")
        
        self.addHelpText(self.winAllRadio,
            "Win Condition\nAll Enemies",
            "Check this to allow the battle to be won by defeating all enemies.")
        self.addHelpText(self.winBossRadio,
            "Win Condition\nFirst Enemy is Boss",
            "Check this to allow the battle to be won by defeating the first enemy (boss).")
        
        sbs6winLeftSizer.Add(winCondText, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winLeftSizer.Add(self.winAllRadio, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winLeftSizer.Add(self.winBossRadio, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winLeftSizer.Add(self.winCustomRadio, 0, wx.LEFT | wx.BOTTOM, 3)
        
        self.defaultBattleGfxRadio = wx.RadioButton(genWindow, wx.ID_ANY, " Based on terrain", style=wx.RB_GROUP)
        self.overrideBattleGfxRadio = wx.RadioButton(genWindow, wx.ID_ANY, " Use one set for all tiles")
        self.battleGfxList = wx.ComboBox(genWindow, wx.ID_ANY)
        
        sbs6winRightSizer.Add(battleGfxText, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winRightSizer.Add(self.defaultBattleGfxRadio, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winRightSizer.Add(self.overrideBattleGfxRadio, 0, wx.LEFT | wx.BOTTOM, 3)
        sbs6winRightSizer.Add(self.battleGfxList, 0, wx.LEFT, 20)
        
        sbs6winSizer.AddSizer(sbs6winLeftSizer, 0, wx.EXPAND)
        sbs6winSizer.AddSizer(sbs6winRightSizer, 1, wx.EXPAND)

        # ----
        
        genPropText = wx.StaticText(genWindow, -1, "Other Properties")

        sbs6propSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.propRepeatableCheck = wx.CheckBox(genWindow, wx.ID_ANY, " Battle is repeatable by entering retrigger region")
        self.propMandatoryCheck = wx.CheckBox(genWindow, wx.ID_ANY, " Completion of battle not dependent upon outcome")
        self.propHalfEXPCheck = wx.CheckBox(genWindow, wx.ID_ANY, " Enemies give half EXP")
        
        sbs6propSizer.Add(genPropText, 0, wx.BOTTOM, 3)
        sbs6propSizer.Add(self.propRepeatableCheck, 0, wx.BOTTOM, 3)
        sbs6propSizer.Add(self.propMandatoryCheck, 0, wx.BOTTOM, 3)
        sbs6propSizer.Add(self.propHalfEXPCheck, 0, wx.BOTTOM, 3)
        
        # ----
        
        cutsceneText = wx.StaticText(genWindow, -1, "Cutscenes")
        beforeText = wx.StaticText(genWindow, -1, "Before")
        afterText = wx.StaticText(genWindow, -1, "After")
        
        sbs6cutsceneSizer = wx.BoxSizer(wx.VERTICAL)
        sbs6csFieldSizer = wx.GridBagSizer()
        
        self.cutsceneBeforeList = wx.ComboBox(genWindow, wx.ID_ANY, size=(200,-1))
        self.cutsceneAfterList = wx.ComboBox(genWindow, wx.ID_ANY, size=(200,-1))
                
        sbs6csFieldSizer.Add(beforeText, pos=(0,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, border=3)
        sbs6csFieldSizer.Add(self.cutsceneBeforeList, pos=(0,1), flag=wx.EXPAND)
        sbs6csFieldSizer.Add(afterText, pos=(1,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, border=3)
        sbs6csFieldSizer.Add(self.cutsceneAfterList, pos=(1,1), flag=wx.EXPAND)
        
        sbs6cutsceneSizer.Add(cutsceneText, 0, wx.BOTTOM | wx.RIGHT, 3)
        sbs6cutsceneSizer.AddSizer(sbs6csFieldSizer, 1, wx.EXPAND)
        
        # ----

        genWndSizer.AddSizer(sbs6winSizer, 0, wx.EXPAND | wx.ALL, 5)
        genWndSizer.AddSizer(sbs6propSizer, 0, wx.EXPAND | wx.ALL, 5)
        genWndSizer.AddSizer(sbs6cutsceneSizer, 0, wx.EXPAND | wx.ALL, 5)

        # --------
        
        mapText = wx.StaticText(mapWindow, -1, "Map")
        
        sbs6mapSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.mapList = wx.ComboBox(mapWindow, wx.ID_ANY, size=(225,-1))
        self.mapList.AppendItems([s.name for s in self.rom.data["maps"]])
        self.mapList.SetSelection(self.curBattle.map_index)
        
        self.addHelpText(self.mapList,
            "Battle Map List",
            "Choose the map on which this battle takes place from the choices in this list.\n\n(Note: The battle will only be triggered if you actually go to that map and the other conditions are met.)")
            
        #self.repeatableCheck = wx.CheckBox(mapWindow, wx.ID_ANY, " Repeatable")
        
        sbs6mapSizer.Add(mapText, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sbs6mapSizer.Add(self.mapList, 0, wx.RIGHT)
        #sbs6mapSizer.Add(self.repeatableCheck, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)

        # ----

        boundsText = wx.StaticText(mapWindow, -1, "Camera Bounds")
        triggerText = wx.StaticText(mapWindow, -1, "Retrigger Region")
        x1Text = wx.StaticText(mapWindow, -1, "X1")
        y1Text = wx.StaticText(mapWindow, -1, "Y1")
        x2Text = wx.StaticText(mapWindow, -1, "X2")
        y2Text = wx.StaticText(mapWindow, -1, "Y2")
        x1Text2 = wx.StaticText(mapWindow, -1, "X1")
        y1Text2 = wx.StaticText(mapWindow, -1, "Y1")
        x2Text2 = wx.StaticText(mapWindow, -1, "X2")
        y2Text2 = wx.StaticText(mapWindow, -1, "Y2")
        
        sbs6coordSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs6coordCol1Sizer = wx.BoxSizer(wx.VERTICAL)
        sbs6coordCol2Sizer = wx.BoxSizer(wx.VERTICAL)
        
        sbs6coordCol1FieldSizer = wx.GridBagSizer()
        sbs6coordCol2FieldSizer = wx.GridBagSizer()

        self.boundsXCtrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.boundsYCtrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.boundsX2Ctrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.boundsY2Ctrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)

        self.addHelpText(self.boundsXCtrl,
            "Camera Bounds: X1",
            "Set the top left corner X position of the map available in the battle.")
        self.addHelpText(self.boundsYCtrl,
            "Camera Bounds: Y1",
            "Set the top left corner Y position of the map available in the battle.")
        self.addHelpText(self.boundsX2Ctrl,
            "Camera Bounds: X2",
            "Set the bottom right corner X position of the map available in the battle.")
        self.addHelpText(self.boundsY2Ctrl,
            "Camera Bounds: Y2",
            "Set the bottom right corner Y position of the map available in the battle.")
            
        self.triggerXCtrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.triggerYCtrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.triggerX2Ctrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        self.triggerY2Ctrl = wx.SpinCtrl(mapWindow, wx.ID_ANY, size=(45,20), max=47)
        
        sbs6coordCol1FieldSizer.Add(x1Text, pos=(0,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol1FieldSizer.Add(self.boundsXCtrl, pos=(0,1), flag=wx.RIGHT, border=3)
        sbs6coordCol1FieldSizer.Add(y1Text, pos=(1,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol1FieldSizer.Add(self.boundsYCtrl, pos=(1,1), flag=wx.RIGHT, border=3)
        sbs6coordCol1FieldSizer.Add(x2Text, pos=(0,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol1FieldSizer.Add(self.boundsX2Ctrl, pos=(0,3), flag=wx.RIGHT, border=3)
        sbs6coordCol1FieldSizer.Add(y2Text, pos=(1,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol1FieldSizer.Add(self.boundsY2Ctrl, pos=(1,3), flag=wx.RIGHT, border=3)

        sbs6coordCol2FieldSizer.Add(x1Text2, pos=(0,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol2FieldSizer.Add(self.triggerXCtrl, pos=(0,1), flag=wx.RIGHT, border=3)
        sbs6coordCol2FieldSizer.Add(y1Text2, pos=(1,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol2FieldSizer.Add(self.triggerYCtrl, pos=(1,1), flag=wx.RIGHT, border=3)
        sbs6coordCol2FieldSizer.Add(x2Text2, pos=(0,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol2FieldSizer.Add(self.triggerX2Ctrl, pos=(0,3), flag=wx.RIGHT, border=3)
        sbs6coordCol2FieldSizer.Add(y2Text2, pos=(1,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6coordCol2FieldSizer.Add(self.triggerY2Ctrl, pos=(1,3), flag=wx.RIGHT, border=3)
        
        sbs6coordCol1Sizer.Add(boundsText, 0, wx.LEFT | wx.BOTTOM, border=3)
        sbs6coordCol1Sizer.AddSizer(sbs6coordCol1FieldSizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 3)
        sbs6coordCol2Sizer.Add(triggerText, 0, wx.LEFT | wx.BOTTOM, border=3)
        sbs6coordCol2Sizer.AddSizer(sbs6coordCol2FieldSizer, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM, 3)
        
        sbs6coordSizer.AddSizer(sbs6coordCol1Sizer, flag=wx.RIGHT, border=3)
        sbs6coordSizer.AddSizer(sbs6coordCol2Sizer, flag=wx.RIGHT, border=3)
        
        # ----

        mapWndSizer.AddSizer(sbs6mapSizer, 0, wx.EXPAND | wx.ALL, 5)
        mapWndSizer.AddSizer(sbs6coordSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --------

        regionText = wx.StaticText(zoneWindow, -1, "Regions")
        pointText = wx.StaticText(zoneWindow, -1, "Points")

        x1Text3 = wx.StaticText(zoneWindow, -1, "X1")
        y1Text3 = wx.StaticText(zoneWindow, -1, "Y1")
        x2Text3 = wx.StaticText(zoneWindow, -1, "X2")
        y2Text3 = wx.StaticText(zoneWindow, -1, "Y2")
        x3Text = wx.StaticText(zoneWindow, -1, "X3")
        y3Text = wx.StaticText(zoneWindow, -1, "Y3")
        x4Text = wx.StaticText(zoneWindow, -1, "X4")
        y4Text = wx.StaticText(zoneWindow, -1, "Y4")
        
        x1Text4 = wx.StaticText(zoneWindow, -1, "X ")
        y1Text4 = wx.StaticText(zoneWindow, -1, "Y ")
        
        sbs6zoneSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sbs6regionSizer = wx.BoxSizer(wx.VERTICAL)
        sbs6pointSizer = wx.BoxSizer(wx.VERTICAL)

        sbs6regionFieldSizer = wx.GridBagSizer()
        sbs6pointFieldSizer = wx.GridBagSizer()
        
        sbs6regionListSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs6regionButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs6regionRadioSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sbs6pointListSizer = wx.BoxSizer(wx.HORIZONTAL)
        sbs6pointButtonSizer = wx.BoxSizer(wx.HORIZONTAL)        
        
        self.regionList = wx.ComboBox(zoneWindow, wx.ID_ANY, size=(80,-1))
        self.pointList = wx.ComboBox(zoneWindow, wx.ID_ANY, size=(80,-1))
        
        self.regionType1Radio = wx.RadioButton(zoneWindow, wx.ID_ANY, " Type 1", style=wx.RB_GROUP)
        self.regionType2Radio = wx.RadioButton(zoneWindow, wx.ID_ANY, " Type 2")
        
        self.regionXCtrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionYCtrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionX2Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionY2Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionX3Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionY3Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionX4Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.regionY4Ctrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)        

        self.addHelpText(self.regionXCtrl,
            "Region Points: X1",
            "Set the point 1 X position of the currently selected AI region.")
        self.addHelpText(self.regionYCtrl,
            "Region Points: Y1",
            "Set the point 1 Y position of the currently selected AI region.")
        self.addHelpText(self.regionX2Ctrl,
            "Region Points: X2",
            "Set the point 2 X position of the currently selected AI region.")
        self.addHelpText(self.regionY2Ctrl,
            "Region Points: Y2",
            "Set the point 2 Y position of the currently selected AI region.")
        self.addHelpText(self.regionX3Ctrl,
            "Region Points: X3",
            "Set the point 3 X position of the currently selected AI region.")
        self.addHelpText(self.regionY3Ctrl,
            "Region Points: Y3",
            "Set the point 3 Y position of the currently selected AI region.")
        self.addHelpText(self.regionX4Ctrl,
            "Region Points: X4",
            "Set the point 4 X position of the currently selected AI region.")
        self.addHelpText(self.regionY4Ctrl,
            "Region Points: Y4",
            "Set the point 4 Y position of the currently selected AI region.")
            
        self.pointXCtrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        self.pointYCtrl = wx.SpinCtrl(zoneWindow, wx.ID_ANY, size=(45,20), max=47)
        
        #sbs6regionListSizer.Add(regionText, flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionListSizer.Add(self.regionList, 1, wx.EXPAND | wx.RIGHT, 3)
        sbs6pointListSizer.Add(self.pointList, 1, wx.EXPAND | wx.RIGHT, 3)
        
        self.addRegionButton = wx.Button(zoneWindow, wx.ID_ANY, "New Region", size=(70,20))
        self.deleteRegionButton = wx.Button(zoneWindow, wx.ID_ANY, "Delete", size=(50,20))
        
        self.addPointButton = wx.Button(zoneWindow, wx.ID_ANY, "New Point", size=(70,20))
        self.deletePointButton = wx.Button(zoneWindow, wx.ID_ANY, "Delete", size=(50,20))
        
        sbs6regionButtonSizer.Add(self.addRegionButton, 0, wx.ALIGN_CENTER_VERTICAL)
        sbs6regionButtonSizer.Add(self.deleteRegionButton, 0, wx.ALIGN_CENTER_VERTICAL)
        
        sbs6pointButtonSizer.Add(self.addPointButton, 0, wx.ALIGN_CENTER_VERTICAL)
        sbs6pointButtonSizer.Add(self.deletePointButton, 0, wx.ALIGN_CENTER_VERTICAL)        
        
        sbs6regionRadioSizer.Add(self.regionType1Radio, 1, wx.ALIGN_CENTER)
        sbs6regionRadioSizer.Add(self.regionType2Radio, 1, wx.ALIGN_CENTER)
        
        sbs6regionFieldSizer.Add(x1Text3, pos=(0,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionXCtrl, pos=(0,1), flag=wx.RIGHT, border=3)
        sbs6regionFieldSizer.Add(y1Text3, pos=(1,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=3)
        sbs6regionFieldSizer.Add(self.regionYCtrl, pos=(1,1), flag=wx.RIGHT | wx.BOTTOM, border=3)
        sbs6regionFieldSizer.Add(x4Text, pos=(0,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionX4Ctrl, pos=(0,3), flag=wx.RIGHT, border=3)
        sbs6regionFieldSizer.Add(y4Text, pos=(1,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=3)
        sbs6regionFieldSizer.Add(self.regionY4Ctrl, pos=(1,3), flag=wx.RIGHT | wx.BOTTOM, border=3)
        sbs6regionFieldSizer.Add(x2Text3, pos=(2,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionX2Ctrl, pos=(2,1), flag=wx.RIGHT, border=3)
        sbs6regionFieldSizer.Add(y2Text3, pos=(3,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionY2Ctrl, pos=(3,1), flag=wx.RIGHT, border=3)
        sbs6regionFieldSizer.Add(x3Text, pos=(2,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionX3Ctrl, pos=(2,3), flag=wx.RIGHT, border=3)
        sbs6regionFieldSizer.Add(y3Text, pos=(3,2), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6regionFieldSizer.Add(self.regionY3Ctrl, pos=(3,3), flag=wx.RIGHT, border=3)        

        sbs6pointFieldSizer.Add(x1Text4, pos=(0,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6pointFieldSizer.Add(self.pointXCtrl, pos=(0,1), flag=wx.RIGHT, border=3)
        sbs6pointFieldSizer.Add(y1Text4, pos=(1,0), flag=wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, border=3)
        sbs6pointFieldSizer.Add(self.pointYCtrl, pos=(1,1), flag=wx.RIGHT, border=3)

        sbs6regionSizer.Add(regionText, 0, wx.EXPAND | wx.ALL, 5)
        sbs6regionSizer.AddSizer(sbs6regionListSizer, 1, wx.EXPAND)
        sbs6regionSizer.AddSizer(sbs6regionButtonSizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sbs6regionSizer.AddSizer(sbs6regionRadioSizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.BOTTOM, 5)
        sbs6regionSizer.AddSizer(sbs6regionFieldSizer, 0)

        sbs6pointSizer.Add(pointText, 0, wx.EXPAND | wx.ALL, 5)
        sbs6pointSizer.AddSizer(sbs6pointListSizer, 1, wx.EXPAND)
        sbs6pointSizer.AddSizer(sbs6pointButtonSizer, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sbs6pointSizer.AddSizer(sbs6pointFieldSizer, 0)
        
        sbs6zoneSizer.AddSizer(sbs6regionSizer, flag=wx.RIGHT, border=10)
        sbs6zoneSizer.AddSizer(sbs6pointSizer, flag=wx.RIGHT)
        
        # ----
        
        zoneWndSizer.AddSizer(sbs6zoneSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --------
        #tgText = wx.StaticText(terrainWindow, -1, "Terrain Generation")
        
        sbs6tgSizer = wx.BoxSizer(wx.VERTICAL)
        
        #self.autoGenerateTerrainRadio = wx.RadioButton(terrainWindow, wx.ID_ANY, "Automatic, based on map tiles
        
        #tgNIYText = wx.StaticText(terrainWindow, -1, "Not yet implemented.")
        
        diffColors = [
            wx.Colour(255,255,255),     # 0 - white
            wx.Colour(192,255,192),     # 1 - white
            wx.Colour(128,255,128),     # 2 - green
            wx.Colour(255,255,128),     # 3 - yellow
            wx.Colour(255,192,128),     # 4 - orange
            wx.Colour(255,128,128),     # 5 - red
            wx.Colour(240,112,112),     # 6 - red
            wx.Colour(224,96,96),     # 7 - red
            wx.Colour(208,80,80),     # 8 - red
            wx.Colour(192,64,64),     # 9 - red
            wx.Colour(176,48,48),     # 10 - red
            wx.Colour(160,32,32),     # 11 - red
            wx.Colour(128,16,16),     # 12 - red
            wx.Colour(96,0,0),     # 13 - red
            wx.Colour(64,0,0),     # 14 - red
            wx.Colour(64,64,64),     # 15 - gray, unmovable
                ]
                
        self.terrainInfoGrid = grid.Grid(terrainWindow, wx.ID_ANY) #, size=(340,400))
        self.terrainInfoGrid.SetRowLabelSize(45)
        self.terrainInfoGrid.SetColLabelSize(20)
        self.terrainInfoGrid.CreateGrid(13,9)
        self.terrainInfoGrid.SetMargins(0,0)
        
        #w,h = self.terrainInfoGrid.GetSize()
        #self.terrainInfoGrid.SetSize((w+15,h))
        
        movetypes = ["Free", "Foot", "Horse", "Fast", "Tires", "Fly", "Float", "Water", "Foot2", "Horse2", "Fast2", "Foot3", "Foot4"] 
        terraintypes = ["Low Sky", "Plains", "Road", "Grass", "Forest", "Hill", "Desert", "High Sky", "Water", "Inaccessible"]
        
        gridCenterAttr = grid.GridCellAttr()
        gridCenterAttr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        
        for i in range(13):
            self.terrainInfoGrid.SetRowLabelValue(i, movetypes[i])
            
        for i in range(9):
            
            self.terrainInfoGrid.SetColLabelValue(i, str(i))
            self.terrainInfoGrid.SetColSize(i, 20)
            self.terrainInfoGrid.SetColAttr(i, gridCenterAttr)
        
        for x in range(9):
            
            for y in range(13):
                
                mti = self.rom.data["movetypes"][y][x]
                le, diff = int(mti[0], 16), int(mti[1], 16)
                #self.terrainInfoGrid.SetCellAlignment(y, x, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
                
                col = diffColors[diff]
                    
                self.terrainInfoGrid.SetCellBackgroundColour(y, x, col)
                if le < 15:
                    self.terrainInfoGrid.SetCellValue(y, x, str(le*15))
        
        bmpXPos = 7
        bmpYPos = 7
        
        bmpXPos += self.terrainInfoGrid.GetRowLabelSize()
        
        for i,bmp in enumerate(icons):
            
            sb = wx.StaticBitmap(terrainWindow, wx.ID_ANY, pos=(bmpXPos,bmpYPos))
            sb.SetBitmap(bmp)
            sb.SetToolTipString(terraintypes[i])
            sb.context = i
            wx.EVT_LEFT_DOWN(sb, self.OnSelectTerrainType)            
            bmpXPos += self.terrainInfoGrid.GetColLabelSize()

        bmpXPos -= 13
        bmpYPos += 40
        
        wx.StaticText(terrainWindow, wx.ID_ANY, "^ Click", pos=(bmpXPos, bmpYPos))
        
        bmpYPos += 20
        
        self.curTerrainBmp = wx.StaticBitmap(terrainWindow, wx.ID_ANY, pos=(bmpXPos,bmpYPos))
        self.curTerrainBmp.SetBitmap(icons[0])
        
        self.curTerrainType = 0
        
        #fnt = self.terrainInfoGrid.GetCellFont(0,0)
        #fnt.SetWeight(wx.BOLD)
        #leftColAttr.SetFont(fnt)
        
        #sbs6tgSizer.Add(tgText, 0, wx.BOTTOM, 3)
        sbs6tgSizer.Add(self.terrainInfoGrid, 0, wx.TOP, 18)
        
        # ----
        
        terrainWndSizer.AddSizer(sbs6tgSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        # --------
        
        #sbs6customSizer = wx.BoxSizer(wx.VERTICAL)
        
        #customNIYText = wx.StaticText(customWindow, -1, "Not yet implemented.")
        
        #sbs6customSizer.Add(customNIYText, 0, wx.BOTTOM, 3)
        
        # ----
        
        #customWndSizer.AddSizer(sbs6customSizer, 0, wx.EXPAND | wx.ALL, 5)

        # --------
        
        #self.battleCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(150,60), style=wx.TE_MULTILINE)

        # --------
        
        self.mapViewer = window.BattleMapViewer(self, wx.ID_ANY, self)
        self.mapViewer.init(None, None)
        self.mapViewer.mapViewPanel.drawFlags = False
        
        # ----

        genWindow.SetSizer(genWndSizer)
        genWndSizer.Layout()
        mapWindow.SetSizer(mapWndSizer)
        mapWndSizer.Layout()
        zoneWindow.SetSizer(zoneWndSizer)
        zoneWndSizer.Layout()
        terrainWindow.SetSizer(terrainWndSizer)
        terrainWndSizer.Layout()
        #customWindow.SetSizer(customWndSizer)
        #customWndSizer.Layout()
        
        self.battleNotebook.AddPage(genWindow, "General")
        self.battleNotebook.AddPage(mapWindow, "Map")
        self.battleNotebook.AddPage(zoneWindow, "AI Zones")
        self.battleNotebook.AddPage(terrainWindow, "Terrain")
        #self.battleNotebook.AddPage(customWindow, "Customize")
        
        sbs6.Add(self.battleNotebook, 1, wx.EXPAND)
        
        # ------------------------
        
        #self.symbolsBox = rompanel.HexBox(self, wx.ID_ANY, size=(0, 42), style=wx.TE_MULTILINE)
        
        #sbs7.Add(self.symbolsBox, 1, wx.EXPAND | wx.ALL, 10)
        
        # -----------------------

        leftSizer = wx.BoxSizer(wx.VERTICAL)
        
        #leftSizer.AddSizer(sbs1, 0, wx.EXPAND)
        leftSizer.AddSizer(sbs2, 1, wx.EXPAND)
        
        #self.sizer.Add(inst, pos=(0,0), span=(1,2), flag=wx.BOTTOM, border=10)
        self.sizer.AddSizer(leftSizer, pos=(0,0), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs6, pos=(0,1), flag=wx.EXPAND)
        self.sizer.AddSizer(sbs5, pos=(1,0), span=(1,2), flag=wx.EXPAND)
        self.sizer.Add(self.mapViewer, pos=(0,2), span=(3,1))
        #self.sizer.AddSizer(sbs7, pos=(3,0), span=(1,2), flag=wx.EXPAND)
        
        self.sizer.Layout()
        
        self.changeBattle(0)
        
        self.updateAnimPanels()
        self.setAnimPanelSelected(True)
        self.refreshAnimPanels()
        
        self.disableUnimplemented()
        
        # ------------------------
        
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, self.battleNotebook.GetId(), self.OnChangePage)
        
        # ----------
        
        #wx.EVT_COMBOBOX(self, self.battleList.GetId(), self.OnSelectBattle)
        
        wx.EVT_BUTTON(self, self.addMonsterButton.GetId(), self.OnAddMonsterButton)
        wx.EVT_BUTTON(self, self.addForceButton.GetId(), self.OnAddForceButton)
        wx.EVT_BUTTON(self, self.addNPCButton.GetId(), self.OnAddNPCButton)
        
        wx.EVT_RADIOBUTTON(self, self.defaultBattleGfxRadio.GetId(), self.OnSelectGraphicsDefault)
        wx.EVT_RADIOBUTTON(self, self.overrideBattleGfxRadio.GetId(), self.OnSelectGraphicsOverride)
        
        wx.EVT_SPINCTRL(self, self.modifyList.GetId(), self.OnChangeUnitIdx)
        wx.EVT_SPINCTRL(self, self.modifyXCtrl.GetId(), self.OnChangeUnitX)
        wx.EVT_SPINCTRL(self, self.modifyYCtrl.GetId(), self.OnChangeUnitY)
        wx.EVT_SPINCTRL(self, self.modifyAICtrl.GetId(), self.OnChangeUnitAI)

        wx.EVT_BUTTON(self, self.modifyDeleteButton.GetId(), self.OnDeleteUnitButton)
        
        wx.EVT_COMBOBOX(self, self.mapList.GetId(), self.OnSelectBattleMap)
        
        wx.EVT_RADIOBUTTON(self, self.winAllRadio.GetId(), self.OnSelectWinAll)
        wx.EVT_RADIOBUTTON(self, self.winBossRadio.GetId(), self.OnSelectWinBoss)
        
        wx.EVT_SPINCTRL(self, self.boundsXCtrl.GetId(), self.OnChangeBoundsX)
        wx.EVT_SPINCTRL(self, self.boundsYCtrl.GetId(), self.OnChangeBoundsY)
        wx.EVT_SPINCTRL(self, self.boundsX2Ctrl.GetId(), self.OnChangeBoundsX2)
        wx.EVT_SPINCTRL(self, self.boundsY2Ctrl.GetId(), self.OnChangeBoundsY2)
        
        # ----
        
        wx.EVT_COMBOBOX(self, self.regionList.GetId(), self.OnSelectRegion)
        wx.EVT_COMBOBOX(self, self.pointList.GetId(), self.OnSelectPoint)

        wx.EVT_RADIOBUTTON(self, self.regionType1Radio.GetId(), self.OnSelectRegionType1)
        wx.EVT_RADIOBUTTON(self, self.regionType2Radio.GetId(), self.OnSelectRegionType2)
        
        wx.EVT_SPINCTRL(self, self.regionXCtrl.GetId(), self.OnChangeRegionX)
        wx.EVT_SPINCTRL(self, self.regionYCtrl.GetId(), self.OnChangeRegionY)
        wx.EVT_SPINCTRL(self, self.regionX2Ctrl.GetId(), self.OnChangeRegionX2)
        wx.EVT_SPINCTRL(self, self.regionY2Ctrl.GetId(), self.OnChangeRegionY2)
        wx.EVT_SPINCTRL(self, self.regionX3Ctrl.GetId(), self.OnChangeRegionX3)
        wx.EVT_SPINCTRL(self, self.regionY3Ctrl.GetId(), self.OnChangeRegionY3)
        wx.EVT_SPINCTRL(self, self.regionX4Ctrl.GetId(), self.OnChangeRegionX4)
        wx.EVT_SPINCTRL(self, self.regionY4Ctrl.GetId(), self.OnChangeRegionY4)

        wx.EVT_SPINCTRL(self, self.pointXCtrl.GetId(), self.OnChangePointX)
        wx.EVT_SPINCTRL(self, self.pointYCtrl.GetId(), self.OnChangePointY)

        # ----
        
        wx.EVT_RADIOBUTTON(self, self.modifyFacingUpRadio.GetId(), self.OnSelectFacingUp)
        wx.EVT_RADIOBUTTON(self, self.modifyFacingLeftRadio.GetId(), self.OnSelectFacingLeft)
        wx.EVT_RADIOBUTTON(self, self.modifyFacingRightRadio.GetId(), self.OnSelectFacingRight)
        wx.EVT_RADIOBUTTON(self, self.modifyFacingDownRadio.GetId(), self.OnSelectFacingDown)
        
        wx.EVT_RADIOBUTTON(self, self.orderSet1Radio.GetId(), self.OnSelectOrderSet)
        wx.EVT_RADIOBUTTON(self, self.orderSet2Radio.GetId(), self.OnSelectOrderSet)
        
        wx.EVT_CHECKBOX(self, self.targetCheck.GetId(), self.OnToggleTriggerRegion)
        wx.EVT_CHECKBOX(self, self.gotoCheck.GetId(), self.OnToggleGotoType)
        
        wx.EVT_COMBOBOX(self, self.targetList.GetId(), self.OnSelectTargetEntry)
        
        wx.EVT_RADIOBUTTON(self, self.gotoForceRadio.GetId(), self.OnSelectGotoForce)
        wx.EVT_RADIOBUTTON(self, self.gotoPointRadio.GetId(), self.OnSelectGotoPoint)
        wx.EVT_RADIOBUTTON(self, self.gotoAllyRadio.GetId(), self.OnSelectGotoAlly)
        wx.EVT_COMBOBOX(self, self.gotoList.GetId(), self.OnSelectGotoEntry)

        wx.EVT_CHECKBOX(self, self.modifyMiscReinforceCheck.GetId(), self.OnToggleReinforce)
        wx.EVT_CHECKBOX(self, self.modifyMiscRespawnCheck.GetId(), self.OnToggleRespawn)
        wx.EVT_CHECKBOX(self, self.modifyMisc1Check.GetId(), self.OnToggleMisc1)
        
        #wx.EVT_BUTTON(self, wx.ID_ANY, self.OnChangeAnim)
        #wx.EVT_BUTTON(self, self.switchButton.GetId(), self.OnSwitchFrame)
        
        wx.EVT_TIMER(self, self.timer.GetId(), self.OnAnimNext)
        
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
        pass
        
        #for p in range(16):
        #    self.colorPanels[p].SetBackgroundColour(self.palette.colors[p])
        #    self.colorPanels[p].Refresh()
        #self.selectedColorLeft.SetBackgroundColour(self.palette.colors[self.color_left])
        #self.selectedColorRight.SetBackgroundColour(self.palette.colors[self.color_right])
        #self.selectedColorLeft.Refresh()
        #self.selectedColorRight.Refresh()
    
    def OnSelectBattle(self, evt):
        self.changeBattle(evt.GetSelection())
        
    def OnAnimNext(self, evt):
        
        self.animFrame ^= 1
        self.refreshAnimPanels()
        self.mapViewer.refreshMapView()
    
    def OnClickPanel(self, evt):
        obj = evt.GetEventObject()
        self.changeUnit(obj.context, obj.num)

    def OnAddMonsterButton(self, evt):
        u = data.BattleUnit()
        u.init(64, 0, 0)
        self.curBattle.enemies.append(u)
        self.updateAnimPanels()
        self.updateModifyEntity()
        self.modify()
        
    def OnAddForceButton(self, evt):
        u = data.BattleUnit()
        u.init(len(self.curBattle.force), 0, 0)
        self.curBattle.force.append(u)
        self.updateAnimPanels()
        self.updateModifyEntity()
        self.modify()
        
    def OnAddNPCButton(self, evt):
        u = data.BattleNPC()
        u.init(0, 0, 0)
        self.curBattle.npcs.append(u)
        self.updateAnimPanels()
        self.updateModifyEntity()
        self.modify()        
    
    def OnDeleteUnitButton(self, evt):
        
        del self.allGroupData[self.curUnitContext][self.curUnitIdx]
        
        self.curUnitIdx = min(self.curUnitIdx, len(self.allGroupData[self.curUnitContext])-1)
        
        if self.curUnitIdx == -1:
            self.curUnitContext = 0
            self.curUnitIdx = 0
            
        self.changeUnit(self.curUnitContext, self.curUnitIdx)
        
        self.updateAnimPanels()
        self.modify()
        
    # ----

    def OnSelectFacingUp(self, evt):
        self.curUnit.facing = 1
        self.updateAnimPanels()
        self.modify()
    def OnSelectFacingLeft(self, evt):
        self.curUnit.facing = 2
        self.updateAnimPanels()
        self.modify()
    def OnSelectFacingRight(self, evt):
        self.curUnit.facing = 0
        self.updateAnimPanels()
        self.modify()
    def OnSelectFacingDown(self, evt):
        self.curUnit.facing = 3
        self.updateAnimPanels()
        self.modify()
        
    def OnChangeUnitIdx(self, evt):
        
        
        val = evt.GetSelection()
        self.changeUnitIdx(val)
        
        #print `val`
        
        
    
    def changeUnitIdx(self, num):

        if self.curUnitContext == 2:
            self.curUnit.idx = num
        else:
            self.curUnit.idx = num+64
        self.modifyList.SetValue(num)
        
        self.updateAnimPanels()
        
        self.modify()
        
    def OnChangeUnitX(self, evt):
        
        val = evt.GetSelection()
        self.curUnit.x = val
        
        self.modify()
        
    def OnChangeUnitY(self, evt):
        
        val = evt.GetSelection()
        self.curUnit.y = val
        
        self.modify()
        
    def OnChangeUnitAI(self, evt):
        
        val = evt.GetSelection()
        self.curUnit.ai[0] = val

        self.modify()

    def OnSelectOrderSet(self, evt):
        
        if evt.GetEventObject() == self.orderSet1Radio:
            self.curOrderSet = 0
        else:
            self.curOrderSet = 1
            
        self.updateModifyEntity()
        
    def OnToggleTriggerRegion(self, evt):
        
        self.curUnit.ai[self.curOrderSet+1][1] = 15 - (evt.GetSelection() * 15)
        self.updateTargetList()
        self.updateModifyEntity()
        self.modify()
        
    def OnToggleGotoType(self, evt):
        
        self.curUnit.ai[self.curOrderSet+1][0] = 255 - (evt.GetSelection() * 255)
        self.updateGotoList()
        self.updateModifyEntity()
        self.modify()

    def OnSelectTargetEntry(self, evt):

        self.curUnit.ai[self.curOrderSet+1][1] = evt.GetSelection()
        self.modify()
        
    def OnSelectGotoForce(self, evt):
        
        battle = self.curBattle
        self.curUnit.ai[self.curOrderSet+1][0] = 0
        
        self.updateGotoList()
        
        self.modify()
        
    def OnSelectGotoPoint(self, evt):
        
        battle = self.curBattle
        self.curUnit.ai[self.curOrderSet+1][0] = 64
        
        self.updateGotoList()
        
        self.modify()

    def OnSelectGotoAlly(self, evt):
        
        battle = self.curBattle
        self.curUnit.ai[self.curOrderSet+1][0] = 128
        
        self.updateGotoList()
        
        self.modify()
    
    def OnSelectGotoEntry(self, evt):
        
        type = int(self.curUnit.ai[self.curOrderSet+1][0] / 64)
        
        idx = evt.GetSelection()
        
        if idx > self.curUnitIdx and type == 2:
            idx += 1
            
        self.curUnit.ai[self.curOrderSet+1][0] = type*64 + idx
        self.modify()

    def OnToggleReinforce(self, evt):
        self.curUnit.reinforce = bool(evt.GetSelection())
        self.modify()
    def OnToggleRespawn(self, evt):
        self.curUnit.respawn = bool(evt.GetSelection())
        self.modify()
    def OnToggleMisc1(self, evt):
        self.curUnit.misc1 = bool(evt.GetSelection())
        self.modify()
        
    # --------

    def OnSelectWinAll(self, evt):
        self.curBattle.boss = False
        self.modify()
    def OnSelectWinBoss(self, evt):
        self.curBattle.boss = True
        self.modify()
    
    # ----

    def OnSelectBattleMap(self, evt):
        self.curBattle.map_index = evt.GetSelection()
        self.modify()
    
    def OnChangeBoundsX(self, evt):     
        self.curBattle.map_x1 = evt.GetSelection()
        self.modify()
    def OnChangeBoundsY(self, evt):     
        self.curBattle.map_y1 = evt.GetSelection()
        self.modify()
    def OnChangeBoundsX2(self, evt):   
        self.curBattle.map_x2 = evt.GetSelection()
        self.modify()
    def OnChangeBoundsY2(self, evt):    
        self.curBattle.map_y2 = evt.GetSelection()
        self.modify()

    # ----
    
    def OnSelectRegion(self, evt):
        self.changeRegion(evt.GetSelection())
    def OnSelectPoint(self, evt):
        self.changePoint(evt.GetSelection())

    def changeRegion(self, num):
        
        region = self.curBattle.regions[num]
        
        self.curRegionIdx = num
        self.regionList.SetSelection(num)
        
        [self.regionType1Radio, self.regionType2Radio][4-region.type].SetValue(True)
        
        self.regionXCtrl.SetValue(region.p1[0])
        self.regionYCtrl.SetValue(region.p1[1])
        self.regionX2Ctrl.SetValue(region.p2[0])
        self.regionY2Ctrl.SetValue(region.p2[1])
        self.regionX3Ctrl.SetValue(region.p3[0])
        self.regionY3Ctrl.SetValue(region.p3[1])
        self.regionX4Ctrl.SetValue(region.p4[0])
        self.regionY4Ctrl.SetValue(region.p4[1])
        
        self.mapViewer.refreshMapView()

    def changePoint(self, num):
        
        point = self.curBattle.points[num]
        
        self.curPointIdx = num
        self.pointList.SetSelection(num)
        
        self.pointXCtrl.SetValue(point[0])
        self.pointYCtrl.SetValue(point[1])
        
        self.mapViewer.refreshMapView()
        
    def OnSelectRegionType1(self, evt):
        self.curBattle.regions[self.curRegionIdx].type = 4
        self.modify()
    def OnSelectRegionType2(self, evt):
        self.curBattle.regions[self.curRegionIdx].type = 3
        self.modify()        
        
    def OnChangeRegionX(self, evt):
        self.changeRegionX(evt.GetSelection())
    def changeRegionX(self, num):
        self.curBattle.regions[self.curRegionIdx].p1[0] = num
        self.regionXCtrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionY(self, evt):
        self.changeRegionY(evt.GetSelection())
    def changeRegionY(self, num):
        self.curBattle.regions[self.curRegionIdx].p1[1] = num
        self.regionYCtrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionX2(self, evt):
        self.changeRegionX2(evt.GetSelection())
    def changeRegionX2(self, num):
        self.curBattle.regions[self.curRegionIdx].p2[0] = num
        self.regionX2Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionY2(self, evt):
        self.changeRegionY2(evt.GetSelection())
    def changeRegionY2(self, num):
        self.curBattle.regions[self.curRegionIdx].p2[1] = num
        self.regionY2Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionX3(self, evt):
        self.changeRegionX3(evt.GetSelection())
    def changeRegionX3(self, num):
        self.curBattle.regions[self.curRegionIdx].p3[0] = num
        self.regionX3Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionY3(self, evt):
        self.changeRegionY3(evt.GetSelection())
    def changeRegionY3(self, num):
        self.curBattle.regions[self.curRegionIdx].p3[1] = num
        self.regionY3Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionX4(self, evt):
        self.changeRegionX4(evt.GetSelection())
    def changeRegionX4(self, num):
        self.curBattle.regions[self.curRegionIdx].p4[0] = num
        self.regionX4Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangeRegionY4(self, evt):
        self.changeRegionY4(evt.GetSelection())
    def changeRegionY4(self, num):
        self.curBattle.regions[self.curRegionIdx].p4[1] = num
        self.regionY4Ctrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()

    def OnChangePointX(self, evt):
        self.changePointX(evt.GetSelection())
    def changePointX(self, num):
        self.curBattle.points[self.curPointIdx][0] = num
        self.pointYCtrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()
    def OnChangePointY(self, evt):
        self.changePointY(evt.GetSelection())
    def changePointY(self, num):
        self.curBattle.points[self.curPointIdx][1] = num
        self.pointYCtrl.SetValue(num)
        self.modify()
        self.mapViewer.refreshMapView()

    # ----
    
    def OnSelectTerrainType(self, evt):
        context = evt.GetEventObject().context
        self.changeTerrainType(context)
    
    def changeTerrainType(self, num):
        self.curTerrainBmp.SetBitmap(icons[num])
        if num == len(icons)-1:
            self.curTerrainType = 255
        else:
            self.curTerrainType = num
            
    # ----
    
    def OnSelectGraphicsDefault(self, evt):
        
        self.updateGeneralWindow()
        
    def OnSelectGraphicsOverride(self, evt):
        
        self.updateGeneralWindow()
        
    # --------

    def changeBattle(self, num):
        
        self.curBattleIdx = num
        
        if not self.rom.data["battles"][num].loaded:
            self.rom.getBattles(num, num)
            
        battle = self.curBattle
        
        self.updateModifiedIndicator(battle.modified)
        
        self.setAnimPanelSelected(False)
        
        self.updateAnimPanels()
        
        self.changeUnit(0, 0)
        
        self.curRegionIdx = 0
        self.curPointIdx = 0
        
        self.regionList.Clear()
        self.regionList.AppendItems(["Region %i" % i for i in range(len(battle.regions))])
        self.regionList.SetSelection(0)
        
        self.pointList.Clear()
        self.pointList.AppendItems(["Point %i" % i for i in range(len(battle.points))])
        self.pointList.SetSelection(0)
        
        self.updateGeneralWindow()
        self.updateMapWindow()
        self.updateZoneWindow()
        
        num = battle.map_index
        if not self.rom.data["maps"][num].loaded:
            self.rom.getMaps(num, num)
        
        battleMap = self.rom.data["maps"][num]
        self.mapViewer.changeMap(battleMap, None)
        self.mapViewer.setViewPos(battle.map_x1 * 24, battle.map_y1 * 24)
        
        #self.battleCtrl.SetValue(hex(self.rom.tables["battles"][self.curBattleIdx]) + "\n" + self.curBattle.raw_bytes)
        
    def changeUnit(self, con, idx):
        
        self.setAnimPanelSelected(False)
        
        self.curUnitContext = con
        self.curUnitIdx = idx
        self.curOrderSet = 0
        
        offsets = [0, 172, 0, 64]
        
        unit = self.curUnit
        battle = self.curBattle
        
        #if self.curSelection >= len(combatants[self.curContext]):
        #    self.curSelection = len(combatants[self.curContext])
        #    combatants[self.curContext].append([offsets[self.curContext], 0, 0])
        #    self.updateAnimPanels()
        
        self.setAnimPanelSelected(True)
        
        self.refreshAnimPanels()
        
        self.orderSet1Radio.SetValue(True)
        
        if self.curUnitContext != 2:
            self.updateTargetList()
            self.updateGotoList()
            
        self.updateModifyEntity()
    
        self.mapViewer.centerViewPos((battle.map_x1 + unit.x) * 24 + 12, (battle.map_y1 + unit.y) * 24 + 12)
        self.mapViewer.refreshMapView()
        #print `combatants[self.curContext][self.curSelection][3]`
        
        #print `unit`

    def updateTargetList(self):
        
        battle = self.curBattle
        
        self.targetList.Clear()        
        self.targetList.AppendItems(["Region %i" % i for i in range(len(battle.regions))])
        self.targetList.SetSelection(0)
        
    def updateGotoList(self):
        
        battle = self.curBattle
        
        self.gotoList.Clear()
        
        type = self.curUnit.ai[self.curOrderSet+1][0] / 64
        
        text = ["Force Member %i", "Point %i", "Monster %i", ""][type]
        num = [len(battle.force), len(battle.points), len(battle.enemies), 0][type]
        items = [text % i for i in range(num)]
    
        if type == 2:
            items.pop(self.curUnitIdx)
            
        self.gotoList.AppendItems(items)
        
        self.gotoList.SetSelection(0)

        
    def setAnimPanelSelected(self, flag):
        
        self.curPanel.bg = [None, 17][flag]
        
    def changeAnim(self, num):
        
        self.curAnim = num
        self.timer.Start(self.animDelays[num])

    def updateAnimPanels(self):

        sprites = self.rom.data["sprites"]
        
        combatants = self.allGroupData

        for con in range(len(combatants)):
            
            curPanels = self.allGroupPanels[con]
            curData = self.allGroupData[con]
            curSizer = self.allGroupSizers[con]
            
            for p in range(len(curPanels)):
                if not curPanels[p].used:
                    previousLen = p
                    break
                    
            curSizer.Clear()
            curSizer.SetRows(len(curData)/5 + 1)
            #curSizer.SetRows(1)
            
            for p, ap in enumerate(curPanels):
                
                if p >= len(curData):
                    ap.used = False
                    ap.Hide()
                else:
                    ap.used = True
                    ap.Show()
                    curSizer.Add(ap, 0)
                
                if ap.used:
                    
                    idx = curData[p].idx * 3
                    if not sprites[idx].loaded:
                        self.rom.getSprites(idx,idx+2)
                    
                    if con == 2:
                        ap.sprite = sprites[idx+[1,0,1,2][curData[p].facing]]
                        ap.flip = curData[p].facing == 0
                    else:
                        ap.sprite = sprites[idx+2]
                        ap.flip = False
                        
                    ap.context = con
                    ap.num = p
                
                else:
                    
                    ap.sprite = None
                    ap.refreshSprite([])

        self.scrollWnd.SetupScrolling(scroll_x = False)
        self.scrollWnd.SetScrollRate(0,12)
        
        self.scrollWnd.Layout()
        
            
    def refreshAnimPanels(self):
        
        panels = self.allGroupPanels
        
        for con in range(len(panels)):
            
            for i,ap in enumerate(panels[con]):
                
                if ap.sprite:
                    if self.animFrame == 0:
                        ap.refreshSprite(ap.sprite.pixels)
                    else:
                        ap.refreshSprite(ap.sprite.pixels2)
                else:
                    ap.refreshSprite([])
                
                ap.Refresh()
            
        sprite = self.curPanel.sprite
        self.modifyAnimPanel.flip = self.curPanel.flip
        
        if self.animFrame == 0:
            self.modifyAnimPanel.refreshSprite(sprite.pixels)
        else:
            self.modifyAnimPanel.refreshSprite(sprite.pixels2)
        
        self.modifyAnimPanel.Refresh()
        
    def updateModifyEntity(self):
        
        unit = self.curUnit
        battle = self.curBattle
        
        hasAI = (self.curUnitContext == 0)
        isNPC = (self.curUnitContext == 2)
        
        if isNPC:
            
            self.modifyList.SetRange(0,239)
            self.modifyList.SetValue(unit.idx)
                
            [self.modifyFacingRightRadio, self.modifyFacingUpRadio, self.modifyFacingLeftRadio, self.modifyFacingDownRadio][self.curUnit.facing].SetValue(True)
            
        else:
            
            self.modifyList.SetValue(unit.idx-64)
            self.modifyList.SetRange(0,173)
        
        self.modifyFacingUpRadio.Enable(isNPC)
        self.modifyFacingLeftRadio.Enable(isNPC)
        self.modifyFacingRightRadio.Enable(isNPC)
        self.modifyFacingDownRadio.Enable(isNPC)
        
        self.modifyXCtrl.SetValue(unit.x)
        self.modifyYCtrl.SetValue(unit.y)
        #self.modifyRestCtrl.SetValue(unit.raw_bytes)
        
        if isNPC or len(self.allGroupData[self.curUnitContext]) > 1:
            self.modifyDeleteButton.Enable(True)
        else:
            self.modifyDeleteButton.Enable(False)
            
        if hasAI:
            self.modifyAICtrl.SetValue(unit.ai[0])
            
        # ----
        
        [self.orderSet1Radio, self.orderSet2Radio][self.curOrderSet].SetValue(True)
        
        if hasAI:
            
            order = unit.ai[self.curOrderSet+1]
            orderType = int(order[0] / 64)
            orderRegion = order[1]
            
        else:
            
            orderType = 3
            orderRegion = 15
        
        hasRegion = (orderRegion != 15 and len(battle.regions))
        hasMoveOrder = (orderType != 3)
        
        battleHasRegions = (len(battle.regions) > 0)
        battleHasPoints = (len(battle.points) > 0)
        
        self.targetCheck.SetValue(hasRegion and battleHasRegions)
        self.targetList.Enable(hasRegion and battleHasRegions)
        
        if orderType == 0:
            self.gotoForceRadio.SetValue(True)
        elif orderType == 1:
            self.gotoPointRadio.SetValue(True)
        elif orderType == 2:
            self.gotoAllyRadio.SetValue(True)
        
        self.gotoCheck.SetValue(hasMoveOrder)
        self.gotoForceRadio.Enable(hasMoveOrder)
        self.gotoPointRadio.Enable(hasMoveOrder)
        self.gotoAllyRadio.Enable(hasMoveOrder)
        self.gotoList.Enable(hasMoveOrder)
        
        if hasAI:
            
            self.modifyMiscReinforceCheck.SetValue(unit.reinforce)
            self.modifyMiscRespawnCheck.SetValue(unit.respawn)
            self.modifyMisc1Check.SetValue(unit.misc1)
        
        # ---
        
        isNotMember = (self.curUnitContext != 1)
        isCombatant = (self.curUnitContext != 2)

        if hasAI:
            
            if int(unit.ai[1][0]/64) == 1 and len(battle.points) == 0:
                unit.ai[1][0] = 255
                self.modify()
                
            if int(unit.ai[2][0]/64) == 1 and len(battle.points) == 0:
                unit.ai[2][0] = 255
                self.modify()
            
        self.orderSet1Radio.Enable(hasAI)
        self.orderSet2Radio.Enable(hasAI)
        
        self.gotoCheck.Enable(hasAI)
        self.modifyMiscReinforceCheck.Enable(hasAI)
        self.modifyMiscRespawnCheck.Enable(hasAI)
        self.modifyMisc1Check.Enable(hasAI)
        
        
        if isCombatant:
            self.unitText.SetLabel("   Unit (temp.):")
        else:
            self.unitText.SetLabel("Sprite (temp.):")
        
        self.modifyList.Enable(isNotMember)
        self.modifyAICtrl.Enable(hasAI)
        
        self.targetCheck.Enable(hasAI and battleHasRegions)
        
        if hasMoveOrder:            
            self.gotoForceRadio.Enable(hasAI)
            self.gotoPointRadio.Enable(hasAI and battleHasPoints)
            self.gotoAllyRadio.Enable(hasAI)
        
        # ---
        
        if hasAI:
            
            orderNum = unit.ai[self.curOrderSet+1][0] % 32
            if orderType == 2 and orderNum > self.curUnitIdx:
                orderNum -= 1
            self.gotoList.SetSelection(orderNum)
            orderNum = unit.ai[self.curOrderSet+1][1]
            self.targetList.SetSelection(orderNum)
        
    def updateGeneralWindow(self):
        
        battle = self.curBattle
        
        if battle.boss:
            self.winBossRadio.SetValue(True)
        else:
            self.winAllRadio.SetValue(True)
            
        self.battleGfxList.Enable(self.overrideBattleGfxRadio.GetValue())
        
    def updateMapWindow(self):
        
        battle = self.curBattle
        
        hasRegions = (len(battle.regions) != 0)
        hasPoints = (len(battle.points) != 0)
        
        self.mapList.SetSelection(battle.map_index)
        self.boundsXCtrl.SetValue(battle.map_x1)
        self.boundsYCtrl.SetValue(battle.map_y1)
        self.boundsX2Ctrl.SetValue(battle.map_x2)
        self.boundsY2Ctrl.SetValue(battle.map_y2)

    def updateZoneWindow(self):
        
        battle = self.curBattle
        
        hasRegions = (len(battle.regions) != 0)
        hasPoints = (len(battle.points) != 0)
        
        self.regionType1Radio.Enable(hasRegions)
        self.regionType2Radio.Enable(hasRegions)
        
        self.regionList.Enable(hasRegions)
        self.regionXCtrl.Enable(hasRegions)
        self.regionYCtrl.Enable(hasRegions)
        self.regionX2Ctrl.Enable(hasRegions)
        self.regionY2Ctrl.Enable(hasRegions)
        self.regionX3Ctrl.Enable(hasRegions)
        self.regionY3Ctrl.Enable(hasRegions)
        self.regionX4Ctrl.Enable(hasRegions)
        self.regionY4Ctrl.Enable(hasRegions)        
        #self.deletePointButton.Enable(True)
        
        self.pointList.Enable(hasPoints)
        self.pointXCtrl.Enable(hasPoints)
        self.pointYCtrl.Enable(hasPoints)
        #self.deletePointButton.Enable(True)
        
        if hasRegions:
            self.changeRegion(self.curRegionIdx)
            
        if hasPoints:
            self.changePoint(self.curPointIdx)

    def OnChangePage(self, evt):
        
        self.updateMapViewerContext()
        
    def updateMapViewerContext(self):
        
        if self.mapViewer.inited:
            
            pg = self.battleNotebook.GetSelection()
            
            #if self.mapViewer.map == self.map or not self.mapViewer.mapList.IsEnabled() or pg == 3:
                
            if pg == 0: # units
                self.mapViewer.updateContext(consts.VC_BATTLE_UNITS)
            elif pg == 1: # map bounds
                self.mapViewer.updateContext(consts.VC_BATTLE_BOUNDS)
            elif pg == 2:   # AI zones
                self.mapViewer.updateContext(consts.VC_BATTLE_AI_ZONES)
            elif pg == 3: # terrain
                self.mapViewer.updateContext(consts.VC_BATTLE_TERRAIN)
            else:
                self.mapViewer.updateContext(consts.VC_NOTHING)
                    
            #else:
            #    self.mapViewer.updateContext(consts.VC_NOTHING)
            
            self.mapViewer.refreshMapView()
            
    def disableUnimplemented(self):
        
        #self.addMonsterButton.Enable(False)
        #self.addForceButton.Enable(False)
        #self.addAllyButton.Enable(False)
        #self.addNPCButton.Enable(False)
        
        self.winCustomRadio.Enable(False)
        
        self.cutsceneBeforeList.Enable(False)
        self.cutsceneAfterList.Enable(False)
        
        self.triggerXCtrl.Enable(False)
        self.triggerYCtrl.Enable(False)
        self.triggerX2Ctrl.Enable(False)
        self.triggerY2Ctrl.Enable(False)
        
        self.addRegionButton.Enable(False)
        self.addPointButton.Enable(False)
        self.deleteRegionButton.Enable(False)
        self.deletePointButton.Enable(False)
        
        self.overrideBattleGfxRadio.Enable(False)
        self.defaultBattleGfxRadio.Enable(False)
        
        self.propRepeatableCheck.Enable(False)
        self.propMandatoryCheck.Enable(False)
        self.propHalfEXPCheck.Enable(False)
        
        self.modifyMiscItemBrokenCheck.Enable(False)
        
        self.modifyItemList.Enable(False)
        
        #self.modifyDeleteButton.Enable(False)
    
    def getCurrentData(self):
        return self.curBattle
    
    changeSelection = changeBattle
    
    curBattle = property(lambda self: self.rom.data["battles"][self.curBattleIdx])
    curPanel = property(lambda self: self.allGroupPanels[self.curUnitContext][self.curUnitIdx])
    curUnit = property(lambda self: self.allGroupData[self.curUnitContext][self.curUnitIdx])
    allGroupData = property(lambda self: [self.curBattle.enemies, self.curBattle.force, self.curBattle.npcs])