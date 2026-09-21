# ---------------------------------------------------------------------------------------------------- #
#
#   ▄▄   ▄▄ ▄▄▄▄▄  ▄▄▄   ▄▄▄▄ ▄▄ ▄▄ ▄▄▄▄  ▄▄▄▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██▀▄▀██ ██▄▄  ██▀██ ███▄▄ ██ ██ ██▄█▄ ██▄▄    ██▄█▀ ▀███▀ 
#   ██   ██ ██▄▄▄ ██▀██ ▄▄██▀ ▀███▀ ██ ██ ██▄▄▄ ▄ ██      █   
#
# ---------------------------------------------------------------------------------------------------- #
#
#   -------------------------------------------------------------------------------------
#   Development History & Contacts |    (Reverse Chronological)
#   -------------------------------|-----------------------------------------------------
#   Principal Investigator         |    Deborah Fygenson
#   Project Guidance               |    Thomas Reese
#   Complete Architecture Overhaul |    Tyler Frischknecht
#   Legacy Versions & Revisions    |    Tyler Frischknecht, Thomas Reese, Nicholas Phelps
#   Initial Pipeline               |    Thomas Reese, Nicholas Phelps
#   -------------------------------------------------------------------------------------
#   Last Updated: 9/18/2026 - Ready for full release!
#
# ---------------------------------------------------------------------------------------------------- #
#
#   Complete overhaul of dil_radius.py and den_radius.py analysis methods, rebuilt from scratch.
#
#   Dilute Radius Methods:
#   "nearest_neighbor"
#       - Calculates all possible distances between each Drop, Drop pair 
#       - Sorts all distances pairs from smallest to largest
#       - Filters all distance pairs leaving only nearest-neighbor pairs
#       - In ascending order, assigns radii by halfway point or intersection point
#
#   Dense Phase Methods
#   "ds_psf"
#       - Fits a sphere-in-sphere (double sphere) manifold to each drop, convolved with a 
#         normalized Gaussian, with fitting parameters:
#           - A: Intensity scaling factor for the dense phase excluding the scaling factor for the
#             dilute phase.
#           - B: Intensity scaling factor for the dilute phase.
#           - Background: Ambient image intensity. Acts as an added constant post-convolution.
#           - Sigma: Gaussian blur characteristic width, corresponding to the point-spread-function
#             of a real-world microscope.
#           - Dense_Radius: Radius of the dense phase region of a droplet.
#       - Calculates reduced chi-square for later analysis of fit quality.
#   "se_psf"
#       - Fits an ellipse-in-sphere manifold to each drop, convolved with a normalized Gaussian, 
#         with fitting parameters:
#           - A: Intensity scaling factor for the dense phase excluding the scaling factor for the
#             dilute phase. Compressed or stretched into an elliptical intensity profile by the 
#             user-supplied aspect ratio/scale factor.
#           - B: Intensity scaling factor for the dilute phase.
#           - Background: background image intensity. Acts as an added constant post-convolution.
#           - Sigma: Gaussian blur characteristic width, corresponding to the point-spread-function
#             of a real-world microscope.
#           - Dense_Radius: Radius of the dense phase region of a droplet.
#       - Calculates reduced chi-square for later analysis of fit quality.
#
# ---------------------------------------------------------------------------------------------------- #
import math
import numpy
import os
#
from concurrent.futures import ProcessPoolExecutor
from functools import partial as Partial
from scipy.ndimage import gaussian_filter as gaussianFilter
from scipy.optimize import curve_fit as curveFit
from scipy.optimize import OptimizeWarning
#
from fygenlib import DropImage, Drop
# ---------------------------------------------------------------------------------------------------- #
__all__ = [
    'computeAllDiluteRadiusNN', 
    'parallelComputeAllDenseRadiusDSPSF',
    'parallelComputeAllDenseRadiusSEPSF'
]
# ---------------------------------------------------------------------------------------------------- #
#
#   DILUTE RADIUS MODEL: NEAREST NEIGHBOR
#   "nearest_neighbor"
#
# ---------------------------------------------------------------------------------------------------- #
def computeAllDiluteRadiusNN(
    Drop_Image : DropImage, 
    Min_Radius : float, 
    Method_Name : str = "nearest_neighbor"
) -> None:
    '''
    # computeAllDiluteRadiusNN

    Computes dilute radii for all Drop objects in a `DropImage`.
    Uses continuous nearest-neighbor chain logic, while former methods used discrete bubble \
    simulation.

    Parameters
    ----------
    `Drop_Image` : *DropImage*
        - Container of all `Drop` objects. Each must have an x and y float assigned.
    `Min_Radius` : *float*
        - The minimum radius threshold, in pixel distance, for a nearest neighbor pair to be used.
    `Method_Name` : *str*, optional
        - Identifier key for this analysis method. Defaults to "nearest_neighbor".

    Returns
    -------
    *None*
        No values are returned. Mutates Drop objects in place.
        Sets Drop.dilute_radius_dict[Method_Name] to computed radius.

    Examples
    --------
    >>> drop_image = DropImage(Image_Matrix)
    >>> drop_image.addDrops([Drop(0.0, 0.0), Drop(1.1, 1.1), Drop(2.2, 2.2)])
    >>> computeAllDiluteRadiusNN(drop_image, 0.2)
    '''

    all_neighbor_distances = _computeAllDistancesNN(Drop_Image)
    sorted_neighbor_distances = _sortAllDistancesNN(all_neighbor_distances, Exclude_Below = Min_Radius * 2)
    nearest_neighbor_set = _filterNearestNeighborsNN(sorted_neighbor_distances)
    _assignDiluteRadiusNN(nearest_neighbor_set, Method_Name)
# -------------------------------------------------- #
def _assignDiluteRadiusNN(
    Nearest_Neighbor_Set : list[tuple[Drop, Drop, float]], 
    Method_Name : str
) -> None:
    '''
    # _assignDiluteRadiusNN

    Assigns each `Drop` object in `Nearest_Neighbor_Set` a dilute radius under the following \
    chain logic:
    - Neither drop has an assigned Dilute Radius:
        -> Dilute Radius for both drops is (distance/2)
    - One drop has an assigned Dilute Radius:
        -> Dilute Radius for the unassigned drop is (distance - other's_radius)
    - Both drops have an assigned Dilute Radius:
        -> Do not overwrite, do nothing, continue

    Parameters
    ----------
    `Nearest_Neighbor_Set` : *list[tuple[Drop, Drop, float]]*
        - A list of `Drop`, `Drop` pairs sorted from shortest to farthest distance, must only contain \
        nearest-neighbors.
    `Method_Name` : *str*
        - Identifier key for this analysis method.

    Returns
    -------
    *None*
        No values are returned. However, Each `Drop.dilute_radius_dict` object is assigned a float.

    Examples
    --------
    >>> _assignDiluteRadiusNN(nearest_neighbor_set)
    >>> _assignDiluteRadiusNN(nearest_neighbor_set, "nearest_neighbor")
    '''

    for drop_a, drop_b, dist in Nearest_Neighbor_Set:

        radius_a = drop_a.dilute_radius_dict.get(Method_Name, None)
        radius_b = drop_b.dilute_radius_dict.get(Method_Name, None)
        # neither drop have assigned radiii
        if radius_a is None and radius_b is None:
            drop_a.dilute_radius_dict[Method_Name] = dist/2
            drop_b.dilute_radius_dict[Method_Name] = dist/2
        # one drop has assigned radius
        elif radius_a is not None and radius_b is None:
            drop_b.dilute_radius_dict[Method_Name] = dist - radius_a
        elif radius_b is not None and radius_a is None:
            drop_a.dilute_radius_dict[Method_Name] = dist - radius_b
        # both drops have assigned radii
        else:
            continue
# -------------------------------------------------- #
def _computeAllDistancesNN(Drop_Image : DropImage) -> list[tuple[Drop, Drop, float]]:
    '''
    # _computeAllDistancesNN

    Generates a list of all possible Drop-Drop pairs and distances.

    Parameters
    ----------
    `Drop_Image` : *DropImage*
        - Container of all `Drop` objects. Each must have an `x` and `y` float assigned.

    Returns
    -------
    *list[tuple[Drop, Drop, float]]*
        - A list of all possible `Drop`-`Drop` combinations and distances. Unsorted.
        - (Drop_1, Drop_2, Distance_Float)

    Examples
    --------
    >>> _computeAllDistancesNN(drop_image)
    '''

    drop_count = len(Drop_Image.drops)
    pair_distances = []

    for i in range(drop_count):
        for j in range(i+1, drop_count):
            pair_distances.append((
                Drop_Image.drops[i], 
                Drop_Image.drops[j], 
                _distance(
                    (Drop_Image.drops[i].x, Drop_Image.drops[i].y),
                    (Drop_Image.drops[j].x, Drop_Image.drops[j].y)
                )
            ))

    return pair_distances
# -------------------------------------------------- #
def _filterNearestNeighborsNN(
    Sorted_Distances : list[tuple[Drop, Drop, float]]
) -> list[tuple[Drop, Drop, float]]:
    '''
    # _filterNearestNeighborsNN

    Filters a list of sorted Drop-Drop pairs and distances. Generates a subset of \
    nearest-neighbor pairs only.

    Parameters
    ----------
    `Sorted_Distances` : *list[tuple[Drop, Drop, float]]*
        - List of (Drop_1, Drop_2, Distance_Float) tuples sorted in ascending order by distance.

    Returns
    -------
    *list[tuple[Drop, Drop, float]]*
        - Filtered subset of pairs where at least one Drop in the pair was not previously \
        matched.
        - (Drop_1, Drop_2, Distance_Float)

    Examples
    --------
    >>> _filterNearestNeighborsNN(sorted_distances)
    '''

    logged_drops = set()
    nearest_neighbors = []

    for drop_a, drop_b, dist in Sorted_Distances:
        # if either drop a or b is new to the set, it is a nearest neighbor
        if drop_a not in logged_drops or drop_b not in logged_drops:
            nearest_neighbors.append((drop_a, drop_b, dist))

            logged_drops.add(drop_a)
            logged_drops.add(drop_b)
            
    return nearest_neighbors
# -------------------------------------------------- #
def _sortAllDistancesNN(
    Pair_Distances : list[tuple[Drop, Drop, float]], 
    Exclude_Below : float
) -> list[tuple[Drop, Drop, float]]:
    '''
    # _sortAllDistancesNN

    Sorts all `Drop`-`Drop` pairs by distance, smallest to largest, filtering out pairs belowe a \
    minimum threshold.

    Parameters
    ----------
    `Pair_Distances` : *list[tuple[Drop, Drop, float]]*
        - Unsorted list of `(Drop_1, Drop_2, Distance_Float)` tuples.
    `Exclude_Below` : *float*
        - Minimum distance cutoff. Pairs with a distance less than this value are excluded.

    Returns
    -------
    *list[tuple[Drop, Drop, float]]*
        - Filtered list of pairs sorted in ascending order by distance.
        - `(Drop_1, Drop_2, Distance_Float)`
    '''

    filtered_pairs = [pair for pair in Pair_Distances if pair[2] >= Exclude_Below]
    return sorted(filtered_pairs, key = lambda pair : pair[2])
# ---------------------------------------------------------------------------------------------------- #
#
#   DENSE RADIUS MODEL: DOUBLE SPHERE FUNCTION - PSF
#   [Deprecated]
#   "ds_psf"
#
# ---------------------------------------------------------------------------------------------------- #
def computeAllDenseRadiusDSPSF(
    Full_Dataset : DropImage,
    Min_Pixels : int = 25,
    Dilute_Method_Name : str = "nearest_neighbor",
    Dense_Method_Name : str = "ds_psf"
) -> None:
    '''
    # computeAllDenseRadiusDSPSF

    [Deprecated]

    Retained as a historical reference for the currently used parallelized implementation. \
    Note that updates to shared helper functions may cause this to produce unexpected results.

    Computes the dense radius for each Drop in a DropImage by fitting a double sphere function \
    to the image data within its dilute radius, convolved with a normalized Gaussian to account \
    for the point spread function of a real-world microscope setup.

    Parameters
    ----------
    `Full_Dataset` : *DropImage*
        - Container holding the full image matrix and sequence of `Drop` objects to analyze.
    `Min_Pixels` : *int*, optional
        - Minimum pixel count required in the cropped drop region to attempt fitting. Defaults to \
        25. Drops below this threshold are assigned NaN.
    `Dilute_Method_Name` : *str*, optional
        - Key used to retrieve each Drop's previously computed dilute radius from \
        `dilute_radius_dict`. Defaults to "nearest_neighbor". As there is currently only one \
        dilute radius calculation method, it is recommended to keep this value as-is.
    `Dense_Method_Name` : *str*, optional
        - Identifier key for this analysis method. Defaults to "ds_psf".

    Returns
    -------
    *None*
        - No values are returned. Mutates Drop objects in place under \
        `Drop.dense_radius_dict[Dense_Method_Name]` and \
        `Drop.fitting_coeff_dict[<Parameter_Name> + Dense_Method_Name]` for all calculated values.

    Examples
    --------
    >>> computeAllDenseRadiusDSPSF(drop_image)
    '''

    print_queue = []

    for drop in Full_Dataset.drops:
        drop_data, drop_mask, x_grid, y_grid = _cropDrop(
            Full_Dataset.image,
            drop.x,
            drop.y,
            drop.dilute_radius_dict.get(Dilute_Method_Name, 0.0)
        )

        if len(drop_data) < Min_Pixels:
            print_queue.append(f"\nNot enough pixels in drop {drop.index} for analysis. Skipping dense radius fit...")
            _setDenseRadiusNanDSPSF(drop, Dense_Method_Name)
            continue

        print_queue.append(_computeDenseRadiusDSPSF(
            drop,
            drop_data,
            drop_mask,
            x_grid,
            y_grid,
            Dense_Method_Name = Dense_Method_Name
        ))
        if drop.index % 10 == 0 and len(print_queue) > 0:
            print('\n'.join(print_queue))
            print_queue.clear()
# -------------------------------------------------- #
def _computeDenseRadiusDSPSF(
    Drop_Obj : Drop,
    Drop_Data : numpy.ndarray[tuple[int], any], 
    Drop_Mask : numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
    X_Grid : numpy.ndarray,
    Y_Grid : numpy.ndarray,

    Guess : list = None,
    Lower_Bounds : list = None,
    Upper_Bounds : list = None,
    Dilute_Method_Name : str = "nearest_neighbor",
    Dense_Method_Name : str = "ds_psf",
) -> str:
    '''
    # _computeDenseRadiusDSPSF

    [Deprecated]

    Retained as a historical reference for the currently used parallelized implementation. \
    Note that updates to shared helper functions may cause this to produce unexpected results.

    Computes the dense radius of a single drop by fitting a double sphere function to the image \
    data within its dilute radius, convolved with a normalized Gaussian to account for the point \
    spread function of a real-world microscope setup.

    Parameters
    ----------
    `Drop_Obj` : *Drop*
        - The `Drop` instance being analyzed. Must have an assigned dilute radius under \
        `Dilute_Method_Name`.
    `Drop_Data` : *numpy.ndarray[tuple[int], any]*
        - A 1D flattened array of masked pixel intensity values within the `Drop`'s dilute radius.
    `Drop_Mask` : *numpy.ndarray[tuple[int, int], numpy.dtype[bool]]*
        - A 2D boolean matrix describing the original shape of `Drop_Data` before flattening.
    `X_Grid` : *numpy.ndarray*
        - A 2D meshgrid of x-coordinates centered on the drop.
    `Y_Grid` : *numpy.ndarray*
        - A 2D meshgrid of y-coordinates centered on the drop.
    `Guess` : *list*, optional
        - Initial fit parameters `[r_dense, background, A, B, sigma]`. If None, defaults are \
        estimated from the dilute radius and image intensity extrema.
    `Lower_Bounds` : *list*, optional
        - Lower parameter optimization bounds for `scipy.optimize.curve_fit`. Defaults \
        to [0, 0, 0, 0, 0].
    `Upper_Bounds` : *list*, optional
        - Upper parameter optimization bounds for `scipy.optimize.curve_fit`. Defaults \
        to `[dilute_radius, max_intensity, inf, inf, inf]`. It is recommended to keep the upper \
        bounds for fitting parameters free, as there is less physical motivation to constrain them.
    `Dilute_Method_Name` : *str*, optional
        - Dictionary key used to look up the precomputed dilute radius on `Drop_Obj`. \
        Defaults to "nearest_neighbor".
    `Dense_Method_Name` : *str*, optional
        - Identifier key used to store fitted dense radius and coefficient values in \
        `Drop_Obj.dense_radius_dict` and `Drop_Obj.fitting_coeff_dict`. Defaults to "ds_psf".

    Returns
    -------
    *str*
        - Formatted status string with fit results `(dense radius, reduced chi-square, \
        fitted coefficients, iterations)` or an error summary if fitting failed.

    Examples
    --------
    >>> _computeDenseRadiusDSPSF(drop, drop_data, drop_mask, x_grid, y_grid)
    '''

    dilute_radius = Drop_Obj.dilute_radius_dict.get(Dilute_Method_Name, 0)

    if Guess is None:
        Guess = [
            dilute_radius/2,
            numpy.min(Drop_Data),
            numpy.max(Drop_Data) / (dilute_radius),
            numpy.min(Drop_Data) / (dilute_radius),
            2   # characteristic width of 2px is the initial guess
        ]
    if Lower_Bounds is None:
        Lower_Bounds = [
            0,  # R >= 0
            0,  # bg >= 0
            0,  # A >= 0
            0,  # b >= 0
            0   # sigma >= 0, if sigma = 0 something went wrong
        ]
    if Upper_Bounds is None:
        Upper_Bounds = [
            dilute_radius,          # R <= r
            numpy.max(Drop_Data),   # bg <= max
            numpy.inf,              # A unbounded
            numpy.inf,              # B unbounded
            numpy.inf               # Sigma unbounded
        ]
    
    # before scipy.curveFit, we must use functools.partial to catch additional data
    # which cannot normally be passed through the standard 'xdata' parameter
    # we pre-link all required data to the function curveFit is iterating on, 
    # and pass a dummy xdata numpy.ndarray such that Scipy doesn't throw an error
    profile_with_data = Partial(_doubleSphereProfile, (X_Grid, Y_Grid, Drop_Mask, dilute_radius))
    dummy_xdata = numpy.zeros(Drop_Data.shape)

    try:
        optimal_parameters, _, info, _, _ = curveFit(
            profile_with_data,
            dummy_xdata,
            Drop_Data,
            p0 = Guess,
            method = 'trf',
            full_output = True,
            bounds = (Lower_Bounds, Upper_Bounds),
            nan_policy = 'omit',
        )
    except Exception as error:
        _setDenseRadiusNanDSPSF(Drop_Obj, Dense_Method_Name)
        return (
            f"\nDrop # {Drop_Obj.index} at ({Drop_Obj.x:.2f}, {Drop_Obj.y:.2f})"
            f"\tFailed... {error}"
        )
    
    dof = len(Drop_Data) - len(optimal_parameters) - 1
    chisq = _calculateReducedChisq(
        Drop_Data, 
        _doubleSphereProfile((X_Grid, Y_Grid, Drop_Mask, dilute_radius), dummy_xdata, *optimal_parameters), 
        dof
    )

    Drop_Obj.dense_radius_dict[Dense_Method_Name] =                     optimal_parameters[0]
    Drop_Obj.fitting_coeff_dict['background_' + Dense_Method_Name] =    optimal_parameters[1]
    Drop_Obj.fitting_coeff_dict['a_' + Dense_Method_Name] =             optimal_parameters[2]
    Drop_Obj.fitting_coeff_dict['b_' + Dense_Method_Name] =             optimal_parameters[3]
    Drop_Obj.fitting_coeff_dict['sigma_' + Dense_Method_Name] =         optimal_parameters[4]
    Drop_Obj.fitting_coeff_dict['chisq_' + Dense_Method_Name] =         chisq

    return (
        f"\n\tDrop #{Drop_Obj.index} at ({Drop_Obj.x:.2f}, {Drop_Obj.y:.2f}):\n"
        f"\t\tDilute Radius:  {dilute_radius:.2f}\n"
        f"\t\tDense Radius:   {optimal_parameters[0]:.2f}\n"
        f"\t\tChisq:          {chisq:.4f}\n"
        f"\t\tSigma:          {optimal_parameters[4]:.2f}\n"
        f"\t\tA:              {optimal_parameters[2]:.4f}\n"
        f"\t\tB:              {optimal_parameters[3]:.4f}\n"
        f"\t\tBackground:     {optimal_parameters[1]:.2f}\n"
        f"\n"
        f"\t\tInitial Guesses:\n"
        f"\t\tRden={Guess[0]:.2f}, BG={Guess[1]:.2f}, A={Guess[2]:.4f}, B={Guess[3]:.4f}, Sigma={Guess[4]:.2f}"
        f"\tCurve Fit Iterations: {info['nfev']}"
    )
# ---------------------------------------------------------------------------------------------------- #
#
#   DENSE RADIUS MODEL: PARALLELIZED DOUBLE SPHERE FUNCTION - PSF
#   "ds_psf"
#   *uses same name as other model because the math behind it is identical
#
# ---------------------------------------------------------------------------------------------------- #
def parallelComputeAllDenseRadiusDSPSF(
    Full_Dataset : DropImage,
    Max_Workers : int = 0,
    Min_Pixels : int = 25,
    Dilute_Method_Name : str = "nearest_neighbor",
    Dense_Method_Name : str = "ds_psf"
) -> None:
    '''
    # parallelComputeAllDenseRadiusDSPSF

    Computes the dense radius for each `Drop` in a `DropImage` by fitting a double sphere \
    function to the image data within its dilute radius, convolved with a normalized Gaussian to \
    account for the point spread function of a real-world microscope setup.

    Uses multiple CPU cores when available for parallelized bulk processing.

    Parameters
    ----------
    `Full_Dataset` : *DropImage*
        - Container holding the full image matrix and sequence of `Drop` objects to analyze.
    `Min_Pixels` : *int*, optional
        - Minimum pixel count required in the cropped drop region to attempt fitting. Defaults to \
        25. Drops below this threshold are assigned NaN.
    `Dilute_Method_Name` : *str*, optional
        - Key used to retrieve each Drop's previously computed dilute radius from \
        `dilute_radius_dict`. Defaults to "nearest_neighbor". As there is currently only one \
        dilute radius calculation method, it is recommended to keep this value as-is.
    `Dense_Method_Name` : *str*, optional
        - Identifier key for this analysis method. Defaults to "ds_psf".

    Returns
    -------
    *None*
        - No values are returned. Mutates Drop objects in place under \
        `Drop.dense_radius_dict[Dense_Method_Name]` and \
        `Drop.fitting_coeff_dict[<Parameter_Name> + Dense_Method_Name]` for all calculated values.

    Examples
    --------
    >>> parallelComputeAllDenseRadiusDSPSF(drop_image)
    '''

    # detect cpu cores for parallel processing
    cores_to_use = Max_Workers
    if cores_to_use < 1:
        total_cores = os.cpu_count()
        if total_cores is None:
            total_cores = 0
        cores_to_use = max(1, total_cores - 2)

    task_list = []

    # parallel processing loop
    with ProcessPoolExecutor(max_workers = cores_to_use) as dispatcher:
        # submit all tasks to process pool
        for drop in Full_Dataset.drops:
            dilute_radius = drop.dilute_radius_dict.get(Dilute_Method_Name, 0.0)

            drop_data, drop_mask, x_grid, y_grid = _cropDrop(
                Full_Dataset.image, 
                drop.x, 
                drop.y, 
                dilute_radius
            )

            if len(drop_data) < Min_Pixels:
                _setDenseRadiusNanDSPSF(drop, Dense_Method_Name)
                continue
            
            task = dispatcher.submit(
                _workerDSPSF,
                Drop_Index = drop.index,
                Dilute_Radius = dilute_radius,
                Drop_Data = drop_data,
                Drop_Mask = drop_mask,
                X_Grid = x_grid,
                Y_Grid = y_grid,
            )
            task_list.append((task, drop))
            
        # join all tasks and route data
        for task, drop in task_list:
            try:
                result = task.result()
            except (RuntimeError, ValueError):
                _setDenseRadiusNanDSPSF(drop, Dense_Method_Name)
                continue

            if not result[1]:
                _setDenseRadiusNanDSPSF(drop, Dense_Method_Name)
            else:
                drop.dense_radius_dict[Dense_Method_Name] =                     float(result[2][0])
                drop.fitting_coeff_dict['background_' + Dense_Method_Name] =    float(result[2][1])
                drop.fitting_coeff_dict['a_' + Dense_Method_Name] =             float(result[2][2])
                drop.fitting_coeff_dict['b_' + Dense_Method_Name] =             float(result[2][3])
                drop.fitting_coeff_dict['sigma_' + Dense_Method_Name] =         float(result[2][4])
                drop.fitting_coeff_dict['chisq_' + Dense_Method_Name] =         float(result[3])
# -------------------------------------------------- #
def _workerDSPSF(
    Drop_Index : int,
    Dilute_Radius : float,
    Drop_Data : numpy.ndarray[tuple[int], any], 
    Drop_Mask : numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
    X_Grid : numpy.ndarray,
    Y_Grid : numpy.ndarray,
) -> tuple[int, bool, list[float] | None, float | None]:
    '''
    # _workerDSPSF

    Prepares and executes a curve fit on a drop's intensity data from its original image. \
    Returns optimized parameters.

    Parameters
    ----------
    `Drop_Index` : *int*
        - Index of the Drop object within `DropImage.drops`.
    `Dilute_Radius` : *float*
        - Precomputed dilute radius threshold used to apply bounds and provide guesses.
    `Drop_Data` : *numpy.ndarray[tuple[int], any],*
        - A 1D flattened array of masked pixel intensity values within the drop's dilute radius.
    `Drop_Mask` : *numpy.ndarray[tuple[int, int], numpy.dtype[bool]]*
        - A 2D boolean matrix describing the original shape of `Drop_Data` before flattening.
    `X_Grid` : *numpy.ndarray*
        - A 2D meshgrid of x-coordinates centered on the drop.
    `Y_Grid` : *numpy.ndarray*
        - A 2D meshgrid of y-coordinates centered on the drop.

    Returns
    -------
    *tuple[int, bool, list[float] | None, float | None]*
        - A tuple `(drop_index, success, optimal_parameters, chisq)`:
        - `drop_index` (*int*): Identifier index of the processed drop.
        - `success` (*bool*): True if curve fitting converged, False if an exception occurred.
        - `optimal_parameters` (*list[float] | None*): Fitted coefficients \
        `[r_dense, background, A, B, sigma]` if successful, otherwise None.
        - `chisq` (*float | None*): Reduced chi-squared value of the fit if successful, \
        otherwise None.

    Examples
    --------
    >>> _workerDSPSF(drop_index, dilute_radius, drop_data, drop_mask, x_grid, y_grid)
    '''
    
    # [Dense Radius, Background, A, B, Sigma]
    guess = [
        Dilute_Radius / 2.0,
        numpy.min(Drop_Data),
        numpy.max(Drop_Data) / Dilute_Radius,
        numpy.min(Drop_Data) / Dilute_Radius,
        1.0
    ]

    lower_bounds = [0.0, 0.0, 0.0, 0.0, 0.0]
    upper_bounds = [Dilute_Radius, numpy.max(Drop_Data), numpy.inf, numpy.inf, numpy.inf]
    
    profileWithData = Partial(_doubleSphereProfile, (X_Grid, Y_Grid, Drop_Mask, Dilute_Radius))
    dummy_xdata = numpy.zeros(Drop_Data.shape)
    
    try:
        optimal_parameters, _ = curveFit(
            profileWithData,
            dummy_xdata,
            Drop_Data,
            p0 = guess,
            method = 'trf',
            bounds = (lower_bounds, upper_bounds),
            nan_policy = 'omit',
        )
    except (ValueError, RuntimeError, OptimizeWarning):
        return (Drop_Index, False, None, None)

        
    # calculate chi squared
    dof = len(Drop_Data) - len(optimal_parameters) - 1
    fitted_profile = _doubleSphereProfile((X_Grid, Y_Grid, Drop_Mask, Dilute_Radius), dummy_xdata, *optimal_parameters)
    chisq = _calculateReducedChisq(Drop_Data, fitted_profile, dof)
    
    return (Drop_Index, True, optimal_parameters, chisq)
# -------------------------------------------------- #
def _setDenseRadiusNanDSPSF(
    Drop_Obj : Drop,
    Dense_Method_Name : str
) -> None:
    '''
    # _setDenseRadiusNanDSPSF

    Sets the dense radius and all associated fitting coefficients for a drop to NaN.

    Parameters
    ----------
    `Drop_Obj` : *Drop*
        - The `Drop` object to be assigned NaN values.
    `Dense_Method_Name` : *str*
        - Identifier key for this analysis method used to index `dense_radius_dict` and prefix \
        coefficient entries in `fitting_coeff_dict`.

    Returns
    -------
    *None*
        - No values are returned. Mutates `Drop_Obj` in place, setting \
        `Drop_Obj.dense_radius_dict[Dense_Method_Name]` and related coefficients to \
        `numpy.nan`.

    Examples
    --------
    >>> _setDenseRadiusNanDSPSF(drop, "ds_psf")
    '''

    Drop_Obj.dense_radius_dict[Dense_Method_Name] =                     numpy.nan
    Drop_Obj.fitting_coeff_dict['background_' + Dense_Method_Name] =    numpy.nan
    Drop_Obj.fitting_coeff_dict['a_' + Dense_Method_Name] =             numpy.nan
    Drop_Obj.fitting_coeff_dict['b_' + Dense_Method_Name] =             numpy.nan
    Drop_Obj.fitting_coeff_dict['sigma_' + Dense_Method_Name] =         numpy.nan
    Drop_Obj.fitting_coeff_dict['chisq_' + Dense_Method_Name] =         numpy.nan
# ---------------------------------------------------------------------------------------------------- #
#
#   DENSE RADIUS MODEL: PARALLELIZED SPHERE ELIPSE FUNCTION - PSF
#   "se_psf"
#
# ---------------------------------------------------------------------------------------------------- #
def parallelComputeAllDenseRadiusSEPSF(
    Full_Dataset : DropImage,
    Aspect_Ratio : float,
    Min_Pixels : int = 25,
    Dilute_Method_Name : str = "nearest_neighbor",
    Dense_Method_Name : str = "se_psf"
) -> None:
    '''
    # parallelComputeAllDenseRadiusSEPSF

    Computes the dense radius for each Drop in a DropImage by fitting a sphere \
    within ellipse function to the image data contained by its dilute radius, convolved with a \
    normalized Gaussian to account for the point spread function of a real-world microscope setup.

    Uses multiple CPU cores when available for parallelized bulk processing.

    Parameters
    ----------
    `Full_Dataset` : *DropImage*
        - Container holding the full image matrix and sequence of Drop objects to analyze.
    `Aspect_Ratio` : *float*
        - The ratio of height to width of the ellipse as it compresses or stretches under gravity.
    `Min_Pixels` : *int*, optional
        - Minimum pixel count required in the cropped drop region to attempt fitting. Defaults to \
        25. Drops below this threshold are assigned NaN.
    `Dilute_Method_Name` : *str*, optional
        - Key used to retrieve each Drop's previously computed dilute radius from \
        `dilute_radius_dict`. Defaults to "nearest_neighbor". As there is currently only one \
        dilute radius calculation method, it is recommended to keep this value as-is.
    `Dense_Method_Name` : *str*, optional
        - Identifier key for this analysis method. Defaults to "se_psf".

    Returns
    -------
    *None*
        - No values are returned. Mutates Drop objects in place under \
        `Drop.dense_radius_dict[Dense_Method_Name]` and \
        `Drop.fitting_coeff_dict[f"{param}_{Dense_Method_Name}"]` for all calculated values.

    Examples
    --------
    >>> parallelComputeAllDenseRadiusSEPSF(drop_image, 0.75)
    '''

    total_cores = os.cpu_count()
    if total_cores is None:
        total_cores = 0
    cores_to_use = max(1, total_cores - 2)
    task_list = []

    with ProcessPoolExecutor(max_workers = cores_to_use) as dispatcher:
        for drop in Full_Dataset.drops:
            dilute_radius = drop.dilute_radius_dict.get(Dilute_Method_Name, 0.0)
            drop_data, drop_mask, x_grid, y_grid = _cropDrop(
                Full_Dataset.image,
                drop.x,
                drop.y,
                dilute_radius
            )
            if len(drop_data) < Min_Pixels:
                _setDenseRadiusNanSEPSF(drop, Dense_Method_Name)
                continue

            task = dispatcher.submit(
                _workerSEPSF,
                Drop_Index = drop.index,
                Dilute_Radius = dilute_radius,
                Aspect_Ratio = Aspect_Ratio,
                Drop_Data = drop_data,
                Drop_Mask = drop_mask,
                X_Grid = x_grid,
                Y_Grid = y_grid,
            )
            task_list.append(task)

        for task, drop in task_list:
            try:
                result = task.result()
            except (RuntimeError, ValueError):
                _setDenseRadiusNanSEPSF(drop, Dense_Method_Name)
                continue

            if not result[1]:
                _setDenseRadiusNanSEPSF(drop, Dense_Method_Name)
            else:
                drop.dense_radius_dict[Dense_Method_Name] =                     float(result[2][0])
                drop.fitting_coeff_dict['background_' + Dense_Method_Name] =    float(result[2][1])
                drop.fitting_coeff_dict['a_' + Dense_Method_Name] =             float(result[2][2])
                drop.fitting_coeff_dict['b_' + Dense_Method_Name] =             float(result[2][3])
                drop.fitting_coeff_dict['sigma_' + Dense_Method_Name] =         float(result[2][4])
                drop.fitting_coeff_dict['scale_factor_' + Dense_Method_Name] =  Aspect_Ratio
                drop.fitting_coeff_dict['chisq_' + Dense_Method_Name] =         float(result[3])
# -------------------------------------------------- #
def _workerSEPSF(
    Drop_Index : int,
    Dilute_Radius : float,
    Aspect_Ratio : float,
    Drop_Data : numpy.ndarray[tuple[int], any],
    Drop_Mask : numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
    X_Grid : numpy.ndarray,
    Y_Grid : numpy.ndarray,
) -> tuple[int, bool, list[float] | None, float | None]:
    '''
    # _workerSEPSF

    Prepares and executes a curve fit using a sphere-within-ellipse model on a drop's intensity \
    data from its original image. Returns optimized parameters.

    Parameters
    ----------
    `Drop_Index` : *int*
        - Index of the Drop object within `DropImage.drops`.
    `Dilute_Radius` : *float*
        - Precomputed dilute radius threshold used to apply bounds and provide guesses.
    `Aspect_Ratio` : *float*
        - The ratio of height to width of the ellipse as it compresses or stretches under gravity.
    `Drop_Data` : *numpy.ndarray[tuple[int], any]*
        - A 1D flattened array of masked pixel intensity values within the drop's dilute radius.
    `Drop_Mask` : *numpy.ndarray[tuple[int, int], numpy.dtype[bool]]*
        - A 2D boolean matrix describing the original shape of `Drop_Data` before flattening.
    `X_Grid` : *numpy.ndarray*
        - A 2D meshgrid of x-coordinates centered on the drop.
    `Y_Grid` : *numpy.ndarray*
        - A 2D meshgrid of y-coordinates centered on the drop.

    Returns
    -------
    *tuple[int, bool, list[float] | None, float | None]*
        - A tuple `(drop_index, success, optimal_parameters, chisq)`:
        - `drop_index` (*int*): Identifier index of the processed drop.
        - `success` (*bool*): True if curve fitting converged, False if an exception occurred.
        - `optimal_parameters` (*list[float] | None*): Fitted coefficients \
        `[r_dense, background, A, B, sigma]` if successful, otherwise None.
        - `chisq` (*float | None*): Reduced chi-squared value of the fit if successful, \
        otherwise None.

    Examples
    --------
    >>> _workerSEPSF(drop_index, dilute_radius, aspect_ratio, drop_data, drop_mask, x_grid, y_grid)
    '''

    # [Dense Radius, Background, A, B, Sigma]
    guess = [
        Dilute_Radius / 2.0,
        numpy.min(Drop_Data),
        numpy.max(Drop_Data) / Dilute_Radius,
        numpy.min(Drop_Data) / Dilute_Radius,
        1.0
    ]
    lower_bounds = [0.0, 0.0, 0.0, 0.0, 0.0]
    upper_bounds = [Dilute_Radius, numpy.max(Drop_Data), numpy.inf, numpy.inf, numpy.inf]

    profileWithData = Partial(_sphereEllipseProfile, (X_Grid, Y_Grid, Drop_Mask, Dilute_Radius, Aspect_Ratio))
    dummy_xdata = numpy.zeros(Drop_Data.shape)

    try:
        optimal_parameters, _ = curveFit(
            profileWithData,
            dummy_xdata,
            Drop_Data,
            p0 = guess,
            method = 'trf',
            bounds = (lower_bounds, upper_bounds),
            nan_policy = 'omit',
        )
    except (ValueError, RuntimeError, OptimizeWarning):
        return (Drop_Index, False, None, None)

    dof = len(Drop_Data) - len(optimal_parameters) - 1
    fitted_profile = _sphereEllipseProfile((X_Grid, Y_Grid, Drop_Mask, Dilute_Radius, Aspect_Ratio), dummy_xdata, *optimal_parameters)
    chisq = _calculateReducedChisq(Drop_Data, fitted_profile, dof)

    return (Drop_Index, True, optimal_parameters, chisq)
# -------------------------------------------------- #
def _setDenseRadiusNanSEPSF(
    Drop_Obj : Drop,
    Dense_Method_Name : str
) -> None:
    '''
    # _setDenseRadiusNanSEPSF

    Sets the dense radius and all associated fitting coefficients for a drop to NaN. Since the \
    sphere-ellipse pipeline is a modification of the double-sphere pipeline, it shares all \
    fitting coefficients, with the addition of a scale factor.

    Parameters
    ----------
    `Drop_Obj` : *Drop*
        - The `Drop` object to be assigned NaN values.
    `Dense_Method_Name` : *str*
        - Identifier key for this analysis method used to index `dense_radius_dict` and prefix \
        coefficient entries in `fitting_coeff_dict`.

    Returns
    -------
    *None*
        - No values are returned. Mutates `Drop_Obj` in place, setting \
        `Drop_Obj.dense_radius_dict[Dense_Method_Name]` and related coefficients to \
        `numpy.nan`.

    Examples
    --------
    >>> _setDenseRadiusNanSEPSF(drop, "se_psf")
    '''
    _setDenseRadiusNanDSPSF(Drop_Obj, Dense_Method_Name)
    Drop_Obj.fitting_coeff_dict['scale_factor_' + Dense_Method_Name] =  numpy.nan
# ---------------------------------------------------------------------------------------------------- #
#
#   INTENSITY PROFILE MODELS
#
# ---------------------------------------------------------------------------------------------------- #
def _doubleSphereProfile(
    Data : tuple[
        numpy.ndarray, 
        numpy.ndarray,
        numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
        float
    ],
    Scipy_Dummy : numpy.ndarray,
    Dense_Radius : float,
    Background : float,
    A : float,
    B : float,
    Sigma : float
) -> numpy.ndarray:
    '''
    # _doubleSphereProfile

    Computes the intensity manifold of a sphere-in-sphere (double sphere) emulsion convolved with \
    a normalized Gaussian, returned as a flattened 1D array.

    Parameters
    ----------
    `Data` : *tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, float]*
        - Tuple of `(x_grid, y_grid, drop_mask, dilute_radius)`
        - `x_grid` and `y_grid` are meshgrids for the cropped drop region.
        - `drop_mask` is a 2D matrix of booleans describing the drop's original shape.
        - `dilute_radius` is the outer bound of the cropped drop region used in the double-sphere \
        equation.
    `Scipy_Dummy` : *numpy.ndarray*
        - Dummy array to satisfy scipy's xdata requirement, despite not being required.
    `Dense_Radius` : *float*
        - The first fitted parameter, radius of the dense phase region of a droplet.
    `Background` : *float*
        - The second fitted parameter, background image intensity. Acts as an added constant \
        post-convolution.
    `A` : *float*
        - Intensity scaling factor for the dense phase excluding the scaling factor for the \
        dilute phase.
    `B` : *float*
        - Intensity scaling factor for the dilute phase.
    `Sigma` : *float*
        - Gaussian blur characteristic width, corresponding to the point-spread-function of a \
        real-world microscope.

    Returns
    -------
    *numpy.ndarray*
        - 1D array of modeled intensity values at each valid pixel.

    Examples
    --------
    >>> _doubleSphereProfile(data, dummy_xdata, 5.0, 500.0, 100.0, 1.0, 1.5)
    '''
    # scipy.curve_fit typically requires the first parameter to be X axis data, and the second parameter to be Y axis data
    # To bypass this, we merge coordinate data into a single tuple, and intensity data into another tuple.
    x_grid, y_grid, shape, dilute_radius = Data

    # --- Piecewise Double Sphere Function --- #
    # This section of the piecewise double sphere function applies to the dense phase only
    piecewise_ds_function = 2 * A * numpy.sqrt(numpy.maximum(0, Dense_Radius**2 - x_grid**2 - y_grid**2))
    # This section of the piecewise double sphere function applies to the dilute phase
    piecewise_ds_function += 2 * B * numpy.sqrt(numpy.maximum(0, dilute_radius**2 - x_grid**2 - y_grid**2))
    
    # Convolve data to PSF (gaussian blur)
    convolved_to_psf = gaussianFilter(piecewise_ds_function, sigma = Sigma)
    masked_fit = convolved_to_psf[shape] + Background
    return masked_fit
# -------------------------------------------------- #
def _sphereEllipseProfile(
    Data : tuple[
        numpy.ndarray, 
        numpy.ndarray,
        numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
        float,
        float
    ],
    Scipy_Dummy : numpy.ndarray,
    Dense_Radius : float,
    Background : float,
    A : float,
    B : float,
    Sigma : float
) -> numpy.ndarray:
    '''
    # _sphereEllipseProfile

    Computes the intensity manifold of an ellipse-in-sphere emulsion convolved with a normalized \
    Gaussian, returned as a flattened 1D array. Because `A` and `scale_factor` are directly \
    multiplied, they are mathematically degenerate. When curve fitting a sphere-ellipse profile, \
    `A` will always artificially inflate or deflate its value to yield a double-sphere manifold \
    inversely proportional to `scale_factor`. Still, something could happen!

    Parameters
    ----------
    `Data` : *tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, float, float]*
        - Tuple of `(x_grid, y_grid, drop_mask, dilute_radius, scale_factor)`
        - `x_grid` and `y_grid` are meshgrids for the cropped drop region.
        - `drop_mask` is a 2D matrix of booleans describing the drop's original shape.
        - `dilute_radius` is the outer bound of the cropped drop region used in the double-sphere \
        equation.
        - `scale_factor` represents the compression or expansion of the elliptical dense region \
        within the overall spherical emulsion.
    `Scipy_Dummy` : *numpy.ndarray*
        - Dummy array to satisfy scipy's xdata requirement, despite not being required.
    `Dense_Radius` : *float*
        - The first fitted parameter, radius of the dense phase region of a droplet.
    `Background` : *float*
        - The second fitted parameter, background image intensity. Acts as an added constant \
        post-convolution.
    `A` : *float*
        - Intensity scaling factor for the dense phase excluding the scaling factor for the \
        dilute phase. Inversely proportional to `scale_factor` relative to a double-sphere \
        profile when curve fit.
    `B` : *float*
        - Intensity scaling factor for the dilute phase.
    `Sigma` : *float*
        - Gaussian blur characteristic width, corresponding to the point-spread-function of a \
        real-world microscope.

    Returns
    -------
    *numpy.ndarray*
        - 1D array of modeled intensity values at each valid pixel.

    Examples
    --------
    >>> _sphereEllipseProfile(data, dummy_xdata, 5.0, 500.0, 100.0, 1.0, 1.5)
    '''
    # scipy.curve_fit typically requires the first parameter to be X axis data, and the second parameter to be Y axis data
    # To bypass this, we merge coordinate data into a single tuple, and intensity data into another tuple.
    x_grid, y_grid, shape, dilute_radius, scale_factor = Data

    # --- Piecewise Sphere Ellipse Function --- #
    # This section of the piecewise sphere ellipse function applies to the dense phase only
    piecewise_ds_function = 2 * A * scale_factor * numpy.sqrt(numpy.maximum(0, Dense_Radius**2 - x_grid**2 - y_grid**2))
    # This section of the piecewise sphere ellipse function applies to the dilute phase
    piecewise_ds_function += 2 * B * numpy.sqrt(numpy.maximum(0, dilute_radius**2 - x_grid**2 - y_grid**2))
    
    # Convolve data to PSF (gaussian blur)
    convolved_to_psf = gaussianFilter(piecewise_ds_function, sigma = Sigma)
    masked_fit = convolved_to_psf[shape] + Background
    return masked_fit
# ---------------------------------------------------------------------------------------------------- #
#
#   POINT SPREAD FUNCTION MODELS
#
# ---------------------------------------------------------------------------------------------------- #
def _buildMatrixPSF(Sigma : float, Matrix_Width : int = None) -> numpy.ndarray:
    '''
    # _buildMatrixPSF

    [Deprecated]

    Builds a normalized 2D Gaussian PSF Matrix with the following specifications:
        - Peak Value === 1
        - Sum === 1

    Parameters
    ----------
    `Sigma` : *float*
        - Gaussian distribution characteristic width in pixels. Must be > 0
    `Matrix_Width` : *int*, optional
        - Half-width of the PSF matrix in Pixels. 
        - If None, defaults to math.ceil(4*sigma) so the PSF captures > 99.99% of the Gaussian.
        Larger values are more accurate, but slower.

    Returns
    -------
    *numpy.ndarray*
        - 2D matrix of shape `((2 * Matrix_Width) + 1, (2 * Matrix_Width) + 1)` normalized by its \
        sum so the peak intensity value is conserved, but blurry interfaces are resolved.

    Examples
    --------
    >>> _buildMatrixPSF(1.5)
    >>> _buildMatrixPSF(2.0, Matrix_Width = 10)
    '''
    if Sigma <= 0:
        raise ValueError(f"Expected Sigma > 0. Actual: {Sigma}")
    if Matrix_Width is None:
        Matrix_Width = int(math.ceil(4.0*Sigma))

    # Build Coordinate Grid centered at (0,0)
    single_axis = numpy.arange(-Matrix_Width, Matrix_Width + 1, dtype = float)
    all_x, all_y = numpy.meshgrid(single_axis, single_axis)

    # Gaussian distribution with peak = 1 at (0,0)
    peak_normalized_psf = numpy.exp(
        -((all_x ** 2) + (all_y ** 2)) / (2.0 * (Sigma ** 2))
    )

    # Normalize by sum so convolution conserves total intensity
    matrix_sum = numpy.sum(peak_normalized_psf)
    
    return peak_normalized_psf / matrix_sum
# ---------------------------------------------------------------------------------------------------- #
#
#   MISC UTILITY
#
# ---------------------------------------------------------------------------------------------------- #
def _calculateReducedChisq(Observed : numpy.ndarray, Expected : numpy.ndarray, Dof : int) -> float:
    '''
    # _calculateReducedChisq

    Calculates the reduced chi-square between observed and expected 1D or 2D arrays and matrices. 

    Parameters
    ----------
    `Observed` : *numpy.ndarray*
        - 1D or 2D array of raw intensity values.
    `Expected` : *numpy.ndarray*
        - 1D or 2D array of fitted data, matching the shape of `Observed`.
    `Dof` : *int*
        - Degrees of freedom. Must be > 0.

    Returns
    -------
    *float*
        - Reduced chi-square value.

    Examples
    --------
    >>> _calculateReducedChisq(measured_profile, fit_profile, 42)
    '''
    chisq = numpy.sum(
        numpy.where(
            Expected != 0, 
            numpy.square(Observed - Expected) / Expected, 
            0.0
        )
    )
    return chisq / Dof
# -------------------------------------------------- #
def _cropDrop(
    Full_Image : numpy.ndarray, 
    X_Center : float, 
    Y_Center : float, 
    Dilute_Radius : float
) -> (
    tuple[
        numpy.ndarray[tuple[int], numpy.dtype[float]],
        numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
        numpy.ndarray[tuple[int, int], numpy.dtype[int]],
        numpy.ndarray[tuple[int, int], numpy.dtype[int]]
    ]
):
    '''
    # _cropDrop

    Crops a square bounding box centered on a droplet, generates centered coordinate meshgrids, \
    and returns only the masked pixel intensity data within the droplet's circular dilute boundary.

    Parameters
    ----------
    `Full_Image` : *numpy.ndarray*
        - 2D grayscale image matrix containing all drops.
    `X_Center` : *float*
        - Horizontal pixel coordinate of the droplet center.
    `Y_Center` : *float*
        - Vertical pixel coordinate of the droplet center.
    `Dilute_Radius` : *float*
        - Radius of the outer dilute phase boundary in pixels. Defines the bounding \
        box half-width and circular boundary for masking.

    Returns
    -------
    *tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]*
        - Tuple containing `(drop_data, drop_mask, x_grid, y_grid)`
            - `drop_data` : 1D array of flattened raw intensity values strictly inside the circular mask.
            - `drop_mask` : 2D boolean mask of shape `(2*R, 2*R)` identifying valid droplet pixels.
            - `x_grid` : 2D meshgrid of horizontal coordinates centered at `(0, 0)`.
            - `y_grid` : 2D meshgrid of vertical coordinates centered at `(0, 0)`.
        - Returns four dummy arrays if the bounding box goes out of range of the image.

    Examples
    --------
    >>> drop_data, mask, x_grid, y_grid = _cropDrop(frame, 512.4, 480.1, 45.0)
    '''

    left_edge = int(X_Center - Dilute_Radius)
    right_edge = int(X_Center + Dilute_Radius)
    bottom_edge = int(Y_Center - Dilute_Radius)
    top_edge = int(Y_Center + Dilute_Radius)

    if (
        top_edge > Full_Image.shape[0] or
        bottom_edge < 0 or
        right_edge > Full_Image.shape[1] or
        left_edge < 0
    ):
        return numpy.array([0]), numpy.array([0]), numpy.array([0]), numpy.array([0])
    
    drop_image = Full_Image[bottom_edge:top_edge, left_edge:right_edge]

    x_axis = numpy.arange(left_edge, right_edge) - X_Center
    y_axis = numpy.arange(bottom_edge, top_edge) - Y_Center
    x_grid, y_grid = numpy.meshgrid(x_axis, y_axis)

    pixel_distances = _distance((x_grid, y_grid), (0,0))
    drop_mask = pixel_distances <= (Dilute_Radius - 1)

    drop_data = drop_image[drop_mask]

    return drop_data, drop_mask, x_grid, y_grid
# -------------------------------------------------- #
def _distance(
    Point_A : tuple[float | numpy.ndarray, float | numpy.ndarray], 
    Point_B : tuple[float | numpy.ndarray, float | numpy.ndarray]
) -> float | numpy.ndarray:
    '''
    # _distance

    If you need a docstring to understand this function, please review the following \
    [documentation](https://en.wikipedia.org/wiki/Euclidean_geometry) for guidance and moral \
    support. I truly believe in you!

    A brief overview of functionality has been provided below for when you return.

    Parameters
    ----------
    `Point_A` : *tuple[float | numpy.ndarray, float | numpy.ndarray]*
        - An (x, y) coordinate pair, or tuple of coordinate meshgrids.
    `Point_B` : *tuple[float | numpy.ndarray, float | numpy.ndarray]*
        - An (x, y) coordinate pair, or tuple of coordinate meshgrids.

    Returns
    -------
    *float* | *numpy.ndarray*
        - The distance between Point_A and Point_B

    Examples
    --------
    >>> _distance((0.0, 4.0), (3.0, 0.0))
    5.0
    '''
    return numpy.hypot(Point_A[0] - Point_B[0], Point_A[1] - Point_B[1])
# -------------------------------------------------- #
def _reconstructMaskedMatrix(
        Flattened_Array : numpy.ndarray[tuple[int], any], 
        Shape_Mask : numpy.ndarray[tuple[int, int], numpy.dtype[bool]],
        Replacement_Values : any = 0
    ) -> numpy.ndarray:
    '''
    # _reconstructMaskedMatrix

    [Unmaintained]

    Reconstructs an array of flattened values into a 2D matrix into the shape of a boolean mask.

    Parameters
    ----------
    `Flattened_Array` : *numpy.ndarray[tuple[int], any]*
        - A 1D array of values
    `Shape_Mask` : *numpy.ndarray[tuple[int, int], numpy.dtype[bool]]*
        - A 2D matrix of boolean values describing the shape `Flattened_Array` should arrange \
        into.
    `Replacement_Values` : *any*, optional
        - Fill value assigned to excluded coordinates in the mask matrix. Defaults to 0.

    Returns
    -------
    *numpy.ndarray*
        - A 2D matrix of shape `Shape_Mask` containing `Flattened_Array` values where \
        `Shape_Mask` is `True` and `Replacement_Values` elsewhere.

    Examples
    --------
    >>> _reconstructMaskedMatrix(
    ...     numpy.array([1, 2]), 
    ...     numpy.array([[True, False], [False, True]]), 
    ...     Replacement_Values = 0
    ... )
    '''

    slots = numpy.count_nonzero(Shape_Mask)
    value_count = Flattened_Array.size
    
    if value_count != slots:
        raise ValueError(f"Unable to reconstruct masked matrix. {value_count} values to fill {slots} indices.")
    
    reconstructed_matrix = numpy.full(Shape_Mask.shape, Replacement_Values)
    reconstructed_matrix[Shape_Mask] = Flattened_Array

    return reconstructed_matrix
# -------------------------------------------------- #
def pixelToMicron(Pixels : int | float, Pixels_Per_Micron = 0.65) -> float:
    '''
    the microscope we use has 0.65 pixels per micron on a 4x objective. yours probably doesn't. \
    regardless, this function is not used in the full release of bcds-engine. it's just a helpful \
    utility for debugging. all our calculations until the end of the pipeline are in pixels, \
    non-index based units are scary.
    '''
    return Pixels / Pixels_Per_Micron
# -------------------------------------------------- #
def micronToPixel(Microns : int | float, Pixels_Per_Micron = 0.65) -> float:
    return Microns * Pixels_Per_Micron
# ---------------------------------------------------------------------------------------------------- #