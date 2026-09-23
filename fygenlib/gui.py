# ---------------------------------------------------------------------------------------------------- #
#
#    ▄▄▄▄ ▄▄ ▄▄ ▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██ ▄▄ ██ ██ ██   ██▄█▀ ▀███▀ 
#   ▀███▀ ▀███▀ ██ ▄ ██      █   
#
# ---------------------------------------------------------------------------------------------------- #
#
#   ------------------------------------------------------------
#   Development History & Contacts       (Reverse Chronological)
#   ------------------------------------------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   Initial Pipeline                |    Tyler Frischknecht
#   ------------------------------------------------------------
#   Last Updated: 9/23/2026 - Ready for full release!
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Handles GUI elements of bcds-main.py setup process. Provides menu to add, remove and reorder
#   directories to analyze, with an optional settings popup for each valid directory.
#
# ---------------------------------------------------------------------------------------------------- #
import os
import tkinter
#
from tkinter import filedialog, messagebox, ttk
from typing import Callable
from os import cpu_count as os_cpuCount
#
from fygenlib.settings import Settings
from fygenlib.paths import getProjectPaths
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'GuiSetup'
]
# -------------------------------------------------- #
class GuiSetup(tkinter.Tk):
    '''
    # GuiSetup

    Child class of `tkinter.Tk`

    Handles GUI elements of bcds-main.py setup process. Provides menu to add, remove and reorder \
    directories to analyze, with an optional settings popup for each valid directory.

    Member Variables
    ----------------
    `program_paths` : *dict[str, os.PathLike | str]*
        - A dict of paths relevant to this program, indexed by name string. Used for path \
        handling regardless of underlying architecture. The only path required in this dict for \
        GuiSetup is under the key 'settings', which routes a folder storing program data \
        between launches and runs. Must be assigned before mainloop is called.
    `directories` : *list[tuple[os.PathLike | str, Settings | None]]*
        - The selection of directories listed in the tkinter menu at any given time. If verified \
        by _validateDirectory, a Settings object will be instantiated and paired with each \
        directory path. If invalid, the path will instead be paired with None.
    `frame` : *ttk.Frame*
        - The window all other tkinter GUI elements are arranged in.
    `tree` : *ttk.Treeview*
        - A reorderable table of directories, manually added, or read from a persistent log file. \
        When invalid directories are detected, they are recolored red, and will be removed before \
        the analysis stage.
    `scrollbar` : *ttk.Scrollbar*
        - A scrollbar to scroll through added directories.
    `last_add_directory` : *os.PathLike* | *str* | *None*
        - Tracks the parent folder of the last directory added. When adding a new directory, the \
        file dialog's initial position will be last_add_directory, if existing. 
    `top_buttons` : *list[tuple[str, typing.Callable, str]]*
        - A list of the buttons which appear above the directory tree view. The tuple contains \
        button text, function to execute when pressed, relative alignment.
    `bottom_buttons` : *list[tuple[str, typing.Callable]]*
        - A list of the buttons which appear below the directory tree view. The tuple contains \
        button text, function to execute when pressed.
    `settings_file_parsers` : *dict[str, Callable]*
        - A dictionary of parsers for persistent project settings files. The key corresponds \
        with a key of the same name in the settings file, with each value being a callable type \
        conversion function.
    `valid_directories` : *list[tuple[os.PathLike | str, Settings]]*
        - A filtered list of valid directories only. Populated at GUI exit, for use in the \
        analysis stage. Not used internally.
    `run_analysis` : *bool*
        - Records whether the GUI was closed from 'Run Analysis' or 'X'. Initialized to False, \
        only True when GUI exited safely. Not used internally.

    Member Functions
    ----------------
    `mainLoop` -> *None*
        - Calls underlying GuiSetup functions to build window, then runs tkinter.Tk.mainloop.
    `_buildWindow` -> *None*
        - Prepares the window for directory population.
    `_buildButtons` -> *None*
        - Populates upper and lower button containers with buttons.
    `_loadLastDirectories` -> *list[os.PathLike | str]*
        - Reads previously added directories from persistent file `last_paths_analyzed.txt` in \
        the settings folder.
    `_updateTree` -> *None*
        - Clears and repopulates the directory Treeview with the most recent updates to \
        `GuiSetup.directories`.
    `_getSelectedIndex` -> *int* | *None*
        - Retrieves the zero-indexed integer corresponding to the currently selected entry in the \
        directory Treeview.
    `_moveUp` -> *None*
        - Modifies the list of directories added to the Treeview in place, swapping the selected \
        element with the one directly above it, if present.
    `_moveDown` -> *None*
        - Modifies the list of directories added to the Treeview in place, swapping the selected \
        element with the one directly below it, if present.
    `_removeItem` -> *None*
        - Modifies the list of directories added to the Treeview in place, removing the selected \
        element, if exists.
    `_addItem` -> *None*
        - Opens a file dialog to select an existing folder, and append to the list of directories \
        in the Treeview.
    `_handleDirectoryData` -> *None*
        - Validates and registers a target folder into GuiSetup.directories.
    `_readSettings` -> *Settings* | *None*
        - Reads the per-project analysis_settings.txt file, if exists, to apply persistent \
        settings on re-analysis.
    `_setSettings` -> *None*
        - Opens settings popup dialog for the currently selected directory in the Treeview, if it \
        has been validated.
    `_exitGuiSafely` -> *None*
        - Saves analysis settings for all valid directories in the TreeView.
    `_validateDirectory` -> *bool*
        - Verifies that a project directory contains required paths and files.

    Instantiation
    -------------
    >>> gui = GuiSetup()
    >>> gui.mainloop()
    >>> run_analysis = gui.run_analysis
    >>> valid_directories = gui.valid_directories
    '''
# -------------------------------------------------- #
    # file paths for internal use
    program_paths :         dict[str, os.PathLike | str]
    directories :           list[tuple[os.PathLike | str, Settings | None]]
    # tkinter elements
    frame :                 ttk.Frame
    tree :                  ttk.Treeview
    scrollbar :             ttk.Scrollbar
    last_add_directory :    os.PathLike | str
    top_buttons :           list[tuple[str, Callable, str]]
    bottom_buttons :        list[tuple[str, Callable]]
    # file handling
    settings_file_parsers : dict[str, Callable]
    # utility values upon window close
    valid_directories :     list[tuple[os.PathLike | str, Settings]]
    run_analysis :          bool
# -------------------------------------------------- #
    # Not used for optimization, but as an architecture safeguard
    __slots__ = [
        "program_paths",
        'directories',
        'frame',
        'tree',
        'scrollbar',
        'last_add_directory',
        'top_buttons',
        'bottom_buttons',
        'settings_file_parsers',
        'valid_directories',
        'run_analysis'
    ]
# -------------------------------------------------- #
    def __init__(this) -> None:
        '''
        # GuiSetup.__init__

        Initializes the tkinter/GuiSetup object, and prepares styles and layouts for mainloop \
        execution.

        Parameters
        ----------
            - `__init__` has no parameters.

        Returns
        -------
        *None*
            - No values are returned.

        Examples
        --------
        >>> gui = GuiSetup()
        '''

        super().__init__()

        bg_color = "#ECECEC"
        this.configure(bg = bg_color)

        style = ttk.Style(this)
        style.theme_use("clam")

        style.configure(".", background = bg_color, foreground = "#000000")
        style.configure("TFrame", background = bg_color)
        style.configure("TLabel", background = bg_color, foreground = "#000000")

        this.program_paths = dict()
        this.last_add_directory = None
        this.run_analysis = False
        this.directories = []

        this.top_buttons = [
            ("Add", this._addItem, 'w'),
            ("Run Analysis", this._exitGuiSafely, 'e')
        ]
        this.bottom_buttons = [
            ("Settings", this._setSettings),
            ("Move Up", this._moveUp),
            ("Move Down", this._moveDown),
            ("Remove", this._removeItem)
        ]
        this.settings_file_parsers = {
            "start_frame" : int,
            "end_frame" : int,
            "bit_depth" : int,
            "skipped_frames" : lambda values: [int(num.strip()) for num in values.split(',') if num.strip()],
            "use_nearest_neighbor" : lambda value: value.strip() == '1',
            "max_workers" : int,
            "use_ds_psf" : lambda value: value.strip() == '1',
            "use_se_psf" : lambda value: value.strip() == '1',
            "se_aspect_ratio" : float
        }

        this.title("bcds-main.py")
# -------------------------------------------------- #
    def mainloop(this) -> None:
        '''
        # GuiSetup.mainloop

        Calls underlying GuiSetup functions to build window, then runs tkinter.Tk.mainloop. \
        Note that this function is blocking, as is the parent class's implementation.

        Parameters
        ----------
            - `mainloop` has no parameters. Tkinter's implementation of mainloop uses a parameter \
            `n` to handle multiple root windows, dropped in this function to avoid confusion. 

        Returns
        -------
        *None*
            - No value is returned. The GuiSetup window should be visible until manually closed.

        Examples
        --------
        >>> gui.mainloop()
        '''

        this._buildWindow()
        super().mainloop()
# -------------------------------------------------- #
    def _buildWindow(this) -> None:
        '''
        # GuiSetup._buildWindow

        Prepares the window for directory population. Loads list of directories if found in \
        .bcds_settings/last_paths_analyzed.txt, or is instantiated empty.

        Parameters
        ----------
            - `_buildWindow` has no parameters.

        Returns
        -------
        *None*
            - No values are returned. Modifies GUI components and stored analysis directories and \
            states.

        Examples
        --------
        >>> gui._buildWindow()
        '''

        ttk.Label(
            this, text = "Select directories for analysis:", font = ("Helvetica", 12, "bold")
        ).pack(pady=15)

        # top buttons
        top_buttons = ttk.Frame(this)
        top_buttons.pack(fill = 'x', padx = 20, pady = (0, 10))
        top_buttons.columnconfigure((0, 1), weight = 1)
        
        # full frame
        this.frame = ttk.Frame(this)
        this.frame.pack(fill = "both", expand = True, padx = 20, pady = 5)
        
        # treeview
        this.tree = ttk.Treeview(
            this.frame, 
            columns = ("display_name",), 
            show = "headings", 
            selectmode = "browse"
        )
        this.tree.pack(side = "left", fill = "both", expand = True)
        this.tree.heading("display_name", text = "Directory Path", anchor = 'w')
        this.tree.column("display_name", anchor = 'w')
        this.tree.tag_configure("invalid", foreground="red")
        
        # scrollbar
        this.scrollbar = ttk.Scrollbar(
            this.frame, 
            orient = "vertical", 
            command = this.tree.yview
        )
        this.scrollbar.pack(side = "right", fill = 'y')
        this.tree.configure(yscrollcommand = this.scrollbar.set)
        
        # buttons
        bottom_buttons = ttk.Frame(this)
        bottom_buttons.pack(fill = 'x', pady = 10, padx = 5)
        bottom_buttons.columnconfigure((0, 1, 2, 3), weight = 1)

        this._buildButtons(top_buttons, bottom_buttons)

        last_directories = this._loadLastDirectories()

        for directory in last_directories:
            this._handleDirectoryData(directory)
        
        this._updateTree()
# -------------------------------------------------- #
    def _buildButtons(this, Top_Frame : ttk.Frame, Bottom_Frame : ttk.Frame) -> None:
        '''
        # GuiSetup._buildButtons

        Populates upper and lower button containers with buttons, each with their associated \
        functions and relative alignments as specified in `__init__`.

        Parameters
        ----------
        `Top_Frame` : *ttk.Frame*
            - The container for top action buttons ("Add", "Run Analysis").
        `Bottom_Frame` : *ttk.Frame*
            - The container for bottom directory organization buttons ("Settings", "Move Up", \
            "Move Down", "Remove").

        Returns
        -------
        *None*
            - No values are returned. Adds button elements directly to the provided containers.

        Examples
        --------
        >>> gui._buildButtons(top_frame, bottom_frame)
        '''

        for column, (text, _function, alignment) in enumerate(this.top_buttons):
            ttk.Button(
                Top_Frame, 
                text = text, 
                command = _function
            ).grid(row = 0, column = column, sticky = alignment)

        for column, (text, _function) in enumerate(this.bottom_buttons):
            ttk.Button(
                Bottom_Frame, 
                text = text, 
                command = _function
            ).grid(row = 0, column = column, sticky = 'ew', padx = 5)
# -------------------------------------------------- #
    def _loadLastDirectories(this) -> list[os.PathLike | str]:
        '''
        # GuiSetup._loadLastDirectories

        Reads previously added directories from persistent file `last_paths_analyzed.txt` \
        in the settings folder.

        Parameters
        ----------
            - `_loadLastDirectories` takes no parameters.

        Returns
        -------
        *list[os.PathLike | str]*
            - A list of directory path strings loaded from the persistent program file. Returns \
            an empty list if `program_paths` is not set, the settings path is missing, or the \
            file does not exist.

        Examples
        --------
        >>> paths = gui._loadLastDirectories()
        '''

        if not this.program_paths:
            return []
        program_settings_path = this.program_paths.get('settings')
        if not program_settings_path:
            return []
        directories_path = os.path.join(program_settings_path, 'last_paths_analyzed.txt')
        if not os.path.exists(directories_path):
            return []
            
        with open(directories_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
# -------------------------------------------------- #
    def _updateTree(this) -> None:
        '''
        # GuiSetup._updateTree

        Clears and repopulates the directory Treeview with the most recent updates to \
        `GuiSetup.directories`. Invalid directories are added (before _updateTree is called) \
        without a Settings instance, which is used here to determine validity and color tagging.

        Parameters
        ----------
            - `_updateTree` takes no parameters.

        Returns
        -------
        *None*
            - No values are returned. Modifies Treeview entries and window title.

        Examples
        --------
        >>> gui._updateTree()
        '''

        for item in this.tree.get_children():
            this.tree.delete(item)
            
        for directory, settings in this.directories:
            clean_name = '/'.join([
                os.path.basename(os.path.dirname(directory)), 
                os.path.basename(directory)
            ])
            row_tags = () if settings is not None else ("invalid",)
            this.tree.insert('', tkinter.END, values = (clean_name,), tags = row_tags)

        this.title(f"bcds-main.py | {len(this.directories)} directories added...")
# -------------------------------------------------- #
    def _getSelectedIndex(this) -> int | None:
        '''
        # GuiSetup._getSelectedIndex

        Retrieves the zero-indexed integer corresponding to the currently selected entry in \
        the directory Treeview.

        Parameters
        ----------
            - `_getSelectedIndex` takes no parameters.

        Returns
        -------
        *int* | *None*
            - The index of the selected row, or `None` if no row is currently selected.

        Examples
        --------
        >>> index = gui._getSelectedIndex()
        '''

        selected_item = this.tree.selection()
        if not selected_item:
            return None
        return this.tree.index(selected_item[0])
# -------------------------------------------------- #
    def _moveUp(this) -> None:
        '''
        # GuiSetup._moveUp

        Modifies the list of directories added to the Treeview in place, swapping the selected \
        element with the one directly above it, if present.

        Parameters
        ----------
            - `_moveUp` has no parameters. Location and selection is tracked internally.

        Returns
        -------
        *None*
            - No values are returned. Internal list of directories is modified in place, and the \
            window is refreshed.

        Examples
        --------
        >>> gui._moveUp()
        '''

        index = this._getSelectedIndex()
        if index is None or index <= 0:
            return
        
        (   # Begin Swap
            this.directories[index], 
            this.directories[index - 1]
        ) = (
            this.directories[index - 1], 
            this.directories[index]
        )   # End Swap
        
        this._updateTree()
        target_index = this.tree.get_children()[index - 1]
        this.tree.selection_set(target_index)
# -------------------------------------------------- #
    def _moveDown(this) -> None:
        '''
        # GuiSetup._moveDown

        Modifies the list of directories added to the Treeview in place, swapping the selected \
        element with the one directly below it, if present. This is a separate function from \
        `GuiSetup._moveUp` purely for simple coupling to separate buttons.

        Parameters
        ----------
            - `_moveDown` has no parameters. Location and selection is tracked internally.

        Returns
        -------
        *None*
            - No values are returned. Internal list of directories is modified in place, and the \
            window is refreshed.

        Examples
        --------
        >>> gui._moveDown()
        '''

        index = this._getSelectedIndex()
        if index is None or index >= len(this.directories) - 1:
            return
        
        (   # Begin Swap
            this.directories[index], 
            this.directories[index + 1]
        ) = (
            this.directories[index + 1], 
            this.directories[index]
        )   # End Swap
        
        this._updateTree()
        target_index = this.tree.get_children()[index + 1]
        this.tree.selection_set(target_index)
# -------------------------------------------------- #
    def _removeItem(this) -> None:
        '''
        # GuiSetup._removeItem

        Modifies the list of directories added to the Treeview in place, removing the selected \
        element, if exists.

        Parameters
        ----------
            - `_removeItem` has no parameters. Location and selection is tracked internally.

        Returns
        -------
        *None*
            - No values are returned. Internal list of directories is modified in place, and the \
            window is refreshed.

        Examples
        --------
        >>> gui._removeItem()
        '''

        index = this._getSelectedIndex()
        if index is None:
            return
        
        this.directories.pop(index)
        this._updateTree()
        
        children = this.tree.get_children()
        if children:
            new_index = min(index, len(children) - 1)
            this.tree.selection_set(children[new_index])
# -------------------------------------------------- #
    def _addItem(this) -> None:
        '''
        # GuiSetup._addItem

        Opens a file dialog to select an existing folder, and append to the list of directories \
        in the Treeview. Tracks the parent directory of the most recent folder added for ease of \
        navigation.

        Parameters
        ----------
            - `_addItem` has no parameters. Directories and navigation are tracked internally.

        Returns
        -------
        *None*
            - No values are returned. Internal list of directories is modified in place, and the \
            window is refreshed.

        Examples
        --------
        >>> gui._addItem()
        '''

        initial_directory = this.last_add_directory

        if initial_directory is None:
            initial_directory = os.path.expanduser("~")

        chosen_directory = filedialog.askdirectory(
            title = "Select Directory to Add",
            initialdir = initial_directory
        )

        if not chosen_directory:
            return
        
        parent = os.path.dirname(chosen_directory) 
        this.last_add_directory = parent

        this._handleDirectoryData(chosen_directory)
# -------------------------------------------------- #
    def _handleDirectoryData(this, Chosen_Directory : os.PathLike | str) -> None:
        '''
        # GuiSetup._handleDirectoryData

        Validates and registers a target folder into GuiSetup.directories. Reads analysis \
        settings file, if exists, and prompts for confirmation of frames to analyze, settings \
        to apply, and analysis methods to use, in a popup menu.

        Parameters
        ----------
        `Chosen_Directory` : *os.PathLike* | str
            - Path to the directory being validated and appended.

        Returns
        -------
        *None*
            - No values are returned. Modifies directory list in place.

        Examples
        --------
        >>> gui._handleDirectoryData(R"D:/J7/100uM")
        '''

        if this._validateDirectory(Chosen_Directory):
            directory_settings = this._readSettings(Chosen_Directory)
            if directory_settings is None:
                directory_settings = Settings()
                PopupSetSettings(
                    this,
                    Chosen_Directory,
                    directory_settings
                )
            this.directories.append((Chosen_Directory, directory_settings))
        else:
            this.directories.append((Chosen_Directory, None))
            
        this._updateTree()
            
        all_indexes = this.tree.get_children()
        if all_indexes:
            last_index = all_indexes[-1]
            this.tree.selection_set(last_index)
            this.tree.see(last_index)
# -------------------------------------------------- #
    def _readSettings(this, Project_Path : str) -> Settings | None:
        '''
        # GuiSetup._readSettings

        Reads the per-project analysis_settings.txt file, if exists, to apply persistent settings \
        on re-analysis. Uses key=value parsers as defined in __init__ under \
        `this.settings_file_parsers`.

        Parameters
        ----------
        `Project_Path` : *str*
            - Path to the target project directory.

        Returns
        -------
        *Settings*
            - A populated `Settings` object if a valid settings file was parsed successfully, \
        *None*
            - `None` if the file does not exist, or has no valid key=value lines.

        Examples
        --------
        >>> settings = gui._readSettings(R"D:/NS20J2/100uM")
        '''

        analysis_settings_path = getProjectPaths(Project_Path).get('analysis_settings', None)

        if not analysis_settings_path:
            return None
        settings_file = os.path.join(analysis_settings_path, 'analysis_settings.txt')
        if not os.path.exists(settings_file):
            return None
            
        settings = Settings()
        has_settings = False

        try: 
            with open(settings_file, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                        
                    key, value = [item.strip() for item in line.split('=', 1)]
                    
                    if key in this.settings_file_parsers:
                        try:
                            parsed_value = this.settings_file_parsers[key](value)
                            setattr(settings, key, parsed_value)
                            has_settings = True
                        except ValueError:
                            continue
        except Exception:
            return None

        return settings if has_settings else None
# -------------------------------------------------- #
    def _setSettings(this) -> None:
        '''
        # GuiSetup._setSettings

        Opens settings popup dialog for the currently selected directory in the Treeview, if it \
        has been validated. Only valid directories received a `Settings` object when initially \
        added to the TreeView, while those paired with *None* are ignored in this function. 

        Parameters
        ----------
            - `_setSettings` takes no parameters. Selection is tracked internally.

        Returns
        -------
        *None*
            - No values are returned. Launches a `PopupSetSettings` entry window.

        Examples
        --------
        >>> gui._setSettings()
        '''

        index = this._getSelectedIndex()
        if index is None:
            return
        
        if this.directories[index][1] is None:
            return
        
        PopupSetSettings(
            this,
            this.directories[index][0],
            this.directories[index][1]
        )
# -------------------------------------------------- #
    def _exitGuiSafely(this) -> None:
        '''
        # GuiSetup._exitGuiSafely

        Saves analysis settings for all valid directories in the TreeView. If invalid directories \
        are detected, a warning message is shown, requiring confirmation to proceed without them, \
        or return to the GUI to correct them. `GuiSetup.run_analysis` is updated to True to \
        indicate the window wasn't prematurely exited.

        Parameters
        ----------
            - `_exitGuiSafely` takes no parameters.

        Returns
        -------
        *None*
            - No values are returned. A configuration file is written for each project in the \
            TreeView, `this.run_analysis` is updated, and the window is destroyed.

        Examples
        --------
        >>> gui._exitGuiSafely()
        '''
    
        for directory, settings in this.directories:
            # if settings was never constructed, its an invalid file
            if settings is None:
                continue
                
            project_paths = getProjectPaths(directory)
            analysis_settings_path = project_paths.get('analysis_settings', None)
            
            if analysis_settings_path is None:
                continue

            os.makedirs(analysis_settings_path, exist_ok=True)
            settings_file_path = os.path.join(analysis_settings_path, 'analysis_settings.txt')
            
            with open(settings_file_path, "w") as file:
                skipped_str = ",".join(str(index) for index in settings.skipped_frames)
                file.write(
                    f"start_frame={settings.start_frame}\n"
                    f"end_frame={settings.end_frame}\n"
                    f"skipped_frames={skipped_str}\n"
                    f"bit_depth={settings.bit_depth}\n"
                    f"use_nearest_neighbor={int(settings.use_nearest_neighbor)}\n"
                    f"max_workers={int(settings.max_workers)}\n"
                    f"use_ds_psf={int(settings.use_ds_psf)}\n"
                    f"use_se_psf={int(settings.use_se_psf)}\n"
                    f"se_aspect_ratio={float(settings.se_aspect_ratio)}"
                )
        
        this.valid_directories = [item for item in this.directories if item[1] is not None]

        project_settings = this.program_paths.get('settings', None)
        os.makedirs(project_settings, exist_ok = True)
        if project_settings is not None:
            with open (os.path.join(project_settings, 'last_paths_analyzed.txt'), 'w') as file:
                file.write('\n'.join(directory_pair[0] for directory_pair in this.valid_directories))

        proceed = True
        if len(this.valid_directories) < len(this.directories):
            proceed = messagebox.askokcancel(
                title = "Invalid Directories Detected",
                message = (
                    "Some selected directories are invalid (highlighted in red) "
                    "and will be skipped.\n\n"
                    "Click 'OK' to continue or 'Cancel' to go back."
                ),
                icon = "warning"
            )

        if proceed:
            this.run_analysis = True
            this.destroy()
# -------------------------------------------------- #
    def _validateDirectory(this, Path : os.PathLike | str) -> bool:
        '''
        # GuiSetup._validateDirectory

        Verifies that a project directory contains required paths and files. At least one droplet \
        image and feature table must be provided to be validated. Creates output directories for \
        segmentation, analysis logs, and meta logs if requirements are met.

        Parameters
        ----------
        `Path` : *os.PathLike* | *str*
            - Path to the project directory to validate.

        Returns
        -------
        *bool*
            - `True` if all directory requirements and file checks pass, otherwise `False`.

        Examples
        --------
        >>> is_valid = gui._validateDirectory(R"D:/NS20J2/100uM")
        '''

        paths = getProjectPaths(Path)

        segmentation_path =     paths.get('segmentation', None)
        analysis_logs_path =    paths.get('analysis_logs', None)
        meta_logs_path =        paths.get('meta_logs', None)
        feature_tables_path =   paths.get('feature_tables', None)
        movie_frames_path =     paths.get('movie_frames', None)

        if (
            segmentation_path is None or
            analysis_logs_path is None or
            meta_logs_path is None or
            feature_tables_path is None or
            movie_frames_path is None
        ):
            return False

        if (
            not os.path.isdir(feature_tables_path) or 
            not os.path.isdir(movie_frames_path)
        ):
            return False
        
        has_csv = False
        with os.scandir(feature_tables_path) as directory:
            for file in directory:
                if file.is_file() and file.name.lower().endswith('.csv'):
                    has_csv = True
                    break
        if not has_csv:
            return False
        
        has_tiff = False
        with os.scandir(movie_frames_path) as directory:
            for file in directory:
                if file.is_file() and (file.name.lower().endswith('.tif') or file.name.lower().endswith('.tiff')):
                    has_tiff = True
                    break            
        if not has_tiff:
            return False
        
        os.makedirs(segmentation_path, exist_ok = True)
        os.makedirs(analysis_logs_path, exist_ok = True)
        os.makedirs(meta_logs_path, exist_ok = True)

        return True
# ---------------------------------------------------------------------------------------------------- #
class PopupSetSettings(tkinter.Toplevel):
    '''
    # PopupSetSettings

    Child class of `tkinter.Toplevel`

    A popup window for GuiSetup to edit the per-project analysis settings for a selected directory.

    Member Variables
    ----------------
    `parent_window` : *tkinter.Tk*
        - The tkinter window this tkinter.TopLevel popup window opens above.
    `project_path` : *os.PathLike* | *str*
        - The directory containing the full project for analysis.
    `settings` : *Settings*
        - The `Settings` object to be reassigning values to as input in this window.
    `total_frames` : *int*
        - The number of .tif or .tiff analysis images found in the movie frames directory within \
        the parent project path.
    `total_cpu_cores` : *int*
        - The number of physical and virtual CPU cores found by the operating system. Used to \
        reccomended an absolute limit on the number of worker threads.
    `start_entry` : *ttk.Entry*
        - An entry for the integer index representing the first image to analyze.
    `end_entry` : *ttk.Entry*
        - An entry for the integer index representing the last image to analyze.
    `skipped_entry` : *ttk.Entry*
        - An entry for a list of comma seperated integer indices to skip analysis of. 
    `bit_entry` : *ttk.Entry*
        - An entry of the bit depth of the frames in the movie. Some microscopes use a \
        non-standard bit depth like 12. This field allows the true range of intensity to be \
        tracked despite being cast to the nearest 2^n-byte int type large enough to contain it.
    `se_aspect_ratio_entry` : *ttk.Entry*
        - An entry for the z to xy aspect ratio of the fitted ellipse, if the sphere-ellipse \
        profile is selected to run. Values below 1 indicate vertical compression under gravity, \
        while values above 1 indicate vertical stretching against gravity.
    `max_workers_entry` : *ttk.Entry*
        - The user-specified target number of worker threads to apply to the parallelized \
        implementations for ds_psf and se_psf.
    `nearest_neighbor_entry` : *tkinter.BooleanVar*
        - A checkbox entry to use the greedy nearest-neighbor algorithm to determine the dillute \
        phase radii of all drops in a drop image.
    `ds_psf_entry` : *tkinter.BooleanVar*
        - A checkbox entry to use the parallelized double-sphere curve fitting algorithms to \
        determine the dense phase radii of all drops with an assigned dilute radius in a drop \
        image.
    `se_psf_entry` : *tkinter.BooleanVar*
        - A checkbox entry to use the parallelized sphere-ellipse curve fitting algorithms to \
        determine the dense phase radii of all drops with an assigned dilute radius in a drop \
        image.

    Member Functions
    ----------------
    `_getFrameStats` -> *int*
        - Reads the number of valid analysis images in the internally tracked project directory.
    `_renderWindow` -> *None*
        - Coordinates input box rendering and response storage.
    `_saveSettings` -> *None*
        - Copies all fields from the rendered window, casts them to the correct data type, then \
        modifies the tracked Settings object in place before closing.
    '''
# -------------------------------------------------- #
    parent_window :          tkinter.Tk
    project_path :           os.PathLike | str
    settings :               Settings
    total_frames :           int
    total_cpu_cores :        int
    # analysis settings
    start_entry :            ttk.Entry
    end_entry :              ttk.Entry
    skipped_entry :          ttk.Entry
    bit_entry :              ttk.Entry
    se_aspect_ratio_entry :  ttk.Entry
    max_workers_entry :      ttk.Entry
    # analysis methods
    nearest_neighbor_entry : tkinter.BooleanVar
    ds_psf_entry :           tkinter.BooleanVar
    se_psf_entry :           tkinter.BooleanVar
# -------------------------------------------------- #
    # Not used for optimization, but as an architecture safeguard
    __slots__ = [
        'parent_window',
        'project_path',
        'settings',
        'total_frames',
        'total_cpu_cores',
        'start_entry',
        'end_entry',
        'skipped_entry',
        'bit_entry',
        'se_aspect_ratio_entry',
        'max_workers_entry',
        'nearest_neighbor_entry',
        'ds_psf_entry',
        'se_psf_entry'
    ]
# -------------------------------------------------- #
    def __init__(
        this, 
        Parent_Window : tkinter.Tk, 
        Project_Path : os.PathLike | str, 
        Current_Settings : Settings
    ) -> None:
        '''
        # PopupSetSettings.__init__

        Initializes the tkinter.Toplevel/PopupSetSettings object, and populates member variables \
        with settings. Renders the window immediately following population.

        Parameters
        ----------
        `Parent_Window` : *tkinter.Tk*
            - The tkinter window this tkinter.TopLevel popup window will be opening above.
        `Project_Path` : *os.PathLike* | *str*
            - The path containing files to be analyzed, and where processed data is to be \
            populated. Used to check how many images are present for analysis.
        `Current_Settings` : *Settings*
            - The existing settings object for the selected project directory in Parent_Window. \
            Used to populate starting values at window render.

        Returns
        -------
        *None*
            - No values are returned.

        Examples
        --------
        >>> popup = PopupSetSettings(Parent_Window, Project_Path, Current_Settings)
        '''

        super().__init__(Parent_Window)
        
        this.parent_window = Parent_Window
        this.project_path = Project_Path
        this.settings = Current_Settings

        this.total_cpu_cores = int(os_cpuCount() or 1)
        
        this.title("Directory Settings")
        this.geometry("500x500")
        this.grab_set() # freeze main window interactions

        this.total_frames = this._getFrameStats()

        if this.settings.end_frame < 0:
            this.settings.end_frame = this.total_frames - 1

        this._renderWindow()
# -------------------------------------------------- #
    def _getFrameStats(this) -> int:
        '''
        # PopupSetSettings._getFrameStats

        Reads the number of valid analysis images in the internally tracked project directory.

        Parameters
        ----------
            - `_getFrameStats` has no parameters. The internally tracked project directory is \
            used for retrieving file count.

        Returns
        -------
        *int*
            - The number of valid analysis images found in the project directory.

        Examples
        --------
        >>> frame_count = popup._getFrameStats()
        '''

        project_paths = getProjectPaths(this.project_path)
        frames_path = project_paths.get('movie_frames', None)
        
        if frames_path and os.path.exists(frames_path):
            frame_files = sorted([
                file for file in os.listdir(frames_path) 
                if (
                    file.lower().endswith(('.tif', '.tiff')) and
                    # handles macos files for people who make bad decisions
                    not file.lower().startswith('._')
                )
            ])
            return len(frame_files)
        return 0
# -------------------------------------------------- #
    def _renderWindow(this) -> None:
        '''
        # PopupSetSettings._renderWindow

        Coordinates input box rendering and response storage. Uses default values determined by \
        the stored Settings object or helper functions. Typically this function is automatically \
        called by __init__.

        Parameters
        ----------
            - `_renderWindow` has no parameters.

        Returns
        -------
        *None*
            - No values are returned.

        Examples
        --------
        >>> popup._renderWindow()
        '''

        ttk.Label(
            this, 
            text = f"Configure Frames (Total Detected: {this.total_frames})", 
            font = ("Helvetica", 12, "bold")
        ).pack(pady = 10)

        input_frame = ttk.Frame(this)
        input_frame.pack(pady = 10)

        # start frame entry
        ttk.Label(
            input_frame, 
            text = "Start Frame Index: (Min = 0)"
        ).grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)
        this.start_entry = ttk.Entry(input_frame, width = 15)
        this.start_entry.insert(0, str(this.settings.start_frame))
        this.start_entry.grid(row = 0, column = 1, sticky = "e", padx = 5, pady = 5)

        # end frame entry
        ttk.Label(
            input_frame, 
            text = f"End Frame Index: (Max = {this.total_frames - 1})"
        ).grid(row = 1, column = 0, sticky = "w", padx = 5, pady = 5)
        this.end_entry = ttk.Entry(input_frame, width = 15)
        this.end_entry.insert(0, str(this.settings.end_frame))
        this.end_entry.grid(row = 1, column = 1, sticky = "e", padx = 5, pady = 5)

        # skipped frames entry
        ttk.Label(
            input_frame, 
            text = "Skipped Frames (comma,separated):"
        ).grid(row = 2, column = 0, sticky = "w", padx = 5, pady = 5)
        this.skipped_entry = ttk.Entry(input_frame, width = 15)
        this.skipped_entry.insert(
            0, 
            ",".join(str(frame) for frame in sorted(this.settings.skipped_frames))
        )
        this.skipped_entry.grid(row = 2, column = 1, sticky = "e", padx = 5, pady = 5)

        # bit depth entry
        ttk.Label(
            input_frame, 
            text = "Image Bit Depth:"
        ).grid(row = 3, column = 0, sticky = "w", padx = 5, pady = 5)
        this.bit_entry = ttk.Entry(input_frame, width = 15)
        this.bit_entry.insert(0, str(this.settings.bit_depth))
        this.bit_entry.grid(row = 3, column = 1, sticky = "e", padx = 5, pady = 5)

        # use nearest-neighbor
        this.nearest_neighbor_entry = tkinter.BooleanVar(
            value = this.settings.use_nearest_neighbor
        )
        ttk.Checkbutton(
            input_frame, 
            text = "Use nearest-neighbor?", 
            variable = this.nearest_neighbor_entry
        ).grid(row = 4, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 5)

        # max workers
        ttk.Label(
            input_frame, 
            text = f"Parallel Workers (Max = {this.total_cpu_cores}):"
        ).grid(row = 5, column = 0, sticky = "w", padx = 5, pady = 5)
        this.max_workers_entry = ttk.Entry(input_frame, width = 15)
        this.max_workers_entry.insert(0, str(this.settings.max_workers))
        this.max_workers_entry.grid(row = 5, column = 1, sticky = "e", padx = 5, pady = 5)

        # use ds-psf
        this.ds_psf_entry = tkinter.BooleanVar(value = this.settings.use_ds_psf)
        ttk.Checkbutton(
            input_frame, 
            text = "Use double-sphere & PSF?", 
            variable = this.ds_psf_entry
        ).grid(row = 6, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 5)

        # use se-psf
        this.se_psf_entry = tkinter.BooleanVar(value = this.settings.use_se_psf)
        ttk.Checkbutton(
            input_frame, 
            text = "Use sphere-ellipse & PSF?", 
            variable = this.se_psf_entry
        ).grid(row = 7, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 5)

        # se-psf aspect ratio
        ttk.Label(
            input_frame, 
            text = "Sphere-Ellipse Aspect Ratio:"
        ).grid(row = 8, column = 0, sticky = "w", padx = 5, pady = 5)
        this.se_aspect_ratio_entry = ttk.Entry(input_frame, width = 15)
        this.se_aspect_ratio_entry.insert(0, str(this.settings.se_aspect_ratio))
        this.se_aspect_ratio_entry.grid(row = 8, column = 1, sticky = "e", padx = 5, pady = 5)

        # button
        button_frame = ttk.Frame(this)
        button_frame.pack(fill = "x", side = "bottom", pady = 15, padx = 20)
        
        ttk.Button(
            button_frame, text = "Cancel", command = this.destroy
        ).pack(side = "left", padx = 5)
        ttk.Button(
            button_frame, text = "Save Settings", command = this._saveSettings
        ).pack(side = "right", padx = 5)
# -------------------------------------------------- #
    def _saveSettings(this) -> None:
        '''
        PopupSetSettings._saveSettings()

        Copies all fields from the window, casts them to the correct corresponding data type, \
        then modifies the tracked Settings object in place. If any fields are invalid, this \
        process is aborted, allowing for user correction. Typically, this function is called \
        after pressing the "Save Settings" button in the rendered tkinter window.

        Parameters
        ----------
            - `_saveSettings` has no parameters.

        Returns
        -------
        *None*
            - No values are returned. The tracked Settings object is modified in place.

        Examples
        --------
        >>> popup._saveSettings()
        '''
        try:
            start_frame = int(this.start_entry.get().strip() or this.settings.start_frame)
            end_frame = int(this.end_entry.get().strip() or this.settings.end_frame)
            skipped_frames = [
                int(frame.strip()) 
                for frame in this.skipped_entry.get().split(",") 
                if frame.strip().isdigit()
            ]
            bit_depth = int(this.bit_entry.get().strip() or this.settings.bit_depth)
            use_nearest_neighbor = bool(this.nearest_neighbor_entry.get())
            max_workers = int(this.max_workers_entry.get().strip() or this.settings.max_workers)
            use_ds_psf = bool(this.ds_psf_entry.get())
            use_se_psf = bool(this.se_psf_entry.get())
            se_aspect_ratio = float(this.se_aspect_ratio_entry.get() or this.settings.se_aspect_ratio)
            
            if (
                start_frame > end_frame or 
                start_frame < 0 or 
                end_frame >= this.total_frames
            ):
                messagebox.showerror("Error", "Frame indices are invalid or out of sequence bounds.")
                return
            
            this.settings.start_frame = start_frame
            this.settings.end_frame = end_frame
            this.settings.skipped_frames = skipped_frames
            this.settings.bit_depth = bit_depth
            this.settings.use_nearest_neighbor = use_nearest_neighbor
            this.settings.max_workers = max_workers
            this.settings.use_ds_psf = use_ds_psf
            this.settings.use_se_psf = use_se_psf
            this.settings.se_aspect_ratio = se_aspect_ratio
            
            this.destroy()
        except Exception as error:
            messagebox.showerror("Error", f"Invalid input detected:\n{error}")
# ---------------------------------------------------------------------------------------------------- #
# You reached the bottom of gui.py
#
# You must be really interested in input sanitization and arranging GUI elements!
# (HINT): measure.py is where the analysis is done, this is only the setup and validation stage.
# Updates to fitting and profiles should be done there. DO NOT implement image analysis in gui.py
# ---------------------------------------------------------------------------------------------------- #