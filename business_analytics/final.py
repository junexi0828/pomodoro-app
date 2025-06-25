import numpy as np

# 시뮬레이션 설정
n = 10000

# 온도 생성 (0°C ~ 30°C, uniform 분포)
temp = np.random.uniform(0, 30, n)

# 날씨 생성 (4/5 확률로 맑음(w=0), 1/5 확률로 흐림(w=1))
weather = np.random.binomial(1, 0.2, n)

# 수요 계산
demand = np.zeros(n, dtype='float32')

for i in range(n):
    if weather[i] == 0:  # 맑은 날 (w=0)
        mu_d = 100 + 3 * temp[i]
        sigma_d = 0.5 * mu_d
    else:  # 흐린 날 (w=1)
        mu_d = 30 + 4 * temp[i]
        sigma_d = 0.6 * mu_d

    # 정규분포에서 수요 생성
    d = np.random.normal(mu_d, sigma_d)

    # 수요가 음수면 0으로 처리
    if d < 0:
        d = 0

    demand[i] = d

# 결과 출력
print("=== 냉면 수요 시뮬레이션 결과 ===")
print(f"시뮬레이션 횟수: {n:,}회")
print(f"평균 온도: {np.mean(temp):.1f}°C")
print(f"맑은 날 비율: {(weather == 0).sum() / n * 100:.1f}%")
print(f"흐린 날 비율: {(weather == 1).sum() / n * 100:.1f}%")
print(f"전체 평균 수요: {np.mean(demand):.1f}그릇")

# 날씨별 평균 수요
sunny_demand = demand[weather == 0]
cloudy_demand = demand[weather == 1]

print(f"맑은 날 평균 수요: {np.mean(sunny_demand):.1f}그릇")
print(f"흐린 날 평균 수요: {np.mean(cloudy_demand):.1f}그릇")

print("\n[수요 공식]")
print("맑은 날 (w=0): μd = 100 + 3t, σd = 0.5μd")
print("흐린 날 (w=1): μd = 30 + 4t, σd = 0.6μd")