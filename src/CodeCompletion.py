
#
#   Code Completion Context Object
#   For TadsPad Code analysis subsystem
#

import TadsParser


# english action construction tokens
verify_token = u"verify"
check_token = u"check"
action_token = u"action"
direct_token = u"dobjFor"
indirect_token = u"iobjFor"
accessory_token = u"aobjFor"
remap_direct_token = u"asDobjFor"
remap_indirect_token = u"asIobjFor"
remap_accessory_token = u"asAobjFor"


def context(caret, line, code):

    """
    Return new context object for code completion
    """

    # now, make a series of suggestions based on the current code
    analysis = set()

    # first check current line
    line_analysis = __search_line(line, caret)

    # if we have line analysis results, set suggestions now
    if line_analysis:
        analysis.add(line_analysis)
        return analysis

    # otherwise, continue to analyze cleaned code
    # look for various macros and templates
    macros = (__search_action_macros, __search_vca_macros, __search_procedural_code)
    for macro in macros:
        m = macro(code)
        if m:
            analysis.add(m)

    return analysis


def __search_procedural_code(code):

    """
    Determine if we're in a procedure, and return objects if so
    """

    if u'{' in code:
        return 'objects'


def __search_vca_macros(code):

    """
    Search cleaned code for verify, check and action macros
    Really all we care about it verify
    """
    if verify_token in code:
        return 'verify'


def __search_action_macros(code):

    """
    Search cleaned code and return action macros in code
    """

    # scan cleaned code for action macros
    tokens = (direct_token, indirect_token, accessory_token)
    for token in tokens:
        if token in code:
            return token
    return None


def __search_line(line, caret):

    """
    Take line and caret and return analysis of line
    """

    # scan current line and return suggestion flags
    # the order here is important, by the way
    line = line[:caret]
    remaps = ((direct_token, remap_direct_token),
              (indirect_token, remap_indirect_token),
              (accessory_token, remap_accessory_token))
    for action, remap in remaps:
        if action in line:
            return remap
    if u'@' in line:
        return 'objects'
    if u'decorationActions = [' in line:
        return 'actions'
    #if u'return action is in (' in line:
    #    return 'actions'
    if u'[' in line and u']' not in line:
        return 'objects'
    if u'=' in line:
        if u'.' in line:
            if line.find(u'=') > line.find(u'.'):
                return 'objects'
        else:
            return 'objects'
    if len(line) > 2:
        if line[0] == '+' or line[1] == '+':
            return 'classes'
    if u':' in line:
        return 'classes'
    if u'.' in line and u')' not in line:
        if u'(' not in line[line.rfind(u'.'):]:
            return 'properties'
    if u'(' in line and u')' not in line:
        return 'objects'
    return None


__author__ = 'dj'
