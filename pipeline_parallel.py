""" Pipeline for running the inversion
"""

import numpy as np
from util import define_models
from util import mineos
from util import inversion
from util import partial_derivatives
from util import weights
from util import constraints
import shutil
import sys
import matplotlib.pyplot as plt
import multiprocess as mp
import os

class FailCheckLimit(Exception):
    pass

def run_inversion_loc(name:str, location:tuple, mdep:int, attempts:int):

    name = name + "." + str(location[0]) + "." + str(location[1])

    #check if this was already run for this set
    if os.path.isfile('./output/models/' + name + '.csv'):

        print(name + " already run for this project name")
        return 1

    model_params = define_models.ModelParams(depth_limits=np.array([0., mdep]),
        id=name, randomize_model=False, randomize_data=False,
        method='mineos',min_layer_thickness=6, head_wave=True, breadth=1,
            roughness = (1,1,4,4,0),
            to_0_grad = (0,0,0,0,0), q_model = './data/earth_models/qmod_highQ')

    depth = np.linspace(0, mdep, mdep)

    i = 0
    #Mineos often fails randomly with file IO, but you can repeat easily without slowing the code down
    failcheck = 0

    #(model, obs, misfit) = inversion.run_inversion_TAarray(model_params,location,25)

    while failcheck < attempts:

        try:
            (model, obs, misfit) = inversion.run_inversion_TAarray(model_params,location,25)

            if model is None:
                return

            break
        except:
            failcheck += 1

            if failcheck >= attempts:
                raise FailCheckLimit(name + ' failed ' + str(attempts) + ' times in a row, aborting.')
                return 0

            continue

        i += 1
        failcheck = 0 #restart count

    define_models.save_model(model, name)
    shutil.rmtree("./output/" + name)

    return 1

def main(mdep:int=400, attempts:int=5):

    name = "Data8322"
    lat = np.arange(25,51,0.5)
    lon = np.arange(-125.,-65,0.5)
    #lat = np.arange(33.,45.5,0.5)
    #lon = np.arange(-119.,-100.5,0.5)

    LT, LN = np.meshgrid(lat, lon)

    LT = LT.flatten()
    LN = LN.flatten()

    #for k in np.arange(0, len(LT)):
    #for k in np.arange(0, 1):
    #for k in np.arange(0, len(LT)):
    #    run_inversion_loc(name, (LT[k],LN[k]), mdep, attempts)
    pool = mp.Pool(mp.cpu_count())
    list(pool.map(lambda k:run_inversion_loc(name, (LT[k],LN[k]), mdep, attempts), range(len(LT))))

if __name__ == '__main__':

    if len(sys.argv)==1:
        print('Doing a whole run')
        main()
    elif len(sys.argv)==2:
        main(int(sys.argv[1]))
    else:
        print('Check input arugment list')