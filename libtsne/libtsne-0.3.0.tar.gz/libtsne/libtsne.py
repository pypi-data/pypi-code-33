#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:04:08 2018

@author: antony
"""

import pandas as pd
import phenograph
import collections
import os
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import libcluster
import libsparse
from libsparse import SparseDataFrame



# As per 10x
TSNE_PERPLEXITY = 30
TSNE_MAX_ITER = 1000
TSNE_LEARNING = 200 #200
TSNE_RANDOM_STATE = 0 #42
TSNE_METRIC = 'correlation' #'euclidean' #'correlation'
TSNE_INIT = 'pca'

def get_cluster_file(name, tpmmode=True, logmode=True):
  file = 'clusters_{}.txt'.format(name)
  
  #if tpmmode:
  #  file += '_tpm'
    
  #if logmode:
  #  file += '_log2'
  
  #file += '.txt'
  
  return file


def get_kmeans_file(name, clusters):
  file = 'clusters_kmeans_{}_{}.txt'.format(clusters, name)
  
  return file


def get_pca_file(name, tpmmode=True, logmode=True):
  return 'pca_data_{}.txt'.format(name)
  
  
def get_pca_var_file(name, tpmmode=True, logmode=True):
  return 'pca_var_{}.txt'.format(name)

def get_dim_file(name, mode='tsne'):
  return '{}_data_{}.txt'.format(mode, name)

def get_tsne_file(name, tpmmode=True, logmode=True):
  return get_dim_file(name, mode='tsne')


def write_clusters(headers, labels, name, tpmmode=True, logmode=True):
    file = get_cluster_file(name, tpmmode=tpmmode, logmode=logmode)
  
    print('Writing clusters to {}...'.format(file))
  
    if type(headers) is pd.core.frame.DataFrame:
        headers = headers.iloc[:, 0].tolist()
  
    # one based is a convience for users so that they don't have to use
    # zero based ids
    df = pd.DataFrame({'Barcode':headers, 'Cluster':labels, 'cluster_one_based':(labels + 1)})
  
    df = df[['Barcode', 'Cluster']]
    df = df.set_index('Barcode')
  
    df.to_csv(file, sep='\t', header=True, index=True)
  
def write_kmeans_clusters(name, clusters, headers, labels):
    file = get_kmeans_file(name, clusters)
  
    print('Writing k-means clusters to {}...'.format(file))
  
    if type(headers) is pd.core.frame.DataFrame:
        headers = headers.iloc[:, 0].tolist()
  
    # one based is a convience for users so that they don't have to use
    # zero based ids
    df = pd.DataFrame({'Barcode':headers, 'Cluster':labels})
  
    df = df[['Barcode', 'Cluster']]
    df = df.set_index('Barcode')
  
    df.to_csv(file, sep='\t', header=True, index=True)
    
  
def read_clusters(file):
  print('Reading clusters from {}...'.format(file))
  
  data = pd.read_csv(file, sep='\t', header=0, index_col=0)
  
  cluster_map = collections.defaultdict(int)
  
  for i in range(0, data.shape[0]):
    cluster_map[data.index[i]] = data['Cluster'][i]
    
  return cluster_map, data



def load_phenograph_clusters(pca, name, cache=True):
    """
    Given a pca matrix, cluster on it
    
    Parameters
    ----------
    pca : array, shape (n_samples, n_pca)
        
    name : str
        Name of run.

    cache : bool, optional
        Create a file of the clusters for reloading. Default is True.

    Returns
    -------
    tsne :  array, shape (n_samples, 2)
        The tsne coordinates for each sample
    """
    
    file = get_cluster_file(name)
  
    if not os.path.isfile(file) or not cache:
        print('{} was not found, creating it with...'.format(file))
        
        k = min(pca.shape[0] - 2, 20)
        
        # Find the interesting clusters
        labels, graph, Q = phenograph.cluster(pca, k=k)
        
        if min(labels) == -1:
          new_label = 100
          labels[np.where(labels == -1)] = new_label
          
        labels += 1
        
        write_clusters(pca.index.tolist(), labels, name)
        
    cluster_map, data = read_clusters(file)
          
    labels = data
    #return cluster_map, labels
    return labels


def load_kmeans_clusters(pca, name, clusters=10, cache=True):
    """
    Given a pca matrix, cluster on it
    
    Parameters
    ----------
    pca : array, shape (n_samples, n_pca)
        
    name : str
        Name of run.

    cache : bool, optional
        Create a file of the clusters for reloading. Default is True.

    Returns
    -------
    tsne :  array, shape (n_samples, 2)
        The tsne coordinates for each sample
    """
    
    file = get_kmeans_file(name, clusters)
  
    if not os.path.isfile(file) or not cache:
        print('{} was not found, creating it with...'.format(file))
        
        labels = KMeans(n_clusters=clusters).fit_predict(pca)
        
        if min(labels) == -1:
          new_label = 100
          labels[np.where(labels == -1)] = new_label
          
        labels += 1
        
        write_kmeans_clusters(name, clusters, pca.index.tolist(), labels)
        
    cluster_map, data = read_clusters(file)
          
    labels = data
    
    return labels


def read_pca(file):
    if not os.path.isfile(file):
        file = get_pca_file(file)
    
    print('Reading pca from {}...'.format(file))
  
    return pd.read_csv(file, sep='\t', header=0, index_col=0)


def load_pca(data, name, n=50, tpmmode=True, logmode=True, exclude=[], cache=True):
  file = get_pca_file(name, tpmmode=tpmmode, logmode=logmode)
  
  if not os.path.isfile(file) or not cache:
    print('{} was not found, creating it with n={}...'.format(file, n))
    
    p, pca = libcluster.pca(data, n=n, exclude=exclude)
    
    labels = ['PC-{}'.format(x + 1) for x in range(0, pca.shape[1])]
    
    var_file = get_pca_var_file(name, tpmmode=tpmmode, logmode=logmode)
    df = pd.DataFrame(p.explained_variance_ratio_, index=labels, columns=['Variance'])
    df.to_csv(var_file, sep='\t', header=True, index=True)
    
    df = pd.DataFrame(pca, index=data.columns, columns=labels)
    df.to_csv(file, sep='\t', header=True, index=True)
  
  return read_pca(file)

def read_tsne(file):
  print('Reading clusters from {}...'.format(file))
  
  return pd.read_csv(file, sep='\t', header=0, index_col=0)

def new_tsne():
    return TSNE(n_components=2,
                verbose=1,
                perplexity=TSNE_PERPLEXITY,
                learning_rate=TSNE_LEARNING,
                n_iter=TSNE_MAX_ITER,
                method='barnes_hut',
                random_state=TSNE_RANDOM_STATE,
                init=TSNE_INIT,
                metric=TSNE_METRIC)
    

def load_tsne(data, name, n=50, tpmmode=True, logmode=True, exclude=[]):
    """
    Run t-sne

    Parameters
    ----------
    data : array, shape (n_samples, n_features)
        If the metric is 'precomputed' X must be a square distance
        matrix. Otherwise it contains a sample per row.
        
    name : str
        Name of run.

    Returns
    -------
    tsne :  array, shape (n_samples, 2)
        The tsne coordinates for each sample
            
    """
    
    file = get_tsne_file(name, tpmmode=tpmmode, logmode=logmode)
      
    if not os.path.isfile(file):
        print('{} was not found, creating it with n={}...'.format(file, n))
    
        _, pca = libcluster.pca(data, n=n, exclude=exclude)
  
        tsne = new_tsne()
        
        tsne_results = tsne.fit_transform(pca)
    
        data = pd.DataFrame({'Barcode':data.index, 'TSNE-1':tsne_results[:, 0], 'TSNE-2':tsne_results[:, 1]})
        data = data[['Barcode', 'TSNE-1', 'TSNE-2']]
        data = data.set_index('Barcode')
  
        data.to_csv(file, sep='\t', header=True, index=True)
  
    return read_tsne(file)


def load_pca_tsne(pca, name, tpmmode=True, logmode=True, exclude=[], cache=True):
    """
    Run t-sne using pca result

    Parameters
    ----------
    pca : array, shape (n_samples, n_pca)
        pca matrix.

    name: str
        name of pca results

    Returns
    -------
    tsne :  array, shape (n_samples, 2)
        The tsne coordinates for each sample
    """
  
    file = get_tsne_file(name, tpmmode=tpmmode, logmode=logmode)
  
    if not os.path.isfile(file) or not cache:
        print('{} was not found, creating it...'.format(file))
        
        # perplexity = 5, n_iter = 5000, learning = 10
        
        tsne = new_tsne()
        
        if isinstance(pca, SparseDataFrame):
            tsne_results = SparseDataFrame(tsne.fit_transform(pca.data), pca.index, pca.columns)
        else:
            tsne_results = tsne.fit_transform(pca)
        
        data = pd.DataFrame({'Barcode':pca.index, 'TSNE-1':tsne_results[:, 0], 'TSNE-2':tsne_results[:, 1]})
        data = data[['Barcode', 'TSNE-1', 'TSNE-2']]
        data = data.set_index('Barcode')
       
        data.to_csv(file, sep='\t', header=True)
  
    return read_tsne(file)


def lz_dz_diversity_plot(diversity, x, y, lz_indices, dz_indices, ax, cmap, norm):
  # How many labels to cycle through (it cannot exceed the number of colors)
  
  #cmap = plt.cm.plasma
  #norm = matplotlib.colors.Normalize(vmin=0, vmax=max(1, round(max(diversity))))
  
  ret = None
  
  if len(lz_indices) > 0:
    div = np.take(diversity, lz_indices)
    x1 = np.take(x, lz_indices)
    y1 = np.take(y, lz_indices)
    indices = np.argsort(div)
    div = np.take(div, indices)
    x1 = np.take(x1, indices)
    y1 = np.take(y1, indices)
    ret = ax.scatter(x1, y1, c=div, cmap=cmap, norm=norm, s=libcluster.MARKER_SIZE, alpha=0.8, marker='^')
    
  if len(dz_indices) > 0:
    div = np.take(diversity, dz_indices)
    x1 = np.take(x, dz_indices)
    y1 = np.take(y, dz_indices)
    indices = np.argsort(div)
    div = np.take(div, indices)
    x1 = np.take(x1, indices)
    y1 = np.take(y1, indices)
    ret = ax.scatter(x1, y1, c=div, cmap=cmap, norm=norm, alpha=0.8, s=libcluster.MARKER_SIZE, marker='o')
  
  return ret


def diversity_plot(pca_results, diversity, lz_indices, dz_indices, prefix, diversity_type):
  fig, ax = libcluster.make_figure()
  
  cmap = plt.cm.plasma
  norm = matplotlib.colors.Normalize(vmin=0, vmax=max(1, round(max(diversity))))

  x = pca_results['tsne-1'].tolist()
  y = pca_results['tsne-2'].tolist()

  lz_dz_diversity_plot(diversity, x, y, lz_indices, dz_indices, ax, cmap, norm)

  libcluster.format_simple_axes(ax, title="t-SNE")

  cax = fig.add_axes([0.8, 0.05, 0.15, 0.02])
  #d = np.array([[0,1]])
  #im = cax.imshow(d, interpolation='nearest', cmap=cmap, norm=norm)
  #fig.colorbar(im, cax=cax, orientation='horizontal')
  
  matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, ticks=[0.0, 1.0], orientation='horizontal')
  
  ax.set_title('Shannon Diversity Index')
  libcluster.save_plot(fig, 'tsne_{}_{}_diversity.pdf'.format(prefix, diversity_type))
  
  
def tsne_legend(ax, labels, colors):
  labeln = min(len(colors), np.max(labels) + 1)
  
  for i in range(0, labeln):
    color = colors[i]
    
    size = len(np.where(labels == i)[0])
    
    ax.scatter([],[], marker='o', color=color, alpha=0.9, s=libcluster.MARKER_SIZE, label="Cluster {} ({})".format(i + 1, size))


def get_tsne_plot_name(name, t1=1, t2=2):
    return 'tsne_{}.pdf'.format(name) #, t1, t2)
      

def format_simple_axes(ax, title="t-SNE", dim1=1, dim2=2, subtitle1="", subtitle2=""):
  libcluster.invisible_axes(ax)
  
  ax.annotate('',
    xy=(40, 0),  # theta, radius
    xytext=(-2, 0),
    xycoords='axes pixels',
    textcoords='axes pixels',
    arrowprops=dict(arrowstyle='->', facecolor='red'))
  
  ax.annotate('',
    xy=(0, 40),  # theta, radius
    xytext=(0, -2),
    xycoords='axes pixels',
    textcoords='axes pixels',
    arrowprops=dict(arrowstyle='->', facecolor='black'))
  
  if subtitle1 != "":
    ax.text(0, -0.04, '{} {} ({})'.format(title, dim1, subtitle1), transform=ax.transAxes)
  else:
    ax.text(0, -0.04, '{} {}'.format(title, dim1), transform=ax.transAxes)
  
  if subtitle2 != "":
    ax.text(-0.04, 0, '{} {} ({})'.format(title, dim2, subtitle2), va='bottom', transform=ax.transAxes, rotation=90)
  else:
    ax.text(-0.04, 0, '{} {}'.format(title, dim2), va='bottom', transform=ax.transAxes, rotation=90)
    
    
