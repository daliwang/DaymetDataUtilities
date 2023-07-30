import numpy as np
import random
from itertools import cycle
#from pprint import pprint
import sys 
import os
import netCDF4 as nc

# configure the right python_path and subdomain_path
# sys.path.append('/home/7xw/Documents/work/ELM_ECP/lib/python3.8/site-packages/')
subdomain_path = '/home/7xw/ELM_ECP/test003/subdomains/'

# make sure all the subdomains are newly created
#remove_file = '/bin/rm ' + subdomain_path +'*'
#os.system(remove_file)

debug = 0

# setup the total gridcell number and number of subdomains
total_gridcells = 75000000  # the average number of land gridcells is 37 M
number_of_subdomains = 4200  # 700 Summit nodes

# generate a continous list of gridcellID
grid_ids = np.linspace(1, total_gridcells, total_gridcells, dtype=int)

# generate a mask of 25M+ non-zero elements (all ones or randamalized or predefined) 
#mask = np.ones(total_gridcells/2, dtype=int)
mask = np.random.randint(2, size=total_gridcells)
while (mask.sum() < total_gridcells/3):
    mask = np.random.randint(2, size=total_gridcells)

if debug :
    print(mask[1:20]); print(mask.sum());print(grid_ids[1:20])

# create an active gridID list and reduce the size of gridIDs array
grid_ids = np.multiply(mask,grid_ids)
grid_ids = grid_ids[grid_ids != 0]

if debug:
    print(grid_ids[1:20])
    
# cyclic (round-robin) partition
domains = [[] for _ in range(number_of_subdomains)]
for element, domain in zip(grid_ids, cycle(domains)):
    domain.append(element)

#pprint(domains)
if debug :
    print(len(domains[number_of_subdomains - 1]));print(len(domains))
'''
# generate local subdomain files
for i in range(number_of_subdomains):
    # convert local gridID-list into array
    domain_arr = np.array(domains[i])
    file_name = subdomain_path + 'subdomain'+ str(i) + '.nc'

    # Open a new NetCDF file to write the data to. For format, you can choose from
    # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
    w_nc_fid = nc.Dataset(file_name, 'w', format='NETCDF4')
    w_nc_fid.title = 'The ELM domain files on individudal process: '+str(i)

    # create our gridIDs variable
    x_dim = w_nc_fid.createDimension("x_dim", domain_arr.size)
    w_nc_var = w_nc_fid.createVariable('gridIDs', np.int32, x_dim)
    w_nc_var.long_name = 'gridIds in the subdomain'
    w_nc_fid.variables['gridIDs'][:] = domain_arr.reshape(domain_arr.size)
    w_nc_fid.close()  # close the new file

'''    
