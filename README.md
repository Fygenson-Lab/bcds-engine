# bcds-engine

Overview
--------
While machine learning and pixel-classification tools reliably detect the centers of circular intensity regions, phase bounds remain difficult
to measure due to diffractive blur at droplet phase boundaries, since humans training the model cannot accurately determine where the physical
boundary resides by eye. Since inaccuracies in radius propagate cubically when determining volume fraction, minimizing error in these radial 
measurements is required for accurate lever rule application and phase diagram generation.

bcds-engine pairs precomputed, neural-network identified center coordinates with raw microscopy frames to more accurately calculate physical 
phase boundaries, by accounting for phase boundary diffraction through the convolution of a fitted intensity manifold with a fitted Gaussian 
point-spread function on a per-drop basis.

Dependencies
------------
- **Python** >=3.10 (Tested on 3.14)
  - [All Releases](https://www.python.org/downloads/)
- **opencv-python** (Tested on 4.13.0.92)
  - `pip install opencv-python`
- **numpy** (Tested on 2.4.3)
  - `pip install numpy`
- **pandas** (Tested on 3.0.1)
  - `pip install pandas`
- **scipy** (Tested on 1.17.1)
  - `pip install scipy`
- **tkinter**: Included by default on Windows/Mac, must be installed through system package manager on Linux. 
  - `sudo apt install python3-tk`

Instructions
------------
1. Directory Setup 
  Organize your analysis files following the layout as organized in `fygenlib/paths.py`,
  or update `paths.py` to match your local structure. Each directory requires:
  - Extracted movie frames (`.tif` or `.tiff`) located in `<movie>/frames`
  - Feature tables (`.csv`) containing subpixel droplet centers located in `<ilastik_data>/tables`
    - Coordinates must be labeled with the column headers `Center of the object_0` (X) and `Center of the object_1` (Y).
    - Any CSV using these headers (from Ilastik or otherwise) is accepted.
  Directories missing these files will fail validation, and will not be processed.
2. Launch bcds-main.py 
  Upon launch, a Tkinter window will appear.
3. Configure Target Paths & Analysis Settings 
  In the Tkinter window, click `Add` to queue each parent directory containing the analysis files.
  Added directories are checked immediately, invalid directories (missing files or improperly organized) are
  highlighted in red and will be skipped over unless fixed, removed, and readded.
  Use `Move Up`, `Move Down`, or `Remove` to edit the order of analysis.
  Valid directories added for the first time will automatically open a settings popup window.
  For previously added/analyzed directories, this menu can be reopened using the `Settings` button.
  The following settings are available as of the most recent release:
  - **Start frame**: First image index to analyze
    - (default is the 0th frame when organized alphabetically)
  - **End frame**: Last image index to analyze
    - (default is the last frame when organized alphabetically)
  - **Skipped frames**: Comma separated frame indices between Start and End to remove from processing queue
    - (e.g., `4, 12, 18`)
  - **Image Bit Depth**: Image bit depth for preserving raw intensity ranges
    - (default is 12-bit for common microscope cameras)
  - **Use Nearest Neighbor**: Applies greedy nearest-neighbor chain logic algorithm to calculate dilute phase radii
    - (default is `True`)
  - **Parallel Workers**: Maximum CPU worker processes ran concurrently for all dense phase algorithms
    - (default is `10`, or capped to system core count if fewer than 10 are available)
  - **Use double-sphere & PSF**: Dense phase radius fitting using double-sphere convolution with a Gaussian PSF
    - (default is `True`)
  - **Use sphere-ellipse & PSF**: Experimental dense phase fitting modeling droplet gravitational flattening
    - (default is `False`)
  - **Sphere-Ellipse Aspect Ratio**: Ratio of vertical height to width ($z/xy$) for elliptical fitting.
    - Values $<1.0$ reflect pooling.
    - (default is `1.0`; ignored if SE & PSF is not selected)
4. Click `Run Analysis` to calculate all dilute and dense radii.
  A segmentation image (heatmap with overlaid dense and dilute radii circles), analysis log csv, and updates to a
  persistent error-tracking log will be generated for each parent directory queued.
