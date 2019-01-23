from sklearn.base import TransformerMixin


class ClusterSpanFinder(TransformerMixin):
    """A transformer computing spans (equivalently, sequences) in clustered data.
    """

    def fit(self, clusters):
        """No-op
        """
        return self

    def transform(self, clusters):
        """Compute spans of data clusters, i.e. the number of points in the same
        cluster not separated from the current point by points in other clusters.

        Args:
            clusters (pd.Series): a series associating rows with clusters.

        Returns:
            pd.Series: a series associating rows with spans.
        """
        # Group *adjacent* observations from the same cluster together
        adjacency = (clusters != clusters.shift()).cumsum()
        spans = clusters.groupby(adjacency).size().reset_index(drop=True)
        groups = clusters.groupby(adjacency).ngroup().to_frame(name="group")

        return groups.join(spans, on="group")[spans.name].rename("span")
