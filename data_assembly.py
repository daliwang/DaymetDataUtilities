import os 
import netCDF4 as nc
import numpy as np
from time import process_time 

#from matplotlib import pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

input_path= '/home/7xw/data/GWSP3_DayMet/'
file_name = '/home/7xw/data/GWSP3_DayMet/NA_V3_tileid.regimg.nc'

# Open a new NetCDF file to write the data to. For format, you can choose from
# 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'

start = process_time()
r_nc_fid = nc.Dataset(file_name, 'r', format='NETCDF3_CLASSIC')
TileID = r_nc_fid['image'][:, :]
end = process_time()
print("Reading GridID takes  {}".format(end-start))

total_rows = len(TileID)
total_cols = len(TileID[1])
start = process_time()  
total_timesteps = 248     # 8 x 31 (days) 
DataDomain=np.zeros((total_timesteps, total_rows, total_cols), dtype = 'float')
DataDomain.fill(-1)
end = process_time()  
print("Creating DataDomain uses: ", end-start)

files = os.listdir(input_path) 
files.sort() 
#output_path = input_path + '/outputs/'

file_no =0

tiles_list = [f for f in files if (f[0:4] == 'TILE')] 
print("total " + str(len(tiles_list)) + " tiles need to be processed")

#tiles_list= ['TILE10845', 'TILE11388', 'TILE13870']  # Three tiles
#tiles_list= ['TILE10845'] # New Orlean
#tiles_list= ['TILE11388']  # Knoxville
#tiles_list= ['TILE13870']  # xxx, AK
for f in tiles_list: 
    start = process_time()  
    print(f)
    iTileID = f[4:]
    print(iTileID)
    ff=input_path + f
    file_name = ff + '/Solar3Hrly/clmforc.Daymet4.1km.Solr.1980-01.nc'

    # Open a new NetCDF file to write the data to. For format, you can choose from
    # 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC', and 'NETCDF4'
    r_nc_fid = nc.Dataset(file_name, 'r', format='NETCDF4')
    FSDS = r_nc_fid['FSDS'][0:total_timesteps, :, :] # read mutiple timestep
    FSDS = FSDS.transpose(0,2,1)   # change to (time, x,y) format
    tile_rows = len(FSDS[0])
    tile_cols = len(FSDS[0][0])
    print (tile_rows, tile_cols)
    # find the first one zero element
    index = np.argmax(FSDS[0] > 0)
    icols = (index % tile_cols)
    irows = int(index / tile_cols)
    index = np.argmax(TileID == int(iTileID))
    gcols = (index % total_cols)
    grows = int(index / total_cols)
    np.copyto(DataDomain[:,grows:grows+tile_rows,gcols-icols:gcols-icols+tile_cols], FSDS, where=FSDS>=0)
    end = process_time()  
    print("Processing ", f, " uses: ", end-start)
    
'''
x = np.linspace(1, total_rows, total_rows, dtype=int)
y = np.linspace(1, total_cols, total_cols, dtype=int)
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
X,Y = np.meshgrid(x, y)
ax.view_init(90,-0)
ax.plot_surface(X, Y,np.transpose(DataDomain[0]))
'''

