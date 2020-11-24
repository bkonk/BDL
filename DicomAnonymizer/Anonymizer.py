import pydicom
from configparser import ConfigParser
from tqdm import tqdm
import glob
import os
import random

class DatasetAnonymizer:
    '''
    Dataset Anonymizer. This class is used to anonymize the entire dataset
    '''
    def __init__(self,inputFolder,outputFolder,configFile):
        self.inputFolder = inputFolder
        self.outputFolder = outputFolder
        self.config = ConfigParser()
        self.config.read(configFile)
    def genRandonDigit(self,num):
        digit = ""
        for i in range(num):
            digit += str(random.randint(0,9))
        return digit
    def genRandomVal(self,tag):
        '''
        Generate random value based on specified tag
        return the generated str
        '''
        if tag=="00080050":
            # Accession Number, 8 digit
            accessionNumber = self.genRandonDigit(8)
            return accessionNumber
        if tag=="00200052":
            # Frame of Reference UID,  1.1.111.111.111.1*39
            frameOfReferenceUID = self.genRandonDigit(1)+"."+self.genRandonDigit(1)+"."+self.genRandonDigit(3)+\
                "."+self.genRandonDigit(3)+"."+self.genRandonDigit(3)+"."+self.genRandonDigit(39)
            return frameOfReferenceUID
        if tag=="0020000e":
            # Series Instance UID, same format as above
            seriesInstanceUID = self.genRandonDigit(1)+"."+self.genRandonDigit(1)+"."+self.genRandonDigit(3)+\
                "."+self.genRandonDigit(3)+"."+self.genRandonDigit(3)+"."+self.genRandonDigit(39)
            return seriesInstanceUID
        if tag=="00080018":
            # SOP Instance UID, same format as above
            sopInstanceUID = self.genRandonDigit(1)+"."+self.genRandonDigit(1)+"."+self.genRandonDigit(3)+\
                "."+self.genRandonDigit(3)+"."+self.genRandonDigit(3)+"."+self.genRandonDigit(39)
            return sopInstanceUID
        if tag=="00880140":
            # Storage Media File-set UID
            storageMediaFilesetUID = self.genRandonDigit(1)+"."+self.genRandonDigit(1)+"."+self.genRandonDigit(3)+\
                "."+self.genRandonDigit(3)+"."+self.genRandonDigit(3)+"."+self.genRandonDigit(39)
            return storageMediaFilesetUID
        if tag=="0020000d":
            # Study Instance UID
            studyInstanceUID = self.genRandonDigit(1)+"."+self.genRandonDigit(1)+"."+self.genRandonDigit(3)+\
                "."+self.genRandonDigit(3)+"."+self.genRandonDigit(3)+"."+self.genRandonDigit(39)
            return studyInstanceUID

    def genConstVal(self,tag):
        '''
        Generate const value based on our pre-defined rule
        return the generated str
        '''
        if tag=="00080022":
            # Acquisition Date
            acquisitionDate = "19900101"
            return acquisitionDate
        if tag=="00080023":
            # Content Date
            contentDate = "19900101"
            return contentDate
    def anonymizeDicom(self,dcm,dict):
        '''
        Anonymize a dicom by pre-defined rules
        dcm: loaded dicom file to anonymize
        dict: additional information, such as series_id
        return an anonymized dicom file
        '''
        all_mentioned_tags = {}
        for t in dict["keep"]:
            all_mentioned_tags[t] = 1
        for t in dict["randomize"]:
            all_mentioned_tags[t] = 1
        for t in all_mentioned_tags["thresholding"]:
            all_mentioned_tags[t] = 1

        # remove private tags
        dcm.remove_private_tags()


        for tag in dcm:
            if tag not in all_mentioned_tags:
                # anonymize unmentioned tags
                dcm[tag] = "anonymous"
            if tag in dict["keep"]:
                pass
            if tag in dict["randomize"]:
                pass


    def anonymizeDataset(self):
        dataset_name = os.path.basename(self.inputFolder)
        print("Anonymizing {0}".format(dataset_name))

        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)

        exam_folder_list = glob.glob(self.inputFolder+"/*")
        for exam_folder in tqdm(exam_folder_list):
            exam_id = os.path.basename(exam_folder)
            anonymized_exam_id = self.config["exam_id"][exam_id]
            anonymized_exam_folder = os.path.join(self.outputFolder,anonymized_exam_id)

            if not os.path.exists(anonymized_exam_folder):
                os.makedirs(anonymized_exam_folder)

            series_folder_list = glob.glob(exam_folder+"/*")
            for series_folder in series_folder_list:
                series_id = os.path.basename(series_folder)
                series_id = series_id.replace(" ","") # trim space
                output_series_folder = os.path.join(anonymized_exam_folder,series_id)

                anonymization_info_dict = self.config
                anonymization_info_dict['series_id'] = series_id
                anonymization_info_dict['exam_id'] = exam_id
                if not os.path.exists(output_series_folder):
                    os.makedirs(output_series_folder)

                dicom_file_list = glob.glob(series_folder+"/*")
                for dicom_file in dicom_file_list:
                    dcm = pydicom.dcmread(dicom_file)
                    anonymized_dcm = self.anonymizeDicom(dcm,anonymization_info_dict)



