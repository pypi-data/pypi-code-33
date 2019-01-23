#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clustercollection.py
# Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
# Implements the basic framework for a collection of clusters
#

from ditto_lib.generic.itemcollection import ItemCollection, logger
from ditto_lib.clustering.cluster import Cluster

from random import randint
from math import sqrt
from multiprocessing import Pool
from sklearn.cluster import KMeans, MeanShift

class ClusterCollection(ItemCollection):
    '''
    Basic class for computing K-Mean clustering algorithm.\n
    Args:\n
    name: The name for the collection\n
    cluster_amount: The amount of clusters to group the items into. This
    defaults to 0. It is best to experiment and find the best value for this
    parameter. Some clustering alogrithms may override this input. 
    '''

    def __init__(self, name, cluster_amount=0):
        super(ClusterCollection, self).__init__(name)
        self._clusters = []
        self._cluster_amount = cluster_amount

    @property
    def cluster_amount(self):
        '''
        Return the amount of clusters, or centroid that this
        collection contains. 
        '''
        return self._cluster_amount

    @cluster_amount.setter
    def cluster_amount(self, cluster_amount):
        '''
        Set the amount of clusters, or centroids that this 
        collection contains
        '''
        self._cluster_amount = cluster_amount

    @property
    def clusters(self):
        '''
        Get all clusters associated with this collection
        '''
        return self._clusters

    def get_feature_ranking(self):
        '''
        Get a list of features in the order of importance. IE, the
        first item in the list will be the most impactful, and the least
        item in the list will be the least impactful in deciding where these
        items will be grouped
        '''
        pass

    def run_kmean(self, n_jobs=None):
        '''
        Run KMean clustering algorithm. Can pass in how many jobs to 
        use for calculation.
        '''
        self._cluster_setup()
        collection, names = self.as_array()
        results = KMeans(self._cluster_amount, random_state=0, n_jobs=n_jobs).fit(collection)
        logger.log('debug', "Iterations = {}".format(results.n_iter_))
        results = results.labels_
        for index, item in enumerate(self._items.keys()):
            self._clusters[results[index]].add_item(item, self._items[item])

    def run_meanshift(self, n_jobs=None):
        '''
        Run Meanshift clustering algorithm. Can pass in how many jobs to
        use for calculation
        '''
        collection, names = self.as_array()
        results = MeanShift(n_jobs=n_jobs).fit(collection).labels_
        self._cluster_amount = max(results) + 1
        self._cluster_setup()
        logger.log('info', "Amount of clusters generated {}".format(self._cluster_amount))
        for index, item in enumerate(self._items.keys()):
            self._clusters[results[index]].add_item(item, self._items[item])

    def get_item_cluster(self, name):
        '''
        Returns the cluster that the item belongs to.
        Takes the name of the item
        '''
        for cluster in self._clusters:
            if cluster.contains(name):
                logger.log('debug', "{} in cluster {}".format(name, cluster.name))
                return cluster
        logger.log('error', "Could not find item {} in {}".format(name, self.name))

    def get_cluster(self, name):
        '''
        Returns the cluster with the given name
        '''
        for cluster in self._clusters:
            if cluster.name == name:
                return cluster
        logger.log('error', "Could not find cluster {} in {}".format(name, self.name))
        return None

    def cluster_as_itemcollection(self, cluster_name):
        '''
        Return the cluster with the given cluster name as 
        an item collection. Returns None if no cluster with that 
        name is stored in this collection
        '''
        for cluster in self._clusters:
            if cluster.name == cluster_name:
                return cluster.as_itemcollection(self.attributes, True)
        logger.log('error', "Could not find cluster {} in {}".format(cluster_name, self.name))
        return None

    def _cluster_setup(self):
        self._clusters = []
        for i in range(self._cluster_amount):
            self._clusters.append(Cluster('Cluster {}'.format(i)))