#!/usr/bin/python

import wx
import wx.html as html
from wx.html import HtmlEasyPrinting

ID_PRINT = 1

page = '<html>'

class Printer(HtmlEasyPrinting):
    global page
    
    def __init__(self):
        HtmlEasyPrinting.__init__(self)

    def GetHtmlText(self,text):
        "Simple conversion of text.  Use a more powerful version"
        return page

    def Print(self, text, doc_name):
        self.SetHeader(doc_name)
        self.PrintText(self.GetHtmlText(text),doc_name)

    def PreviewText(self, text, doc_name):
        self.SetHeader(doc_name)
        HtmlEasyPrinting.PreviewText(self, self.GetHtmlText(text))
        

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title, numRows):
        wx.Frame.__init__(self, parent, id, title, size=(500, 350))

        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.BuildReport(numRows)
        
        htmlwin = html.HtmlWindow(panel, -1, style=wx.NO_BORDER)
        htmlwin.SetBackgroundColour(wx.RED)
        htmlwin.SetStandardFonts()
        htmlwin.SetPage(page)

        vbox.Add((-1, 10), 0)
        vbox.Add(htmlwin, 1, wx.EXPAND | wx.ALL, 9)

        buttonOk = wx.Button(panel, ID_PRINT, 'Print Report')

        self.Bind(wx.EVT_BUTTON, self.OnPrint, id=ID_PRINT)

        hbox.Add((100, -1), 1, wx.EXPAND | wx.ALIGN_RIGHT)
        hbox.Add(buttonOk, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        vbox.Add(hbox, 0, wx.EXPAND)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnClose(self, event):
        self.Close()

    def OnPrint(self, e):
        print "OnPrint: called"
        # do the printing, then close the window
        printer = Printer()
        printer.Print(page, "Employee Certification Report")
        self.Close()

    def BuildReport(self, numRows):
        global page
        
        page = '<html><body bgcolor="#8e8e95">'

        page += '<h1>Employee Certifications Report</h1></br>'

        page += '<table cellspacing="5" border="0" width="450">'
        
        for i in range(numRows):
            page += '<tr width="200" align="left">' + \
            '<td bgcolor="#e7e7e7">&nbsp;&nbsp;' + 'Row' + str(i) + '</td>' + \
            '<td bgcolor="#aaaaaa">&nbsp;&nbsp;<b>' + str((numRows*1000) + (i*100)) + '</b></td>' + \
            '</tr> '

        page += '</body></table></html>'
        
app = wx.App(0)
MyFrame(None, -1, 'Basic Statistics', 10)
app.MainLoop()
