import wx
import rompanel

class DefaultPanel(rompanel.ROMPanel):
    
    def init(self):
        
        sbox1 = wx.StaticText(self, -1, "This feature is not implemented yet.")
        self.sizer.Add(sbox1, pos=(0,0), flag=wx.EXPAND)

class SF2EditPanel(rompanel.ROMPanel):
    
    def init(self):
        
        sbox1 = wx.StaticText(self, -1, "This feature is not implemented yet.")
        sbox2 = wx.StaticText(self, -1, "However, it is implemented in SF2Edit.exe.")
        self.sizer.Add(sbox1, pos=(0,0), flag = wx.EXPAND | wx.BOTTOM, border=10)
        self.sizer.Add(sbox2, pos=(1,0), flag = wx.EXPAND)