import os
import re


def rename_files(directory, new_name, filter):
    files = os.listdir(directory)
    counter = 1

    for file in files:
        if re.match(filter, file):
            file_extension = "." + file.split('.')[-1]
            os.rename(os.path.join(directory, file), os.path.join(directory, new_name + str(counter) + filter))
            counter += 1
            os.rename(directory + file, directory + new_name + str(counter) + file_extension)
            print('Renamed ' + file + ' to ' + new_name + str(counter) + file_extension)


rename_files("/Downloads/test_renamer/", 'new_name', 'txt')

