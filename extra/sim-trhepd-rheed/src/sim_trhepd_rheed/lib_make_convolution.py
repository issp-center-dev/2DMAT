import numpy as np
import copy


def calc(RC_data_org, number_of_beams, number_of_glancing_angles, omega, verbose_mode):

    sigma = 0.5 * omega / (np.sqrt(2.0 * np.log(2.0)))

    def g(x):
        g = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(
            -0.5 * x**2.0 / sigma**2.0
        )

        return g

    RC_data_cnv = np.zeros((number_of_glancing_angles, number_of_beams + 1))
    # copy glancing angle
    RC_data_cnv[:, 0] = copy.deepcopy(RC_data_org[:, 0])

    if verbose_mode:
        print("RC_data_org =\n", RC_data_org)
        print("RC_data_cnv =\n", RC_data_cnv)

    for beam_index in range(number_of_beams):
        for index in range(number_of_glancing_angles):
            integral = 0.0
            angle_interval = 0.0
            for index2 in range(number_of_glancing_angles):
                if index2 < number_of_glancing_angles - 1:
                    angle_interval = RC_data_org[index2 + 1, 0] - RC_data_org[index2, 0]
                integral += (
                    RC_data_org[index2, beam_index + 1]
                    * g(RC_data_org[index, 0] - RC_data_org[index2, 0])
                    * angle_interval
                )
                if verbose_mode:
                    print(
                        "beam_index, index, index2, g(RC_data_org[index,0] - RC_data_org[index2,0]) =",
                        beam_index,
                        index,
                        index2,
                        g(RC_data_org[index, 0] - RC_data_org[index2, 0]),
                    )
            RC_data_cnv[index, beam_index + 1] = integral

    if verbose_mode:
        print("RC_data_cnv =\n", RC_data_cnv)

    return RC_data_cnv

