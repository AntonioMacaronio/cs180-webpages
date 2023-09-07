# CS194-26 (CS294-26): Project 1 starter Python code - Anthony Zhang (3036218223)

# these are just some suggested libraries
# instead of scikit-image you could use matplotlib and opencv to read, write, and display images

import numpy as np
import skimage as sk
from skimage.transform import rescale, downscale_local_mean
import skimage.io as skio

# name of the input file (SELECT AN IMAGE BY UNCOMMENTING)
# imname = 'cathedral.jpg'
# imname = 'church.tif'
# imname = 'emir.tif'
# imname = 'harvesters.tif'
# imname = 'icon.tif'
# imname = 'lady.tif'
# imname = 'melons.tif'
# imname = 'monastery.jpg'
# imname = 'onion_church.tif'
# imname = 'sculpture.tif'
# imname = 'self_portrait.tif'
# imname = 'three_generations.tif'
# imname = 'tobolsk.jpg'
# imname = 'train.tif'
# imname = 'zakat1.tif'
# imname = 'zakat2.tif'
# imname = 'piony1.tif'
imname = 'piony2.tif'

# read in the image
im = skio.imread(imname)

# convert to double (might want to do this later on to save memory)    
im = sk.img_as_float(im) # im is a 2d numpy array, shape is 1024 by 390
    
# compute the height of each part (just 1/3 of total)
height = np.floor(im.shape[0] / 3.0).astype(int)

# separate color channels
b = im[:height]
g = im[height: 2*height]
r = im[2*height: 3*height]

# cropping the images by 10% off each edge
b_numRows, b_numCols = b.shape
g_numRows, g_numCols = g.shape
r_numRows, r_numCols = r.shape
b = b[int(.05 * b_numRows):int(.95 * b_numRows), int(.05 * b_numCols):int(.95 * b_numCols)]
g = g[int(.05 * g_numRows):int(.95 * g_numRows), int(.05 * g_numCols):int(.95 * g_numCols)]
r = r[int(.05 * r_numRows):int(.95 * r_numRows), int(.05 * r_numCols):int(.95 * r_numCols)]

# given a 2D numpy array, outputs a list of downscaled versions until exhaustive search is viable (400 pixels x 400 pixels dimensions)
def image_pyramid(image, method="downscale"):
    output = [image]
    curr_image = image
    while curr_image.shape[0] >= 400 and curr_image.shape[1] >= 400:
        if method == "rescale":
            new_image = rescale(curr_image, 0.5, anti_aliasing=True)
        else:
            new_image = rescale(curr_image, 0.5, anti_aliasing=True)
        output.append(new_image)
        curr_image = new_image
    return output

# a version of np.roll but instead of wrapping around, the empty space is white
def roll_wrapper(image, x, y):
    # the first x cols becomes white
    image_copy = np.copy(image)
    if x > 0:
        image_copy = np.roll(image_copy, x, axis=1)
        image_copy[:, :x] = 1
    # the last x cols becomes white    
    elif x < 0:
        image_copy = np.roll(image_copy, x, axis=1)
        image_copy[:, x:] = 1
    # the first y rows becomes white
    if y > 0:
        image_copy = np.roll(image_copy, y, axis=0)
        image_copy[:y, :] = 1
    # the last y rows becomes white
    elif y < 0:
        image_copy = np.roll(image_copy, y, axis=0)
        image_copy[y:, :] = 1
    return image_copy

# aligns a a color 2d numpy array onto a blue 2d numpy array and returns the aligned image and its shift
def align(color, blue):
    smallest_error = float("inf")
    best_fit = None
    shift = (None, None)
    for x in range(-15, 16):
        for y in range(-15, 16):
            shifted_color = roll_wrapper(color, x, y)
            curr_error = np.sum((blue - shifted_color) ** 2) # sum of squared differences
            if curr_error < smallest_error:
                smallest_error = curr_error
                best_fit = shifted_color
                shift = (x, y)
    return best_fit, shift

# returns the color image aligned to the blue image with any image size by using image pyramids
def align_wrapper(color_pyramid, blue_pyramid):
    pyramid_height = len(color_pyramid)
    prevShift = (0, 0)
    for i in range(pyramid_height-1, -1, -1):
        print(prevShift)
        color_i = color_pyramid[i]
        blue_i = blue_pyramid[i]

        shifted_color_i, shift_i = align(roll_wrapper(color_i, 2*prevShift[0], 2*prevShift[1]), blue_i)
        prevShift = (shift_i[0] + 2*prevShift[0], shift_i[1] + 2*prevShift[1])
        if i == 0:
            # return shifted_color_i, (shift_i[0] + 2*prevShift[0], shift_i[1] + 2*prevShift[1])
            return shifted_color_i, prevShift
        
r_pyramid = image_pyramid(r)
g_pyramid = image_pyramid(g)
b_pyramid = image_pyramid(b)

# we downscale to a reasonable size
ar, red_shift = align_wrapper(r_pyramid, g_pyramid)
ag, green_shift = align_wrapper(g_pyramid, b_pyramid)
                              

# create a color image
im_out = np.dstack([roll_wrapper(r, red_shift[0] + green_shift[0], red_shift[1] + green_shift[1]), 
                    roll_wrapper(g, green_shift[0], green_shift[1]), 
                    b])

# printing the final shifts
print("FINAL SHIFTS")
print((red_shift[0] + green_shift[0], red_shift[1] + green_shift[1]))
print(green_shift)


# save the image
imname_name_string = imname.split('.')[0]
fname = 'out_path/' + imname_name_string + '.jpg'
skio.imsave(fname, im_out)

# display the image
skio.imshow(im_out)
skio.show()