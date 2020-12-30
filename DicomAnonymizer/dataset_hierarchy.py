import os
import glob
from tqdm import tqdm
import shutil

def add_exam_layer(inputDataset, outputDataset):
    '''
    Given a dataset of Dataset/Patient/Series/Dicom structure, add an exam1 folder under the Patient folder
    '''
    exam_folder_name = "exam1"
    patient_folder_list = glob.glob(inputDataset+"/*")
    for patient_folder in tqdm(patient_folder_list):
        patient_id = os.path.basename(patient_folder)
        output_patient_folder = os.path.join(outputDataset,patient_id)

        if not os.path.exists(output_patient_folder):
            os.makedirs(output_patient_folder)

        output_exam_folder = os.path.join(output_patient_folder,exam_folder_name)

        if not os.path.exists(output_exam_folder):
            os.makedirs(output_exam_folder)

        series_folder_list = glob.glob(patient_folder+"/*")

        for series_folder in series_folder_list:
            series_id = os.path.basename(series_folder)
            output_series_folder = os.path.join(output_exam_folder,series_id)

            if not os.path.exists(output_series_folder):
                os.makedirs(output_series_folder)

            dicom_file_list = glob.glob(series_folder+"/*")

            for dicom_file in dicom_file_list:
                dicom_name = os.path.basename(dicom_file)
                output_dicom_file = os.path.join(output_series_folder,dicom_name)
                shutil.copyfile(dicom_file,output_dicom_file)


def main():
    inputDataset = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    outputDataset = "/mnt/sdc/dataset/Duke_Abdominal_Original_V2"
    add_exam_layer(inputDataset,outputDataset)


if __name__ == "__main__":
    main()