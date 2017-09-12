
# Standard Python modules
import sys
# PyQt Modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
# CCCG modules
from gui.mainwindow_ui import Ui_MainWindow
# CIME modules
from Tools.standard_script_setup import *
from CIME.XML.machines import Machines
from CIME.XML.files import Files
from CIME.XML.compsets import Compsets
from CIME.XML.grids import Grids


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


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
#        print "gridname is {}".format(grid.keys())
        ResList.addItem(grid[0])
        
if __name__ == "__main__":
    main()
