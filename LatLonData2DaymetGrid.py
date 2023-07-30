import netCDF4 as nc
import numpy as np
#from mpl_toolkits import basemap
from pyproj import Transformer
import matplotlib.pyplot as plt

save = 1

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

# get the coarse resolution data and the locations (lat, lon)
r_surf = nc.Dataset('surfdata.nc', 'r', format='NETCDF4')
lats = r_surf.variables['LATIXY'][:]
lons = r_surf.variables['LONGXY'][:]
mask = r_surf.variables['PFTDATA_MASK'][:]

# get the fine resolution data and the locations (lat, lon)
r_daymet = nc.Dataset('Daymet_FSDS.nc', 'r', format='NETCDF4')
lats_d = r_daymet.variables['lat'][:]
lons_d = r_daymet.variables['lon'][:]
x_coor = r_daymet.variables['x'][:]  # 1D x-axis
y_coor = r_daymet.variables['y'][:]  # 1D y-axis
FSDS = r_daymet.variables['FSDS'][0,:,:]

fig = plt.figure()
# ax1 -- contour plot of resampled data
ax1 = fig.add_subplot(211)
plt.imshow(mask)
# ax2 -- imshow plot of resampled data
ax2 = fig.add_subplot(212)
plt.imshow(FSDS[::10,::10])  # show the 1/10 image

# convert (lat, lon) into (x, y) 
proj_daymet = "+proj=lcc +lat_0=42.5 +lon_0=-100 +lat_1=25 +lat_2=60 +x_0=0 +y_0=0 +ellps=WGS84 +units=m +no_defs" #custom CRS
transformer = Transformer.from_crs("EPSG:4326", proj_daymet)

# (lat, lon) 
all_points = np.column_stack((lats.flatten(),lons.flatten()))
print(len(all_points))

reduction_rate = 1    #  reduce the data to 1/N (1 no reduction).     
sub_points = all_points[::reduction_rate]  # reduce the point to 1/N
print(len(sub_points))
sub_points = sub_points[(sub_points[:,0] < lats_d.max()) 
                        & (sub_points[:,0] > lats_d.min())]
print(len(sub_points))
xy_list=[]
for pt in sub_points:
    xy_list.append(transformer.transform(pt[0], pt[1]))
xy = np.array(xy_list)
print(len(xy))

# remove all the outside points
xy_daymet=xy[(xy[:,0] < x_coor.max()) & (xy[:,0] > x_coor.min())
              & (xy[:,1] < y_coor.max()) & (xy[:,1] > y_coor.min())]
print(len(xy_daymet))

# remove all the outside points
latlon_daymet=sub_points[(xy[:,0] < x_coor.max()) & (xy[:,0] > x_coor.min())
              & (xy[:,1] < y_coor.max()) & (xy[:,1] > y_coor.min())]
print(len(latlon_daymet))

# find the nearest points and their index within DayMet (XY)domain
x_daymet=[]
y_daymet=[]
for point in xy_daymet:
    x_daymet.append(find_nearest(x_coor, point[0]))
    y_daymet.append(find_nearest(y_coor, point[1]))
    
#if save:
#    np.savetxt('origin_points_y_x.csv', yx_daymet, fmt='%10.3f', delimiter=',')
#    np.savetxt('origin_points_lat_lon.csv', latlon_daymet, fmt='%10.3f', delimiter=',') 
print(y_daymet[0:5])

# save the location and index into files
import pandas as pd
data_x = pd.DataFrame(x_daymet, columns=["x_coordinate ","x_index"])
data_y = pd.DataFrame(y_daymet, columns=["y_coordinate ","y_index"])
points_in_daymet = pd.concat([data_x, data_y], axis=1)

data_xy = pd.DataFrame(xy_daymet, columns=["x","y"])
data_latlon = pd.DataFrame(latlon_daymet, columns=["lat ","lon"])
original_points = pd.concat([data_xy, data_latlon], axis=1)

if save:
    points_in_daymet.to_csv("points_in_daymet_grid.csv", index=False)
    original_points.to_csv("original_points_within_daymet_domain.csv", index=False)
    
### save the data location for intepration     
gy = lats[:,0]
gx = lons[0,:]
y_index=[]
x_index=[]
for pt in latlon_daymet:
    y_idx = np.where(gy == pt[0])
    x_idx = np.where(gx == pt[1])
    y_index.append(y_idx[0][0])
    x_index.append(x_idx[0][0])    
print(y_index[0:5],x_index[0:5])

data_y = pd.DataFrame(y_index, columns=["y_index"])
data_x = pd.DataFrame(x_index, columns=["x_index"])
points_index = pd.concat([data_y, data_x], axis=1)

original_points_index = pd.concat([original_points, points_index], axis=1)
if save:
    points_index.to_csv("points_index.csv", index=False)
    original_points_index.to_csv("original_points_index.csv", index=False)
    
print("i am done")