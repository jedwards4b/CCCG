
# Standard Python modules
import sys
# PyQt Modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QFileDialog,\
    QTableWidgetItem
from PyQt5 import QtCore
# CCCG modules
from gui.mainwindow_ui import Ui_MainWindow
from gui.casewindow_ui import Ui_CaseWindow

# CIME modules
from Tools.standard_script_setup import *
from CIME.case import Case
from CIME.XML.machines import Machines
from CIME.XML.files import Files
from CIME.XML.compsets import Compsets
from CIME.XML.grids import Grids


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self._casenames = []
        self.CaseWindow = {}
        
    def MachineSelect(self, text):
        """ Handle selection of Machine """
        machine = self.MachineList.Machobj.set_machine(text)
        compilers = self.MachineList.Machobj.get_value("COMPILERS").split(',')
        self.CompilerList.setEnabled(True)
        self.CompilerList.clear()
        self.CompilerList.addItems(compilers)
        mpilibs = self.MachineList.Machobj.get_value("MPILIBS").split(',')
        mpilibs.append("mpi_serial")
        self.MPILIBList.setEnabled(True)
        self.MPILIBList.clear()
        self.MPILIBList.addItems(mpilibs)

    def CompsetSelect(self, text):
        files = Files()
        components = files.get_components("COMPSETS_SPEC_FILE")
        for comp in components:
            infile = files.get_value("COMPSETS_SPEC_FILE", {"component":comp})
            compsetobj = Compsets(infile=infile, files=files)
            longname, _, _ = compsetobj.get_compset_match(text)
            if longname is not None:
                self.CompsetLongName.setEnabled(True)
                self.CompsetLongName.setText(longname)
                valid_grids = self.ResList.gridsobj.find_valid_alias_list(longname)
                self.ResList.clear()
                for grid in valid_grids:
                    self.ResList.addItem(grid[0])

    def OpenCase(self):
        filedialog = QFileDialog()
        filedialog.setFileMode(QFileDialog.Directory)
        if filedialog.exec_():
            casename = filedialog.selectedFiles()[0]
            if casename in self._casenames:
                # Should be an error - case is already open
                pass
            else:
                self._casenames.append(casename)
                self.CaseWindow[casename] = CaseWindow(casename)
                self.CaseWindow[casename].show()

                
class CaseWindow(QMainWindow, Ui_CaseWindow):
    def __init__(self, casename):
        super(CaseWindow, self).__init__()
        self.setupUi(self)
        with Case(casename) as case:
            self.populate_case_tab(case)
            self.populate_setup_tab(case)
            self.populate_build_tab(case)
            self.populate_run_tab(case)

    def tablecellactivated(self):
        print "Which table?"
            
    def populate_case_tab(self, case):
        env_case = case.get_env('case')
        self.populate_tab(env_case, self.CaseTabtableWidget)

    def populate_setup_tab(self, case):
        env_mach_pes = case.get_env('mach_pes')
        self.populate_tab(env_mach_pes, self.SetuptableWidget)
#        self.SetuptableWidget.cellActivated.connect(self.tablecellactivated)
        
    def populate_build_tab(self, case):
        env_build = case.get_env('build')
        self.populate_tab(env_build, self.BuildtableWidget)
    
    def populate_run_tab(self, case):
        env_run = case.get_env('run')
        self.populate_tab(env_run, self.RuntableWidget)
    
        
        
    def populate_tab(self, entry_id_obj, tableWidget):
        entry_nodes = entry_id_obj.get_nodes("entry")
        tableWidget.setHorizontalHeaderLabels(['Variable', 'Value'])
        tableWidget.setColumnCount(2)
        tableWidget.setRowCount(len(entry_nodes))
        row = 0
        for node in entry_nodes:
            vid = node.get("id")
            vid_entry = QTableWidgetItem(vid)
            vid_entry.setFlags(QtCore.Qt.NoItemFlags)
            value_entry = QTableWidgetItem(str(entry_id_obj.get_value(vid)))
            value_entry.setFlags(QtCore.Qt.ItemIsSelectable)
            tableWidget.setItem(row, 0, vid_entry)
            tableWidget.setItem(row, 1, value_entry)
            row += 1


            
        
def main():
    args = sys.argv
    parser = argparse.ArgumentParser(usage="Fill this in",
                                     description="an experimental gui tool",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CIME.utils.setup_standard_logging_options(parser)
    args = CIME.utils.parse_args_and_handle_standard_logging_options(args, parser)


    app = QApplication(sys.argv)
    main_window = MainWindow()
    list_models(main_window.ModelList)
    list_machines(main_window.MachineList)
    list_compsets(main_window.CompsetList)
    list_grids(main_window.ResList)
    main_window.MachineList.activated[str].connect(main_window.MachineSelect)
    main_window.CompsetList.activated[str].connect(main_window.CompsetSelect)
    main_window.actionOpen.triggered.connect(main_window.OpenCase)
    main_window.show()
    sys.exit(app.exec_())

def list_models(ModelList):
    ModelList.addItems(("CESM","ACME"))
    
def list_machines(MachineList):
    MachineList.Machobj = Machines()
    mach_list = MachineList.Machobj.list_available_machines()
    MachineList.addItems(mach_list)

def list_compsets(CompsetList):
    files = Files()
    components = files.get_components("COMPSETS_SPEC_FILE")
    for comp in components:
        infile = files.get_value("COMPSETS_SPEC_FILE", {"component":comp})
        compsetobj = Compsets(infile=infile, files=files)
        _, compsets = compsetobj.return_all_values()
        CompsetList.addItems(sorted(compsets.keys()))
        CompsetList.insertSeparator(999)


def list_grids(ResList):
    ResList.gridsobj = Grids()
    all_grids = ResList.gridsobj.find_valid_alias_list()
    for grid in all_grids:
        ResList.addItem(grid[0])
        
        
if __name__ == "__main__":
    main()
