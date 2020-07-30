from scipy.optimize import fmin
import numpy as np
import os
import shutil
import Solver_Surface as Solver
from argparse import ArgumentParser

def f_calc(x_list, info, extra=False):
    sol_surf = Solver.Surface(info)
    min_list = info["min_list"]
    max_list = info["max_list"]
    unit_list = info["unit_list"]
    label_list = info["label_list"]
    main_dir = info["main_dir"]
    ##### judge value #####
    out_of_range = False
    for index in range(dimension):
        if x_list[index] < min_list[index] or x_list[index] > max_list[index]:
            print(
                "Warning: %s = %f is out of range(min%f ~ max%f)."
                % (label_list[index], x_list[index], min_list[index], max_list[index])
            )
            out_of_range = True
    ##### unit modify #####
    new_x_list = []
    for index in range(dimension):
        new_x_list.append(x_list[index] / unit_list[index])
    x_list = new_x_list
    print(len(x_list), dimension)

    if out_of_range:
        y = 100.0
    else:
        info["Log_number"] += 1
        sol_surf.set_log(info["Log_number"])
        y = sol_surf.f(x_list, extra)
        os.chdir(main_dir)
        # callback_list seems not to be used.
        if not extra_data:
            callback = [info["Log_number"]]
            for index in range(dimension):
                callback.append(x_list[index])
            callback.append(y)
            callback_list.append(callback)
        print("Debug: Log {}".format(info["Log_number"]))
    return y


############################

def get_info(args):
    dimension = args.dimension
    if len(args.llist) != dimension:
        print("Error: len(llist) is not equal to dimension")
        exit(1)
    if len(args.slist) != dimension:
        print("Error: len(slist) is not equal to dimension")
        exit(1)
    if len(args.inilist) != dimension:
        print("Error: len(inilist) is not equal to dimension")
        exit(1)
    if len(args.unit_list) != dimension:
        print("Error: len(unit_list) is not equal to dimension")
        exit(1)
    if len(args.minlist) != dimension:
        print("Error: len(inilist) is not equal to dimension")
        exit(1)
    if len(args.maxlist) != dimension:
        print("Error: len(inilist) is not equal to dimension")
        exit(1)
    if len(args.initial_scale_list) != dimension:
        print("Error: len(initial_scale_list) is not equal to dimension")
        exit(1)
    info = {}
    info["dimension"] = args.dimension
    info["label_list"] = args.llist
    info["string_list"] = args.slist
    info["initial_list"] = args.inilist
    info["unit_list"] = args.unit_list
    info["min_list"] = args.minlist
    info["max_list"] = args.maxlist
    info["initial_scale_list"] = args.initial_scale_list
    info["surface_input_file"] = args.sinput
    info["bulk_output_file"] = args.boutput
    info["surface_output_file"] = args.soutput
    info["Rfactor"] = args.rfactor  # "A":General or "B":Pendry
    info["normalization"] = args.norm  # "TOTAL" or "MAX"
    info["file"] = {}
    info["file"]["calculated_first_line"] = args.cfirst
    info["file"]["calculated_last_line"] = args.clast
    info["file"]["row_number"] = args.rnumber  # row number of 00 spot in .s file
    info["omega"] = args.omega  # half width of convolution
    info["degree_max"] = args.dmax
    info["xtol_value"] = args.xtol
    info["ftol_value"] = args.ftol
    info["main_dir"] = os.getcwd()
    info["Log_number"] = 0

    # Read experiment-data
    print("Read experiment.txt")
    degree_list = []
    I_experiment_list = []
    experiment_first_line = args.efirst
    experiment_last_line = args.elast
    with open("experiment.txt", "r") as fp:
        lines = fp.readlines()
        for line in lines[experiment_first_line - 1:experiment_last_line]:
            line = line.split()
            degree_list.append(float(line[0]))
            I_experiment_list.append(float(line[1]))
    info["degree_list"] = degree_list

    I_experiment_list_normalized = []
    if info["normalization"] == "TOTAL":
        I_experiment_total = sum(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(
                (I_experiment_list[i]) / I_experiment_total
            )
    elif info["normalization"] == "MAX":
        I_experiment_max = max(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(I_experiment_list[i] / I_experiment_max)

    info["experiment"] = {}
    info["experiment"]["I"] = I_experiment_list
    info["experiment"]["I_normalized"] = I_experiment_list_normalized
    info["experiment"]["I_total"] = I_experiment_total
    return info


if __name__ == "__main__":
    ###### Parameter Settings ######
    parser = ArgumentParser()

    parser.add_argument("-d", "--dimension", type=int, required=True)

    parser.add_argument("-ll", "--llist", type=str, nargs="*", required=True)

    parser.add_argument("-sl", "--slist", type=str, nargs="*", required=True)

    parser.add_argument("-il", "--inilist", type=float, nargs="*", required=True)

    parser.add_argument("-unit_l", "--unit_list", type=float, nargs="*", required=True)

    parser.add_argument("-mi", "--minlist", type=float, nargs="*", required=True)

    parser.add_argument("-ma", "--maxlist", type=float, nargs="*", required=True)

    parser.add_argument(
        "-ini_scale_l", "--initial_scale_list", type=float, nargs="*", required=True
    )

    parser.add_argument(
        "-n",
        "--norm",
        type=str,
        default="TOTAL",
        choices=["TOTAL", "MAX"],
        help="(default: %(default)s)",
    )

    parser.add_argument(
        "-rf",
        "--rfactor",
        type=str,
        default="A",
        choices=["A", "B"],
        help="(default: %(default)s)",
    )

    parser.add_argument(
        "-ef", "--efirst", type=int, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-el", "--elast", type=int, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-cf", "--cfirst", type=int, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-cl", "--clast", type=int, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-dm", "--dmax", type=float, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-rn", "--rnumber", type=int, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-o", "--omega", type=float, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-xt", "--xtol", type=float, required=True, help="(default: %(default)s)"
    )

    parser.add_argument(
        "-ft", "--ftol", type=float, required=True, help="(default: %(default)s)"
    )
    parser.add_argument(
        "--sinput", type=str, default="surf.txt", help="(default: %(default)s)"
    )
    parser.add_argument(
        "--boutput", type=str, default="bulkP.b", help="(default: %(default)s)"
    )
    parser.add_argument(
        "--soutput", type=str, default="surf-bulkP.s", help="(default: %(default)s)"
    )

    args = parser.parse_args()

    main_dir = os.getcwd()
    Log_number = 0
    extra_data = False
    callback_list = []
    info = get_info(args)

    # Is it right ? arg.degree_max is ignored.
    info["degree_max"] = info["degree_list"][-1]
    dimension = info["dimension"]
    # Rerform bulk-calculation
    print("Perform bulk-calculation")
    os.system("%s/bulk.exe" % main_dir)
    # make initial simplex
    initial_simplex_list = []
    initial_list = info["initial_list"]
    initial_scale_list = info["initial_scale_list"]
    initial_simplex_list.append(initial_list)

    for index in range(dimension):
        initial_list2 = []
        for index2 in range(dimension):
            if index2 == index:
                initial_list2.append(initial_list[index2] + initial_scale_list[index2])
            else:
                initial_list2.append(initial_list[index2])
        initial_simplex_list.append(initial_list2)

    # fminsearch
    print("Perform optimization by fminsearch")
    [xopt, fopt, itera, funcalls, warnflag, allvecs] = fmin(
        f_calc,
        initial_list,
        args=(info,),
        xtol=info["xtol_value"],
        ftol=info["ftol_value"],
        retall=True,
        full_output=True,
        maxiter=10000,
        maxfun=100000,
        initial_simplex=initial_simplex_list,
    )
    # result = fmin(f, initial_list, maxiter = 500, maxfun = 10000)
    # print(result)

    extra_data = True
    info["Log_number"] = 0
    fx_for_simplex_list = []
    print("iteration:", itera)
    print("len(allvecs):", len(allvecs))
    for step in range(itera):
        print("step:", step)
        print("allvecs[step]:", allvecs[step])
        fx_for_simplex_list.append(f_calc(allvecs[step], info, extra_data))

    label_list = info["label_list"]
    with open("SimplexData.txt", "w") as file_SD:
        file_SD.write("#step")
        for index in range(dimension):
            file_SD.write(" %s" % label_list[index])
        file_SD.write(" R-factor\n")
        for step in range(itera):
            file_SD.write(str(step))
            for index in range(dimension):
                file_SD.write(" %f" % allvecs[step][index])
            file_SD.write(" %f\n" % fx_for_simplex_list[step])

    with open("History_FunctionCall.txt", "w") as file_callback:
        file_callback.write("#No")
        for index in range(dimension):
            file_callback.write(" %s" % label_list[index])
        file_callback.write("\n")
        for callback in callback_list:
            for index in range(dimension + 2):
                file_callback.write(str(callback[index]))
                if not index == dimension + 1:
                    file_callback.write(" ")
            file_callback.write("\n")

    if warnflag == 0:
        print("Optimization terminated successfully.")
    elif warnflag == 1:
        print("Warning: Maximum number of function evaluations made.")
    elif warnflag == 2:
        print("Warning: Maximum number of iterations reached.")

    print("Current function value:", fopt)
    print("Iterations:", itera)
    print("Function evaluations:", funcalls)
    print("Solution:")
    for index in range(dimension):
        print("%s =" % (label_list[index]), xopt[index])
