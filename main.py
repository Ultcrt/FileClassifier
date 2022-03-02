import shutil
import time

import exifread
import os

if __name__ == '__main__':
    photo_directory = input("Please input image directory: ")
    filenames = os.listdir(photo_directory)
    print(filenames, "\nDirectory contains files above, are you sure to process? (Y/N)")
    answer = input("")
    while answer != "Y" and answer != "N":
        print("Invalid input, Y for yes and N for no: ")
        answer = input("")
    count = 0
    if answer == "Y":
        print("Processing...")
        for filename in filenames:
            file_path = os.path.join(photo_directory, filename)
            # Ignore directories
            if not os.path.isdir(file_path):
                # Ignore .ini files
                if not filename.endswith(".ini"):
                    with open(file_path, "rb") as f:
                        exif_info = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal")
                        # Has exif
                        if exif_info.get("EXIF DateTimeOriginal", None) is not None:
                            taken_time_string = str(exif_info["EXIF DateTimeOriginal"])
                            taken_time_struct = time.strptime(taken_time_string, "%Y:%m:%d %H:%M:%S")
                        # Doesn't have exif
                        else:
                            create_timestamp = os.path.getctime(file_path)
                            modified_timestamp = os.path.getmtime(file_path)
                            taken_timestamp = modified_timestamp if create_timestamp > modified_timestamp else create_timestamp
                            taken_time_struct = time.localtime(taken_timestamp)
                        year_path = os.path.join(photo_directory, str(taken_time_struct.tm_year))
                        mon_path = os.path.join(year_path, str(taken_time_struct.tm_mon).zfill(2))
                        if not os.path.exists(year_path):
                            os.mkdir(year_path)
                        if not os.path.exists(mon_path):
                            os.mkdir(mon_path)
                        shutil.copy(file_path, mon_path)
                        count += 1
    print("Finished (%d in total)." % count)
