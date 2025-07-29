# film_developer
Takes RAW image files and creates tiff files for further editing.
Created for digitizing film-negatives.
We invert the image data and create a linear ProPhoto RGB image in a 16 Bit .tiff file.

The script currently does not correct image for color cast due to film-base color.

Code currently depends on 'ISO22028-2_ROMM-RGB.icc' as .icc color profile, downloaded directly from the ICC website (https://www.color.org/chardata/rgb/rommrgb.xalter).
