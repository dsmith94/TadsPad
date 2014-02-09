
#
#   TADS Class search/datatype
#


import re

# regular expression patterns
class_pattern = re.compile("class\s(\w*):\s([\w|,|\s]*)", flags=re.S)
object_pattern = re.compile("(\w*):\s([\w|,|\s]*)")
block_comments = re.compile("/\*.*?\*/", flags=re.S)
method_pattern = re.compile("(\w*\((\w*)\))")
property_pattern = re.compile("(\w*)\s=")


class TClass:
    def __init__(self):

        # tads class definition

        self.name = ""
        self.code = ""
        self.help = ""
        self.line = 0
        self.file = ""
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
                if line is ';':
                    break
                self.code = self.code + line + '\n'
            index += 1

    def add_member(self, member):

        # add member to members array
        # replace if exists
        index = 0
        for m in self.members[:]:
            if m.name is member.name:

                # we have match, replace (but save the help if the one to be replace has none)
                self.members[index] = member
                return
            index += 1
        self.members.append(member)

    def find_members(self):

        # find members (properties and methods) of this class
        lines = self.code.split('\n')
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
                            self.add_member(TMember(name=match.group(1).strip(), line=index))
                    else:
                        match = method_pattern.match(line.strip())
                        if match:

                            # we have a method! add it to members list
                            self.add_member(TMethod(name=match.group(1).strip(), line=index, arguments=match.group(2)))
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


def extract(code):

    # extract a list of classes to return
    # look for class name, and comment

    # stage 1: clean code of bracketed enclosures, to avoid confusing parser
    code = clean(code)

    # stage 2: find classes by line numbers
    classes = index_classes(code)

    # stage 3: populate documentation by extracting comments, and get code
    for c in classes:
        c.help = find_comments(code, c.line)
        c.get_code_from_string(code)
        c.find_members()

        # stage 4: get documentation for each member of class
        for m in c.members:
            m.find_comments(c.code)

    return classes


def cross_reference(classes):

    # take a list of classes, find their inheritances, and connect applicable once together
    for c in classes:
        for i in c.inherits:
            for c2 in classes:
                if i == c2.name:
                    for m in c2.members:
                        c.add_member(m)


def index_classes(code):

    # stuff the classes objects with names and line numbers
    classes = []
    lines = code.split("\n")
    index = 0

    # iterate over each line in code
    for line in lines:

        # use regular expression engine to locate class on line
        match = class_pattern.match(line)
        if match:

            # we have a class here! save the index and name and subclasses
            c = TClass()
            c.line = index
            c.name = match.group(1)
            c.inherits = inherited(match.group(2))
            classes.append(c)

        index += 1

    return classes


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
