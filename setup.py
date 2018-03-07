from setuptools import setup

setup(
    name = "OMI_Convert2nc",
    version = "0.0.1",
    author = "Xiaomeng Jin",
    packages=['OMI_Convert2nc'],
    install_requires=['numpy','netcdf4','datetime'],
)
