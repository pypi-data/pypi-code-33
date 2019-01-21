#import matplotlib
#matplotlib.use('agg')
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import sys
import matplotlib.colors as mcolors
import os
import collections
import math
import seaborn as sns
import libplot
from libsparse.libsparse import SparseDataFrame
from numpy import ndarray
import pandas as pd

s=80
alpha=0.8

PATIENT_082917_COLOR = 'mediumorchid'
PATIENT_082917_EDGE_COLOR = 'purple'

PATIENT_082217_COLOR = 'gold'
PATIENT_082217_EDGE_COLOR = 'goldenrod'

PATIENT_011018_COLOR = 'mediumturquoise'
PATIENT_011018_EDGE_COLOR = 'darkcyan'

PATIENT_013118_COLOR = 'salmon'
PATIENT_013118_EDGE_COLOR = 'darkred'

EDGE_COLOR = 'dimgray'
MARKER_SIZE = 40
ALPHA=0.8

C3_COLORS = ['tomato', 'mediumseagreen', 'royalblue']
EDGE_COLORS = ['darkred', 'darkgreen', 'darkblue']


PCA_RANDOM_STATE = 0


def pca(data, n=50, exclude=[], mode='random'):
    """
    Setup the PCA on a data set
    """
  
    # remove rows containing all zeros
    #data = remove_empty_rows(data) # data[(data.T != 0).any()]
  
    print('New size {}'.format(data.shape))
  
    #if tpmmode:
    #  print('Converting to tpm...')
    #  data = tpm(data)
  
    # In log mode, convert to log2 tpm
    #if logmode:
    #  print('Converting to log2...')
    #  data = log2(data)
    
    
    #data = data.values #as_matrix()

      # Scale between 0 and 1
      #data_std = StandardScaler().fit_transform(datat)
  
    data = data.T #np.transpose(data)
  
    print('tranpose {}'.format(data.shape))
  
    # Perform PCA
  
    if isinstance(data, SparseDataFrame):
        print('PCA sparse mode')
        pca = TruncatedSVD(n_components=n, random_state=PCA_RANDOM_STATE)
    elif mode == 'full':
        print('PCA full mode')
        pca = PCA(n_components=n, svd_solver='full', random_state=PCA_RANDOM_STATE)
    else:
        print('PCA random mode')
        # Use the default random, faster solver
        pca = PCA(n_components=n, random_state=PCA_RANDOM_STATE)
    
    if isinstance(data, SparseDataFrame):
        pca_results = pca.fit_transform(data.matrix) #libsparse.SparseDataFrame(pca.fit_transform(data.matrix), data.index, data.columns)
    else:
        pca_results = pca.fit_transform(data) #data_std) #datat)
  
    if len(exclude) > 0:
        # filter
        pca_results = pca_results[:, np.where(np.in1d(list(range(0, n)), exclude, invert=True))[0]]
  
    print(pca_results.shape)
  
    return pca, pca_results


def lighter(color, percent):
  '''assumes color is rgb between (0, 0, 0) and (255, 255, 255)'''
  color = np.array(color)
  white = np.array([255, 255, 255])
  vector = white-color
  
  return color + vector * percent
    

def draw_ellipse(position, covariance, ax=None, **kwargs):
    """Draw an ellipse with a given position and covariance"""
    ax = ax or plt.gca()
    
    # Convert covariance to principal axes
    if covariance.shape == (2, 2):
      U, s, Vt = np.linalg.svd(covariance)
      angle = np.degrees(np.arctan2(U[1, 0], U[0, 0]))
      width, height = 2 * np.sqrt(s)
    else:
      angle = 0
      width, height = 2 * np.sqrt(covariance)
    
    # Draw the Ellipse
    for nsig in range(1, 3):
      ax.add_patch(Ellipse(position, nsig * width, nsig * height, angle, **kwargs))

      
                         
        
def plot_gmm(gmm, X, colors, colormap, label=True, ax=None):
  ax = ax or plt.gca()
  labels = gmm.fit(X).predict(X)
  
  if label:
      #ax.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', zorder=2)
      ax.scatter(X[:, 0], X[:, 1], c=labels, cmap=colormap, s=MARKER_SIZE, alpha=ALPHA, zorder=2, norm=mcolors.Normalize(vmin=0, vmax=7))
  else:
      ax.scatter(X[:, 0], X[:, 1], alpha=alpha, s=MARKER_SIZE, zorder=2)
  
  #ax.axis('equal')
  
  w_factor = 0.4 / gmm.weights_.max()
  
  for i in range(0, len(gmm.means_)):
    pos = gmm.means_[i]
    covar = gmm.covariances_[i]
    w = gmm.weights_[i]
    color = colors[i]
    
    #w in zip(gmm.means_, gmm.covariances_, gmm.weights_
    #for pos, covar, w in zip(gmm.means_, gmm.covariances_, gmm.weights_):
    
    sys.stderr.write("w " + str(w) + "\n")
    draw_ellipse(pos, covar, facecolor=color, alpha=w * w_factor)

  return labels


def plot_cluster_ellipses(gmm, X, colors, ax=None):
  ax = ax or plt.gca()
  labels = gmm.fit(X).predict(X)
  
  w_factor = 0.25 / gmm.weights_.max()
  
  for i in range(0, len(gmm.means_)):
    pos = gmm.means_[i]
    covar = gmm.covariances_[i]
    w = gmm.weights_[i]
    color = 'dimgray' #colors[i]
    
    draw_ellipse(pos, covar, edgecolor=color, facecolor='none', alpha=0.5) #(w * w_factor))

  return labels


def draw_outline(x, y, ax, color):
  points = np.transpose([x, y])
  
  print("points", str(len(points)))
  
  hull = ConvexHull(points)
  
   # close the polygon shape
  vertices = np.append(hull.vertices, hull.vertices[0])
  
  points = points[vertices]
  
  x = points[:, 0]
  y = points[:, 1]
  
  ax.plot(x, y, '--', lw=1, color=color, alpha=0.5)
  
  return x, y
  
  #t = np.arange(len(x))
  #ti = np.linspace(0, t.max(), 200)

  #xi = interp1d(t, x, kind='cubic')(ti)
  #yi = interp1d(t, y, kind='cubic')(ti)
  
  #ax.plot(xi, yi, '--', lw=1, color=color, alpha=0.4)
  
  #return xi, yi
  
 
def fill_outline(x, y, ax, color):
  x, y = draw_outline(x, y, ax, color)
  
  plt.fill(x, y, color=color, alpha=0.15)
  
  
def plot_cluster_outlines(gmm, X, colors, colormap, lz_indices, dz_indices, ax=None):
  ax = ax or plt.gca()
  labels = gmm.fit(X).predict(X)
  
  #
  # LZ
  #
  
  # red
  indices = np.intersect1d(lz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'red')
   
  # green
  indices = np.intersect1d(lz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'green')
    
  # blue
  indices = np.intersect1d(lz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'blue')
  
  #
  # DZ
  #
  
  # red
  indices = np.intersect1d(dz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'red')
    
  # green
  indices = np.intersect1d(dz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'green')
    
  # blue
  indices = np.intersect1d(dz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    draw_outline(x1, x2, ax, 'blue')

  return labels


def plot_gmm2(gmm, X, colors, colormap, lz_indices, dz_indices, ax=None):
  ax = ax or plt.gca()
  labels = gmm.fit(X).predict(X)
  
  w_factor = 0.25 / gmm.weights_.max()
  
  for i in range(0, len(gmm.means_)):
    pos = gmm.means_[i]
    covar = gmm.covariances_[i]
    w = gmm.weights_[i]
    color = colors[i]
    
    draw_ellipse(pos, covar, facecolor=color, alpha=(w * w_factor))
  
  #
  # LZ
  #
  
  # red
  indices = np.intersect1d(lz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='tomato', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[0], alpha=ALPHA, zorder=10)
   
    
  # green
  indices = np.intersect1d(lz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='mediumseagreen', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[1], alpha=ALPHA, zorder=10)
    
  # blue
  indices = np.intersect1d(lz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='royalblue', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[2], alpha=ALPHA, zorder=10)
  
  #
  # DZ
  #
  
  # red
  indices = np.intersect1d(dz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='tomato', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[0], alpha=ALPHA, zorder=10)
    
  # green
  indices = np.intersect1d(dz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='mediumseagreen', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[1], alpha=ALPHA, zorder=10)
    
  # blue
  indices = np.intersect1d(dz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='royalblue', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[2], alpha=ALPHA, zorder=10)

  return labels

  

def plot_gmm3(gmm, X, colors, colormap, lz_indices, dz_indices, ax=None):
  ax = ax or plt.gca()
  labels = gmm.fit(X).predict(X)
  
  #
  # Outlines
  #
  
  lz_dz_indices = lz_indices + dz_indices
  
  indices = np.intersect1d(lz_dz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    fill_outline(x1, x2, ax, 'red')
   
  # green
  indices = np.intersect1d(lz_dz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    fill_outline(x1, x2, ax, 'green')
    
  # blue
  indices = np.intersect1d(lz_dz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    fill_outline(x1, x2, ax, 'blue')
  
  
  
  #
  # LZ
  #
  
  # red
  indices = np.intersect1d(lz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='tomato', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[0], alpha=ALPHA, zorder=10)
   
  # green
  indices = np.intersect1d(lz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='mediumseagreen', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[1], alpha=ALPHA, zorder=10)
    
  # blue
  indices = np.intersect1d(lz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='royalblue', s=MARKER_SIZE, marker='^', edgecolor=EDGE_COLORS[2], alpha=ALPHA, zorder=10)
  
  #
  # DZ
  #
  
  # red
  indices = np.intersect1d(dz_indices, label_indices(labels, 0))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='tomato', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[0], alpha=ALPHA, zorder=10)
    
    
  # green
  indices = np.intersect1d(dz_indices, label_indices(labels, 1))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='mediumseagreen', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[1], alpha=ALPHA, zorder=10)
    
  # blue
  indices = np.intersect1d(dz_indices, label_indices(labels, 2))
  
  if len(indices) > 0:
    x1, x2 = filter_x(X, 0, 1, indices)
    l = np.take(labels, indices)
    ax.scatter(x1, x2, color='royalblue', s=MARKER_SIZE, marker='o', edgecolor=EDGE_COLORS[2], alpha=ALPHA, zorder=10)

  return labels


def plot_louvain(labels, X, colors, lz_indices, dz_indices, ax):
  # How many labels to cycle through (it cannot exceed the number of colors)
  
  labeln = min(len(colors), np.max(labels) + 1)
  
  for l in range(0, labeln):
    li = label_indices(labels, l)
    
    indices = np.intersect1d(lz_indices, li)
  
    if len(indices) > 0:
      x1, x2 = filter_x(X, 0, 1, indices)
      ax.scatter(x1, x2, color=colors[l], edgecolor=colors[l], s=MARKER_SIZE, marker='^', alpha=0.8, zorder=10)
      
    indices = np.intersect1d(dz_indices, li)
  
    if len(indices) > 0:
      x1, x2 = filter_x(X, 0, 1, indices)
      ax.scatter(x1, x2, color=colors[l], edgecolor=colors[l], s=MARKER_SIZE, marker='o', alpha=0.8, zorder=10)
      
  
def plot_louvain_lz_dz(labels, X, colors, lz_indices, dz_indices, ax):
  # How many labels to cycle through (it cannot exceed the number of colors)
  print(len(colors))
  print(np.max(labels))
  labeln = min(len(colors), np.max(labels) + 1)
  
  for l in range(0, labeln):
    li = label_indices(labels, l)
    
    indices = np.intersect1d(lz_indices, li)
  
    if len(indices) > 0:
      x1, x2 = filter_x(X, 0, 1, indices)
      ax.scatter(x1, x2, color='white', edgecolor='black', s=MARKER_SIZE, marker='^', alpha=0.7, zorder=10)
      
    indices = np.intersect1d(dz_indices, li)
  
    if len(indices) > 0:
      x1, x2 = filter_x(X, 0, 1, indices)
      ax.scatter(x1, x2, color='white', edgecolor='black', s=MARKER_SIZE, marker='o', alpha=0.7, zorder=10)
      
  
def label_indices(labels, l):
  return np.where(labels == l)[0]
  
  
#def make_colormap():
#  colors = []
#  colors.append('red')
#  colors.append('green')
#  colors.append('blue')
#  colors.append('orange')
#  colors.append('violet')
#  colors.append('gold')
#  colors.append('gray')
#  colors.append('black')
#  
#  return [colors, mcolors.ListedColormap(colors, name='gmm')]


def colors():
    l = list(plt.cm.tab20.colors)
  
    ret = []
  
    for i in range(0, 20, 2):
        # skip gray
        if i == 14:
            continue
      
        ret.append(l[i])
        
    for i in range(0, 20, 2):
        if i == 14:
            continue
      
        ret.append(l[i + 1])    

  
    #ret = list(plt.cm.tab10.colors)
    #ret.extend(list(plt.cm.Set3.colors))
    ret.extend(list(plt.cm.Dark2.colors))
  
    #ret.extend(list(plt.cm.Dark2.colors))
    #ret.extend(list(plt.cm.Set2.colors))
  
    return ret


def colormap(n=-1):
    c = colors()
    
    if n > 0:
        c = c[0:n]
    
    return mcolors.ListedColormap(c, name='cluster')

def write_tables(data, labels, colors, clusters, prefix):
  ulabels = set(labels)

  for label in sorted(ulabels):
    indices = np.where(labels == label)
    
    d = data[data.columns[indices]]
    
    file = prefix + "_c" + str(clusters) + "_" + colors[label] + ".txt"
    
    print(file)
    
    d.to_csv(file, sep="\t", header=True, index=True)
    
    #print indices


def write_groups(data, labels, colors, clusters, prefix):
  ulabels = set(labels)
  
  dir = 'c' + str(clusters)
  
  if not os.path.exists(dir):
    os.makedirs(dir)

  for label in sorted(ulabels):
    indices = np.where(labels == label)
    
    d = data[data.columns[indices]]
    
    file = dir + '/' + prefix + "_c" + str(clusters) + "_" + colors[label] + ".txt"
    
    print(file)
    
    #d.to_csv(file, sep="\t", header=True, index=True)
    
    f = open(file, 'w')
    
    f.write("Sample ID\n")
    
    for c in data.columns.values[indices]:
      f.write(c + "\n")
    
    f.close()
    
    
def find_indices(df, search):
  return np.where(df.columns.str.contains(search))[0].tolist() # pca = pca.T [df.columns.get_loc(c) for c in df.filter(like=search).columns]


#def format_axes(ax):
#  ax.spines['right'].set_visible(False)
#  ax.spines['top'].set_visible(False)
#  ax.spines['bottom'].set_color('dimgray')
#  ax.spines['left'].set_color('dimgray')
#  ax.minorticks_on()
#  ax.get_yaxis().set_tick_params(which='both', direction='in')
#  ax.get_xaxis().set_tick_params(which='both', direction='in')
  

def format_legend(ax, cols=6, markerscale=None):
  ax.legend(bbox_to_anchor=[0, 0.95], loc='lower left', ncol=cols, frameon=False, fontsize='small', markerscale=markerscale, handlelength=1, columnspacing=0.5)

def format_legend_2(ax):
  ax.legend(bbox_to_anchor=[0.95, 0.95], loc='lower left', ncol=1, frameon=False, fontsize='small', handlelength=1, columnspacing=1)


def make_figure(w=8, h=8):
  """
  Make a figure of uniform size
  """
  fig = plt.figure(figsize=(w, h))
  ax = fig.add_subplot(1, 1, 1)
  
  return [fig, ax]
  

def plot_setup():
  libplot.setup()
  
  
def save_plot(fig, out, pad=3):
  fig.tight_layout(pad=pad) #rect=[o, o, w, w])

  plt.savefig(out, dpi=600)


def filter_x(x, c1, c2, indices):
  x1 = np.take(x[:, c1], indices)
  x2 = np.take(x[:, c2], indices)
  
  return x1, x2


def filter_log2(data):
  datat = data[(data.T != 0).any()]
  
  # Transpose for PCA
  datat = datat.transpose().as_matrix()
  # Add 1 for log
  datat += 1
  datat = np.log2(datat)
  
  return datat


def log2(data):
  #data = data.as_matrix()
  # Add 1 for log
  #data += 1
  #data = np.log2(data)
  
  return (data + 1).apply(np.log2)


def tpm(data):
  return data / data.sum(axis=0) * 1000000



def remove_empty_cols(data):
    if isinstance(data, SparseDataFrame):
        return data.remove_empty_cols()
    else:
        if isinstance(data, ndarray):
            data = pd.DataFrame(data)
            
        #return data.loc[(data != 0).any(1)]
        ret = data.loc[:, data.sum(axis=0) != 0]
        
        return ret
    
def remove_empty_rows(data):
    return remove_empty_cols(data.T).T
    
def remove_empty_cells(data):
    return remove_empty_cols(remove_empty_rows(data))
    
  
def format_axes(ax, title="t-SNE", d1=1, d2=2, subtitle1="", subtitle2=""):
    if subtitle1 != "":
        ax.set_xlabel('{} {} ({})'.format(title, d1, subtitle1))
    else:
        ax.set_xlabel('{} {}'.format(title, d1))
  
    if subtitle2 != "":
        ax.set_ylabel('{} {} ({})'.format(title, d2, subtitle2))
    else:
        ax.set_ylabel('{} {}'.format(title, d2))
  
    
def format_simple_axes(ax, title="t-SNE", d1=1, d2=2, subtitle1="", subtitle2=""):
  libplot.invisible_axes(ax)
  
  ax.annotate('',
    xy=(40, 0),  # theta, radius
    xytext=(-2, 0),
    xycoords='axes pixels',
    textcoords='axes pixels',
    arrowprops=dict(arrowstyle='->', facecolor='black'), zorder=1000)
  
  
  ax.annotate('',
    xy=(0, 40),  # theta, radius
    xytext=(0, -2),
    xycoords='axes pixels',
    textcoords='axes pixels',
    arrowprops=dict(arrowstyle='->', facecolor='black'), zorder=1000)
  
  if subtitle1 != "":
    ax.text(0, -0.04, '{} {} ({})'.format(title, d1, subtitle1), transform=ax.transAxes)
  else:
    ax.text(0, -0.04, '{} {}'.format(title, d1), transform=ax.transAxes)
  
  if subtitle2 != "":
    ax.text(-0.04, 0, '{} {} ({})'.format(title, d2, subtitle2), va='bottom', transform=ax.transAxes, rotation=90)
  else:
    ax.text(-0.04, 0, '{} {}'.format(title, d2), va='bottom', transform=ax.transAxes, rotation=90)




    
    
def write_group_exp(data, labels, colors, prefix="tsne"):
  ulabels = set(labels)
  
  for label in sorted(ulabels):
    indices = np.where(labels == label)[0]
    
    file = '{}_exp_{}.txt'.format(prefix, label + 1)
    
    print(indices)
    print(data.shape)
    
    d = data.take(indices, axis=1)
    
    print(file)
    
    d.to_csv(file, sep="\t", header=True, index=True)
    
    #f = open(file, 'w')
    
    #f.write("Sample ID\n")
    
    #for c in data.columns.values[indices]:
    #  f.write(c + "\n")
    
    #f.close()
  
  
def write_tsne_groups(data, labels, name):
  ulabels = set(labels)
  
  for label in sorted(ulabels):
    indices = np.where(labels == label)
    
    file = 'tsne_{}_{}.txt'.format(name, label + 1)
    
    #d.to_csv(file, sep="\t", header=True, index=True)
    
    f = open(file, 'w')
    
    f.write("Sample ID\n")
    
    for c in data.columns.values[indices]:
      f.write(c + "\n")
    
    f.close()
    

def shannon_diversity_mode(labels, indices_map):
  """
  Diversity in LZ
  """
  
  label_ids = set(labels)
  
  label_indices_map = collections.defaultdict(list)
  
  
  
  # indices per label
  for l in label_ids:
    indices = np.where(labels == l)[0]
    label_indices_map[l] = indices
  
  score_map = collections.defaultdict(float)
  
  lz_map = collections.defaultdict(lambda: collections.defaultdict(int))
  
  for l in label_ids:
    count_map = collections.defaultdict(int)
    
    label_indices = label_indices_map[l]
    
    n = len(label_indices)
    
    for p in indices_map:
      for mode in indices_map[p]:
        if mode == 'all':
          continue
        
        indices = indices_map[p][mode]
      
        # intersect to find proportions
        overlap = np.intersect1d(label_indices, indices)
        
        c = len(overlap)
        
        count_map[mode] += c
        
        lz_map[l][mode] += c
  
    h = 0
  
    for mode in count_map:
      d = count_map[mode] / n
      
      if d > 0:
        h += d * math.log(d)

    h *= -1
    
    score_map[l] = h
    
  ret = np.zeros(len(labels))
  
  for l in label_ids:
    indices = label_indices_map[l]
    ret[indices] = score_map[l]
  
  return ret, score_map, lz_map


def shannon_diversity(labels, indices_map, name):
  
  
  label_ids = set(labels)
  
  label_indices_map = collections.defaultdict(list)
  
  #
  # Diversity between patients
  #
  
  score_map = collections.defaultdict(float)
  
  patient_map = collections.defaultdict(lambda: collections.defaultdict(int))
  
  # indices per label
  for l in label_ids:
    indices = np.where(labels == l)[0]
    label_indices_map[l] = indices
  
  for l in label_ids:
    count_map = collections.defaultdict(int)
    
    label_indices = label_indices_map[l]
    
    n = len(label_indices)
    
    for p in indices_map:
      indices = indices_map[p]['all']
      
      # intersect to find proportions
      overlap = np.intersect1d(label_indices, indices)
      
      size = len(overlap)
      
      count_map[p] += size
      
      patient_map[l][p] += size
  
    h = 0
  
    for p in indices_map:
      d = count_map[p] / n
      
      if d > 0:
        h += d * math.log(d)

    h *= -1
    
    score_map[l] = h
    
  ret = np.zeros(len(labels))
  
  s = 0
  
  for l in label_ids:
    indices = label_indices_map[l]
    
    ret[indices] = score_map[l]
    
    s += len(indices)
    
  # LZ/DZ diversity
  ret_lz, score_map_lz, lz_map = shannon_diversity_mode(labels, indices_map)

  #
  # Write
  #
  
  f = open('diversity_{}.txt'.format(name), 'w')
  
  h1 = '{} patients'.format(';'.join([p for p in sorted(indices_map)]))
  
  f.write('cluster\tsize\t{}\tpatient diversity\tlz;dz sizes\tlz;dz diversity\n'.format(h1))
  
  for l in sorted(score_map):
    patients = ";".join([str(patient_map[l][p]) for p in sorted(indices_map)])
    
    modes = ";".join([str(lz_map[l]['lz']), str(lz_map[l]['dz'])])
    
    f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(l + 1, len(label_indices_map[l]), patients, score_map[l], modes, score_map_lz[l]))
  
  f.close()
  
  return ret, ret_lz




def correlation_plot(x, y, clusters, name, marker='o', s=MARKER_SIZE, xlabel='', ylabel='', fig=None, ax=None):
    """
    Create a tsne plot without the formatting
    """
    
    c = colors()
  
    if ax is None:
        fig, ax = libplot.new_fig()
      
    ids = list(sorted(set(clusters['Cluster'])))
      
    for i in range(0, len(ids)):
        l = ids[i]
        
        print('Label {}'.format(l))
        indices = np.where(clusters['Cluster'] == l)[0]
        
        n = len(indices)
        
        label = 'C{} ({:,})'.format(l, n)
    
        x1 = np.take(x, indices)
        y1 = np.take(y, indices)
          
        ax.scatter(x1, y1, color=c[i], edgecolor=c[i], s=s, marker=marker, alpha=0.8, label=label)
    
    sns.regplot(np.array(x), np.array(y), ax=ax, scatter=False)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    format_legend(ax)
    
    return fig, ax


def scatter_clusters(x, \
                     y, \
                     clusters, \
                     marker='o', \
                     s=libplot.MARKER_SIZE, \
                     alpha=libplot.ALPHA, \
                     c=None, \
                     edgecolors='none', \
                     prefix = '', \
                     fig=None, \
                     ax=None):
    """
    Create a tsne plot without the formatting
    """
    
    if ax is None:
        fig, ax = libplot.new_fig()
    
    if c is None:
        c = colors()
        
    
    ids = list(sorted(set(clusters['Cluster'])))
      
    for i in range(0, len(ids)):
        l = ids[i]
        
        indices = np.where(clusters['Cluster'] == l)[0]
        
        n = len(indices)
        
        label = '{}{} ({:,})'.format(prefix, l, n)
    
        x1 = x[indices] #np.take(x, indices)
        y1 = y[indices] #np.take(y, indices)
          
        ax.scatter(x1, y1, color=c[i], edgecolors=edgecolors, s=s, marker=marker, alpha=alpha, label=label)

    return fig, ax


def cluster_colors(clusters, c=colors()):
    ret = []
    
    ids = list(sorted(set(clusters['Cluster'])))
    
    cmap = {}
    
    for i in range(0, len(ids)):
        cmap[ids[i]] = i
    
    for i in range(0, clusters.shape[0]):
        ret.append(c[cmap[clusters['Cluster'][i]]])
        
    return ret
