import os
import glob

counter = 1
dir_name = 'C:\\Users\\Emilio\Desktop\\trasferimenti\\images\\'
list_of_files = sorted(filter(os.path.isfile,
                              glob.glob(dir_name + '*')))
# 'C:\\Users\\Emilio\\Desktop\\trasferimenti\\images\\tavola_ottimizzata_25_episodio_4_07.jpg'

for index, file in enumerate(list_of_files):
    src = file
    src_tavola = 'tavola_ottimizzata_' + file.split('\\')[-1].split('_')[2]
    episode_number = file.split('\\')[-1].split('_')[4]
    episode = 'episodio_' + file.split('\\')[-1].split('_')[4]
    if counter == 1:
        previous_episode_number = episode_number
    else:
        previous_episode_number = list_of_files[index-1].split('\\')[-1].split('_')[4]
    base_path = 'C:\\Users\\Emilio\Desktop\\trasferimenti\\images_renamed\\'

    if counter < 10:
        panel = 'vignetta_000'
    elif counter < 100:
        panel = 'vignetta_00'
    else:
        panel = 'vignetta_0'
    dst = base_path + episode + '_' + src_tavola + '_' + panel + str(counter) + '.jpg'
    os.rename(src, dst)
    if previous_episode_number == episode_number:
        counter += 1
    else:
        counter = 1


