from shutil import rmtree
from os import walk, path, mkdir
from pydub import AudioSegment
from sys import argv, exit

RESULT_DIRNAME = 'Result'
RESULT_CONVERTED_DIRNAME = 'Result_mp3'
FILE_EXTENSION = '.mp3'
SUPPORTED_FORMATS = [
    'mp3',
    'flac'
]

def get_trees():
  result_files = []
  for root, _, files in walk(RESULT_DIRNAME):
    for filename in files:
      result_files.append(path.join(path.realpath(root), filename))

  result_converted_files = []
  for root, _, files in walk(RESULT_CONVERTED_DIRNAME):
    for filename in files:
      result_converted_files.append(path.join(path.realpath(root), filename))

  return result_files, result_converted_files

def compare_trees():
  result_files, result_converted_files = get_trees()
  new_files = []
  for file in result_files:
    path = list(file.partition(RESULT_DIRNAME))
    path[1] = RESULT_CONVERTED_DIRNAME
    if not ''.join(path) + FILE_EXTENSION in result_converted_files:
      new_files.append(file)
  return new_files

def make_result_tree():
    size = 0
    for _, _, files in walk(RESULT_DIRNAME):
        size += len(files)
    new_files = compare_trees()
    if not new_files:
      print("All resource from result folder is already converted")
      return
    if not path.exists(RESULT_CONVERTED_DIRNAME):
        print("Creating result directory ({})".format(RESULT_CONVERTED_DIRNAME))
        mkdir(RESULT_CONVERTED_DIRNAME)
    text_template = """
    Current result folder contain {} files.
    {} files is already converted to {}.
    Do you want to converted another {} files?"""
    print(text_template.format(size, size-len(new_files), FILE_EXTENSION[1:], len(new_files)))
    if input("y/n ").lower() == 'y':
        currentIndex = 1
        for root, dirs, files in walk(RESULT_DIRNAME):
            for dirname in dirs:
                currentDirName = path.join(RESULT_CONVERTED_DIRNAME, '\\'.join(root.split('\\')[1:]), dirname)
                if not path.exists(currentDirName):
                    mkdir(currentDirName)
            for filename in files:
                currentDirName = path.join(RESULT_CONVERTED_DIRNAME, '\\'.join(root.split('\\')[1:]))
                if path.join(path.realpath(root), filename) in new_files:
                    if FILE_EXTENSION == '.flac':
                        AudioSegment.from_raw(path.join(root, filename),
                                              sample_width=2,
                                              frame_rate=44100,
                                              channels=2).export(path.join(currentDirName, filename) + FILE_EXTENSION,
                                                                 format='flac')
                    elif FILE_EXTENSION == '.mp3':
                        AudioSegment.from_raw(path.join(root, filename),
                                              sample_width=2,
                                              frame_rate=44100,
                                              channels=2).export(path.join(currentDirName, filename) + FILE_EXTENSION,
                                                                 format='mp3')
                    print("\t{}..{}\t{} successfully converted to {}".format(currentIndex, len(new_files), path.join(root, filename), FILE_EXTENSION[1:]))
                    currentIndex += 1
    else:
        print("OK. See you later")
        return
    print("\t All new files successfully converted to {}".format(FILE_EXTENSION[1:]))

if __name__ == "__main__":
    if len(argv) > 1:
        RESULT_DIRNAME = argv[1]
    if len(argv) > 2:
        RESULT_CONVERTED_DIRNAME = argv[2]
    if len(argv) > 3:
        FILE_EXTENSION = '.' + argv[3]
    if len(argv) > 4:
        print("Too many arguments.")
        print("Usage: raw2flac RESULT_DIRNAME DESTINATION_DIRNAME FILE_FORMAT")
        print("default: RESULT_DIRNAME - {} \n\t DESTINATION_DIRNAME - {} \n\t FILE_FORMAT - {}".format(RESULT_DIRNAME, RESULT_CONVERTED_DIRNAME, FILE_EXTENSION))
        exit(2)
    if not FILE_EXTENSION[1:] in SUPPORTED_FORMATS:
        print("Unknown audio format {}".format(FILE_EXTENSION[1:]))
        print("Supported formats: {}".format(', '.join(SUPPORTED_FORMATS)))
        exit(3)
    print("Start scaning \n\t{} \nto find source file and convert to {} in folder \n\t{}\n".format(path.realpath(RESULT_DIRNAME), FILE_EXTENSION[1:], path.realpath(RESULT_CONVERTED_DIRNAME)))
    if path.exists(RESULT_DIRNAME):
        make_result_tree()
    else:
        print("Can't find result dir with name {}".format(RESULT_DIRNAME))
    input("Press enter to quit")