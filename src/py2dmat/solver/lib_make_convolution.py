import numpy as np
import sys

def calc(RC_data_org, RC_data_cnv, number_of_beams, number_of_glancing_angles, omega, verbose_mode):

    sigma = 0.5 * omega / (np.sqrt(2.0*np.log(2.0)))

    def g(x):
        g = (1.0 / (sigma*np.sqrt(2.0*np.pi))) * np.exp(-0.5 * x ** 2.0 / sigma ** 2.0)

        return g

    angle_interval = RC_data_org[1,0] - RC_data_org[0,0]

    if verbose_mode:
       print("RC_data_org =\n",RC_data_org) 
       print("RC_data_cnv =\n",RC_data_cnv) 
       print('angle_ interval=', angle_interval)

    for beam_index in range(number_of_beams):
        for index in range(number_of_glancing_angles):
            integral = 0.0
            for index2 in range(number_of_glancing_angles):
                integral += RC_data_org[index2,beam_index+1] * g(RC_data_org[index,0] - RC_data_org[index2,0]) * angle_interval
                if verbose_mode:
                    print("beam_index, index, index2, g(RC_data_org[index,0] - RC_data_org[index2,0]) =",beam_index, index, index2, g(RC_data_org[index,0] - RC_data_org[index2,0]))
            RC_data_cnv[index, beam_index+1]=integral

    if verbose_mode:
       print("RC_data_cnv =\n",RC_data_cnv) 

    return RC_data_cnv
