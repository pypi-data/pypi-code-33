import math
import seaborn as sns
import matplotlib.pyplot as plt
from pandas import DataFrame

from crimjustsimpy import ExperimentData


#########################################################################################
# Handy visualizations from the experiment's data frame.
#########################################################################################

# Plot docket sizes histogram.
def plot_docket_sizes_hist(df:DataFrame):
    plot_hist(df.groupby("docketId").size(),title="Docket Sizes", bins="ints")

# Plot case probability of conviction histogram.
def plot_prob_guilt_hist(df:DataFrame):
    plot_df_hist(df, "pConvict", title="Probability of Conviction")

# Pie chart of pleas vs trials.
def plot_pleas_vs_trials_pie(df:DataFrame):
    values = [(len(df.loc[df['plead'] == True])), (len(df.loc[df['tried'] == True]))]
    plot_pie(['Plead', 'Tried'], values,
                       colors=['y', 'c'],
                       title='Plea vs Trial')

# Pie chart of trial results.
def plot_trial_results_pie(df:DataFrame):
    values = [(len(df.loc[df['acquitted'] == True])), (len(df.loc[df['convicted'] == True]))]
    plot_pie(['Acquitted', 'Convicted'], values,
                       colors=['g', 'r'], title='Trial Result')

# Pie chart of guilty/not guilty.
def plot_guilt_summary_pie(df:DataFrame):
    values = [(len(df.loc[df['guilty'] == False])), (len(df.loc[df['guilty'] == True]))]
    plot_pie(['Not Guilty', 'Guilty'], values, colors=['g', 'm'], title='Guilty vs Not Guilty')

# Pie chart of case results.
def plot_case_results_pie(df:DataFrame):
    values = [(len(df.loc[df['acquitted'] == True])), (len(df.loc[df['plead'] == True])), (len(df.loc[df['convicted'] == True]))]
    plot_pie(['Acquitted', 'Plead', 'Convicted'], values,
         colors=['g', 'y', 'r'], title='Case Results')

# Plot sentencing histogram.
def plot_sentences_hist(df:DataFrame):
    plot_df_hist(df,"sentence",title="Sentences")

#########################################################################################
# Visualizations directly from the data structures.
#########################################################################################

# Plot docket sizes histogram.
def view_dockets(data:ExperimentData):
    plot_hist(data.dockets, getter=lambda d:len(d.cases), title="Docket Sizes", bins="ints")

# Plot case probability of conviction histogram.
def view_prob_guilt(data:ExperimentData):
    plot_hist(data.cases, getter=lambda c:c.prob_convict, title="p(convict)")

# Pie chart of pleas vs trials.
def view_pleas_vs_trials(data:ExperimentData):
    num_plead = len(data.cases_plead)
    num_tried = len(data.cases_tried)
    plot_pie(['Plead', 'Tried'],[num_plead, num_tried],colors=['y','c'],title='Plea vs Trial')

# Pie chart of trial results.
def view_trial_results(data:ExperimentData):
    num_acquitted = len(data.cases_acquitted)
    num_convicted = len(data.cases_convicted)
    plot_pie(['Acquitted', 'Convicted'],[num_acquitted, num_convicted], colors=['g','r'],title='Trial Result')

# Pie chart of guilty/not guilty.
def view_guilt_summary(data:ExperimentData):
    num_guilty = len(data.cases_guilty)
    num_not_guilty = len(data.cases_not_guilty)
    plot_pie(['Not Guilty', 'Guilty'],[num_not_guilty, num_guilty], colors=['g','m'], title='Guilty vs Not Guilty')

# Pie chart of case results.
def view_case_results(data:ExperimentData):
    num_acquitted = len(data.cases_acquitted)
    num_plead = len(data.cases_plead)
    num_convicted = len(data.cases_convicted)
    plot_pie(['Acquitted', 'Plead', 'Convicted'],[num_acquitted, num_plead, num_convicted],
             colors = ['g', 'y', 'r'], title='Case Results')

# Plot sentencing results histogram.
def view_sentences(data:ExperimentData):
    plot_hist(data.sentences, title="Sentences")

# Some helper functions.

def extract_data(values, getter):
    if getter is None:
        return values
    return [getter(i) for i in values]

def plot_line(values, *, title=None, getter=None):
    items = extract_data(values, getter)
    g = sns.lineplot(y=items, x=range(len(items)))
    g.set_title(title)
    plt.show()

def plot_hist(values, *, title=None, getter=None, bins='fd'):
    items = extract_data(values, getter)
    if(bins=='ints'):
        bins = make_int_edges(items,50)
    g = sns.distplot(items,bins=bins,hist=True,kde=False)
    g.set_title(title)
    plt.show()

def make_int_edges(items,max_bins):
    lo = math.floor(min(items))
    hi = math.ceil(max(items))
    span = hi-lo + 1
    step = int(span / max_bins) + 1
    num_edges = int(span / step) + 1
    edges = [(lo + i*step)-0.5 for i in range(0, num_edges)]
    return edges

def plot_pie(labels, values,*,title=None,colors=None):
    plt.pie(values, labels=labels, colors=colors, startangle=90)
    plt.title(title)
    plt.show()

def plot_df_hist(df:DataFrame, column, *, title):
    values = df[column]
    plot_hist(values,title=title)

def plot_df_pie(df:DataFrame,column,*,title,mapping):
    values = df.groupby(column).size()
    plt.pie(values, startangle=90)
    plt.title(title)
    plt.show()