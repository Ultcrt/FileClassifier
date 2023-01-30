import shutil
import time

import exifread
import os

if __name__ == '__main__':
    recursive_flag = input("Do you want to classify files recursively? (Y/N)")
    while recursive_flag != "Y" and recursive_flag != "N":
        recursive_flag = input("Invalid input, Y for yes and N for no: ")

    classify_precision = input("Do you want to classify files by day, month or year? (Y/M/D)")
    while classify_precision != "Y" and classify_precision != "M" and classify_precision != "D":
        classify_precision = input("Invalid input, Y for year, M for month and D for day: ")

    input_directory = input("Please input directory: ")
    if recursive_flag == "Y":
        filepaths = []
        for path, _, filenames in os.walk(input_directory):
            for filename in filenames:
                filepaths.append(os.path.join(path, filename))
    else:
        filepaths = []
        for filename in os.listdir(input_directory):
            filepaths.append(os.path.join(input_directory, filename))

    for filepath in filepaths:
        print(filepath)
    double_check = input("Directory contains %s files above, are you sure to process? (Y/N)" % len(filepaths))
    while double_check != "Y" and double_check != "N":
        double_check = input("Invalid input, Y for yes and N for no: ")

    output_directory = "./output/"
    error_directory = os.path.join(output_directory, "error")
    log_path = os.path.join(output_directory, "log.txt")

    count = 0
    if double_check == "Y":
        print("Processing...")
        for filepath in filepaths:
            # Ignore directories
            if not os.path.isdir(filepath):
                # Ignore .ini files
                if not filepath.endswith(".ini"):
                    with open(filepath, "rb") as f:
                        try:
                            exif_info = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
                            # Has exif
                            if exif_info.get("EXIF DateTimeOriginal", None) is not None:
                                taken_time_string = str(exif_info["EXIF DateTimeOriginal"])
                                taken_time_struct = time.strptime(taken_time_string, "%Y:%m:%d %H:%M:%S")
                            # Doesn't have exif
                            else:
                                create_timestamp = os.path.getctime(filepath)
                                modified_timestamp = os.path.getmtime(filepath)
                                taken_timestamp = min(modified_timestamp, create_timestamp)
                                taken_time_struct = time.localtime(taken_timestamp)

                            if classify_precision == "Y":
                                dest_path = os.path.join(
                                    output_directory,
                                    str(taken_time_struct.tm_year)
                                )
                            elif classify_precision == "M":
                                dest_path = os.path.join(
                                    output_directory,
                                    str(taken_time_struct.tm_year),
                                    str(taken_time_struct.tm_mon).zfill(2)
                                )
                            elif classify_precision == "D":
                                dest_path = os.path.join(
                                    output_directory,
                                    str(taken_time_struct.tm_year),
                                    str(taken_time_struct.tm_mon).zfill(2),
                                    str(taken_time_struct.tm_mday).zfill(2)
                                )
                        except Exception as e:
                            dest_path = os.path.join(output_directory, "error")
                            with open(log_path, "a") as log:
                                log.write(filepath + " -> " + str(e) + "\n")

                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path, exist_ok=True)

                        shutil.copy2(filepath, dest_path)
                        count += 1

                        print("\r%.2f%%" % (100 * count / len(filepaths)), end="")
    print("\nFinished (copied %d files in total)." % count)
    input("Press any key to exit...")
