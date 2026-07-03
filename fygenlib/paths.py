# ---------------------------------------------------------------------------------------------------- #
#
#   ▄▄▄▄   ▄▄▄ ▄▄▄▄▄▄ ▄▄ ▄▄  ▄▄▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██▄█▀ ██▀██  ██   ██▄██ ███▄▄   ██▄█▀ ▀███▀ 
#   ██    ██▀██  ██   ██ ██ ▄▄██▀ ▄ ██      █
#
# ---------------------------------------------------------------------------------------------------- #
#
#   ------------------------------------------------------------
#   Development History & Contacts  |    (Reverse Chronological)
#   --------------------------------|---------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   Initial Pipeline                |    Tyler Frischknecht
#   ------------------------------------------------------------
#   Last Updated: 6/24/2024
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Handles path routing. Utility for other fygenlib scripts.
#
# ---------------------------------------------------------------------------------------------------- #
import os
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'getProjectPaths',
    'getProgramPaths'
]
# ---------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    print("This program serves no purpose to you if you're running it as main.")
    os._exit()
# ---------------------------------------------------------------------------------------------------- #
'''
THE FOLLOWING PATHS ARE RELATIVE TO THE ROOT DIRECTORY OF EACH EXPERIMENT 

    <ROOT>
    ├───<logs>
    │   ├───<...>
    │   └───<analysis_logs>    
    │       ├───analysis_log_X.csv
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
def getProjectPaths(Root):
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
THE FOLLOWING PATHS ARE RELATIVE TO THE WORKING DIRECTORY OF __main__

    <ROOT>
    ├───__main__.py
    ├───<fygenlib>
    │   ├───__init__.py
    │   ├───droplets.py
    │   ├───gui.py
    │   ├───measure.py
    │   └───paths.py
    └───<fygensettings>
        └───last_paths_analyzed.txt

Box drawing characters for future edits:
─ │ ┌ ┐ └ ┘ ┤ ├ ┬ ┴ ┼
'''
# ---------------------------------------------------------------------------------------------------- #
def getProgramPaths() -> os.PathLike | str:
    paths = {
        'settings' :    'fygensettings'
    }

    return paths
# ---------------------------------------------------------------------------------------------------- #