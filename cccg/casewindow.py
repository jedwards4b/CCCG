from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QFileDialog,\
    QTableWidgetItem

# PyQtGraphics Modules
from pyqtgraph.parametertree import ParameterTree, Parameter
import pyqtgraph.parametertree.parameterTypes 

from CIME.XML.standard_module_setup import *
from CIME.case import Case

from gui.casewindow_ui import Ui_CaseWindow

logger = logging.getLogger(__name__)

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

