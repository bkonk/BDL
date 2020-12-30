import os
import glob
import random
import numpy as np
import re

def generate_reordering(dataset_folder):
    exam_folder_list = glob.glob(dataset_folder+"/*")
    exam_id_list = []
    for exam_folder in exam_folder_list:
        exam_id = os.path.basename(exam_folder)
        exam_id_list.append(exam_id)
    random.shuffle(exam_id_list)
    # generate config format exam_id new_id
    for i in range(len(exam_id_list)):
        print("{} = {:03d}".format(exam_id_list[i],i))

def generate_cdid_reordering(path_file):
    pass

def task_1():
    '''
    Generate the mapping between the Original Patient/Exam ID to new ID
    '''
    dataset_folder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    generate_reordering(dataset_folder)


def task_2():
    '''
    Rename Lrm_****_assess --> Lrm_****_cdid
    '''
    path_file = '/mnt/sdc/dataset/tmp/file_fullpath.txt'
    fullpath = np.loadtxt(path_file,dtype=np.str,delimiter='\n')
    mapping = {}
    for path in fullpath:
        m = re.search('Lrm_[0-9]{4}_assess',path)
        if not m:
            print(path)
        else:
            mapping[m.group(0)] = m.group(0)[:-6]+'cdid'

    for old_name in mapping:
        print('{0} = {1}'.format(old_name,mapping[old_name]))

if __name__=="__main__":
    task_2()