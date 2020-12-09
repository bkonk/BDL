import time
from DicomAnonymizer import Anonymizer
import pydicom

def main():
    inputFolder = "/mnt/sdc/dataset/Duke_Abdominal_Test_Original"
    outputFolder = "/mnt/sdc/dataset/Duke_Abdominal_Test_Anonymized"
    scriptFile = "duke_abdominal.script"

    tic = time.time()
    anonymizer = Anonymizer.DatasetAnonymizer(inputFolder,
                            outputFolder,
                            scriptFile)
    anonymizer.anonymizeDataset()
    toc = time.time()
    print("Time Elapsed {0} seconds".format(toc-tic))

def test():
    test_file = "/mnt/sdc/dataset/Duke_Abdominal_Test_Anonymized/093/5/0001.dicom"
    ds = pydicom.dcmread(test_file)
    print("OK")
if __name__ == "__main__":
    test()
    #main()