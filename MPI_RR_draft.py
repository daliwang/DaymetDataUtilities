from mpi4py import MPI
import numpy as np
import random
from itertools import cycle

size_array = 10
number_of_domains = 3

grid_ids = np.linspace(1, size_array, size_array, dtype=int)    
mask = np.random.randint(2, size=size_array)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if (rank== 0):
    print(masks)

# create the global list of land surface gridcell
grid_ids = np.multiply(mask,grid_ids)
grid_ids = grid_ids[grid_ids != 0]

if (rank ==0):
    print(grid_ids)
    
# cyclic (round-robin) partition scheme

domains = [[] for _ in range(number_of_domains)]
for element, domain in zip(grid_ids, cycle(domains)):
    domain.append(element)
    
#from pprint import pprint
#pprint(domains)

domain_arr = np.array(domains)
