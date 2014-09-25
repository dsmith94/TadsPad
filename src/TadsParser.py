
# TadsParser.py
# collection of routines to parse tads source code into python object


class TClass:

    def __init__(self):

        # new instance of tads class
        self.name = ""
        self.line = 0
        self.end = 0
        self.filename = ""
        self.help = ""
        self.members = {}
        self.keywords = []
        self.inherits = []

    def get_inherits(self, declaration):

        """
        Get set of inherited classes from a class declaration string
        returns list
        """

        self.inherits = get_inherits(declaration)


class TMember:

    def __init__(self):

        # new member of Tads class or object, complete with help context data
        self.name = ""
        self.line = 0
        self.help = ""


class TModify:

    def __init__(self):

        # init new modify
        self.name = u""
        self.line = 0
        self.end = 0
        self.members = {}


class TObject(TClass):

    def __init__(self):
        TClass.__init__(self)
        self.implemented = []

    def __check_actor(self, path):

        # by convention, all topic reponses are stored in same file as actor or actor state
        # look for all topics stored in a given object
        result = []

        # open file for actor object
        from codecs import open as open_unicode
        try:
            with open_unicode(path + "/" + self.filename, 'rU', "utf-8") as f:
                file_contents = f.read()

        except IOError, e:
            MessageSystem.error("Could not load file: " + e.filename, "File read error")
            return []

        # now perform search
        file_contents = clean(file_contents)
        file_contents = file_contents.split(u"\n")
        level = file_contents[self.line].count(u'+')
        code = file_contents[self.line + 1:]
        for line in code:
            if line:
                if line[0] != u' ' and u';' not in line:

                    # looks like we've got an object def of some kind
                    if u'+' in line:
                        if line.count(u'+') > level:

                            # and it is nested into the actor or actor state
                            # is it a topic of some kind?
                            if u'Topic' in line:

                                # it is, add to results
                                if u'@' in line:
                                    result.append(line[line.find(u'@') + 1:].strip())

                                elif u'[' in line:
                                    if u',' in line:
                                        buffer = line[line.find(u'[') + 1:line.find(u']')]
                                        buffer = buffer.split(u',')
                                        result.extend([o.strip() for o in buffer])
                                    else:
                                        result.append(line[line.find(u'[') + 1:line.find(u']')].strip())
                        else:

                            # we're no longer nesting objects into a state or actor, so quit search
                            return result

        return result

    def check(self, level, keywords=None, path=None):

        # check level of implementation for a given object
        # look for actor or actor state in inherits, but dont bother unless we have keywords to search against
        if keywords:

            # we're searching an actor state or actor, search level of implementation
            implemented = self.__check_actor(path)
            return [k for k in keywords if k not in implemented]

        else:

            return self.__check_thing(level)

    def __check_thing(self, level):

        # return implementation level of a thing object
        properties = [u'smellDesc', u'listenDesc', u'feelDesc', u'tasteDesc', u'bulk']
        if level == 'Standard':
            properties.extend([u'readDesc', u'objInPrep', u'listOrder', u'visibleInDark', u'bulkCapacity',
                               u'maxSingleBulk'])
        if level == 'Extensive':
            properties.extend([u'readDesc', u'objInPrep', u'listOrder', u'fluidName', u'visibleInDark',
                               u'isTransparent', u'isOpenable', u'isSwitchable', u'isWearable', u'isBoardable',
                               u'isEnterable', u'isLightable', u'isEdible', u'isDecoration', u'lockability',
                               u'isOpen', u'isLocked', u'isOn', u'isLit', u'wornBy', u'maxSingleBulk', u'bulkCapacity'])

        # now check this object for missing properties and return a list of properties
        result = []
        for p in properties:
            if p not in self.implemented:
                result.append(p)
        return result


def search(filename, final_classes, final_modifys, final_globals, final_actions):

    """
    search given filename, and populate classes, modifys and globals
    """

    classes = {}
    modifys = []
    global_objects = {}
    actions = []

    # open filename, harvest data from buffer
    from codecs import open as open_unicode
    try:
        with open_unicode(filename, 'rU', "utf-8") as fb:
            uncleaned = fb.read()
            cleaned = clean(uncleaned)
            classes.update(class_search(cleaned, uncleaned, filename))
            modifys.extend(modify_search(cleaned, filename))
            global_search(cleaned, uncleaned, filename, classes.values(), modifys, global_objects)
            actions.extend(action_search(cleaned))

    except IOError, e:
        MessageSystem.error("Could not load file: " + e.filename, "File read error")

    else:

        # add to our collective classes, modifys, global objects
        final_classes.update(classes)
        final_modifys.extend(modifys)
        final_globals.update(global_objects)
        final_actions.extend(actions)


def action_search(code):

    """
    Find all action definitions in passed string, return list
    """

    result = []
    tokens = (u"DefineIAction", u"DefineTAction", u"DefineTIAction", u"DefineTIAAction")

    # prepare code by cleaning it and splitting into lines
    lines = clean(code).split(u'\n')
    for line in lines:

        # search each line for our tokens
        for token in tokens:

            # do we have action in this line?
            if token in line:

                # found action, get name of action for our list
                start = line.find(token) + len(token) + 1
                end = len(line.strip()) - 1
                name = line[start:end]
                result.append(name)

    return result


def inherit_search(c, classes):

    """
    Ensure that all parent classes are in for inheritance purposes, recursive
    """

    # collect inherited classes and match them
    result = []
    for i in c.inherits:
        if i in classes:
            inherits = inherit_search(classes[i], classes)
            result.append(i)
            result.extend(inherits)
    return list(set(result))


def global_search(cleaned, uncleaned, filename, classes, modifys, globals_vars):

    """
    Search code for globals, after removing classes and modifys
    """

    lines = cleaned.split(u'\n')
    uncleaned = uncleaned.split(u'\n')

    # remove classes and modifys from lines
    for c in classes:
        for l in xrange(c.line, c.end):
            lines[l] = u"\n"
    for m in modifys:
        for l in xrange(m.line, m.end):
            lines[l] = u"\n"

    # parameters on which we skip adding as global - we don't need literally everything
    skip = u'Define', u'Replace', u'class', u'_', u'Init', u'Preinit', u'Global'

    # and now we look for globals in lines
    for index, line in enumerate(lines):

        # skip all those silly defines and replacers and classes
        if any(token in line for token in skip):
            continue

        # anything left should be a global
        if line:
            if line[0].isalnum():

                # literally anything else should be a global
                text = ""
                if u':' in line and u' ':
                    text = line[:line.find(u':')]
                    if u' ' in text:
                        text = None
                elif u'(' in line and u')' in line and u':' not in line:
                    text = line[:line.find(u')') + 1]
                if text:
                    new = TObject()
                    new.name = text
                    new.filename = filename
                    new.line = index
                    new.help = __get_documentation(uncleaned, new.line)
                    globals_vars[new.name] = new


def modify_search(code, filename):

    """
    Search code for modifys, and return list
    uses uncleaned code
    """

    result = []

    # separate code as a set of lines and remove indents
    lines = clean(code).split(u'\n')
    for index, line in enumerate(lines):
        line = line.strip()
        if line[:7] == 'modify ':

            # we've found a modify here, change the code in the class
            name = line[7:].strip('{').strip()

            # new modify here, add to modify list
            new = TModify()
            new.name = name
            new.filename = filename
            new.line = index
            new.end = index

            # find end of this modify
            for end_index, end_line in enumerate(lines[new.line:]):

                # semicolon - we've found the end of the modify
                if u';' in end_line:
                    new.end = end_index + index
                    break

            # now that we have start and end of class, search for members
            new.members = __member_search(lines[new.line:new.end])

            result.append(new)
    return result


def get_members(class_list, classes, modifys=None):

    """
    return members affiliated with a list of unicode class keys, with data from classes dict passed
    """

    result = []

    for c in class_list:
        if c in classes:

            # class match - the class exists. add members to result
            result.extend(classes[c].members.values())

            # return parent members as well
            for i in classes[c].inherits:
                if i in classes:
                    result.extend(classes[i].members.values())

            # modifys members as well
            if modifys:
                for m in modifys:
                    if m.name == c or m.name in classes[c].inherits:
                        result.extend(m.members.values())

    return result


def get_inherits(declaration):

    """
    Get class inheritances in a line
    """

    # find where inherited classes in declaration begins by looking for :
    # check also for dynamic objects
    start_index = declaration.find(u":")
    if not start_index:
        start_index = declaration.rfind(u"+")
    result = []
    if start_index:
        start_index += 1
        for c in declaration[start_index:]:

            # look for alphanumeric or comma
            if str(c).isalnum() or c == u',' or c == u' ':
                result.append(c)
            else:
                break
    result = u''.join(result)
    return [r.strip() for r in result.split(u',')]


def object_in_line(line):

    """
    Look for object in line - return class inheritances if it's there, else return nothing
    requires cleaned code
    """

    # make sure we're not looking at a class
    if u':' in line and u'class' not in line:
        return None

    # okay, we've found a colon, it's prolly an object
    # else look for ++
    if u'+' in line or u':' in line:
        classes = get_inherits(line)
        if classes:
            return classes
    return None


def object_search(code, filename):

    """
    search cleaned code for objects within file
    return dict of objects
    """

    result = {}

    # comb thru code line by line to find non-anonomous objects
    lines = code.split(u'\n')
    for index, line in enumerate(lines):
        if u':' in line and u'class' not in line:
            if line[0].isalnum() or line[0] == u'+':

                # we've found an object, and it's not a class. get name, line number and members
                name = line[:line.find(u":")]
                name = name.strip(u"+ ")
                if name:
                    new = TObject()
                    new.name = name
                    new.filename = filename
                    new.line = index
                    new.get_inherits(line)

                    # find end of this object
                    for end_index, end_line in enumerate(lines[new.line:]):

                        # semicolon - we've found the end of the object
                        if u';' in end_line:
                            new.end = end_index + index
                            break

                    # now that we have start and end of object, search for members
                    new.members = __member_search(lines[new.line:new.end])

                    # save the implemented members
                    new.implemented = new.members.keys()

                    # add new object
                    result[new.name] = new

    return result


def class_search(code, uncleaned, filename):

    """
    Search code for classes
    return dictionary of classes
    """

    result = {}

    # save non-cleaned code for later purpose
    uncleaned = uncleaned.split(u'\n')

    # separate code as a set of lines and remove indents
    lines = code.split(u'\n')
    for index, line in enumerate(lines):
        line = line.strip()
        if line[:6] == 'class ':

            # we've found a class here, find name of class and it's members and docs
            new = TClass()
            new.name = line[6:line.find(u":")]
            new.line = index
            new.get_inherits(line)
            new.filename = filename
            new.help = __get_documentation(uncleaned, new.line)

            # find end of this class
            for end_index, end_line in enumerate(lines[new.line:]):

                # semicolon - we've found the end of the class
                if u';' in end_line:
                    new.end = end_index + index
                    break

            # now that we have start and end of class, search for members
            new.members = __member_search(lines[new.line:new.end])

            # now get docs for members
            for m in new.members.values():
                m.help = __get_documentation(uncleaned, m.line + new.line)

            # add new class
            result[new.name] = new

    return result


def __get_documentation(lines, index):

    """
    Search for documentation in code (provided as a list of lines) near a given line number index
    """

    index -= 1
    try:
        if '*/' in lines[index]:

            # we've found a comment, capture help text here
            result = list()
            for line in reversed(lines[:index + 1]):
                result.append(line.strip(u'/* \r'))
                if '/*' in line:

                    # end of comment, return result
                    result.reverse()
                    return u' '.join(result).strip()
    except:
        return u"No help found on that keyword. "
    return u"No help found on that keyword. "


def __member_search(lines):

    """
    Search for members in a list of lines of code, return dict of members
    """

    result = {}
    for index, line in enumerate(lines):

        # look for equals sign (for members) or parenths (for methods)
        line = line.strip()
        line = line.replace(u' ', u'')
        if u'=' in line:
            if u'(' not in line or u'(' in line and line.find(u'=') < line.find(u'('):

                # we've found a member, add it to our results dict
                new = TMember()
                new.line = index
                new.name = line[0:line.find(u'=')]
                result[new.name] = new
                continue

        if u'(' in line and u')' in line:

            # we've found a method, add it to our results dict
            new = TMember()
            new.line = index
            #new.name = line[0:line.find(u')') + 1]
            name = []
            for i in line[0:line.find(u')') + 1]:
                if i.isalnum() or i == u',' or i == u'(' or i == u')':
                    capturing = True
                else:
                    capturing = False
                if capturing:
                    name.append(i)
            new.name = u''.join(name)
            result[new.name] = new

    # we're finished, return dictionary
    return result


def clean(code, brackets=True):

    """
    Clean code passed as string, return spaces instead of comments and strings, but preserve line numbers
    """
    clean_sequence = (__scrub_block_comments, __scrub_line_comments, __scrub_all_quotes)

    # return code scrubbed at each phase of the cleaning sequence
    for phase in clean_sequence:
        code = phase(code)

    # if brackets are true, clean them too
    if brackets:
        code = __scrub_brackets(code)

    return code


def replace_next(text, lst, old, new):

    """
    accepts a string, then replaces next in a list matching old substring with new
    also will potentially look for regular expression match, false by default
    used in find...replace stuff
    """

    # recursively replace all in string by replacing next position in a string
    try:
        next_index = lst.pop(0)
    except IndexError:
        return text
    else:
        new_length_difference = len(new) - len(old)
        sub_text1 = text[:next_index]
        sub_text2 = text[next_index + len(old):]
        for i in xrange(0, len(lst)):
            lst[i] += new_length_difference
        return replace_next(sub_text1 + new + sub_text2, lst, old, new)


def extract_strings(code):

    """
    Clean code of comments and regular code and escape quotes, preserving strings
    """

    comments = __scrub_block_comments, __scrub_line_comments
    escapes = u"\\\"", u"\\\'"

    # start by removing comments
    for remove in comments:
        code = remove(code)

    # remove escape quotes
    for remove in escapes:
        code = code.replace(remove, u"  ")

    # now remove all but strings
    result = []
    in_double = False
    in_single = False
    pointy_brackets_level = 0

    # comb thru string character by character
    for ch in code:

        # always add line endings
        if ch == u"\n":
            result.append(ch)
            continue

        # look for quotes and skip anything in pointy brackets
        if ch == u"\"" and not in_single:
            if in_double:
                in_double = False
            else:
                in_double = True
                result.append(u" ")
                continue
        if ch == u"\'" and not in_double:
            if in_single:
                in_single = False
            else:
                in_single = True
                result.append(u" ")
                continue
        if in_double or in_single:
            if ch == u"<":
                pointy_brackets_level += 1
            if ch == u">":
                if pointy_brackets_level > 0:
                    pointy_brackets_level -= 1
        else:
            pointy_brackets_level = 0

        # only add character to result if we're not inside pointy brackets
        if pointy_brackets_level == 0:
            if in_double or in_single:
                result.append(ch)
                continue
        result.append(u" ")

    # now finished, return result
    return u"".join(result)


def __scrub_block_comments(code):

    """
    Remove block comments from string, replace with spaces, preserve line numbering, return result
    """

    slash = False
    asterisk = False
    in_comment = False
    result = []

    # search string character by character
    for ch in code:

        # if not in comments, check for /*
        if not in_comment:

            # check for slash in string
            if ch == u'/':

                # slash, next look for asterisk
                if not slash:
                    slash = True
                    result.append(ch)
                    continue

            # do we have an asterisk?
            if ch == u'*' and slash:
                in_comment = True
                slash = False
                result[-1] = u' '
                result.append(u' ')
                continue

            else:
                if slash:
                    slash = False
            result.append(ch)

        # only spaces go in comments
        else:

            # we're done with comment if we have asterisk followed by slash
            if ch == u'*':
                if not asterisk:
                    asterisk = True
                    result.append(u' ')
                    continue

            # if we have *\ symbols, close comment
            if ch == u'/' and asterisk:
                in_comment = False

            # terminate asterisk flag if still on
            if asterisk:
                asterisk = False

            # in comments we add only spaces
            if ch != u'\n':
                result.append(u' ')
            else:
                result.append(u'\n')

    # we're finished
    return u''.join(result)


def __scrub_line_comments(code):

    """
    Remove line comments from string, replace with spaces, preserve line numbering, return result
    """

    slash = False
    in_comment = False
    result = []

    # search string character by character
    for ch in code:

        # check for slash in string
        if ch == u'/':

            # do we have two slashes in a row?
            if not slash:
                slash = True
            else:
                in_comment = True
                slash = False
                result[-1] = u' '
                result.append(u' ')
                continue

        else:
            if slash:
                slash = False

        # only spaces go in comments
        if in_comment:

            # we're done with comment if we have a line ending
            if ch == u'\n':
                in_comment = False
                result.append(u'\n')
                continue

            result.append(u' ')

        # otherwise everything goes in
        else:
            result.append(ch)

    # we're finished
    return u''.join(result)


def __scrub_brackets(code):

    """
    Scrub code of all brackets, like {}, replacing with spaces - return result
    """
    result = []
    level = 0

    # search string character by character
    for ch in code:

        # do we have bracket?
        if ch == u'{':

            # yes, skip these chars until we hit } at matching level
            level += 1
            result.append(u'{')
            continue

        # matching bracket, bring level down one
        if ch == u'}':

            if level > 0:
                level -= 1
                result.append(u'}')
                continue

        # always add newline
        if ch == u'\n':
            result.append(u'\n')
            continue

        # now, if we're in a set of brackets, add only spaces, otherwise add character directly
        if level == 0:
            result.append(ch)
        else:
            result.append(u' ')

    # we're finished
    return u''.join(result)


def __scrub_all_quotes(code):

    """
    Scrub code of " and ' style quotes
    """
    quotes = (u"\"", u"\'")
    return __scrub_quotes(code, quotes)


def __scrub_quotes(code, quotes):

    """
    Remove quoted strings (delineated by quote style) replaced with spaces from code passed as string, return result
    """

    in_escape_sequence = False
    in_quotes = False
    kind_of_quote = u''
    result = []

    # search character by character in code string
    for ch in code:

        # check for quote
        if ch in quotes and not in_escape_sequence:
            if in_quotes:
                if ch == kind_of_quote:
                    in_quotes = False
            else:
                in_quotes = True
                kind_of_quote = ch
            result.append(ch)
            continue

        # specific rules whilst in quotes
        if in_quotes:

            # only use spaces in quotes
            if ch != u'\n':
                result.append(u' ')
            else:
                result.append(u'\n')

            # skip escape quotes
            if in_escape_sequence:
                in_escape_sequence = False
                continue

            if ch == u'\\':
                in_escape_sequence = True
                continue

        else:
            result.append(ch)

    # we're finished
    return u''.join(result)


__author__ = 'dj'

