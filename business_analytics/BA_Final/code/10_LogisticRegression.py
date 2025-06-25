# =============================
# (1) 시그모이드 함수 직접 구현 및 시각화
import numpy as np
import matplotlib.pyplot as plt

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

x = np.linspace(-10, 10, 100)
y = sigmoid(x)

plt.plot(x, y)
plt.title("Sigmoid Function")
plt.grid()
plt.show()

# =============================
# (2) 텐서플로우를 이용한 로지스틱 회귀 직접 구현

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# 입력 데이터 (광고노출 횟수)
x = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
# 정답 데이터 (구매 여부: 0=미구매, 1=구매)
y = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]

# 시그모이드 확률 함수
def prob(x, w, b):
    z = w * x + b
    return 1 / (1 + tf.exp(-z))

# 손실 함수 (엔트로피)
def loss(x, y, w, b):
    a = prob(x, w, b)
    l = y * tf.math.log(a) + (1 - y) * tf.math.log(1 - a)
    return -tf.reduce_mean(l)

# 그래디언트 함수
def grad_w(x, y, w, b):
    a = prob(x, w, b)
    return tf.reduce_mean((a - y) * x)

def grad_b(x, y, w, b):
    a = prob(x, w, b)
    return tf.reduce_mean(a - y)

# 초기값 설정
w = tf.Variable(0.2)
b = tf.Variable(-0.2)
lr = 0.01

# 학습 루프
while True:
    dw = grad_w(x, y, w, b)
    db = grad_b(x, y, w, b)
    w.assign_sub(lr * dw)
    b.assign_sub(lr * db)
    if abs(dw.numpy()) < 0.0001 and abs(db.numpy()) < 0.0001:
        break

print("최종 w:", w.numpy())
print("최종 b:", b.numpy())

# 확률 시각화
x_test = np.linspace(0, 55, 100)
y_prob = prob(x_test, w, b)

plt.plot(x_test, y_prob)
plt.scatter(x, y, color='red')  # 실제 데이터
plt.title("Logistic Regression with TensorFlow")
plt.grid()
plt.show()

# 예측 결과
y_hat = []
for xi in x:
    p = prob(xi, w, b).numpy()
    y_hat.append(1 if p >= 0.5 else 0)
print("예측 결과:", y_hat)
print("정답:", y)

# =============================
# (3) 사이킷런으로 로지스틱 회귀 구현

from sklearn.linear_model import LogisticRegression
import numpy as np

# 입력데이터 및 정답
x = [[5], [10], [15], [20], [25], [30], [35], [40], [45], [50]]
y = [0, 0, 0, 0, 1, 1, 0, 1, 1, 1]

# 모델 학습
model = LogisticRegression(penalty=None)  # penalty 제거
model.fit(x, y)

# 예측 결과
print("예측:", model.predict(x))

# 가중치 및 절편
print("가중치 w:", model.coef_)
print("절편 b:", model.intercept_)

# =============================
# (4) Kaggle 신용카드 부정사용 탐지 (기본 예제)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# 데이터 불러오기 (CSV 위치는 적절히 변경)
df = pd.read_csv("creditcard.csv")

# 피처/정답 분리
x = df.drop("Class", axis=1)
y = df["Class"]

# 학습/테스트 분리
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

# 로지스틱 회귀 모델 훈련
model = LogisticRegression(penalty=None, max_iter=1000)
model.fit(x_train, y_train)

# 예측 및 성능 평가
y_pred = model.predict(x_test)
print(classification_report(y_test, y_pred))