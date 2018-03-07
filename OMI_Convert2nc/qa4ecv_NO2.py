"""
A python module for reading and converting QA4ECV NO2 data to netCDF format.

"""
import numpy as np
import gzip
import re
import netCDF4 as nc4
import os
from datetime import datetime

def readHeader(fname):
    """Read QA4ECV NO2 ASCII data header.

    PARAMETERS
    ----------
    fname : str
        Path to the filename

    RETURNS
    -------
    header : a list of useful variables: year, month, nlat, nlon, lat_start, lat_end, lon_start, lon_end 
    """
    f=gzip.open(fname,'rb')
    line0 = f.readline()
    line1 = str(f.readline())
    date = re.findall(r"[-+]?\d*\.\d+|\d+", line1)
    year = int(date[0])
    month = int(date[1])
    line2 = str(f.readline())
    lon_array = re.findall(r"[-+]?\d*\.\d+|\d+", line2)
    nlon = int(lon_array[0])
    lon_start = float(lon_array[1])*-1.
    lon_end = float(lon_array[2])
    line3 = str(f.readline())
    lat_array = re.findall(r"[-+]?\d*\.\d+|\d+", line3)
    nlat = int(lat_array[0])
    lat_start = float(lat_array[1])*-1.
    lat_end = float(lat_array[2])
    header = [year, month, nlat, nlon, lat_start, lat_end, lon_start, lon_end]
    f.close()
    return header

def readData(fname, nlat, nlon):
    """Read QA4ECV NO2 ASCII data to a two-dimensional array.

    PARAMETERS
    ----------
    fname : str
        Path to the filename
    nlat : int
        Number of latitudes
    nlon : int
        Number of Longitudes
    RETURNS
    -------
    xi : a two-dimensional array (lat, lon)
    """
    f=gzip.open(fname,'rb')
    kint = 4 #each integer is 3 characters
    kcol = 20 # Each line has 20 columns
    klJump = int(nlon/20)  # Each latitude group is 12 lines (rows)   
    kcStrt   = 0         
    kcLast   = kint*kcol-1
    xi = np.zeros((nlat, nlon))
    for i in range(4):
        f.readline()
    for nl in range(0,nlat):       
        f.readline()
        klon = -1
        for kline in range(0, klJump):
            for kc in range(0,kcol):
                klon = klon+1
                xi[nl,klon] = int(f.readline(kint)) 
            f.readline(2)
    return xi

def convert2nc(data, nlat, nlon, lat_start, lat_end, lon_start, lon_end, outname, varname):
    """Read QA4ECV NO2 ASCII data to a two-dimensional array.

    PARAMETERS
    ----------
    data : array
        Input data (lat, lon)
    nlat : int
        Number of latitudes
    nlon : int
        Number of Longitudes
    lat_start : float
        Latitude of the first row.
    lat_end : float
        Latitude of the last row.
    lon_start : float
        Longitude of the first column.
    lon_end : float
        Longitude of the last column. 
     outname : str
        Path to NetCDF file 
    varname : str
        Variable Name
    """
    if os.path.exists(outname):
        os.remove(outname)
    lat = np.linspace(lat_start, lat_end, num=nlat)
    lon = np.linspace(lon_start, lon_end, num=nlon)
    f = nc4.Dataset(outname,'w', format='NETCDF4')
    tempgrp = f.createGroup(varname)
    tempgrp.createDimension('lon', len(lon))
    tempgrp.createDimension('lat', len(lat))
    longitude = tempgrp.createVariable('Longitude', 'f4', 'lon')
    latitude = tempgrp.createVariable('Latitude', 'f4', 'lat')
    temp = tempgrp.createVariable(varname, 'f4', ('lat', 'lon'), fill_value=-999)
    print(temp.shape)
    longitude[:] = lon
    latitude[:] = lat
    temp[:,:] = data
    today = datetime.today()
    f.description = "QA4ECV monthly average NO2"
    f.history = "Created " + today.strftime("%d/%m/%y")
    longitude.units = 'degrees east'
    latitude.units = 'degrees north'
    temp.units = '1e13 molec/cm2'
    f.close()
