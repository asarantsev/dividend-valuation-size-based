import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.api import OLS
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from scipy.stats import shapiro

def compute(price, total, key):
    print('')
    print(key)
    print('')
    ltotal = np.log(1 + total * 0.01)
    lwealth = np.append(np.array([0]), np.cumsum(ltotal))
    wealth = np.exp(lwealth)
    dpaid = 0.01 * (total - price) * wealth[:-1]
    premeasure = lwealth[1:] - np.log(dpaid)
    Reg = OLS(np.diff(premeasure), pd.DataFrame({'const' : 1, 'lag' : premeasure[:-1], 'trend': range(len(premeasure) - 1)})).fit()
    print(Reg.summary())
    res = Reg.resid
    plot_acf(res)
    plt.title('original residuals ' + key)
    plt.show()
    plot_acf(abs(res))
    plt.title('absolute residuals ' + key)
    plt.show()
    print('Shapiro-Wilk p = ', shapiro(res)[1])
    print('Trend = ', -Reg.params['trend']/Reg.params['lag'])
    
priceDF = pd.read_excel('price-total.xlsx', sheet_name = 'price')
totalDF = pd.read_excel('price-total.xlsx', sheet_name = 'total')
keys = ['Lo 30', 'Med 40', 'Hi 30', 'Lo 20', 'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20', '2-Dec', '3-Dec', '4-Dec', '5-Dec', '6-Dec', '7-Dec', '8-Dec', '9-Dec', 'Hi 10']
for key in keys:
    price = priceDF[key].values
    total = totalDF[key].values
    compute(price, total, key)