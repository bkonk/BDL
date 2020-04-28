import os
import glob
import shutil
import sys

def merge_folders(folder):
    sub_folder_list = glob.glob(folder+'/*')
    for sub_folder in sub_folder_list:
        img_file_list = glob.glob(sub_folder+'/*')
        for img_file in img_file_list:
            img_name = os.path.basename(img_file)
            tgt_file_path = os.path.join(folder,img_name)
            shutil.move(img_file,tgt_file_path)
        os.rmdir(sub_folder)

def main():
    folder = sys.argv[1]
    merge_folders(folder)

if __name__ == "__main__":
    main()
