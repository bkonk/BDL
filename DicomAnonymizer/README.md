#Dicom Anonymizer
This repository contains the code to anonymize dicom files so that after the anonymization process 
they are free from PHI and can be shared in research community. Note that only dicom tags are processed.
The image (MRI,CT) keep unchanged after the anonymization. 

##Usage
The main module is Anonymizer.py. To anonymize a dataset, you need to set the directory of the unanonymized
dataset, the directory of the anonymized dataset and a script file. An example can be found in main.py.

##Dataset Hierarchy
This anonymizer support two different kinds of dataset hierarchy: DATASET/EXAM/SERIES/DICOM and 
DATASET/PATIENT/EXAM/SERIES/DICOM. They correspond to the method anonymizeDatasetV1 and anonymizeDatasetV2
respectively. 

##Anonymization Script
 The anonymization script, for example, duke_abdominal.script, is used to set the behaviour for each tag in a dicom
 file. 


