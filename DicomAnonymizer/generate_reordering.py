import os
import glob
import random

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

if __name__=="__main__":
    dataset_folder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    generate_reordering(dataset_folder)