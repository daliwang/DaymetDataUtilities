import os 
import netCDF4 as nc
import numpy as np
from itertools import cycle
#from pprint import pprint
from time import process_time 

#from matplotlib import pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

input_path= '/home/7xw/data/GWSP3_DayMet/2014NA'
file_name = '/home/7xw/data/GWSP3_DayMet/2014NA/clmforc.Daymet4.1km.FSDS.2014-01.nc'
subdomain_path = input_path + '/subdomains/'

vis =0 
debug = 0
save_memory = 1

number_of_subdomains = 4200  # 4200 for 700 Summit nodes
i_timesteps = 248   # 248 for 31 days

print('number of subdomains: ('+ str(number_of_subdomains) + '), timeseries: ('+ str(i_timesteps) + ')')

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

# grid_id starts with 0
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

# partition data into subdomain

FSDS_domains = []
for i in range(i_timesteps):
    # convert the FSDS array to a list
    data_list = FSDS[i].tolist()
    # cyclic (round-robin) partition
    domains = [[] for _ in range(number_of_subdomains)]
    for element, domain in zip(data_list, cycle(domains)):
        domain.append(element)

    FSDS_domains.append(domains.copy())

    #pprint(domains)
    if debug and i==0 :
        print(len(domains[0]), len(domains[number_of_subdomains - 1]));print(len(domains))

end = process_time()
print("Partitioning FSDS/GridID takes  {}".format(end-start))

if save_memory: 
    del grid_ids, FSDS, mask

# generate local subdomain files
start = process_time()
for i in range(number_of_subdomains):
    # convert local grid_id_lists into an array
    
    grid_id_arr = np.array(grid_id_domains[i])
    i_data = []
    for j in range(i_timesteps):
        i_data.append(np.array(FSDS_domains[j][i]))
        
    # convert the local data_list into an array
    data_arr = np.array(i_data)

    file_name = subdomain_path + 'subdomain'+ str(i) + '.nc'

    # Open a new NetCDF file to write the data to. For format, you can choose from
    # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
    w_nc_fid = nc.Dataset(file_name, 'w', format='NETCDF4')
    w_nc_fid.title = 'The ELM domain files on individudal process: '+str(i)

    # create our gridIDs variable
    x_dim = w_nc_fid.createDimension('x_dim', grid_id_arr.size)
    time_dim = w_nc_fid.createDimension('time_dim', i_timesteps)
    w_nc_var = w_nc_fid.createVariable('gridIDs', np.int32, ('x_dim'))
    w_nc_var.long_name = 'gridIds in the subdomain'    
    w_nc_fid.variables['gridIDs'][:] = grid_id_arr.reshape(grid_id_arr.size)
    
    w_nc_var = w_nc_fid.createVariable('FSDS', np.float32, ('time_dim', 'x_dim'))
    w_nc_var.long_name = 'FSDS in the subdomain'    
    w_nc_fid.variables['FSDS'][:] = data_arr.reshape(i_timesteps, grid_id_arr.size)

    w_nc_fid.close()  # close the new file

end = process_time()
print("Saving FSDS/GridID takes  {}".format(end-start))

if save_memory:
    del data_list, data_arr, domain, grid_id_arr, domains, grid_id_domains
