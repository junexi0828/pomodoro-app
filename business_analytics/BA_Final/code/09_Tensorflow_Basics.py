# -------------------------------
# [1] TensorFlow 기본 사용
# -------------------------------
import tensorflow as tf

# 정수형 텐서 정의
a = tf.constant(1)
print(a)  # 출력: tf.Tensor(1, shape=(), dtype=int32)

# 실수형 텐서 정의
b = tf.constant(1.0)
print(b)  # 출력: tf.Tensor(1.0, shape=(), dtype=float32)

# -------------------------------
# [2] 행렬 정의 및 연산
# -------------------------------
a = tf.constant([[1, 2], [3, 4]])
b = tf.constant([[5, 6], [7, 8]])

# 행렬의 shape 확인
print("a.shape:", a.shape)
print("b.shape:", b.shape)

# 행렬 덧셈
print("a + b =\n", tf.add(a, b))

# 행렬 곱셈
print("a @ b =\n", tf.matmul(a, b))

# -------------------------------
# [3] 단위행렬과 역행렬
# -------------------------------
i = tf.eye(2)  # 단위행렬
print("Identity:\n", i)
print("a * I =\n", tf.matmul(a, i))

a_inv = tf.linalg.inv(tf.cast(a, dtype=tf.float32))  # 역행렬은 float32 필요
print("Inverse of a:\n", a_inv)
print("a * a_inv =\n", tf.matmul(tf.cast(a, tf.float32), a_inv))

# -------------------------------
# [4] 회귀분석 예제 (softdrink.csv 사용)
# -------------------------------
import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기
df = pd.read_csv('softdrink.csv')
x = tf.constant(df['temp'].values, dtype=tf.float32)
y = tf.constant(df['sales'].values, dtype=tf.float32)

# 산점도 출력
plt.scatter(x, y)
plt.xlabel('Temperature')
plt.ylabel('Sales')
plt.title('Original Data')
plt.show()

# -------------------------------
# [5] 초기 모델 설정 및 예측 함수 정의
# -------------------------------
# 초기 파라미터 설정
a = tf.Variable(20.0)
b = tf.Variable(650.0)

# 예측 함수
def y_hat(x): return a * x + b

# 예측값 시각화
plt.scatter(x, y, label='Actual')
plt.plot(x, y_hat(x), color='red', label='Prediction')
plt.legend()
plt.title('Initial Model')
plt.show()

# -------------------------------
# [6] MSE 오차 함수 정의
# -------------------------------
def loss_fn(y, y_pred):
    return tf.reduce_mean(tf.square(y - y_pred))

# 초기 MSE 계산
print("Initial MSE:", loss_fn(y, y_hat(x)).numpy())

# -------------------------------
# [7] Gradient 계산
# -------------------------------
with tf.GradientTape() as tape:
    pred = y_hat(x)
    loss = loss_fn(y, pred)
da, db = tape.gradient(loss, [a, b])
print("Gradient da:", da.numpy())
print("Gradient db:", db.numpy())

# -------------------------------
# [8] 경사하강법 최적화 (반복)
# -------------------------------
a = tf.Variable(20.0)
b = tf.Variable(650.0)
learning_rate = 0.001

while True:
    with tf.GradientTape() as tape:
        pred = y_hat(x)
        loss = loss_fn(y, pred)
    da, db = tape.gradient(loss, [a, b])

    # 파라미터 업데이트
    a.assign_sub(learning_rate * da)
    b.assign_sub(learning_rate * db)

    # 종료 조건
    if tf.abs(da) < 0.05 and tf.abs(db) < 0.05:
        break

print("최적화 종료 후 a:", a.numpy(), "b:", b.numpy())
print("최종 MSE:", loss_fn(y, y_hat(x)).numpy())

# 최종 결과 시각화
plt.scatter(x, y, label='Actual')
plt.plot(x, y_hat(x), color='green', label='Final Model')
plt.title('Final Fitted Model')
plt.legend()
plt.show()