from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QFileDialog,\
    QTableWidgetItem


from CIME.XML.standard_module_setup import *

# CCCG modules
from gui.mainwindow_ui import Ui_MainWindow
from createnewcase import CreateNewCase
from casewindow import CaseWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self._casenames = []
        self.CaseWindow = {}
        self.CaselistWidget.itemActivated.connect(self.OpenCaseDialog)
        self.CreateNewcaseButton.clicked.connect(self.OpenCreateNewcase)

    def OpenCreateNewcase(self):
        self.CreateNewcaseDialog = CreateNewCase(self.CaselistWidget._casedir)
        self.CreateNewcaseDialog.show()
        
    def FindCaseDir(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.Directory)
        if filedialog.exec_():
            casename = filedialog.selectedFiles()[0]
            self.OpenCase(casename)

    def OpenCaseDialog(self, caselistitem):
        fullpath = os.path.join(self.CaselistWidget._casedir,caselistitem.text())
        print fullpath
        self.OpenCase(fullpath)

    def OpenCase(self, casename):
        if casename in self._casenames:
            # casename is already open - change focus?
            pass
        else:
            self._casenames.append(casename)
            self.CaseWindow[casename] = CaseWindow(casename)
            self.CaseWindow[casename].show()

    def SetCaserootdirectory(self, dirname):
        # list all subdirectories of dirname
        for casedir in filter(os.path.isdir, [os.path.join(dirname, f) for f in os.listdir(dirname)]):
            # Confirm this is a case directory 
            if os.path.isfile(os.path.join(casedir,"env_case.xml")):
                self.CaselistWidget.addItem(os.path.basename(casedir))
                self.CaselistWidget._casedir = dirname

