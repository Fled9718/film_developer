import os
import numpy as np
import rawpy
import tifffile as tf

icc_path = 'src/ISO22028-2_ROMM-RGB.icc'

def load_image(src_location):
    # read raw data from file
    with rawpy.imread(src_location) as raw:
        rawdata = raw.postprocess(
            use_camera_wb = True,
            gamma = (1, 1),  # sRGB: 2.4, 0; P3: 2.6, 0; for linear: 1, 1
            no_auto_bright = True,
            output_bps = 16,  # output_BitsPerSample
            output_color = rawpy.ColorSpace.ProPhoto
        )

        # crop out extra pixels
        crop_y = raw.sizes.crop_top_margin - raw.sizes.top_margin
        crop_x = raw.sizes.crop_left_margin - raw.sizes.left_margin

        exposed = rawdata[
                  crop_x: crop_x + raw.sizes.crop_width,
                  crop_y: crop_y + raw.sizes.crop_height
                  ]

    return exposed

def get_icc_profile():
    try:
        with open(icc_path, 'rb') as f:
            icc_profile = f.read()
    except FileNotFoundError:
        print('NO ICC FILE FOUND')

    return icc_profile

def invert_image(image_data):
    max_color = np.iinfo(image_data.dtype).max
    return max_color - image_data

def process_all_in_folder(src_path, exp_path):
    if not os.path.exists(exp_path):
        os.makedirs(exp_path)
        print(f"Created directory: {exp_path}")

    tested_raw_formats = ['.cr2']

    for filename in os.listdir(src_path):
        if any(filename.lower().endswith(ext) for ext in tested_raw_formats):
            input_image_path = os.path.join(src_path, filename)

            try:
                #load image
                img = load_image(input_image_path)
                print(f"Processing {filename}...")

                #export
                basename, _ = os.path.splitext(filename)
                tf.imwrite(
                    exp_path + '/' + basename + '.tiff',    # location & name
                    invert_image(img),                      # data
                    bigtiff = False,
                    photometric = 'RGB',
                    iccprofile = get_icc_profile(),
                    metadata = {'ColorSpace': 'ProPhoto RGB'}
                )
            except Exception as e:
                print(f"Could not process {filename}. Reason: {e}")

if __name__ == '__main__':
    #get folder names for images
    print('Starting batch inverter...')

    input_path = input('Please enter absolute RAW image path: ')
    output_path = input('Please enter absolute TIFF output path: ')

    # Clean up the paths (removes extra spaces or quotes from drag-and-drop).
    clean_input_path = input_path.strip().strip('"').strip("'")
    clean_output_path = output_path.strip().strip('"').strip("'")

    print("\nStarting processing...")
    process_all_in_folder(clean_input_path, clean_output_path)
    print('\nAll done!') #script closes automatically after this