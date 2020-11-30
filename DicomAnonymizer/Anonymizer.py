import pydicom
from configparser import ConfigParser
from tqdm import tqdm
import glob
import os
import random
import xml.etree.ElementTree as ET

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
        tagIntSuf = int("0X"+sTag[5:])
        tag = pydicom.tag.Tag((tagIntPre,tagIntSuf))
        return tag

    def extractDigits(self,mixed):
        digits = ""
        for s in mixed:
            if s.isdigit():
                digits.append(s)
        return digits
    def anonymizeDicom(self,dcm,dict):
        '''
        Anonymize a dicom by pre-defined rules
        dcm: loaded dicom file to anonymize
        dict: additional information obtained outside the dicom, such as exam_id, series_id from directory
        return an anonymized dicom by creating a new one
        '''
        anonyDcmObj = pydicom.dataset.Dataset()

        for sTag in self.tagsHandler:
            vr = self.lookupTable["dictionary_vr"][sTag]
            tag = self.str2tag(sTag)

            if self.tagsHandler[sTag]["method"] == "keep":
                if tag in dcm:
                    elem = pydicom.DataElement(tag,vr,dcm[tag])
                    anonyDcmObj.add(elem)
            elif self.tagsHandler[sTag]["method"] == "const":
                if tag in dcm:
                    elem = pydicom.DataElement(tag,vr,self.tagsHandler[sTag]["value"])
                    anonyDcmObj.add(elem)
            elif self.tagsHandler[sTag]["method"] == "lookup":
                if tag in dcm:
                    tagName = self.lookupTable["Tag2Name"][tag]
                    elem = pydicom.DataElement(tag,vr,self.lookupTable[tagName][dcm[tag]])
                    anonyDcmObj.add(elem)
            elif self.tagsHandler[sTag]["method"] == "less_than":
                if tag in dcm:
                    sVal = dcm[tag]
                    iVal = int(sVal)
                    maxVal = self.tagsHandler[sTag]["value"]
                    if iVal > maxVal:
                        modifiedVal = maxVal
                    else:
                        modifiedVal = iVal
                    elem = pydicom.DataElement(tag,vr,str(modifiedVal))
                    anonyDcmObj.add(elem)
            else:
                raise NameError('Unknown Method')



    def anonymizeDataset(self):
        dataset_name = os.path.basename(self.inputFolder)
        print("Anonymizing {0}".format(dataset_name))

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



