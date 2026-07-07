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
#   Initial Pipeline                |    Tyler Frischknecht
#   -------------------------------------------------------
#   Last Updated: 7/3/2026 - Updated year in 'Last Updated' section. It is 2026, not 2024...
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
THE FOLLOWING PATH HIERARCHY IS RECCOMENDED FOR UNMODIFIED USE OF bcds-main.py

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
THE FOLLOWING PATH HIERARCHY IS RECCOMENDED FOR UNMODIFIED USE OF bcds-main.py

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
    paths = {
        'settings' :    '.bcds_settings'
    }

    return paths
# ---------------------------------------------------------------------------------------------------- #