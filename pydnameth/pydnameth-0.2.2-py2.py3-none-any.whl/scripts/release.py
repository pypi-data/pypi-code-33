from pydnameth.config.experiment.types import Method
from pydnameth.scripts.develop import \
    cpg_proc_table_linreg_dev, \
    cpg_proc_table_variance_linreg_dev, \
    cpg_proc_table_polygon_dev, \
    cpg_proc_table_z_test_linreg_dev, \
    cpg_proc_clock_linreg_dev, \
    cpg_plot_methylation_scatter_dev, \
    attributes_plot_observables_histogram_dev


def cpg_proc_table_linreg(
    data,
    annotations,
    attributes,
    params=None
):
    """
    Producing table with information for linear regression between target observable
    and methylation level for each CpG.

    Each row corresponds to specific CpG.

    Columns:

    * item: CpG id.
    * aux: gene, on which CpG is mapped.
    * R2: determination coefficient. A statistical measure of how well the regression line approximates the data points.
    * intercept: estimated value of the intercept of linear regression.
    * slope: estimated value of the slope of linear regression.
    * intercept_std: standard error of the estimate of the intercept of linear regression.
    * slope_std: standard error of the estimate of the slope of linear regression.
    * intercept_p_value: p-value for the intercept of linear regression.
    * slope_p_pvalue: p-value for the slope of linear regression.

    Possible parameters of experiment:

    * None

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param params: parameters of experiment.
    """
    cpg_proc_table_linreg_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        params=params
    )


def cpg_proc_table_variance_linreg(
    data,
    annotations,
    attributes,
    params=None
):
    """
    Producing table with information for linear regression of variance from primary linear regression between target observable
    and methylation level for each CpG.

    Each row corresponds to specific CpG.

    Columns:

    * item: CpG id.
    * aux: gene, on which CpG is mapped.
    * R2: determination coefficient of primary linear regression.
      A statistical measure of how well the regression line approximates the data points.
    * intercept: estimated value of the intercept of primary linear regression.
    * slope: estimated value of the slope of primary linear regression.
    * intercept_std: standard error of the estimate of the intercept of primary linear regression.
    * slope_std: standard error of the estimate of the slope of primary linear regression.
    * intercept_p_value: p-value for the intercept of primary linear regression.
    * slope_p_pvalue: p-value for the slope of primary linear regression.
    * R2_var: determination coefficient of linear regression for variance.
      A statistical measure of how well the regression line approximates the data points.
    * intercept_var: estimated value of the intercept of linear regression for variance.
    * slope_var: estimated value of the slope of linear regression for variance.
    * intercept_std_var: standard error of the estimate of the intercept of linear regression for variance.
    * slope_std_var: standard error of the estimate of the slope of linear regression for variance.
    * intercept_p_value_var: p-value for the intercept of linear regression for variance.
    * slope_p_pvalue_var: p-value for the slope of linear regression for variance.

    Possible parameters of experiment:

    * None

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param params: parameters of experiment.
    """
    cpg_proc_table_variance_linreg_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        params=params
    )


def cpg_proc_table_polygon(
    data,
    annotations,
    attributes,
    observables_list,
    params=None
):
    """
    Producing table with information about observable-specificity of methylation level
    and target observable for each CpG using result of linear regression performed for each subset separately.

    Firstly, for each subjects subset creates polygon.

    Secondly, intersection of all of polygons analyzed and linear regression characteristics analyzed.

    Each row corresponds to specific CpG.

    Columns:

    * item: CpG id.
    * aux: gene, on which CpG is mapped.
    * area_intersection_rel: relative intersection area of polygons
      which is equals area of polygon(s) intersection to area of polygons union ratio.
    * slope_intersection_rel: relative intersection area of allowed regions for slopes of linear regression.
    * max_abs_slope: maximal absolute slope between all provided subjects subsets

    For each subjects subset the next columns are added to the resulting table:

    * R2_***: determination coefficient. A statistical measure of how well the regression line approximates the data points.
    * intercept_***: estimated value of the intercept of linear regression.
    * slope_***: estimated value of the slope of linear regression.
    * intercept_std_***: standard error of the estimate of the intercept of linear regression.
    * slope_std_***: standard error of the estimate of the slope of linear regression.
    * intercept_p_value_***: p-value for the intercept of linear regression.
    * slope_p_pvalue_***: p-value for the slope of linear regression.

    Where *** is the name of subjects subset.

    Possible parameters of experiment:

    * None

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param observables_list: list of subjects subsets. Each element in list is dict,
     where ``key`` is observable name and ``value`` is possible values for this observable.
    :param params: parameters of experiment.
    """

    child_method = Method.linreg

    cpg_proc_table_polygon_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        observables_list=observables_list,
        child_method=child_method,
        params=params
    )


def cpg_proc_table_z_test_linreg(
    data,
    annotations,
    attributes,
    observables_list,
    params=None
):
    """
    Producing table with information about z-test for slopes of linear regression performed for each subset separately.

    Each row corresponds to specific CpG.

    Columns:

    * item: CpG id.
    * aux: gene, on which CpG is mapped.
    * z_value: number of standard deviations by which data point is above the mean value.
      The considered data point is the difference between two linear regressions slopes.
    * abs_z_value: absolute z_value
    * p_value: probability of rejecting the null hypothesis that the difference in slopes is zero.

    For each subjects subset the next columns are added to the resulting table:

    * R2_***: determination coefficient. A statistical measure of how well the regression line approximates the data points.
    * intercept_***: estimated value of the intercept of linear regression.
    * slope_***: estimated value of the slope of linear regression.
    * intercept_std_***: standard error of the estimate of the intercept of linear regression.
    * slope_std_***: standard error of the estimate of the slope of linear regression.
    * intercept_p_value_***: p-value for the intercept of linear regression.
    * slope_p_pvalue_***: p-value for the slope of linear regression.

    Where *** is the name of subjects subset.

    Possible parameters of experiment:

    * None

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param observables_list: list of subjects subsets. Each element in list is dict,
     where ``key`` is observable name and ``value`` is possible values for this observable.
     :param params: parameters of experiment.
    """

    child_method = Method.linreg

    cpg_proc_table_z_test_linreg_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        observables_list=observables_list,
        child_method=child_method,
        params=params
    )

def cpg_proc_clock_linreg(
    data,
    annotations,
    attributes,
    params=None
):
    """
    Producing epigentic clock, using best CpGs target-predictors.

    Firstly, produce linear regression between target observable
    and methylation level to define best CpGs target-predictors, which are at the top of table.

    Secondly, produce epigentic clock.

    Epigentic clock represents as table:
    Each row corresponds to clocks, which are built on all CpGs from the previous rows including the current row.
    Columns:

    * item: CpG id.
    * aux: gene, on which CpG is mapped.
    * R2: determination coefficient of linear regression between real and predicted target observable.
      A statistical measure of how well the regression line approximates the data points.
    * r: correlation coefficient of linear regression between real and predicted target observable.
    * evs: explained variance regression score.
    * mae: mean absolute error regression loss.
    * summary: summary output from OLS.

    Possible parameters of experiment:

    * ``'type'``: type of clocks. \n
      Possible options: \n
      ``'all'``: iterative building of clocks starting from one element in the model, ending with ``'size'`` elements in the model. \n
      ``'single '``: building of clocks only with ``'size'`` elements in the model. \n
      ``'deep'``: iterative building of clocks starting from one element in the model, ending with ``'size'`` elements in the model, but choosing all posible combinations from ``'size'`` elements.
    * ``'part'``: the proportion of considered number of subject in the test set. From ``0.0`` to ``1.0``.
    * ``'size'``: maximum number of exogenous variables in a model.
    * ``'runs'`` number of bootstrap runs in model

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param params: parameters of experiment.
    """

    child_method = Method.linreg

    cpg_proc_clock_linreg_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        child_method=child_method,
        params=params
    )

def cpg_plot_methylation_scatter(
    data,
    annotations,
    attributes,
    cpg_list,
    observables_list,
    params=None
):
    """
    Plotting methylation level from observables as scatter for provided subjects subsets and provided CpG list.

    Possible parameters of experiment:

     * ``'x_range'``: can be ``'auto'`` or list with two elements, which are borders of target axis.

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param cpg_list: List of CpGs for plotting
    :param observables_list: list of subjects subsets. Each element in list is dict,
     where ``key`` is observable name and ``value`` is possible values for this observable.
    :param params: parameters of experiment.
    """

    child_method = Method.linreg

    cpg_plot_methylation_scatter_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        cpg_list=cpg_list,
        observables_list=observables_list,
        child_method=child_method,
        params=params
    )


def attributes_plot_observables_histogram(
    data,
    annotations,
    attributes,
    observables_list,
    params=None
):
    """
    Plotting histogram for target observable distribution for provided subjects subsets and provided CpG list.

    Possible parameters of experiment:

    * ``'bin_size'``: bin size for numeric target. \n
      For categorical target is not considered.
    * ``'opacity'``: opacity level.
      From ``0.0`` to ``1.0``.
    * ``'barmode'``: type of barmode. \n
      Possible options: \n
      ``'overlay'`` for overlaid histograms. \n
      ``'stack'`` for stacked histograms. \n

    :param data: pdm.Data instance, which specifies information about dataset.
    :param annotations: pdm.Annotations instance, which specifies subset of CpGs.
    :param attributes: pdm.Attributes instance, which specifies information about subjects.
    :param cpg_list: List of CpGs for plotting
    :param observables_list: list of subjects subsets. Each element in list is dict,
     where ``key`` is observable name and ``value`` is possible values for this observable.
    :param params: parameters of experiment.
    """
    attributes_plot_observables_histogram_dev(
        data=data,
        annotations=annotations,
        attributes=attributes,
        observables_list=observables_list,
        params=params
    )

