import wx
import sys
sys.path.insert(0, '../')
import util

class ROMFrame(wx.MDIChildFrame):
    
    def __init__(self, parent, id, rpc, *args, **kwargs):
        
        if rpc.canMaximize:
            wx.MDIChildFrame.__init__(self, parent, id, *args, **kwargs)
        else:
            wx.MDIChildFrame.__init__(self, parent, id, style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX, *args, **kwargs)

        self.parent = parent
        
        self.outerPanel = wx.Panel(self, -1)
        self.outerPanel.parent = parent

        self.outerPanel.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.outerPanel.SetSizer(self.outerPanel.sizer)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.sizer.Add(self.outerPanel, 1, wx.EXPAND)
        
        self.wasMaximized = False
        
        self.SetTitle(rpc.frameTitle)

        self.contentPanel = rpc(self.outerPanel, -1, self.parent.rom)
        self.contentPanel.updateModifiedIndicator(False)
        
        self.outerPanel.sizer.Add(self.contentPanel, 0, wx.ALL, 10)
        self.outerPanel.sizer.Fit(self.outerPanel)
        #panel.SetMaxSize(cpanel.GetSize())

        self.sizer.Fit(self)
        
        if not self.contentPanel.canMaximize:
            self.bestSize = self.GetSize()
            self.SetMaxSize(self.bestSize)
            #self.ToggleWindowStyle(wx.MAXIMIZE_BOX)
    
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def OnMaximize(self, evt):
        
        self.wasMaximized = True
        
    def OnSize(self, evt):
        
        isMax = self.IsMaximized()
        
        if hasattr(self, "bestSize"):
            
            if isMax:
                self.SetMaxSize((-1,-1))
                self.SetSize(self.parent.GetSize())
            else:
                self.SetMaxSize(self.bestSize)
                self.wasMaximized = False
            #self.SetMaxSize(self.bestSize)
            
        evt.Skip()
        
    def OnMinimize(self, evt):
        
        if hasattr(self, "bestSize"):
            
            self.SetMaxSize((-1,-1))
            self.SetSize(self.parent.GetSize())
        
        evt.Skip()
                
    def OnClose(self, evt):
        
        self.parent.frames.remove(self)
        
        evt.Skip()
        
class ROMPanel(wx.Panel):
    
    frameTitle = "Editor"
    canMaximize = False
    
    def __init__(self, parent, id, rom, **kwargs):
        
        wx.Panel.__init__(self, parent, id, **kwargs)
        
        self.parent = parent.parent
        self.rom = rom
        self.sizer = wx.GridBagSizer(4, 4)
        self.SetSizer(self.sizer)
        
        self.helpText = {}
        
        self.Hide()
        
        self.init()
        
        wx.EVT_SHOW(self, self.ShowHandler)
        
        self.Show()
        
    def init(self):
        pass

    def modify(self, obj=None):
        
        if not obj:
            obj = self.getCurrentData()
            
        obj.modified = True
        self.modified =True
        self.parent.modify()
        
        if hasattr(self, "treeItem"):
            self.parent.layoutTree.modify(self.treeItem)
            
        # OLD: self.updateModifiedIndicator(True)
    
    def commit(self, action):
        
        us = self.parent.tempUndoStack
        rs = self.parent.tempRedoStack
        if not us.has_key(self):
            us[self] = []
        us[self].append(action)
        
        if rs.has_key(self):
            rs[self] = []
        
        #self.parent.updateUndoRedo()
        
    def updateModifiedIndicator(self, val):
        
        # OLD:
        """if val:
            self.parent.modifiedPanel.SetBackgroundColour("#FF0000")
        else:
            self.parent.modifiedPanel.SetBackgroundColour("#00FF00")
        
        self.parent.modifiedPanel.Refresh()"""
        # /OLD
        
        # legacy code, too lazy to remove it
        
        pass
    
    def updateCurrentDataName(self, idx, string):
        
        data = self.getCurrentData()
        
        if not data.hasCustomName and string != data.name:
            
            data.hasCustomName = True
            
            token = "%i:" % idx
            loc = string.find(token)
            
            if loc != -1:
                start = loc + len(token)
            else:
                start = 0
            
            newName = "%i: " % idx + string[start:].lstrip().rstrip()
            data.name = newName
        
    def addHelpText(self, obj, header, text):
        
        id = obj.GetId()
        
        if id:
            self.helpText[obj.GetId()] = [header, text]
            #wx.EVT_MOUSE_EVENTS(obj, self.OnGetHelpForItem)
            
    def SetROM(self, rom):
        self.rom = rom
    
    def OnGetHelpForItem(self, evt):
        
        #print "\n".join(dir(evt))
        
        id = evt.GetId()

        #print `evt.Entering()` + ", " + `evt.Leaving()`

        parent = self.parent

        if evt.Entering() and parent.helpPanel.IsEnabled():
            
            if id in self.helpText.keys():

                parent.helpHeader.SetLabel(self.helpText[id][0])
                parent.helpText.SetLabel(self.helpText[id][1])
                parent.helpPanel.GetSizer().Layout()
                parent.helpText.Wrap(parent.helpPanel.GetSize()[0])
                #parent.

        evt.Skip()
        
    def ShowHandler(self, evt):
        if evt.GetShow():
            self.OnShow(evt)
        else:
            self.OnHide(evt)
            
    def OnShow(self, evt):
        evt.Skip()
        
    def OnHide(self, evt):
        evt.Skip()
    
    def getCurrentData(self):
        return None

class HexBox(wx.TextCtrl):
    
    def __init__(self, parent, id, **kwargs):
        wx.TextCtrl.__init__(self, parent, id, **kwargs)
        self.SetFont(parent.parent.editFont)
        self.SetForegroundColour("#B0B0B0")
        self.SetEditable(False)
        
class HexListBox(wx.ListBox):

    def __init__(self, parent, id, **kwargs):
        wx.ListBox.__init__(self, parent, id, **kwargs)
        self.SetFont(parent.parent.editFont)
        self.SetForegroundColour("#B0B0B0")
        self.SetWindowStyle(wx.TE_PROCESS_TAB)
        #self.SetEditable(False)
    
    def SetContents(self, text):
        self.Clear()
        t2s = lambda t: util.tabs2spaces(t, 8)
        self.AppendItems(map(t2s, text.splitlines()))
        
class ColorPanel(wx.Panel):
    
    def __init__(self, parent, id, color, size=(20,20), num=None, enable=True):
        
        wx.Panel.__init__(self, parent, id)
        self.color = color
        self.num = num
        self.SetBackgroundColour(color)
        self.SetSize(size)
        
        if enable:
            wx.EVT_LEFT_DOWN(self, self.OnClick)
        
    def OnClick(self, evt):
        self.GetParent().changeEditColor(self.num)


class ColorPanel2(wx.Panel):
    
    def __init__(self, parent, id, color, size=(20,20), num=None, enable=True):
        
        wx.Panel.__init__(self, parent, id)
        self.color = color
        self.num = num
        self.SetBackgroundColour(color)
        self.SetSize(size)
        
        if enable:
            wx.EVT_MOUSE_EVENTS(self, self.OnClick)
        
    def OnClick(self, evt):
        if evt.LeftDown():
            self.GetParent().changeEditColor(0, self.num)
        elif evt.RightDown():
            self.GetParent().changeEditColor(1, self.num)
        
        
class SpritePanel(wx.Panel):
    
    def __init__(self, parent, id, width, height, palette, pixels=[], scale=1, edit=False, bg=15, xpad=0, ypad=0, func=None, grid=False, draw=None, **kwargs):
        wx.Panel.__init__(self, parent, id, **kwargs)

        if self.alphaBMP is None:
            self.alphaBMP = wx.Bitmap("alpha.png")
            self.selectBrush = wx.Brush(wx.Colour(0,0,128), wx.SOLID)
            self.selectBrush2 = wx.Brush(wx.Colour(0,128,0), wx.SOLID)
            self.selectBrush3 = wx.Brush(wx.Colour(192,192,192), wx.SOLID)
            self.magentaBrush = wx.Brush(wx.Colour(255,0,255), wx.SOLID)
            self.transPen = wx.Pen(wx.Colour(0,0,0,0), 1)
            self.transBrush = wx.Brush(wx.Colour(0,0,0,0), wx.TRANSPARENT)
            self.gridPen = wx.Pen(wx.Colour(0,0,0,128), 1)
            
            self.obsPen = wx.Pen(wx.Colour(255,0,0), 5)
            self.zonePen = wx.Pen(wx.Colour(0,0,255), 5)
            self.eventPen = wx.Pen(wx.Colour(0,255,0), 5)
            self.stairsPen = wx.Pen(wx.Colour(0,255,255), 5)
            self.chestPen = wx.Pen(wx.Colour(255,255,0), 7)
            self.barrelPen = wx.Pen(wx.Colour(255,128,64), 7)
            self.vasePen = wx.Pen(wx.Colour(224,224,255), 7)
            self.floorPen = wx.Pen(wx.Colour(0,255,0), 7)
            self.tablePen = wx.Pen(wx.Colour(255,255,255), 5)
            self.roofPen1 = wx.Pen(wx.Colour(255,255,255), 5)
            self.roofPen2 = wx.Pen(wx.Colour(128,128,128), 5)
            self.roofPen3 = wx.Pen(wx.Colour(255,128,128), 5)
            self.otherPen = wx.Pen(wx.Colour(255,255,0), 5)
            
            self.darkBGBrush = wx.Brush(wx.Colour(32,32,32), wx.SOLID)
            
        self.width = width
        self.height = height
        self.xpad = xpad
        self.ypad = ypad
        self.palette = palette
        self.pixels = pixels
        self.scale = scale
        self.bg = bg
        self.buffer = None
        self.func = func
        self.grid = grid
        self.drawFunc = draw
        self.flip = False
        
        self.pixelsStack = []
        self.bmpStack = []
        
        self.SetSize((width,height))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.refreshSprite(pixels)
        
        wx.EVT_PAINT(self, self.OnPaint)
        
        if func == "edit":
            wx.EVT_MOUSE_EVENTS(self, self.OnEdit)
        elif edit:
            wx.EVT_MOUSE_EVENTS(self, func)
        else:
            wx.EVT_LEFT_DOWN(self, func)
    
    def SetSize(self, size):
        
        w = size[0]*self.scale + self.xpad*2
        h = size[1]*self.scale + self.ypad*2
        wx.Panel.SetSize(self, (w,h))
        
    def refreshSprite(self, pixels=None, force=False):
        
        rt = self.palette.rgbaTuples()
        
        if pixels is not None:
            self.pixels = pixels
            
        if self.flip: 
            self.pixels = [p[::-1] for p in self.pixels] #[reversed(p) for p in self.pixels]
            
        if force:
            self.pixelsStack = []
            self.bmpStack = []
            
        if self.pixels not in self.pixelsStack:
        
            buf = ""
            for row in self.pixels:
                for p in row:
                    for t in rt[int(p, 16)]:
                        buf += chr(t)
            
            extra = max(0, self.width*self.height*4 - len(buf))
            buf += chr(0) * extra
            
            #print "-------------"
            #print `self.height`
            #print `self.width`
            #print `(len(buf)/4)/64`
            
            self.bmp = wx.BitmapFromBufferRGBA(self.width, self.height, buf)

            self.pixelsStack.append(self.pixels[:])
            self.bmpStack.append(self.bmp)
            
        else:
            
            self.bmp = self.bmpStack[self.pixelsStack.index(self.pixels)]

    def OnPaint(self, evt):

        px = self.xpad
        py = self.ypad
        
        #if self.buffer:
        #    dc = wx.BufferedPaintDC(self, wx.Bitmap())
        #else:
        s = self.scale
        
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.SetPen(wx.Pen(self.GetBackgroundColour(), 1))
        dc.DrawRectangle(0, 0, s*self.width + px*2, s*self.height + py*2)
        
        dc.SetUserScale(s,s)

        if self.bg == 16:
            bgBrush = wx.Brush(self.GetBackgroundColour(), wx.STIPPLE)
            bgBrush.SetStipple(self.alphaBMP)
            bgPen = self.transPen
            bgPen.SetStipple(self.alphaBMP)
        elif self.bg == 17:
            bgBrush = self.selectBrush
            bgPen = None
        elif self.bg == 18:
            bgBrush = self.selectBrush2
            bgPen = None
        elif self.bg == 19:
            bgBrush = self.selectBrush3
            bgPen = None
        elif self.bg == 20:
            bgBrush = self.magentaBrush
            bgPen = None
        elif self.bg is not None:
            bgBrush = wx.Brush(self.palette.colors[self.bg], wx.SOLID)
            bgPen = wx.Pen(self.palette.colors[self.bg], 1)
            
        brushes = [wx.Brush(self.palette.colors[j], wx.SOLID) for j in range(1,16)]
        pens = [wx.Pen(self.palette.colors[j], 0) for j in range(1,16)]
        
        if self.bg is not None:
            if bgPen:
                dc.SetPen(bgPen)
            dc.SetBrush(bgBrush)
            dc.DrawRectangle(0, 0, s*self.width + px*2, s*self.height + py*2)
        
        dc.DrawBitmap(self.bmp, px/2, py/2)
        
        if self.drawFunc:
            self.drawFunc(self, dc)

        dc.SetUserScale(1, 1)
            
        if self.grid:
            
            dc.SetPen(self.gridPen)
            dc.SetBrush(self.transBrush)
            
            rects = []
            for y in range(0, int(self.scale * self.height), int(self.grid * self.scale)):
                for x in range(0, int(self.scale * self.width), int(self.grid * self.scale)):
                    rects.append((x-1, y-1, x+self.grid*self.scale+1, y+self.grid*self.scale+1))
            dc.DrawRectangleList(rects, self.gridPen, self.transBrush)
            
            #dc.DrawLine(0, 0, s*self.width + px*2, 0)
            #dc.DrawLine(0, 0, 0, s*self.height + py*2)
        
        evt.Skip()
        
    def OnEdit(self, evt):
        
        if evt.LeftIsDown() or evt.RightIsDown():
            
            tileWidth = self.width / 8
            tileHeight = self.height / 8
            
            parent = self.GetParent()
            
            color1 = self.GetParent().color_left
            color2 = self.GetParent().color_right

            x = evt.GetX()/self.scale
            y = evt.GetY()/self.scale
            
            m = self.GetParent().mode
            
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return
            
            spr = self.GetParent().getCurrentSpriteObject()
            
            if hasattr(spr, "raw_pixels"):
                oldpix = spr.raw_pixels[:]
                if hasattr(parent, "frame"):
                    oldpix2 = spr.raw_pixels2[:]
                
            if evt.ShiftDown():

                col = int(self.pixels[y][x], 16)
                if evt.LeftIsDown():
                    
                    try:
                        self.GetParent().color_left = col
                        scl = self.GetParent().selectedColorLeft
                        scl.color = col
                        scl.SetBackgroundColour(self.GetParent().palette.colors[scl.color])
                        scl.Refresh()
                    except:
                        pass
                
                else:
                    
                    try:
                        self.GetParent().color_right = col
                        scr = self.GetParent().selectedColorRight
                        scr.color = col
                        scr.SetBackgroundColour(self.GetParent().palette.colors[scr.color])
                        scr.Refresh()
                    except:
                        pass
            
            elif m == 0:   # single pixel
                
                if evt.LeftIsDown():
                    color = color1
                else:
                    color = color2
                color = hex(color)[2:]
                    
                if self.pixels[y][x] != str(color):
                    
                    self.pixels[y] = self.pixels[y][:x] + color + self.pixels[y][x+1:]
                    parent.modify()
                    
                    spr = parent.getCurrentSpriteObject()
                        
                    frame = 1
                    if not hasattr(parent, "frame") or parent.frame == 0:
                        frame = 0
                    spr.setPixel(x,y,color,frame)

                    self.refreshSprite()
                    self.Refresh()
                    self.GetParent().refreshPixels()
            
            elif m == 1:   # floodfill
                
                if evt.LeftIsDown():
                    color = color1
                else:
                    color = color2
                color = hex(color)[2:]
                    
                findColor = self.pixels[y][x]
                
                current = [(x,y)]
                checked = []
                next = []
                
                while current:
                    
                    for c in current:
                        
                        #print `c`
                        
                        x,y = c
                        
                        if x < 0 or x >= self.width or y < 0 or y >= self.height or c in checked:
                            continue
                            
                        if self.pixels[y][x] != findColor:
                            continue
                        
                        spr = parent.getCurrentSpriteObject()
                        
                        self.pixels[y] = self.pixels[y][:x] + color + self.pixels[y][x+1:]

                        frame = 1
                        if not hasattr(parent, "frame") or parent.frame == 0:
                            frame = 0
                        spr.setPixel(x,y,color,frame)
                                
                        parent.modify()
                        
                        checked.append(c)
                        
                        pixelLeft = (x-1,y)
                        pixelUp = (x,y-1)
                        pixelRight = (x+1,y)
                        pixelDown = (x,y+1)
                        
                        if pixelLeft not in checked:
                            next.append(pixelLeft)
                        if pixelUp not in checked:
                            next.append(pixelUp)
                        if pixelRight not in checked:
                            next.append(pixelRight)
                        if pixelDown not in checked:
                            next.append(pixelDown)
                        
                    current = next[:]
                    next = []
                
                self.refreshSprite()
                self.Refresh()
                self.GetParent().refreshPixels()
                
            elif m == 2:   # replace
                
                if evt.LeftIsDown():
                    color = color1
                else:
                    color = color2
                color = hex(color)[2:]
                    
                if self.pixels[y][x] != str(color):
                    
                    repl = self.pixels[y][x]
                    
                    # MAKE SURE TO ADD IN RAW_PIXELS CHANGES
                    
                    for y,row in enumerate(self.pixels):
                        self.pixels[y] = row.replace(repl, color)
                    
                    self.GetParent().modify()
                    
                    
                    
                    frame = 1
                    if not hasattr(parent, "frame") or parent.frame == 0:
                        frame = 0
                    
                    if frame == 0:
                        spr.raw_pixels = spr.raw_pixels.replace(repl, color)
                    else:
                        spr.raw_pixels2 = spr.raw_pixels2.replace(repl, color)
                    
                    self.refreshSprite()
                    self.Refresh()
                    self.GetParent().refreshPixels()
    
            else:
                return
            
            if spr and hasattr(spr, "raw_pixels"):
                dif = (oldpix != spr.raw_pixels) or (hasattr(parent, "frame") and oldpix2 != spr.raw_pixels2)
                if dif:
                    if not hasattr(parent, "frame"):
                        parent.commit([[oldpix], [spr.raw_pixels[:]]])
                    else:
                        parent.commit([[oldpix, oldpix2], [spr.raw_pixels[:], spr.raw_pixels2[:]]])
                    
    alphaBMP = None
    selectBrush = None

class MapViewPanel(wx.Panel):
    
    def __init__(self, parent, id, width, height, palette, pixels=[], scale=1, edit=False, bg=15, xpad=0, ypad=0, func=None, grid=False, draw=None, **kwargs):
        wx.Panel.__init__(self, parent, id, **kwargs)

        if self.alphaBMP is None:
            self.alphaBMP = wx.Bitmap("alpha.png")
            self.selectBrush = wx.Brush(wx.Colour(0,0,128), wx.SOLID)
            self.selectBrush2 = wx.Brush(wx.Colour(0,128,0), wx.SOLID)
            self.selectBrush3 = wx.Brush(wx.Colour(192,192,192), wx.SOLID)
            self.transPen = wx.Pen(wx.Colour(0,0,0,0), 1)
            self.transBrush = wx.Brush(wx.Colour(0,0,0,0), wx.TRANSPARENT)
            self.gridPen = wx.Pen(wx.Colour(0,0,0), 1)
            
            thinW = 3
            thickW = 5
            
            self.obsPen = wx.Pen(wx.Colour(255,0,0), thinW)
            self.zonePen = wx.Pen(wx.Colour(0,0,255), thinW)
            self.eventPen = wx.Pen(wx.Colour(0,255,0), thinW)
            self.stairsPen = wx.Pen(wx.Colour(0,255,255), thinW)
            self.chestPen = wx.Pen(wx.Colour(255,255,0), thickW)
            self.barrelPen = wx.Pen(wx.Colour(255,128,64), thickW)
            self.vasePen = wx.Pen(wx.Colour(224,224,255), thickW)
            self.floorPen = wx.Pen(wx.Colour(0,255,0), thickW)
            self.tablePen = wx.Pen(wx.Colour(255,255,255), thinW)
            self.roofPen1 = wx.Pen(wx.Colour(255,255,255), thinW)
            self.roofPen2 = wx.Pen(wx.Colour(128,128,128), thinW)
            self.roofPen3 = wx.Pen(wx.Colour(255,128,128), thinW)
            self.otherPen = wx.Pen(wx.Colour(255,255,0), thinW)
            
            self.eventCoordPen = wx.Pen(wx.Colour(255,255,0), thickW)
            self.warpCoordPen = wx.Pen(wx.Colour(255,128,0), thickW)
            self.copySrcPen = wx.Pen(wx.Colour(0,255,255), thickW)
            self.copyDestPen = wx.Pen(wx.Colour(192,192,192), thickW)
            
            self.darkBGBrush = wx.Brush(wx.Colour(32,32,32), wx.SOLID)
            
        self.width = width
        self.height = height
        self.xpad = xpad
        self.ypad = ypad
        self.palette = palette
        self.pixels = pixels
        self.scale = scale
        self.bg = bg
        self.buffer = None
        self.func = func
        self.grid = grid
        self.drawFunc = draw
        
        self.drawBlocks = True
        self.drawFlags = True
        
        self.curViewX = 0
        self.curViewY = 0
        
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        #self.SetSize((width, height))
    
        wx.EVT_PAINT(self, self.OnPaint)
        
        if func == "edit":
            wx.EVT_MOUSE_EVENTS(self, self.OnEdit)
        elif edit:
            wx.EVT_MOUSE_EVENTS(self, func)
        else:
            wx.EVT_LEFT_DOWN(self, func)
    
    def changeMap(self, map, palette):
        
        self.map = map
        self.palette = palette
        self.blockBMPs = []
        self.updateBlockBMPs()
        
    def updateBlockBMPs(self, idx=None):
        
        if idx:
            redo = [idx]
        else:
            redo = range(len(self.map.blocks))
        
        if not self.blockBMPs:
            self.blockBMPs = [None] * len(self.map.blocks)
        
        rt = self.palette.rgbaTuples()
        
        for idx in redo:
            
            blk = self.map.blocks[idx]
            
            buf = ""
            
            for row in blk.pixels:
                for p in row:
                    for t in rt[int(p, 16)]:
                        buf += chr(t)
            
            self.blockBMPs[idx] = wx.BitmapFromBufferRGBA(24, 24, buf)
            
        self.Refresh()
            
    def OnPaint(self, evt):
        
        #fdc = wx.PaintDC(self)
        
        self.width, self.height = self.GetSize()
        
        dc = wx.AutoBufferedPaintDC(self) #, wx.EmptyBitmap(self.width, self.height))
        
        #print `self.GetSize()`
        
        cont = self.GetGrandParent()
        s, px, py = self.scale, self.xpad, self.ypad
        
        if self.bg == 16:
            bgBrush = wx.Brush(self.GetBackgroundColour(), wx.STIPPLE)
            bgBrush.SetStipple(self.alphaBMP)
            bgPen = self.transPen
            bgPen.SetStipple(self.alphaBMP)
        elif self.bg == 17:
            bgBrush = self.selectBrush
            bgPen = None
        elif self.bg == 18:
            bgBrush = self.selectBrush2
            bgPen = None
        elif self.bg == 19:
            bgBrush = self.selectBrush3
            bgPen = None
        elif self.bg is not None:
            bgBrush = wx.Brush(self.palette.colors[self.bg], wx.SOLID)
            bgPen = self.gridPen #wx.Pen(self.palette.colors[self.bg], 1)

        blockW = int(24 * s)
        blockH = int(24 * s)
        
        if self.bg is not None:
            if bgPen:
                dc.SetPen(bgPen)
            dc.SetBrush(bgBrush)
            dc.DrawRectangle(0, 0, self.width + px*2, self.height + py*2)
        
        dc.SetUserScale(s,s)
        
        tWidth = self.width / blockW + 2
        tHeight = self.height / blockH + 2
        
        tViewX = int(self.curViewX) / 24
        tViewY = int(self.curViewY) / 24
        xofs = self.curViewX % 24
        yofs = self.curViewY % 24
        
        # draw actual block graphics
        
        if self.drawBlocks:
            
            for y in range(tHeight):
                for x in range(tWidth):
                    if tViewX+x < 64 and tViewY+y < 64:
                        idx = (tViewY+y) * 64 + (tViewX+x)
                        blk = self.map.layoutData[idx] & 0x3ff
                        dc.DrawBitmap(self.blockBMPs[blk], x*24 - xofs, y*24 - yofs)
                        
        else:

            dc.SetBrush(self.darkBGBrush)
            dc.SetPen(self.transPen)
            
            for y in range(tHeight):
                for x in range(tWidth):
                    if tViewX+x < 64 and tViewY+y < 64:
                        idx = (tViewY+y) * 64 + (tViewX+x)
                        px = x*24 - xofs
                        py = y*24 - yofs
                        dc.DrawRectangle(px, py, 24, 24)
        
        # draw flag graphics
        
        if self.drawFlags:
            
            dc.SetBrush(self.transBrush)
            
            for y in range(tHeight):
                for x in range(tWidth):
                    
                    if tViewX+x < 64 and tViewY+y < 64:
                        
                        idx = (tViewY+y) * 64 + (tViewX+x)
                        blk = self.map.layoutData[idx] & 0xfc00
                        
                        if blk:
                            
                            px = x*24 - xofs
                            py = y*24 - yofs
                            
                            mask = blk & 0x3c00
                            obsMask = blk & 0xc000
                            
                            noObs = False
                            noEvt = False
                            
                            if obsMask == 0xc000:
                                dc.SetPen(self.obsPen)
                                dc.DrawLine(px+4, py+4, px+20, py+20)
                                dc.DrawLine(px+20, py+4, px+4, py+20)
                            elif obsMask == 0x8000:
                                dc.SetPen(self.stairsPen)
                                dc.DrawLine(px+20, py+4, px+4, py+20)
                            elif obsMask == 0x4000:
                                dc.SetPen(self.stairsPen)
                                dc.DrawLine(px+4, py+4, px+20, py+20)
                            else:
                                noObs = True
                                
                            if mask == 0x1000:
                                dc.SetPen(self.zonePen)
                                dc.DrawRectangle(px+4, py+4, 16, 16)
                            elif mask == 0x1400:
                                dc.SetPen(self.eventPen)
                                dc.DrawRectangle(px+4, py+4, 16, 16)
                            elif mask == 0x1800:
                                dc.SetPen(self.chestPen)
                                dc.DrawCircle(px+12, py+4, 1)
                                dc.DrawCircle(px+20, py+12, 1)
                                dc.DrawCircle(px+12, py+20, 1)
                                dc.DrawCircle(px+4, py+12, 1)
                            elif mask == 0x1c00:
                                dc.SetPen(self.floorPen)
                                dc.DrawCircle(px+12, py+4, 1)
                                dc.DrawCircle(px+20, py+12, 1)
                                dc.DrawCircle(px+12, py+20, 1)
                                dc.DrawCircle(px+4, py+12, 1)
                            elif mask == 0x2c00:
                                dc.SetPen(self.vasePen)
                                dc.DrawCircle(px+12, py+4, 1)
                                dc.DrawCircle(px+20, py+12, 1)
                                dc.DrawCircle(px+12, py+20, 1)
                                dc.DrawCircle(px+4, py+12, 1)
                            elif mask == 0x3000:
                                dc.SetPen(self.barrelPen)
                                dc.DrawCircle(px+12, py+4, 1)
                                dc.DrawCircle(px+20, py+12, 1)
                                dc.DrawCircle(px+12, py+20, 1)
                                dc.DrawCircle(px+4, py+12, 1)
                            elif mask == 0x2800:
                                dc.SetPen(self.tablePen)
                                dc.DrawLine(px+4, py+12, px+20, py+12)
                                dc.DrawLine(px+12, py+4, px+12, py+20)
                            elif mask == 0x0800:
                                dc.SetPen(self.roofPen1)
                                dc.DrawCircle(px+12, py+12, 8)
                            elif mask == 0x0c00:
                                dc.SetPen(self.roofPen2)
                                dc.DrawCircle(px+12, py+12, 8)
                            elif mask == 0x0400:
                                dc.SetPen(self.roofPen3)
                                dc.DrawCircle(px+12, py+12, 8)
                            else:
                                noEvt = True

                            if blk & 0xfc00 and noObs and noEvt:
                                dc.SetPen(self.otherPen)
                                dc.DrawCircle(px+12, py+12, 8)                        
            
        dc.SetUserScale(1, 1)
        
        if self.grid:
            
            dc.SetPen(self.gridPen)
            dc.SetBrush(self.transBrush)
            
            rects = []
            for y in range(tHeight):
                for x in range(tWidth):
                    px = x*blockW-xofs*s
                    py = y*blockH-yofs*s
                    rects.append((px-1, py-1, self.grid*self.scale+1, self.grid*self.scale+1))
            dc.DrawRectangleList(rects, self.gridPen, self.transBrush)

        if self.drawFunc:
            dc.SetUserScale(s,s)
            self.drawFunc(dc, tViewX, tViewY, xofs, yofs)
            dc.SetUserScale(1,1)
            
        evt.Skip()
        
                
    alphaBMP = None
    selectBrush = None