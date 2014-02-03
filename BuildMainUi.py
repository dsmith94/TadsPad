
#
#   library collection that calls a sequence of functions to build main ui system
#

import wx
import wx.lib.agw.aui as aui
import MessageSystem
import CodeNotebook
import ObjectBrowser
import MessagePane
import ProjectBrowser


def init(top_window):

    # add the controls that will make up the top window
    create_menu_system(top_window)
    create_status_bar(top_window)
    create_notebook(top_window)
    create_object_browser(top_window)
    create_message_pane(top_window)


def create_message_pane(top_window):

    # show message pane
    r = wx.Display().GetGeometry()
    top_window.message_pane = MessagePane.MessagePane(top_window)
    the_pane = aui.AuiPaneInfo()
    the_pane.MinSize(r.Width, r.Height / 6)
    the_pane.Bottom()
    the_pane.Caption("Message Pane")
    top_window.mgr.AddPane(top_window.message_pane, the_pane)
    top_window.mgr.Update()
    top_window.message_pane.show_message("")


def create_object_browser(top_window):

    # show object browser and project browser
    local_panel = wx.Panel(top_window)
    r = wx.Display().GetGeometry()
    local_panel.SetSize((r.Width / 5, r.Width / 5))
    top_window.object_browser = ObjectBrowser.ObjectBrowser(top_window.notebook, parent=local_panel)
    top_window.project_browser = ProjectBrowser.ProjectBrowser(top_window.object_browser, parent=local_panel)
    the_pane = aui.AuiPaneInfo()
    the_pane.MinSize((r.Width / 5, r.Width / 5))
    the_pane.RightSnappable()
    the_pane.Right()
    the_pane.Caption("Project View")
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(top_window.object_browser, 1, wx.EXPAND | wx.ALL)
    sizer.Add(top_window.project_browser, 1, wx.EXPAND | wx.ALL)
    sizer.SetMinSize((r.Width / 5, r.Width / 5))
    local_panel.SetSizer(sizer)
    top_window.object_browser.SetSize((r.Width / 5, r.Width / 5))
    top_window.mgr.AddPane(local_panel, the_pane)
    top_window.mgr.Update()


def create_status_bar(top_window):

    # setup main window status bar
    status_bar = top_window.CreateStatusBar()


def create_menu_system(top_window):

    # create primary menu system
    menu_bar = wx.MenuBar()

    # file menu
    file_menu = wx.Menu()
    project_menu = wx.Menu()
    add_empty_item = file_menu.Append(wx.ID_ANY, 'New File', 'Add New File to Project...')
    save_item = file_menu.Append(wx.ID_ANY, 'Save', 'Save This File')
    save_as_item = file_menu.Append(wx.ID_ANY, 'Save As...', 'Save This File to Different Name')
    save_all_item = file_menu.Append(wx.ID_ANY, 'Save All\tCtrl+S', 'Save All Modified Files')
    file_menu.AppendSeparator()
    new_project_item = project_menu.Append(wx.ID_ANY, 'New Project', 'Create New Project...')
    load_project_item = project_menu.Append(wx.ID_ANY, 'Load Project', 'Load Previously Edited Project...')
    file_menu.AppendMenu(wx.ID_ANY, "Project", project_menu)
    file_menu.AppendSeparator()
    play_project_item = file_menu.Append(wx.ID_ANY, 'Play\tF5', 'Play Current Project')
    file_menu.AppendSeparator()
    exit_program_item = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit TadsPad')
    top_window.Bind(wx.EVT_MENU, top_window.on_quit, exit_program_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_page, save_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_page_as, save_as_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_all, save_all_item)
    top_window.Bind(wx.EVT_MENU, top_window.new_page, add_empty_item)
    top_window.Bind(wx.EVT_MENU, top_window.new_project, new_project_item)
    top_window.Bind(wx.EVT_MENU, top_window.load_project, load_project_item)
    top_window.Bind(wx.EVT_MENU, top_window.play_project, play_project_item)

    # edit menu
    edit_menu = wx.Menu()
    undo_item = edit_menu.Append(wx.ID_UNDO, 'Undo\tCtrl+Z', 'Undo')
    redo_item = edit_menu.Append(wx.ID_REDO, 'Redo\tCtrl+Y', 'Redo')
    edit_menu.AppendSeparator()
    cut_item = edit_menu.Append(wx.ID_CUT, 'Cut\tCtrl+X', 'Cut')
    copy_item = edit_menu.Append(wx.ID_COPY, 'Copy\tCtrl+C', 'Copy')
    paste_item = edit_menu.Append(wx.ID_PASTE, 'Paste\tCtrl+V', 'Paste')
    edit_menu.AppendSeparator()
    spell_item = edit_menu.Append(wx.ID_ANY, 'Spell Check\tF7', 'After the Deadline Spell Check')
    edit_menu.AppendSeparator()
    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, 'Preferences', 'Preferences')
    top_window.Bind(wx.EVT_MENU, top_window.undo, undo_item)
    top_window.Bind(wx.EVT_MENU, top_window.redo, redo_item)
    top_window.Bind(wx.EVT_MENU, top_window.cut, cut_item)
    top_window.Bind(wx.EVT_MENU, top_window.copy, copy_item)
    top_window.Bind(wx.EVT_MENU, top_window.paste, paste_item)
    top_window.Bind(wx.EVT_MENU, top_window.spell_check, spell_item)

    # view menu
    view_menu = wx.Menu()
    debug_pane_item = view_menu.Append(wx.ID_ANY, 'Message Pane', 'Toggle Message Pane')
    object_pane_item = view_menu.Append(wx.ID_ANY, 'Object Pane', 'Toggle Object Pane')

    # tools menu
    tools_menu = wx.Menu()
    view_transcript_item = tools_menu.Append(wx.ID_ANY, 'View Transcript', 'Command Transcript View Window')
    top_window.Bind(wx.EVT_MENU, top_window.load_transcript_view, view_transcript_item)
    spell_checker_item = tools_menu.Append(wx.ID_ANY, 'Spell Check', 'Check Spelling in All Game Strings')
    top_window.Bind(wx.EVT_MENU, top_window.spell_check, spell_checker_item)

    # help menu
    help_menu = wx.Menu()
    tutorial_item = help_menu.Append(wx.ID_HELP_CONTENTS, 'Tutorial', 'Tutorial')
    library_item = help_menu.Append(wx.ID_HELP_INDEX, 'Library Reference', 'Library Reference')
    help_menu.AppendSeparator()
    about_item = help_menu.Append(wx.ID_ABOUT, 'About TadsPad...', 'About TadsPad...')
    top_window.Bind(wx.EVT_MENU, MessageSystem.library_reference, library_item)
    top_window.Bind(wx.EVT_MENU, MessageSystem.tutorial_system, tutorial_item)
    top_window.Bind(wx.EVT_MENU, MessageSystem.about_box, about_item)

    # finalize finished menu
    menu_bar.Append(file_menu, '&File')
    menu_bar.Append(edit_menu, '&Edit')
    menu_bar.Append(view_menu, '&View')
    menu_bar.Append(tools_menu, '&Tools')
    menu_bar.Append(help_menu, '&Help')
    top_window.SetMenuBar(menu_bar)

__author__ = 'dj'


def create_notebook(top_window):

    # make main notebook object
    top_window.mgr = aui.AuiManager()
    top_window.mgr.SetManagedWindow(top_window)
    top_window.notebook = CodeNotebook.Notebook(top_window)
    top_window.mgr.AddPane(top_window.notebook, aui.AuiPaneInfo().Name("notebook_code").CenterPane().PaneBorder(False))
    top_window.mgr.Update()
