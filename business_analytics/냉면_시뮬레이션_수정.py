import numpy as np

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

print("=== 기본 정보 ===")
print(f"시뮬레이션 횟수: {n:,}")
print(f"온도 범위: 0°C ~ 30°C (uniform 분포)")
print(f"날씨 확률: 맑음 80%, 흐림 20%")
print(f"판매가격: {p:,}원")
print(f"생산비용: {c:,}원")
print(f"품절비용: {Cu:,}원")
print(f"재고비용: {Co:,}원")

# 평균 수요 분석
sunny_demand = []
cloudy_demand = []
for i in range(n):
    if weather[i] == 0:
        sunny_demand.append(demand[i])
    else:
        cloudy_demand.append(demand[i])

print(f"\n=== 수요 분석 ===")
print(f"전체 평균 수요: {np.mean(demand):.2f}")
print(f"맑은 날 평균 수요: {np.mean(sunny_demand):.2f} (샘플 수: {len(sunny_demand):,})")
print(f"흐린 날 평균 수요: {np.mean(cloudy_demand):.2f} (샘플 수: {len(cloudy_demand):,})")

# 단순 평균 기반 생산량 결정
sum_profit_simple = 0
sum_Q_simple = 0

print("\n=== 단순 평균 기반 생산량 결정 ===")
for i in range(n):
    # 단순히 평균 수요로 생산량 결정
    if weather[i] == 0:  # 맑은 날
        Q = 100 + 3 * temp[i]
    else:  # 흐린 날
        Q = 30 + 4 * temp[i]

    d = demand[i]

    # 이익 계산
    profit = -c * Q
    if d <= Q:
        profit += p * d + s * (Q - d)
    else:
        profit += p * Q

    sum_Q_simple += Q
    sum_profit_simple += profit

avg_Q_simple = sum_Q_simple / n
avg_profit_simple = sum_profit_simple / n

print(f"평균 생산량: {avg_Q_simple:.2f}")
print(f"평균 기대이익: {avg_profit_simple:.2f}원")

# 최적 생산량 결정 (뉴스벤더 모델 적용)
print("\n=== 최적 생산량 결정 (뉴스벤더 모델) ===")

# 임계확률 계산
critical_ratio = Cu / (Cu + Co)
print(f"임계확률: {critical_ratio:.3f}")

sum_profit_optimal = 0
sum_Q_optimal = 0

for i in range(n):
    # 날씨와 온도에 따른 수요 분포 계산
    if weather[i] == 0:  # 맑은 날
        mu_d = 100 + 3 * temp[i]
        sigma_d = 0.5 * mu_d
    else:  # 흐린 날
        mu_d = 30 + 4 * temp[i]
        sigma_d = 0.6 * mu_d

    # 정규분포의 역함수를 이용한 최적 생산량 계산
    from scipy.stats import norm
    Q_optimal = norm.ppf(critical_ratio, mu_d, sigma_d)

    if Q_optimal < 0:
        Q_optimal = 0

    d = demand[i]

    # 이익 계산
    profit = -c * Q_optimal
    if d <= Q_optimal:
        profit += p * d + s * (Q_optimal - d)
    else:
        profit += p * Q_optimal

    sum_Q_optimal += Q_optimal
    sum_profit_optimal += profit

avg_Q_optimal = sum_Q_optimal / n
avg_profit_optimal = sum_profit_optimal / n

print(f"평균 생산량: {avg_Q_optimal:.2f}")
print(f"평균 기대이익: {avg_profit_optimal:.2f}원")

# 비교 분석
print(f"\n=== 비교 분석 ===")
print(f"단순 평균 방법 - 생산량: {avg_Q_simple:.2f}, 이익: {avg_profit_simple:.2f}원")
print(f"최적화 방법   - 생산량: {avg_Q_optimal:.2f}, 이익: {avg_profit_optimal:.2f}원")
print(f"이익 개선: {avg_profit_optimal - avg_profit_simple:.2f}원 ({((avg_profit_optimal - avg_profit_simple) / avg_profit_simple * 100):.2f}%)")

# 온도별 수요 분석
temp_ranges = [(0, 10), (10, 20), (20, 30)]
print(f"\n=== 온도별 수요 분석 ===")

for temp_min, temp_max in temp_ranges:
    temp_mask = (temp >= temp_min) & (temp < temp_max)
    temp_demand = demand[temp_mask]
    temp_weather = weather[temp_mask]

    sunny_temp_demand = temp_demand[temp_weather == 0]
    cloudy_temp_demand = temp_demand[temp_weather == 1]

    print(f"온도 {temp_min}°C-{temp_max}°C:")
    print(f"  전체 평균 수요: {np.mean(temp_demand):.2f}")
    if len(sunny_temp_demand) > 0:
        print(f"  맑은 날 평균 수요: {np.mean(sunny_temp_demand):.2f}")
    if len(cloudy_temp_demand) > 0:
        print(f"  흐린 날 평균 수요: {np.mean(cloudy_temp_demand):.2f}")