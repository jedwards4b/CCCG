
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
from mainwindow import MainWindow

# CIME modules
from Tools.standard_script_setup import *

logger = logging.getLogger(__name__)

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
