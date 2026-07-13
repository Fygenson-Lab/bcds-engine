# ---------------------------------------------------------------------------------------------------- #
#
#    ▄▄▄▄ ▄▄▄▄▄ ▄▄▄▄▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄  ▄▄▄▄  ▄▄▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ███▄▄ ██▄▄    ██     ██   ██ ███▄██ ██ ▄▄ ███▄▄   ██▄█▀ ▀███▀ 
#   ▄▄██▀ ██▄▄▄   ██     ██   ██ ██ ▀██ ▀███▀ ▄▄██▀ ▄ ██      █   
#
# ---------------------------------------------------------------------------------------------------- #
#
#   ------------------------------------------------------------
#   Development History & Contacts 
#   ------------------------------------------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   Initial Pipeline                |    Tyler Frischknecht
#   ------------------------------------------------------------
#   Last Updated: 7/3/2026 - Completed all Class & Function documentation
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Class structure to store which methods to apply during analysis of a DropImage, and other analysis 
#   utilities
#
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'Settings'
]
# ---------------------------------------------------------------------------------------------------- #
class Settings:
    '''
    # Settings

    Stores which methods to apply during analysis of a DropImage, and other analysis utilities.

    Member Variables
    ----------------
    `bit_depth` : *int*
        - The bit depth of a single pixel in each emulsion image. Many libraries cannot handle \
        bit depths outside 2^N. This setting preserves intensity scales between conversions.
    `start_frame` : *int*
        - The starting index for analysis. Note that alphanumeric values in the frame's file name \
        do not pertain to start_frame. Instead, start_frame represents the n-th file name when sorted \
        alphabetically.
    `end_frame` : *int*
        - The ending index for analysis. Note that alphanumeric values in the frame's file name \
        do not pertain to end_frame. Instead, end_frame represents the n-th file name when sorted \
        alphabetically. 
    `skipped_frames` : *list[int]*
        - A list of all indices to skip during analysis. Like start_frame and end_frame, these \
        indices represent the n-th file name when sorted alphabetically.
    `use_nearest_neighbor` : *bool*
        - The main supported dilute radius calculation method. Uses a greedy nearest-neighbor \
        model to calculate dilute radii for all drops based on relative distance from one another.
    `use_ds_psf` : *bool*
        - The main supported dense radius calculation method. Uses a 'double-sphere' equation, \
        convolved with a Gaussian point spread function to iteratively fit the intensity profile \
        of a drop within its previously calculated dilute radius. The emulsion is characterized \
        as a sphere containing its own spherical condrop.
    `use_se_psf` : *bool*
        - An experimental dense radius calculation method. Similar to the 'ds_psf' method above, \
        it uses an intensity equation and Gaussian blur convolution. Instead of a sphere, the \
        condrop is characterized as an ellipse to account for gravity and oblating.

    Member Functions
    ----------------
    `set`
        - Sets one or more parameters of this object at once with keyword arguments.
    `setDefaults`
        - Sets all settings to default values.
    '''
# -------------------------------------------------- #
    bit_depth :         int
    start_frame :       int
    end_frame :         int
    skipped_frames :    list[int]
    # dilute radius methods
    use_nearest_neighbor :  bool
    # dense radius methods
    use_ds_psf :    bool
    use_se_psf :    bool
# -------------------------------------------------- #
    # Not used for optimization, but as an architecture safeguard
    __slots__ = [
        "bit_depth",
        "start_frame",
        "end_frame",
        "skipped_frames",
        "use_nearest_neighbor",
        "use_ds_psf",
        "use_se_psf"
    ]
# -------------------------------------------------- #
    def __init__(this, **Parameters) -> None:
        '''
        # Settings.__init__

        Initializes the Settings object, sets defaults, then reassigns any passed parameters.

        Parameters
        ----------
        `**Parameters` : *dict*
            - Keyword arguments representing attributes defined in this object's __slots__, and \
            their new values.
        
        Returns
        -------
        *None*
            - No values are returned from initialization functions.

        Raises
        ------
        *AttributeError*
            - If any provided keyword argument is not a valid attribute of \
            this object's __slots__.

        Examples
        --------
        >>> settings = Settings(bit_depth = 16, start_frame = 4) 
        '''

        this.setDefaults()

        if Parameters:
            this.set(**Parameters)
# -------------------------------------------------- #
    def set(this, **Parameters) -> None:
        '''
        # Settings.set

        Sets one or more parameters of this object at once with keyword arguments. Used as an \
        alternative to direct access of member variables for bulk setting.

        Parameters
        ----------
        `**Parameters` : *dict*
            - Keyword arguments representing attributes defined in this object's __slots__, and \
            their new values.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Raises
        ------
        *AttributeError*
            - If any provided keyword argument is not a valid attribute of \
            this object's __slots__.

        Examples
        --------
        >>> settings.set(bit_depth = 16, start_frame = 4) 
        '''

        for key, value in Parameters.items():
            if key in this.__slots__:
                setattr(this, key, value)
            else:
                raise AttributeError(f"{key} is not a valid attribute")
# -------------------------------------------------- #
    def setDefaults(this) -> None:
        '''
        # Settings.setDefaults

        Sets all settings to default values.
        bit_depth is 12 bits by default, a common microscope camera bit resolution.
        start_frame, end_frame, and skipped_frames are set to analyze all frames by default.
        use_nearest_neighbor and use_ds_psf are enabled by default, while all other experimental \
        fitting methods are disabled by default.

        Parameters
        ----------
            - `setDefaults` has no parameters.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Examples
        --------
        >>> settings.setDefaults()
        '''

        this.bit_depth =        12
        this.start_frame =      0
        this.end_frame =        -1
        this.skipped_frames =   []

        this.use_nearest_neighbor = True
        this.use_ds_psf = True
        this.use_se_psf = False
# ---------------------------------------------------------------------------------------------------- #