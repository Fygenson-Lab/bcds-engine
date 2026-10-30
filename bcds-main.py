# ---------------------------------------------------------------------------------------------------- #
#
#   ▄▄▄▄   ▄▄▄▄ ▄▄▄▄   ▄▄▄▄     ▄▄   ▄▄  ▄▄▄  ▄▄ ▄▄  ▄▄   ▄▄▄▄  ▄▄ ▄▄ 
#   ██▄██ ██▀▀▀ ██▀██ ███▄▄ ▄▄▄ ██▀▄▀██ ██▀██ ██ ███▄██   ██▄█▀ ▀███▀ 
#   ██▄█▀ ▀████ ████▀ ▄▄██▀     ██   ██ ██▀██ ██ ██ ▀██ ▄ ██      █  
#
# ---------------------------------------------------------------------------------------------------- #
#
#   --------------------------------------------------------------------------------------
#   Development History & Contacts  |    (Reverse Chronological)
#   --------------------------------|----------------------------------------------------
#   Principal Investigator          |    Deborah Fygenson
#   Project Guidance                |    Thomas Reese
#   Complete Architecture Overhaul  |    Tyler Frischknecht
#   Legacy Versions & Revisions     |    Tyler Frischknecht, Thomas Reese, Nicholas Phelps
#   Initial Pipeline                |    Thomas Reese, Nicholas Phelps
#   --------------------------------------------------------------------------------------
#   Last Updated: 9/23/2026 - Ready for full release!
#
# ---------------------------------------------------------------------------------------------------- #
import cv2
import numpy
import os
import pandas
import traceback
#
from datetime import datetime as Datetime
#
from fygenlib import *
# ---------------------------------------------------------------------------------------------------- #
def printAverages(
    Drop_Image : DropImage,
    Dilute_Method : str,
    Dense_Method : str
) -> None:
    
    # dilute Radii
    array_data = numpy.array([drop.dilute_radius_dict.get(Dilute_Method, numpy.nan) for drop in Drop_Image.drops])
    dilute_radii_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # dense Radii
    array_data = numpy.array([drop.dense_radius_dict.get(Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    dense_radii_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # a
    array_data = numpy.array([drop.fitting_coeff_dict.get("a_"+Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    a_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # b
    array_data = numpy.array([drop.fitting_coeff_dict.get("b_"+Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    b_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # background
    array_data = numpy.array([drop.fitting_coeff_dict.get("background_"+Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    bg_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # sigma (psf width)
    array_data = numpy.array([drop.fitting_coeff_dict.get("sigma_"+Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    sigma_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    # reduced chisq
    array_data = numpy.array([drop.fitting_coeff_dict.get("chisq_"+Dense_Method, numpy.nan) for drop in Drop_Image.drops])
    chisq_mean = numpy.nanmean(array_data) if array_data.size > 0 and not numpy.isnan(array_data).all() else numpy.nan

    print(
        f"\nAverage data across frame (Does not filter outliers)\n"
        f"\t Dilute Radii: {dilute_radii_mean:.3f} px\n"
        f"\t  Dense Radii: {dense_radii_mean:.3f} px\n"
        f"\t            A: {a_mean:.3f}\n"
        f"\t            B: {b_mean:.3f}\n"
        f"\t   Background: {bg_mean:.3f}\n"
        f"\t    PSF Width: {sigma_mean:.3f} px\n"
        f"\tReduced Chisq: {chisq_mean:.3f}\n"
    )
# -------------------------------------------------- #
def populateDropImage(
    Drop_Image : DropImage, 
    Feature_Table : pandas.DataFrame, 
    X_Label = "Center of the object_0", 
    Y_Label = "Center of the object_1"
) -> None:
    
    for x, y in zip(Feature_Table[X_Label], Feature_Table[Y_Label]):
        Drop_Image.addDrop(Drop(x, y))
# -------------------------------------------------- #
def writeMeta(Path : os.PathLike | str, Message : str, Timestamp : bool = True) -> None:
    print(Message)
    if Timestamp:
        Message = f"[{Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\t{Message}\n"
    else:
        Message += '\n'
    try:
        with open (Path, 'a', encoding = 'utf-8') as meta_log:
            meta_log.write(Message)
    except OSError as error:
        print(f"Failed to write metadata to {Path}: {error}")
# -------------------------------------------------- #
def setup() -> tuple[bool, list[os.PathLike | str]]:
    suppressWarnings()

    program_paths = getProgramPaths()
    setup_gui = GuiSetup()
    setup_gui.program_paths = program_paths
    setup_gui.mainloop()
    return setup_gui.run_analysis, setup_gui.valid_directories
# -------------------------------------------------- #
def suppressWarnings() -> None:
    try:
        if hasattr(cv2, 'utils') and hasattr(cv2.utils, 'logging'):
            level = getattr(cv2.utils.logging, 'LOG_LEVEL_ERROR', 2)
            cv2.utils.logging.setLogLevel(level)
        elif hasattr(cv2, 'setLogLevel'):
            cv2.setLogLevel(2)
    except Exception:
        print("Unable to suppress OpenCV warnings.")
    numpy.seterr(invalid = 'ignore', divide = 'ignore')
# -------------------------------------------------- #
def getFilteredFilePaths(Target : os.PathLike | str) -> list[os.PathLike | str]:
    files_all_paths = sorted([
        os.path.join(Target, filename) 
        for filename in os.listdir(Target)
    ])
    filtered_files_all_paths = []
    for path in files_all_paths:
        if ( # filter out apple metadata files
            not os.path.basename(path) == '.DS_Store' and
            not os.path.basename(path).startswith('._')
        ):
            filtered_files_all_paths.append(path)
    return filtered_files_all_paths
# ---------------------------------------------------------------------------------------------------- #
def main() -> None:
    run_analysis, analysis_directories_and_settings = setup()
    if not run_analysis:
        return

    for directory, settings in analysis_directories_and_settings:
        paths = getProjectPaths(directory)
        meta_log_path = os.path.join(paths['meta_logs'], 'meta_log_bcds.txt')

        writeMeta(meta_log_path, "-" * 100, Timestamp = False)
        writeMeta(
            meta_log_path,
            f"Starting analysis...",
        )

        filtered_all_frame_paths = getFilteredFilePaths(paths['movie_frames'])
        filtered_all_table_paths = getFilteredFilePaths(paths['feature_tables'])

        if len(filtered_all_frame_paths) != len(filtered_all_table_paths):
            writeMeta(
                meta_log_path,
                f"Skipping full directory. "
                f"Found {len(filtered_all_frame_paths)} and {len(filtered_all_table_paths)} feature tables."
            )
            continue

        # record keeping for meta_log
        successful_images = 0
        total_images = len(filtered_all_frame_paths)

        # run analysis
        for frame_index in range(settings.start_frame, settings.end_frame+1):
            this_frame_success = 1
            applied_dense_methods = []

            if frame_index in settings.skipped_frames or frame_index > total_images:
                writeMeta(
                    meta_log_path,
                    f"Skipping frame {frame_index}/{total_images}"
                )
                continue

            frame_path = filtered_all_frame_paths[frame_index]
            feature_table_path = filtered_all_table_paths[frame_index]
            
            # cv2 wants to handle image as 8-bit, force it to remain whatever it was before.
            try:
                raw_image = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH)
                if raw_image is None:
                    raise RuntimeError(
                        f"OpenCV unable to open image, or image contains no data at path: {frame_path}"
                    )
                opencv_bit_depth = raw_image.itemsize * 8
                if opencv_bit_depth < settings.bit_depth:
                    raise RuntimeError(
                        "OpenCV unable to read image in valid bit depth. "
                        f"opencv_bit_depth = {opencv_bit_depth}, expected_bit_depth = {settings.bit_depth}"
                    )
                Drop_Image = DropImage(raw_image, Bit_Depth = settings.bit_depth)
                feature_Table = pandas.read_csv(feature_table_path)
            except RuntimeError as error:
                writeMeta(
                    meta_log_path,
                    f"\tError processing {os.path.basename(frame_path)}: {error}",
                )
                continue
            
            print('+ '+'-'*96+' +')
            print(f"Processing {os.path.basename(frame_path)}")

            populateDropImage(Drop_Image, feature_Table)

            try:
                print("Calculating dilute radii...")
                if settings.use_nearest_neighbor:
                    computeAllDiluteRadiusNN(Drop_Image, Min_Radius = 10)
                    print("\tCalculated dilute radii with nearest-neighbor model")
            except Exception as error:
                error_traceback = traceback.format_exc()
                writeMeta(
                    meta_log_path,
                    f"Encountered an error applying the Nearest-Neighbor model on {os.path.basename(frame_path)}:\n"
                    f"\t{error}\n"
                    f"\t{error_traceback}",
                )
                continue # can't calculate dense without dilute!

            print("Calculating dense radii...")
            if settings.use_ds_psf:
                max_workers = settings.max_workers
                try:
                    parallelComputeAllDenseRadiusDSPSF(Drop_Image, Max_Workers = max_workers)
                    print("Calculated dense radii with double sphere + PSF model:")
                    printAverages(Drop_Image, "nearest_neighbor", "ds_psf")
                    applied_dense_methods.append("ds_psf")
                except Exception as error:
                    error_traceback = traceback.format_exc()
                    writeMeta(
                        meta_log_path, 
                        f"Encountered an error applying the Double-Sphere model on {os.path.basename(frame_path)}:\n"
                        f"\t{error}\n"
                        f"\t{error_traceback}",
                    )

            if settings.use_se_psf:
                max_workers = settings.max_workers
                try:
                    parallelComputeAllDenseRadiusSEPSF(
                        Drop_Image, 
                        settings.se_aspect_ratio, 
                        Max_Workers = max_workers
                    )
                    print("Calculated dense radii with sphere elipse + PSF model:")
                    printAverages(Drop_Image, "nearest_neighbor", "se_psf")
                    applied_dense_methods.append("se_psf")
                except Exception as error:
                    error_traceback = traceback.format_exc()
                    writeMeta(
                        meta_log_path, 
                        f"Encountered an error applying the Sphere-Ellipse model on {os.path.basename(frame_path)}:\n"
                        f"\t{error}\n"
                        f"\t{error_traceback}",
                    )

            print("Finished calculations!")

            print("Generating segmentation image...")
            if len(applied_dense_methods) > 0:
                try:
                    Drop_Image.segmentationImage(
                        os.path.join(
                            paths['segmentation'], 
                            os.path.splitext(os.path.basename(frame_path))[0] + '_segmentation_image.png',
                        ),
                        "nearest_neighbor",
                        applied_dense_methods[0]
                    )
                except Exception as error:
                    writeMeta(meta_log_path, f"Unable to generate segmentation image for {os.path.basename(frame_path)}\n\t{error}")
                    this_frame_success = 0
            else:
                print("No dense phase analysis methods were applied! Unable to generate segmentation image...")
                writeMeta(meta_log_path, f"No dense phase analysis methods were applied! Unable to generate segmentation image for {os.path.basename(frame_path)}")

            print("Writing analysis log...")
            try:
                Drop_Image.writeCSV(
                    os.path.join(
                        paths['analysis_logs'], 
                        os.path.splitext(os.path.basename(frame_path))[0] + '_analysis_log.csv'
                    )
                )
            except Exception as error:
                writeMeta(meta_log_path, f"Unable to write analysis log for {os.path.basename(frame_path)}\n\t{error}")
                this_frame_success = 0

            successful_images += this_frame_success

        writeMeta(
            meta_log_path, 
            f"Successfully processed {successful_images}/{total_images}."
        )
# ---------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
# ---------------------------------------------------------------------------------------------------- #
