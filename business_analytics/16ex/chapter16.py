'''
from pulp import *

LP = LpProblem("bakery problem", LpMaximize)
X1 = LpVariable("cake")
X2 = LpVariable("baguette")
LP += 10*X1 + 6*X2
LP += 3*X1 + 8*X2 <= 20
LP += 45*X1 + 30*X2 <= 180
LP += X1 >= 0
LP += X2 >= 0
LP.solve()
for v in LP.variables():
    print(v.name, '=', v.varValue)
print("Total profit is ", value(LP.objective))

from pulp import *

LP = LpProblem("sausage_problem", LpMaximize)
Xcr = LpVariable("Xcr",0)
Xbr = LpVariable("Xbr",0)
Xpr = LpVariable("Xpr",0)
Xar = LpVariable("Xar",0)
Xcb = LpVariable("Xcb",0)
Xbb = LpVariable("Xbb",0)
Xpb = LpVariable("Xpb",0)
Xab = LpVariable("Xab",0)
Xcm = LpVariable("Xcm",0)
Xbm = LpVariable("Xbm",0)
Xpm = LpVariable("Xpm",0)
Xam = LpVariable("Xam",0)

LP += 0.7*Xcr + 0.6*Xbr + 0.4*Xpr + 0.85*Xar \
   + 1.05*Xcb + 0.95*Xbb + 0.75*Xpb + 1.20*Xab \
   + 1.55*Xcm + 1.45*Xbm + 1.25*Xpm + 1.70*Xam

LP += Xcr + Xcb + Xcm <= 200
LP += Xbr + Xbb + Xbm <= 300
LP += Xpr + Xpb + Xpm <= 150
LP += Xar + Xab + Xam <= 400
LP += 0.9*Xbr + 0.9*Xpr - 0.1*Xcr - 0.1*Xar <= 0
LP += 0.8*Xcr - 0.2*Xbr - 0.2*Xpr - 0.2*Xar >= 0
LP += 0.25*Xbb - 0.75*Xcb - 0.75*Xpb - 0.75*Xab >= 0
LP += Xam == 0
LP += 0.5*Xbm + 0.5*Xpm - 0.5*Xcm - 0.5*Xam <= 0

LP.solve()

for v in LP.variables():
    print(v.name, '=', v.varValue)
print("Total profit is ", value(LP.objective))

import numpy as np
from numpy.random import normal
from statistics import NormalDist

p=500
c=100
s=0
Cu=p-c
Co=c-s
mu=300
sigma=150

Q = int(NormalDist(mu=mu, sigma=sigma).inv_cdf(0.8))
n=100000
sum = 0
for i in range(n):
    x = np.random.normal(mu, sigma)
    if x<0: x=0
    profit = -c*Q
    if x<=Q: profit += p*x + s*(Q-x)
    else: profit += p*Q
    sum += profit
avg = sum/n
print("Order Quantity = ", Q)
print("Expected profit = ", avg)

import numpy as np
n=100000
temp = np.random.uniform(0, 30, n)
weather = np.random.binomial(1, 0.3, n)
demand = np.zeros(n, dtype='float32')
for i in range(n):
    mu_d = 5*temp[i] + 50
    if weather[i]==0: sigma_d = 0.5 * mu_d
    else: sigma_d = 0.6 * mu_d
    d = np.random.normal(mu_d, sigma_d)
    if d<0: d=0
    demand[i] = d

p=8000
c=2000
s=0
Cu=p-c
Co=c-s

sum_profit = 0
sum_Q = 0
for i in range(n):
    mu_d = 5*temp[i] + 50
    Q = mu_d
    d = demand[i]
    profit = -c*Q
    if d<=Q: profit += p*d + s*(Q-d)
    else: profit += p*Q
    sum_Q += Q
    sum_profit += profit

avg_Q = sum_Q/n
avg_profit = sum_profit/n
print("Production Quantity = ", avg_Q)
print("Expected profit = ", avg_profit)


import numpy as np
n=100000
temp = np.random.uniform(0, 30, n)
weather = np.random.binomial(1, 0.3, n)
demand = np.zeros(n, dtype='float32')
for i in range(n):
    mu_d = 5*temp[i] + 50
    if weather[i]==0: sigma_d = 0.5 * mu_d
    else: sigma_d = 0.6 * mu_d
    d = np.random.normal(mu_d, sigma_d)
    if d<0: d=0
    demand[i] = d

p=8000
c=2000
s=0
Cu=p-c
Co=c-s
import tensorflow as tf
def inventory_loss(demand_true, q):
    stock = q-demand_true
    is_understock = stock < 0
    inventory_error = tf.abs(stock)
    understock_loss = Cu*inventory_error
    overstock_loss = Co*inventory_error
    return tf.where(is_understock, understock_loss, overstock_loss)

x_train = np.zeros((n,2), dtype='float32')
x_train[:,0] = (temp - min(temp))/(max(temp)-min(temp))
x_train[:,1] = weather
demand_train = (demand - min(demand))/(max(demand)-min(demand))

from tensorflow import keras
model = keras.Sequential([
    keras.layers.Dense(2, input_shape=(2,), activation='sigmoid'),
    keras.layers.Dense(1, activation=None),
])
model.compile(optimizer='adam', loss=inventory_loss)
model.fit(x_train, demand_train, epochs=20)

n_test=10000
temp_new = np.random.uniform(0, 30, n_test)
weather_new = np.random.binomial(1, 0.3, n_test)
x_test = np.zeros((n_test,2), dtype='float32')
x_test[:,0]=(temp_new - min(temp))/(max(temp)-min(temp))
x_test[:,1]=np.random.binomial(1, 0.3, n_test)
pred = model.predict(x_test)
Q_prop = pred*(max(demand)-min(demand))+min(demand)
print("Mean of Q_prop = ", np.mean(Q_prop))
'''

import numpy as np
n=100000
temp = np.random.uniform(0, 30, n)
weather = np.random.binomial(1, 0.3, n)
demand = np.zeros(n, dtype='float32')
for i in range(n):
    mu_d = 5*temp[i] + 50
    if weather[i]==0: sigma_d = 0.5 * mu_d
    else: sigma_d = 0.6 * mu_d
    d = np.random.normal(mu_d, sigma_d)
    if d<0: d=0
    demand[i] = d

p=8000
c=2000
s=0
Cu=p-c
Co=c-s
import tensorflow as tf
def inventory_loss(demand_true, q):
    stock = q-demand_true
    is_understock = stock < 0
    inventory_error = tf.abs(stock)
    understock_loss = Cu*inventory_error
    overstock_loss = Co*inventory_error
    return tf.where(is_understock, understock_loss, overstock_loss)
x_train = np.zeros((n,2), dtype='float32')
x_train[:,0] = (temp - min(temp))/(max(temp)-min(temp))
x_train[:,1] = weather
demand_train = (demand - min(demand))/(max(demand)-min(demand))

from tensorflow import keras
model = keras.Sequential([
    keras.layers.Dense(2, input_shape=(2,), activation='sigmoid'),
    keras.layers.Dense(1, activation=None),
])
model.compile(optimizer='adam', loss=inventory_loss)
model.fit(x_train, demand_train, epochs=20)

n_test=100000
temp_new = np.random.uniform(0, 30, n_test)
weather_new = np.random.binomial(1, 0.3, n_test)
x_test = np.zeros((n_test,2), dtype='float32')
x_test[:,0]=(temp_new - min(temp))/(max(temp)-min(temp))
x_test[:,1]=np.random.binomial(1, 0.3, n_test)
pred = model.predict(x_test)
Q_prop = pred*(max(demand)-min(demand))+min(demand)

sum_profit = 0
sum_Q = 0
for i in range(n_test):
    mu_d = 5*temp_new[i] + 50
    if weather_new[i]==0: sigma_d = 0.5 * mu_d
    else: sigma_d = 0.6 * mu_d
    d = np.random.normal(mu_d, sigma_d)
    if d<0: d=0
    Q = Q_prop[i]
    profit = -c*Q
    if d<=Q: profit += p*d + s*(Q-d)
    else: profit += p*Q
    sum_Q += Q
    sum_profit += profit

avg_Q = sum_Q/n
avg_profit = sum_profit/n
print("Production Quantity = ", avg_Q)
print("Expected profit = ", avg_profit)
