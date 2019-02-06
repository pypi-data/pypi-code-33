import matplotlib.pyplot as plt

def FKLSetNewFigure(figsize=(8,5),xlabel="x",ylabel="y",style="ggplot"):
    plt.figure(figsize=figsize) 
    plt.style.use(style)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    return 
def FKLSaveFigure(save_path=None):
    if(type(save_path)==str):
        plt.savefig(save_path)
    return 
def FKLShow():
    plt.show()
    return 
def FKLBar(x,y,width=0.5,color="gray"):
    plt.bar(left=x,height=y,width=width,color=color)
    return 
def FKLDot(x,y,color="gray"):
    plt.plot(x,y,"o",color=color)
    return     
def FKLLine(x,y,color="gray"):
    plt.plot(x,y,"-",color=color)
    return 
