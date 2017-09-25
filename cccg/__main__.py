
# Standard Python modules
import sys
from ConfigParser import SafeConfigParser as config_parser
    
# PyQt Modules
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QFileDialog,\
    QTableWidgetItem
from PyQt5 import QtCore
# PyQtGraphics Modules
from pyqtgraph.parametertree import ParameterTree, Parameter
import pyqtgraph.parametertree.parameterTypes 

# CCCG modules
from gui.mainwindow_ui import Ui_MainWindow
from gui.create_newcase_ui import Ui_CreateNewcase
from gui.casewindow_ui import Ui_CaseWindow

# CIME modules
from Tools.standard_script_setup import *
from CIME.case import Case
from CIME.utils import check_name
from CIME.XML.machines import Machines
from CIME.XML.files import Files
from CIME.XML.compsets import Compsets
from CIME.XML.grids import Grids

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
        self.CreateNewcaseDialog = CreateNewCase()
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



            
class CreateNewCase(QMainWindow, Ui_CreateNewcase):
    def __init__(self):
        super(CreateNewCase, self).__init__()
        self.setupUi(self)
        self.CreateNewcaseArgs = {}
    
        self.list_models()
        self.list_machines()
        self.list_compsets()
        self.list_grids()
        self.MachineList.activated[str].connect(self.MachineSelect)
        self.CompilerList.activated[str].connect(self.CompilerSelect)
        self.MPILIBList.activated[str].connect(self.MPIlibSelect)

        self.CompsetLongName.returnPressed.connect(self.CompsetLongnameSelect)
        self.CompsetList.activated[str].connect(self.CompsetSelect)
        self.CancelCreateNewcase.clicked.connect(self.cancel)
        self.ApplyCreateNewcase.clicked.connect(self.create_new_case)
        self.CaseNameInput.returnPressed.connect(self.set_casename)
        self.ResList.activated[str].connect(self.set_grid)

    def set_grid(self, text):
        self.CreateNewcaseArgs["res"] = text
        self.check_ready_to_apply()

    def CompilerSelect(self, text):
        self.CreateNewcaseArgs["compiler"] = text
        self.check_ready_to_apply()

    def MPIlibSelect(self, text):
        logger.info("Here {}".format(text))
        self.CreateNewcaseArgs["mpilib"] = text
        self.check_ready_to_apply()
                       
    def set_casename(self):
        text = self.CaseNameInput.text()
        if check_name(text):
            self.CreateNewcaseArgs["case"] = text
            self.ApplyCreateNewcase.setEnabled(True)
        self.check_ready_to_apply()

    def check_ready_to_apply(self):
        ready = True
        for var in ("res", "compiler", "mpilib", "case", "compset", "machine"):
            if var not in self.CreateNewcaseArgs.keys():
                ready = False
                logger.info("{} not yet defined".format(var))
        self.ApplyCreateNewcase.setEnabled(ready)



    def create_new_case(self):
        
        pass


        
    def cancel(self):
        self.close()

        
    def list_models(self):
        self.ModelList.addItems(("CESM","ACME"))
    
    def list_machines(self):
        self.MachineList.Machobj = Machines()
        mach_list = self.MachineList.Machobj.list_available_machines()
        self.MachineList.addItems(mach_list)
        name = self.MachineList.Machobj.get_machine_name()
        if name is not None:
            self.MachineList.setCurrentIndex(mach_list.index(name))
            self.MachineSelect(name)
            
    def list_compsets(self):
        files = Files()
        components = files.get_components("COMPSETS_SPEC_FILE")
        for comp in components:
            infile = files.get_value("COMPSETS_SPEC_FILE", {"component":comp})
            compsetobj = Compsets(infile=infile, files=files)
            _, compsets = compsetobj.return_all_values()
            self.CompsetList.addItems(sorted(compsets.keys()))
            self.CompsetList.insertSeparator(999)
            

    def list_grids(self):
        self.ResList.gridsobj = Grids()
        all_grids = self.ResList.gridsobj.find_valid_alias_list()
        for grid in all_grids:
            self.ResList.addItem(grid[0])
        
    def MachineSelect(self, text):
        """ Handle selection of Machine """
        machine = self.MachineList.Machobj.set_machine(text)
        compilers = self.MachineList.Machobj.get_value("COMPILERS").split(',')
        self.CompilerList.setEnabled(True)
        self.CompilerList.clear()
        if "compiler" not in self.CreateNewcaseArgs.keys():
            self.CreateNewcaseArgs["compiler"] = compilers[0]
        self.CompilerList.addItems(compilers)
        mpilibs = self.MachineList.Machobj.get_value("MPILIBS").split(',')
        mpilibs.append("mpi_serial")
        if "mpilib" not in self.CreateNewcaseArgs.keys():
            self.CreateNewcaseArgs["mpilib"] = mpilibs[0]
        self.MPILIBList.setEnabled(True)
        self.MPILIBList.clear()
        self.MPILIBList.addItems(mpilibs)
        self.CreateNewcaseArgs["machine"] = machine
        self.check_ready_to_apply()
        
    def CompsetLongnameSelect(self):
        self.CreateNewcaseArgs["compset"] = self.CompsetLongName.text()
        self.check_ready_to_apply()

        
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
                self.CreateNewcaseArgs["compset"] = longname
        self.check_ready_to_apply()

    

                
class CaseWindow(QMainWindow, Ui_CaseWindow):
    def __init__(self, casename):
        super(CaseWindow, self).__init__()
        self.setupUi(self)
        self.setMouseTracking(1)
        with Case(casename) as case:
            self.populate_case_tab(case)
            self.populate_setup_tab(case)
            self.populate_build_tab(case)
            self.populate_run_tab(case)

    def tablecellactivated(self):
        print "Which table?"
            

    def populate_case_tab(self, case):
        entry_id_obj = case.get_env('case')
        self.populate_tab(case, entry_id_obj, self.CaseParameterTree, writable=False)

    def populate_run_tab(self, case):
        entry_id_obj = case.get_env('run')
        self.populate_tab(case, entry_id_obj, self.RunParameterTree)

    def populate_setup_tab(self, case):
        entry_id_obj = case.get_env('mach_pes')
        self.populate_tab(case, entry_id_obj, self.SetupParameterTree)

    def populate_build_tab(self, case):
        entry_id_obj = case.get_env('build')
        self.populate_tab(case, entry_id_obj, self.BuildParameterTree)

    def populate_tab(self, case, entry_id_obj, parametertree, writable=True):
        entry_nodes = entry_id_obj.get_nodes("entry")
        for node in entry_nodes:
            vid = node.get("id")
            type = entry_id_obj.get_type_info(vid)
            if type == "integer":
                type = "int"
            elif type == "logical":
                type = "bool"
            elif type == "char":
                type = "str"
            elif type == "real":
                type = "float"
            if hasattr(entry_id_obj, "_component_value_list") and vid in entry_id_obj._component_value_list:
                top_param = Parameter.create(name=vid, type='group')
                for comp in entry_id_obj._components:
                    name = vid + "_{}".format(comp)
                    value = case.get_value(name)
                    if value is not None:
                        param = Parameter.create(name=name, type=type, value=value)
                        param.setWritable(writable)
                        top_param.addChild(param)
                parametertree.addParameters(top_param)
            else:
                value = case.get_value(vid)
                valid_values = entry_id_obj.get_valid_values(vid)
                tip = entry_id_obj.get_description(node)
                if valid_values is not None:
                    if type == "str":
                        type = 'list'
                param = Parameter.create(name=vid, type=type, value=value, values=valid_values)
#                param.widget.setToolTip(tip)
                param.setWritable(writable)
                parametertree.addParameters(param)


def main():
    args = sys.argv
    parser = argparse.ArgumentParser(usage="Fill this in",
                                     description="an experimental gui tool",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-caseroot" , "--caseroot", default=None,
                        help="Case directory to reference")

    CIME.utils.setup_standard_logging_options(parser)
    args = CIME.utils.parse_args_and_handle_standard_logging_options(args, parser)


    app = QApplication(sys.argv)
    main_window = MainWindow()
    if args.caseroot:
        main_window.OpenCase(args.caseroot)

    cccg_config = get_cccg_config()
    for name, value in cccg_config.items("main"):
        if name == "case_root_dir_list":
            values = value.split(',')
            for val in values:
                main_window.CaserootdirectoryComboBox.addItem(val)
            main_window.CaserootdirectoryComboBox.setCurrentIndex(0)
    main_window.CaserootdirectoryComboBox.activated[str].connect(main_window.SetCaserootdirectory)
            
        
        
    main_window.show()
    sys.exit(app.exec_())


# Should only be called from get_cccg_config()
def _read_cccg_config_file():
    """
    """
    from ConfigParser import SafeConfigParser as config_parser

    cccg_config_file = os.path.abspath(os.path.join(os.path.expanduser("~"),
                                                  ".cccg","config"))
    cccg_config = config_parser()
    if(os.path.isfile(cccg_config_file)):
        cccg_config.read(cccg_config_file)
    else:
        cccg_config.add_section('main')

    return cccg_config

_CCCGCONFIG = None
def get_cccg_config():
    global _CCCGCONFIG
    if (not _CCCGCONFIG):
        _CCCGCONFIG = _read_cccg_config_file()

    return _CCCGCONFIG

def reset_cccg_config():
    """
    Useful to keep unit tests from interfering with each other
    """
    global _CCCGCONFIG
    _CCCGCONFIG = None


    
        
if __name__ == "__main__":
    main()
