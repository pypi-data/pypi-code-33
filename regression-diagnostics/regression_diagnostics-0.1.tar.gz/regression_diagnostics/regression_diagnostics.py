# Import libraires and set style
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")
from scipy import stats
from statsmodels.graphics.gofplots import ProbPlot

plt.style.use('seaborn')
plt.rc('font', size=14)
plt.rc('figure', titlesize=18)
plt.rc('axes', labelsize=15)
plt.rc('axes', titlesize=18)

class RegressionDiagnostics():

    def __init__(self, actual, predicted):

        """ RegressionDiagnostics class for calculating and
        visualizing a probability distribution.

		Attributes:
			actual (list of floats) values input by user
			predicted (list of floats) values input by user
			residuals (list of floats) actual - predicted
            standard residuals(list of floats) residuals divided by std
		"""

        self.y_test = actual
        self.y_pred = predicted
        self.residuals = self.y_test - self.y_pred
        self.standard_residuals = self.residuals / np.std(self.residuals)

    def shapiro(self):

        """Function to calculate the shapiro-wilk p-value of the residuals

		Args:
			None

		Returns:
			float: Shapiro-Wilk p-value

		"""

        shapiro_pvalue = stats.shapiro(self.residuals)[1]
        print("Shapiro-Wilk p-value: %f"% (shapiro_pvalue))
        return shapiro_pvalue

    def fit_residplot(self):

        """Function to plot fitted vs residuals

		Args:
			None

		Returns:
			None

		"""

        plot_lm_1 = plt.figure(1)
        plot_lm_1.set_figheight(8)
        plot_lm_1.set_figwidth(12)

        sns.residplot(self.y_pred, self.y_test, scatter_kws={'alpha': 0.5},
        line_kws={'color': 'red', 'lw': 1, 'alpha': 0.9})

        plot_lm_1.axes[0].set_title('Residuals vs Fitted')
        plot_lm_1.axes[0].set_xlabel('Fitted values')
        plot_lm_1.axes[0].set_ylabel('Residuals')

        plt.show();

    def qqplot(self):

        """Function to plot qqplot of the standard residuals

		Args:
			None

		Returns:
			None

		"""

        QQ = ProbPlot(self.standard_residuals)
        plot_lm_2 = QQ.qqplot(line='45', alpha=0.5, color='#4C72B0', lw=1)

        plot_lm_2.set_figheight(8)
        plot_lm_2.set_figwidth(12)

        plot_lm_2.axes[0].set_title('Normal Q-Q')
        plot_lm_2.axes[0].set_xlabel('Theoretical Quantiles')
        plot_lm_2.axes[0].set_ylabel('Standardized Residuals');

        plt.show();

    def pred_actualplot(self):

        """Function to plot the predicted vs actual values

		Args:
			None

		Returns:
			None

		"""

        plot_lm_3 = plt.figure(3)
        plot_lm_3.set_figheight(8)
        plot_lm_3.set_figwidth(12)

        plt.scatter(self.y_pred, self.y_test, alpha=0.5)

        lineStart = self.y_pred.min()
        lineEnd = self.y_pred.max()
        axisStart = min(self.y_pred.min(), self.y_test.min())
        axisEnd = max(self.y_pred.max(), self.y_test.max())

        plt.plot([lineStart, lineEnd], [lineStart, lineEnd], 'k-', color = 'r')
        plt.xlim(axisStart, axisEnd)
        plt.ylim(axisStart, axisEnd)


        plot_lm_3.axes[0].set_title('Predicted vs Actual')
        plot_lm_3.axes[0].set_xlabel('Predicted values')
        plot_lm_3.axes[0].set_ylabel('Actual values');
