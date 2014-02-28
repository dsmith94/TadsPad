
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
    top_window.output_pane = MessagePane.OutputPane(top_window)
    top_window.message_book.AddPage(top_window.message_pane, "Context Help")
    top_window.message_book.AddPage(top_window.output_pane, "Compile Output")
    the_pane = aui.AuiPaneInfo().PaneBorder(True).CloseButton(False).Name("messages")
    the_pane.MinSize(r.Width, r.Height / 6)
    the_pane.Bottom()
    the_pane.BottomSnappable(False)
    the_pane.BottomDockable(True)
    top_window.mgr.AddPane(top_window.message_book, the_pane)
    top_window.mgr.Update()
    top_window.message_pane.show_message("")
    top_window.message_book.Update()



def create_object_browser(top_window):

    # show object browser and project browser
    local_panel = wx.Panel(top_window)
    r = wx.Display().GetGeometry()
    local_panel.SetSize((r.Width / 5, r.Width / 5))
    top_window.object_browser = ObjectBrowser.ObjectBrowser(top_window.notebook, parent=local_panel)
    top_window.project_browser = ProjectBrowser.ProjectBrowser(top_window.object_browser, parent=local_panel)
    the_pane = aui.AuiPaneInfo().CloseButton(False).Name("project")
    the_pane.MinSize((r.Width / 5, r.Width / 5))
    the_pane.RightSnappable(False)
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
    close_project_item = project_menu.Append(wx.ID_ANY, 'Close Project', 'Close Current TadsPad Project')
    file_menu.AppendMenu(wx.ID_ANY, "Project", project_menu)
    file_menu.AppendSeparator()
    exit_program_item = file_menu.Append(wx.ID_EXIT, 'Exit', 'Exit TadsPad')
    top_window.Bind(wx.EVT_MENU, top_window.on_quit, exit_program_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_page, save_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_page_as, save_as_item)
    top_window.Bind(wx.EVT_MENU, top_window.save_all, save_all_item)
    top_window.Bind(wx.EVT_MENU, top_window.new_page, add_empty_item)
    top_window.Bind(wx.EVT_MENU, top_window.new_project, new_project_item)
    top_window.Bind(wx.EVT_MENU, top_window.load_project, load_project_item)
    top_window.Bind(wx.EVT_MENU, top_window.close_project, close_project_item)

    # edit menu
    edit_menu = wx.Menu()
    undo_item = edit_menu.Append(wx.ID_UNDO, 'Undo\tCtrl+Z', 'Undo')
    redo_item = edit_menu.Append(wx.ID_REDO, 'Redo\tCtrl+Y', 'Redo')
    edit_menu.AppendSeparator()
    cut_item = edit_menu.Append(wx.ID_CUT, 'Cut\tCtrl+X', 'Cut')
    copy_item = edit_menu.Append(wx.ID_COPY, 'Copy\tCtrl+C', 'Copy')
    paste_item = edit_menu.Append(wx.ID_PASTE, 'Paste\tCtrl+V', 'Paste')
    find_item = edit_menu.Append(wx.ID_FIND, 'Find and Replace\tCtrl+F', 'Find and Replace Text Strings')
    edit_menu.AppendSeparator()
    theme_item = edit_menu.Append(wx.ID_ANY, 'Text Settings', 'Change Text Size and Color')
    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, 'Preferences', 'Preferences')
    top_window.Bind(wx.EVT_MENU, top_window.undo, undo_item)
    top_window.Bind(wx.EVT_MENU, top_window.redo, redo_item)
    top_window.Bind(wx.EVT_MENU, top_window.cut, cut_item)
    top_window.Bind(wx.EVT_MENU, top_window.copy, copy_item)
    top_window.Bind(wx.EVT_MENU, top_window.paste, paste_item)
    top_window.Bind(wx.EVT_MENU, top_window.find_replace, find_item)
    top_window.Bind(wx.EVT_MENU, top_window.preferences_window, preferences_item)
    top_window.Bind(wx.EVT_MENU, top_window.theme_window, theme_item)

    # view menu
    view_menu = wx.Menu()
    debug_pane_item = view_menu.Append(wx.ID_ANY, 'Toggle Message Pane\tF3', 'Hide/Show Messages')
    object_pane_item = view_menu.Append(wx.ID_ANY, 'Toggle Object Pane\tF4', 'Hide/Show Object Pane')
    top_window.Bind(wx.EVT_MENU, top_window.toggle_messages, debug_pane_item)
    top_window.Bind(wx.EVT_MENU, top_window.toggle_objects, object_pane_item)

    # tools menu
    tools_menu = wx.Menu()
    view_transcript_item = tools_menu.Append(wx.ID_ANY, 'View Transcript\tF6', 'Command Transcript View Window')
    top_window.Bind(wx.EVT_MENU, top_window.load_transcript_view, view_transcript_item)
    spell_item = tools_menu.Append(wx.ID_ANY, 'Spell Check\tF7', 'After the Deadline Spell Check')
    top_window.Bind(wx.EVT_MENU, top_window.spell_check, spell_item)
    tools_menu.AppendSeparator()
    play_project_item = tools_menu.Append(wx.ID_ANY, 'Play\tF5', 'Play Current Project')
    top_window.Bind(wx.EVT_MENU, top_window.play_project, play_project_item)

    # help menu
    help_menu = wx.Menu()
    bookshelf_item = help_menu.Append(wx.ID_HELP_CONTENTS, 'Adv3Lite Bookshelf\tF1', 'Complete TADS Adv3Lite Documentation Set')
    help_menu.AppendSeparator()
    about_item = help_menu.Append(wx.ID_ABOUT, 'About TadsPad...', 'About TadsPad...')
    top_window.Bind(wx.EVT_MENU, MessageSystem.bookshelf_system, bookshelf_item)
    top_window.Bind(wx.EVT_MENU, MessageSystem.about_box, about_item)

    # make list of menu items to gray out when project is not loaded
    top_window.grayable.append(add_empty_item)
    top_window.grayable.append(save_item)
    top_window.grayable.append(save_all_item)
    top_window.grayable.append(save_as_item)
    top_window.grayable.append(undo_item)
    top_window.grayable.append(redo_item)
    top_window.grayable.append(cut_item)
    top_window.grayable.append(copy_item)
    top_window.grayable.append(paste_item)
    top_window.grayable.append(find_item)
    top_window.grayable.append(view_transcript_item)
    top_window.grayable.append(spell_item)
    top_window.grayable.append(play_project_item)

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
    top_window.mgr.SetAutoNotebookStyle(aui.AUI_MGR_SMOOTH_DOCKING | aui.AUI_DOCK_NONE)
    top_window.mgr.SetDockSizeConstraint(0.5, 0.5)
    top_window.mgr.SetManagedWindow(top_window)
    top_window.notebook = CodeNotebook.Notebook(top_window)
    top_window.message_book = aui.AuiNotebook(top_window, agwStyle=aui.AUI_NB_BOTTOM)
    top_window.mgr.AddPane(top_window.notebook, aui.AuiPaneInfo().Name("notebook_code").CenterPane().PaneBorder(False))
    top_window.Fit()
    top_window.mgr.Update()

