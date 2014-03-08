
import wx
import re
import MessageSystem
import operator
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

        self.notebook.objects = list()
        self.DeleteAllItems()

        # loop through all files in project, and get objects in each
        files = wx.GetTopLevelParent(self).project.files
        path = wx.GetTopLevelParent(self).project.path
        master = ''
        for file_name in files:
            try:
                f = open(path + "/" + file_name, 'r')
                file_contents = f.read()
                f.close()
            except IOError, e:
                MessageSystem.error("Could not load file: " + e.filename, "File read error")

            # if the file can be read, update objects from the file
            else:
                if file_contents:
                    master += file_contents
                    objects = TClass.search(file_contents, "object", file_name)
                    for o in objects:

                        # add object to our master object list
                        self.notebook.objects.append(o)

                        # update members in objects
                        TClass.get_all_members(o, self.notebook.classes)

        # and update the columns in the catalog
        self.notebook.objects = sorted(self.notebook.objects, key=operator.attrgetter('name'))

        # update classes which contain 'modify' keyword
        TClass.modify(master, self.notebook.classes)

        # now update the notebook objects list box
        index = 0
        for o in self.notebook.objects:
            self.InsertStringItem(index, o.name)
            self.SetStringItem(index, 1, str(o.file))
            self.SetStringItem(index, 2, str(o.line))
            index += 1





