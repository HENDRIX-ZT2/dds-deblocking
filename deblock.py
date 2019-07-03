
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import colorspace 

import imageio

def deblock( rgba ):
	dtype = rgba.dtype
	height, width, depth = rgba.shape
	rgb = rgba[:,:,:3]
	
	# convert to YUV colorspace so luminance is separated from chroma
	yuv = colorspace.RGB2YUV( rgb )
	
	# blur chroma
	# ndimage.filters.uniform_filter(yuv[:,:,1], size=4, output=yuv[:,:,1])#, origin=(-1,-1) )
	# ndimage.filters.uniform_filter(yuv[:,:,2], size=4, output=yuv[:,:,2])#, origin=(-1,-1) )
	ndimage.gaussian_filter(yuv[:,:,1], sigma=1.5, output=yuv[:,:,1])#, origin=(-1,-1) )
	ndimage.gaussian_filter(yuv[:,:,2], sigma=1.5, output=yuv[:,:,2])#, origin=(-1,-1) )
	
	blockiness_h = np.zeros( (height, width), dtype=dtype )
	blockiness_v = np.zeros( (height, width), dtype=dtype )
	
	# detect block edges on luminance
	Th = 60
	lum = yuv[:,:,0]
	#horizontal blockiness
	for x in range(0, width-4, 1):
		for y in range(0, height-4, 4):
			A = (lum[y,x] - lum[y+1,x]) - (lum[y-1,x] - lum[y,x])
			B = (lum[y,x] - lum[y+1,x]) - (lum[y+1,x] - lum[y-2,x])
			g = False if (A < Th) and (B < Th) else True
			blockiness_h[y,x] = g
			blockiness_h[y+1,x] = g
			
	#vertical blockiness
	for x in range(0, width-4, 4):
		for y in range(0, height-4, 1):
			C = (lum[y,x] - lum[y,x+1]) - (lum[y,x-1] - lum[y,x])
			D = (lum[y,x] - lum[y,x+1]) - (lum[y,x+1] - lum[y,x-2])
			h = False if (C < Th) and (D < Th) else True
			blockiness_v[y,x] = h
			blockiness_v[y,x+1] = h
	blockiness = blockiness_h + blockiness_v
	
	# replace block edges by blurred luminance
	yuv[:,:,0] = np.where( blockiness, ndimage.gaussian_filter(yuv[:,:,0], sigma=.3 ), yuv[:,:,0]  )
	
	plt.imshow(blockiness, interpolation='nearest')
	plt.show()
	
	# convert back to rgb
	rgb_out = colorspace.YUV2RGB( yuv ).astype(dtype)
	return rgb_out
	
	

file = "TyrannosaurusRex_Adult_M.dds"
# file = "Capelin_Adult_F.png"
im = imageio.imread(file)
deblocked = deblock(im)
imageio.imwrite('test.png', deblocked)