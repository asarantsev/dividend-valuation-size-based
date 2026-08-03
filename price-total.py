import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.api import OLS
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from scipy import stats 
from statsmodels.stats.diagnostic import acorr_ljungbox as LB

# analysis of residuals 
def check(res, key):
    print(LB(res, lags=[5], return_df = True)['lb_pvalue'].values[0])
    print(LB(abs(res), lags = [5], return_df = True)['lb_pvalue'].values[0])
    plot_acf(res, zero = False)
    plt.title('Original Residuals ' + key)
    plt.savefig(key + '-original.png')
    plt.close()
    plot_acf(abs(res), zero = False)
    plt.title('Absolute Residuals ' + key)
    plt.savefig(key + '-absolute.png')
    plt.close()
    print('Shapiro-Wilk p = ', stats.shapiro(res)[1])

# price = arithmetic price returns in %, total = arithmetic total returns in %
def compute(price, total, key):
    print('')
    print(key)
    print('')
    N = len(price)
    ltotalret = np.log(1 + total * 0.01)
    lpriceret = np.log(1 + price * 0.01)
    lwealth = np.append(np.array([0]), np.cumsum(ltotalret))
    lindex = np.append(np.array([0]), np.cumsum(lpriceret))
    wealth = np.exp(lwealth)
    index = np.exp(lindex)
    dpaid = 0.01 * (total - price) * index[:-1]
    if min(dpaid) < 0:
        return -1
    if min(dpaid) > 0:
        premeasure = lwealth[1:] - np.log(dpaid)
        Reg = OLS(np.diff(premeasure), pd.DataFrame({'const' : 1, 'lag' : premeasure[:-1], 'trend': range(N - 1)})).fit()
        print(Reg.summary())
        res = Reg.resid
        check(res, key + '-measure')
        trend = -Reg.params['trend']/Reg.params['lag']
        measure = premeasure - trend * range(N)
        plt.plot(measure)
        plt.title('Valuation Measure For ' + key)
        plt.savefig(key + '-valuation.png')
        plt.close()
        print('Trend = ', trend)
        return 0
    
priceDF = pd.read_excel('price-total.xlsx', sheet_name = 'price')
totalDF = pd.read_excel('price-total.xlsx', sheet_name = 'total')
keys = ['Lo 30', 'Med 40', 'Hi 30', 'Lo 20', 'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20', 'Lo 10', '2-Dec', '3-Dec', '4-Dec', '5-Dec', '6-Dec', '7-Dec', '8-Dec', '9-Dec', 'Hi 10']
for key in keys:
    price = priceDF[key].values
    total = totalDF[key].values
    compute(price, total, key)        