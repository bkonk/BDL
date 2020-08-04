import numpy as np
from ast import literal_eval
from scipy import interpolate
import xmltodict
import pydicom as dcm
import operator
import cv2
from skimage.draw import polygon
import os

def GetROIcoords(roi):

    # get index of ROI

    ind = int(roi['integer'][1])

    # get coordinate data of ROI

    x = roi['array']['dict']['array'][1]['string']

    # convert string coordinates to tuples

    coords = [literal_eval(coord) for coord in x]

    # parse out x and y and make closed loop

    x = [i[0] for i in coords] + [coords[0][0]]

    y = [i[1] for i in coords] + [coords[0][1]]

    # apply parametric spline interpolation

    tck, _ = interpolate.splprep([x,y], s=0, per=True)

    x, y = interpolate.splev(np.linspace(0,1,500), tck)

    return ind,x,y


def GetImageMaskData(file_xml, dcm_files, new_dims):
    # open up xml file and grab the list of ROIs

    with open(file_xml) as f:

        doc = xmltodict.parse(f.read())

    roi_list = doc['plist']['dict']['array']['dict']

    # parse out the image shape

    # imshape = (int(roi_list[0]['integer'][0]),int(roi_list[0]['integer'][3]))

    # get slice locations of all dicoms

    locs = [(d, float(dcm.dcmread(d).SliceLocation)) for d in dcm_files]
    # print(locs)

    if (locs[0][1] - locs[1][1]) > 0:
        print('Z is reversed')
        # z_reversed = True
        if (int(locs[-1][1]) - int(locs[0][1])) > 0:
            print('error A')
            # print(range(len(locs[:][1]),0))
            print(len(locs))
            for err in range(len(locs) - 1, 0, -1):
                # print(err)
                # print(err)
                # print(int(locs[err][1]))#
                # print(int(locs[err+1][1]))
                if (int(locs[err][1]) - int(locs[err + 1][1])) > 0:
                    print('error at slice location ', str(err))
                    locs = locs[err:][:]  # =[]
                    break
    else:
        print('Z is correct')
        if (int(locs[-1][1]) - int(locs[0][1])) < 0:
            print('error B')
            # for err in range(len(locs)):
            #    if (int(locs[err][1])-int(locs[err+1][1]))<0:
            #        print('error at slice location ',str(err))
            # locs[err:][:]=[]
            #        break

    z_reversed = False
    # sort

    locs.sort(key=operator.itemgetter(1))

    dcm_files = [l[0] for l in locs]

    # load dicoms into volume

    image_volume = np.stack([dcm.dcmread(d).pixel_array for d in dcm_files])

    # .astype(np.float)

    window_center = 50.0

    window_width = 400.0

    #    jpg_scale = 255.0

    lower_limit = window_center - (window_width / 2)

    upper_limit = window_center + (window_width / 2)

    # dicom_img = dicom.read_file(dcm_file_path, force=True)
    dicom_img = dcm.dcmread(dcm_files[0])

    img = image_volume

    if hasattr(dicom_img, 'RescaleSlope'):
        rescale_slope = float(dicom_img.RescaleSlope)
        print('rescale_slope: ', rescale_slope)
    else:
        rescale_slope = float(1)

    if hasattr(dicom_img, 'RescaleIntercept'):
        rescale_intercept = float(dicom_img.RescaleIntercept)
        print('rescale_intercept: ', rescale_intercept)
    else:
        rescale_intercept = float(0)

    hounsfield_img = (img * rescale_slope) + rescale_intercept

    clipped_img = np.clip(hounsfield_img, lower_limit, upper_limit)

    windowed_img = (clipped_img / window_width) - (lower_limit / window_width)

    # rescale_slope = 1
    # rescale_intercept = 0

    # multi_slice_viewer0(windowed_img,title='Brandon was here',labels=[], vrange=[0,1])
    # _Inputs_
    # Volume: image volume ndarray in format [slice,rows,columns]
    # title: string to display above images
    # labels: list of labels to display in upper right corner of every slice
    # must have one label per slice
    # vrange: window range in list format: [minimum, maximum]

    # plt.show()

    # slopes = np.stack([dcm.dcmread(d).RescaleSlope for d in dcm_files]).astype(np.float)

    # intercepts = np.stack([dcm.dcmread(d).RescaleIntercept for d in dcm_files]).astype(np.float)

    # maxpixel = np.stack([dcm.dcmread(d).LargestImagePixelValue for d in dcm_files]).astype(np.float)

    # PixelRepresentation = np.stack([dcm.dcmread(d).PixelRepresentation for d in dcm_files]).astype(np.float)

    # exposurenp = np.stack([dcm.dcmread(d).Exposure for d in dcm_files]).astype(np.float)

    # import pdb; pdb.set_trace()

    # # normalize by image

    # for i in range(windowed_img.shape[0]):

    #     im = windowed_img[i]

    #     im /= np.max(im)

    #     windowed_img[i] = im

    # resample image volume to desired dimensions

    output_shape = (windowed_img.shape[0], new_dims[0], new_dims[1])

    im_vol = np.zeros(output_shape)
    for i in range(windowed_img.shape[0]):
        im_vol[i,:,:] = cv2.resize(windowed_img[i,:,:],(new_dims[0], new_dims[1]))
    #im_vol = cv2.resize(windowed_img, output_shape)

    # convert contours into masks

    # make empty mask

    mask = np.zeros(output_shape)

    # import pdb; pdb.set_trace()

    # calculate rescaling factor in each dimension

    x_scale = float(new_dims[1]) / float(windowed_img.shape[2])

    y_scale = float(new_dims[0]) / float(windowed_img.shape[1])

    # loop over ROIs

    for cur_roi in roi_list:
        ind, x, y = GetROIcoords(cur_roi)

        xs = [d * x_scale for d in x]

        ys = [d * y_scale for d in y]

        rr, cc = polygon(ys, xs)

        # one of these two lines determines

        #  z-axis orientation of the mask

        # if z_reversed:

        #    zind = ind

        # else:

        #   zind = mask.shape[0]-ind-1

        zind = ind  # mask.shape[0]-ind-1 #switch
        mask[zind, rr, cc] = 1

    maskback = np.copy(mask)
    if z_reversed:
        for num, loc in enumerate(range(mask.shape[0] - 1, -1, -1)):
            maskback[num, :, :] = mask[loc, :, :]
        mask = maskback

    return im_vol, mask

def GetImageMaskDataOri(file_xml, dcm_files):
    # open up xml file and grab the list of ROIs without resize
    # Zhe Zhu revised 2020/07/12

    with open(file_xml) as f:

        doc = xmltodict.parse(f.read())

    roi_list = doc['plist']['dict']['array']['dict']

    locs = [(d, float(dcm.dcmread(d).SliceLocation)) for d in dcm_files]
    # print(locs)

    if (locs[0][1] - locs[1][1]) > 0:
        #print('Z is reversed')
        # z_reversed = True
        if (int(locs[-1][1]) - int(locs[0][1])) > 0:
            print('error A')
            # print(range(len(locs[:][1]),0))
            print(len(locs))
            for err in range(len(locs) - 1, 0, -1):
                # print(err)
                # print(err)
                # print(int(locs[err][1]))#
                # print(int(locs[err+1][1]))
                if (int(locs[err][1]) - int(locs[err + 1][1])) > 0:
                    print('error at slice location ', str(err))
                    locs = locs[err:][:]  # =[]
                    break
    else:
        #print('Z is correct')
        if (int(locs[-1][1]) - int(locs[0][1])) < 0:
            print('error B')
            # for err in range(len(locs)):
            #    if (int(locs[err][1])-int(locs[err+1][1]))<0:
            #        print('error at slice location ',str(err))
            # locs[err:][:]=[]
            #        break

    z_reversed = False
    # sort

    locs.sort(key=operator.itemgetter(1))

    dcm_files = [l[0] for l in locs]

    # load dicoms into volume

    image_volume = np.stack([dcm.dcmread(d).pixel_array for d in dcm_files])

    # .astype(np.float)

    window_center = 50.0

    window_width = 400.0

    dicom_img = dcm.dcmread(dcm_files[0])

    if hasattr(dicom_img,'WindowCenter'):
        window_center = dicom_img.WindowCenter
    else:
        print("No Window Center, use default")

    if hasattr(dicom_img,'WindowWidth'):
        window_width = dicom_img.WindowWidth
    else:
        print("No Window Width, use default")
    #    jpg_scale = 255.0

    lower_limit = window_center - (window_width / 2)

    upper_limit = window_center + (window_width / 2)

    # dicom_img = dicom.read_file(dcm_file_path, force=True)


    img = image_volume



    if hasattr(dicom_img, 'RescaleSlope'):
        rescale_slope = float(dicom_img.RescaleSlope)
        #print('rescale_slope: ', rescale_slope)
    else:
        rescale_slope = float(1)

    if hasattr(dicom_img, 'RescaleIntercept'):
        rescale_intercept = float(dicom_img.RescaleIntercept)
        #print('rescale_intercept: ', rescale_intercept)
    else:
        rescale_intercept = float(0)

    hounsfield_img = (img * rescale_slope) + rescale_intercept

    clipped_img = np.clip(hounsfield_img, lower_limit, upper_limit)

    windowed_img = (clipped_img / window_width) - (lower_limit / window_width)

    output_shape = windowed_img.shape

    im_vol = windowed_img


    mask = np.zeros(output_shape)


    x_scale = 1.0

    y_scale = 1.0

    # loop over ROIs

    for cur_roi in roi_list:
        ind, x, y = GetROIcoords(cur_roi)

        xs = [d * x_scale for d in x]

        ys = [d * y_scale for d in y]

        rr, cc = polygon(ys, xs)

        # one of these two lines determines

        #  z-axis orientation of the mask

        # if z_reversed:

        #    zind = ind

        # else:

        #   zind = mask.shape[0]-ind-1

        zind = ind  # mask.shape[0]-ind-1 #switch
        mask[zind, rr, cc] = 1

    maskback = np.copy(mask)
    if z_reversed:
        for num, loc in enumerate(range(mask.shape[0] - 1, -1, -1)):
            maskback[num, :, :] = mask[loc, :, :]
        mask = maskback

    return im_vol, mask

def ExtractImgAndMask(xml_file,dicom_file_list,output_folder):
    '''
    Extract the image and mask, and save to the target folder
    Zhe Zhu, 2020/07/12
    '''
    output_img_folder = os.path.join(output_folder,'img')
    output_mask_folder = os.path.join(output_folder,'mask')

    if not os.path.exists(output_img_folder):
        os.makedirs(output_img_folder)
    if not os.path.exists(output_mask_folder):
        os.makedirs(output_mask_folder)

    img_vol, mask_data = GetImageMaskDataOri(xml_file, dicom_file_list)

    assert img_vol.shape == mask_data.shape

    # Normalize
    img_vol *= 255.0
    mask_data *= 255.0

    img_vol.astype(np.uint8)
    mask_data.astype(np.uint8)

    slice_num = img_vol.shape[0]

    for i in range(slice_num):
        img_file = os.path.join(output_img_folder,'{:04d}.png'.format(i))
        mask_file = os.path.join(output_mask_folder,'{:04d}.png'.format(i))
        cv2.imwrite(img_file,img_vol[i,:,:])
        cv2.imwrite(mask_file,mask_data[i,:,:])

