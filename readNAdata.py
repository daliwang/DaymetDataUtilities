# Code for whole NA domain using Kao's dataset
import os 
import netCDF4 as nc
import numpy as np

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

input_path= '/home/7xw/data/GWSP3_DayMet/2014NA'
file_name = '/home/7xw/data/GWSP3_DayMet/2014NA/clmforc.Daymet4.1km.FSDS.2014-01.nc'

# Open a new NetCDF file to write the data to. For format, you can choose from
# 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
r_nc_fid = nc.Dataset(file_name, 'r', format='NETCDF4')

total_rows = r_nc_fid.dimensions['x'].size
total_cols = r_nc_fid.dimensions['y'].size
total_timesteps = r_nc_fid.dimensions['time'].size
i_timesteps = 2

FSDS = r_nc_fid['FSDS'][0:i_timesteps, :, :] # read mutiple timestep
#FSDS = FSDS.transpose(0,2,1)   # change to (time, x,y) format

x = np.linspace(1, total_rows, total_rows, dtype=int)
y = np.linspace(1, total_cols, total_cols, dtype=int)
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
X,Y = np.meshgrid(x, y)
ax.view_init(90,0)
ax.plot_wireframe(Y, X, FSDS[0])
plt.show()