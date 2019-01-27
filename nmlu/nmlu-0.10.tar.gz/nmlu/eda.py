import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy


def set_plot_sane_defaults(mode='classic'):
    set_plot_sizes(sml=12, med=14, big=16)
    # see https://matplotlib.org/gallery/style_sheets/style_sheets_reference.html
    mpl.style.use({
        'classic': 'default',
        'serious': 'bmh',
        'dark': 'dark_background',
        'boring': 'classic',
        'cool': 'ggplot',
        'seaborn': 'seaborn',
    }[mode])
    mpl.rcParams['figure.facecolor'] = 'white' if mode != 'dark' else 'black'


def set_plot_sizes(sml=12, med=14, big=16):
    plt.rc('font', size=sml)          # controls default text sizes
    plt.rc('axes', titlesize=sml)     # fontsize of the axes title
    plt.rc('axes', labelsize=med)     # fontsize of the x and y labels
    plt.rc('xtick', labelsize=sml)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=sml)    # fontsize of the tick labels
    plt.rc('legend', fontsize=sml)    # legend fontsize
    plt.rc('figure', titlesize=big)   # fontsize of the figure title


def set_plot_bgs(color='white'):
    mpl.rcParams['figure.facecolor'] = 'white'


def plot_pairs_dists(df, y_col=None, except_cols=None, figsize=None, palette=None):
    if except_cols is None:
        except_cols = set()
    if y_col is not None:
        except_cols.add(y_col)
    return sns.pairplot(
        df,
        hue=y_col,
        palette=palette,
        vars=set(df.columns.values).difference(except_cols),
        size=figsize
    )


def plot_heatmap(df, figsize=(16, 16)):
    fig, ax = plt.subplots(figsize=figsize)
    return sns.heatmap(df.corr(), annot=True, ax=ax)


def plot_pairs_corr(df, figsize=(18, 16)):
    axes = pd.plotting.scatter_matrix(df, alpha=0.3, figsize=figsize, diagonal='kde')
    corr = df.corr().values
    for i, j in zip(*np.triu_indices_from(axes, k=1)):
        axes[i, j].annotate("%.3f" % corr[i, j], (0.8, 0.8), xycoords='axes fraction', ha='center', va='center')


def show_cat_feature_vs_y(df, fld, y_fld):
    df = df.reset_index()
    pivot_args = dict(
        data=df, index=fld, columns=y_fld,
        aggfunc='size', fill_value=0,
    )
    tbl_args = pivot_args.copy()
    tbl_args.update(aggfunc='count', values='index', margins=True)
    tbl = pd.pivot_table(**tbl_args)
    print(tbl)
    plot_tbl = pd.pivot_table(**pivot_args)
    plot_tbl.plot.bar()
    plt.show()


def plot_dendrogram(df, figsize=(16, 10)):
    corr = np.round(scipy.stats.spearmanr(df).correlation, 4)
    corr_condensed = scipy.cluster.hierarchy.distance.squareform(1 - corr)
    z = scipy.cluster.hierarchy.linkage(corr_condensed, method='average')
    plt.figure(figsize=figsize)
    return scipy.cluster.hierarchy.dendrogram(
        z, labels=df.columns, orientation='left', leaf_font_size=16)
