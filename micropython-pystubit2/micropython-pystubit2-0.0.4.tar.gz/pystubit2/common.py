


def _rgb_24bit(color):
  r = max(min(color[0],255),0)
  g = max(min(color[1],255),0)
  b = max(min(color[2],255),0)
  return (r<<16)+(g<<8)+(b)

def _24bit_rgb(val24):
  r = (val24 >> 16) & 0x000000ff
  g = (val24 >>  8) & 0x000000ff
  b =  val24        & 0x000000ff
  return r,g,b

def _coord_line():
  pass
  
def _line_coord():
  pass
  
