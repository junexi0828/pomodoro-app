#----------------------------------
# 선형계획법 기본 예제 (케이크 & 바게트)
#----------------------------------
from pulp import *

# 1. 문제 정의 (최대화 문제)
LP = LpProblem("Cake_and_Baguette", LpMaximize)

# 2. 결정변수 정의 (X1: 케이크, X2: 바게트)
X1 = LpVariable("X1", lowBound=0)
X2 = LpVariable("X2", lowBound=0)

# 3. 목적함수 입력
LP += 10 * X1 + 6 * X2

# 4. 제약조건 입력
LP += 3 * X1 + 8 * X2 <= 20  # 밀가루 제약
LP += 45 * X1 + 30 * X2 <= 180  # 오븐 시간 제약

# 5. 최적화 수행
LP.solve()

# 6. 결과 출력
for v in LP.variables():
    print(f"{v.name} = {v.varValue}")

print("총 수익:", value(LP.objective))

#-------------------------------------
# 소시지 생산 문제
#-------------------------------------
from pulp import *

# 문제 정의
LP = LpProblem("sausage_problem", LpMaximize)

# 결정변수 정의
X11 = LpVariable("X11", lowBound=0)
X12 = LpVariable("X12", lowBound=0)
X21 = LpVariable("X21", lowBound=0)
X22 = LpVariable("X22", lowBound=0)

# 목적함수 정의
LP += (3000 - 2000) * X11 + (2000 - 1000) * X12 + \
      (3000 - 3000) * X21 + (2000 - 2000) * X22

# 제약조건 정의
LP += X11 + X12 <= 60     # 원료1
LP += X21 + X22 <= 60     # 원료2
LP += X11 + X21 == 40     # 소시지1 원료합
LP += X12 + X22 == 40     # 소시지2 원료합

# 최적화
LP.solve()

# 출력
for v in LP.variables():
    print(f"{v.name} = {v.varValue}")
print("총 이익:", value(LP.objective))

#-------------------------------------
# ex16_3_newsvendor_simulation.py (뉴스벤더 시뮬레이션)
#-------------------------------------
import numpy as np

# 가격 설정
c = 100   # 생산비
p = 500   # 판매가
s = 0     # 잔존가격

# 비용 계산
Cu = p - c
Co = c - s

# 수요 정규분포 설정
mu = 300
sigma = 150
Q = 300

# 시뮬레이션
profit = []
for i in range(100000):
    x = int(np.random.normal(mu, sigma))
    x = max(0, x)
    if x <= Q:
        π = -c * Q + p * x + s * (Q - x)
    else:
        π = -c * Q + p * Q
    profit.append(π)

print("기대이익:", np.mean(profit))

#---------------------------------
# ex16_4_neuralnet_inventory.py (신경망 기반 생산계획 최적화)
#---------------------------------
import numpy as np
import tensorflow as tf
from tensorflow import keras

# 데이터 생성
n = 500
temp = np.random.uniform(0, 30, n)
weather = np.random.binomial(1, 0.3, n)

demand = np.zeros(n)
for i in range(n):
    mean = 5 * temp[i] + 50
    std = 0.5 * mean if weather[i] == 0 else 0.6 * mean
    demand[i] = np.random.normal(mean, std)

# 입력 및 출력
x_train = np.column_stack((temp / 30, weather))
y_train = demand

# 커스텀 손실 함수 정의
def inventory_loss(y_true, y_pred):
    c = 2000
    p = 8000
    s = 0
    Cu = p - c
    Co = c - s
    stock = y_pred - y_true
    is_understock = tf.cast(stock < 0, tf.float32)
    inventory_error = tf.abs(stock)
    return tf.where(is_understock, Cu * inventory_error, Co * inventory_error)

# 신경망 구성
model = keras.models.Sequential([
    keras.layers.Dense(2, activation='relu', input_shape=(2,)),
    keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss=inventory_loss)
model.fit(x_train, y_train, epochs=20, verbose=0)

# 테스트
x_test = np.column_stack((np.random.uniform(0, 30, 10000) / 30,
                          np.random.binomial(1, 0.3, 10000)))
Q_prop = model.predict(x_test).flatten()

# 수요 생성 및 이익 계산
profit = []
for i in range(len(Q_prop)):
    temp = x_test[i][0] * 30
    w = x_test[i][1]
    mean = 5 * temp + 50
    std = 0.5 * mean if w == 0 else 0.6 * mean
    d = np.random.normal(mean, std)
    Q = Q_prop[i]
    if d <= Q:
        π = -2000 * Q + 8000 * d
    else:
        π = -2000 * Q + 8000 * Q
    profit.append(π)

print("기대이익:", np.mean(profit))

#------------------------------------------------------------------------------------------------
# 똑같은 예제 다른 풀이  시작
#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
# ① 선형계획법 - 베이커리 예제 (케이크 & 바게트)
from pulp import *

# 문제 정의
model1 = LpProblem("Bakery_Profit_Maximization", LpMaximize)

# 결정변수 (케이크: x, 바게트: y)
x = LpVariable("Cake", lowBound=0, cat='Continuous')
y = LpVariable("Baguette", lowBound=0, cat='Continuous')

# 목적함수 (이익 최대화)
model1 += 5*x + 3*y

# 제약조건
model1 += 2*x + y <= 8    # 밀가루 제약
model1 += x + y <= 5      # 오븐 시간 제약

# 최적화 수행
model1.solve()

# 결과 출력
print("[베이커리 예제]")
print("케이크 생산량:", x.value())
print("바게트 생산량:", y.value())
print("최대 이익:", value(model1.objective))
print("-"*40)

#------------------------------------------------------------------------------------------------
# ② 선형계획법 - 소시지 생산 최적화 예제
model2 = LpProblem("Sausage_Optimization", LpMaximize)

x2 = LpVariable("Regular", lowBound=0, cat='Continuous')
y2 = LpVariable("Spicy", lowBound=0, cat='Continuous')

model2 += 1.5*x2 + 2*y2
model2 += 4*x2 + 3*y2 <= 48  # 돼지고기 제약
model2 += 2*x2 + 4*y2 <= 40  # 쇠고기 제약

model2.solve()

print("[소시지 예제]")
print("Regular 소시지 생산:", x2.value())
print("Spicy 소시지 생산:", y2.value())
print("총 이익:", value(model2.objective))
print("-"*40)

#------------------------------------------------------------------------------------------------
# ③ 뉴스벤더 모델 - 시뮬레이션 기반 최적 주문량 찾기
import numpy as np

Co = 2   # 과잉비용
Cu = 8   # 부족비용
mu = 50  # 평균수요
sigma = 10  # 표준편차

Q_range = np.arange(30, 80, 1)
profits = []

for Q in Q_range:
    demand = np.random.normal(mu, sigma, 10000)
    shortage = np.maximum(demand - Q, 0)
    overage = np.maximum(Q - demand, 0)
    profit = Cu*(Q - shortage) - Co*overage
    profits.append(np.mean(profit))

best_Q = Q_range[np.argmax(profits)]
print("[뉴스벤더 시뮬레이션]")
print("최적 주문량(Q*) :", best_Q)
print("최대 기대이익 :", np.max(profits))
print("-"*40)

#------------------------------------------------------------------------------------------------
# ④ 뉴스벤더 신경망 기반 최적화 - Custom Loss 적용
import tensorflow as tf
from tensorflow import keras

np.random.seed(42)
X_train = np.random.normal(50, 10, 10000)
y_train = X_train

Co = 2
Cu = 8

def newsvendor_loss(y_true, y_pred):
    underage = tf.maximum(y_true - y_pred, 0)
    overage = tf.maximum(y_pred - y_true, 0)
    return Cu * underage + Co * overage

model = keras.Sequential([
    keras.layers.Dense(10, input_shape=[1], activation='relu'),
    keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss=newsvendor_loss)
model.fit(X_train, y_train, epochs=30, batch_size=32, verbose=0)

Q_opt = model.predict(np.array([[0]]))
print("[뉴스벤더 NN 최적화]")
print("신경망이 예측한 최적 주문량:", Q_opt[0][0])
