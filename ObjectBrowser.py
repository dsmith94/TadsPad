
import wx
import re
import MessageSystem
import operator


# object browser subsystem
# display all objects in a story at any given time


# this is what an object definition looks like to a regular expression machine
object_looks_like = "\+*\s*([a-zA-Z]*):"

# this is what the classes look like
classes_look_like = ": ([\w*|,|\s])*"


class ObjectInMemory():

    def __init__(self):

        ## hang onto filename, linenumber, and definition
        ## along with class information

        self.classes = []
        self.filename = None
        self.definition = None
        self.line_number = None

    def __repr__(self):
        return repr((self.definition, self.filename, self.line_number, self.classes))


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

        self.notebook.objects = []
        self.DeleteAllItems()

        # loop through all files in project, and get objects in each
        files = wx.GetTopLevelParent(self).project.files
        path = wx.GetTopLevelParent(self).project.path
        for file_name in files:
            try:
                f = open(path + "/" + file_name, 'r')
                file_contents = f.read()
                f.close()
            except IOError, e:
                MessageSystem.error("Could not load file: " + e.filename, "File read error")

            # if the file can be read, update objects from the file
            if file_contents:
                list_of_objects = search_for_objects(file_contents, file_name)
                for o in list_of_objects:

                    # add object to our master object list
                    self.notebook.objects.append(o)

            # and update the columns in the catalog
            self.notebook.objects = sorted(self.notebook.objects, key=operator.attrgetter('definition'))

            index = 0
            for o in self.notebook.objects:
                self.InsertStringItem(index, o.definition)
                self.SetStringItem(index, 1, str(o.filename))
                self.SetStringItem(index, 2, str(o.line_number))
                index += 1


def search_for_objects(code, file_name):

    # search all the code provided and build an updated object dictionary

    # get a list of lines representing the code
    objects_list = []
    lines = code.split("\n")
    line_number = 0
    for line in lines:
        object_definition_search = re.search(object_looks_like, line)
        if object_definition_search:

            # we have an object definition, add to our list with the line number file and classes
            if object_definition_search.start(0) == 0:
                object_definition = object_definition_search.group(0).strip(":").strip("+").strip("\r").strip("\n").strip()
                if object_definition != "":
                    o = ObjectInMemory()
                    o.definition = object_definition
                    o.line_number = line_number
                    o.filename = file_name
                    search_for_classes = re.search(classes_look_like, line)
                    if search_for_classes:
                        classes = search_for_classes.group().strip(":").split(",")
                        for c in classes:
                            o.classes.append(c.strip("\n").strip("\r").strip(" "))
                    objects_list.append(o)

        line_number += 1

    # return finished list
    return objects_list





