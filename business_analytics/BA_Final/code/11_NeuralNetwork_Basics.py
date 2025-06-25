# =============================
# ex11-1.py — 퍼셉트론 예제: OR 연산
# =============================

def perceptron(x1, x2):
    w1, w2, b = 1, 1, -0.5
    z = w1 * x1 + w2 * x2 + b
    return 1 if z >= 0 else 0

# 테스트
print(perceptron(0, 0))  # 0
print(perceptron(0, 1))  # 1
print(perceptron(1, 0))  # 1
print(perceptron(1, 1))  # 1

# =============================
# ex11-2.py XOR 연산은 단일 퍼셉트론으로 불가능한 예제
# =============================

def perceptron(x1, x2):
    w1, w2, b = 1, 1, -1.5
    z = w1 * x1 + w2 * x2 + b
    return 1 if z >= 0 else 0

# XOR 테스트
print(perceptron(0, 0))  # 0
print(perceptron(0, 1))  # 0 (틀림)
print(perceptron(1, 0))  # 0 (틀림)
print(perceptron(1, 1))  # 1

# =============================
# ex11-3.py — 시그모이드 함수 및 뉴런 출력 계산
# =============================
import numpy as np

# 시그모이드 함수
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# 뉴런 출력 계산
def neuron(x, w, b):
    z = np.dot(w, x) + b
    a = sigmoid(z)
    return a

# 테스트
x = np.array([1.0, 0.5])
w = np.array([0.4, 0.7])
b = -0.2
print(neuron(x, w, b))  # 예측값 출력

# =============================
# ex11-4.py — 딥러닝 기본 구조: 역전파 구현 기초(퍼셉트론 구현)
# =============================
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# 데이터 로딩 및 전처리
digits = load_digits()
X = digits.data / 16  # 정규화
y = digits.target % 2  # 짝수/홀수 분류

# 학습용/테스트용 데이터 분할
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 시그모이드 함수 및 파생 함수
def sigmoid(z):
    return 1 / (1 + np.exp(-z))
def sigmoid_deriv(a):
    return a * (1 - a)

# 뉴런 출력 함수
def forward(x, w0, b0, w1, b1, w2, b2):
    z0 = np.dot(x, w0) + b0
    a0 = sigmoid(z0)
    z1 = np.dot(x, w1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(np.c_[a0, a1], w2) + b2
    a2 = sigmoid(z2)
    return a0, a1, a2

# 초기화
n = x_train.shape[0]
d = x_train.shape[1]
w0 = np.zeros(d)
b0 = 0
w1 = np.zeros(d)
b1 = 0
w2 = np.array([0.0, 0.0])
b2 = 0

# 학습 반복
for epoch in range(100):
    grad_w0 = np.zeros(d)
    grad_b0 = 0
    grad_w1 = np.zeros(d)
    grad_b1 = 0
    grad_w2 = np.zeros(2)
    grad_b2 = 0
    loss = 0

    for i in range(n):
        x = x_train[i]
        y_true = y_train[i]

        # 순전파
        a0, a1, a2 = forward(x, w0, b0, w1, b1, w2, b2)
        y_pred = a2[0]

        # 손실 및 그래디언트 계산
        loss += - (y_true * np.log(y_pred + 1e-10) + (1 - y_true) * np.log(1 - y_pred + 1e-10))
        dz2 = y_pred - y_true
        grad_w2[0] += dz2 * a0
        grad_w2[1] += dz2 * a1
        grad_b2 += dz2

        dz0 = dz2 * w2[0] * sigmoid_deriv(a0)
        grad_w0 += dz0 * x
        grad_b0 += dz0

        dz1 = dz2 * w2[1] * sigmoid_deriv(a1)
        grad_w1 += dz1 * x
        grad_b1 += dz1

    # 평균 손실 출력
    print(f"Epoch {epoch+1}, Loss: {loss/n:.4f}")

    # 파라미터 업데이트
    lr = 0.1
    w0 -= lr * grad_w0 / n
    b0 -= lr * grad_b0 / n
    w1 -= lr * grad_w1 / n
    b1 -= lr * grad_b1 / n
    w2 -= lr * grad_w2 / n
    b2 -= lr * grad_b2 / n

# =============================
#ex11-5.py — 예측 및 정확도 확인
# =============================

correct = 0
total = len(x_test)

for i in range(total):
    a0, a1, a2 = forward(x_test[i], w0, b0, w1, b1, w2, b2)
    y_pred = 1 if a2 >= 0.5 else 0
    if y_pred == y_test[i]:
        correct += 1

accuracy = correct / total
print("정확도:", accuracy)
# =============================
