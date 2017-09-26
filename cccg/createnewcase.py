from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QFileDialog,\
    QTableWidgetItem


from CIME.XML.standard_module_setup import *
from CIME.XML.machines import Machines
from CIME.case import Case
from CIME.XML.files import Files
from CIME.XML.compsets import Compsets
from CIME.XML.grids import Grids
from CIME.utils import check_name, get_cime_root


# CCCG modules
from gui.create_newcase_ui import Ui_CreateNewcase

logger = logging.getLogger(__name__)
            
class CreateNewCase(QMainWindow, Ui_CreateNewcase):
    def __init__(self, casedir):
        super(CreateNewCase, self).__init__()
        self._casedir = casedir
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
        srcroot = os.path.dirname(os.path.abspath(get_cime_root()))
        casename = self.CreateNewcaseArgs["case"]
        with Case(os.path.join(self._casedir,casename)) as case:
            case.create(casename,
                        srcroot,
                        self.CreateNewcaseArgs["compset"],
                        self.CreateNewcaseArgs["res"],
                        machine_name=self.CreateNewcaseArgs["machine"],
                        compiler=self.CreateNewcaseArgs["compiler"],
                        mpilib=self.CreateNewcaseArgs["mpilib"],
                        run_unsupported=True)
        
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

    

