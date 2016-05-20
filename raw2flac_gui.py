from os import walk, path, mkdir
from pydub import AudioSegment
from sys import argv, exit

from PyQt5.QtWidgets import QWidget, QFileDialog, QApplication
from PyQt5.QtCore import pyqtSignal, QThread

from main_ui import Ui_Form

class convertFileThread(QThread):

    successfullyConvert = pyqtSignal(str, str)

    def __init__(self, resourceDict, audioFormat):
        QThread.__init__(self)
        self.resourceDict = resourceDict
        self.audioFormat = audioFormat

    def __del__(self):
        self.wait()

    def _convert(self, resourcePath, destinationPath):
        try:
            AudioSegment.from_raw(resourcePath,
                                  sample_width=2,
                                  frame_rate=22050,
                                  channels=2).export(destinationPath,
                                                     format=self.audioFormat)
            return True
        except:
            return False

    def run(self):
        for resPath in self.resourceDict:
            if self._convert(resPath, self.resourceDict[resPath]):
                self.successfullyConvert.emit(resPath, self.resourceDict[resPath])
            else:
                print("Handle exception with convert {} to {}".format(resPath, self.resourceDict[resPath]))


class MainWindow(Ui_Form):
    def __init__(self, form):
        self.setupUi(form)

        self.RESULT_DIRNAME = ''
        self.RESULT_CONVERTED_DIRNAME = ''
        self.FILE_EXTENSION = '.' + self.audioFormatComboBox.currentText()
        self.currentIndex = 0

        self.resourceDirectoryDialogButton.clicked.connect(self.showResourceDialog)
        self.resourceDirectoryLineEdit.textChanged.connect(self.resourceChanged)
        self.destinationDirectoryDialogButton.clicked.connect(self.showDestinationDialog)
        self.destinationDirectoryLineEdit.textChanged.connect(self.destinationChanged)
        self.audioFormatComboBox.currentTextChanged.connect(self.formatChange)
        self.scanButton.clicked.connect(self.compareTrees)
        self.convertButton.clicked.connect(self.convert)

    def scanButtonChangeState(self):
        parent_dir = self.RESULT_CONVERTED_DIRNAME.partition("\\")[0]
        self.scanButton.setEnabled(path.isdir(self.RESULT_DIRNAME) and path.isdir(parent_dir))

    def resourceChanged(self):
        self.RESULT_DIRNAME = self.resourceDirectoryLineEdit.text()
        self.scanButtonChangeState()

    def destinationChanged(self):
        self.RESULT_CONVERTED_DIRNAME = self.destinationDirectoryLineEdit.text()
        self.scanButtonChangeState()

    def formatChange(self, text):
        self.FILE_EXTENSION = '.' + text
        if self.convertButton.isEnabled():
            self.convertButton.setEnabled(False)
            self.informationTextEdit.clear()
            self.informationTextEdit.append("Scan again to find new files")

    def showResourceDialog(self):
        path_dir = path.normpath(QFileDialog.getExistingDirectory())
        if path_dir != '.':
            self.resourceDirectoryLineEdit.setText(path_dir)
            self.RESULT_DIRNAME = path_dir
            if not self.destinationDirectoryLineEdit.text():
                self.RESULT_CONVERTED_DIRNAME = path_dir + "_" + self.FILE_EXTENSION[1:]
                self.destinationDirectoryLineEdit.setText(self.RESULT_CONVERTED_DIRNAME)
            self.scanButtonChangeState()

    def showDestinationDialog(self):
        path_dir = path.normpath(QFileDialog.getExistingDirectory())
        if path_dir != '.':
            self.destinationDirectoryLineEdit.setText(path_dir)
            self.RESULT_CONVERTED_DIRNAME = path_dir
            self.scanButtonChangeState()

    def compareTrees(self):
        self.FILE_EXTENSION = "." + self.audioFormatComboBox.currentText()
        self.scanMessage = """Current result folder contain {} files.
{} files is already converted to {}.
Press convert button to start convert another {} files."""
        result_files = []
        for root, _, files in walk(self.RESULT_DIRNAME):
            for filename in files:
                result_files.append(path.relpath(path.join(root, filename), start=self.RESULT_DIRNAME))

        result_converted_files = []
        for root, _, files in walk(self.RESULT_CONVERTED_DIRNAME):
            for filename in files:
                if filename.endswith(self.FILE_EXTENSION):
                    result_converted_files.append(path.relpath(path.join(root, filename), start=self.RESULT_CONVERTED_DIRNAME))

        new_files = []
        for file in result_files:
            if not file + self.FILE_EXTENSION in result_converted_files:
                new_files.append(path.normpath(file))

        self.informationTextEdit.clear()
        if not new_files:
            self.informationTextEdit.append("All resource from {} is already convert".format(self.RESULT_DIRNAME))
        else:
            self.new_files = new_files
            self.informationTextEdit.append(self.scanMessage.format(len(result_files), len(result_converted_files), self.FILE_EXTENSION[1:], len(new_files)))
            self.convertButton.setEnabled(True)
            self.convertProgressBar.setMaximum(len(new_files))
            self.convertProgressBar.setValue(0)
            self.currentIndex = 0

    def convert(self):
        resourceDict = {}
        if not path.exists(self.RESULT_CONVERTED_DIRNAME):
            mkdir(self.RESULT_CONVERTED_DIRNAME)
        for root, dirs, files in walk(path.relpath(self.RESULT_DIRNAME)):
            for dirname in dirs:
                dirpath = path.join(root, dirname)
                full_dirpath = path.join(self.RESULT_CONVERTED_DIRNAME, path.relpath(path.realpath(dirpath), start=self.RESULT_DIRNAME))
                if not path.exists(full_dirpath):
                    mkdir(full_dirpath)
            for filename in files:
                fill_respath = path.join(self.RESULT_DIRNAME, path.relpath(path.realpath(root), start=self.RESULT_DIRNAME))
                full_destpath = path.join(self.RESULT_CONVERTED_DIRNAME, path.relpath(path.realpath(root), start=self.RESULT_DIRNAME))
                if path.relpath(path.join(root, filename), start=self.RESULT_DIRNAME) in self.new_files:
                    resourceDict[path.join(fill_respath, filename)] = path.join(full_destpath, filename) + self.FILE_EXTENSION
        self.convertButton.setEnabled(False)
        self.thread = convertFileThread(resourceDict, self.FILE_EXTENSION[1:])
        self.thread.successfullyConvert[str, str].connect(self.convertAnotherOne)
        self.thread.start()


    def convertAnotherOne(self, resourcePath, destinationPath):
        self.informationTextEdit.append("{} successfully convert".format(resourcePath))
        self.convertProgressBar.setValue(self.convertProgressBar.value() + 1)

if __name__ == "__main__":
    app = QApplication(argv)
    app.setStyle("fusion")
    win = QWidget()
    ui = MainWindow(win)
    win.show()
    exit(app.exec_())
