from . import Kmeans
from . import GM 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pa
from scipy.sparse import csr_matrix, isspmatrix
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise_distances
import mpl_toolkits.mplot3d.axes3d as p3
import pylab as p
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
import sys
import os
import time
from matplotlib.lines import Line2D
from matplotlib.pyplot import cm
from collections import Counter
from gprofiler import gprofiler
import copy
import operator
import scipy
import seaborn as sns

class MICTI:
    def __init__(self,data,geneNames,cellNames,k=None,cluster_label=None,cluster_assignment=None, th=0,seed=None, ensembel=False, organisum="hsapiens"):
        self.data=data
        self.k=k
        self.th=th
        self.geneNames=geneNames
        self.cellNames=cellNames
        self.seed=seed
        self.ensembl=ensembel
        self.organsm=organisum
        self.cluster_assignment=cluster_assignment
        self.cluster_label=cluster_label
        self.data_ICF=self.ICF(self.data)

    def get_cluster_assignment(self):
        return self.cluster_assignment
    
    def get_cluster_data(self, cluster_number):
        return self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:], self.cellNames[np.in1d(np.array(self.cluster_assignment), cluster_number)]
    def gene_symbol_to_ENSEMBLID(self, symbol, organisum="hsapiens"):
        if(organisum=="hsapiens"):
            genes=pa.read_csv("../data/mart_export_stable_genes.txt", sep="\t")
        elif(organisum=="mmusculus"):
            genes=pa.read_csv("../data/mart_export_mouse_stable_gene.txt", sep="\t")
        else:
            print("give organisum")
       
        genes.index=genes["Gene name"] 
        ENSEBMLID=genes.loc[symbol,"Gene stable ID"]
        return ENSEBMLID.dropna().drop_duplicates()
    
    def ENSEMBLID_to_geneSymbol(self, ENSEMBL, organisum="hsapiens"):
        if(organisum=="hsapiens"):
            genes=pa.read_csv("../data/mart_export_stable_genes.txt", sep="\t")
        elif(organisum=="mmusculus"):
            genes=pa.read_csv("../data/mart_export_mouse_stable_gene.txt", sep="\t")
        else:
            print("give organisum")
        genes.index=genes["Gene stable ID"] 
        gene_symbol=genes.loc[ENSEMBL,"Gene name"]
        return gene_symbol.dropna().drop_duplicates()
    
    def ICF(self,data):
        matrixx=pa.DataFrame((data.T.toarray()))
        totalCells=matrixx.shape[1]
        idf=np.log(totalCells/np.array(matrixx[matrixx > self.th].count(axis=1).add(1)))
        icf_matrix=matrixx.T*np.array(idf)
        return np.array(icf_matrix) 
    
    def get_Visualization(self,dim=2,method="PCA"):
        
        if method=="PCA":
                if dim>3:
                        print ("Please give at most three dimentions")
                else:
                        svd = TruncatedSVD(n_components=dim)
                        svd_fit = svd.fit(self.data)
                        svdTransform=svd.fit_transform(self.data)
                        if dim==3:
                                fig=p.figure()
                                ax = p3.Axes3D(fig)
                                ax.scatter(svdTransform[:,0], svdTransform[:,1], svdTransform[:,2], c=self.cluster_assignment)
                                ax.set_xlabel("PCA1")
                                ax.set_ylabel("PCA2")
                                ax.set_zlabel("PCA3")
                                fig.add_axes(ax)
                                p.show()
                        elif dim==2:
                                plt.scatter(svdTransform[:,0], svdTransform[:,1], c=self.cluster_assignment)
                                plt.xlabel("PCA1")
                                plt.ylabel("PCA2")
                                plt.suptitle("MICTI with k={0:d}".format(self.k), fontsize=8)
                                plt.legend(bbox_to_anchor=(1.65, 1.65), loc='center', ncol=1)
                                plt.legend(list(self.cluster_assignment))
                                plt.show()
                        else:
                                print ("dimentionality error")
        elif method=="tsne":

                if dim>3:
                        print ("Please give at most three dimentions")
                else:
                        svd = TruncatedSVD(n_components=10)
                        svd_fit = svd.fit(self.data)
                        svdTransformTsne=svd.fit_transform(self.data)
                        X_tsne=TSNE(n_components=dim, random_state=0)
                        x_tsne=X_tsne.fit_transform(svdTransformTsne)
                        if dim==3:
                                fig=p.figure()
                                ax = p3.Axes3D(fig)
                                ax.scatter(x_tsne[:,0], x_tsne[:,1], x_tsne[:,2], c=self.cluster_assignment)
                                ax.set_xlabel("tsne1")
                                ax.set_xlabel("tsne2")
                                ax.set_xlabel("tsne3")
                                fig.add_axes(ax)
                                p.show()
                        elif dim==2:
                                data = pa.DataFrame(columns=['tsne_1','tsne_2','cell type'])
                                data['cell type']=[self.cluster_label[i] for i in list(self.cluster_assignment)]
                                data['tsne_1']=x_tsne[:,0]
                                data['tsne_2']=x_tsne[:,1]
                                
                                facet = sns.lmplot(data=data, x='tsne_1', y='tsne_2', hue='cell type', fit_reg=False, legend=True, legend_out=True)
                             
                                plt.savefig("MICTI_Plot.pdf", format="pdf")
                                plt.show()
                        else:
                                print ("dimetionality error")
        else:
                print ("Please give method==pca or method=tsne")

        
    def get_cluster_data(self, cluster_number):
        return self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:], self.cellNames[np.in1d(np.array(self.cluster_assignment), cluster_number)]
    
    def get_cluster_ICF_data(self, cluster_number):
        return self.ICF(self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:])
    
    def get_cluster_CF_data(self,cluster_number):
        return self.CF(self.data[np.in1d(np.array(self.cluster_assignment), cluster_number),:]) 
    
    def get_selected_cluster_marker(self, clusters):
        
        datta=self.data[np.in1d(np.array(self.cluster_assignment), clusters),:]
        index=self.cluster_assignment[np.in1d(np.array(self.cluster_assignment), clusters)]
        dat_common=self.CF(datta)
        dat_identity=self.ICF(datta)
        idd_com=[] 
        idd_j=[]
        for j in clusters:
            datt=dat_identity[np.in1d(np.array(index), [j]),:]
            idxx=np.mean(datt, axis=0)
            idxx=np.array(idxx).reshape(idxx.shape[0],)
            idx = idxx.argsort()[::-1]
            iD=[]
            print('Cluster identifier',j)
            if self.ensembl:
                for i in range(18): # Print each gene along with the feature-encoding weight
                    print('{0:s}:{1:.2e}'.format(list(self.ENSEMBLID_to_geneSymbol([self.geneNames[idx[i]]]))[0], idxx[idx[i]]))
                    iD.append(list(self.ENSEMBLID_to_geneSymbol([self.geneNames[idx[i]]]))[0])
            else:
                for i in range(18): # Print each gene along with the feature-encoding weight
                    print('{0:s}:{1:.2e}'.format(self.geneNames[idx[i]], idxx[idx[i]]))
                    iD.append(self.geneNames[idx[i]])
            idd_j.append(iD)
            
        return datt, idxx

    def get_gene_over_representation(self,topn=10):
        enrichmentTable={}    
        for i in range(self.k):
            top10Genes=[] 
            print('Cluster {0:s} ({1:d} cells)'.format(self.cluster_label[i], int(np.sum(self.cluster_assignment==i))))
            idxx=np.mean(self.data_ICF[self.cluster_assignment==i,:], axis=0)
            idxx=np.array(idxx).reshape(idxx.shape[0],)
            idx = idxx.argsort()[::-1]
            for j in range(topn): 
                top10Genes.append(self.geneNames[idx[j]])
            
            if self.ensembl:
                top10Genes=list(self.ENSEMBLID_to_geneSymbol(top10Genes,organisum=self.organsm))
                print(top10Genes)
            else:
                top10Genes=top10Genes
                print(top10Genes)
            enrichment = gprofiler(top10Genes, organism=self.organsm)
            enrichmentTable[i]=enrichment.sort_values(by=['p.value'])[["term.id","p.value","domain","term.name","intersection"]]
            print('')
        return enrichmentTable
    
    def get_MICTI_standardized_mean_over_var(self, clusters):
        
        datta=self.data_ICF[np.in1d(np.array(self.cluster_assignment), clusters),:]
        ccc=np.array(pa.DataFrame(datta).loc[~(pa.DataFrame(datta)==0).all(axis=0)])
        val=np.mean(ccc, axis=0)/(np.log(np.var(ccc, axis=0)+2))
        z_score=(val-np.mean(val))/np.sqrt(np.var(val))
        return z_score
    
    def calculate_pvalue(self, scores):
        return 2*(1-scipy.special.ndtr(abs(scores)))
    def FDR_BH(self, p):
        """Benjamini-Hochberg p-value correction for multiple hypothesis testing."""
        p = np.asfarray(p)
        by_descend = p.argsort()[::-1]
        by_orig = by_descend.argsort()
        steps = float(len(p)) / np.arange(len(p), 0, -1)
        q = np.minimum(1, np.minimum.accumulate(steps * p[by_descend]))
        return q[by_orig]
    def marker_gene_FDR_p_value(self, clusterNo):
        z_score=self.get_MICTI_standardized_mean_over_var(clusterNo)
        p_val=self.calculate_pvalue(z_score)
        FDR_pvalue=self.FDR_BH(p_val)
        result=pa.DataFrame({"Z_scores":z_score,"p_value":p_val,"fdr":FDR_pvalue}, index=self.geneNames)
        return result.sort_values("fdr")
    
    def get_gene_over_representation_for_topn_genes(self,topn=10):
        enrichmentTable={}    
        for i in range(self.k):
            
            print('Cluster {0:s} ({1:d} cells)'.format(str(self.cluster_label[i]), int(np.sum(self.cluster_assignment==i))))
            genes=list(self.marker_gene_FDR_p_value(i).index)
            top10Genes=genes[:topn]
            
            if self.ensembl:
                top10Genes=list(self.ENSEMBLID_to_geneSymbol(top10Genes,organisum=self.organsm))
                print(top10Genes)
            else:
                top10Genes=top10Genes
                print(top10Genes)
            enrichment = gprofiler(top10Genes, organism=self.organsm)
            enrichmentTable[i]=enrichment.sort_values(by=['p.value'])[["term.id","p.value","domain","term.name","intersection"]]
            print('')
        return enrichmentTable
    def get_gene_list_over_representation_analysis(self, gene_list):
        enrichment = gprofiler(gene_list, organism=self.organsm)
        enrichmentTable=enrichment.sort_values(by=['p.value'])
        return enrichmentTable
    def get_markers_by_Pvalues_and_Zscore(self,cluster,threshold_pvalue=.01, threshold_z_score=0):
        result=self.marker_gene_FDR_p_value(cluster)
        genenames=result.loc[list(np.array(result["fdr"]<threshold_pvalue) & np.array(result["Z_scores"]>threshold_z_score)),:].sort_values("fdr")
        return genenames
    
    def cluster_cells(self,numberOfCluster, method="kmeans", maxiter=10e3):
        self.cluster_label=[str(i) for i in range(numberOfCluster)]
        if method=="kmeans":
            kmean=Kmeans.Kmeans(self.data, numberOfCluster, self.geneNames, self.cellNames)
            _, self.cluster_assignment=kmean.kmeans_multiple_runs(maxiter,5)
            self.k=len(set(self.cluster_assignment))
        elif method=="GM":
            EM_GM=GM.GM(self.data, numberOfCluster, self.geneNames, self.cellNames)
            EM_GMM=EM_GM.EM_for_high_dimension()
            self.cluster_assignment=np.argmax(EM_GMM["resp"], axis=1)
            self.k=len(set(self.cluster_assignment))

        #self.get_Visualization(method="tsne")
            
        return None
