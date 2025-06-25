import numpy as np
import tensorflow as tf

# 시뮬레이션 횟수
n = 100000

# 온도 t는 0°C에서 30°C까지 uniform 분포로 변동
temp = np.random.uniform(0, 30, n)

# 날씨는 4/5의 확률로 맑고(w=0), 1/5의 확률로 흐림(w=1)
weather = np.random.binomial(1, 0.2, n)  # 0.2확률로 흐림(w=1), 0.8확률로 맑음(w=0)

# 수요 계산
demand = np.zeros(n, dtype='float32')
for i in range(n):
    # 새로운 평균 수요 공식 적용
    if weather[i] == 0:  # 맑은 날 (w=0)
        mu_d = 100 + 3 * temp[i]
        sigma_d = 0.5 * mu_d
    else:  # 흐린 날 (w=1)
        mu_d = 30 + 4 * temp[i]
        sigma_d = 0.6 * mu_d

    d = np.random.normal(mu_d, sigma_d)
    if d < 0:
        d = 0
    demand[i] = d

# 비용 및 가격 설정 (기존 예제와 동일)
p = 8000  # 판매가격
c = 2000  # 생산비용
s = 0     # 폐기비용
Cu = p - c  # 기회비용 (품절비용)
Co = c - s  # 보유비용 (과잉재고비용)

# 재고 손실 함수 정의
def inventory_loss(demand_true, q):
    stock = q - demand_true
    is_understock = stock < 0
    inventory_error = tf.abs(stock)
    understock_loss = Cu * inventory_error
    overstock_loss = Co * inventory_error
    return tf.where(is_understock, understock_loss, overstock_loss)

# 학습 데이터 준비
x_train = np.zeros((n, 2), dtype='float32')
x_train[:, 0] = (temp - min(temp)) / (max(temp) - min(temp))  # 온도 정규화
x_train[:, 1] = weather  # 날씨 (0: 맑음, 1: 흐림)
demand_train = (demand - min(demand)) / (max(demand) - min(demand))  # 수요 정규화

# 신경망 모델 구성 (기존 예제와 동일한 구조)
model = tf.keras.Sequential([
    tf.keras.layers.Dense(2, input_shape=(2,), activation='sigmoid'),
    tf.keras.layers.Dense(1, activation=None),
])

# 모델 컴파일
model.compile(optimizer='adam', loss=inventory_loss)

# 모델 학습 (기존 예제와 동일한 epochs=20)
print("모델 학습 중...")
model.fit(x_train, demand_train, epochs=20, verbose=1)

# 테스트 데이터 생성
n_test = 100000
temp_new = np.random.uniform(0, 30, n_test)
weather_new = np.random.binomial(1, 0.2, n_test)  # 4/5 확률로 맑음, 1/5 확률로 흐림

# 테스트 데이터 전처리
x_test = np.zeros((n_test, 2), dtype='float32')
x_test[:, 0] = (temp_new - min(temp)) / (max(temp) - min(temp))
x_test[:, 1] = weather_new

# 예측
print("예측 중...")
pred = model.predict(x_test)
Q_prop = pred * (max(demand) - min(demand)) + min(demand)

# 성능 평가
sum_profit = 0
sum_Q = 0

print("성능 평가 중...")
for i in range(n_test):
    # 실제 수요 계산
    if weather_new[i] == 0:  # 맑은 날
        mu_d = 100 + 3 * temp_new[i]
        sigma_d = 0.5 * mu_d
    else:  # 흐린 날
        mu_d = 30 + 4 * temp_new[i]
        sigma_d = 0.6 * mu_d

    d = np.random.normal(mu_d, sigma_d)
    if d < 0:
        d = 0

    Q = Q_prop[i][0]  # 예측된 생산량

    # 이익 계산
    profit = -c * Q
    if d <= Q:
        profit += p * d + s * (Q - d)
    else:
        profit += p * Q

    sum_Q += Q
    sum_profit += profit

# 결과 출력
avg_Q = sum_Q / n_test
avg_profit = sum_profit / n_test

print(f"\n=== 시뮬레이션 결과 ===")
print(f"평균 생산량: {avg_Q:.2f}")
print(f"평균 기대이익: {avg_profit:.2f}원")

# 날씨별 평균 수요 출력
sunny_demands = []
cloudy_demands = []

for i in range(1000):  # 샘플로 1000개만
    temp_sample = np.random.uniform(0, 30)

    # 맑은 날 수요
    mu_sunny = 100 + 3 * temp_sample
    sunny_demands.append(mu_sunny)

    # 흐린 날 수요
    mu_cloudy = 30 + 4 * temp_sample
    cloudy_demands.append(mu_cloudy)

print(f"\n=== 조건별 평균 수요 분석 ===")
print(f"맑은 날 평균 수요: {np.mean(sunny_demands):.2f}")
print(f"흐린 날 평균 수요: {np.mean(cloudy_demands):.2f}")
print(f"전체 평균 수요: {np.mean(demand):.2f}")