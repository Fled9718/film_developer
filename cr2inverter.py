import numpy as np
import rawpy
import tifffile as tf

#todo embed exif data in .tiff export
#too much fuckery with tifffile, since something cries about the created tiff files.
#also, the tiff files are not supposed the final product.
#inversion and colorspace work. colorspace communication with different photo editors questionable.
#however, I know how to set darktable to work things.
#just need to test with actuall negatives.

#todo build little script/app so I can batchprocess a roll of film like this

#source image location
src_path = 'res/'
src_file_name = 'test'
src_file_type = '.CR2'
src_location = src_path + src_file_name + src_file_type

#export location
exp_path = 'exp/'

#icc profile location
icc_path = 'src/ISO22028-2_ROMM-RGB.icc'

#read raw data from file
with rawpy.imread(src_location) as raw:
    rawdata = raw.postprocess( #3 colors (RGB), not 4 (RGBG) for my Canon 5dIV
        use_camera_wb = True,
        gamma = (1, 1), #sRGB: 2.4, 0; P3: 2.6, 0; for linear: 1, 1
        no_auto_bright = True,
        output_bps = 16, #output_BitsPerSample
        output_color = rawpy.ColorSpace.ProPhoto
        )

    #crop out extra pixels and debayering artifacts I guess
    crop_y = raw.sizes.crop_top_margin - raw.sizes.top_margin
    crop_x = raw.sizes.crop_left_margin - raw.sizes.left_margin

    exposed = rawdata[
              crop_x : crop_x + raw.sizes.crop_width,
              crop_y : crop_y + raw.sizes.crop_height
              ]

#invert the image
def invert_image(image_data):
    max_color = np.iinfo(image_data.dtype).max #runtime about the same as, maybe faster than hardcoding the max value of 65535
    return max_color - image_data

#get icc profile
try:
    with open(icc_path, 'rb') as f:
        icc_profile = f.read()
except FileNotFoundError:
    print('NO ICC FILE FOUND')

#export
tf.imwrite(
    exp_path + 'test' + '.tiff',  #location & name
    invert_image(exposed),              #data
    bigtiff = False,
    photometric = 'RGB',
    iccprofile = icc_profile,
    metadata = {'ColorSpace': 'ProPhoto RGB'}
    )