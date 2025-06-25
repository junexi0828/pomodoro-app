import numpy as np

# TensorFlow 임포트 (에러 방지를 위해 try-except 사용)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense
    TF_AVAILABLE = True
    print("TensorFlow를 사용하여 신경망 모델을 학습합니다.")
except ImportError:
    print("TensorFlow가 설치되지 않았습니다. 기본 통계 방법을 사용합니다.")
    TF_AVAILABLE = False

# 시뮬레이션 횟수
n = 100000

print("=== 냉면 수량 결정 시뮬레이션 ===")
print(f"시뮬레이션 횟수: {n:,}")

# 온도 t는 0°C에서 30°C까지 uniform 분포로 변동
temp = np.random.uniform(0, 30, n)

# 날씨는 4/5의 확률로 맑고(w=0), 1/5의 확률로 흐림(w=1)
weather = np.random.binomial(1, 0.2, n)  # 0.2확률로 흐림(w=1), 0.8확률로 맑음(w=0)

print(f"온도 범위: 0°C ~ 30°C (uniform 분포)")
print(f"날씨 확률: 맑음 80%, 흐림 20%")

# 수요 계산 (새로운 공식 적용)
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

print(f"\n=== 비용 정보 ===")
print(f"판매가격: {p:,}원")
print(f"생산비용: {c:,}원")
print(f"품절비용: {Cu:,}원")
print(f"재고비용: {Co:,}원")

# 수요 분석
sunny_indices = weather == 0
cloudy_indices = weather == 1

print(f"\n=== 수요 분석 ===")
print(f"전체 평균 수요: {np.mean(demand):.2f}")
print(f"맑은 날 평균 수요: {np.mean(demand[sunny_indices]):.2f} (샘플 수: {np.sum(sunny_indices):,})")
print(f"흐린 날 평균 수요: {np.mean(demand[cloudy_indices]):.2f} (샘플 수: {np.sum(cloudy_indices):,})")

if TF_AVAILABLE:
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
    model = Sequential([
        Dense(2, input_shape=(2,), activation='sigmoid'),
        Dense(1, activation=None),
    ])

    # 모델 컴파일
    model.compile(optimizer='adam', loss=inventory_loss)

    # 모델 학습 (기존 예제와 동일한 epochs=20)
    print("\n=== 신경망 모델 학습 ===")
    print("모델 학습 중...")
    history = model.fit(x_train, demand_train, epochs=20, verbose=1, batch_size=1000)

    # 테스트 데이터 생성
    n_test = 100000
    temp_new = np.random.uniform(0, 30, n_test)
    weather_new = np.random.binomial(1, 0.2, n_test)  # 4/5 확률로 맑음, 1/5 확률로 흐림

    # 테스트 데이터 전처리
    x_test = np.zeros((n_test, 2), dtype='float32')
    x_test[:, 0] = (temp_new - min(temp)) / (max(temp) - min(temp))
    x_test[:, 1] = weather_new

    # 예측
    print("\n예측 중...")
    pred = model.predict(x_test, verbose=0)
    Q_prop = pred * (max(demand) - min(demand)) + min(demand)

    # 성능 평가
    sum_profit_nn = 0
    sum_Q_nn = 0

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

        sum_Q_nn += Q
        sum_profit_nn += profit

    # 신경망 결과
    avg_Q_nn = sum_Q_nn / n_test
    avg_profit_nn = sum_profit_nn / n_test

    print(f"\n=== 신경망 모델 결과 ===")
    print(f"평균 생산량: {avg_Q_nn:.2f}")
    print(f"평균 기대이익: {avg_profit_nn:.2f}원")


# 비교를 위한 단순 평균 방법
sum_profit_simple = 0
sum_Q_simple = 0

print("\n=== 단순 평균 방법 (기준선) ===")
for i in range(10000):  # 비교를 위해 1만 개 샘플만 사용
    temp_sample = np.random.uniform(0, 30)
    weather_sample = np.random.binomial(1, 0.2)

    # 단순히 평균 수요로 생산량 결정
    if weather_sample == 0:  # 맑은 날
        Q = 100 + 3 * temp_sample
        mu_d = 100 + 3 * temp_sample
        sigma_d = 0.5 * mu_d
    else:  # 흐린 날
        Q = 30 + 4 * temp_sample
        mu_d = 30 + 4 * temp_sample
        sigma_d = 0.6 * mu_d

    d = np.random.normal(mu_d, sigma_d)
    if d < 0:
        d = 0

    # 이익 계산
    profit = -c * Q
    if d <= Q:
        profit += p * d + s * (Q - d)
    else:
        profit += p * Q

    sum_Q_simple += Q
    sum_profit_simple += profit

avg_Q_simple = sum_Q_simple / 10000
avg_profit_simple = sum_profit_simple / 10000

print(f"평균 생산량: {avg_Q_simple:.2f}")
print(f"평균 기대이익: {avg_profit_simple:.2f}원")

# 결과 비교
print(f"\n=== 결과 비교 ===")
print(f"단순 평균 방법: 생산량 {avg_Q_simple:.2f}, 이익 {avg_profit_simple:.2f}원")
if TF_AVAILABLE:
    print(f"신경망 방법:   생산량 {avg_Q_nn:.2f}, 이익 {avg_profit_nn:.2f}원")
    improvement = avg_profit_nn - avg_profit_simple
    improvement_pct = (improvement / avg_profit_simple) * 100
    print(f"이익 개선: {improvement:.2f}원 ({improvement_pct:.2f}%)")
else:
    print("TensorFlow를 설치하면 신경망 방법과 비교할 수 있습니다.")

# 조건별 이론적 수요 분석
print(f"\n=== 조건별 이론적 수요 분석 ===")
temp_samples = [0, 15, 30]  # 최저, 중간, 최고 온도

for t in temp_samples:
    print(f"\n온도 {t}°C에서:")

    # 맑은 날 수요
    mu_sunny = 100 + 3 * t
    sigma_sunny = 0.5 * mu_sunny
    print(f"  맑은 날 (80% 확률): 평균 {mu_sunny:.0f}, 표준편차 {sigma_sunny:.0f}")

    # 흐린 날 수요
    mu_cloudy = 30 + 4 * t
    sigma_cloudy = 0.6 * mu_cloudy
    print(f"  흐린 날 (20% 확률): 평균 {mu_cloudy:.0f}, 표준편차 {sigma_cloudy:.0f}")

    # 가중 평균 수요
    weighted_avg = 0.8 * mu_sunny + 0.2 * mu_cloudy
    print(f"  가중 평균 수요: {weighted_avg:.0f}")

print(f"\n프로그램 실행 완료!")
print(f"총 시뮬레이션 데이터: {n:,}개")
if TF_AVAILABLE:
    print(f"신경망 테스트 데이터: {n_test:,}개")
    print(f"신경망 학습 에포크: 20")
print(f"단순 방법 테스트 데이터: 10,000개")