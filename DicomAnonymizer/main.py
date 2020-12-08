import time
from DicomAnonymizer import Anonymizer

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
if __name__ == "__main__":
    main()