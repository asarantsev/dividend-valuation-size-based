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
    # Ljung-Box tests for original and absolute values of residuals for 5 lags
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
    # if total returns are equal or less than price returns for some years
    if min(total - price) <= 0:
        return -1 # error code
    # if we pass this check
    else:
        N = len(price)
        
        # convert arithmetic to geometric returns
        ltotalret = np.log(1 + total * 0.01)
        lpriceret = np.log(1 + price * 0.01)
        
        # wealth and index level processes: products of total and price returns
        lwealth = np.append(np.array([0]), np.cumsum(ltotalret))
        lindex = np.append(np.array([0]), np.cumsum(lpriceret))
        wealth = np.exp(lwealth)
        index = np.exp(lindex)
        
        # computation of dividends paid
        dpaid = 0.01 * (total - price) * index[:-1]
        
        # premeasure: measure with trend, cumulative sum of differences between total returns and dividend growth
        premeasure = lwealth[1:] - np.log(dpaid)
        
        # main regression to define the new valuation measure
        Reg = OLS(np.diff(premeasure), pd.DataFrame({'const' : 1, 'lag' : premeasure[:-1], 'trend': range(N - 1)})).fit()
        print(Reg.summary())
        res = Reg.resid
        
        # analysis of residuals for this main regression
        check(res, key + '-measure')
        
        # trend which we subtract from premeasure to get measure
        trend = -Reg.params['trend']/Reg.params['lag'] 
        measure = premeasure - trend * range(N)
        plt.plot(measure)
        plt.title('Valuation Measure For ' + key)
        plt.savefig(key + '-valuation.png')
        plt.close()
        print('Trend = ', trend)
        
        # modeling total returns of next year dependence upon the new valuation measure
        Reg = stats.linregress(measure[:-1], ltotalret[1:])
        print('Regression of measure vs total log returns: Slope and Intercept = ', Reg.slope, Reg.intercept)
        print('P-value = ', Reg.pvalue)
        
        # analysis of residuals
        res = ltotalret[1:] - Reg.slope * measure[:-1] - Reg.intercept * np.ones(N-1)
        check(res, key + '-returns')
        return 0

# all portfolios available from the data library
keys3 = ['Lo30', 'Med40', 'Hi30']
keys5 = ['Lo20', 'Qnt2', 'Qnt3', 'Qnt4', 'Hi20']
keys10 = ['Lo10', '2Dec', '3Dec', '4Dec', '5Dec', '6Dec', '7Dec', '8Dec', '9Dec', 'Hi10']

# read and analyze data for size-based portfolios, change to keys10 or keys5 if need
priceDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'price-size')
totalDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'total-size')
for key in keys3:
    price = priceDF[key].values
    total = totalDF[key].values
    print(compute(price, total, key+'-size'))
    
# read and analyze data for value-based portfolios, change to keys10 or keys5 if need
priceDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'price-value')
totalDF = pd.read_excel('price-total-value-size.xlsx', sheet_name = 'total-value')
for key in keys3:
    price = priceDF[key].values
    total = totalDF[key].values
    print(compute(price, total, key+'-value'))