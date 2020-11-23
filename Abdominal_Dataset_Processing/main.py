import os
import glob
import pickle
import pydicom
import json

def cal_stat():
    '''
    Calculate Dataset Statistics
    11/18/2020
    Zhe Zhu
    '''
    anonymized_dataset_folder = '/mnt/sdc/dataset/Duke_Abdominal_Anonymized'
    dataset_info = {}
    dataset_info_file = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/dataset_info.pickle'
    patient_folder_list = glob.glob(anonymized_dataset_folder+'/*')
    for patient_folder in patient_folder_list:
        patient_id = os.path.basename(patient_folder)
        dataset_info[patient_id] = {}
        sequence_folder_list = glob.glob(patient_folder+'/*')
        for sequence_folder in sequence_folder_list:
            sequence_id = os.path.basename(sequence_folder)
            dicom_file_list = glob.glob(sequence_folder+'/*')
            dicom_file_num = len(dicom_file_list)
            dataset_info[patient_id][sequence_id] = dicom_file_num
    # find out empty folders first
    for pid in dataset_info:
        for sid in dataset_info[pid]:
            if dataset_info[pid][sid] == 0:
                print(pid,sid)

    # dataset statistics
    patient_num = 0
    volume_num = 0
    slice_num = 0

    patient_num = len(dataset_info)
    for pid in dataset_info:
        volume_num += len(dataset_info[pid])
        for sid in dataset_info[pid]:
            slice_num += dataset_info[pid][sid]

    print("Patient Num: {0}".format(patient_num))
    print("Volume Num: {0}".format(volume_num))
    print("Slice Num: {0}".format(slice_num))

    with open(dataset_info_file,'wb') as f:
        pickle.dump(dataset_info,f)
    print("Dataset_info pickled")

def cal_pid_mapping():
    dataset_folder = '/mnt/sdc/dataset/Duke_Abdominal_Anonymized'
    pid_map_txt = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/pid_map.txt'
    pid_map_pickle = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/pid_map.pickle'
    pid_map_json = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/pid_map.json'

    pid_map = {}

    patient_folder_list = glob.glob(dataset_folder+'/*')
    for patient_folder in patient_folder_list:
        old_patient_id = os.path.basename(patient_folder)
        sequence_folder_list = glob.glob(patient_folder+'/*')
        for sequence_folder in sequence_folder_list:
            sequence_id = os.path.basename(sequence_folder)
            dicom_file_list = glob.glob(sequence_folder+'/*')
            for dicom_file in dicom_file_list:
                dcm = pydicom.dcmread(dicom_file)
                new_patient_id = dcm.PatientName
                if old_patient_id not in pid_map:
                    pid_map[old_patient_id] = new_patient_id.family_name
                else:
                    if pid_map[old_patient_id] != new_patient_id:
                        print("ERROR {} {} {}".format(old_patient_id,sequence_id,dicom_file))

    with open(pid_map_pickle,'wb') as f:
        pickle.dump(pid_map,f)
    with open(pid_map_json,'w') as f:
        json.dump(pid_map,f)
    with open(pid_map_txt,'w') as f:
        for old_pid in pid_map:
            f.write(old_pid+' '+pid_map[old_pid]+'\n')


def task_1():
    '''
    Dataset stats
    Zhe Zhu
    2020/11/18
    '''
    print("Task 1, calculate dataset statistics")
    cal_stat()

def task_2():
    '''
    Get the old_patient_id new_patient_id map
    Zhe Zhu
    2020/11/18
    '''
    print("Task 2, calculate the old/new patient_id mapping")
    cal_pid_mapping()

def task_3():
    '''
    check if there are two pid that are the same
    Zhe Zhu,2020/11/18
    '''
    pid_map_pickle = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/pid_map.pickle'
    with open(pid_map_pickle,'rb') as f:
        pid_map = pickle.load(f)
    patient_num = len(pid_map)
    pid_set = {}
    for old_pid in pid_map:
        pid_set[pid_map[old_pid]] = 1
    pid_num = len(pid_set)
    print("Patient No. : {}".format(patient_num))
    print("PID No. : {}".format(pid_num))

def main():
    #task_1()
    #task_2()
    task_3()

if __name__ == "__main__":
    main()