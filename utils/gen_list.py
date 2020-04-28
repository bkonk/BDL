import glob
import os
import sys

def gen_img_file_list(img_folder):
    img_path_list = glob.glob(img_folder+'/*')
    img_file_list = []
    for img_path in img_path_list:
        img_file = os.path.basename(img_path)
        img_file_list.append(img_file+'\n')
    return img_file_list

def main():
    img_folder = sys.argv[1]
    img_list_file = sys.argv[2]

    img_file_list = gen_img_file_list(img_folder)
    with open(img_list_file,'w') as fid:
        fid.writelines(img_file_list)

if __name__ == "__main__":
    main()

