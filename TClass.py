
#
#   TADS Class search/datatype
#


import re

# regular expression patterns
class_pattern = re.compile("class\s(\w*):\s([\w|,|\s]*)\n", flags=re.S)
object_pattern = re.compile("(\+*\s)(\w*):\s?([\w|,|\s]*)(\'.*\')?(\s)?(@\w*)?(\s*)?\n")
block_comments = re.compile("/\*.*?\*/", flags=re.S)
method_pattern = re.compile("(\w*\((\w*)\))")
property_pattern = re.compile("(\w*)\s=")
modify_pattern = re.compile("\s*modify\s(\w*)")


class TClass:
    def __init__(self):

        # tads class definition

        self.name = ""
        self.code = ""
        self.help = ""
        self.line = 0
        self.end = 0
        self.file = ""
        self.pluses = 0
        self.parent = ""
        self.at = ""
        self.inherits = []
        self.members = []

    def __repr__(self):
        return repr((self.name, self.file, self.line, self.inherits))

    def get_code_from_string(self, string):

        # fill the class with code from this string, using line number
        lines = string.split('\n')
        index = 0
        for line in lines:
            if index > self.line:
                if line == ';':
                    break
                self.code = self.code + line + '\n'
            index += 1

    def add_member(self, members):

        # add list of members to members array
        # replace if exists
        for s in members:
            index = 0
            for m in self.members[:]:
                if m.name == s.name:

                    # we have match, replace (but save the help if the one to be replace has none)
                    self.members[index] = s
                    return
                index += 1
            self.members.append(s)

    def find_members(self, code):

        # find members (properties and methods) of this class
        lines = code.split('\n')
        within_block_comment = False
        index = 0
        for line in lines:

            # firstly, skip comments
            if '//' not in line:

                # check for block comments too
                if '/*' in line:
                    within_block_comment = True
                if within_block_comment is False:

                    # not in any comments, check for methods and properties
                    # equals sign usually means a property
                    if '=' in line:
                        match = property_pattern.match(line.strip())
                        if match:

                            # we have a property! add it to our members list
                            self.add_member([TMember(name=match.group(1).strip(), line=index)])

                    else:
                        match = method_pattern.match(line.strip())
                        if match:

                            # we have a method! add it to members list
                            self.add_member([TMethod(name=match.group(1).strip(), line=index, arguments=match.group(2))])
            if '*/' in line:
                within_block_comment = False
            index += 1


class TMember:
    def __init__(self, name, line):

        # class for members of a tads class
        self.name = name
        self.line = line
        self.help = ''
        self.type = 'property'

    def find_comments(self, string):

        # get comments for documentation on this tads object member
        self.help = find_comments(string, self.line)


class TMethod(TMember):
    def __init__(self, name, line, arguments):
        TMember.__init__(self, name, line)

        # a tads object method is also a member
        self.type = 'method'

        # usually it has some arguments, divide them by ',' and store in list
        self.arguments = arguments.split(',')
        self.arguments = [item.strip() for item in self.arguments]
        if self.arguments[0] is '':
            self.arguments = []


def search(data, code, pattern, filename=None):

    # search for definitions in code, and append/update current data dictionary
    # when we find a definition, collect the line and classes it inherits and members
    name = 1
    inherits = 2
    pluses = None
    parent = None
    if pattern == "class":
        pattern = class_pattern
    if pattern == "object":
        pattern = object_pattern
        pluses = 1
        name = 2
        inherits = 3
        parent = 6
    if pattern == "modify":
        pattern = modify_pattern
        inherits = None
    objects = pattern.finditer(code)
    ordered = []

    # search for objects
    for m in objects:

        # found an object definition
        # muwahahahahaha
        if m:

            # first check that object doesn't already exist
            object_code = code_extract(code, m.start())
            if m.group(name) in data:

                # it does! is the code the same?
                if data[m.group(name)].code == object_code:

                    # no change needed here, pass on
                    continue

            # otherwise, make new object and use it in data dictionary
            obj = TClass()
            obj.name = m.group(name)
            if filename:
                obj.file = filename
            if inherits:
                obj.inherits = inherited(m.group(inherits))
            if pluses:
                obj.pluses = len(m.group(pluses).strip())
            if parent:
                if m.group(parent):
                    if '@' in m.group(parent):
                        obj.parent = m.group(parent)
                        obj.parent = obj.parent[obj.parent.find('@') + 1:].strip()
            obj.line = code.count("\n", 1, m.start()) + 1
            obj.end = obj.line + obj.code.count("\n") + 1
            obj.code = object_code
            obj.find_members(clean(obj.code))
            ordered.append(obj)
            data[m.group(name)] = obj

    # if we did a search for pluses, handle object-parent pluses notation search
    find_parents(ordered)

    # we're done!


def find_parents(objects):

    # find the parents to a list of object from a set of pluses
    for index, o in enumerate(objects):

        # the parent is always the next object up with fewer pluses
        if o.pluses:
            for x in reversed(objects[:index]):
                if x.pluses < o.pluses:

                    # in case we have pluses and @ on the same object, it's probably a topic
                    if o.parent:
                        o.at = o.parent

                    # either way continue assigning
                    o.parent = x.name
                    break

    return objects


def modify(code, classes):

    # look for 'modify' keyword and retool affected classes
    code = clean(code)

    # we've got our list of mods!
    mods = {}
    search(mods, code, "modify")
    mods = mods.values()

    # go over list of classes and apply modifys
    for m in mods:
        if m.name in classes:
            classes[m.name].add_member(m.members)
    cross_modifys(mods, classes)


def code_extract(code, start=0):

    # extract object code from passed code string, return at ;
    # start at the index passed as "start"
    return code[start:code.find("\n;\n", start)]


def extract(code):

    # extract a list of classes to return
    # look for class name, and comment

    # stage 1: clean code of bracketed enclosures, to avoid confusing parser
    code = clean(code)

    # stage 2: find classes by line numbers
    classes = {}
    search(classes, code, "class")

    # stage 3: populate documentation by extracting comments, and get code
    for c in classes.values():
        c.help = find_comments(code, c.line)
        c.get_code_from_string(code)
        c.find_members(code)

        # stage 4: get documentation for each member of class
        for m in c.members:
            m.find_comments(c.code)

    return classes


def cross_modifys(modifys, classes):

    # when given a list of modifys, make sure the inherited classes get their new mods
    # this is faster than just calling cross ref all the time
    for m in modifys:
        for c in classes.values():
            if m.name in c.inherits:
                c.add_member(m.members)
            else:
                for i in c.inherits:
                    if i in classes:
                        classes[i].add_member(m.members)


def cross_reference(classes):

    # take a list of classes, find their inheritances, and connect applicable once together
    # [c.add_member(c2.members) for c in classes for i in c.inherits for c2 in classes if i == c2.name]

    for c in classes.values():
        c.inherits.extend(get_all_inherits(c, classes))
    for c in classes.keys():
        get_all_class_members(c, classes)


def get_all_inherits(x, classes):

    # find all the inherits classes for passed class (x) in classes
    result = []
    for i in x.inherits:
        if i in classes:
            result.extend(i)
            result.extend(get_all_inherits(classes[i], classes))
    return list(set(result))


def get_all_class_members(class_declaration, classes):

    # recursively return all members from a class declaration as a list
    # this search is for classes, not objects
    if class_declaration in classes:
        for i in classes[class_declaration].inherits:
            if i in classes:
                get_all_class_members(i, classes)
                if classes[i].members:
                    classes[class_declaration].members.extend(classes[i].members)
                    classes[class_declaration].members = list(set(classes[class_declaration].members))


def get_all_object_members(obj, classes):

    # recursively return all members from a class declaration as a list
    # this search is for objects
    if obj:
        [obj.members.extend(classes[i].members) for i in obj.inherits if i in classes]
        obj.members = list(set(obj.members))


def find_comments(string, position):

    # pull block comment from string (just above position)
    # return nicely formatted comment

    # prep string for searching - we only need the code up to line number (position)
    lines = string.split('\n')
    code = ""
    index = 0
    for line in lines:
        code = code + line + '\n'
        index += 1
        if index == position:
            break
    comments = ""

    # look for comments by two strings - /* and */
    start = code.rfind('/*')
    end = code.rfind('*/')
    if start > -1 and end > -1:
        comments = code[start:end]
        comments = comments.replace('/*', '')
        comments = comments.replace('*/', '')
        comments = comments.replace('*   ', '')
        comments = comments.replace('\n', '')
        comments = comments.replace('     ', ' ')
        comments = comments.replace('    ', ' ')
        comments = comments.replace('   ', ' ')
        comments = comments.replace('  ', ' ')
    return comments.strip()


def inherited(string):

    # return a list of inherited classes from a comma-delin string
    classes = string.split(",")
    cleaned = []
    for c in classes[:]:
        cleaned.append(c.strip())
    return cleaned


def clean(code):

    # remove bracketed enclosures from passed string
    return_value = ""
    brackets = 0
    code = code.replace(r"\'", "[$$single &&quotes&& &&goes&& here$$]")
    in_single_quotes = False
    in_double_quotes = False
    in_block_comments = False
    in_line_comments = False
    index = 0
    skip = False
    for c in code:

        # analyze code character by character to remove enclosures
        # first, we must not be in quotes or comments
        two_chars = code[index:index + 2]
        if "/*" in two_chars:
            in_block_comments = True
        if "*/" in two_chars:
            in_block_comments = False
        if "//" in two_chars:
            in_line_comments = True
        if in_line_comments and '\n' in c:
            in_line_comments = False
        if c is r"'" and not in_block_comments and not in_line_comments:
            if not in_single_quotes:
                in_single_quotes = True
            else:
                in_single_quotes = False
                skip = True
        if c is r'"' and not in_block_comments and not in_line_comments:
            if not in_double_quotes:
                in_double_quotes = True
            else:
                in_double_quotes = False
                skip = True
        if not in_single_quotes and not in_double_quotes and not skip:

            # add this char to string for return, if not in brackets
            if c is '{' and not in_block_comments and not in_line_comments:
                brackets += 1
            if brackets is 0:
                return_value += c
            if c is '}' and not in_block_comments and not in_line_comments:
                brackets -= 1
                if brackets < 0:
                    brackets = 0
        if skip:
            skip = False
        index += 1

    return_value = return_value.replace("[$$single &&quotes&& &&goes&& here$$]", r"\'")
    return return_value


__author__ = 'dj'
