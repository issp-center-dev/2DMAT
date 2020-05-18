from scipy.optimize import fmin
import numpy as np
import os
import shutil
from argparse import ArgumentParser

######Parameter Settings######
parser = ArgumentParser()

parser.add_argument('-d', '--dimension', 
                    type=int, 
                    required=True)

parser.add_argument('-ll', '--llist', 
                    type=str, 
                    nargs='*', 
                    required=True)

parser.add_argument('-sl', '--slist', 
                    type=str, 
                    nargs='*', 
                    required=True)

parser.add_argument('-il','--inilist', 
                    type=float, 
                    nargs='*',
                    required=True)

parser.add_argument('-unit_l','--unit_list', 
                    type=float, 
                    nargs='*',
                    required=True)

parser.add_argument('-mi','--minlist',
                    type=float,
                    nargs='*',
                    required=True)

parser.add_argument('-ma','--maxlist',
                    type=float,
                    nargs='*', 
                    required=True)

parser.add_argument('-ini_scale_l','--initial_scale_list',
                    type=float,
                    nargs='*', 
                    required=True)

parser.add_argument('-n','--norm',
                    type=str,
                    default='TOTAL',
                    choices=['TOTAL', 'MAX'],
                    help='(default: %(default)s)')

parser.add_argument('-rf','--rfactor',
                    type=str,
                    default='A',
                    choices=['A', 'B'],
                    help='(default: %(default)s)')

parser.add_argument('-ef','--efirst',
                    type=int,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-el','--elast',
                    type=int,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-cf','--cfirst',
                    type=int,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-cl','--clast',
                    type=int,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-dm','--dmax',
                    type=float,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-rn','--rnumber',
                    type=int,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-o','--omega',
                    type=float,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-xt','--xtol',
                    type=float,
                    required=True,
                    help='(default: %(default)s)')

parser.add_argument('-ft','--ftol',
                    type=float,
                    required=True,
                    help='(default: %(default)s)')

args = parser.parse_args()

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
label_list = args.llist
string_list = args.slist
initial_list = args.inilist
unit_list = args.unit_list
min_list = args.minlist
max_list = args.maxlist
initial_scale_list = args.initial_scale_list
surface_input_file = "surf.txt"
bulk_output_file = "bulkP.b"
surface_output_file = "surf-bulkP.s"
normalization = args.norm#"TOTAL" or "MAX"
Rfactor = args.rfactor#"A":General or "B":Pendry
experiment_first_line = args.efirst
experiment_last_line = args.elast
calculated_first_line = args.cfirst
calculated_last_line = args.clast
degree_max = args.dmax
row_number = args.rnumber#row number of 00 spot in .s file
omega = args.omega#half width of convolution
xtol_value = args.xtol
ftol_value = args.ftol
##############################

######Parameter Settings######
#dimension = 10
#label_list = ["z2(Si1)", "z3(O2)", "z4(Si2)", "z5(N)", "z6(Si3)", "z7(C1)", "z8(C2)", "z9(Si4)", "z10(Si5)", "z11(C3)"]
#string_list = ['value_02', 'value_03', 'value_04', 'value_05', 'value_06', 'value_07', 'value_08', 'value_09', 'value_10', 'value_11']
#initial_list = [8.67, 7.04, 5.45, 4.83, 3.11, 2.63, 2.44, 0.67, 0.59, 0.00]
#unit_list = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
#min_list = [-100.0, -100.0, -100.0, -100.0, -100.0, -100.0, -100.0, -100.0, -100.0, -100.0]
#max_list = [ 100.0,  100.0,  100.0,  100.0,  100.0,  100.0,  100.0,  100.0,  100.0,  100.0]
#initial_scale_list = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
#surface_input_file = "surf.txt"
#bulk_output_file = "bulkP.b"
#surface_output_file = "surf-bulkP.s"
#normalization = "TOTAL"#"TOTAL" or "MAX"
#Rfactor = "A"#"A":General or "B":Pendry
#experiment_first_line = 1
#experiment_last_line = 61
#calculated_first_line = 5
#calculated_last_line = 65
#row_number = 2#.sファイルの何列目が00スポットか
#omega = 0.5#コンボリューションの半値幅
##############################

######define functions######
def replace(fitted_x_list):
    file_input = open("template.txt", "r")
    file_output = open(surface_input_file, "w")
    for line in file_input:
        for index in range(dimension):
            if line.find(string_list[index]) != -1:
                line = line.replace(string_list[index], fitted_x_list[index])
        file_output.write(line)
    file_input.close()
    file_output.close()

def g(x):
    g = (0.939437 / omega) * np.exp(-2.77259 * (x ** 2.0 / omega ** 2.0))
    return g

def f(x_list):
    #####judge value#####
    out_of_range = False
    for index in range(dimension):
        if x_list[index] < min_list[index] or x_list[index] > max_list[index]:
            print("Warning: %s = %f is out of range(min%f ~ max%f)."%(label_list[index], x_list[index], min_list[index], max_list[index]))
            out_of_range = True
    #####unit modify#####
    new_x_list = []
    for index in range(dimension):
        new_x_list.append(x_list[index] / unit_list[index])
    x_list = new_x_list
    #####################
    if out_of_range:
        y = 100.0
    else:
        global Log_number
        global extra_data
        Log_number += 1
        fitted_x_list = []
        for index in range(dimension):
            if x_list[index] < 0:
                fitted_value = "%.8f"%(x_list[index])
            else:
                fitted_value = " " + "%.8f"%(x_list[index])
            fitted_value = fitted_value[:len(string_list[index])]
            fitted_x_list.append(fitted_value)
        for index in range(dimension):
            print(label_list[index], "=", fitted_x_list[index])
        replace(fitted_x_list)
        if extra_data:
            folder_name = "Extra_Log%08d"%Log_number
        else:
            folder_name = "Log%08d"%Log_number
        os.mkdir(folder_name)
        shutil.copy("%s"%bulk_output_file,"%s/%s"%(folder_name, bulk_output_file))
        shutil.copy("%s"%surface_input_file, "%s/%s"%(folder_name, surface_input_file))
        os.chdir(folder_name)
        for time in range(100):
            print("Perform surface-calculation")
            os.system("%s/surf.exe"%main_dir)
            NaN_exist = False
            file_check = open("%s"%surface_output_file, "r")
            line_count = 0
            for line in file_check:
                line_count += 1
                if calculated_first_line <= line_count <= calculated_last_line:
                    if line.find("NaN") != -1:
                        NaN_exist = True
            file_check.close()
            if not NaN_exist:
                print("PASS : %s does not have NaN."%surface_output_file)
                break
            else:
                print("WARNING : %s has NaN. Perform surface-calculation one more time."%surface_output_file)
        I_calculated_list = []
        file_result = open("%s"%surface_output_file, "r")
        line_count = 0
        for line in file_result:
            line_count += 1
            if calculated_first_line <= line_count <= calculated_last_line:
                line = line.replace(",", "")
                line = line.split()
                I_calculated_list.append(float(line[row_number - 1]))
            if line_count == calculated_last_line:
                if round(float(line[0]), 1) == degree_max:
                    print("PASS : degree_max_exp = %s, degree_max_cal = %s"%(degree_max, line[0]))
                else:
                    print("WARNING : degree_max_exp = %s, degree_max_cal = %s"%(degree_max, line[0]))
        file_result.close()
        
        #####convolution#####
        convolution_I_calculated_list = []
        for index in range(len(I_calculated_list)):
            integral = 0.0
            for index2 in range(len(I_calculated_list)):
                integral += I_calculated_list[index2] * g(degree_list[index] - degree_list[index2]) * 0.1
            convolution_I_calculated_list.append(integral)
        if len(I_calculated_list) == len(convolution_I_calculated_list):
            print("PASS : len(calculated_list)%d = len(convolution_I_calculated_list)%d"%(len(I_calculated_list), len(convolution_I_calculated_list)))
        else:
            print("WARNING : len(calculated_list)%d != len(convolution_I_calculated_list)%d"%(len(I_calculated_list), len(convolution_I_calculated_list)))
        #####################

        convolution_I_calculated_list_normalized = []
        if normalization == "TOTAL":
            I_calculated_total = sum(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append((convolution_I_calculated_list[i])/I_calculated_total)
        elif normalization == "MAX":
            I_calculated_max = max(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(convolution_I_calculated_list[i]/I_calculated_max)
        if Rfactor == "A":
            y1 = 0.0
            for i in range(len(degree_list)):
                y1 = y1+(I_experiment_list_normalized[i]-convolution_I_calculated_list_normalized[i])**2.0
            y = np.sqrt(y1)
        elif Rfactor == "B":
            y1 = 0.0
            for i in range(len(degree_list)):
                y1 = y1+(I_experiment_list_normalized[i]-convolution_I_calculated_list_normalized[i])**2.0
            y2 = 0.0
            for i in range(len(degree_list)):
                y2 = y2+I_experiment_list_normalized[i]**2.0
            y3 = 0.0
            for i in range(len(degree_list)):
                y3 = y3+convolution_I_calculated_list_normalized[i]**2.0
            y = y1/(y2+y3)
        print("R-factor =", y)
        file_RC = open("RockingCurve.txt","w")
        file_RC.write("#")
        for index in range(dimension):
            file_RC.write("%s = %s"%(label_list[index], fitted_x_list[index]))
            if not index == dimension -1:
                file_RC.write(" ")
        file_RC.write("\n")
        file_RC.write("#R-factor = %f"%y)
        file_RC.write("\n")
        if normalization == "TOTAL":
            file_RC.write("#I_calculated_total=%f"%I_calculated_total)
            file_RC.write("\n")
            file_RC.write("#I_experiment_total=%f"%I_experiment_total)
        elif normalization == "MAX":
            file_RC.write("#I_calculated_max=%f"%I_calculated_max)
            file_RC.write("\n")
            file_RC.write("#I_experiment_max=%f"%I_experiment_max)
        file_RC.write("\n")
        file_RC.write("#degree convolution_I_calculated I_experiment convolution_I_calculated(normalized) I_experiment(normalized) I_calculated")
        file_RC.write("\n")
        for index in range(len(degree_list)):
            file_RC.write(str(degree_list[index]))
            file_RC.write(" ")
            file_RC.write(str(convolution_I_calculated_list[index]))
            file_RC.write(" ")
            file_RC.write(str(I_experiment_list[index]))
            file_RC.write(" ")
            file_RC.write(str(convolution_I_calculated_list_normalized[index]))
            file_RC.write(" ")
            file_RC.write(str(I_experiment_list_normalized[index]))
            file_RC.write(" ")
            file_RC.write(str(I_calculated_list[index]))
            file_RC.write("\n")
        file_RC.close()
        os.chdir(main_dir)
        if not extra_data:
            callback = [Log_number]
            for index in range(dimension):
                callback.append(x_list[index])
            callback.append(y)
            callback_list.append(callback)
    return y
    
############################

main_dir = os.getcwd()
Log_number = 0
extra_data = False
callback_list = []

#Read experiment-data
print("Read experiment.txt")
degree_list = []
I_experiment_list = []
fp = open("experiment.txt","r")
read = fp.readlines()
count = 0
for line in read:
    count = count+1
    if experiment_first_line <= count <= experiment_last_line:
        line = line.split()
        degree_list.append(float(line[0]))
        I_experiment_list.append(float(line[1]))
fp.close()
degree_max = degree_list[-1]

I_experiment_list_normalized = []
if normalization == "TOTAL":
    I_experiment_total = sum(I_experiment_list)
    for i in range(len(I_experiment_list)):
        I_experiment_list_normalized.append((I_experiment_list[i])/I_experiment_total)
elif normalization == "MAX":
    I_experiment_max = max(I_experiment_list)
    for i in range(len(I_experiment_list)):
        I_experiment_list_normalized.append(I_experiment_list[i]/I_experiment_max)

#Rerform bulk-calculation
print("Perform bulk-calculation")
os.system("%s/bulk.exe"%main_dir)

#make initial simplex
initial_simplex_list = []
initial_simplex_list.append(initial_list)

for index in range(dimension):
    initial_list2 = []
    for index2 in range(dimension):
        if index2 == index:
            initial_list2.append(initial_list[index2] + initial_scale_list[index2])
        else:
            initial_list2.append(initial_list[index2])
    initial_simplex_list.append(initial_list2)

#fminsearch
print("Perform optimization by fminsearch")
[xopt, fopt, itera, funcalls, warnflag, allvecs] = fmin(f, initial_list, xtol=xtol_value, ftol=ftol_value, retall = True, full_output = True, maxiter = 10000, maxfun = 100000, initial_simplex = initial_simplex_list)
#result = fmin(f, initial_list, maxiter = 500, maxfun = 10000)
#print(result)

extra_data = True
Log_number = 0
fx_for_simplex_list = []
print("itera:", itera)
print("len(allvecs):", len(allvecs))
for step in range(itera):
    print("step:", step)
    print("allvecs[step]:", allvecs[step])
    fx_for_simplex_list.append(f(allvecs[step]))

file_SD = open("SimplexData.txt", "w")
file_SD.write("#step")
for index in range(dimension):
    file_SD.write(" %s"%label_list[index])
file_SD.write(" R-factor")
file_SD.write("\n")
for step in range(itera):
    file_SD.write(str(step))
    for index in range(dimension):
        file_SD.write(" %f"%allvecs[step][index])
    file_SD.write(" %f"%fx_for_simplex_list[step])
    file_SD.write("\n")
file_SD.close()

file_callback = open("History_FunctionCall.txt","w")
file_callback.write("#No")
for index in range(dimension):
    file_callback.write(" %s"%label_list[index])
file_callback.write("\n")
for callback in callback_list:
    for index in range(dimension + 2):
        file_callback.write(str(callback[index]))
        if not index == dimension + 1:
            file_callback.write(" ")
    file_callback.write("\n")
file_callback.close()

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
    print("%s ="%(label_list[index]), xopt[index])
