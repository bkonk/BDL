import os
import pydicom
import glob

def str2tag(sTag):
    '''
    Given the string format of the tag, convert to dicom Tag object
    The string should be in the format of ****,****
    '''
    tagIntPre = int("0X" + sTag[0:4], 16)
    tagIntSuf = int("0X" + sTag[5:], 16)
    tag = pydicom.tag.Tag((tagIntPre, tagIntSuf))
    return tag

def checkTagValAcrossDataset(tagID,tagName,datasetFolder,outFolder):
    '''
    Check a tag's value across the entire dataset
    Zhe Zhe
    2020/12/09
    '''
    tagHex = str2tag(tagID)
    info = {}
    datasetFolderList = glob.glob(datasetFolder+"/*")
    for examFolder in datasetFolderList:
        examID = os.path.basename(examFolder)
        if examID not in info:
            info[examID] = {}
        seriesFolderList = glob.glob(examFolder+"/*")
        for seriesFolder in seriesFolderList:
            seriesID = os.path.basename(seriesFolder)
            if seriesID not in info[examID]:
                info[examID][seriesID] = {}
            dicomFileList = glob.glob(seriesFolder+"/*")
            for dicomFile in dicomFileList:
                dicomFileName = os.path.basename(dicomFile)
                ds = pydicom.dcmread(dicomFile)
                if tagHex in ds:
                    tagVal = str(ds[tagHex].value)
                    info[examID][seriesID][dicomFileName] = tagVal
                elif tagHex in ds.file_meta:
                    tagVal = str(ds.file_meta[tagHex].value)
                    info[examID][seriesID][dicomFileName] = tagVal
                else:
                    print(dicomFile+" NOT have "+tagName+" tag")
    # save the info
    outFile = os.path.join(outFolder,tagName+".txt")
    with open(outFile,'w') as fid:
        for examID in info:
            for seriesID in info[examID]:
                for dicomFileName in info[examID][seriesID]:
                    fid.write(examID+" "+seriesID+" "+dicomFileName+" "+info[examID][seriesID][dicomFileName]+"\n")
    print(tagName+" Done")

def test_1():
    '''
    Check tags that contain UID
    2020/12/09 version
    '''
    UIDList = ["0020,0052","0020,000e","0008,0018","0088,0140","0020,000d",
               "0002,0002","0002,0003","0002,0010","0002,0012"]
    UIDTagNameList = ["Frame of Reference UID","Series Instance UID","SOP Instance UID","Storage Media File-set UID","Study Instance UID",
                      "Media Storage SOP Class UID ","Media Storage SOP Instance UID","Transfer Syntax UID","Implementation Class UID"]
    datasetFolder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    outputFolder = "/mnt/sdc/dataset/statistics"
    for i in range(len(UIDList)):
        tagID = UIDList[i]
        tagName = UIDTagNameList[i]
        checkTagValAcrossDataset(tagID,tagName,datasetFolder,outputFolder)

def test_2():
    '''
    Debug
    '''
    tagID = "0002,0002"
    tagName = "Media Storage SOP Class UID"
    datasetFolder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    outputFolder = "/mnt/sdc/dataset/statistics"
    checkTagValAcrossDataset(tagID, tagName, datasetFolder, outputFolder)

def test_3():
    '''
    Re-run for the file_meta tags
    Zhe Zhu, 2020/12/10
    '''
    print("Test 3")
    UIDList = ["0002,0002", "0002,0003", "0002,0010", "0002,0012"]
    UIDTagNameList = ["Media Storage SOP Class UID ", "Media Storage SOP Instance UID", "Transfer Syntax UID",
                      "Implementation Class UID"]
    datasetFolder = "/mnt/sdc/dataset/Duke_Abdominal_Original"
    outputFolder = "/mnt/sdc/dataset/statistics"
    for i in range(len(UIDList)):
        tagID = UIDList[i]
        tagName = UIDTagNameList[i]
        checkTagValAcrossDataset(tagID, tagName, datasetFolder, outputFolder)
def main():
    #test_1()
    #test_2()
    test_3()
if __name__ == "__main__":
    main()