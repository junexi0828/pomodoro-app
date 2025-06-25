import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("=== Tensorflow를 활용한 선형 회귀분석 실습 ===\n")

# 1. 데이터 불러오기
print("1. 데이터 불러오기")
df = pd.read_csv('softdrink.csv')
print(f"데이터 형태: {df.shape}")
print(f"데이터 미리보기:\n{df.head()}\n")

x = tf.constant(df['temp'].values, dtype=tf.float32)
y = tf.constant(df['sales'].values, dtype=tf.float32)

print(f"기온 데이터 (x): {x}")
print(f"매출 데이터 (y): {y}\n")

# 2. 산점도 그리기
print("2. 산점도 그리기")
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.7)
plt.xlabel('Temperature (°C)')
plt.ylabel('Sales')
plt.title('Softdrink Sales vs Temperature')
plt.grid(True, alpha=0.3)
plt.show()

# 3. 초기 모델 수립
print("3. 초기 모델 수립")
a = tf.Variable(20.0)  # 기울기
b = tf.Variable(650.0)  # 절편

def y_hat(x):
    return a * x + b

print(f"초기 파라미터: a = {a.numpy()}, b = {b.numpy()}\n")

# 4. 예측값 시각화
print("4. 초기 예측값 시각화")
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.7, label='실제 데이터')
plt.plot(x, y_hat(x), color='red', linewidth=2, label='초기 예측선')
plt.xlabel('Temperature (°C)')
plt.ylabel('Sales')
plt.title('초기 회귀선 vs 실제 데이터')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# 5. 평균제곱오차(MSE) 계산
print("5. 평균제곱오차(MSE) 계산")
def loss_fn(y, y_pred):
    return tf.reduce_mean(tf.square(y - y_pred))

initial_loss = loss_fn(y, y_hat(x))
print(f"초기 MSE: {initial_loss.numpy():.4f}\n")

# 6. 그래디언트 계산 및 경사하강법
print("6. 경사하강법을 통한 모델 학습")
learning_rate = 0.001
max_steps = 10000

print("학습 시작...")
for step in range(max_steps):
    with tf.GradientTape() as tape:
        pred = y_hat(x)
        loss_val = loss_fn(y, pred)

    # 그래디언트 계산
    da, db = tape.gradient(loss_val, [a, b])

    # 종료 조건
    if tf.abs(da) < 0.05 and tf.abs(db) < 0.05:
        print(f"수렴! {step+1}번째 단계에서 종료")
        break

    # 파라미터 업데이트
    a.assign_add(-learning_rate * da)
    b.assign_add(-learning_rate * db)

    # 진행상황 출력 (1000단계마다)
    if (step + 1) % 1000 == 0:
        print(f"Step {step+1}: a = {a.numpy():.4f}, b = {b.numpy():.4f}, MSE = {loss_val.numpy():.4f}")

final_loss = loss_fn(y, y_hat(x))
print(f"\n최종 결과:")
print(f"a = {a.numpy():.4f}")
print(f"b = {b.numpy():.4f}")
print(f"최종 MSE = {final_loss.numpy():.4f}")
print(f"회귀식: y = {a.numpy():.4f} × x + {b.numpy():.4f}\n")

# 7. 최종 결과 시각화
print("7. 최종 결과 시각화")
plt.figure(figsize=(10, 6))
plt.scatter(x, y, alpha=0.7, label='실제 데이터')
plt.plot(x, y_hat(x), color='green', linewidth=2, label='최종 회귀선')
plt.xlabel('Temperature (°C)')
plt.ylabel('Sales')
plt.title('최종 회귀 결과')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# 8. 예측 성능 평가
print("8. 예측 성능 평가")
y_pred = y_hat(x)
mse = tf.reduce_mean(tf.square(y - y_pred))
rmse = tf.sqrt(mse)
mae = tf.reduce_mean(tf.abs(y - y_pred))

print(f"평균제곱오차 (MSE): {mse.numpy():.4f}")
print(f"평균제곱근오차 (RMSE): {rmse.numpy():.4f}")
print(f"평균절대오차 (MAE): {mae.numpy():.4f}")

# 결정계수 (R²) 계산
ss_res = tf.reduce_sum(tf.square(y - y_pred))
ss_tot = tf.reduce_sum(tf.square(y - tf.reduce_mean(y)))
r_squared = 1 - (ss_res / ss_tot)
print(f"결정계수 (R²): {r_squared.numpy():.4f}")

print("\n=== Tensorflow 회귀분석 실습 완료 ===")