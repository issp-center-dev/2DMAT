from __future__ import division
from __future__ import absolute_import
from io import open
try:
    from mpi4py import MPI
    MPI_flag = True
except:
    MPI_flag = False
import numpy as np
#import matplotlib.pyplot as plt
import os
import shutil
import sys
from argparse import ArgumentParser

def main():
    ######Parameter Settings######
    parser = ArgumentParser()
    parser.add_argument(u'--dimension', type=int, default=2, help=u'(default: %(default)s)')
    parser.add_argument(u'--llist', type=unicode, nargs=u'*', default=[u"z1(Si)", u"z2(Si)"], help=u'(default: %(default)s)')
    parser.add_argument(u'--slist', type=unicode, nargs=u'*', default=[u"value_01", u"value_02"], help=u'(default: %(default)s)')
    parser.add_argument(u'--sinput', type=unicode, default=u'surf.txt', help=u'(default: %(default)s)')
    parser.add_argument(u'--boutput', type=unicode, default=u'bulkP.b', help=u'(default: %(default)s)')
    parser.add_argument(u'--soutput', type=unicode, default=u'surf-bulkP.s', help=u'(default: %(default)s)')
    parser.add_argument(u'--norm', type=unicode, default=u'TOTAL', choices=[u'TOTAL', u'MAX'], help=u'(default: %(default)s)')
    parser.add_argument(u'--rfactor', type=unicode, default=u'A', choices=[u'A', u'B'], help=u'(default: %(default)s)')
    parser.add_argument(u'--efirst', type=int, default=1, help=u'(default: %(default)s)')
    parser.add_argument(u'--elast', type=int, default=56, help=u'(default: %(default)s)')
    parser.add_argument(u'--cfirst', type=int, default=5, help=u'(default: %(default)s)')
    parser.add_argument(u'--clast', type=int, default=60, help=u'(default: %(default)s)')
    parser.add_argument(u'--dmax', type=float, default=6.0, help=u'(default: %(default)s)')
    parser.add_argument(u'--rnumber', type=int, default=8, help=u'(default: %(default)s)')
    parser.add_argument(u'--omega', type=float, default=0.5, help=u'(default: %(default)s)')
    args = parser.parse_args()

    dimension = args.dimension
    #Debug
    print("test")
    print(dimension)
    exit(0)
    if len(args.llist) != dimension:
        print u"Error: len(llist) is not equal to dimension"
        exit(1)
    if len(args.slist) != dimension:
        print u"Error: len(slist) is not equal to dimension"
        exit(1)
    label_list = args.llist
    string_list = args.slist
    surface_input_file = args.sinput
    bulk_output_file = args.boutput
    surface_output_file = args.soutput
    normalization = args.norm#"TOTAL" or "MAX"
    Rfactor = args.rfactor#"A":General or "B":Pendry
    experiment_first_line = args.efirst
    experiment_last_line = args.elast
    calculated_first_line = args.cfirst
    calculated_last_line = args.clast
    degree_max = args.dmax
    row_number = args.rnumber#row number of 00 spot in .s file
    omega = args.omega#half width of convolution
    ##############################

    ######define functions######
    def replace(fitted_x_list):
        file_input = open(u"template.txt", u"r")
        file_output = open(surface_input_file, u"w")
        for line in file_input:
            for index in xrange(dimension):
                if line.find(string_list[index]) != -1:
                    line = line.replace(string_list[index], fitted_x_list[index])
            file_output.write(line)
        file_input.close()
        file_output.close()

    def g(x):
        g = (0.939437 / omega) * np.exp(-2.77259 * (x ** 2.0 / omega ** 2.0))
        return g

    def f(x_list):
        Log_number = round(x_list[0])
        x_list = x_list[1:]
        fitted_x_list = []
        for index in xrange(dimension):
            if x_list[index] < 0:
                fitted_value = u"%.8f"%(x_list[index])
            else:
                fitted_value = u" " + u"%.8f"%(x_list[index])
            fitted_value = fitted_value[:len(string_list[index])]
            fitted_x_list.append(fitted_value)
        for index in xrange(dimension):
            print label_list[index], u"=", fitted_x_list[index]
        replace(fitted_x_list)
        folder_name = u"Log%08d"%Log_number
        os.mkdir(folder_name)
        shutil.copy(u"%s"%bulk_output_file,u"%s/%s"%(folder_name, bulk_output_file))
        shutil.copy(u"%s"%surface_input_file, u"%s/%s"%(folder_name, surface_input_file))
        os.chdir(folder_name)
        for time in xrange(100):
            print u"Perform surface-calculation"
            os.system(u"%s/surf.exe"%main_dir)
            NaN_exist = False
            file_check = open(u"%s"%surface_output_file, u"r")
            line_count = 0
            for line in file_check:
                line_count += 1
                if calculated_first_line <= line_count <= calculated_last_line:
                    if line.find(u"NaN") != -1:
                        NaN_exist = True
            file_check.close()
            if not NaN_exist:
                print u"RASS : %s does not have NaN."%surface_output_file
                break
            else:
                print u"WARNING : %s has NaN. Perform surface-calculation one more time."%surface_output_file
        I_calculated_list = []
        file_result = open(u"%s"%surface_output_file, u"r")
        line_count = 0
        for line in file_result:
            line_count += 1
            if calculated_first_line <= line_count <= calculated_last_line:
                line = line.replace(u",", u"")
                line = line.split()
                I_calculated_list.append(float(line[row_number -1]))
            if line_count == calculated_last_line:
                if round(float(line[0]), 1) == degree_max:
                    print u"PASS : degree_max = %s"%line[0]
                else:
                    print u"WARNING : degree_max = %s"%line[0]
        file_result.close()
        
        #####convolution#####
        convolution_I_calculated_list = []
        for index in xrange(len(I_calculated_list)):
            integral = 0.0
            for index2 in xrange(len(I_calculated_list)):
                integral += I_calculated_list[index2] * g(degree_list[index] - degree_list[index2]) * 0.1
            convolution_I_calculated_list.append(integral)
        if len(I_calculated_list) == len(convolution_I_calculated_list):
            print u"PASS : len(calculated_list)%d = len(convolution_I_calculated_list)%d"%(len(I_calculated_list), len(convolution_I_calculated_list))
        else:
            print u"WARNING : len(calculated_list)%d != len(convolution_I_calculated_list)%d"%(len(I_calculated_list), len(convolution_I_calculated_list))
        #####################

        convolution_I_calculated_list_normalized = []
        if normalization == u"TOTAL":
            I_calculated_total = sum(convolution_I_calculated_list)
            for i in xrange(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append((convolution_I_calculated_list[i])/I_calculated_total)
        elif normalization == u"MAX":
            I_calculated_max = max(convolution_I_calculated_list)
            for i in xrange(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(convolution_I_calculated_list[i]/I_calculated_max)
        if Rfactor == u"A":
            y1 = 0.0
            for i in xrange(len(degree_list)):
                y1 = y1+(I_experiment_list_normalized[i]-convolution_I_calculated_list_normalized[i])**2.0
            y = np.sqrt(y1)
        elif Rfactor == u"B":
            y1 = 0.0
            for i in xrange(len(degree_list)):
                y1 = y1+(I_experiment_list_normalized[i]-convolution_I_calculated_list_normalized[i])**2.0
            y2 = 0.0
            for i in xrange(len(degree_list)):
                y2 = y2+I_experiment_list_normalized[i]**2.0
            y3 = 0.0
            for i in xrange(len(degree_list)):
                y3 = y3+convolution_I_calculated_list_normalized[i]**2.0
            y = y1/(y2+y3)
        print u"R-factor =", y
        file_RC = open(u"RockingCurve.txt",u"w")
        file_RC.write(u"#")
        for index in xrange(dimension):
            file_RC.write(u"%s = %s"%(label_list[index], fitted_x_list[index]))
            if not index == dimension -1:
                file_RC.write(u" ")
        file_RC.write(u"\n")
        file_RC.write(u"#R-factor = %f"%y)
        file_RC.write(u"\n")
        if normalization == u"TOTAL":
            file_RC.write(u"#I_calculated_total=%f"%I_calculated_total)
            file_RC.write(u"\n")
            file_RC.write(u"#I_experiment_total=%f"%I_experiment_total)
        elif normalization == u"MAX":
            file_RC.write(u"#I_calculated_max=%f"%I_calculated_max)
            file_RC.write(u"\n")
            file_RC.write(u"#I_experiment_max=%f"%I_experiment_max)
        file_RC.write(u"\n")
        file_RC.write(u"#degree convolution_I_calculated I_experiment convolution_I_calculated(normalized) I_experiment(normalized) I_calculated")
        file_RC.write(u"\n")
        for index in xrange(len(degree_list)):
            file_RC.write(unicode(degree_list[index]))
            file_RC.write(u" ")
            file_RC.write(unicode(convolution_I_calculated_list[index]))
            file_RC.write(u" ")
            file_RC.write(unicode(I_experiment_list[index]))
            file_RC.write(u" ")
            file_RC.write(unicode(convolution_I_calculated_list_normalized[index]))
            file_RC.write(u" ")
            file_RC.write(unicode(I_experiment_list_normalized[index]))
            file_RC.write(u" ")
            file_RC.write(unicode(I_calculated_list[index]))
            file_RC.write(u"\n")
        file_RC.close()
        os.chdir(main_dir)
        return y
    ############################

    main_dir = os.getcwdu()

    #Read experiment-data
    print u"Read experiment.txt"
    degree_list = []
    I_experiment_list = []
    fp = open(u"experiment.txt",u"r")
    read = fp.readlines()
    count = 0
    for line in read:
        count = count+1
        if experiment_first_line <= count <= experiment_last_line:
            line = line.split()
            degree_list.append(float(line[0]))
            I_experiment_list.append(float(line[1]))
    fp.close()

    I_experiment_list_normalized = []
    if normalization == u"TOTAL":
        I_experiment_total = sum(I_experiment_list)
        for i in xrange(len(I_experiment_list)):
            I_experiment_list_normalized.append((I_experiment_list[i])/I_experiment_total)
    elif normalization == u"MAX":
        I_experiment_max = max(I_experiment_list)
        for i in xrange(len(I_experiment_list)):
            I_experiment_list_normalized.append(I_experiment_list[i]/I_experiment_max)

    #Rerform bulk-calculation
    print u"Perform bulk-calculation"
    os.system(u"%s/bulk.exe"%main_dir)

    #Make ColorMap
    print u"Read MeshData.txt"
    mesh_list = []
    file_MD = open(u"MeshData.txt", u"r")
    for line in file_MD:
        if line[0] == u"#":
           continue
        line = line.split()
        mesh = []
        for value in line:
            mesh.append(float(value))
        mesh_list.append(mesh)

    #print("check read mesh")
    #for mesh in mesh_list:
    #    print(mesh)

    print u"Make ColorMap"
    fx_list = []
    file_CM = open(u"ColorMap.txt", u"w")
    file_CM.write(u"#")
    for label in label_list:
        file_CM.write(u"%s "%label)
    file_CM.write(u"R-factor\n")
    iterations = len(mesh_list)
    iteration_count = 0
    for mesh in mesh_list:
        iteration_count += 1
        print u"Iteration : %d/%d"%(iteration_count, iterations)
        print u"mesh before:", mesh
        for value in mesh[1:]:
            file_CM.write(u"%f "%value)
        fx = f(mesh)
        fx_list.append(fx)
        file_CM.write(u"%f\n"%fx)
        print u"mesh after:", mesh
    fx_order = np.argsort(fx_list)
    minimum_point = []
    print u"mesh_list[fx_order[0]]:"
    print mesh_list[fx_order[0]]
    for index in xrange(1, dimension + 1):
        minimum_point.append(mesh_list[fx_order[0]][index])
    file_CM.write(u"#Minimum point :")
    for value in minimum_point:
        file_CM.write(u" %f"%value)
    file_CM.write(u"\n")
    file_CM.write(u"#R-factor : %f"%fx_list[fx_order[0]])
    file_CM.write(u"\n")
    file_CM.write(u"#see Log%d"%round(mesh_list[fx_order[0]][0]))
    file_CM.close()

rank = 0
size = 1
if MPI_flag:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
maindir2 = os.getcwdu()

if rank == 0:
    pieces = size
    lines = []
    file_input = open(u"MeshData.txt", u"r")
    for line in file_input:
        if not line[0] == u"#":
            lines.append(line)
    file_input.close()

    total = len(lines)
    elements = total // pieces

    for index in xrange(pieces):
        file_output = open(u"devided_MeshData%08d.txt"%(index), u"w")
        for index2 in xrange(elements):
            file_output.write(lines[index2])
        del lines[0:elements]
        if index == pieces - 1:
            for index3 in xrange(len(lines)):
                file_output.write(lines[index3])
        file_output.close()

    for i in xrange(pieces):
        sub_folder_name = u"mapper%08d"%(i)
        os.mkdir(sub_folder_name)
        for item in [u"bulk.exe", u"surf.exe", u"bulk.txt", u"template.txt", u"experiment.txt"]:
            shutil.copy(item,u"%s/%s"%(sub_folder_name, item))
        shutil.copy(u"devided_MeshData%08d.txt"%(i), u"%s/MeshData.txt"%(sub_folder_name))

if MPI_flag:
    comm.Barrier()

#sys.stdout = open(u"output_from_rank%08d.txt"%(rank), u"w")
print("test")
exit(0)
os.chdir(u"mapper%08d"%(rank))
main()

#sys.stdout.close()
#sys.stdout = sys.__stdout__

print u"complete main process : rank%08d/%08d"%(rank, size)

if MPI_flag:
    comm.Barrier()

if rank == 0:
    os.chdir(maindir2)
    all_data = []
    for i in xrange(size):
        file_input = open(u"mapper%08d/ColorMap.txt"%(i), u"r")
        lines = file_input.readlines()
        file_input.close()
        for line in lines:
            if line[0] == u"#":
                continue
            all_data.append(line)

    file_output = open(u"ColorMap.txt", u"w")
    for line in all_data:
        file_output.write(line)
    file_output.close()
    print u"complete"
