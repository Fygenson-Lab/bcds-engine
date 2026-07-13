# ---------------------------------------------------------------------------------------------------- # 
#
#   ▄▄▄▄  ▄▄▄▄   ▄▄▄  ▄▄▄▄   ▄▄▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██▀██ ██▄█▄ ██▀██ ██▄█▀ ███▄▄   ██▄█▀ ▀███▀ 
#   ████▀ ██ ██ ▀███▀ ██    ▄▄██▀ ▄ ██      █
#
# ---------------------------------------------------------------------------------------------------- #
#
#   --------------------------------------------------------------------------------------
#   Development History & Contacts       (Reverse Chronological)
#   --------------------------------------------------------------------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   Core Architecture Overhaul      |    Tyler Frischknecht
#   Legacy Versions & Revisions     |    Tyler Frischknecht, Thomas Reese, Nicholas Phelps
#   Initial Pipeline                |    Thomas Reese, Nicholas Phelps
#   --------------------------------------------------------------------------------------
#   Last Updated: 6/29/2026 - Completed all Class & Function documentation
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Complete overhaul of legacy library bubbles.py
#   - Classes now storage and export only, data processing now initiated in dedicated sub modules
#   - Using OpenCV (cv2) instead of slower skimage & matplotlib libraries for reading and writing 
#     images
#   - Cleaner implementation of pandas for CSV export
#
#   Drop
#   - Stores processed data as dicts for dynamic insertion of different or new fitting methods
#
#   DropImage
#   - Stores image data and Drop data
#   - Exports dataset as .csv
#   - Exports segmented image as .png
#
# ---------------------------------------------------------------------------------------------------- #
import cv2
import numpy
import pandas
#
from os import PathLike as os_PathLike
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'Drop',
    'DropImage'
]
# ---------------------------------------------------------------------------------------------------- #
class Drop:
    '''
    # Drop

    Stores coordinates and analysis results for a single drop. Primary data component of DropImage.

    Member Variables
    ----------------
    `x` : *float*
        - The x-coordinate this Drop is located at in the original DropImage. Used for radial \
        analysis.
    `y` : *float*
        - The y-coordinate this Drop is located at in the original DropImage. Used for radial \
        analysis.
    `index` : *int*
        - The index this Drop is within a DropImage. Used as a key for lookup in DropImage \
        methods.
    `dilute_radius_dict` : *dict[str, float]*
        - Dynamic table of all calculated dilute radii. Keys accessed by fitting method name, \
        i.e. "nearest-neighbor". Values represent calculated radii.
    `dense_radius_dict` : *dict[str, float]*
        - Dynamic table of all calculated dense radii. Keys accessed by fitting method name, i.e. \
        "ds_psf". Values represent calculated radii.
    `fitting_coeff_dict` : *dict[str, float]*
        - Dynamic table of all coefficients used in dilute and dense radius fitting. Keys \
        accessed by coefficient name + fitting method name i.e. "background_ds_psf". Values \
        represent fitted coefficients.

    Member Functions
    ----------------
    `set`
        - Sets one or more parameters of this object at once with keyword arguments. Used as an \
        alternative to direct access of member variables for bulk setting.

    Instantiation
    -------------
    >>> drop = Drop(x, y)
    >>> drop = Drop(x, y, index)
    '''
# -------------------------------------------------- #
    x :                     float
    y :                     float
    index :                 int
    dilute_radius_dict :    dict[str, float]
    dense_radius_dict :     dict[str, float]
    fitting_coeff_dict :    dict[str, float]
# -------------------------------------------------- #
    # Not used for optimization, but as an architecture safeguard
    __slots__ = [
        "x", 
        "y", 
        "index",
        "dilute_radius_dict", 
        "dense_radius_dict", 
        "fitting_coeff_dict"
    ]
# -------------------------------------------------- #
    def __init__(this, X : float, Y : float, Index : int | None = None) -> None:
        '''
        # Drop.__init__

        Constructor for Drop object.

        Parameters
        ----------
        `X` : *float*
            - Passed to Drop.x
        `Y` : *float*
            - Passed to Drop.y
        `Index` : *int*, optional
            - Passed to Drop.index

        Returns
        -------
        *None*
            - No values are returned from initialization functions.

        Examples
        --------
        >>> drop = Drop(1.2, 3.4)
        >>> drop = Drop(1.2, 3.4, Index = 0)
        '''

        # data passed at initialization
        this.x = X
        this.y = Y
        this.index = Index

        # data to be populated during analysis
        this.dilute_radius_dict =    {}
        this.dense_radius_dict =     {}
        this.fitting_coeff_dict =    {}
# -------------------------------------------------- #
    def set(this, **Parameters) -> None:
        '''
        # Drop.set

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
        >>> drop1.set(x = 123.4, y = 567.8) 
        >>> drop2.set(
        ...     dilute_radius_dict = drop2.dilute_radius_dict.copy(),
        ...     dense_radius_dict = drop2.dense_radius_dict.copy(),
        ...     fitting_coeff_dict = drop2.fitting_coeff_dict.copy()
        ... )
        '''

        for key, value in Parameters.items():
            if key in this.__slots__:
                setattr(this, key, value)
            else: 
                raise AttributeError(f"{key} is not a valid attribute")
# ---------------------------------------------------------------------------------------------------- #
class DropImage:
    '''
    # DropImage

    Stores a 2x2 matrix of pixel intensities across a full image of emulsions, associated bit \
    depth, and list of Drop objects as one unit. Handles widescale data organization and file \
    export.

    Member Variables
    ----------------
    `image` : *numpy.ndarray*
        - The raw 2x2 matrix of pixel intensities across a full raw image of emulsions.
    `bit_depth` : *int*
        - The associated bit depth of the emulsion image. Used to preserve the relativity \
        of pixel intensities as it's converted to new datatypes by imported libraries.
    `drops` : *list[Drop]*
        - List of Drop objects describing regions across the full image of emulsions.

    Member Functions
    ----------------
    `addDrop`
        - Adds a Drop object to DropImage list.
    `addDrops`
        - Adds list of Drop objects in bulk to DropImage list, in order.
    `removeDrop`
        -  Removes a target Drop from DropImage. Handles Drop index reassignment natively.
    `setDrops`
        - Clears and sets list of Drop objects in bulk to DropImage's stored list.
    `writeCSV`
        - Exports all data collected during analysis as a CSV.
    `segmentationImage`
        - Generates an 8-bit heatmap image with calculated dilute and dense radii circles \
        superimposed over each analyzed Drop.

    Instantiation
    -------------
    >>> drop_image = DropImage(Image_Matrix)
    >>> drop_image = DropImage(Image_Matrix, Bit_Depth = 12)
    '''
# -------------------------------------------------- #
    image :     numpy.ndarray
    bit_depth : int
    drops :     list[Drop]
# -------------------------------------------------- #
    # Not used for optimization, but as an architecture safeguard
    __slots__ = [
        "image",
        "bit_depth",
        "drops"
    ]
# -------------------------------------------------- #
    def __init__(
        this, 
        Image : numpy.ndarray, 
        Bit_Depth : int = 12, 
    ) -> None:
        '''
        # DropImage.__init__

        Constructor for DropImage object.

        Parameters
        ----------
        `Image` : *numpy.ndarray*
            - A 2x2 matrix of pixel intensities across a full image of emulsions.
        `Bit_Depth` : *int*, optional
            - The bit depth of the raw image. CV2, used across functions of DropImage, stores \
            data in slices of 2^N. This keeps track of what the underlying data type should be.
        
        Returns
        -------
        *None*
            - No values are returned from initialization functions.

        Examples
        --------
        >>> drop_image = DropImage(Image_Matrix)
        >>> drop_image = DropImage(Image_Matrix, Bit_Depth = 12)
        '''

        this.image = Image
        this.bit_depth = Bit_Depth
        this.drops = []
# -------------------------------------------------- #
    def addDrop(this, New_Drop : Drop) -> None:
        '''
        # DropImage.addDrop

        Adds a Drop object to DropImage list.

        Parameters
        ----------
        `New_Drop` : *fygenlib.Drop*
            - The previously instantiated Drop object to be added.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Examples
        --------
        >>> drop_image.addDrop(existing_drop)
        >>> drop_image.addDrop(Drop(1.2, 3.4))
        '''

        index = len(this.drops)
        New_Drop.index = index
        this.drops.append(New_Drop)
# -------------------------------------------------- #
    def addDrops(this, Drops : list[Drop]) -> None:
        '''
        # DropImage.addDrops

        Adds list of Drop objects in bulk to DropImage list, in order.

        Parameters
        ----------
        `Drops` : *list[fygenlib.Drop]*
            - The list previously instantiated Drop objects to be added, in order.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Examples
        --------
        >>> drop_image.addDrops([drop1, drop2, drop3])
        '''

        for drop in Drops:
            this.addDrop(drop)
# -------------------------------------------------- #
    def removeDrop(this, Target_Drop : Drop):
        '''
        # DropImage.removeDrop
        
        Removes a target Drop from DropImage. Handles Drop index reassignment natively.
        If target Drop is not found in list, function returns silently.

        Parameters
        ----------
        `Target_Drop` : *fygenlib.Drop*
            - Target Drop object to be removed from DropImage storage.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Examples
        --------
        >>> drop_image.removeDrop(drop)
        '''

        if Target_Drop not in this.drops:
            return
        
        target_index = this.drops.index(Target_Drop)
        this.drops.pop(target_index)
        
        for drop_index in range(target_index, len(this.drops)):
            this.drops[drop_index].index -= 1
# -------------------------------------------------- #
    def setDrops(this, Drops : list[Drop]) -> None:
        '''
        # DropImage.setDrops

        Clears and sets list of Drop objects in bulk to DropImage's stored list.

        Parameters
        ----------
        `Drops` : *list[fygenlib.Drops]*
            - The list previously instantiated Drop objects to be added, in order.

        Returns
        -------
        *None*
            - No values are returned from this function. Mutates this object in place.

        Examples
        --------
        >>> drop_image.setDrops([drop1, drop2, drop3])
        '''
                
        this.drops = []
        for drop in Drops:
            this.addDrop(drop)
# -------------------------------------------------- #
    def writeCSV(this, Export_Path : os_PathLike | str) -> None:
        '''
        # DropImage.writeCSV

        Exports all data collected during analysis as a CSV.

        All calculated dilute radii are added by fitting method name:
        - dilute_radius_<fitting_method>, i.e. "dilute_radius_nearest_neighbor"

        All calcualted dense radii are added by fitting method name:
        - "dense_radius_<fitting_method>", i.e. "dense_radius_dspsf"

        All additional fitting parameters are added by name, and fitting method name:
        - "<parameter>_<fitting_method>", i.e. "sigma_ds_psf"

        Parameters
        ----------
        `Export_Path` : *os.PathLike* | *str*
            - Target destination for analysis log CSV.

        Returns
        -------
        *None*
            - No values are returned from this function. An analysis log CSV is saved at the \
            passed target destination.

        Examples
        --------
        >>> drop_image.writeCSV("C:\\users\\fygenson\\logs\\analysis_log.csv")
        '''

        complete_data_dictlist = []

        for drop in this.drops:
            row = {
                "xcen" : drop.x,
                "ycen" : drop.y
            }

            for fitting_method, value in drop.dilute_radius_dict.items():
                row[f"dilute_radius_{fitting_method}"] = value

            for fitting_method, value in drop.dense_radius_dict.items():
                row[f"dense_radius_{fitting_method}"] = value

            for name, value in drop.fitting_coeff_dict.items():
                row[name] = value if value is not None else numpy.nan

            complete_data_dictlist.append(row)

        dataframe = pandas.DataFrame(complete_data_dictlist)
        dataframe.to_csv(Export_Path, index = False)
# -------------------------------------------------- #
    def segmentationImage(
        this, 
        Export_Path : os_PathLike | str, 
        Dilute_Method : str, 
        Dense_Method : str
    ) -> None:
        '''
        # DropImage.segmentationImage

        Generates an 8-bit heatmap image with calculated dilute and dense radii circles \
        superimposed over each analyzed Drop.

        Parameters
        ----------
        `Export_Path` : *os.PathLike* | *str*
            - Target destination for segmentation image.
        `Dilute_Method` : *str*
            - Desired dilute radius calculation method for superimposed circles.
        `Dense_Method` : *str*
            - Desired dense radius calculation method for superimposed circles.

        Returns
        -------
        *None*
            - No values are returned from this function. A segmentation image is saved at the \
            passed target destination.

        Examples
        --------
        >>> drop_image.segmentationImage(
        ...     "C:\\users\\fygenson\\images\\segmentation_image.png",
        ...     "nearest_neighbor",
        ...     "ds_psf"
        ... )
        '''

        # normalize image to 8-bit for visual export
        max_intensity = (2 ** this.bit_depth) - 1
        normalized_image = (
            this.image.astype('float32') * (255.0 / max_intensity)
        ).astype('uint8')
        # apply heatmap
        segmentation_image = cv2.applyColorMap(normalized_image, cv2.COLORMAP_VIRIDIS)
        # draw circles
        for drop in this.drops:
            dilute_radius = drop.dilute_radius_dict.get(Dilute_Method, 0)
            dense_radius = drop.dense_radius_dict.get(Dense_Method, 0)
        
            # check to see if circle has both a dense and dilute radius
            if (
                numpy.isnan(dilute_radius) or 
                dilute_radius <= 0 or 
                numpy.isnan(dense_radius) or 
                dense_radius <= 0 or
                dense_radius >= dilute_radius
            ):
                continue

            center = (int(drop.x), int(drop.y))

            shift_bits = 4
            scale_factor = 1 << shift_bits
            
            subpixel_center = (int(center[0] * scale_factor), int(center[1] * scale_factor))
            subpixel_dilute = int(dilute_radius * scale_factor)
            subpixel_dense = int(dense_radius * scale_factor)
            
            cv2.circle(
                segmentation_image, subpixel_center, subpixel_dilute, (255,0,0), 1, 
                lineType = cv2.LINE_AA, shift = shift_bits
            )
            cv2.circle(
                segmentation_image, subpixel_center, subpixel_dense, (0,0,255), 1, 
                lineType = cv2.LINE_AA, shift = shift_bits
            )

        cv2.imwrite(Export_Path, segmentation_image)
# ---------------------------------------------------------------------------------------------------- #