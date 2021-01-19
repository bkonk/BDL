import pydicom
from configparser import ConfigParser
from tqdm import tqdm
import glob
import os
import random
import xml.etree.ElementTree as ET
from pydicom import config
config.enforce_valid_values = True
import numpy as np



class DatasetAnonymizer:
    '''
    Dataset Anonymizer. This class is used to anonymize the entire dataset
    inputFolder: original dataset folder
    outputFolder: anonymized dataset folder
    scriptFile: xml file describing how to deal with each tag
    '''
    def __init__(self,inputFolder,outputFolder,scriptFile):
        self.inputFolder = inputFolder
        self.outputFolder = outputFolder
        self.scriptFile = scriptFile
        self.lookupTableFile = ""
        self.parseScript()
        self.parseLookupTableFile()
        print("Dicom Anonymizer Initialized")
        print("Use Script File: {0}".format(self.scriptFile))
        print("Use Lookup Table File: {0}".format(self.lookupTableFile))

    def parseScript(self):
        '''
        Parse the xml script file
        '''
        tree = ET.parse(self.scriptFile)
        root = tree.getroot()
        self.tagsHandler = {}
        for elem in root:
            handler = self.processScriptElem(elem)
            self.tagsHandler[handler["tagID"]] = handler

    def processScriptElem(self,elem):
        handler = {}
        tagProcessMethod = elem.attrib['f']
        if tagProcessMethod == "keep":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "keep"
            return handler
        elif tagProcessMethod == "const":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "const"
            handler["value"] = elem.attrib['v']
            return handler
        elif tagProcessMethod == "empty":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "const"
            handler["value"] = ""
            return handler
        elif tagProcessMethod == "lookup":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "lookup"
            handler["lookupTableFile"] = elem.attrib['p']
            if self.lookupTableFile=="":
                self.lookupTableFile = elem.attrib['p']
            return handler
        elif tagProcessMethod == "less_than":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "less_than"
            handler["value"] = elem.attrib['v']
            return handler
        elif tagProcessMethod == "random":
            tagID = elem.attrib['t']
            handler["tagID"] = tagID
            handler["method"] = "random"
            return handler
        else:
            raise NameError('Unknown Method')

    def parseLookupTableFile(self):
        self.lookupTable = ConfigParser()
        self.lookupTable.read(self.lookupTableFile)

    def str2tag(self,sTag):
        '''
        Given the string format of the tag, convert to dicom Tag object
        The string should be in the format of ****,****
        '''
        tagIntPre = int("0X" + sTag[0:4], 16)
        tagIntSuf = int("0X"+sTag[5:],16)
        tag = pydicom.tag.Tag((tagIntPre,tagIntSuf))
        return tag

    def extractDigits(self,mixed):
        digits = ""
        for s in mixed:
            if s.isdigit():
                digits += s
        return digits

    def fmtSeriesID(self,s):
        left_brace_index = s.find('(')
        right_brace_index = s.find(')')
        fmtSeriesID = ""
        if left_brace_index == -1 and right_brace_index == -1:
            # only number
            fmtSeriesID = s.strip()
        elif left_brace_index != -1 and right_brace_index != -1:
            # slice or odd or even
            number_str = s[:left_brace_index].strip()
            odd_index = s.find('odd')
            even_index = s.find('even')
            bar_index = s.find('-')
            if odd_index != -1:
                fmtSeriesID = number_str.strip() + '_odd'
            elif even_index != -1:
                fmtSeriesID = number_str.strip() + '_even'
            elif bar_index != -1:
                begin_str = s[left_brace_index + 1:bar_index]
                fmtSeriesID = number_str.strip() + '_' + begin_str
        return fmtSeriesID

    def anonymizeDicom(self,dcm, dict_study):
        '''
        Anonymize a dicom by pre-defined rules
        dcm: loaded dicom file to anonymize
        dict: additional information obtained outside the dicom, such as exam_id, series_id from directory
        return an anonymized dicom by creating a new one
        '''
        anonyDcmObj = pydicom.dataset.Dataset()

        # copy pixel_array
        arr = dcm.pixel_array
        anonyDcmObj.PixelData = arr.tobytes()

        # set the required fields
        anonyDcmObj.preamble = dcm.preamble
        anonyDcmObj.file_meta = dcm.file_meta
        anonyDcmObj.is_little_endian = dcm.is_little_endian
        anonyDcmObj.is_implicit_VR = dcm.is_implicit_VR

        # Test
        #anonyDcmObj.file_meta.MediaStorageSOPClassUID = []

        for sTag in self.tagsHandler:
            
            vr = self.lookupTable["dictionary_vr"][sTag]
            tag = self.str2tag(sTag)

            if self.tagsHandler[sTag]["method"] == "keep":
                if tag in dcm:
                    elem = dcm[tag]
                    anonyDcmObj.add(elem)
                elif tag in dcm.file_meta:
                    # because file_meta has already been copied
                    pass
            elif self.tagsHandler[sTag]["method"] == "const":
                if tag in dcm or tag in dcm.file_meta:
                    if tag in dcm:
                        elem = dcm[tag]
                        elem.value = self.tagsHandler[sTag]["value"]
                        anonyDcmObj.add(elem)
                    else:
                        # The tag belongs to file_meta
                        anonyDcmObj.file_meta[tag].value = self.tagsHandler[sTag]["value"]

            elif self.tagsHandler[sTag]["method"] == "lookup":
                if tag in dcm:
                    tagName = self.lookupTable["Tag2Name"][str(tag).replace(" ","")]
                    elem = dcm[tag]
                    if tagName == 'PatientName':
                        tagVal = 'Lrm_' + str(dcm[tag].value).split('_')[1] + '_assess'
                    else:
                        tagVal = str(dcm[tag].value)
                    elem.value = self.lookupTable[tagName][tagVal]
                    anonyDcmObj.add(elem)
            elif self.tagsHandler[sTag]["method"] == "less_than":
                if tag in dcm:
                    sVal = dcm[tag].value
                    iVal = int(self.extractDigits(sVal))
                    maxVal = int(self.tagsHandler[sTag]["value"])
                    if iVal > maxVal:
                        modifiedVal = maxVal
                    else:
                        modifiedVal = iVal
                    elem = dcm[tag]
                    elem.value = "{:03d}Y".format(modifiedVal)
                    anonyDcmObj.add(elem)
           
            elif self.tagsHandler[sTag]["method"] == "random":
                                
                if tag in dcm or tag in dcm.file_meta:
                                                           
                    if self.tagsHandler[sTag]["tagID"] == "0020,000e": #SeriesInstanceUID
                        rand_str = '.'.join([dict_study['rand_6_SeriesInstanceUID'], dict_study['rand_5_SeriesInstanceUID'], '2.1.1', dict_study['rand_tail_SeriesInstanceUID']])
                    elif self.tagsHandler[sTag]["tagID"] == "0008,0018": #SOPInstanceUID
                        rand_str = '.'.join([dict_study['rand_6_SOPInstanceUID'], dict_study['rand_5_SOPInstanceUID'], '2.1.3', dict_study['rand_tail_SOPInstanceUID']])
                    elif self.tagsHandler[sTag]["tagID"] == "0020,000d": #StudyInstanceUID    
                        rand_str = '.'.join([dict_study['rand_6_StudyInstanceUID'], dict_study['rand_5_StudyInstanceUID'], '2.1.1', dict_study['rand_tail_StudyInstanceUID']])
                    elif self.tagsHandler[sTag]["tagID"] == "0002,0003": #MediaStorageSOPInstanceUID  
                        rand_str = '.'.join([dict_study['rand_6_MediaStorageSOPInstanceUID'], dict_study['rand_5_MediaStorageSOPInstanceUID'], '2.1.3', dict_study['rand_tail_MediaStorageSOPInstanceUID']])

                    if tag in dcm:
                        elem = dcm[tag]
                        elem.value = rand_str
                        anonyDcmObj.add(elem)
                    elif tag in dcm.file_meta:
                        elem = dcm.file_meta[tag]
                        elem.value = rand_str
                        anonyDcmObj.file_meta.add(elem)
                    
            else:
                raise NameError('Unknown Method')
        return anonyDcmObj



    def anonymizeDatasetV1(self):
        '''
        Anonymize a dataset that has the following hierarchy:
        Dataset/Exam/Series/DicomFiles
        This follows the original Duke Abdonimal dataset structure
        '''
        dataset_name = os.path.basename(self.inputFolder)
        print("Anonymizing {0}".format(dataset_name))
        print("Assuming the dataset has the Dataset/Exam/Series/DicomFiles structure")

        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)

        exam_folder_list = glob.glob(self.inputFolder+"/*")
        for exam_folder in tqdm(exam_folder_list):
            exam_id = os.path.basename(exam_folder)
            anonymized_exam_id = self.lookupTable["PatientName"][exam_id]
            anonymized_exam_folder = os.path.join(self.outputFolder,anonymized_exam_id)

            if not os.path.exists(anonymized_exam_folder):
                os.makedirs(anonymized_exam_folder)

            series_folder_list = glob.glob(exam_folder+"/*")
            for series_folder in series_folder_list:
                series_id = os.path.basename(series_folder)
                series_id = series_id.replace(" ","") # trim space
                output_series_folder = os.path.join(anonymized_exam_folder,series_id)

                anonymization_info_dict = {}
                anonymization_info_dict['series_id'] = series_id
                anonymization_info_dict['exam_id'] = exam_id
                if not os.path.exists(output_series_folder):
                    os.makedirs(output_series_folder)

                dicom_file_list = glob.glob(series_folder+"/*")
                for dicom_file in dicom_file_list:
                    dcm = pydicom.dcmread(dicom_file)
                    anonymized_dcm = self.anonymizeDicom(dcm,anonymization_info_dict)

                    dicom_file_name = os.path.basename(dicom_file)
                    anonDcmFile = os.path.join(output_series_folder,dicom_file_name)
                    pydicom.filewriter.dcmwrite(anonDcmFile,anonymized_dcm)

    def anonymizeDatasetV2(self):
        '''
        Anonymize a dataset that has the following hierarchy:
        Dataset/Patient/Exam/Series/DicomFiles
        This aims to deal with a more general medical imaging dataset structure
        '''
        dataset_name = os.path.basename(self.inputFolder)
        print("Anonymizing {0}".format(dataset_name))
        print("Assuming the dataset has the Dataset/Patient/Exam/Series/DicomFiles structure")

        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)

        patient_folder_list = glob.glob(self.inputFolder+"/*")
        for patient_folder in patient_folder_list:
            patient_id = os.path.basename(patient_folder)#.upper()
#             print('PATIENT ID: ', patient_id)
            anonymized_patient_id = self.lookupTable["PatientName"][patient_id]
            output_patient_folder = os.path.join(self.outputFolder,anonymized_patient_id)

            if not os.path.exists(output_patient_folder):
                os.makedirs(output_patient_folder)

            exam_folder_list = glob.glob(patient_folder+"/*")
            
            #random vals (same across study)
            rand_5_SeriesInstanceUID = ''.join([str(np.random.randint(0,9)) for i in range(0,5)])
            rand_5_SOPInstanceUID = ''.join([str(np.random.randint(0,9)) for i in range(0,5)])
            rand_5_StudyInstanceUID = ''.join([str(np.random.randint(0,9)) for i in range(0,5)])
            rand_5_MediaStorageSOPInstanceUID = ''.join([str(np.random.randint(0,9)) for i in range(0,5)])
            
            rand_6_SeriesInstanceUID = '.'.join([str(np.random.randint(0,9)) for i in range(0,6)])
            rand_6_SOPInstanceUID = '.'.join([str(np.random.randint(0,9)) for i in range(0,6)])
            rand_6_StudyInstanceUID = '.'.join([str(np.random.randint(0,9)) for i in range(0,6)])
            rand_6_MediaStorageSOPInstanceUID = '.'.join([str(np.random.randint(0,9)) for i in range(0,6)])
            
            rand_tail_StudyInstanceUID = ''.join([str(np.random.randint(0,9)) for i in range(0,31)])

            for exam_folder in tqdm(exam_folder_list):
                exam_id = os.path.basename(exam_folder)
                output_exam_folder = os.path.join(output_patient_folder,exam_id)

                if not os.path.exists(output_exam_folder):
                    os.makedirs(output_exam_folder)

                series_folder_list = glob.glob(exam_folder+"/*")

                for series_folder in series_folder_list:
                    series_id = os.path.basename(series_folder)
                    series_id = series_id.replace(" ","") # trim space
                    output_series_folder = os.path.join(output_exam_folder,series_id)

                    anonymization_info_dict = {}
                    anonymization_info_dict['series_id'] = series_id
                    anonymization_info_dict['exam_id'] = exam_id
                                             
                    #random vals (same across series)
                    anonymization_info_dict['rand_tail_SeriesInstanceUID'] = ''.join([str(np.random.randint(0,9)) for i in range(0,32)])
                    anonymization_info_dict['rand_tail_SOPInstanceUID'] = ''.join([str(np.random.randint(0,9)) for i in range(0,32)])
#                     anonymization_info_dict['rand_tail_StudyInstanceUID'] = ''.join([str(np.random.randint(0,9)) for i in range(0,31)])
                    anonymization_info_dict['rand_tail_StudyInstanceUID'] = rand_tail_StudyInstanceUID
                    anonymization_info_dict['rand_tail_MediaStorageSOPInstanceUID'] = anonymization_info_dict['rand_tail_SOPInstanceUID']
                                             
                    #random vals --add study vals to dict
                    anonymization_info_dict['rand_5_SeriesInstanceUID'] = rand_5_SeriesInstanceUID
                    anonymization_info_dict['rand_5_SOPInstanceUID'] = rand_5_SOPInstanceUID
                    anonymization_info_dict['rand_5_StudyInstanceUID'] = rand_5_StudyInstanceUID
                    anonymization_info_dict['rand_5_MediaStorageSOPInstanceUID'] = rand_5_MediaStorageSOPInstanceUID
                    anonymization_info_dict['rand_6_SeriesInstanceUID'] = rand_6_SeriesInstanceUID
                    anonymization_info_dict['rand_6_SOPInstanceUID'] = rand_6_SOPInstanceUID
                    anonymization_info_dict['rand_6_StudyInstanceUID'] = rand_6_StudyInstanceUID
                    anonymization_info_dict['rand_6_MediaStorageSOPInstanceUID'] = rand_6_MediaStorageSOPInstanceUID
                    
                    
                    
                    if not os.path.exists(output_series_folder):
                        os.makedirs(output_series_folder)

                    dicom_file_list = glob.glob(series_folder+"/*")
                    for dicom_file in dicom_file_list:
                        dcm = pydicom.dcmread(dicom_file)
                        anonymized_dcm = self.anonymizeDicom(dcm,anonymization_info_dict)

                        dicom_file_name = os.path.basename(dicom_file)
                        anonDcmFile = os.path.join(output_series_folder,dicom_file_name)
                        pydicom.filewriter.dcmwrite(anonDcmFile,anonymized_dcm)



