import sys
import numpy as np
import csv

sys.path.append('/home/zzhu/zzhu/Liver/python')
import parse_reader_csv

def load_reading(reading_file):
    '''Load the reader file into dict format'''
    map_txt = '/home/zzhu/Data/data/ai_vs_radiologist/map_fatonly.txt'

    dt = {'names': ('series_name', 'label'), 'formats': ('S20', 'i2')}
    name_label_list = np.loadtxt(map_txt, dtype=dt)
    name_label_dict = {}
    for i in range(len(name_label_list)):
        name_label_dict[name_label_list[i][0].decode("utf-8")] = name_label_list[i][1]
    name_label_dict['dwi_t2'] = name_label_dict['dwi_and_t2']
    name_label_dict['t2'] = name_label_dict['dwi_and_t2']
    name_label_dict['hepatocyte'] = name_label_dict['hepa_trans']
    name_label_dict['transitional'] = name_label_dict['hepa_trans']
    info_dict_file = reading_file

    col_begin = 5
    col_end = 43
    # deal with anything else classes
    with open(info_dict_file, 'r') as csv_file:
        rows = csv.reader(csv_file, delimiter=',')
        header = next(rows, None)
        for i in range(col_begin, col_end):
            series_name = header[i]
            if series_name not in name_label_dict:
                name_label_dict[series_name] = name_label_dict['anythingelse']

    # load info_dict
    series_info = parse_reader_csv.parse(info_dict_file, name_label_dict)
    reading_dict = {}
    for info in series_info:
        series_id = info['series_id']
        series_label = info['series_label']
        reading_dict[series_id] = series_label
    return reading_dict

def write2config(anno,configFile):
    series_labels = {}
    for series_id in anno:
        id_list = series_id.split("_")
        patientName = "LRML_{:04d}".format(int(id_list[0]))
        if patientName not in series_labels:
            series_labels[patientName] = {}
        if len(id_list) == 3:
            volumeID = id_list[1]+"_"+id_list[2]
        else:
            volumeID = id_list[1]
        label = anno[series_id]
        series_labels[patientName][volumeID] = label

    with open(configFile,'w') as fid:
        for patientName in series_labels:
            fid.write("["+patientName+"]\n")
            for volumeID in series_labels[patientName]:
                label = series_labels[patientName][volumeID]
                fid.write(volumeID+"="+"{}".format(label)+"\n")
def main():
    anno_file = '/home/zzhu/Data/Liver/LIRADSMachineLearnin_DATA_latest.csv'
    configFile = '/mnt/sdc/dataset/Duke_Abdominal_Supplementary/labels.txt'
    anno = load_reading(anno_file)
    write2config(anno,configFile)
    print("Annotation saved")


if __name__=="__main__":
    main()
