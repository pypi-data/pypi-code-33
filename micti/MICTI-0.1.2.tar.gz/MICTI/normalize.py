import numpy as np 

def normalizeUMIWithscalefactor(data, scale_factor=10e6):
    cellNormalizedData=np.log(1+(data/np.sum(data,axis=1)[0]))*scale_factor
    return(cellNormalizedData)

def getTPM(rowCountData, index_column=None, ensembol_gene=False, withGene_version=False):

    if index_column is not None:
        rowCountData.index=rowCountData[index_column]
        rowCountData=rowCountData.drop([index_column], axis=1)
    #read gene annotation from file
    geneNames=pa.read_csv("data/mart_export_stable_genes_human.txt", sep="\t")
    geneNames["len_inkb"]=(geneNames["Gene end (bp)"]-geneNames["Gene start (bp)"])/1000
    if ensembol_gene & withGene_version:
        geneNames.index=geneNames["Gene stable ID version"]
    elif ensembol_gene:
        geneNames.index=geneNames["Gene stable ID"]
    else:
        geneNames.index=geneNames["Gene name"]
    #get gene length information
    gene_length=geneNames.loc[list(rowCountData.index),:].dropna()["len_inkb"]
    count_data=rowCountData.loc[gene_length.index,:]

    count_data_RKB=count_data.div(list(gene_length), axis=0)
    count_data_TPM=count_data_RKB.div(count_data_RKB.sum(axis=0), axis=1)*10e6

    return count_data_TPM




















	


