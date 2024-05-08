import numpy as np
#import copy


#def calc(data, number_of_beams, number_of_glancing_angles, omega, verbose_mode):
def calc(data, omega):
    sigma = 0.5 * omega / (np.sqrt(2.0 * np.log(2.0)))

    def g(x):
        g = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * x**2 / sigma**2)
        return g

    conv = np.zeros(data.shape)
    # # copy glancing angle
    # RC_data_cnv[:, 0] = copy.deepcopy(data[:, 0])

    # if verbose_mode:
    #     print("data =\n", data)
    #     print("conv =\n", conv)

    # for beam_index in range(number_of_beams):
    #     for index in range(number_of_glancing_angles):
    #         integral = 0.0
    #         angle_interval = 0.0
    #         for index2 in range(number_of_glancing_angles):
    #             if index2 < number_of_glancing_angles - 1:
    #                 angle_interval = RC_data_org[index2 + 1, 0] - RC_data_org[index2, 0]
    #             integral += (
    #                 RC_data_org[index2, beam_index + 1]
    #                 * g(RC_data_org[index, 0] - RC_data_org[index2, 0])
    #                 * angle_interval
    #             )
    #             if verbose_mode:
    #                 print(
    #                     "beam_index, index, index2, g(RC_data_org[index,0] - RC_data_org[index2,0]) =",
    #                     beam_index,
    #                     index,
    #                     index2,
    #                     g(RC_data_org[index, 0] - RC_data_org[index2, 0]),
    #                 )
    #         RC_data_cnv[index, beam_index + 1] = integral

    xs = np.array(data[:,0])
    vs = data[:,1:]

    dxs = np.roll(xs,-1) - xs
    dxs[-1] = dxs[-2]

    ys = np.zeros(vs.shape)

    for idx in range(xs.shape[0]):
        ys[idx] = np.einsum('ik,i,i->k', vs, g(xs-xs[idx]), dxs)

    conv[:,0] = xs
    conv[:,1:] = ys

    # if verbose_mode:
    #     print("conv =\n", conv)

    return conv

