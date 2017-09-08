
# Standard Python modules
import sys
# PyQt Modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox
# CCCG modules
from gui.mainwindow_ui import Ui_MainWindow
# CIME modules
from Tools.standard_script_setup import *
from CIME.XML.machines import Machines



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def MachineSelect(self, text):
        machine = self.MachineList.Machobj.set_machine(text)
        compilers = self.MachineList.Machobj.get_value("COMPILERS").split(',')
        self.CompilerList.clear()
        self.CompilerList.addItems(compilers)
        mpilibs = self.MachineList.Machobj.get_value("MPILIBS").split(',')
        mpilibs.append("mpi_serial")
        self.MPILIBList.clear()
        self.MPILIBList.addItems(mpilibs)
        
        
def main():
    args = sys.argv
    parser = argparse.ArgumentParser(usage="Fill this in",
                                     description="an experimental gui tool",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CIME.utils.setup_standard_logging_options(parser)
    args = CIME.utils.parse_args_and_handle_standard_logging_options(args, parser)


    app = QApplication(sys.argv)
    main_window = MainWindow()
    list_machines(main_window.MachineList)
    list_compilers(main_window.MachineList, main_window.CompilerList)
    main_window.MachineList.activated[str].connect(main_window.MachineSelect)
    main_window.show()
    sys.exit(app.exec_())

    


def list_machines(MachineList):
    MachineList.Machobj = Machines()
    mach_list = MachineList.Machobj.list_available_machines()
    MachineList.addItems(mach_list)

def list_compilers(MachineList, CompilerList):
    mach = MachineList.currentText()
    

    
def list_mpilibs(MachineList, MPILIBList):
    mach = MachineList.currentText()
    print "{}".format(mach)

    

if __name__ == "__main__":
    main()
