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
    if min(total - price) <= 0:
        return -1
    else:
        N = len(price)
        ltotalret = np.log(1 + total * 0.01)
        lpriceret = np.log(1 + price * 0.01)
        lwealth = np.append(np.array([0]), np.cumsum(ltotalret))
        lindex = np.append(np.array([0]), np.cumsum(lpriceret))
        wealth = np.exp(lwealth)
        index = np.exp(lindex)
        dpaid = 0.01 * (total - price) * index[:-1]
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

keys = ['Lo30', 'Med40', 'Hi30', 'Lo20', 'Qnt2', 'Qnt3', 'Qnt4', 'Hi20', 'Lo10', '2Dec', '3Dec', '4Dec', '5Dec', '6Dec', '7Dec', '8Dec', '9Dec', 'Hi10']

priceDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'price-size')
totalDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'total-size')
for key in keys:
    price = priceDF[key].values
    total = totalDF[key].values
    print(compute(price, total, key+'-size'))
    
priceDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'price-value')
totalDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'total-value')
for key in keys:
    price = priceDF[key].values
    total = totalDF[key].values
    print(compute(price, total, key+'-value'))