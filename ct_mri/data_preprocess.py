import os
import shutil
import glob
import zipfile
import pickle
import numpy as np
import ct_mri.roi as roi
import time
import re

def task_1():
    '''
    Move the data into a folder where folder name doesn't contain space
    Zhe Zhu, 2020/05/01
    '''
    source_data_folder = '/mnt/sdc/Liver/Liver segmentation AI input data'
    target_data_folder = '/mnt/sdc/Liver/segmentation_data'

    series_folder_list = glob.glob(source_data_folder+'/*')
    for series_folder in series_folder_list:
        series_name = os.path.basename(series_folder)
        series_name = series_name[series_name.find('- ')+2:]
        target_folder = os.path.join(target_data_folder,series_name)
        shutil.move(series_folder,target_folder)
    print('Move from {0} to {1}'.format(source_data_folder,target_data_folder))

def task_2():
    '''
    Print all the zip files
    Zhe Zhu, 2020/05/01
    '''
    folder = '/mnt/sdc/Liver/segmentation_data'
    series_folder_list = glob.glob(folder+'/*')
    for series_folder in series_folder_list:
        zip_file_list = glob.glob(series_folder+'/*')
        for zip_file in zip_file_list:
            print(zip_file)
def task_3():
    '''Unzip all the files'''
    folder = '/mnt/sdc/Liver/segmentation_data'
    series_folder_list = glob.glob(folder + '/*')
    for series_folder in series_folder_list:
        zip_file_list = glob.glob(series_folder + '/*')
        for zip_file in zip_file_list:
            zip_file_name = os.path.basename(zip_file)
            name_abbr = zip_file_name[zip_file_name.rfind('- ')+2:]
            name_abbr = name_abbr.replace(' ','_')
            name_abbr = name_abbr[:-4]
            tgt_folder = os.path.join(os.path.dirname(zip_file),name_abbr)
            with zipfile.ZipFile(zip_file,'r') as zfile:
                zfile.extractall(tgt_folder)
            print(zip_file)

def task_4():
    '''
    Delete all __MACOSX folders
    Zhe Zhu,2020/05/04
    '''
    folder = '/mnt/sdc/Liver/segmentation_data/'
    for dirpath,dirnames,filenames in os.walk(folder):
        for dirname in dirnames:
            if dirname == "__MACOSX":
                shutil.rmtree(os.path.join(dirpath,dirname))

def task_5():
    '''
    Remove all .DS_Store files
    Zhe Zhu,2020/05/06
    '''
    folder = '/mnt/sdc/Liver/segmentation_data/'
    count = 0
    for dirpath,dirnames,filenames in os.walk(folder):
        for filename in filenames:
            if filename == ".DS_Store":
                os.remove(os.path.join(dirpath,filename))
                count += 1
    print('{0} .DS_Store file deleted'.format(count))
def task_6():
    '''
    Move the data into a new folder for further process (remove folders containing spaces in the name)
    Zhe Zhu, 2020/05/06
    '''
    source_folder = '/mnt/sdc/Liver/segmentation_data/'
    target_folder = '/mnt/sdc/Liver/segmentation_processed/'
    for dirpath, dirnames, filenames in os.walk(source_folder):
        if len(filenames) == 3:
            dir_hlist = dirpath.split('/')
            series_name = dir_hlist[5]
            target_series_folder = os.path.join(target_folder,series_name)
            if not os.path.exists(target_folder):
                os.mkdir(target_series_folder)
            patient_id = dir_hlist[-1]
            patient_folder = os.path.join(target_series_folder,patient_id)
            if not os.path.exists(patient_folder):
                os.makedirs(patient_folder)
            for filename in filenames:
                source_file = os.path.join(dirpath,filename)
                target_file = os.path.join(patient_folder,filename)
                if not os.path.exists(target_file):
                    shutil.copyfile(source_file,target_file)

def task_7():
    '''
    Unzip all the dicom files
    Zhe Zhu, 2020/05/06
    Updated on 2020/06/30: save the log for dataset statistics
    '''
    dataset_folder = '/mnt/sdc/Liver/segmentation_processed/'
    log_folder = '/mnt/sdc/Liver/dataset_log'
    dataset_info_file = os.path.join(log_folder,'dataset_info.txt')
    missing_info_file = os.path.join(log_folder,'missing_file.txt')

    dataset_info_dict = {}
    missing_info_list = []

    series_folder_list = glob.glob(dataset_folder+'/*')
    for series_folder in series_folder_list:
        series_name = os.path.basename(series_folder)
        dataset_info_dict[series_name] = {}
        patient_folder_list = glob.glob(series_folder+'/*')
        for patient_folder in patient_folder_list:
            patient_id = os.path.basename(patient_folder)
            dataset_info_dict[series_name][patient_id] = {}

            dicom_zip_file_list = glob.glob(patient_folder+'/*.zip')
            target_folder = os.path.join(patient_folder,'dicoms')
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            if not dicom_zip_file_list:
                missing_info_list.append(patient_folder)
                print("NO ZIP FILE! {0}".format(patient_folder))
            else:
                with zipfile.ZipFile(dicom_zip_file_list[0],'r') as zfile:
                    #print('Upzipping '+dicom_zip_file_list[0])
                    zfile.extractall(target_folder)

                    mac_folder = os.path.join(target_folder,'__MACOSX')
                    if os.path.exists(mac_folder):
                        #print('removing {}'.format(mac_folder))
                        shutil.rmtree(mac_folder)

                    # find the dicoms, may exist deep
                    b_no_dicoms = True
                    for root, dirs, files in os.walk(target_folder):
                        if files:
                            b_no_dicoms = False
                            dataset_info_dict[series_name][patient_id]['dicom_file_list'] = files
                            dataset_info_dict[series_name][patient_id]['root'] = root
                    if b_no_dicoms:
                        print('NO DICOM FILES {}'.format(target_folder))
                        missing_info_list.append(patient_folder)

    with open(dataset_info_file,'wb') as f:
        pickle.dump(dataset_info_dict,f)
    print('dataset info saved!')
    with open(missing_info_file,'wb') as f:
        pickle.dump(missing_info_list,f)
    print('missing info saved!')

def task_8():
    '''
    Use pickle protocol 2 instead of 3
    Zhe Zhu, 2020/07/01
    '''
    info_file_src = '/mnt/sdc/Liver/dataset_log/dataset_info.txt'
    mising_file_src = '/mnt/sdc/Liver/dataset_log/missing_file.txt'

    info_file_tgt = '/mnt/sdc/Liver/dataset_log/dataset_info_2.txt'
    missing_file_tgt = '/mnt/sdc/Liver/dataset_log/missing_file_2.txt'

    with open(info_file_src,'rb') as f:
        info = pickle.load(f)
    with open(info_file_tgt,'wb') as f:
        pickle.dump(info,f,protocol=2)

    with open(mising_file_src,'rb') as f:
        missing = pickle.load(f)
    with open(missing_file_tgt,'wb') as f:
        pickle.dump(missing,f,protocol=2)

    print('Convertsion finished!')

def task_9():
    '''Test ROI Extraction'''
    print('Task 9 here')

    xml_file = '/mnt/sdc/Liver/segmentation_processed/ctarterial/LRML_0038_CTarterial/LRML_0038_CTarterial.xml'
    dicom_folder = '/mnt/sdc/Liver/segmentation_processed/ctarterial/LRML_0038_CTarterial/dicoms/LRML_0038_CTarterial_DICOMs/Abdomen_11_Cirrhosis_Ap_(Adult)_AA19275/BODYAXW_5.0_I31f_2'
    newdim = np.array((512,512))

    dicom_files = glob.glob(dicom_folder+'/*')

    img_vol,mask_data = roi.GetImageMaskDataOri(xml_file,dicom_files)
    print(np.max(img_vol))
    print(np.max(mask_data))
    print(img_vol.shape)
    print(mask_data.shape)
def task_10():
    '''
    Test the img & mask write func
    Zhe Zhu, 2020/07/12
    '''
    print("Task 10")
    xml_file = '/mnt/sdc/Liver/segmentation_processed/ctarterial/LRML_0038_CTarterial/LRML_0038_CTarterial.xml'
    dicom_folder = '/mnt/sdc/Liver/segmentation_processed/ctarterial/LRML_0038_CTarterial/dicoms/LRML_0038_CTarterial_DICOMs/Abdomen_11_Cirrhosis_Ap_(Adult)_AA19275/BODYAXW_5.0_I31f_2'
    newdim = np.array((512, 512))

    dicom_files = glob.glob(dicom_folder + '/*')
    output_folder = '/mnt/sdc/Liver/tmp/20200712'
    roi.ExtractImgAndMask(xml_file=xml_file,dicom_file_list=dicom_files,
                          output_folder=output_folder)

def task_11():
    '''
    Process the whole segmentation dataset
    Zhe Zhu, 2020/07/12
    '''
    dataset_folder = '/mnt/sdc/Liver/segmentation_processed'
    dataset_info_file = '/mnt/sdc/Liver/dataset_log/dataset_info.txt'

    log_file = '/mnt/sdc/Liver/dataset_log/issues.txt'
    issues_list = []

    dataset_output_folder = '/mnt/sdc/Liver/dataset/v1'

    with open(dataset_info_file,'rb') as f:
        dataset_info = pickle.load(f)




    count = 0
    for series_id in dataset_info:
        start = time.time()
        print("Processing {}".format(series_id))
        output_series_folder = os.path.join(dataset_output_folder,series_id)
        if not os.path.exists(output_series_folder):
            os.makedirs(output_series_folder)
        series_info = dataset_info[series_id]
        for patient_id in series_info:

            if not series_info[patient_id]:
                print("Empty {0} {1}".format(series_id,patient_id))
                continue
            dicom_name_list = series_info[patient_id]['dicom_file_list']
            dicom_name_list.sort()

            dicom_folder = series_info[patient_id]['root']
            dicom_file_list = [os.path.join(dicom_folder,dicom_name) for dicom_name in dicom_name_list]

            patient_folder = os.path.join(dataset_folder,series_id,patient_id)


            xml_file_list = glob.glob(patient_folder+'/*.xml')
            if not xml_file_list:
                err_msg = series_id+' '+patient_id+' '+'no xml file'
                issues_list.append(err_msg)
                print(err_msg)
                continue
            xml_file = xml_file_list[0]

            print('Processing {0} {1}'.format(patient_folder,count))
            output_patient_folder = os.path.join(output_series_folder, patient_id)
            if not os.path.exists(output_patient_folder):
                os.makedirs(output_patient_folder)
            else:
                continue
            try:
                roi.ExtractImgAndMask(xml_file=xml_file,
                                dicom_file_list=dicom_file_list,
                                output_folder=output_patient_folder)
            except TypeError as te:
                err_msg = series_id+' '+patient_id+' '+str(te)
                issues_list.append(err_msg)
                print(err_msg)
            except IndexError as ie:
                err_msg = series_id + ' ' + patient_id + ' ' + str(ie)
                issues_list.append(err_msg)
                print(err_msg)
            except AttributeError as ae:
                err_msg = series_id + ' ' + patient_id + ' ' + str(ae)
                issues_list.append(err_msg)
                print(err_msg)
            except Exception as be:
                err_msg = series_id + ' ' + patient_id + ' ' + str(be)
                issues_list.append(err_msg)
                print(err_msg)
            count += 1
        print("Time elapsed {0}".format(time.time()-start))
    with open(log_file,'w') as f:
        pickle.dump(issues_list,f)

def task_12():
    '''
    Deal with patient id
    Save the dataset to patient_id/series_name/data
    Zhe Zhu, 2020/07/17
    '''
    pattern_1 = r'LRML_([0-9]{4})_.*'
    pattern_2 = r'MAD01_([0-9]{4})S([0-9]{3})_.*'
    pattern_3 = r'JKB01_([0-9]{3})_([0-9]{2}).*'
    pattern_4 = r'NGM01_([0-9]{3})_([0-9]{2}).*'
    pattern_5 = r'NGM03_([0-9]{5})_.*'
    pattern_6 = r'NSTx1_([0-9]{2})_([0-9]{3})_.*'
    pattern_7 = r'NGM02_([0-9]{3})_([0-9]{3})_.*'
    pattern_8 = r'JKB01_([0-9]{3})A_([0-9]{2})_.*'
    dataset_info_file = '/mnt/sdc/Liver/dataset_log/dataset_info.txt'

    v1_folder = '/mnt/sdc/Liver/dataset/v1'
    output_folder = '/mnt/sdc/Liver/dataset/v2'

    with open(dataset_info_file, 'rb') as f:
        dataset_info = pickle.load(f)

    for series_name in dataset_info:
        series_info = dataset_info[series_name]
        for patient_id in series_info:
            match_1 = re.match(pattern_1,patient_id)
            match_2 = re.match(pattern_2,patient_id)
            match_3 = re.match(pattern_3,patient_id)
            match_4 = re.match(pattern_4,patient_id)
            match_5 = re.match(pattern_5,patient_id)
            match_6 = re.match(pattern_6,patient_id)
            match_7 = re.match(pattern_7,patient_id)
            match_8 = re.match(pattern_8,patient_id)
            if match_1:
                unique_id = 'LRML_'+match_1.group(1)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_2:
                unique_id = 'MAD01_'+match_2.group(1)+'_'+match_2.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_3:
                unique_id = 'JKB01_'+match_3.group(1)+'_'+match_3.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_4:
                unique_id = 'NGM01_'+match_4.group(1)+'_'+match_4.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_5:
                unique_id = 'NGM03_'+match_5.group(1)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_6:
                unique_id = 'NSTx1_'+match_6.group(1)+'_'+match_6.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_7:
                unique_id = 'NGM02_'+match_7.group(1)+'_'+match_7.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)
            if match_8:
                unique_id = 'JKB01_'+match_8.group(1)+'_'+match_8.group(2)
                output_patient_folder = os.path.join(output_folder,unique_id)
                if not os.path.exists(output_patient_folder):
                    os.makedirs(output_patient_folder)

            output_series_folder = os.path.join(output_patient_folder,series_name)
            if not os.path.exists(output_series_folder):
                os.makedirs(output_series_folder)

            v1_series_folder = os.path.join(v1_folder,series_name,patient_id)
            # copy img
            tgt_img_folder = os.path.join(output_series_folder,'img')
            if not os.path.exists(tgt_img_folder):
                os.makedirs(tgt_img_folder)
            tgt_mask_folder = os.path.join(output_series_folder,'mask')
            if not os.path.exists(tgt_mask_folder):
                os.makedirs(tgt_mask_folder)

            img_file_list = glob.glob(v1_series_folder+'/img/*')
            for img_file in img_file_list:
                img_file_name = os.path.basename(img_file)
                tgt_img_file = os.path.join(tgt_img_folder,img_file_name)
                shutil.copyfile(img_file,tgt_img_file)

            mask_file_list = glob.glob(v1_series_folder+'/mask/*')
            for mask_file in mask_file_list:
                mask_file_name = os.path.basename(mask_file)
                tgt_mask_file = os.path.join(tgt_mask_folder,mask_file_name)
                shutil.copyfile(mask_file,tgt_mask_file)


def task_13():
    '''
    split train and test
    Zhe Zhu, 2020/07/19
    '''
    # 7 different patterns, match separately
    pattern_1 = r'LRML_.*'
    pattern_2 = r'MAD01_.*'
    pattern_3 = r'JKB01_.*'
    pattern_4 = r'NGM01_.*'
    pattern_5 = r'NGM03_.*'
    pattern_6 = r'NSTx1_.*'
    pattern_7 = r'NGM02_.*'
    pattern_list = [pattern_1,pattern_2,pattern_3,pattern_4,
                    pattern_5,pattern_6,pattern_7]

    # split ratio
    train_rate = 0.8

    #
    train_patient_list = []
    val_patient_list = []

    # 17 different series
    series_list = ['ctarterial','ctdelay','ctportal','ctpre','dynarterial','dyndelay',
                   'dynhbp','dynportal','dynpre','dyntransitional','fat','opposed',
                   'PDWF','SSFSE','SSFSEfs','t1nfs','t2fse']

    train_stat = {}
    val_stat = {}

    for series_id in series_list:
        train_stat[series_id] = 0
        val_stat[series_id] = 0

    dataset_folder = '/mnt/sdc/Liver/dataset/v2'

    train_output_file = '/mnt/sdc/Liver/dataset_log/train.txt'
    val_output_file = '/mnt/sdc/Liver/dataset_log/val.txt'

    patient_folder_list = glob.glob(dataset_folder+'/*')

    patient_info_list = []
    for i in range(len(pattern_list)):
        patient_info_list.append([])

    for patient_folder in patient_folder_list:
        patient_id = os.path.basename(patient_folder)
        for i,pattern in enumerate(pattern_list):
            match = re.match(pattern,patient_id)
            if match:
                patient_info_list[i].append(patient_folder)

    for i in range(len(pattern_list)):
        patient_pattern_list = patient_info_list[i]
        train_num = int(len(patient_pattern_list)*train_rate)
        train_patient_list.extend(patient_pattern_list[:train_num])
        val_patient_list.extend(patient_pattern_list[train_num:])

    # cal statistics
    for patient_folder in train_patient_list:
        series_folder_list = glob.glob(patient_folder+'/*')
        for series_folder in series_folder_list:
            series_id = os.path.basename(series_folder)
            train_stat[series_id] += 1
    for patient_folder in val_patient_list:
        series_folder_list = glob.glob(patient_folder+'/*')
        for series_folder in series_folder_list:
            series_id = os.path.basename(series_folder)
            val_stat[series_id] += 1

    # print the statistics
    print('train stat:')
    print(train_stat)

    print('val stat:')
    print(val_stat)

    # extract patient id only
    for i in range(len(train_patient_list)):
        train_patient_list[i] = os.path.basename(train_patient_list[i])

    for i in range(len(val_patient_list)):
        val_patient_list[i] = os.path.basename(val_patient_list[i])

    # save the splits
    with open(train_output_file,'wb') as f:
        pickle.dump(train_patient_list,f)

    with open(val_output_file,'wb') as f:
        pickle.dump(val_patient_list,f)

    print('Train set has {} patients'.format(len(train_patient_list)))

    print('Val set has {} patients'.format(len(val_patient_list)))




if __name__ == "__main__":
    #task_1()
    #task_2()
    #task_3()
    #task_4()
    #task_6()
    #task_7()
    #task_8()
    #task_9()
    #task_10()
    #task_11()
    #task_12()
    task_13()