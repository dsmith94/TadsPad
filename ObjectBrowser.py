
import wx
import codecs
import MessageSystem
import TadsParser



# object browser subsystem
# display all objects in a story at any given time


# this is what an object definition looks like to a regular expression machine
object_looks_like = "\+*\s*([a-zA-Z]*):"

# this is what the classes look like
classes_look_like = ": ([\w*|,|\s])*"


class ObjectBrowser(wx.ListCtrl):

    def __init__(self, notebook, parent):

        ## new instance of object browser
        wx.ListCtrl.__init__(self, parent=parent, style=wx.LC_REPORT | wx.BORDER_SUNKEN)

        # when object is activated use the ObjectActivated event
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.object_activated)

        # finalize columns and finish
        r = wx.Display().GetGeometry()
        self.InsertColumn(0, "Object", width=r.Width / 11)
        self.InsertColumn(1, "file")
        self.InsertColumn(2, "line")

        # set reference to notebook
        self.notebook = notebook

    def object_activated(self, event):

        # object in the object browser has been activated, call it up in the notebook
        obj = event.GetEventObject()
        index = event.GetIndex()

        file_name = str(obj.GetItem(index, 1).GetText())
        line_number = int(obj.GetItem(index, 2).GetText())
        self.notebook.find_page(file_name, line_number)

    def rebuild_object_catalog(self):

        # rebuild objects catalog from the source files listed in our makefile

        # no project? then exit
        if wx.GetTopLevelParent(self).project is None:
            return

        self.notebook.objects = {}
        self.DeleteAllItems()

        # loop through all files in project, and get objects in each
        files = wx.GetTopLevelParent(self).project.files
        path = wx.GetTopLevelParent(self).project.path
        for file_name in files:
            try:
                with codecs.open(path + "/" + file_name, 'rU', "utf-8") as f:
                    file_contents = f.read()
            except IOError, e:
                MessageSystem.error("Could not load file: " + e.filename, "File read error")

            # if the file can be read, update modifys objects from the file
            else:
                if file_contents:
                    self.notebook.modifys.extend(TadsParser.modify_search(file_contents, file_name))
                    self.notebook.objects.update(TadsParser.object_search(TadsParser.clean(file_contents), file_name))

        # now update the notebook objects list box
        for o in self.notebook.objects.values():

            # update members in objects
            o.members = TadsParser.get_members(o.inherits, self.notebook.classes, self.notebook.modifys)

        # and finally add to display box
        for index, o in enumerate(sorted(self.notebook.objects.iterkeys(), key=lambda s: s.lower())):
            self.InsertStringItem(index, self.notebook.objects[o].name)
            self.SetStringItem(index, 1, str(self.notebook.objects[o].filename))
            self.SetStringItem(index, 2, str(self.notebook.objects[o].line))
