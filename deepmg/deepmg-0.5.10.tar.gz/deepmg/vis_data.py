"""
======================================================================================
functions for visualizing data
======================================================================================
Author: Thanh Hai Nguyen, Team Integromics, ICAN, Paris, France'
date: 20/12/2017 (updated to 31/10/2018, stable version)'
'this module includes:
'1. convert_color_real_img: convert data to given hex value (for SPecies Bins (SPB) and PResent (PR) bins)
'2. convert_bin: convert data to index of bin
'3. embed_image: generating images using manifold learning (t-SNE, LDA, PCA...)
'4. fillup_image: generating images using Fill-up
'5. coordinates_fillup: build coordinates for fill-up
"""
#from scipy.misc import imread
import numpy as np
import math

import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
              
def convert_color_real_img(value, debug=0, type='spb', num_bin=10 ):
    """ load and reading images save to data array  (use for abundance data) to create color images
    Args:
        value (float): orginial value
        debug (int): mode of debug
        type (string): spb (based on  abundance distribution) or pr (presence): custom color with hex ONLY for 10 bins
    Returns:
        value of color (hex)
    """
    color_v=0   
    
    #array of 10 colors: index 0 - 10, 0: black, 10: white
    color_arry = ['#000000', '#8B0000','#FF0000','#EE4000', '#FFA500', '#FFFF00','#00CD00', '#0000FF','#00BFFF','#ADD8E6','#FFFFFF'] 
    #break = [1e-07,4e-07,1.6e-06,6.4e-06,2.56e-05,0.0001024,0.0004096,0.0016384,0.0065536]
    if type=='spb':
        if value >= 0.0065536:
            color_v='#000000'
        elif value >= 0.0016384:
            color_v='#8B0000'
        elif value >= 0.0004096:
            color_v='#FF0000'
        elif value >= 0.0001024:
            color_v='#EE4000'
        elif value >= 2.56e-05:
            color_v= '#FFA500'
        elif value >= 6.4e-06:
            color_v= '#FFFF00'
        elif value >= 1.6e-06:
            color_v= '#00CD00'
        elif value >= 4e-07:
            color_v= '#0000FF'
        elif value >= 1e-07:
            color_v= '#00BFFF'        
        elif value > 0:
            color_v=  '#ADD8E6'
        else:
            color_v= 'w'
    elif type=='pr':
        if value >0:
            color_v='black'
        else:
            color_v='w'
   
    else:
        print 'this type ' +str(type) + ' is not supported!!!'
        exit()
        
    if debug==1:
        print(value,color_v)
  #  print(value,color_v)
   # print color_arry[1]
    return color_v

def convert_bin(value, debug=0, type='spb', 
    num_bin=10, max_v=0.0065536, min_v= 1e-07, multi_coef=4, color_img=False ):
    """ load and reading images save to data array  (use for abundance data) to create images
    **notes: ONLY apply to data range 0-1
    Args:
        value (float): orginial value
        debug (int): mode of debug
        type: 'spb' (ONLY support for 10 bins) or 'pr' (2 bins- binary bins) or eqw (Equal Width Binning)
            if 'eqw' : Equal Width Binning with thresold min_v,max_v
                max_v
                min_v
        num_bin : number of bins
        min_v,max_v: range to bin
        multi_coef: use for predefinded bin ('ab')
        color_img : return hex if num_bin=10 and use color images 
    
    Return:
        float if color_img=False, hex if color_img=True
    """
    color_v=0   
    #color_arry_num = [1,0.9,0.8,0.7,0.6, 0.5,0.4,0.3, 0.2,0.1]
    color_arry = ['#000000', '#8B0000','#FF0000','#EE4000', '#FFA500', '#FFFF00','#00CD00', '#0000FF','#00BFFF','#ADD8E6','#FFFFFF'] 
   # if debug==1:        
    #    print str(value) + '_'+ str(max_v)+'_' +str(min_v)
   
    if type == 'spb':
        if value >= (min_v * math.pow(multi_coef, 8)):            
            color_v=1.0
        elif value >= (min_v * math.pow(multi_coef, 7)):
            color_v=0.9
        elif value >= (min_v * math.pow(multi_coef, 6)):
            color_v=0.8
        elif value >= (min_v * math.pow(multi_coef, 5)):
            color_v=0.7
        elif value >= (min_v * math.pow(multi_coef, 4)):
            color_v=0.6
        elif value >= (min_v * math.pow(multi_coef, 3)):
            color_v=0.5
        elif value >= (min_v * math.pow(multi_coef, 2)):
            color_v=0.4
        elif value >= (min_v * math.pow(multi_coef, 1)):
            color_v=0.3
        elif value >= min_v:
            color_v=0.2        
        elif value > 0:
            color_v=0.1
        else:
            color_v= 0
   
    elif type=='pr':
        if value>0:
            color_v=1.0
        else:
            color_v=0
   
    elif type=='eqw':    #Equal Width Binning with a thresold max_v, return color_v is the id of binbin
        #in gray scale in python: 1: white, 0: black --> near 0: dark, near 1: white
        dis_max_min = max_v - min_v     #eg. dis_max_min=0.6
        v_bin = float(dis_max_min / num_bin) #distince between 2 bins, eg. 0.06 if num_bin = 10
        
        if value >= max_v: # old: 'if value > max_v': fixed from 15h30, 7/3
            color_v = num_bin
        elif value <= min_v: # old: 'elif value < min_v or value <= 0': fixed from 15h30, 7/3
            color_v = 0       
        else:
            #dis_min = value - min_v
            #print 'dis_min=' + str(dis_min)
            color_v = math.ceil ((value - min_v)/v_bin) 

        #scale color_v to 0-1, a greater real value will have a bigger color_v
        #print'value' + str(value) + '=min_v=' + str(min_v) + '=max_v=' + str(max_v) + '=v_bin=' + str(v_bin) + '==float((value-min_v)/v_bin)==' + str(math.ceil (float((value-min_v)/v_bin))) + '===color_v===' + str(color_v)
        #print '===color_v===' + str(color_v)        
        #print color_v
        if color_img and num_bin==10: #if use 10 distinct color, return #hex
            color_v = color_arry [ int(num_bin - color_v)]
        else: #if use gray, return real value
            color_v =  float(color_v / num_bin)
            
    else:
        print 'this type '+ str(type) + ' is not supported!!'

    if debug==1:
        print 'min_v=' +str(min_v) + 'max_v' + str(max_v)
        print(value,color_v)

    return color_v    
  
def embed_image(X_embedded, X, name_file, size_p=1, fig_size=4, type_data='spb', 
        marker='ro', num_bin=10, margin = 0, alpha_v=0.5, 
        setcolor ='color', max_v=0.0065536, min_v= 1e-07, dpi_v = 75, colormap='', 
        cmap_vmin=0.0, cmap_vmax =1.0):
    
    """ create an image using manifolds #https://matplotlib.org/api/markers_api.html
    Args:
        X_embedded (array): coordinates of points after manifold
        X (array) : value of data point 
        color_arr (array): array of colors of points
        name_file (string): name image output
        size_p (int): point size
        fig_size=4 (int) : figure size (usually, 1: gives imgages of 84x84, 2: 162x162,...)
        type_data: type of data: spb/pr/eqw
        marker (string): shape of point (refer:https://matplotlib.org/api/markers_api.html), should use 'o' (for large img and if density not high) and ',': pixels (for small images)
        alpha_v (float): mode of transparent 0-1
        num_bin (int): number of bins
        margin (float): margin of image (white border)
        setcolor: color/gray
        [min_v, max_v]: the range to set bins
        dpi_v : dpi of images
        colormap : colormap used to set colors for the image (if ''-->custom set)
        [cmap_vmin, cmap_vmax]: the range to set colors using colormap provided by Python
    Returns:
        an image
    """

    #binning 
    if setcolor=="gray":
        color_arr = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin) for y in X ]   
    else:
        if colormap=='':
            if type_data=="eqw" and num_bin==10: #if forget to set auto_v = 1, then generating black/white/gray images
                color_arr = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin, color_img =True) for y in X ]  
            else:
                color_arr = [convert_color_real_img(y, debug=0, type=type_data) for y in  X ]   
        else:
            color_arr = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin) for y in X ]           
    
    #set options to remove padding/white border
    mpl.rcParams['savefig.pad_inches'] = 0   
    fig, ax = plt.subplots(figsize=(fig_size*1.0/dpi_v,fig_size*1.0/dpi_v), dpi=dpi_v, facecolor='w')   
    #ax.set_axis_bgcolor('w')
    #ax.set_axis_bgcolor('w')
    ax.set_facecolor('w')
    ax.axis('off') #if do not have this, images will appear " strange black point"!!
    ax = plt.axes([0,0,1,1], frameon=False) #refer https://gist.github.com/kylemcdonald/bedcc053db0e7843ef95c531957cb90f
    # Then we disable our xaxis and yaxis completely. If we just say plt.axis('off'),
    # they are still used in the computation of the image padding.
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # Even though our axes (plot region) are set to cover the whole image with [0,0,1,1],
    # by default they leave padding between the plotted data and the frame. We use tigher=True
    # to make sure the data gets scaled to the full extents of the axes.
    plt.autoscale(tight=True) 
    #print fig.get_dpi() #default
    #embbed points
    
    #set lim_max,min in x-axis and y-axis
    x_max = np.max(X_embedded[:,0])
    x_min = np.min(X_embedded[:,0])
    y_max = np.max(X_embedded[:,1])
    y_min = np.min(X_embedded[:,1])

    #variable containing data point <> 0 or not avaiable
    new_color_array = []
    new_X_embedded = []
    
    #if importances_feature <> 'none':
    #    print 'use important feature'
    #     for i in range(0,len(importances_feature)):
    #         print X_embedded[importances_feature [i] ]
    #         print color_arr [importances_feature [i] ]

    #skip white points (which have no information)
    if setcolor=="gray":   
        color_1 =  np.ones(len(color_arr)) - color_arr
        color_1 = [str(i) for i in color_1]
        #print color_1
        for i in range(0,int(len(X_embedded))) :
            if color_1[i] <> '1.0': #in grayscale, '1': white
                new_color_array.append(color_1[i]) #convert to string and scale of gray
                new_X_embedded.append(X_embedded[i])    
    else: #if use color images
        if colormap =='':
            for i in range(0,int(len(X_embedded))) :
                if color_arr[i] <> 'w':
                    new_color_array.append(color_arr [i])
                    new_X_embedded.append(X_embedded[i])   
        else:
            color_1 =  np.ones(len(color_arr)) - color_arr           
            for i in range(0,int(len(X_embedded))) :
                if color_1[i] <> 1.0: #in grayscale, 1: white
                    new_color_array.append(color_1[i]) #convert to string and scale of gray
                    new_X_embedded.append(X_embedded[i]) 
            

    new_X_embedded= np.stack(new_X_embedded)
    #print 'len(new_X_embedded)=' + str(len(new_X_embedded))
    #print 'len(new_color_array)=' + str(len(new_color_array))
    #print new_color_array
    #print len(new_X_embedded)
    if colormap=='': #if use predefined color or grayscale
        ax.scatter(new_X_embedded[:,0],new_X_embedded[:,1], s=size_p, marker = marker,color=new_color_array, edgecolors='none', alpha = alpha_v)          
    else:       
        if not(colormap in ['viridis','rainbow','gist_rainbow','jet','nipy_spectral','Paired','Reds','YlGnBu',
                        'viridis_r','rainbow_r','gist_rainbow_r','jet_r','nipy_spectral_r','Paired_r','Reds_r','YlGnBu_r']):             
            print 'colormap ' +str(colormap) + ' is not supported!!'
            exit()            
        #ax.scatter(new_X_embedded[:,0],new_X_embedded[:,1], s=size_p, marker = marker,c=new_color_array, edgecolors='none', alpha = alpha_v, cmap=cmap)        
        #ax.scatter(new_X_embedded[:,0],new_X_embedded[:,1], s=size_p, marker = marker,c=new_color_array, edgecolors='none', alpha = alpha_v, cmap=plt.get_cmap(colormap))        
        if cmap_vmax == cmap_vmin:
             ax.scatter(new_X_embedded[:,0],new_X_embedded[:,1], s=size_p, marker = marker,c=new_color_array, edgecolors='none', alpha = alpha_v, cmap=plt.get_cmap(colormap),vmin=cmap_vmax/num_bin,vmax=cmap_vmax)      
        else:
            ax.scatter(new_X_embedded[:,0],new_X_embedded[:,1], s=size_p, marker = marker,c=new_color_array, edgecolors='none', alpha = alpha_v, cmap=plt.get_cmap(colormap),vmin=cmap_vmin,vmax=cmap_vmax)      
  
    #fixing the same positions for all images  
    plt.xlim([x_min - margin, x_max + margin])
    plt.ylim([y_min - margin, y_max + margin])
    fig.savefig(name_file+'.png') ##True to see "not available area (unused area)"    
    plt.close('all')
  
def fillup_image(X, name_file, fig_size, size_p=1, cor_x=0,cor_y=0, marker_p='ro', type_data='spb', setcolor="color", 
        max_v=0.0065536, min_v= 1e-07, num_bin = 10, dpi_v = 75, alpha_v=0.5, colormap='',cmap_vmin=0.0, cmap_vmax=1.0):
    """ create an image using fillup 
    Args:       
        X (array): value of data point    
        name_file (string): name image output
        fig_size=4 (int) : figure size (usually, 1: gives imgages of 84x84, 2: 162x162,...), 
            to compute/convert inches-pixel look at http://auctionrepair.com/pixels.html, 
                Pixels / DPI = Inches
                Inches * DPI = Pixels
        size_p (int): point size
        type_data (string): type of data (abundance: spb or presence: pr)
        setcolor: color/gray
        cor_x (float): coordinates of x
        cor_y (float): coordinates of y
        marker_p (string): shape of point (refer to :https://matplotlib.org/api/markers_api.html), should use 'o' (for large img and if density not high) and ',': pixels (for small images)
        [min_v, max_v]: the range to set bins
        dpi_v (int): dpi of images
        colormap : colormap used to set colors for the image (if ''-->custom set)
            colormap for color images (refer to https://matplotlib.org/examples/color/colormaps_reference.html)
        [cmap_vmin, cmap_vmax]: the range to set colors using colormap provided by Python
        
    Returns:
        an image
    """
    #get bins for features
    if setcolor=="gray":
        colors = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin) for y in X ]   
        #print 'use gray'
        #print X.shape
    else:
        if colormap == '':
            if (type_data=="eqw" and num_bin == 10):  #if use color, eqw: 10 distinct color
                colors = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin, color_img =True) for y in X ]  
            else:
                colors = [convert_color_real_img(y, debug=0, type=type_data) for y in  X ]
        else:
            #print 'use colormap'
            #colors = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin) for y in X ]   
            colors = [convert_bin(y, debug=0, type=type_data, min_v = min_v, max_v = max_v, num_bin = num_bin) for y in X ] 
            #print   colors
            #print X.shape
            #print '#use colormap'
    #fig, ax = plt.subplots(figsize=(fig_size,fig_size), facecolor='w')
    
    #set the size of images
    mpl.rcParams['savefig.pad_inches'] = 0   
    fig, ax = plt.subplots(figsize=(fig_size*1.0/dpi_v,fig_size*1.0/dpi_v), dpi=dpi_v, facecolor='w')   
    #ax.set_axis_bgcolor('w')
    ax.set_facecolor('w')

    #eliminate border/padding
    ax.axis('off') #if do not have this, images will appear " strange black point"!!
    ax = plt.axes([0,0,1,1], frameon=False) #refer https://gist.github.com/kylemcdonald/bedcc053db0e7843ef95c531957cb90f
    # Then we disable our xaxis and yaxis completely. If we just say plt.axis('off'),
    # they are still used in the computation of the image padding.
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # Even though our axes (plot region) are set to cover the whole image with [0,0,1,1],
    # by default they leave padding between the plotted data and the frame. We use tigher=True
    # to make sure the data gets scaled to the full extents of the axes.
    plt.autoscale(tight=True) 
    #print fig.get_dpi() #default
    
    
    #size_fig: eg. t2d: 23.9165214862 -> matrix 24x24
    #draw images
    if setcolor=="gray":                     
        #ax.scatter(cor_x,cor_y, marker = marker_p, color=str( 1 - colors))
        color_1 =  np.ones(len(colors)) - colors
        color_1 = [str(i) for i in color_1]
        #print colors
        #print np.max(colors)
        #print color_1
        ax.scatter(cor_x,cor_y, s=size_p, marker = marker_p,color=color_1, edgecolors='none', alpha = alpha_v)

        #ax.plot(cor_x,cor_y, marker_p, color=str( 1 - colors), markersize=size_p)
    else:           
        #print colors
        # refer to https://pythonspot.com/matplotlib-scatterplot/
        if colormap=='': #if use predefined color
            ax.scatter(cor_x,cor_y, s=size_p, marker = marker_p,color=colors, edgecolors='none', alpha = alpha_v)
        else: 
           
            if not(colormap in ['viridis','rainbow','gist_rainbow','jet','nipy_spectral','Paired','Reds','YlGnBu',
                        'viridis_r','rainbow_r','gist_rainbow_r','jet_r','nipy_spectral_r','Paired_r','Reds_r','YlGnBu_r']):             
                print 'colormap ' +str(colormap) + ' is not supported!!'
                exit()
            
            #print 'colormap ' +str(colormap) + ' selected!'
            #colors = np.stack(colors)
            #print colors
            #color_1 =  np.ones(len(colors)) - colors
            
            #set lim_max,min in x-axis and y-axis
            x_max = np.max(cor_x)
            x_min = np.min(cor_x)
            y_max = np.max(cor_y)
            y_min = np.min(cor_y)

            cor_x_new =[]
            cor_y_new =[]
            color_new = []
            #skip value = 0
            for i in range(0,int(len(colors))) : #remove point with value = 0
                if colors[i] <> 0.0: #in grayscale, 1: white
                    color_new.append(1-colors[i]) #convert to string and scale of gray
                    cor_x_new.append(cor_x[i]) 
                    cor_y_new.append(cor_y[i]) 
            #color_1 = [str(i) for i in color_1]
           # ax.scatter(cor_x_new,cor_y_new, s=size_p, marker = marker_p,c=color_new, edgecolors='none', alpha = alpha_v,cmap=cmap)
            #ax.scatter(cor_x_new,cor_y_new, s=size_p, marker = marker_p,c=color_new, edgecolors='none', alpha = alpha_v,cmap=plt.get_cmap(colormap))
            #ax.scatter(cor_x_new,cor_y_new, s=size_p, marker = marker_p,c=color_new, edgecolors='none', alpha = alpha_v,cmap=plt.get_cmap(colormap),vmin=1.0/num_bin,vmax=1)
            if cmap_vmax == cmap_vmin:
                ax.scatter(cor_x_new,cor_y_new, s=size_p, marker = marker_p,c=color_new, edgecolors='none', alpha = alpha_v,cmap=plt.get_cmap(colormap),vmin=cmap_vmax/num_bin,vmax=cmap_vmax)
            else:              
                ax.scatter(cor_x_new,cor_y_new, s=size_p, marker = marker_p,c=color_new, edgecolors='none', alpha = alpha_v,cmap=plt.get_cmap(colormap),vmin=cmap_vmin,vmax=cmap_vmax)
          
          
            #this code to keep the same positions for all images belongging to a dataset
            plt.xlim([x_min, x_max])
            plt.ylim([y_min, y_max])
    
    #create image
    fig.savefig(name_file+'.png')#, transparent=False) ##True to see "not available area (unused area)"    
    plt.close('all')

def coordinates_fillup(num_features):
    cordi_x = []
    cordi_y = []   
    #build coordinates for fill-up with a square of len_square*len_square
    len_square = int(math.ceil(math.sqrt(num_features)))
    print 'square_fit_features=' + str(len_square) 
    k = 0
    for i in range(0,len_square):
        for j in range(0,len_square):                
            if k == (num_features):
                break
            else:
                cordi_x.append(j*(-1))
                cordi_y.append(i*(-1))
                k = k+1
        if k == (num_features):
            break
    print '#features=' +str(k)
    return cordi_x, cordi_y
   