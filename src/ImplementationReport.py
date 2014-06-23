
# class handling implementation report window

import wx
import TadsParser
import MessageSystem

class Box(wx.Frame):
    def __init__(self, type, project, notebook, extent="Minimal"):
        wx.Frame.__init__(self, None, title="Implementation Report: " + type, style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        # build report what has/hasn't been programming into current project
        self.project = project
        self.notebook = notebook
        r = wx.Display().GetGeometry()
        self.Size = (r.Width - r.Width / 10, r.Height / 2)
        self.type = type
        self.extent = extent
        self.report_text = wx.TextCtrl(self, -1, u"", wx.DefaultPosition, (r.Width - r.Width / 10, r.Height / 2), style=wx.NO_BORDER | wx.TE_MULTILINE)
        self.report_text.SetEditable(False)
        self.copy_button = wx.Button(parent=self)
        self.copy_button.SetHelpText("Copy Report to Clipboard")
        self.copy_button.SetLabel("Copy Text")
        self.copy_button.Bind(wx.EVT_BUTTON, self.copy_report)
        self.CloseButton = wx.Button(parent=self)
        self.CloseButton.SetHelpText("Close Current Find/Replace Window")
        self.CloseButton.SetLabel("Close")
        self.CloseButton.Bind(wx.EVT_BUTTON, self.CustomCloseButtonEvent)
        self.status = self.CreateStatusBar()
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(self.copy_button)
        buttons.Add(self.CloseButton)
        sizer.Add(self.report_text, 0, wx.EXPAND | wx.ALL, border=r.Width / 100)
        sizer.Add(buttons, 1, wx.EXPAND | wx.ALL, border=r.Width / 75)
        self.SetSizer(sizer)
        self.Fit()
        self.Update()
        self.__show_report()

    def __show_report(self):

        # show report onscreen, depending on type

        if self.type == "Actor":
            self.report_text.SetValue(self.__actor_report())
        else:
            self.report_text.SetValue(self.__thing_report())

    def __thing_report(self):

        # generate thing report and return it
        result = u"Thing Implementation Report for: " + self.project.name
        objects = []
        for o in self.notebook.objects.values():
            inherits = TadsParser.inherit_search(o, self.notebook.classes)
            if u'Thing' in inherits and u'Room' not in inherits:
                objects.append(o)
        number = str(len(objects))
        result = result + u"\nTotal number of Thing objects: " + number + u"\n"
        for o in objects:
            result = result + u'\n\n' + o.name
            for p in o.check(self.extent):
                result = result + u"\n    " + p

        return result

    def __actor_report(self):

        # generate actor report text and return it
        path = self.project.path
        result = u"Actor Implementation Report for: " + self.project.name
        number_of_actors = str(len([o for o in self.notebook.objects.values() if u'Actor' in o.inherits]))
        number_of_states = str(len([o for o in self.notebook.objects.values() if u'ActorState' in o.inherits]))
        result = result + u"\nTotal number of Actors: " + number_of_actors + u"\nTotal number of Actor States:" + \
            number_of_states + u"\n"
        for o in self.notebook.objects.values():

            # search actor and actor states
            object_mixins = TadsParser.inherit_search(o, self.notebook.classes)
            if u'ActorState' in object_mixins or u'Actor' in object_mixins:

                # only find things and topics for conversations, not game meta objects
                keywords = []
                for keyword in self.notebook.objects.values():
                    inherits = TadsParser.inherit_search(keyword, self.notebook.classes)
                    if u'Thing' in inherits or u'Topic' in inherits:
                        keywords.append(keyword.name)

                result = result + u"\n\n" + o.name + u":"
                items = o.check(None, keywords, path)
                for i in items:
                    result = result + u"\n    " + i

        return result

    def copy_report(self, event):

        # copy report to clipboard
        clipdata = wx.TextDataObject()
        text = self.report_text.GetValue()
        clipdata.SetText(text)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()

    def CustomCloseButtonEvent(self, event):

        # press close button
        self.Destroy()


__author__ = 'dj'
