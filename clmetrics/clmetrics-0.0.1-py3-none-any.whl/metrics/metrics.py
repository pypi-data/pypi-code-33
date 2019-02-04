import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics.cluster import unsupervised
from scipy.spatial.distance import cdist, pdist, euclidean

class ClusterMetrics:
    'Common base class for all metrics'
    def __init__(self, data, labels, *args, **kwargs):
        self.data = data
        self.labels = labels
        self.args=args
        self.args=kwargs
        
    def silhouette_samples(self,data,labels,metric='euclidean',**kwds):
        """Compute the Silhouette Coefficient for each sample.
    
            The Silhouette Coefficient is a measure of how well samples are clustered
            with samples that are similar to themselves. Clustering models with a high
            Silhouette Coefficient are said to be dense, where samples in the same
            cluster are similar to each other, and well separated, where samples in
            different clusters are not very similar to each other.
            The Silhouette Coefficient is calculated using the mean intra-cluster
            distance (``a``) and the mean nearest-cluster distance (``b``) for each
            sample.  The Silhouette Coefficient for a sample is ``(b - a) / max(a,
            b)``.
            Note that Silhouette Coefficient is only defined if number of labels
            is 2 <= n_labels <= n_samples - 1.
            This function returns the Silhouette Coefficient for each sample.
            The best value is 1 and the worst value is -1. Values near 0 indicate
            overlapping clusters.
            Read more in the :ref:`User Guide <silhouette_coefficient>`.
    
        Args:   
            data : array [n_samples_a, n_samples_a] if metric == “precomputed”, or, [n_samples_a, n_features] otherwise
            Array of pairwise distances between samples, or a feature array.
    
            labels : array, shape = [n_samples]
            label values for each sample
    
            metric : string, or callable
            The metric to use when calculating distance between instances in a feature array. If metric is a string, it must be one of the options allowed by sklearn.metrics.pairwise.pairwise_distances. If data is the distance array itself, use “precomputed” as the metric.
    
            `**kwds` : optional keyword parameters
            Any further parameters are passed directly to the distance function. If using a scipy.spatial.distance metric, the parameters are still metric dependent. See the scipy docs for usage examples.
    
        Returns:    
            silhouette : array, shape = [n_samples]
                Silhouette Coefficient for each samples.
        """
    
        return unsupervised.silhouette_samples(data,labels,metric,**kwds)
    
    def silhouette_score(self,data,labels,metric='euclidean',sample_size=None,random_state=None,**kwds):
        """Compute the mean Silhouette Coefficient of all samples.
    
            The Silhouette Coefficient is calculated using the mean intra-cluster
            distance (``a``) and the mean nearest-cluster distance (``b``) for each
            sample.  The Silhouette Coefficient for a sample is ``(b - a) / max(a,
            b)``.  To clarify, ``b`` is the distance between a sample and the nearest
            cluster that the sample is not a part of.
            Note that Silhouette Coefficient is only defined if number of labels
            is 2 <= n_labels <= n_samples - 1.
            This function returns the mean Silhouette Coefficient over all samples.
            To obtain the values for each sample, use :func:`silhouette_samples`.
            The best value is 1 and the worst value is -1. Values near 0 indicate
            overlapping clusters. Negative values generally indicate that a sample has
            been assigned to the wrong cluster, as a different cluster is more similar.
            Read more in the :ref:`User Guide <silhouette_coefficient>`.
            Parameters
    
        Args:
            data : array [n_samples_a, n_samples_a] if metric == "precomputed", or, \
                     [n_samples_a, n_features] otherwise
                Array of pairwise distances between samples, or a feature array.
            labels : array, shape = [n_samples]
                 Predicted labels for each sample.
            metric : string, or callable
                The metric to use when calculating distance between instances in a
                feature array. If metric is a string, it must be one of the options
                allowed by :func:`metrics.pairwise.pairwise_distances
                <sklearn.metrics.pairwise.pairwise_distances>`. If data is the distance
                array itself, use ``metric="precomputed"``.
            sample_size : int or None
                The size of the sample to use when computing the Silhouette Coefficient
                on a random subset of the data.
                If ``sample_size is None``, no sampling is used.
            random_state : int, RandomState instance or None, optional (default=None)
                The generator used to randomly select a subset of samples.  If int,
                random_state is the seed used by the random number generator; If
                RandomState instance, random_state is the random number generator; If
                None, the random number generator is the RandomState instance used by
                `np.random`. Used when ``sample_size is not None``.
            **kwds : optional keyword parameters
                Any further parameters are passed directly to the distance function.
                If using a scipy.spatial.distance metric, the parameters are still
                metric dependent. See the scipy docs for usage examples.
    
        Returns:
            silhouette : float
                Mean Silhouette Coefficient for all samples.
        """
    
        return unsupervised.silhouette_score(data,labels,metric,sample_size,random_state,**kwds)
    
    def silhouette_plot(self,data,labels,metric='euclidean',fig_size = None,cluster = None,y=None,index = False,**kwds):
    
        """Makes a silhouette bar graph.
    
            Calculate the silhouette of the samples and then plot a graph of the chosen cluster 
            and the silhouettes of the samples or plot a graph with all the means of the 
            silhouettes of the clusters
    
        Args:
            data : array [n_samples_a, n_samples_a] if metric == "precomputed", or, \
                     [n_samples_a, n_features] otherwise
                Array of pairwise distances between samples, or a feature array.
            labels : array, shape = [n_samples]
                 Predicted labels for each sample.
            metric : string, or callable
                The metric to use when calculating distance between instances in a
                feature array. If metric is a string, it must be one of the options
                allowed by :func:`metrics.pairwise.pairwise_distances
                <sklearn.metrics.pairwise.pairwise_distances>`. If data is the distance
                array itself, use ``metric="precomputed"``.
            fig_size : number, type int
                Number for the figsize of the plot if fig_size == None then a 
                calculation is made to leave a suitable size for the quantity of samples.
            cluster : number do cluster,type int
                Cluster number to generate the silhouettes graph of its samples 
                if cluster == None will then generate a plot of the mean silhouettes of all clusters.
            y : Smple ID
                ID of the samples, used to label the bars on the y-axis
    
            **kwds : optional keyword parameters
                Any further parameters are passed directly to the distance function.
                If using a scipy.spatial.distance metric, the parameters are still
                metric dependent. See the scipy docs for usage examples.
    
        Returns:
            Void
    
        """
        
        silhouette_samples = unsupervised.silhouette_samples(data,labels,metric,**kwds)
    
        df = pd.DataFrame(silhouette_samples)
        df['cluster'] = labels
    
        if cluster == None:
            cluster_means = df.groupby('cluster').mean()
            dit = dict(zip(cluster_means.index,cluster_means[0]))
            df2 = pd.DataFrame(list(dit.items()))
            df2.columns = ['Cluster','silhouette_mean']
            
            
            if fig_size == None:
                if len(df2) > 64:
                    fig = plt.figure(figsize=(len(df2)/7,len(df2)/3))
                else:
                    fig = plt.figure(figsize=(10,8))
            else:
                fig = plt.figure(figsize = fig_size)
    
    
            df2 = df2.sort_values(['silhouette_mean'],ascending=False).reset_index(drop=True)
            ax = sns.barplot(df2['silhouette_mean'],y = df2.index,orient='h')
            ax.set_yticklabels(df2['Cluster'])
            plt.ylabel('Cluster')
            plt.show()  
    
        elif cluster != None:
            if y.all() != None:
                df['y'] = y
    
            cluster = df[df['cluster'] == cluster]
            cluster.columns = ['silhouette','Cluster','y']
            cluster = cluster.sort_values(['silhouette'],ascending=False).reset_index(drop=True)
            
            if fig_size == None:
                if len(cluster) > 64:
                    fig = plt.figure(figsize=(len(cluster)/7,len(cluster)/3))
                else:
                    fig = plt.figure(figsize=(12,10))
            else:
                fig = plt.figure(figsize = fig_size)
    
            ax = sns.barplot(cluster['silhouette'],y = cluster.index,orient='h')
    
            if index != None:
                ax.set_yticklabels(cluster['y'])
    
            plt.ylabel('ID samples')
            plt.show()
            return fig
    
    def elbow(self,data, max_number_of_clusters, step = 1):
        """Plots the elbow containing the variance of each cluster
        Args:
            data: data to be clustered
            max_number_of_clusters: maximum number of clusters
            step: determines how much the iteraction will increase (1 by default)
                For example, if step = 10, the function will plot the elbow for every 10 clusters
        Returns:
            void
        """
        distortions = []
        K = np.arange(1, max_number_of_clusters+1,step)
        for k in K:
            kmeans = KMeans(n_clusters=k).fit(data)
            kmeans.fit(data)
            distortions.append(sum(np.min(cdist(data, kmeans.cluster_centers_, 'euclidean'), axis=1)) / len(data))
    
        # Plot the elbow
        plt.plot(K, distortions, 'x-')
        plt.xlabel('k')
        plt.ylabel('Distortion')
        plt.title('The Elbow Method showing the optimal k')
        plt.show()
    
    #Dunn Index:
    
    def normalize_to_smallest_integers(self,labels):
        """Normalizes a list of integers so that each number is reduced to the minimum possible integer, maintaining the order of elements.
        
        Args:
            labels: the list to be normalized
        
        Returns:
            numpy.array with the values normalized as the minimum integers between 0 and the maximum possible value.
        """
    
        max_v = len(set(labels)) if -1 not in labels else len(set(labels)) - 1
        sorted_labels = np.sort(np.unique(labels))
        unique_labels = range(max_v)
        new_c = np.zeros(len(labels), dtype=np.int32)
    
        for i, clust in enumerate(sorted_labels):
            new_c[labels == clust] = unique_labels[i]
    
        return new_c
    
    
    def dunn(self,labels, distances):
        """
        Dunn index for cluster validation (the bigger, the better)
        
        .. math:: D = \\min_{i = 1 \\ldots n_c; j = i + 1\ldots n_c} \\left\\lbrace \\frac{d \\left( c_i,c_j \\right)}{\\max_{k = 1 \\ldots n_c} \\left(diam \\left(c_k \\right) \\right)} \\right\\rbrace
        
        Args:
            labels: a list containing cluster labels for each of the n elements
            distances: an n x n numpy.array containing the pairwise distances between elements
        
        Returns:
            The computed Dunn Index for the given data
        """
    
        labels = self.normalize_to_smallest_integers(labels)
    
        unique_cluster_distances = np.unique(self.min_cluster_distances(labels, distances))
        max_diameter = max(self.diameter(labels, distances))
    
        if np.size(unique_cluster_distances) > 1:
            return unique_cluster_distances[1] / max_diameter
        return unique_cluster_distances[0] / max_diameter
    
    
    def min_cluster_distances(self,labels, distances):
        """Calculates the distances between the two nearest points of each cluster.
    
        Args:
            labels: a list containing cluster labels for each of the n elements
            distances: an n x n numpy.array containing the pairwise distances between elements
    
        Returns:
            List containing distances between the two nearest points of each cluster
        """
        labels = self.normalize_to_smallest_integers(labels)
        n_unique_labels = len(np.unique(labels))
    
        min_distances = np.zeros((n_unique_labels, n_unique_labels))
        for i in np.arange(0, len(labels) - 1):
            for ii in np.arange(i + 1, len(labels)):
                if labels[i] != labels[ii] and distances[i, ii] > min_distances[labels[i], labels[ii]]:
                    min_distances[labels[i], labels[ii]] = min_distances[labels[ii], labels[i]] = distances[i, ii]
        return min_distances
    
        
    def diameter(self,labels, distances):
        """Calculates cluster diameters (the distance between the two farthest data points in a cluster)
        
        Args:
            labels: a list containing cluster labels for each of the n elements
            distances: an n x n numpy.array containing the pairwise distances between elements
        
        Returns:
            List containing diameters of each cluster
        """
        labels = self.normalize_to_smallest_integers(labels)
        n_clusters = len(np.unique(labels))
        diameters = np.zeros(n_clusters)
    
        for i in np.arange(0, len(labels) - 1):
            for ii in np.arange(i + 1, len(labels)):
                if labels[i] == labels[ii] and distances[i, ii] > diameters[labels[i]]:
                    diameters[labels[i]] = distances[i, ii]
        return diameters
            
    
    def cluster_evaluation(self,data,labels,distances,max_number_of_clusters = None,step = 1,fig_size = None,cluster = None,y=None):
    
        """Evaluates the clustering trough Silhouette and Elbow plots and Dunn Index.
    
        Args:
            data : array [n_samples_a, n_samples_a] if metric == "precomputed", or, \
                     [n_samples_a, n_features] otherwise
                Array of pairwise distances between samples, or a feature array.
            labels : array, shape = [n_samples]
                 Predicted labels for each sample.
            distances : list containing distances
                Distances between each data, used in the evaluation functions 
            max_number_of_clusters : number int
                maximum allowed number of clusters
            step : determines how much the iteraction will increase (1 by default)
                For example, if step = 10, the function will plot the elbow for every 10 clusters
            fig_size : number, type int
                Number for the figsize of the plot if fig_size == None then a 
                calculation is made to leave a suitable size for the quantity of samples.
            cluster : number do cluster,type int
                Cluster number to generate the silhouettes graph of its samples 
                if cluster == None will then generate a plot of the mean silhouettes of all clusters.
            y : Smple ID
                ID of the samples, used to label the bars on the y-axis
    
            **kwds : optional keyword parameters
                Any further parameters are passed directly to the distance function.
                If using a scipy.spatial.distance metric, the parameters are still
                metric dependent. See the scipy docs for usage examples.
    
        Returns:
            Void
    
        """
        print("Result of silhouette: "+ str(self.silhouette_score(distances,labels, metric= 'precomputed')))
        print("Result of dunn index: " + str(self.dunn(labels,distances)),"\n")
        if max_number_of_clusters != None:
            self.elbow(data,max_number_of_clusters,step)
        self.silhouette_plot(distances,labels,metric= 'precomputed',fig_size = fig_size,cluster = cluster,y=y)

    def get_clusters(self, data, labels):
        '''Finds the points in data that belongs to each cluster 
        Args:
            data: an array containing the data
            labels: an array containing the labels
        Returns:
            an array containing the points divided by cluster; each cluster points is an array
        '''
        clusters = []
        for i in range(len(np.unique(labels))):
            clusters.append(data[np.where(labels == i)])
        return clusters
    
    def get_total_distances(self, data):
        '''Computes distances between every point in data
            and turns it into a squareform
        Args:
            data: an array containing the data
        Returns:
            an array with the pairwise distances of the data
        '''
        total_distances = pdist(data)
        return total_distances
    
    def get_intracluster_distances(self, data, labels):
        '''Computes within-cluster distances
            and turns it into a squareform
        Args:
            data: an array containing the data
            labels: an array containing the labels
        Returns:
            an array with the pairwise within-cluster distances
        '''
        clusters = self.get_clusters(data, labels)
        intraclusters_distances = []
        for i in range(len(clusters)):
            intraclusters_distances.append(pdist(clusters[i]))
        return intraclusters_distances
    
    def c_index(self, data, labels):
        '''Computes C-Index for the the given data and labels
        Args:
            data: an array containing the data
            labels: an array containing the labels
        Returns:
            an int number representing the computed C-Index
        '''
        intracluster_distances = self.get_intracluster_distances(data, labels)
        s_w = 0
        f_w = 0
        for i in range(len(intracluster_distances)):
            s_w = s_w + np.sum(intracluster_distances[i])
            f_w = f_w + len(intracluster_distances[i])
        sorted_distances = np.sort(pdist(data))
        d_sorted_distances = sorted_distances[::-1]
        s_min = np.sum(sorted_distances[:f_w])
        s_max = np.sum(d_sorted_distances[:f_w])
        return (s_w - s_min)/(s_max - s_min)
    
    def compute_s(clusters, i):
        '''Computes de root mean square deviation of a cluster
        Args:
            clusters: clusters: a list of lists,
            in which every list contains the elements of each cluster
            i: index of the cluster
        Returns:
            The dispersion of the cluster
        '''
        return np.std(clusters[i])
    
    def compute_d(i, j, centers):
        '''Computes the euclidean distance between two given centroids
        Args:
            i, j: indexes of the two clusters
            centers: a list containing the cluster centroids
        Returns:
            distance between clusters i and j
        '''
        return euclidean(centers[i], centers[j])
    
    def davies_bouldin(clusters, centers):
        '''Computes the Davies-Bouldin index for clustering evaluation
        Args:
            clusters: a list of lists,
            in which every list contains the elements of each cluster
            centers: a list of the centers of each cluster
        Returns:
            A value corresponding to the Davies-Bouldin index computed for the clusters
        '''
        dispersions_array = np.array([])
        max_dispersions_array = np.array([])
        for i in range(len(clusters)):
            for j in range(len(clusters)):
                if j == i:
                    continue
                else:
                    dispersions_array = np.append(dispersions_array,
                                                  (compute_s(clusters, i) +
                                                   compute_s(clusters, j))/compute_d(i, j, centers))
            max_dispersions_array = np.append(max_dispersions_array, max(dispersions_array))
        return sum(max_dispersions_array)/len(clusters)
