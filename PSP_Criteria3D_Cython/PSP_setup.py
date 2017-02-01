from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'Criteria 3D solver',
  ext_modules = cythonize("PSP_solverC.pyx"),
)