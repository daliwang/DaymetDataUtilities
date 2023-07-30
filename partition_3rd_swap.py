# Code for whole NA domain using Kao's dataset
import os 
import netCDF4 as nc
import numpy as np
from itertools import cycle
from pprint import pprint
from time import process_time 

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

input_path= '/home/7xw/data/GWSP3_DayMet/2014NA'
file_name = '/home/7xw/data/GWSP3_DayMet/2014NA/clmforc.Daymet4.1km.FSDS.2014-01.nc'

vis =0 
debug = 1
save_memory = 1

number_of_subdomains = 4200  # 4200 for 700 Summit nodes
i_timesteps = 248   # 248 for 31 days

start = process_time()
# Open a new NetCDF file to write the data to. For format, you can choose from
# 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
r_nc_fid = nc.Dataset(file_name, 'r', format='NETCDF4')

total_rows = r_nc_fid.dimensions['x'].size
total_cols = r_nc_fid.dimensions['y'].size
total_timesteps = r_nc_fid.dimensions['time'].size


FSDS = r_nc_fid['FSDS'][0:i_timesteps, :, :] # read (timestep, y, x) format
#FSDS = FSDS.transpose(0,2,1)   # change to (time, x,y) format
end = process_time()
print("Reading FSDS takes  {}".format(end-start))

if vis :
    x = np.linspace(1, total_rows, total_rows, dtype=int)
    y = np.linspace(1, total_cols, total_cols, dtype=int)
    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
    X,Y = np.meshgrid(x, y)
    ax.view_init(90,0)
    ax.plot_wireframe(Y, X, FSDS[0])
    plt.show()

# Create a global ID for ALL the gridcells

start = process_time()
total_gridcells = total_rows * total_cols
grid_ids = np.linspace(0, total_gridcells-1, total_gridcells, dtype=int)

# create a mask for land grid_ids (1)
mask = FSDS[0]    # FSDS is in (time, Y, X) format
mask = np.where(~np.isnan(mask), 1, 0)

# create an flattened list of land gridID and reduce the size of gridIDs array
grid_ids = grid_ids.reshape(total_cols,total_rows)
grid_ids = np.multiply(mask,grid_ids)
grid_ids = grid_ids[grid_ids != 0]

end = process_time()
print("Generate Grid_id takes  {}".format(end-start))

# use the size of land gridcells to resize the FSDS matrix
start = process_time()
landcells = len(grid_ids)
if debug:
    print('number of land cells is '+str(landcells))
    
FSDS=FSDS[~np.isnan(FSDS)]
FSDS = np.reshape(FSDS,(i_timesteps,landcells))

end = process_time()
print("Creating dense FSDS takes  {}".format(end-start))


start = process_time()
# partition landcells into subdomains
# number_of_subdomains = 4200  # 4200 for 700 Summit nodes

# cyclic (round-robin) partition
domains = [[] for _ in range(number_of_subdomains)]
for element, domain in zip(grid_ids, cycle(domains)):
    domain.append(element)

#for i in range(number_of_subdomains):
#    # convert local gridID-list into array
#    grid_id_arr[i] = np.array(domains[i])  
grid_id_domains = domains.copy()

# partition the FSDS over landcells
# landcell_idx is alse the column_idx of FSDS
landcell_idx = np.linspace(0, landcells-1, landcells, dtype=int)

domains = [[] for _ in range(number_of_subdomains)]
for element, domain in zip(landcell_idx, cycle(domains)):
    domain.append(element)
    
# save the boundaries of each subdomain (for array_split)
size_of_subdomains = [ len(domain) for domain in domains]

# partitioned landcells_idx in subdomains 
arranged_grid_idx = np.concatenate(domains).ravel()
print(arranged_grid_idx)
# find the original index of landcells for column swap
np.sort(arranged_grid_idx)
grid_swap_idx = (np.argsort(arranged_grid_idx))

# create swap index and arrange FSDS
idx = np.empty_like(grid_swap_idx)
idx[grid_swap_idx] = np.arange(len(grid_swap_idx))
FSDS = FSDS[:,idx]

end = process_time()
print("Partitioning FSDS/GridID takes  {}".format(end-start))
