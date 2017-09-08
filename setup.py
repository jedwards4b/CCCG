from setuptools import setup
from pyqt_distutils.build_ui import build_ui

try:
    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

setup(
    name="cccg",
    version="0.1",
    packages=["cccg"],
    cmdclass=cmdclass,
)

