import wx
import consts
from panels import rompanel

caravanIcon = wx.Icon("caravan.ico", wx.BITMAP_TYPE_ICO)

class CaravanParentFrame(wx.MDIParentFrame):
    
    def __init__(self, parent, id, subTitle=None, *args, **kwargs):
        
        self.baseTitle = "The Caravan v0.6 UNSTABLE"
        
        if subTitle:
            self.baseTitle += " -- " + subTitle
        
        wx.MDIParentFrame.__init__(self, parent, id, self.baseTitle, size=(1024,768), *args, **kwargs)
                
        self.CreateStatusBar()
        self.SetIcon(caravanIcon)
        
class CaravanChildFrame(wx.MDIChildFrame):
    
    def __init__(self, parent, id, title, *args, **kwargs):
        
        wx.MDIChildFrame.__init__(self, parent, id, title, *args, **kwargs)
                
        self.CreateStatusBar()
        self.SetIcon(caravanIcon)

class MapViewer(wx.Panel):
    
    def __init__(self, parent, id, mainFrame, *args, **kwargs):

        wx.Panel.__init__(self, parent, id, *args, **kwargs)
        
        self.SetMinSize((480,480))
        
        self.parent = parent
        
        self.viewPageWidth = 5
        self.viewPageHeight = 5
        
        self.viewDownX = 0
        self.viewDownT = 0
        
        self.mouseBlockX = 0
        self.mouseBlockY = 0
        
        self.viewDelay = 0
        self.maxViewDelay = 100

        self.curViewMode = 0
        self.viewAll = 0
        
        self.mainFrame = mainFrame
        self.inited = False
        
        self.map = None
        self.palette = None
        
        self.viewerContext = 0
        
        self.curZoom = 5
        
        self.isDragging = False
        self.dragX1 = 0
        self.dragY1 = 0
        self.dragX2 = 0
        self.dragY2 = 0
        
        self.curMapIdx = None
        
        # ---------
    
    def init(self, map, palette):

        if not self.inited:
            
            self.inited = True
            
            if map is None:
                self.curMapIdx = 0
                map = self.mainFrame.rom.data["maps"][0]
            if palette is None:
                palette = self.mainFrame.rom.data["palettes"][map.paletteIdx]
            
            self.mainPanel = wx.Panel(self, -1)
            self.mainSizer = mainSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            self.editFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Courier New")
            
            # ------
            
            #sbs2layoutViewSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPanel, -1, "Map View"), wx.VERTICAL)
        
            self.viewGrid = sbs2layoutViewGrid = wx.FlexGridSizer(2,2)
            self.viewGrid.AddGrowableCol(0, 1)
            self.viewGrid.AddGrowableRow(0, 1)
            #viewGrid = wx.GridSizer(1,1)
            #viewGrid = wx.GridSizer(self.viewWidth,self.viewHeight)
            
            self.mapViewPanel = rompanel.MapViewPanel(self.mainPanel, wx.ID_ANY, 24*20, 24*20, self.palette, scale=1, bg=16, func=self.OnClickViewPanel, edit=True, grid=24) #, draw=self.drawMapData)
            #self.mapViewPanel.buffer = True
            #self.mapViewPanel.curViewX = 0
            #self.mapViewPanel.curViewY = 0
            self.mapViewPanel.id = 0
            #viewGrid.Add(self.mapViewPanel)
            
            #self.mapViewPanels = []
            #for i in range(self.viewWidth*self.viewHeight):
            #    p = rompanel.TestSpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1, bg=16, func=self.OnClickViewPanel, edit=True, grid=24, draw=self.drawMapData)
            #    p.id = i
            #    self.mapViewPanels.append(p)
            #    viewGrid.Add(p)
            
            #self.mapViewSliderX = wx.Slider(layoutWindow, wx.ID_ANY, 0, 0, (64-self.viewWidth)/self.viewPageHeight, size=(-1,20), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
            #self.mapViewSliderY = wx.Slider(layoutWindow, wx.ID_ANY, 0, 0, (64-self.viewHeight)/self.viewPageWidth, size=(20,-1), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS)
            #self.mapViewSliderX.context = "mapx"
            #self.mapViewSliderY.context = "mapy"
            
            self.mapViewBarX = wx.ScrollBar(self.mainPanel, wx.ID_ANY, style=wx.HORIZONTAL)
            self.mapViewBarX.SetScrollbar(0, self.viewPageWidth*2, 64, self.viewPageWidth)
            self.mapViewBarX.context = "mapx"
            self.mapViewBarY = wx.ScrollBar(self.mainPanel, wx.ID_ANY, style=wx.VERTICAL)
            self.mapViewBarY.SetScrollbar(0, self.viewPageHeight*2, 64, self.viewPageHeight)
            self.mapViewBarY.context = "mapy"
            
            self.gridCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "")
            self.gridCheck.SetValue(True)
            
            #sbs2layoutViewGrid.AddSizer(viewGrid, 0)
            sbs2layoutViewGrid.Add(self.mapViewPanel, 1, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.mapViewBarY, 0, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.mapViewBarX, 0, wx.EXPAND)
            #sbs2layoutViewGrid.Add(self.mapViewSliderX, 0, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.gridCheck, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            
            #sbs2layoutViewSizer.AddSizer(sbs2layoutViewGrid, 1, wx.ALL | wx.EXPAND, 5)
            
            # ----
            
            self.sideSizer = sideSizer = wx.BoxSizer(wx.VERTICAL)
            self.sideSizer.SetMinSize((160,-1))
            mouseText = wx.StaticText(self.mainPanel, -1, "Mouse")
            self.mousePosText = wx.StaticText(self.mainPanel, wx.ID_ANY, "(0,0)")
            self.mousePosText.SetFont(self.editFont)
            
            zoomText = wx.StaticText(self.mainPanel, -1, "Zoom")
            self.zoomSlider = wx.Slider(self.mainPanel, wx.ID_ANY, 4, 0, 8, style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_RIGHT)
            self.zoomSlider.SetSize((-1,600))
            self.curZoomText = wx.StaticText(self.mainPanel, wx.ID_ANY, "100%")
            self.curZoomText.SetFont(self.editFont)
            
            dispText = wx.StaticText(self.mainPanel, -1, "Display")
            #self.dispLayer1Check = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Layer 1")
            #self.dispLayer2Check = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Layer 2")
            self.dispLayersCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Blocks")
            self.dispFlagsCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Flags")
            self.dispEventCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Events")
            self.dispNPCCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " NPCs")

            self.dispLayersCheck.SetValue(True)
            self.dispFlagsCheck.SetValue(True)
            self.dispEventCheck.SetValue(True)
            self.dispNPCCheck.SetValue(True)
            
            self.dispEventCheck.Enable(False)
            self.dispNPCCheck.Enable(False)
            
            editText = wx.StaticText(self.mainPanel, -1, "Currently Editing")
            self.curEditText = wx.StaticText(self.mainPanel, -1, "Blocks")
            self.curEditText.SetFont(self.editFont)
            
            optsText = wx.StaticText(self.mainPanel, -1, "UI Options")
            self.topCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Always on top")
            self.dragCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Alternate drag mode")
            #self.topCheck.SetValue(True)
            
            dispSizer = wx.BoxSizer(wx.VERTICAL)
            dispSizer.Add(self.dispLayersCheck, 0, wx.TOP, 5)
            dispSizer.Add(self.dispFlagsCheck, 0, wx.TOP, 3)
            dispSizer.Add(self.dispEventCheck, 0, wx.TOP, 3)
            dispSizer.Add(self.dispNPCCheck, 0, wx.TOP, 3)

            optsSizer = wx.BoxSizer(wx.VERTICAL)
            optsSizer.Add(self.topCheck, 0, wx.TOP, 5)
            optsSizer.Add(self.dragCheck, 0, wx.TOP, 3)
            
            #self.mapCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Map locked to main window")
            #self.mapList = wx.ComboBox(self.mainPanel, wx.ID_ANY, size=(150,-1))
            #self.mapList.AppendItems([s.name for s in self.getContentPanel().rom.data["maps"]])
            #self.mapList.SetSelection(self.getContentPanel().curMapIdx)
            
            sideSizer.Add((0,15))
            #sideSizer.Add(self.mapCheck, 0, wx.ALIGN_CENTER)
            #sideSizer.Add(self.mapList, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(editText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.curEditText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(mouseText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.mousePosText, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
            sideSizer.Add(zoomText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.curZoomText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(self.zoomSlider, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(dispText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.AddSizer(dispSizer, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(optsText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.AddSizer(optsSizer, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add((0,15))
            
            # ----
            
            #contentPanel = wx.Panel(self, -1)
            #contentPanelSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.AddSizer(sbs2layoutViewGrid, 1, wx.EXPAND)
            mainSizer.AddSizer(sideSizer, 0, wx.ALIGN_CENTER_VERTICAL)
            
            #sbs2layoutViewGrid.FitInside(self.mainPanel)
            #contentPanel.SetSizer(contentPanelSizer)
            
            #mainSizer.Add(contentPanel, 1, wx.EXPAND)
            
            #contentPanelSizer.Layout()
            
            self.mainPanel.SetSizer(mainSizer)
            #mainSizer.Layout()
            #mainSizer.Fit(self)
            
            #self.SetSize(mainSizer.GetSize())
        
            frmSizer = wx.BoxSizer(wx.HORIZONTAL)
            frmSizer.Add(self.mainPanel, 1, wx.EXPAND)
            self.SetSizer(frmSizer)
            frmSizer.Fit(self)

            #mainSizer.Fit(self)
            
            w, h = self.GetSize()
            self.sideX = w - self.mapViewPanel.width
            self.sideY = h - self.mapViewPanel.height
            
            # -----
            
            wx.EVT_SIZE(self, self.OnResize)
            
            #wx.EVT_COMBOBOX(self, self.mapList.GetId(), self.OnSelectMap)
            
            wx.EVT_SLIDER(self, self.zoomSlider.GetId(), self.OnChangeZoom)
            wx.EVT_SCROLL(self, self.OnChangeMapView)
            
            wx.EVT_CHECKBOX(self, self.dispLayersCheck.GetId(), self.OnToggleDispCheck)
            wx.EVT_CHECKBOX(self, self.dispFlagsCheck.GetId(), self.OnToggleFlagCheck)
            wx.EVT_CHECKBOX(self, self.gridCheck.GetId(), self.OnToggleGridCheck)
            #wx.EVT_CHECKBOX(self, self.mapCheck.GetId(), self.OnToggleMapCheck)
            wx.EVT_CHECKBOX(self, self.topCheck.GetId(), self.OnToggleTopCheck)
            wx.EVT_CLOSE(self, self.OnClose)
            
            wx.EVT_MOUSEWHEEL(self, self.OnMouseWheel)
            # -----
            
            #self.SetSize((480,480))
        
        if map is not None or palette is not None:
            self.changeMap(map, palette)
        
    def OnClose(self, evt):
        self.Hide()
        
    def OnResize(self, evt):
        
        if evt.GetEventObject() == self:
            
            w, h = evt.GetSize()
            #self.viewGrid.Fit(self.mapViewPanel)
            #self.viewGrid.Layout()
            self.mainPanel.SetSize(self.GetClientSize())
            #self.GetSizer().Fit(self.mapViewPanel)
            self.setViewPos(self.curViewX, self.curViewY)
            self.updateScrollbars()
            self.mapViewPanel.Refresh(False)
            
    def OnSelectMap(self, evt):
        map = self.getContentPanel().rom.data["maps"][evt.GetSelection()]
        palette = self.getContentPanel().rom.data["palettes"][map.paletteIdx]
        self.changeMap(map, palette)
        
    def OnChangeZoom(self, evt):
        
        self.changeZoom(evt.GetSelection())
        evt.Skip()
        
    def changeZoom(self, zoom):
        
        self.curZoom = zoom
        self.zoomSlider.SetValue(self.curZoom)
        
        s = self.scales[self.curZoom]
        
        if self.mapViewPanel.scale != s:
            
            self.mapViewPanel.scale = s
            self.updateScrollbars()
            self.curZoomText.SetLabel("%i%%" % (s * 100))
            self.sideSizer.Layout()
            self.setViewPos(self.curViewX, self.curViewY)
            self.refreshMapView()
        
    #def OnToggleMapCheck(self, evt):
    #    self.mapList.Enable(not evt.GetSelection())
        
    def OnToggleGridCheck(self, evt):
        self.mapViewPanel.grid = [False, 24][evt.GetSelection()]
        self.refreshMapView()

    def OnToggleDispCheck(self, evt):
        self.mapViewPanel.drawBlocks = evt.GetSelection()
        self.refreshMapView()
    
    def OnToggleFlagCheck(self, evt):
        self.mapViewPanel.drawFlags = evt.GetSelection()
        self.refreshMapView()
        
    def OnToggleTopCheck(self, evt):
        self.SetWindowStyle(self.GetWindowStyle() ^ wx.STAY_ON_TOP)
        
    def OnMouseWheel(self, evt):
        
        rt = evt.GetWheelRotation()
        
        if evt.ShiftDown():
            
            if rt > 0:
                zoom = min(len(self.scales)-1, self.curZoom+1)
            elif rt < 0:
                zoom = max(0, self.curZoom-1)
            
            if zoom != self.curZoom:
                self.changeZoom(zoom)
    
            evt.Skip()
            
        elif evt.ControlDown():
            self.setViewPos(self.curViewX - rt, self.curViewY)
        
        else:
            self.setViewPos(self.curViewX, self.curViewY - rt)
        
        self.refreshMapView()
        evt.Skip()
            
    def OnChangeMapView(self, evt):
        
        obj = evt.GetEventObject()
        
        if hasattr(obj, "context"):
            
            if obj.context == "mapx":
                self.oldViewX = self.curViewX
                self.mapViewPanel.curViewX = obj.GetThumbPosition() #min(64 - self.viewPageWidth, obj.GetThumbPosition())
                #self.refreshMapView()
            elif obj.context == "mapy":
                self.oldViewY = self.curViewY
                self.mapViewPanel.curViewY = obj.GetThumbPosition() #min(64 - self.viewPageHeight, obj.GetThumbPosition())
                #self.refreshMapView()
            else:
                return
        
            self.refreshMapView()
            
        evt.Skip()

    def OnClickViewPanel(self, evt):
        
        obj = evt.GetEventObject()
        x = (evt.GetX())
        y = (evt.GetY())
        blockW = int(24 * obj.scale)
        blockH = int(24 * obj.scale)
        blockX = int(max(0, min(self.map.width-1, (x / obj.scale + self.curViewX) / 24)))
        blockY = int(max(0, min(self.map.height-1, (y / obj.scale + self.curViewY) / 24)))
        
        cont = self.getContentPanel()
        
        # handle moving view window
        
        if blockX != self.mouseBlockX or blockY != self.mouseBlockY:
            self.mouseBlockX = blockX
            self.mouseBlockY = blockY
            self.mousePosText.SetLabel("(%i,%i)" % (blockX, blockY))
            self.sideSizer.Layout()
            
        if evt.MiddleDown():
            self.viewDownX = x
            self.viewDownY = y
            obj.SetFocus()
            #print "(%i,%i) -- %s" % (x + self.curViewX, y + self.curViewY, hex(self.map.layoutData[blockY*64 + blockX])[2:])
            
        if evt.MiddleIsDown():
            
            #self.viewDelay -= 1
            sizeX, sizeY = self.GetSize()
            #if self.viewDelay < 0:
            xd = int((x - self.viewDownX) / obj.scale)
            yd = int((y - self.viewDownY) / obj.scale)
            self.oldViewX = self.curViewX
            self.oldViewY = self.curViewY
            self.setViewPos(self.curViewX - xd, self.curViewY - yd)
            #self.viewDelay = self.maxViewDelay
            
            #if not evt.Dragging():
            if xd or yd:
                self.viewDownX = x
                self.viewDownY = y
                if self.oldViewX != self.curViewX or self.oldViewY != self.curViewY:
                    self.refreshMapView()
        
            return

        # --------------------
        # handle individual clicking
        
        idx = blockY*64 + blockX
        blk = self.map.layoutData[idx]
            
        if self.viewerContext == consts.VC_BLOCKS:  # placing graphical block
            
            if evt.ShiftDown():
                
                if evt.LeftIsDown():
                    cont.curListBlockLeft = self.map.layoutData[idx] & 0x3ff
                elif evt.RightIsDown():
                    cont.curListBlockRight = self.map.layoutData[idx] & 0x3ff
                else:
                    return
                
                cont.refreshBlockListSelPanels()
            
            else:

                if evt.LeftIsDown():
                    bot = cont.curListBlockLeft
                elif evt.RightIsDown():
                    bot = cont.curListBlockRight
                else:
                    return
                
                bot &= 0x3ff
                
                top = blk & 0xfc00
                
                if (blk & 0x3ff) != bot:
                
                    self.map.layoutData[idx] = top | bot
                    
                    obj.pixels = self.map.blocks[bot].pixels
                    obj.Refresh()
                    
                    cont.modify()

                
        elif self.viewerContext == consts.VC_FLAGS:  # placing flag data or clearing
            
            #self.viewDelay = 0
            
            #x += self.curViewX
            #y += self.curViewY
            #idx = (y / blockH) * 64 + (x / blockW)
                
            change = False
            
            if evt.LeftIsDown():
                
                val = cont.curInterFlag
                
                newObs = val & 0xc000
                newEvent = val & 0x3c00
                oldObs = blk & 0xc000
                oldEvent = blk & 0x3c00
                bot = blk & 0x3ff
                
                if newObs and oldObs != newObs:
                    self.map.layoutData[idx] = bot | newObs | oldEvent
                elif newObs == 0x4000:
                    self.map.layoutData[idx] ^= 0xc000
                elif newEvent and oldEvent != newEvent:
                    self.map.layoutData[idx] = bot | oldObs | newEvent
                else:
                    return

            elif evt.RightIsDown():
                
                val = cont.curInterFlag
                
                if blk & 0xfc00:
                    
                    if evt.ShiftDown():
                        self.map.layoutData[idx] = blk & 0x3ff
                    else:
                        newObs = val & 0xc000
                        newEvent = val & 0x3c00
                        if newObs:
                            self.map.layoutData[idx] = blk & 0x3fff
                        if newEvent:
                            self.map.layoutData[idx] = blk & 0xc3ff
                else:
                    return
                
            else:
                return
                
            obj.Refresh()
            cont.modify()
            
            #self.refreshMapView()
        
        # -------------
        # the following are changes that simply mirror changes to event forms.
        
        elif self.viewerContext == consts.VC_EVENT_WARP:
            
            event = cont.getCurrentEvent()
            
            if event:
                    
                if evt.LeftDown() and self.map == cont.map:
                    cont.changeWarpX(blockX)
                    cont.changeWarpY(blockY)
                
                elif evt.RightDown():
                    
                    cont.changeWarpDestX(blockX)
                    cont.changeWarpDestY(blockY)

                    idx = 0
                    for i,m in enumerate(cont.rom.data["maps"]):
                        if self.map == m:
                            idx = i
                            break
                    
                    cont.changeWarpMap(idx)
                
                else:
                    evt.Skip()
                    return
                        
                cont.modify()
            
        elif self.viewerContext == consts.VC_EVENT_COPY:
            
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if self.dragCheck.GetValue():   # click, click
                    dragStartCond = evt.ShiftDown() and not self.isDragging
                    if self.isDragging == "l":
                        dragEndCond = evt.LeftDown()
                    else:
                        dragEndCond = evt.RightDown()
                else:
                    dragStartCond = evt.ShiftDown()
                    if self.isDragging == "l":
                        dragStartCond = dragStartCond and evt.LeftIsDown()
                    elif self.isDragging == "r":
                        dragStartCond = dragStartCond and evt.RightIsDown()
                    dragEndCond = True
                    
                if dragStartCond:
                    
                    if not self.isDragging:
                        
                        if evt.LeftDown():
                            self.isDragging = "l"
                            cont.setCopyBlank(False)
                        elif evt.RightDown():
                            self.isDragging = "r"
                        else:
                            evt.Skip()
                            
                        self.dragX1 = blockX
                        self.dragY1 = blockY
                
                elif self.isDragging and dragEndCond:
                    
                    self.isDragging = False
                
                elif evt.RightDown():
                    
                    cont.eventPropCopyDestXCtrl.SetValue(blockX)
                    cont.eventPropCopyDestYCtrl.SetValue(blockY)
                    event.destx = blockX
                    event.desty = blockY
                    obj.Refresh()
                    cont.modify()
                    
                elif evt.LeftDown():
                    
                    if evt.ControlDown():
                        if event.copyType != 0:
                            cont.eventPropCopyTrigXCtrl.SetValue(blockX)
                            cont.eventPropCopyTrigYCtrl.SetValue(blockY)
                            event.x = blockX
                            event.y = blockY
                        else:
                            evt.Skip()
                            return
                            
                    else:
                        cont.eventPropCopySrcXCtrl.SetValue(blockX)
                        cont.eventPropCopySrcYCtrl.SetValue(blockY)
                        event.srcx = blockX
                        event.srcy = blockY
                        
                    obj.Refresh()
                    cont.modify()
                    
                if self.isDragging:
                    
                    self.dragX2 = blockX
                    self.dragY2 = blockY
                    
                    x1, x2 = sorted([blockX, self.dragX1])
                    y1, y2 = sorted([blockY, self.dragY1])
                    
                    if self.isDragging == "l":
                        cont.eventPropCopySrcXCtrl.SetValue(x1)
                        cont.eventPropCopySrcYCtrl.SetValue(y1)
                        event.srcx = x1
                        event.srcy = y1
                    else:
                        cont.eventPropCopyDestXCtrl.SetValue(x1)
                        cont.eventPropCopyDestYCtrl.SetValue(y1)
                        event.destx = x1
                        event.desty = y1
                        
                    cont.eventPropCopyWidthCtrl.SetValue(x2 - x1 + 1)
                    cont.eventPropCopyHeightCtrl.SetValue(y2 - y1 + 1)
                    event.width = x2 - x1 + 1
                    event.height = y2 - y1 + 1
                    cont.modify()
                    obj.Refresh()
        
        elif self.viewerContext == consts.VC_EVENT_ITEM:
        
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if evt.LeftIsDown():
                    cont.changeItemX(blockX)
                    cont.changeItemY(blockY)
                    
        elif self.viewerContext == consts.VC_AREA:
            
            event = cont.curArea

            if self.dragCheck.GetValue():   # click, click
                dragStartCond = evt.ShiftDown() and not self.isDragging
                if self.isDragging == "l":
                    dragEndCond = evt.LeftDown()
                else:
                    dragEndCond = evt.RightDown()
            else:
                dragStartCond = evt.ShiftDown()
                if self.isDragging == "l":
                    dragStartCond = dragStartCond and evt.LeftIsDown()
                elif self.isDragging == "r":
                    dragStartCond = dragStartCond and evt.RightIsDown()
                dragEndCond = True
                
            if dragStartCond:
                
                if not self.isDragging:
                    
                    if evt.LeftDown():
                        self.isDragging = "l"
                        cont.changeAreaLayer1X1(blockX)
                        cont.changeAreaLayer1Y1(blockY)
                    elif evt.RightDown():
                        self.isDragging = "r"
                    else:
                        evt.Skip()
                        
                    self.dragX1 = blockX
                    self.dragY1 = blockY
            
            elif self.isDragging and dragEndCond:
                
                self.isDragging = False
            
            elif evt.RightDown():
                
                cont.changeAreaLayer2X1(blockX)
                cont.changeAreaLayer2Y1(blockY)
                
            elif evt.LeftDown():
                
                width = event.l1x2 - event.l1x1
                height = event.l1y2 - event.l1y1
                cont.changeAreaLayer1X1(blockX)
                cont.changeAreaLayer1Y1(blockY)
                cont.changeAreaLayer1X2(blockX+width)
                cont.changeAreaLayer1Y2(blockY+height)
                
            if self.isDragging:
                
                self.dragX2 = blockX
                self.dragY2 = blockY
                
                x1, x2 = sorted([blockX, self.dragX1])
                y1, y2 = sorted([blockY, self.dragY1])
                
                if self.isDragging == "l":
                    cont.changeAreaLayer1X2(x2)
                    cont.changeAreaLayer1Y2(y2)
                #else:
                #    cont.changeAreaLayer2X1(x1)
                #    cont.changeAreaLayer2Y1(y1)
                    
                cont.changeAreaLayer2X2(x2 - x1 + 1)
                cont.changeAreaLayer2Y2(y2 - y1 + 1)       

        evt.Skip()
    
    # --------------------
    # custom draw funcs
    
    def drawDraggingRect(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        event = self.passes[0]["obj"](cont)
        
        if event and self.map == cont.map:
            
            oldX, oldY = None, None
            
            for curPass in self.passes:
                
                event = curPass["obj"](cont)
                
                x1 = curPass["x1"](event)
                y1 = curPass["y1"](event)
                x2 = curPass["x2"](event)
                y2 = curPass["y2"](event)
                
                realX = (x1 - tx) * 24 - ox
                realY = (y1 - ty) * 24 - oy
                w = (x2 - x1)
                h = (y2 - y1)

                midX = ((x1 + x2) / 2.0 - tx) * 24 - ox
                midY = ((y1 + y2) / 2.0 - ty) * 24 - oy
                
                if not curPass.has_key("condition") or curPass["condition"](event):

                    if curPass.has_key("line") and oldCond:
                        dc.DrawLine(midX, midY, oldX, oldY)
                    
                    if curPass.has_key("pen"):
                        dc.SetPen(curPass["pen"])
                    dc.DrawRoundedRectangle(realX+2, realY+2, w*24-4, h*24-4, 4)
                    
                    if curPass.has_key("xline"):
                        dc.DrawLine(realX+2, realY+2, realX+w*24-2, realY+h*24-2)
                        dc.DrawLine(realX+2, realY+h*24-2, realX+w*24-2, realY+2)
            
                    if curPass.has_key("point") and curPass["point"](event):
                        
                        self.drawEventPoint(dc, tx, ty, ox, oy)
                
                    oldCond = True
                else:
                    oldCond = False
                    
                oldX, oldY, oldW, oldH = midX, midY, w, h
    
    def drawWarpPoints(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        event = cont.getCurrentEvent()
        
        if cont.getCurrentEvent():
            
            x = event.x
            y = event.y
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            dc.SetPen(self.mapViewPanel.warpCoordPen)
            
            if event.sameMap:
                destMap = cont.map
            else:
                destMap = cont.rom.data["maps"][event.destmap]

            oldX, oldY = realX, realY
            x = event.destx
            y = event.desty
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            
            if not (event.sameDestX and event.sameDestY):
                
                if event.sameMap and cont.map == self.map:

                    dc.DrawLine(oldX+12, oldY+12, realX+12, realY+12)
                    
                else:
                
                    if self.map == destMap:
                        oldX, oldY = realX, realY
                    elif cont.map == self.map:
                        x, y, w, h = cont.getCurrentEventCoords()
                        oldX = (x - tx) * 24 - ox
                        oldY = (y - ty) * 24 - oy
                    else:
                        return
                        
                    x1, y1 = (0 - tx) * 24 - ox, (0 - ty) * 24 - oy
                    x2, y2 = (64 - tx) * 24 - ox, (0 - ty) * 24 - oy
                    x3, y3 = (64 - tx) * 24 - ox, (64 - ty) * 24 - oy
                    x4, y4 = (0 - tx) * 24 - ox, (64 - ty) * 24 - oy
                    dc.DrawLine(x1, y1, oldX+2, oldY+2)
                    dc.DrawLine(x2, y2, oldX+22, oldY+2)
                    dc.DrawLine(x3, y3, oldX+22, oldY+22)
                    dc.DrawLine(x4, y4, oldX+2, oldY+22)
                    
                if self.map == destMap:

                    x = event.destx
                    y = event.desty
                    realX = (x - tx) * 24 - ox
                    realY = (y - ty) * 24 - oy
                    
                    if event.sameDestY:
                        dc.DrawRoundedRectangle(realX+2, -24, 24-4, cont.map.height*24+24, 4)
                    elif event.sameDestX:
                        dc.DrawRoundedRectangle(-24, realY+2, cont.map.width*24+24, 24-4, 4)
                    else:
                        dc.DrawRoundedRectangle(realX+2, realY+2, 24-4, 24-4, 4)
            
            dc.SetPen(self.mapViewPanel.eventCoordPen)
            realX = (event.x - tx) * 24 - ox
            realY = (event.y - ty) * 24 - oy
            if event.sameY:
                dc.DrawRoundedRectangle(realX+2, -24, 24-4, cont.map.height*24+24, 4)
            elif event.sameX:
                dc.DrawRoundedRectangle(-24, realY+2, cont.map.width*24+24, 24-4, 4)
            else:
                self.drawEventPoint(dc, tx, ty, ox, oy)
            
    def drawEventPoint(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        
        if cont.getCurrentEvent() and self.map == cont.map:
            
            x, y, w, h = cont.getCurrentEventCoords()
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            dc.SetPen(self.mapViewPanel.eventCoordPen)
            dc.DrawRoundedRectangle(realX+4, realY+4, w*24-8, h*24-8, 4)
            dc.CrossHair(realX+w*12, realY+h*12)
            
    # --------------------------
    
    def updateContext(self, context=None):
        
        if context is None:
            context = self.viewerContext
            
        self.viewerContext = context
            
        if self.inited:
            
            self.mapViewPanel.drawFunc = None
            self.passes = []
            
            if self.viewerContext == consts.VC_EVENT_WARP:
                
                self.mapViewPanel.drawFunc = self.drawWarpPoints
                
            elif self.viewerContext == consts.VC_EVENT_COPY:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[0]["condition"] = lambda obj: not obj.copyBlank
                self.passes[0]["pen"] = self.mapViewPanel.copySrcPen
                self.passes[0]["x1"] = lambda obj: obj.srcx
                self.passes[0]["y1"] = lambda obj: obj.srcy
                self.passes[0]["x2"] = lambda obj: obj.srcx + obj.width
                self.passes[0]["y2"] = lambda obj: obj.srcy + obj.height

                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[1]["pen"] = self.mapViewPanel.copyDestPen
                self.passes[1]["line"] = True
                self.passes[1]["point"] = lambda obj: obj.copyType != 0
                self.passes[1]["x1"] = lambda obj: obj.destx
                self.passes[1]["y1"] = lambda obj: obj.desty
                self.passes[1]["x2"] = lambda obj: obj.destx + obj.width
                self.passes[1]["y2"] = lambda obj: obj.desty + obj.height
                    
            elif self.viewerContext == consts.VC_EVENT_ITEM:
                
                self.mapViewPanel.drawFunc = self.drawEventPoint
                    
            elif self.viewerContext == consts.VC_AREA:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.curArea
                self.passes[0]["pen"] = self.mapViewPanel.eventCoordPen
                self.passes[0]["xline"] = True
                self.passes[0]["x1"] = lambda obj: obj.l1x1
                self.passes[0]["y1"] = lambda obj: obj.l1y1
                self.passes[0]["x2"] = lambda obj: obj.l1x2 + 1
                self.passes[0]["y2"] = lambda obj: obj.l1y2 + 1
                    
                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.curArea
                self.passes[1]["condition"] = lambda obj: obj.hasLayer2
                self.passes[1]["pen"] = self.mapViewPanel.floorPen
                self.passes[1]["xline"] = True
                self.passes[1]["x1"] = lambda obj: obj.l2x
                self.passes[1]["y1"] = lambda obj: obj.l2y
                self.passes[1]["x2"] = lambda obj: obj.l2x + obj.l1x2 - obj.l1x1 + 1
                self.passes[1]["y2"] = lambda obj: obj.l2y + obj.l1y2 - obj.l1y1 + 1
                
            self.curEditText.SetLabel(self.vcTexts[self.viewerContext])
            self.sideSizer.Layout()
        
    def setViewPos(self, x, y):
        s = self.mapViewPanel.scale
        maxX = self.map.width * 24
        maxY = self.map.height * 24
        sizeX, sizeY = self.mapViewPanel.GetSize()
        self.mapViewPanel.curViewX = max(0, min(maxX - sizeX / s, x))
        self.mapViewPanel.curViewY = max(0, min(maxY - sizeY / s, y))
        self.mapViewBarX.SetThumbPosition(x)
        self.mapViewBarY.SetThumbPosition(y)
        #self.refreshMapView()
    
    def centerViewPos(self, x, y):
        sizeX, sizeY = self.mapViewPanel.GetSize()
        self.setViewPos(x - (sizeX / 2), y - (sizeY / 2))
        
    def refreshMapView(self):
        
        """pix = [""] * 24 * self.viewHeight
        
        for i in range(self.viewWidth * self.viewHeight):
            x = (i % self.viewWidth)
            y = (i / self.viewWidth)
            mx = self.curViewX + x
            my = self.curViewY + y
            blkIdx = self.map.layoutData[my*64+mx] & 0x3ff
            blk = self.map.blocks[blkIdx]
            for r in range(24):
                pix[r+y*24] += blk.pixels[r]"""
            
        #for i,p in enumerate(self.mapViewPanels):
        #    mx = self.curViewX + (i % self.viewWidth)
        #    my = self.curViewY + (i / self.viewWidth)
        #    blk = self.map.layoutData[my*64+mx] & 0x3ff
        #    p.pixels = self.map.blocks[blk].pixels
        
        #self.mapViewPanel.pixels = pix
        #self.mapViewPanel.Refresh(False)
        
        #self.mapViewPanel.curViewX = self.curViewX
        #self.mapViewPanel.curViewY = self.curViewY
        #self.mapViewPanel.Refresh(False)
        
        #self.Refresh(False)
        #self.Freeze()
        #for p in self.mapViewPanels:
        #    p.Refresh()
        #self.Thaw()
        
        if self.inited:
            self.mapViewPanel.Refresh()
        
        pass
        
    def changeMap(self, map, palette):
        
        if map != self.map or palette != self.palette:
            
            if map is not None:
                self.map = map
            if palette is not None:
                self.palette = palette

            if hasattr(self.getContentPanel(), "updateMapViewerContext"):
                self.getContentPanel().updateMapViewerContext()
            else:
                self.updateContext(self.viewerContext)
            
            if not self.map.loaded:
                self.getContentPanel().rom.getMaps(self.curMapIdx, self.curMapIdx)

            self.mapViewPanel.changeMap(self.map, self.palette)

            self.mapViewPanel.curViewX = 0
            self.mapViewPanel.curViewY = 0
            self.mapViewPanel.Refresh()
            
            self.setViewPos(0, 0)
            self.updateScrollbars()
 
    def updateScrollbars(self):
        
        s = self.mapViewPanel.scale
        x = self.mapViewPanel.GetSize()[0] / s
        y = self.mapViewPanel.GetSize()[1] / s
        
        #print "(%i,%i)" % (x,y)
        self.mapViewBarX.SetScrollbar(self.curViewX, x, self.map.width * 24, 120)
        self.mapViewBarY.SetScrollbar(self.curViewY, y, self.map.height * 24, 120)
        
    curViewX = property(lambda self: self.mapViewPanel.curViewX)
    curViewY = property(lambda self: self.mapViewPanel.curViewY)
    #curMapIdx = property(lambda self: self.mapList.GetSelection())
        
    getContentPanel = lambda self: self.parent # mainFrame.contentPanel #.subPanel
        
    vcTexts = ["Nothing", "Blocks", "Flags", "Event:Warp", "Event:Copy", "Event:Item", "Area"]
    
    scales = [.25, .33, .5, .75, 1, 1.5, 2, 3, 5]
    
class BattleMapViewer(MapViewer):

    def OnClickViewPanel(self, evt):
        
        obj = evt.GetEventObject()
        x = (evt.GetX())
        y = (evt.GetY())
        blockW = int(24 * obj.scale)
        blockH = int(24 * obj.scale)
        blockX = int(max(0, min(self.map.width-1, (x / obj.scale + self.curViewX) / 24)))
        blockY = int(max(0, min(self.map.height-1, (y / obj.scale + self.curViewY) / 24)))
        
        cont = self.getContentPanel()
        
        # handle moving view window
        
        if blockX != self.mouseBlockX or blockY != self.mouseBlockY:
            self.mouseBlockX = blockX
            self.mouseBlockY = blockY
            self.mousePosText.SetLabel("(%i,%i)" % (blockX, blockY))
            self.sideSizer.Layout()
            
        if evt.MiddleDown():
            self.viewDownX = x
            self.viewDownY = y
            obj.SetFocus()
            
        if evt.MiddleIsDown():
            
            #self.viewDelay -= 1
            sizeX, sizeY = self.GetSize()
            #if self.viewDelay < 0:
            xd = int((x - self.viewDownX) / obj.scale)
            yd = int((y - self.viewDownY) / obj.scale)
            self.oldViewX = self.curViewX
            self.oldViewY = self.curViewY
            self.setViewPos(self.curViewX - xd, self.curViewY - yd)
            #self.viewDelay = self.maxViewDelay
            
            #if not evt.Dragging():
            if xd or yd:
                self.viewDownX = x
                self.viewDownY = y
                if self.oldViewX != self.curViewX or self.oldViewY != self.curViewY:
                    self.refreshMapView()
        
            return

        # --------------------
        # handle individual clicking
        
        idx = blockY*64 + blockX
        blk = self.map.layoutData[idx]
            
        battle = cont.curBattle
        
        if self.viewerContext == consts.VC_BATTLE_UNITS:  # placing allies/enemies
            
            if evt.LeftIsDown():

                bx = blockX - battle.map_x1
                by = blockY - battle.map_y1
                    
                if evt.ShiftDown():
                
                    swap = None
                    for g,con in enumerate(cont.allGroupData):
                        for i,u in enumerate(con):
                            if u.x == bx and u.y == by and u is not cont.curUnit:
                                cont.changeUnit(g,i)
                                return
                
                else:
                    
                    cont.curUnit.x = bx
                    cont.curUnit.y = by
                    cont.modifyXCtrl.SetValue(bx)
                    cont.modifyYCtrl.SetValue(by)
                    cont.modify()
                    self.refreshMapView()

            elif evt.RightDown():
                
                bx = blockX - battle.map_x1
                by = blockY - battle.map_y1
                
                swap = None
                for con in cont.allGroupData:
                    for u in con:
                        if u.x == bx and u.y == by and u is not cont.curUnit:
                            swap = u
                            break
                    if swap:
                        break
                
                if swap:
                    
                    if evt.ShiftDown():
                        
                        if cont.curUnitContext == 2:
                            cont.changeUnitIdx(swap.idx)
                        elif cont.curUnitContext == 0:
                            cont.changeUnitIdx(swap.idx-64)
                        else:
                            return
                        
                    else:
                        swap.x = cont.curUnit.x
                        swap.y = cont.curUnit.y
                        cont.curUnit.x = bx
                        cont.curUnit.y = by
                        cont.modifyXCtrl.SetValue(bx)
                        cont.modifyYCtrl.SetValue(by)
                        
                    cont.modify()
                    self.refreshMapView()
                
        elif self.viewerContext == consts.VC_BATTLE_BOUNDS:  # changing bounds of battle map
            
            if evt.LeftIsDown():

                diffX = blockX - battle.map_x1
                diffY = blockY - battle.map_y1
                
                battle.map_x1 = blockX
                battle.map_y1 = blockY
                
                if not evt.ShiftDown():
                    
                    for con in cont.allGroupData:
                        for unit in con:
                            unit.x -= diffX
                            unit.y -= diffY
            
                    cont.modifyXCtrl.SetValue(cont.curUnit.x)
                    cont.modifyYCtrl.SetValue(cont.curUnit.y)
                
                if evt.ControlDown():

                    battle.map_x2 += diffX
                    battle.map_y2 += diffY

            elif evt.RightIsDown():

                diffX = blockX - battle.map_x2 + 1
                diffY = blockY - battle.map_y2 + 1
                
                battle.map_x2 = blockX+1
                battle.map_y2 = blockY+1
                
                if evt.ShiftDown():
                    
                    for con in cont.allGroupData:
                        for unit in con:
                            unit.x += diffX
                            unit.y += diffY
            
                    cont.modifyXCtrl.SetValue(cont.curUnit.x)
                    cont.modifyYCtrl.SetValue(cont.curUnit.y)
                
                if evt.ControlDown():

                    for con in cont.allGroupData:
                        for unit in con:
                            unit.x -= diffX
                            unit.y -= diffY
                            
                    battle.map_x1 += diffX
                    battle.map_y1 += diffY                

            else:
                return
            
            cont.boundsXCtrl.SetValue(battle.map_x1)
            cont.boundsYCtrl.SetValue(battle.map_y1)
            cont.boundsX2Ctrl.SetValue(battle.map_x2)
            cont.boundsY2Ctrl.SetValue(battle.map_y2)
                
            obj.Refresh()
            cont.modify()
            
            self.refreshMapView()
        
        elif self.viewerContext == consts.VC_BATTLE_AI_ZONES:
            
            if battle.regions:
                
                wasDragging = self.isDragging
                
                if not evt.LeftIsDown():
                    self.isDragging = False
                    
                if evt.LeftDown():
                    
                    region = battle.regions[cont.curRegionIdx]
                    bpt = [blockX - battle.map_x1, blockY - battle.map_y1]
                    
                    if bpt == region.p1:   self.isDragging = 1
                    elif bpt == region.p2:   self.isDragging = 2
                    elif bpt == region.p3:   self.isDragging = 3
                    elif bpt == region.p4:   self.isDragging = 4
                    
                if self.isDragging:
                    
                    region = battle.regions[cont.curRegionIdx]
                    bpt = [blockX - battle.map_x1, blockY - battle.map_y1]
                    
                    if self.isDragging == 1:
                        cont.changeRegionX(bpt[0])
                        cont.changeRegionY(bpt[1])
                    elif self.isDragging == 2:
                        cont.changeRegionX2(bpt[0])
                        cont.changeRegionY2(bpt[1])
                    elif self.isDragging == 3:
                        cont.changeRegionX3(bpt[0])
                        cont.changeRegionY3(bpt[1])
                    elif self.isDragging == 4:
                        cont.changeRegionX4(bpt[0])
                        cont.changeRegionY4(bpt[1])
                    
            if battle.points:
                
                if evt.RightIsDown():
                    bpt = [blockX - battle.map_x1, blockY - battle.map_y1]
                    cont.changePointX(bpt[0])
                    cont.changePointY(bpt[1])
            
        elif self.viewerContext == consts.VC_BATTLE_TERRAIN:
            
            if evt.LeftIsDown():
                
                if blockX >= battle.map_x1 and blockX <= battle.map_x2 and blockY >= battle.map_y1 and blockY <= battle.map_y2:

                    realX = blockX - battle.map_x1
                    realY = blockY - battle.map_y1
                    
                    rawIdx = realY * 48 + realX
                    tileIdx = rawIdx / 32
                    rowIdx = (rawIdx % 32) / 4
                    strIdx = (rawIdx % 4) * 2
                    
                    if not evt.ShiftDown():
                        
                        row = battle.terrain.tiles[tileIdx].pixels[rowIdx]
                        row = row[:strIdx] + hex(cont.curTerrainType)[2:].zfill(2) + row[strIdx+2:]
                        battle.terrain.tiles[tileIdx].pixels[rowIdx] = row

                        obj.Refresh()
                        cont.modify()
                        
                        self.refreshMapView()
                    
                    else:
                        
                        tt = int(battle.terrain.tiles[tileIdx].pixels[rowIdx][strIdx:strIdx+2], 16)
                        cont.changeTerrainType(min(len(cont.terrainIcons)-1, tt))
                    
        """# -------------
        # the following are changes that simply mirror changes to event forms.
        
        elif self.viewerContext == consts.VC_EVENT_WARP:
            
            event = cont.getCurrentEvent()
            
            if event:
                    
                if evt.LeftDown() and self.map == cont.map:
                    cont.changeWarpX(blockX)
                    cont.changeWarpY(blockY)
                
                elif evt.RightDown():
                    
                    cont.changeWarpDestX(blockX)
                    cont.changeWarpDestY(blockY)

                    idx = 0
                    for i,m in enumerate(cont.rom.data["maps"]):
                        if self.map == m:
                            idx = i
                            break
                    
                    cont.changeWarpMap(idx)
                
                else:
                    evt.Skip()
                    return
                        
                cont.modify()
            
        elif self.viewerContext == consts.VC_EVENT_COPY:
            
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if self.dragCheck.GetValue():   # click, click
                    dragStartCond = evt.ShiftDown() and not self.isDragging
                    if self.isDragging == "l":
                        dragEndCond = evt.LeftDown()
                    else:
                        dragEndCond = evt.RightDown()
                else:
                    dragStartCond = evt.ShiftDown()
                    if self.isDragging == "l":
                        dragStartCond = dragStartCond and evt.LeftIsDown()
                    elif self.isDragging == "r":
                        dragStartCond = dragStartCond and evt.RightIsDown()
                    dragEndCond = True
                    
                if dragStartCond:
                    
                    if not self.isDragging:
                        
                        if evt.LeftDown():
                            self.isDragging = "l"
                            cont.setCopyBlank(False)
                        elif evt.RightDown():
                            self.isDragging = "r"
                        else:
                            evt.Skip()
                            
                        self.dragX1 = blockX
                        self.dragY1 = blockY
                
                elif self.isDragging and dragEndCond:
                    
                    self.isDragging = False
                
                elif evt.RightDown():
                    
                    cont.eventPropCopyDestXCtrl.SetValue(blockX)
                    cont.eventPropCopyDestYCtrl.SetValue(blockY)
                    event.destx = blockX
                    event.desty = blockY
                    obj.Refresh()
                    cont.modify()
                    
                elif evt.LeftDown():
                    
                    if evt.ControlDown():
                        if event.copyType != 0:
                            cont.eventPropCopyTrigXCtrl.SetValue(blockX)
                            cont.eventPropCopyTrigYCtrl.SetValue(blockY)
                            event.x = blockX
                            event.y = blockY
                        else:
                            evt.Skip()
                            return
                            
                    else:
                        cont.eventPropCopySrcXCtrl.SetValue(blockX)
                        cont.eventPropCopySrcYCtrl.SetValue(blockY)
                        event.srcx = blockX
                        event.srcy = blockY
                        
                    obj.Refresh()
                    cont.modify()
                    
                if self.isDragging:
                    
                    self.dragX2 = blockX
                    self.dragY2 = blockY
                    
                    x1, x2 = sorted([blockX, self.dragX1])
                    y1, y2 = sorted([blockY, self.dragY1])
                    
                    if self.isDragging == "l":
                        cont.eventPropCopySrcXCtrl.SetValue(x1)
                        cont.eventPropCopySrcYCtrl.SetValue(y1)
                        event.srcx = x1
                        event.srcy = y1
                    else:
                        cont.eventPropCopyDestXCtrl.SetValue(x1)
                        cont.eventPropCopyDestYCtrl.SetValue(y1)
                        event.destx = x1
                        event.desty = y1
                        
                    cont.eventPropCopyWidthCtrl.SetValue(x2 - x1 + 1)
                    cont.eventPropCopyHeightCtrl.SetValue(y2 - y1 + 1)
                    event.width = x2 - x1 + 1
                    event.height = y2 - y1 + 1
                    cont.modify()
                    obj.Refresh()
        
        elif self.viewerContext == consts.VC_EVENT_ITEM:
        
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if evt.LeftDown():
                    cont.changeItemX(blockX)
                    cont.changeItemY(blockY)
                    
        elif self.viewerContext == consts.VC_AREA:
            
            event = cont.curArea

            if self.dragCheck.GetValue():   # click, click
                dragStartCond = evt.ShiftDown() and not self.isDragging
                if self.isDragging == "l":
                    dragEndCond = evt.LeftDown()
                else:
                    dragEndCond = evt.RightDown()
            else:
                dragStartCond = evt.ShiftDown()
                if self.isDragging == "l":
                    dragStartCond = dragStartCond and evt.LeftIsDown()
                elif self.isDragging == "r":
                    dragStartCond = dragStartCond and evt.RightIsDown()
                dragEndCond = True
                
            if dragStartCond:
                
                if not self.isDragging:
                    
                    if evt.LeftDown():
                        self.isDragging = "l"
                        cont.changeAreaLayer1X1(blockX)
                        cont.changeAreaLayer1Y1(blockY)
                    elif evt.RightDown():
                        self.isDragging = "r"
                    else:
                        evt.Skip()
                        
                    self.dragX1 = blockX
                    self.dragY1 = blockY
            
            elif self.isDragging and dragEndCond:
                
                self.isDragging = False
            
            elif evt.RightDown():
                
                cont.changeAreaLayer2X1(blockX)
                cont.changeAreaLayer2Y1(blockY)
                
            elif evt.LeftDown():
                
                width = event.l1x2 - event.l1x1
                height = event.l1y2 - event.l1y1
                cont.changeAreaLayer1X1(blockX)
                cont.changeAreaLayer1Y1(blockY)
                cont.changeAreaLayer1X2(blockX+width)
                cont.changeAreaLayer1Y2(blockY+height)
                
            if self.isDragging:
                
                self.dragX2 = blockX
                self.dragY2 = blockY
                
                x1, x2 = sorted([blockX, self.dragX1])
                y1, y2 = sorted([blockY, self.dragY1])
                
                if self.isDragging == "l":
                    cont.changeAreaLayer1X2(x2)
                    cont.changeAreaLayer1Y2(y2)
                #else:
                #    cont.changeAreaLayer2X1(x1)
                #    cont.changeAreaLayer2Y1(y1)
                    
                cont.changeAreaLayer2X2(x2 - x1 + 1)
                cont.changeAreaLayer2Y2(y2 - y1 + 1)       """

        evt.Skip()
    
    # -----------------------
    # custom draw func
    
    def drawBattleUnits(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        battle = cont.curBattle
        
        # offset tile position by start of battle map
        btx = tx - battle.map_x1
        bty = ty - battle.map_y1
        
        sx = -btx * 24 - ox
        sy = -bty * 24 - oy
        
        dc.SetPen(self.mapViewPanel.eventCoordPen)
        dc.DrawRoundedRectangle(sx+8, sy+8, (battle.map_x2 - battle.map_x1) * 24 - 16, (battle.map_y2 - battle.map_y1) * 24 - 16, 8)
        
        try:
            
            for con in xrange(len(cont.allGroupData)):
                
                curPanels = cont.allGroupPanels[con]
                curData = cont.allGroupData[con]
                
                for idx in xrange(len(curData)):
                    
                    cp = curPanels[idx]
                    cd = curData[idx]
                    dc.DrawBitmap(cp.bmp, (cd.x - btx) * 24 - ox, (cd.y - bty) * 24 - oy)
            
        except IndexError, e:
            
            #print con, idx
            pass
        
        if self.viewerContext == consts.VC_BATTLE_UNITS:
          
            x = cont.curUnit.x - btx
            y = cont.curUnit.y - bty
            dc.SetPen(self.mapViewPanel.tablePen)
            dc.DrawRoundedRectangle(x * 24 - ox - 2, y * 24 - oy - 2, 28, 28, 8)
            
        elif self.viewerContext == consts.VC_BATTLE_TERRAIN:
            
            us = dc.GetUserScale()
            dc.SetUserScale(us[0]*3/4, us[1]*3/4)
            
            mw = battle.map_x2 - battle.map_x1
            mh = battle.map_y2 - battle.map_y1
            
            for y in xrange(mh):
                for x in xrange(mw):
                    
                    dx = (x - tx + battle.map_x1) * 32 - ox * 4 / 3
                    dy = (y - ty + battle.map_y1) * 32 - oy * 4 / 3 
                    
                    rawIdx = y * 48 + x
                    tileIdx = rawIdx / 32
                    rowIdx = (rawIdx % 32) / 4
                    strIdx = (rawIdx % 4) * 2
                    
                    t = int(battle.terrain.tiles[tileIdx].pixels[rowIdx][strIdx:strIdx+2], 16)
                        
                    if t < 9:
                        dc.DrawBitmap(cont.terrainIcons[t], dx, dy)
                    else:
                        dc.DrawBitmap(cont.terrainIcons[-1], dx, dy)
        
        elif self.viewerContext == consts.VC_BATTLE_AI_ZONES:
            
            if battle.regions:
                
                region = battle.regions[cont.curRegionIdx]
                
                p1x, p1y = (region.p1[0] - btx) * 24 - ox + 12, (region.p1[1] - bty) * 24 - oy + 12
                p2x, p2y = (region.p2[0] - btx) * 24 - ox + 12, (region.p2[1] - bty) * 24 - oy + 12
                p3x, p3y = (region.p3[0] - btx) * 24 - ox + 12, (region.p3[1] - bty) * 24 - oy + 12
                p4x, p4y = (region.p4[0] - btx) * 24 - ox + 12, (region.p4[1] - bty) * 24 - oy + 12
                
                dc.SetPen(self.mapViewPanel.eventPen)
                dc.DrawLine(p1x, p1y, p2x, p2y)
                dc.DrawLine(p2x, p2y, p3x, p3y)
                dc.DrawLine(p3x, p3y, p4x, p4y)
                dc.DrawLine(p4x, p4y, p1x, p1y)
                dc.DrawCircle(p1x, p1y, 8)
                dc.DrawCircle(p2x, p2y, 8)
                dc.DrawCircle(p3x, p3y, 8)
                dc.DrawCircle(p4x, p4y, 8)
            
            if battle.points:
                
                point = battle.points[cont.curPointIdx]
                
                dc.SetPen(self.mapViewPanel.copySrcPen)
                dc.DrawRoundedRectangle((point[0] - btx) * 24 - ox + 4, (point[1] - bty) * 24 - oy + 4, 16, 16, 4)
                
    # --------------------------
    
    def updateContext(self, context=None):
        
        if context is None:
            context = self.viewerContext
            
        self.viewerContext = context
        
        if self.inited:
            
            self.mapViewPanel.drawFunc = self.drawBattleUnits
            self.passes = []
            
            #if self.viewerContext == consts.VC_BATTLE_UNITS:
                
            #    self.mapViewPanel.drawFunc = self.drawBattleUnits
                
            """    
            elif self.viewerContext == consts.VC_EVENT_COPY:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[0]["condition"] = lambda obj: not obj.copyBlank
                self.passes[0]["pen"] = self.mapViewPanel.copySrcPen
                self.passes[0]["x1"] = lambda obj: obj.srcx
                self.passes[0]["y1"] = lambda obj: obj.srcy
                self.passes[0]["x2"] = lambda obj: obj.srcx + obj.width
                self.passes[0]["y2"] = lambda obj: obj.srcy + obj.height

                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[1]["pen"] = self.mapViewPanel.copyDestPen
                self.passes[1]["line"] = True
                self.passes[1]["point"] = lambda obj: obj.copyType != 0
                self.passes[1]["x1"] = lambda obj: obj.destx
                self.passes[1]["y1"] = lambda obj: obj.desty
                self.passes[1]["x2"] = lambda obj: obj.destx + obj.width
                self.passes[1]["y2"] = lambda obj: obj.desty + obj.height
                    
            elif self.viewerContext == consts.VC_EVENT_ITEM:
                
                self.mapViewPanel.drawFunc = self.drawEventPoint
                    
            elif self.viewerContext == consts.VC_AREA:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.curArea
                self.passes[0]["pen"] = self.mapViewPanel.eventCoordPen
                self.passes[0]["xline"] = True
                self.passes[0]["x1"] = lambda obj: obj.l1x1
                self.passes[0]["y1"] = lambda obj: obj.l1y1
                self.passes[0]["x2"] = lambda obj: obj.l1x2 + 1
                self.passes[0]["y2"] = lambda obj: obj.l1y2 + 1
                    
                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.curArea
                self.passes[1]["condition"] = lambda obj: obj.hasLayer2
                self.passes[1]["pen"] = self.mapViewPanel.floorPen
                self.passes[1]["xline"] = True
                self.passes[1]["x1"] = lambda obj: obj.l2x
                self.passes[1]["y1"] = lambda obj: obj.l2y
                self.passes[1]["x2"] = lambda obj: obj.l2x + obj.l1x2 - obj.l1x1 + 1
                self.passes[1]["y2"] = lambda obj: obj.l2y + obj.l1y2 - obj.l1y1 + 1
            
            """
            
            self.curEditText.SetLabel(self.vcTexts[self.viewerContext])
            self.sideSizer.Layout()
            
    vcTexts = ["Nothing", "Units", "Map Bounds", "AI Zones", "Terrain"]
    
# ----------------------------------------
# Old mapviewer, when it was a frame

"""class MapViewer(CaravanChildFrame):
    
    def __init__(self, parent, id, mainFrame):

        CaravanChildFrame.__init__(self, parent, id, "Map Viewer", style=wx.DEFAULT_FRAME_STYLE)
        
        self.SetMinSize((480,480))
        
        self.viewPageWidth = 5
        self.viewPageHeight = 5
        
        self.viewDownX = 0
        self.viewDownT = 0
        
        self.mouseBlockX = 0
        self.mouseBlockY = 0
        
        self.viewDelay = 0
        self.maxViewDelay = 100

        self.curViewMode = 0
        self.viewAll = 0
        
        self.mainFrame = mainFrame
        self.inited = False
        
        self.map = None
        self.palette = None
        
        self.viewerContext = 0
        
        self.curZoom = 5
        
        self.isDragging = False
        self.dragX1 = 0
        self.dragY1 = 0
        self.dragX2 = 0
        self.dragY2 = 0
        
        # ---------
    
    def init(self, map, palette):

        if not self.inited:
            
            self.inited = True
            
            if map is None:
                map = self.mainFrame.rom.data["maps"][0]
            if palette is None:
                palette = self.mainFrame.rom.data["palettes"][map.paletteIdx]
            
            self.mainPanel = wx.Panel(self, -1)
            self.mainSizer = mainSizer = wx.BoxSizer(wx.HORIZONTAL)
            
            self.editFont = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Courier New")
            
            # ------
            
            #sbs2layoutViewSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPanel, -1, "Map View"), wx.VERTICAL)
        
            self.viewGrid = sbs2layoutViewGrid = wx.FlexGridSizer(2,2)
            self.viewGrid.AddGrowableCol(0, 1)
            self.viewGrid.AddGrowableRow(0, 1)
            #viewGrid = wx.GridSizer(1,1)
            #viewGrid = wx.GridSizer(self.viewWidth,self.viewHeight)
            
            self.mapViewPanel = rompanel.MapViewPanel(self.mainPanel, wx.ID_ANY, 24*20, 24*20, self.palette, scale=1, bg=16, func=self.OnClickViewPanel, edit=True, grid=24) #, draw=self.drawMapData)
            #self.mapViewPanel.buffer = True
            #self.mapViewPanel.curViewX = 0
            #self.mapViewPanel.curViewY = 0
            self.mapViewPanel.id = 0
            #viewGrid.Add(self.mapViewPanel)
            
            #self.mapViewPanels = []
            #for i in range(self.viewWidth*self.viewHeight):
            #    p = rompanel.TestSpritePanel(layoutWindow, wx.ID_ANY, 24, 24, self.palette, scale=1, bg=16, func=self.OnClickViewPanel, edit=True, grid=24, draw=self.drawMapData)
            #    p.id = i
            #    self.mapViewPanels.append(p)
            #    viewGrid.Add(p)
            
            #self.mapViewSliderX = wx.Slider(layoutWindow, wx.ID_ANY, 0, 0, (64-self.viewWidth)/self.viewPageHeight, size=(-1,20), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
            #self.mapViewSliderY = wx.Slider(layoutWindow, wx.ID_ANY, 0, 0, (64-self.viewHeight)/self.viewPageWidth, size=(20,-1), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS)
            #self.mapViewSliderX.context = "mapx"
            #self.mapViewSliderY.context = "mapy"
            
            self.mapViewBarX = wx.ScrollBar(self.mainPanel, wx.ID_ANY, style=wx.HORIZONTAL)
            self.mapViewBarX.SetScrollbar(0, self.viewPageWidth*2, 64, self.viewPageWidth)
            self.mapViewBarX.context = "mapx"
            self.mapViewBarY = wx.ScrollBar(self.mainPanel, wx.ID_ANY, style=wx.VERTICAL)
            self.mapViewBarY.SetScrollbar(0, self.viewPageHeight*2, 64, self.viewPageHeight)
            self.mapViewBarY.context = "mapy"
            
            self.gridCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "")
            self.gridCheck.SetValue(True)
            
            #sbs2layoutViewGrid.AddSizer(viewGrid, 0)
            sbs2layoutViewGrid.Add(self.mapViewPanel, 1, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.mapViewBarY, 0, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.mapViewBarX, 0, wx.EXPAND)
            #sbs2layoutViewGrid.Add(self.mapViewSliderX, 0, wx.EXPAND)
            sbs2layoutViewGrid.Add(self.gridCheck, 0, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            
            #sbs2layoutViewSizer.AddSizer(sbs2layoutViewGrid, 1, wx.ALL | wx.EXPAND, 5)
            
            # ----
            
            self.sideSizer = sideSizer = wx.BoxSizer(wx.VERTICAL)
            self.sideSizer.SetMinSize((160,-1))
            mouseText = wx.StaticText(self.mainPanel, -1, "Mouse")
            self.mousePosText = wx.StaticText(self.mainPanel, wx.ID_ANY, "(0,0)")
            self.mousePosText.SetFont(self.editFont)
            
            zoomText = wx.StaticText(self.mainPanel, -1, "Zoom")
            self.zoomSlider = wx.Slider(self.mainPanel, wx.ID_ANY, 4, 0, 8, style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_RIGHT)
            self.zoomSlider.SetSize((-1,600))
            self.curZoomText = wx.StaticText(self.mainPanel, wx.ID_ANY, "100%")
            self.curZoomText.SetFont(self.editFont)
            
            dispText = wx.StaticText(self.mainPanel, -1, "Display")
            #self.dispLayer1Check = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Layer 1")
            #self.dispLayer2Check = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Layer 2")
            self.dispLayersCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Blocks")
            self.dispFlagsCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Flags")
            self.dispEventCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " Events")
            self.dispNPCCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, " NPCs")

            self.dispLayersCheck.SetValue(True)
            self.dispFlagsCheck.SetValue(True)
            self.dispEventCheck.SetValue(True)
            self.dispNPCCheck.SetValue(True)
            
            self.dispEventCheck.Enable(False)
            self.dispNPCCheck.Enable(False)
            
            editText = wx.StaticText(self.mainPanel, -1, "Currently Editing")
            self.curEditText = wx.StaticText(self.mainPanel, -1, "Blocks")
            self.curEditText.SetFont(self.editFont)
            
            optsText = wx.StaticText(self.mainPanel, -1, "UI Options")
            self.topCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Always on top")
            self.dragCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Alternate drag mode")
            #self.topCheck.SetValue(True)
            
            dispSizer = wx.BoxSizer(wx.VERTICAL)
            dispSizer.Add(self.dispLayersCheck, 0, wx.TOP, 5)
            dispSizer.Add(self.dispFlagsCheck, 0, wx.TOP, 3)
            dispSizer.Add(self.dispEventCheck, 0, wx.TOP, 3)
            dispSizer.Add(self.dispNPCCheck, 0, wx.TOP, 3)

            optsSizer = wx.BoxSizer(wx.VERTICAL)
            optsSizer.Add(self.topCheck, 0, wx.TOP, 5)
            optsSizer.Add(self.dragCheck, 0, wx.TOP, 3)
            
            self.mapCheck = wx.CheckBox(self.mainPanel, wx.ID_ANY, "Map locked to main window")
            self.mapList = wx.ComboBox(self.mainPanel, wx.ID_ANY, size=(150,-1))
            self.mapList.AppendItems([s.name for s in self.getContentPanel().rom.data["maps"]])
            self.mapList.SetSelection(self.getContentPanel().curMapIdx)
            
            sideSizer.Add((0,15))
            sideSizer.Add(self.mapCheck, 0, wx.ALIGN_CENTER)
            sideSizer.Add(self.mapList, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(editText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.curEditText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(mouseText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.mousePosText, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
            sideSizer.Add(zoomText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.Add(self.curZoomText, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(self.zoomSlider, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(dispText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.AddSizer(dispSizer, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add(optsText, 0, wx.ALIGN_CENTER | wx.TOP, 15)
            sideSizer.AddSizer(optsSizer, 0, wx.ALIGN_CENTER | wx.TOP, 5)
            sideSizer.Add((0,15))
            
            # ----
            
            #contentPanel = wx.Panel(self, -1)
            #contentPanelSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.AddSizer(sbs2layoutViewGrid, 1, wx.EXPAND)
            mainSizer.AddSizer(sideSizer, 0, wx.ALIGN_CENTER_VERTICAL)
            
            #sbs2layoutViewGrid.FitInside(self.mainPanel)
            #contentPanel.SetSizer(contentPanelSizer)
            
            #mainSizer.Add(contentPanel, 1, wx.EXPAND)
            
            #contentPanelSizer.Layout()
            
            self.mainPanel.SetSizer(mainSizer)
            #mainSizer.Layout()
            #mainSizer.Fit(self)
            
            #self.SetSize(mainSizer.GetSize())
        
            frmSizer = wx.BoxSizer(wx.HORIZONTAL)
            frmSizer.Add(self.mainPanel, 1, wx.EXPAND)
            self.SetSizer(frmSizer)
            frmSizer.Fit(self)

            #mainSizer.Fit(self)
            
            w, h = self.GetSize()
            self.sideX = w - self.mapViewPanel.width
            self.sideY = h - self.mapViewPanel.height
            
            # -----
            
            wx.EVT_SIZE(self, self.OnResize)
            
            wx.EVT_COMBOBOX(self, self.mapList.GetId(), self.OnSelectMap)
            
            wx.EVT_SLIDER(self, self.zoomSlider.GetId(), self.OnChangeZoom)
            wx.EVT_SCROLL(self, self.OnChangeMapView)
            
            wx.EVT_CHECKBOX(self, wx.ID_ANY, self.OnToggleDispCheck)
            wx.EVT_CHECKBOX(self, self.gridCheck.GetId(), self.OnToggleGridCheck)
            wx.EVT_CHECKBOX(self, self.mapCheck.GetId(), self.OnToggleMapCheck)
            wx.EVT_CHECKBOX(self, self.topCheck.GetId(), self.OnToggleTopCheck)
            wx.EVT_CLOSE(self, self.OnClose)
            
            wx.EVT_MOUSEWHEEL(self, self.OnMouseWheel)
            # -----
            
            #self.SetSize((480,480))
        
        if map is not None or palette is not None:
            self.changeMap(map, palette)
        
    def OnClose(self, evt):
        self.Hide()
        
    def OnResize(self, evt):
        
        if evt.GetEventObject() == self:
            
            w, h = evt.GetSize()
            #self.viewGrid.Fit(self.mapViewPanel)
            #self.viewGrid.Layout()
            self.mainPanel.SetSize(self.GetClientSize())
            #self.GetSizer().Fit(self.mapViewPanel)
            self.setViewPos(self.curViewX, self.curViewY)
            self.updateScrollbars()
            self.mapViewPanel.Refresh(False)
            
    def OnSelectMap(self, evt):
        map = self.getContentPanel().rom.data["maps"][evt.GetSelection()]
        palette = self.getContentPanel().rom.data["palettes"][map.paletteIdx]
        self.changeMap(map, palette)
        
    def OnChangeZoom(self, evt):
        
        self.changeZoom(evt.GetSelection())
        evt.Skip()
        
    def changeZoom(self, zoom):
        
        self.curZoom = zoom
        self.zoomSlider.SetValue(self.curZoom)
        
        s = self.scales[self.curZoom]
        
        if self.mapViewPanel.scale != s:
            
            self.mapViewPanel.scale = s
            self.updateScrollbars()
            self.curZoomText.SetLabel("%i%%" % (s * 100))
            self.sideSizer.Layout()
            self.setViewPos(self.curViewX, self.curViewY)
            self.refreshMapView()
        
    def OnToggleMapCheck(self, evt):
        self.mapList.Enable(not evt.GetSelection())
        
    def OnToggleGridCheck(self, evt):
        self.mapViewPanel.grid = [False, 24][evt.GetSelection()]
        self.refreshMapView()

    def OnToggleDispCheck(self, evt):
        self.refreshMapView()

    def OnToggleTopCheck(self, evt):
        self.SetWindowStyle(self.GetWindowStyle() ^ wx.STAY_ON_TOP)
        
    def OnMouseWheel(self, evt):
        
        rt = evt.GetWheelRotation()
        
        if evt.ShiftDown():
            
            if rt > 0:
                zoom = min(len(self.scales)-1, self.curZoom+1)
            elif rt < 0:
                zoom = max(0, self.curZoom-1)
            
            if zoom != self.curZoom:
                self.changeZoom(zoom)
    
            evt.Skip()
            
        elif evt.ControlDown():
            self.setViewPos(self.curViewX - rt, self.curViewY)
        
        else:
            self.setViewPos(self.curViewX, self.curViewY - rt)
        
        self.refreshMapView()
        evt.Skip()
            
    def OnChangeMapView(self, evt):
        
        obj = evt.GetEventObject()
        
        if hasattr(obj, "context"):
            
            if obj.context == "mapx":
                self.oldViewX = self.curViewX
                self.mapViewPanel.curViewX = obj.GetThumbPosition() #min(64 - self.viewPageWidth, obj.GetThumbPosition())
                #self.refreshMapView()
            elif obj.context == "mapy":
                self.oldViewY = self.curViewY
                self.mapViewPanel.curViewY = obj.GetThumbPosition() #min(64 - self.viewPageHeight, obj.GetThumbPosition())
                #self.refreshMapView()
            else:
                return
        
            self.refreshMapView()
            
        evt.Skip()

    def OnClickViewPanel(self, evt):
        
        obj = evt.GetEventObject()
        x = (evt.GetX())
        y = (evt.GetY())
        blockW = int(24 * obj.scale)
        blockH = int(24 * obj.scale)
        blockX = int(max(0, min(self.map.width-1, (x / obj.scale + self.curViewX) / 24)))
        blockY = int(max(0, min(self.map.height-1, (y / obj.scale + self.curViewY) / 24)))
        
        cont = self.getContentPanel()
        
        # handle moving view window
        
        if blockX != self.mouseBlockX or blockY != self.mouseBlockY:
            self.mouseBlockX = blockX
            self.mouseBlockY = blockY
            self.mousePosText.SetLabel("(%i,%i)" % (blockX, blockY))
            self.sideSizer.Layout()
            
        if evt.MiddleDown():
            self.viewDownX = x
            self.viewDownY = y
            obj.SetFocus()
            print "(%i,%i) -- %s" % (x + self.curViewX, y + self.curViewY, hex(self.map.layoutData[blockY*64 + blockX])[2:])
            
        if evt.MiddleIsDown():
            
            #self.viewDelay -= 1
            sizeX, sizeY = self.GetSize()
            #if self.viewDelay < 0:
            xd = int((x - self.viewDownX) / obj.scale)
            yd = int((y - self.viewDownY) / obj.scale)
            self.oldViewX = self.curViewX
            self.oldViewY = self.curViewY
            self.setViewPos(self.curViewX - xd, self.curViewY - yd)
            #self.viewDelay = self.maxViewDelay
            
            #if not evt.Dragging():
            if xd or yd:
                self.viewDownX = x
                self.viewDownY = y
                if self.oldViewX != self.curViewX or self.oldViewY != self.curViewY:
                    self.refreshMapView()
        
            return

        # --------------------
        # handle individual clicking
        
        idx = blockY*64 + blockX
        blk = self.map.layoutData[idx]
            
        if self.viewerContext == consts.VC_BLOCKS:  # placing graphical block
            
            if evt.ShiftDown():
                
                if evt.LeftDown():
                    cont.curListBlockLeft = self.map.layoutData[idx] & 0x3ff
                elif evt.RightIsDown():
                    cont.curListBlockRight = self.map.layoutData[idx] & 0x3ff
                else:
                    return
                
                cont.refreshBlockListSelPanels()
            
            else:

                if evt.LeftIsDown():
                    bot = cont.curListBlockLeft
                elif evt.RightIsDown():
                    bot = cont.curListBlockRight
                else:
                    return
                
                bot &= 0x3ff
                
                top = blk & 0xfc00
                
                if (blk & 0x3ff) != bot:
                
                    self.map.layoutData[idx] = top | bot
                    
                    obj.pixels = self.map.blocks[bot].pixels
                    obj.Refresh()
                    
                    cont.modify()

                
        elif self.viewerContext == consts.VC_FLAGS:  # placing flag data or clearing
            
            #self.viewDelay = 0
            
            #x += self.curViewX
            #y += self.curViewY
            #idx = (y / blockH) * 64 + (x / blockW)
                
            change = False
            
            if evt.LeftDown():
                
                val = cont.curInterFlag
                
                newObs = val & 0xc000
                newEvent = val & 0x3c00
                oldObs = blk & 0xc000
                oldEvent = blk & 0x3c00
                bot = blk & 0x3ff
                
                if newObs and oldObs != newObs:
                    self.map.layoutData[idx] = bot | newObs | oldEvent
                elif newObs == 0x4000:
                    self.map.layoutData[idx] ^= 0xc000
                elif newEvent and oldEvent != newEvent:
                    self.map.layoutData[idx] = bot | oldObs | newEvent
                else:
                    return

            elif evt.RightIsDown():
                
                if blk & 0xfc00:
                    self.map.layoutData[idx] = blk & 0x3ff
                else:
                    return
                
            else:
                return
                
            obj.Refresh()
            cont.modify()
            
            #self.refreshMapView()
        
        # -------------
        # the following are changes that simply mirror changes to event forms.
        
        elif self.viewerContext == consts.VC_EVENT_WARP:
            
            event = cont.getCurrentEvent()
            
            if event:
                    
                if evt.LeftDown() and self.map == cont.map:
                    cont.changeWarpX(blockX)
                    cont.changeWarpY(blockY)
                
                elif evt.RightDown():
                    
                    cont.changeWarpDestX(blockX)
                    cont.changeWarpDestY(blockY)

                    idx = 0
                    for i,m in enumerate(cont.rom.data["maps"]):
                        if self.map == m:
                            idx = i
                            break
                    
                    cont.changeWarpMap(idx)
                
                else:
                    evt.Skip()
                    return
                        
                cont.modify()
            
        elif self.viewerContext == consts.VC_EVENT_COPY:
            
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if self.dragCheck.GetValue():   # click, click
                    dragStartCond = evt.ShiftDown() and not self.isDragging
                    if self.isDragging == "l":
                        dragEndCond = evt.LeftDown()
                    else:
                        dragEndCond = evt.RightDown()
                else:
                    dragStartCond = evt.ShiftDown()
                    if self.isDragging == "l":
                        dragStartCond = dragStartCond and evt.LeftIsDown()
                    elif self.isDragging == "r":
                        dragStartCond = dragStartCond and evt.RightIsDown()
                    dragEndCond = True
                    
                if dragStartCond:
                    
                    if not self.isDragging:
                        
                        if evt.LeftDown():
                            self.isDragging = "l"
                            cont.setCopyBlank(False)
                        elif evt.RightDown():
                            self.isDragging = "r"
                        else:
                            evt.Skip()
                            
                        self.dragX1 = blockX
                        self.dragY1 = blockY
                
                elif self.isDragging and dragEndCond:
                    
                    self.isDragging = False
                
                elif evt.RightDown():
                    
                    cont.eventPropCopyDestXCtrl.SetValue(blockX)
                    cont.eventPropCopyDestYCtrl.SetValue(blockY)
                    event.destx = blockX
                    event.desty = blockY
                    obj.Refresh()
                    cont.modify()
                    
                elif evt.LeftDown():
                    
                    if evt.ControlDown():
                        if event.copyType != 0:
                            cont.eventPropCopyTrigXCtrl.SetValue(blockX)
                            cont.eventPropCopyTrigYCtrl.SetValue(blockY)
                            event.x = blockX
                            event.y = blockY
                        else:
                            evt.Skip()
                            return
                            
                    else:
                        cont.eventPropCopySrcXCtrl.SetValue(blockX)
                        cont.eventPropCopySrcYCtrl.SetValue(blockY)
                        event.srcx = blockX
                        event.srcy = blockY
                        
                    obj.Refresh()
                    cont.modify()
                    
                if self.isDragging:
                    
                    self.dragX2 = blockX
                    self.dragY2 = blockY
                    
                    x1, x2 = sorted([blockX, self.dragX1])
                    y1, y2 = sorted([blockY, self.dragY1])
                    
                    if self.isDragging == "l":
                        cont.eventPropCopySrcXCtrl.SetValue(x1)
                        cont.eventPropCopySrcYCtrl.SetValue(y1)
                        event.srcx = x1
                        event.srcy = y1
                    else:
                        cont.eventPropCopyDestXCtrl.SetValue(x1)
                        cont.eventPropCopyDestYCtrl.SetValue(y1)
                        event.destx = x1
                        event.desty = y1
                        
                    cont.eventPropCopyWidthCtrl.SetValue(x2 - x1 + 1)
                    cont.eventPropCopyHeightCtrl.SetValue(y2 - y1 + 1)
                    event.width = x2 - x1 + 1
                    event.height = y2 - y1 + 1
                    cont.modify()
                    obj.Refresh()
        
        elif self.viewerContext == consts.VC_EVENT_ITEM:
        
            event = cont.getCurrentEvent()
            
            if event and self.map == cont.map:
                
                if evt.LeftDown():
                    cont.changeItemX(blockX)
                    cont.changeItemY(blockY)
                    
        elif self.viewerContext == consts.VC_AREA:
            
            event = cont.curArea

            if self.dragCheck.GetValue():   # click, click
                dragStartCond = evt.ShiftDown() and not self.isDragging
                if self.isDragging == "l":
                    dragEndCond = evt.LeftDown()
                else:
                    dragEndCond = evt.RightDown()
            else:
                dragStartCond = evt.ShiftDown()
                if self.isDragging == "l":
                    dragStartCond = dragStartCond and evt.LeftIsDown()
                elif self.isDragging == "r":
                    dragStartCond = dragStartCond and evt.RightIsDown()
                dragEndCond = True
                
            if dragStartCond:
                
                if not self.isDragging:
                    
                    if evt.LeftDown():
                        self.isDragging = "l"
                        cont.changeAreaLayer1X1(blockX)
                        cont.changeAreaLayer1Y1(blockY)
                    elif evt.RightDown():
                        self.isDragging = "r"
                    else:
                        evt.Skip()
                        
                    self.dragX1 = blockX
                    self.dragY1 = blockY
            
            elif self.isDragging and dragEndCond:
                
                self.isDragging = False
            
            elif evt.RightDown():
                
                cont.changeAreaLayer2X1(blockX)
                cont.changeAreaLayer2Y1(blockY)
                
            elif evt.LeftDown():
                
                width = event.l1x2 - event.l1x1
                height = event.l1y2 - event.l1y1
                cont.changeAreaLayer1X1(blockX)
                cont.changeAreaLayer1Y1(blockY)
                cont.changeAreaLayer1X2(blockX+width)
                cont.changeAreaLayer1Y2(blockY+height)
                
            if self.isDragging:
                
                self.dragX2 = blockX
                self.dragY2 = blockY
                
                x1, x2 = sorted([blockX, self.dragX1])
                y1, y2 = sorted([blockY, self.dragY1])
                
                if self.isDragging == "l":
                    cont.changeAreaLayer1X2(x2)
                    cont.changeAreaLayer1Y2(y2)
                #else:
                #    cont.changeAreaLayer2X1(x1)
                #    cont.changeAreaLayer2Y1(y1)
                    
                cont.changeAreaLayer2X2(x2 - x1 + 1)
                cont.changeAreaLayer2Y2(y2 - y1 + 1)       

        evt.Skip()
    
    def drawDraggingRect(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        event = self.passes[0]["obj"](cont)
        
        if event and self.map == cont.map:
            
            oldX, oldY = None, None
            
            for curPass in self.passes:
                
                event = curPass["obj"](cont)
                
                x1 = curPass["x1"](event)
                y1 = curPass["y1"](event)
                x2 = curPass["x2"](event)
                y2 = curPass["y2"](event)
                
                realX = (x1 - tx) * 24 - ox
                realY = (y1 - ty) * 24 - oy
                w = (x2 - x1)
                h = (y2 - y1)

                midX = ((x1 + x2) / 2.0 - tx) * 24 - ox
                midY = ((y1 + y2) / 2.0 - ty) * 24 - oy
                
                if not curPass.has_key("condition") or curPass["condition"](event):

                    if curPass.has_key("line") and oldCond:
                        dc.DrawLine(midX, midY, oldX, oldY)
                    
                    if curPass.has_key("pen"):
                        dc.SetPen(curPass["pen"])
                    dc.DrawRoundedRectangle(realX+2, realY+2, w*24-4, h*24-4, 4)
                    
                    if curPass.has_key("xline"):
                        dc.DrawLine(realX+2, realY+2, realX+w*24-2, realY+h*24-2)
                        dc.DrawLine(realX+2, realY+h*24-2, realX+w*24-2, realY+2)
            
                    if curPass.has_key("point") and curPass["point"](event):
                        
                        self.drawEventPoint(dc, tx, ty, ox, oy)
                
                    oldCond = True
                else:
                    oldCond = False
                    
                oldX, oldY, oldW, oldH = midX, midY, w, h
    
    def drawWarpPoints(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        event = cont.getCurrentEvent()
        
        if cont.getCurrentEvent():
            
            x = event.x
            y = event.y
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            dc.SetPen(self.mapViewPanel.warpCoordPen)
            
            if event.sameMap:
                destMap = cont.map
            else:
                destMap = cont.rom.data["maps"][event.destmap]

            oldX, oldY = realX, realY
            x = event.destx
            y = event.desty
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            
            if not (event.sameDestX and event.sameDestY):
                
                if event.sameMap and cont.map == self.map:

                    dc.DrawLine(oldX+12, oldY+12, realX+12, realY+12)
                    
                else:
                
                    if self.map == destMap:
                        oldX, oldY = realX, realY
                    elif cont.map == self.map:
                        x, y, w, h = cont.getCurrentEventCoords()
                        oldX = (x - tx) * 24 - ox
                        oldY = (y - ty) * 24 - oy
                    else:
                        return
                        
                    x1, y1 = (0 - tx) * 24 - ox, (0 - ty) * 24 - oy
                    x2, y2 = (64 - tx) * 24 - ox, (0 - ty) * 24 - oy
                    x3, y3 = (64 - tx) * 24 - ox, (64 - ty) * 24 - oy
                    x4, y4 = (0 - tx) * 24 - ox, (64 - ty) * 24 - oy
                    dc.DrawLine(x1, y1, oldX+2, oldY+2)
                    dc.DrawLine(x2, y2, oldX+22, oldY+2)
                    dc.DrawLine(x3, y3, oldX+22, oldY+22)
                    dc.DrawLine(x4, y4, oldX+2, oldY+22)
                    
                if self.map == destMap:

                    x = event.destx
                    y = event.desty
                    realX = (x - tx) * 24 - ox
                    realY = (y - ty) * 24 - oy
                    
                    if event.sameDestY:
                        dc.DrawRoundedRectangle(realX+2, -24, 24-4, cont.map.height*24+24, 4)
                    elif event.sameDestX:
                        dc.DrawRoundedRectangle(-24, realY+2, cont.map.width*24+24, 24-4, 4)
                    else:
                        dc.DrawRoundedRectangle(realX+2, realY+2, 24-4, 24-4, 4)
            
            dc.SetPen(self.mapViewPanel.eventCoordPen)
            realX = (event.x - tx) * 24 - ox
            realY = (event.y - ty) * 24 - oy
            if event.sameY:
                dc.DrawRoundedRectangle(realX+2, -24, 24-4, cont.map.height*24+24, 4)
            elif event.sameX:
                dc.DrawRoundedRectangle(-24, realY+2, cont.map.width*24+24, 24-4, 4)
            else:
                self.drawEventPoint(dc, tx, ty, ox, oy)
            
    def drawEventPoint(self, dc, tx, ty, ox, oy):
        
        cont = self.getContentPanel()
        
        if cont.getCurrentEvent() and self.map == cont.map:
            
            x, y, w, h = cont.getCurrentEventCoords()
            realX = (x - tx) * 24 - ox
            realY = (y - ty) * 24 - oy
            dc.SetPen(self.mapViewPanel.eventCoordPen)
            dc.DrawRoundedRectangle(realX+4, realY+4, w*24-8, h*24-8, 4)
            dc.CrossHair(realX+w*12, realY+h*12)
            
    def updateContext(self, context=None):
        
        if context is None:
            context = self.viewerContext
            
        self.viewerContext = context
            
        if self.inited:
            
            self.mapViewPanel.drawFunc = None
            self.passes = []
            
            if self.viewerContext == consts.VC_EVENT_WARP:
                
                self.mapViewPanel.drawFunc = self.drawWarpPoints
                
            elif self.viewerContext == consts.VC_EVENT_COPY:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[0]["condition"] = lambda obj: not obj.copyBlank
                self.passes[0]["pen"] = self.mapViewPanel.copySrcPen
                self.passes[0]["x1"] = lambda obj: obj.srcx
                self.passes[0]["y1"] = lambda obj: obj.srcy
                self.passes[0]["x2"] = lambda obj: obj.srcx + obj.width
                self.passes[0]["y2"] = lambda obj: obj.srcy + obj.height

                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.getCurrentEvent()
                self.passes[1]["pen"] = self.mapViewPanel.copyDestPen
                self.passes[1]["line"] = True
                self.passes[1]["point"] = lambda obj: obj.copyType != 0
                self.passes[1]["x1"] = lambda obj: obj.destx
                self.passes[1]["y1"] = lambda obj: obj.desty
                self.passes[1]["x2"] = lambda obj: obj.destx + obj.width
                self.passes[1]["y2"] = lambda obj: obj.desty + obj.height
                    
            elif self.viewerContext == consts.VC_EVENT_ITEM:
                
                self.mapViewPanel.drawFunc = self.drawEventPoint
                    
            elif self.viewerContext == consts.VC_AREA:
                
                self.mapViewPanel.drawFunc = self.drawDraggingRect

                self.passes.append({})
                self.passes[0]["obj"] = lambda cont: cont.curArea
                self.passes[0]["pen"] = self.mapViewPanel.eventCoordPen
                self.passes[0]["xline"] = True
                self.passes[0]["x1"] = lambda obj: obj.l1x1
                self.passes[0]["y1"] = lambda obj: obj.l1y1
                self.passes[0]["x2"] = lambda obj: obj.l1x2 + 1
                self.passes[0]["y2"] = lambda obj: obj.l1y2 + 1
                    
                self.passes.append({})
                self.passes[1]["obj"] = lambda cont: cont.curArea
                self.passes[1]["condition"] = lambda obj: obj.hasLayer2
                self.passes[1]["pen"] = self.mapViewPanel.floorPen
                self.passes[1]["xline"] = True
                self.passes[1]["x1"] = lambda obj: obj.l2x
                self.passes[1]["y1"] = lambda obj: obj.l2y
                self.passes[1]["x2"] = lambda obj: obj.l2x + obj.l1x2 - obj.l1x1 + 1
                self.passes[1]["y2"] = lambda obj: obj.l2y + obj.l1y2 - obj.l1y1 + 1
                
            self.curEditText.SetLabel(self.vcTexts[self.viewerContext])
            self.sideSizer.Layout()
        
    def setViewPos(self, x, y):
        s = self.mapViewPanel.scale
        maxX = self.map.width * 24
        maxY = self.map.height * 24
        sizeX, sizeY = self.mapViewPanel.GetSize()
        self.mapViewPanel.curViewX = max(0, min(maxX - sizeX / s, x))
        self.mapViewPanel.curViewY = max(0, min(maxY - sizeY / s, y))
        self.mapViewBarX.SetThumbPosition(x)
        self.mapViewBarY.SetThumbPosition(y)
        #self.refreshMapView()
        
    def refreshMapView(self):
        
        """"""pix = [""] * 24 * self.viewHeight
        
        for i in range(self.viewWidth * self.viewHeight):
            x = (i % self.viewWidth)
            y = (i / self.viewWidth)
            mx = self.curViewX + x
            my = self.curViewY + y
            blkIdx = self.map.layoutData[my*64+mx] & 0x3ff
            blk = self.map.blocks[blkIdx]
            for r in range(24):
                pix[r+y*24] += blk.pixels[r]""""""
            
        #for i,p in enumerate(self.mapViewPanels):
        #    mx = self.curViewX + (i % self.viewWidth)
        #    my = self.curViewY + (i / self.viewWidth)
        #    blk = self.map.layoutData[my*64+mx] & 0x3ff
        #    p.pixels = self.map.blocks[blk].pixels
        
        #self.mapViewPanel.pixels = pix
        #self.mapViewPanel.Refresh(False)
        
        #self.mapViewPanel.curViewX = self.curViewX
        #self.mapViewPanel.curViewY = self.curViewY
        #self.mapViewPanel.Refresh(False)
        
        #self.Refresh(False)
        #self.Freeze()
        #for p in self.mapViewPanels:
        #    p.Refresh()
        #self.Thaw()
        
        if self.inited:
            self.mapViewPanel.Refresh()
        
        pass
        
    def changeMap(self, map, palette):
        
        if map != self.map or palette != self.palette:
            
            if map is not None:
                self.map = map
            if palette is not None:
                self.palette = palette

            if hasattr(self.getContentPanel(), "updateMapViewerContext"):
                self.getContentPanel().updateMapViewerContext()
            else:
                self.updateContext(self.viewerContext)
            
            if not self.map.loaded:
                self.getContentPanel().rom.getMaps(self.curMapIdx, self.curMapIdx)

            self.mapViewPanel.changeMap(self.map, self.palette)

            self.mapViewPanel.curViewX = 0
            self.mapViewPanel.curViewY = 0
            self.mapViewPanel.Refresh()
            
            self.setViewPos(0, 0)
            self.updateScrollbars()
 
    def updateScrollbars(self):
        
        s = self.mapViewPanel.scale
        x = self.mapViewPanel.GetSize()[0] / s
        y = self.mapViewPanel.GetSize()[1] / s
        
        #print "(%i,%i)" % (x,y)
        self.mapViewBarX.SetScrollbar(self.curViewX, x, self.map.width * 24, 120)
        self.mapViewBarY.SetScrollbar(self.curViewY, y, self.map.height * 24, 120)
        
    curViewX = property(lambda self: self.mapViewPanel.curViewX)
    curViewY = property(lambda self: self.mapViewPanel.curViewY)
    curMapIdx = property(lambda self: self.mapList.GetSelection())
        
    getContentPanel = lambda self: self.mainFrame.contentPanel #.subPanel
        
    vcTexts = ["Nothing", "Blocks", "Flags", "Event:Warp", "Event:Copy", "Event:Item", "Area"]
    
    scales = [.25, .33, .5, .75, 1, 1.5, 2, 3, 5]"""