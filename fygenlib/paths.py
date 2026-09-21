# ---------------------------------------------------------------------------------------------------- #
#
#   ▄▄▄▄   ▄▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██▄█▀ ██▀██  ██   ██▄██ ███▄▄   ██▄█▀ ▀███▀ 
#   ██    ██▀██  ██   ██ ██ ▄▄██▀ ▄ ██      █
#
# ---------------------------------------------------------------------------------------------------- #
#
#   -------------------------------------------------------
#   Development History & Contacts
#   -------------------------------------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   paths.py                        |    Tyler Frischknecht
#   -------------------------------------------------------
#   Last Updated: 9/10/2026 - Ready for full release!
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Handles paths/file routing. Utility for other fygenlib modules.
#
# ---------------------------------------------------------------------------------------------------- #
import os
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'getProjectPaths',
    'getProgramPaths'
]
# ---------------------------------------------------------------------------------------------------- #
'''
THE FOLLOWING PATH HIERARCHY IS RECOMMENDED FOR UNMODIFIED USE OF bcds-main.py

    <NANOSTAR_CONCENTRATION_FOR_ANALYSIS>
    ├───<logs>
    │   ├───<...>
    │   └───<analysis_logs>    
    │       ├───CapXXX_analysis_log.csv
    │       └───...
    ├───<ilastik_data>
    │   ├───<masks>
    │   │   ├───CapXXX_Object Identities.tiff
    │   │   └───...
    │   └───<tables>
    │       ├───CapXXX_table.csv
    │       └───...
    ├───<plots>
    │   └───...
    ├───<movie>
    │   ├───movie.tif
    │   └───<frames>
    │       ├───CapXXX.tif
    │       └───...
    └───<segmentation_images>
        ├───CapXXX_segmentation_image.png
        └───...

Box drawing characters for future edits:
─ │ ┌ ┐ └ ┘ ┤ ├ ┬ ┴ ┼
'''
# ---------------------------------------------------------------------------------------------------- #
def getProjectPaths(Root : os.PathLike | str) -> dict[str, os.PathLike | str]:
    '''
    # getProjectPaths

    Returns all necessary paths for radial analysis as a dict, relative to the path passed as a \
    parameter. This function does not make directories, it instead maps out all useful paths.

    This function seems redundant, but it allows file architecture to be completely remapped \
    without updating the code across bcds or fygenlib. 

    Parameters
    ----------
    `Root` : *os.PathLike* | *str*
        - The parent folder which should contain a movie and ilastik_data folder before analysis. \
        Other folders such as logs or segmentation_images will be made and populated if not \
        existing.

    Returns
    -------
    *dict[str, os.PathLike | str]*
        - A dict of absolute paths for each folder required for analysis. Keys are the name of \
        each folder such as root, logs, movie, etc... while values are the corresponding path.

    Examples
    --------
    >>> concentration_path = R"/NS20J2/20uM"
    >>> paths_dict = getProjectPaths(concentration_path)
    >>> print(paths_dict['analysis_logs'])
    /NS20J2/20uM/logs/analysis_logs
    '''
    paths = {
        'root' :            Root,
        'logs' :            os.path.join(Root, 'logs'),
        'movie' :           os.path.join(Root, 'movie'),
        'segmentation' :    os.path.join(Root, 'segmentation_images'),
        'ilastik' :         os.path.join(Root, 'ilastik_data'),
    }
    
    paths['analysis_logs'] =    os.path.join(paths['logs'], 'analysis_logs')
    paths['analysis_settings'] = os.path.join(paths['logs'], 'analysis_settings')
    paths['meta_logs'] =        os.path.join(paths['logs'], 'meta_logs')
    paths['movie_frames'] =     os.path.join(paths['movie'], 'frames')
    paths['feature_tables'] =   os.path.join(paths['ilastik'], 'tables')
    paths['object_masks'] =    os.path.join(paths['ilastik'], 'masks')
    
    return paths
# ---------------------------------------------------------------------------------------------------- #
'''
THE FOLLOWING PATH HIERARCHY IS RECOMMENDED FOR UNMODIFIED USE OF bcds-main.py

    <bcds-engine>
    ├───bcds-main.py
    ├───<fygenlib>
    │   ├───__init__.py
    │   ├───drops.py
    │   ├───gui.py
    │   ├───measure.py
    │   ├───settings.py
    │   └───paths.py
    └───<.bcds_settings>
        └───last_paths_analyzed.txt

Box drawing characters for future edits:
─ │ ┌ ┐ └ ┘ ┤ ├ ┬ ┴ ┼
'''
# ---------------------------------------------------------------------------------------------------- #
def getProgramPaths() -> dict[str, os.PathLike | str]:
    '''
    # getProgramPaths

    Returns all necessary bcds specific directories for settings or persistent data. This \
    function does not make directories, it instead maps out all useful paths.

    This function seems redundant, but it allows file architecture to be completely remapped \
    without updating the code across bcds or fygenlib. 

    Parameters
    ----------
        - getProgramPaths has no parameters. Persistent program data is stored relative to \
        __main__

    Returns
    -------
    *dict[str, os.PathLike | str]*
        - A dict of absolute paths for each folder required for analysis. Keys are the name of \
        each folder such as settings, while values are the corresponding path.

    Examples
    --------
    >>> paths_dict = getProgramPaths()
    >>> print(paths_dict['settings'])
    /.bcds_settings
    '''

    paths = {
        'settings' :    '.bcds_settings'
    }

    return paths
# ---------------------------------------------------------------------------------------------------- #