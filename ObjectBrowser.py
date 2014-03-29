
import wx
import codecs
import MessageSystem
import TClass



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
        master = ''
        for file_name in files:
            try:
                with codecs.open(path + "/" + file_name, 'rU', "utf-8") as f:
                    file_contents = f.read()
            except IOError, e:
                MessageSystem.error("Could not load file: " + e.filename, "File read error")

            # if the file can be read, update objects from the file
            else:
                if file_contents:
                    master += file_contents
                    TClass.search(self.notebook.objects, file_contents, "object", file_name)
                    for o in self.notebook.objects.values():

                        # update members in objects
                        TClass.get_all_object_members(o, self.notebook.classes)

        # update classes which contain 'modify' keyword
        TClass.modify(master, self.notebook.classes)
        TClass.cross_reference(self.notebook.classes)

        # now update the notebook objects list box
        for index, o in enumerate(sorted(self.notebook.objects.iterkeys(), key=lambda s: s.lower())):
            self.InsertStringItem(index, self.notebook.objects[o].name)
            self.SetStringItem(index, 1, str(self.notebook.objects[o].file))
            self.SetStringItem(index, 2, str(self.notebook.objects[o].line))
