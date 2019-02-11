def contours(img,c):
    '''
        Draw contours on image

    '''
    raise NotImplementedError


def rect(img,corners, color='r',linewidth=3):
    '''
        Draw rectangle on image 

        Add limits according to image dimensions
        Parameters 
        ----------
        corners : list
            ymin,ymax,xmin,xmax
        linewidth : int 
            number of pixels the lines od the rectangle cover. Should 
            be odd.
        Returns 
        -------
    '''
    #get colour in rgb 
    colrgb = [255,0,0] # add a colour function selector here
    # line overlap
    olap        = (linewidth-1)/2
    # Draw top horizontal line 
    img[corners[1]-olap:corners[1]+olap+1,corners[2]:corners[3]] = colrgb
    # Draw bottom horizontal line
    img[corners[0]-olap:corners[0]+olap+1,corners[2]:corners[3]] = colrgb
    # Draw  left vertical line 
    img[corners[0]:corners[1],corners[2]-olap:corners[2]+olap+1] = colrgb
    # Draw  left vertical line 
    img[corners[0]:corners[1],corners[3]-olap:corners[3]+olap+1] = colrgb

    return img

def colourstr2rgb(colorstr):
    '''


    '''
    