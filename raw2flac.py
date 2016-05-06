from shutil import rmtree
from os import walk, path, mkdir
from pydub import AudioSegment
from time import sleep

RESULT_DIRNAME = 'Result'
RESULT_CONVERTED_DIRNAME = 'Result_flac'


def make_result_tree():
    size = 0
    for _, _, files in walk(RESULT_DIRNAME):
        size += len(files)
    print("Creating result directory ({})".format(RESULT_CONVERTED_DIRNAME))
    mkdir(RESULT_CONVERTED_DIRNAME)
    print("Start converting {} file. It may take a few minutes.".format(size))
    currentIndex = 1
    for root, dirs, files in walk(RESULT_DIRNAME):
        for dirname in dirs:
            currentDirName = path.join(RESULT_CONVERTED_DIRNAME, '\\'.join(root.split('\\')[1:]), dirname)
            mkdir(currentDirName)
        for filename in files:
            currentDirName = path.join(RESULT_CONVERTED_DIRNAME, '\\'.join(root.split('\\')[1:]))
            AudioSegment.from_raw(path.join(root, filename),
                                  sample_width=2,
                                  frame_rate=44100,
                                  channels=2).export(path.join(currentDirName, filename) + '.flac',
                                                     format='flac')
            print("\t{}..{}\t{} successfully converted to flac".format(currentIndex, size, path.join(root, filename)))
            currentIndex += 1


def clear():
    if path.exists(RESULT_CONVERTED_DIRNAME):
        print("Warning: {} will be removed in few second".format(RESULT_CONVERTED_DIRNAME))
        sleep(5)
        rmtree(RESULT_CONVERTED_DIRNAME)
        print("Successfully remove {}".format(RESULT_CONVERTED_DIRNAME))

if __name__ == "__main__":
    if path.exists(RESULT_DIRNAME):
        clear()
        make_result_tree()
        print("Successfully converted all files")
    else:
        print("Can't find result dir with name {}".format(RESULT_DIRNAME))
