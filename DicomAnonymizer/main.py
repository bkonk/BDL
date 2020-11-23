import time
from DicomAnonymizer import Anonymizer

def main():
    inputFolder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    outputFolder = "/mnt/sdc/dataset/Duke_Abdominal_Anonymized"
    configFile = "duke_abdominal.config"

    tic = time.time()
    anonymizer = Anonymizer.DatasetAnonymizer(inputFolder,
                            outputFolder,
                            configFile)
    anonymizer.anonymizeDataset()
    toc = time.time()
    print("Time Elapsed {0} seconds".format(toc-tic))
if __name__ == "__main__":
    main()