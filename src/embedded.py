
#
#   embedded.py
#   Keep standard text files TadsPad uses around in embedded form so we don't need to have a bunch of extra
#   text files in the installation
#

# embedded start.t file
start = u"""#charset "us-ascii"

#include <tads.h>
#include "advlite.h"


/*
 *
 *	$TITLE$
 *	by
 *	$AUTHOR$
 *
 *
 *	$FILENAME$
 *
 *
 */


versionInfo: GameID
    IFID = '$IFID$'
    name = '$TITLE$'
    byline = 'by $AUTHOR$'
    htmlByline = 'by <a href="mailto:$EMAIL$">$AUTHOR$</a>'
    version = '1'
    authorEmail = '$AUTHOR$ <$EMAIL$>'
    desc = '$DESC$'
    htmlDesc = '$HTMLDESC$'
;

gameMain: GameMainDef
    /* Define the initial player character; this is compulsory */
    initialPlayerChar = me
;


/* The starting location; this can be called anything you like */

startroom: Room 'The Starting Location'
    "Add your description here. "
;

/*
 *   The player character object. This doesn't have to be called me, but me is a
 *   convenient name. If you change it to something else, remember to change
 *   gameMain.initialPlayerChar accordingly.
 */

+ me: Thing 'you'
    isFixed = true
    person = 2  // change to 1 for a first-person game
    contType = Carrier
;

"""

# embedded blank.t
blank = u"""#charset "us-ascii"

#include <tads.h>
#include "advlite.h"


/*
 *
 *
 *	$FILENAME$
 *
 *	for
 *
 *	$TITLE$
 *
 *
 *
 */


"""

# embedded standard makefile
makefile = u"""
# TADS 3 makefile
#
# Warning: this file was mechanically generated.  You may edit this file
# manually, but your changes might be modified or discarded when
# you load this file into a TADS development tool.  The TADS tools
# generally retain the comment at the start of the file and the
# comment marked "##sources" below, but other comments might be
# discarded, the formatting might be changed, and some option
# settings might be modified.



-o $NAME$.t3
-pre
-D LANGUAGE=english
-w1
-Fy obj -Fo obj
$LIBRARY$


##sources
$SOURCE$

"""

# embedded web makefile
web_makefile = u"""

# TADS 3 makefile
#
# Warning: this file was mechanically generated.  You may edit this file
# manually, but your changes might be modified or discarded when
# you load this file into a TADS development tool.  The TADS tools
# generally retain the comment at the start of the file and the
# comment marked "##sources" below, but other comments might be
# discarded, the formatting might be changed, and some option
# settings might be modified.



-o $NAME$.t3
-pre
-D LANGUAGE=english
-w1
-Fy obj -Fo obj
-D TADS_INCLUDE_NET
-source tadsnet
$LIBRARY$

##sources
$SOURCE$

"""


# embedded ignore
ignore = u"""
us-ascii
advlite.h
mailto
$IFID$
$TITLE$
$AUTHOR$
$EMAIL$
$FILENAME$
dobj
iobj
subj
obj
"""

# embedded tips
tips = u"""You can spell check any file you're working on in TadsPad if you have the Internet connected. Just have the file open in the editor and press "F7."
To navigate to a specific object in a TADS project, double-click the object in the Object Browser panel. Even if the file containing the object isn't currently open, TadsPad will pull it up for you.
If your project has produced errors on compilation, you can double-click the error in the Compile Output panel and TadsPad will pull up the line with the offending code.
TadsPad features context sensitive help. To learn about an adv3Lite specific property or method, simply click on it or move the caret to it with the arrow keys. Help text will appear in the Context Help panel.
If you don't like the default panel layout, you can drag and dock any panel to any side of the screen, or simply float them as independent windows.
TadsPad hooks into the TADS compiler and interpreter. It can usually guess where both exist on a given system, but if you need to change the defaults, simply click Edit->Executable Path from the menu bar.
If you don't like the font size or colors, you change them easily from Edit->Text Settings on the menu bar.
If a transcript from the last game run-thru is available, you can view it from Tools->View Transcript on the menu bar, or simply press "F6". You can run the game up to any command by double-clicking one of the commands on the Transcript View Window.
You can pull up the full Tads/adv3Lite documentation at any time by pressing "F1".
TadsPad is fully cross-platform. You can work on the same game (with none of the text character weirdness inherent to platform hopping) from any machine.
Code completion recognizes game objects with custom members. The code recognition database refreshes with each project save, so if code completion is not working, try saving your work.
When creating a new project, you have the option of using a "custom" library. This gives you the ability to use the adv3Liter library in conjunction with whatever adv3Lite source files and extensions you choose, giving your game setup maximum flexibility.
"""

# embedded themes
# start with obsidian
obsidian = u"""<?xml version="1.0" encoding="utf-8"?>
<colorTheme id="21" name="Obsidian" modified="2011-02-01 16:43:47" author="Morinar">
    <searchResultIndication color="#616161" />
    <filteredSearchResultIndication color="#616161" />
    <occurrenceIndication color="#616161" />
    <writeOccurrenceIndication color="#616161" />
    <findScope color="#E0E2E4" />
    <deletionIndication color="#E0E2E4" />
    <sourceHoverBackground color="#FFFFFF" />
    <singleLineComment color="#7D8C93" />
    <multiLineComment color="#7D8C93" />
    <commentTaskTag color="#FF8BFF" />
    <javadoc color="#7D8C93" />
    <javadocLink color="#678CB1" />
    <javadocTag color="#E0E2E4" />
    <javadocKeyword color="#A082BD" />
    <class color="#678CB1" />
    <interface color="#678CB1" />
    <method color="#678CB1" />
    <methodDeclaration color="#E8E2B7" />
    <bracket color="#E8E2B7" />
    <number color="#FFCD22" />
    <string color="#EC7600" />
    <operator color="#E8E2B7" />
    <keyword color="#93C763" />
    <annotation color="#A082BD" />
    <staticMethod color="#E0E2E4" />
    <localVariable color="#E0E2E4" />
    <localVariableDeclaration color="#E0E2E4" />
    <field color="#678CB1" />
    <staticField color="#678CB1" />
    <staticFinalField color="#E0E2E4" />
    <deprecatedMember color="#E0E2E4" />
    <enum color="#E0E2E4" />
    <inheritedMethod color="#E0E2E4" />
    <abstractMethod color="#E0E2E4" />
    <parameterVariable color="#E0E2E4" />
    <typeArgument color="#E0E2E4" />
    <typeParameter color="#E0E2E4" />
    <constant color="#A082BD" />
    <background color="#293134" />
    <currentLine color="#2F393C" />
    <foreground color="#E0E2E4" />
    <lineNumber color="#81969A" />
    <selectionBackground color="#804000" />
    <selectionForeground color="#E0E2E4" />
</colorTheme>
"""

# mr
mr = u"""<?xml version="1.0" encoding="utf-8"?>
<colorTheme id="32" name="Mr" modified="2011-01-26 22:56:17" author="Jongosi" website="http://TwinCreations.co.uk">
    <searchResultIndication color="#D8D8D8" />
    <filteredSearchResultIndication color="#D8D8D8" />
    <occurrenceIndication color="#000000" />
    <writeOccurrenceIndication color="#000000" />
    <sourceHoverBackground color="#D8D8D8" />
    <singleLineComment color="#FF9900" />
    <multiLineComment color="#FF9900" />
    <commentTaskTag color="#FF3300" />
    <javadoc color="#FF3300" />
    <javadocLink color="#990099" />
    <javadocTag color="#990099" />
    <javadocKeyword color="#990099" />
    <class color="#006600" />
    <interface color="#666666" />
    <method color="#000099" />
    <methodDeclaration color="#000099" />
    <bracket color="#000099" />
    <number color="#0000FF" />
    <string color="#CC0000" />
    <operator color="#0000FF" />
    <keyword color="#0000FF" />
    <annotation color="#990000" />
    <staticMethod color="#990000" />
    <localVariable color="#0066FF" />
    <localVariableDeclaration color="#000099" />
    <field color="#000099" />
    <staticField color="#552200" />
    <staticFinalField color="#552200" />
    <deprecatedMember color="#D8D8D8" />
    <enum color="#FF0000" />
    <inheritedMethod color="#000099" />
    <abstractMethod color="#000099" />
    <parameterVariable color="#0000FF" />
    <typeArgument color="#0000FF" />
    <typeParameter color="#006600" />
    <constant color="#552200" />
    <background color="#FFFFFF" />
    <currentLine color="#D8D8D8" />
    <foreground color="#333333" />
    <lineNumber color="#D8D8D8" />
    <selectionBackground color="#D8D8D8" />
    <selectionForeground color="#333333" />
</colorTheme>
"""

# minimal
minimal = u"""<?xml version="1.0" encoding="utf-8"?>
<colorTheme id="43" name="minimal" modified="2011-01-27 17:26:58" author="meers davy">
    <searchResultIndication color="#EFEFEF" />
    <filteredSearchResultIndication color="#EFEFEF" />
    <occurrenceIndication color="#EFEFEF" />
    <writeOccurrenceIndication color="#EFEFEF" />
    <findScope color="#BCADff" />
    <deletionIndication color="#aaccff" />
    <sourceHoverBackground color="#EEEEEE" />
    <singleLineComment color="#334466" />
    <multiLineComment color="#334466" />
    <commentTaskTag color="#666666" />
    <javadoc color="#05314d" />
    <javadocLink color="#05314d" />
    <javadocTag color="#05314d" />
    <javadocKeyword color="#05314d" />
    <class color="#000066" />
    <interface color="#000066" />
    <method color="#5c8198" />
    <methodDeclaration color="#5c8198" />
    <bracket color="#000066" />
    <number color="#333333" />
    <string color="#333333" />
    <operator color="#333333" />
    <keyword color="#5c8198" />
    <annotation color="#AAAAFF" />
    <staticMethod color="#5c8198" />
    <localVariable color="#5c8198" />
    <localVariableDeclaration color="#5c8198" />
    <field color="#566874" />
    <staticField color="#05314d" />
    <staticFinalField color="#05314d" />
    <deprecatedMember color="#ab2525" />
    <enum color="#000066" />
    <inheritedMethod color="#5c8198" />
    <abstractMethod color="#5c8198" />
	<constant color="#A082BD" />
    <parameterVariable color="#5c8198" />
    <typeArgument color="#5c8198" />
    <typeParameter color="#5c8198" />
    <background color="#ffffff" />
    <currentLine color="#aaccff" />
    <foreground color="#000000" />
    <lineNumber color="#666666" />
    <selectionBackground color="#Efefff" />
    <selectionForeground color="#000066" />
</colorTheme>
"""

# pastal
pastel = u"""<?xml version="1.0" encoding="utf-8"?>
<colorTheme id="68" name="Pastel" modified="2011-01-30 00:51:47" author="Ian Kabeary" website="http://iank.ca">
    <searchResultIndication color="#616161" />
    <filteredSearchResultIndication color="#616161" />
    <occurrenceIndication color="#616161" />
    <writeOccurrenceIndication color="#616161" />
    <findScope color="#E0E2E4" />
    <deletionIndication color="#E0E2E4" />
    <sourceHoverBackground color="#FFFFFF" />
    <singleLineComment color="#7D8C93" />
    <multiLineComment color="#7D8C93" />
    <commentTaskTag color="#a57b61" />
    <javadoc color="#7D8C93" />
    <javadocLink color="#678CB1" />
    <javadocTag color="#E0E2E4" />
    <javadocKeyword color="#A082BD" />
    <class color="#678CB1" />
    <interface color="#678CB1" />
    <method color="#678CB1" />
    <methodDeclaration color="#95bed8" />
    <bracket color="#95bed8" />
    <number color="#c78d9b" />
    <string color="#c78d9b" />
    <operator color="#E8E2B7" />
    <keyword color="#a57b61" />
    <annotation color="#A082BD" />
    <staticMethod color="#E0E2E4" />
    <localVariable color="#E0E2E4" />
    <localVariableDeclaration color="#E0E2E4" />
    <field color="#678CB1" />
    <staticField color="#678CB1" />
    <staticFinalField color="#E0E2E4" />
    <deprecatedMember color="#E0E2E4" />
    <enum color="#E0E2E4" />
    <inheritedMethod color="#E0E2E4" />
    <abstractMethod color="#E0E2E4" />
    <parameterVariable color="#E0E2E4" />
    <typeArgument color="#E0E2E4" />
    <typeParameter color="#E0E2E4" />
    <constant color="#A082BD" />
    <background color="#1f2223" />
    <currentLine color="#2F393C" />
    <foreground color="#E0E2E4" />
    <lineNumber color="#81969A" />
    <selectionBackground color="#95bed8" />
    <selectionForeground color="#E0E2E4" />
</colorTheme>
"""

# solarized
solarized = u"""<?xml version="1.0" encoding="utf-8"?>
<colorTheme id="1013" name="Solarized Light" modified="2011-04-02 23:38:38" author="George" website="http://ethanschoonover.com/solarized">
    <searchResultIndication color="#ECE7D5" />
    <filteredSearchResultIndication color="#ECE7D5" />
    <occurrenceIndication color="#ECE7D5" />
    <writeOccurrenceIndication color="#ECE7D5" />
    <findScope color="#BCADAD" />
    <deletionIndication color="#657A81" />
    <sourceHoverBackground color="#ECE7D5" />
    <singleLineComment color="#93A1A1" bold="false" italic="true" />
    <multiLineComment color="#586E75" italic="true" />
    <commentTaskTag color="#D33682" italic="true" />
    <javadoc color="#586E75" italic="false" />
    <javadocLink color="#D30102" underline="false" strikethrough="false" />
    <javadocTag color="#D30102" />
    <javadocKeyword color="#D30102" />
    <class color="#657A81" />
    <interface color="#657A81" />
    <method color="#657A81" />
    <methodDeclaration color="#657A81" />
    <bracket color="#657A81" />
    <number color="#2AA198" />
    <string color="#2AA198" />
    <operator color="#657A81" />
    <keyword color="#B58900" bold="false" />
    <annotation color="#D30102" />
    <staticMethod color="#657A81" />
    <localVariable color="#657A81" />
    <localVariableDeclaration color="#657A81" />
    <field color="#657A81" />
    <staticField color="#657A81" />
    <staticFinalField color="#657A81" />
    <deprecatedMember color="#657A81" />
    <enum color="#657A81" />
    <inheritedMethod color="#657A81" />
    <abstractMethod color="#657A81" />
    <parameterVariable color="#657A81" />
    <typeArgument color="#657A81" />
    <typeParameter color="#657A81" />
    <constant color="#00FF00" />
    <background color="#FDF6E3" />
    <currentLine color="#FDF6E3" />
    <foreground color="#657A81" />
    <lineNumber color="#586E75" />
    <selectionBackground color="#ECE7D5" />
    <selectionForeground color="#596D73" />
</colorTheme>
"""


__author__ = 'dj'
