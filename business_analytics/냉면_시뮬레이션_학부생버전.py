# 냉면 수량 결정 시뮬레이션 - 학부생 과제
# 이름: 홍길동, 학번: 2024000001

import numpy as np
import random
import math

print("냉면집 수량 결정 시뮬레이션 프로그램")
print("=" * 40)

# 시뮬레이션 설정
n = 5000  # 시뮬레이션 횟수 (너무 많으면 컴퓨터가 느려질까봐...)
print("시뮬레이션 횟수:", n)

# 가격 정보
selling_price = 8000  # 판매가격
production_cost = 2000  # 생산비용
# 폐기비용은 0이라고 교수님이 말씀하셨음

print("판매가격:", selling_price, "원")
print("생산비용:", production_cost, "원")

# 시뮬레이션 시작
print("\n시뮬레이션 시작...")

# 데이터 저장할 리스트들
temp_list = []
weather_list = []
demand_list = []

# 온도와 날씨 데이터 생성
for i in range(n):
    # 온도는 0도에서 30도 사이
    temp = random.uniform(0, 30)
    temp_list.append(temp)

    # 날씨: 맑음이 80%, 흐림이 20%
    if random.random() < 0.8:
        weather = 0  # 맑음
    else:
        weather = 1  # 흐림
    weather_list.append(weather)

print("온도, 날씨 데이터 생성 완료")

# 수요 계산
for i in range(n):
    temp = temp_list[i]
    weather = weather_list[i]

    if weather == 0:  # 맑은 날
        average_demand = 100 + 3 * temp
        std_dev = 0.5 * average_demand
    else:  # 흐린 날
        average_demand = 30 + 4 * temp
        std_dev = 0.6 * average_demand

    # 정규분포에서 수요 생성
    demand = np.random.normal(average_demand, std_dev)

    # 수요가 음수면 0으로 처리
    if demand < 0:
        demand = 0

    demand_list.append(demand)

print("수요 데이터 생성 완료")

# 수요 분석
sunny_demands = []
cloudy_demands = []

for i in range(n):
    if weather_list[i] == 0:
        sunny_demands.append(demand_list[i])
    else:
        cloudy_demands.append(demand_list[i])

print("\n=== 수요 분석 결과 ===")
print("전체 평균 수요:", round(sum(demand_list)/len(demand_list), 1), "그릇")
print("맑은 날 평균 수요:", round(sum(sunny_demands)/len(sunny_demands), 1), "그릇")
print("흐린 날 평균 수요:", round(sum(cloudy_demands)/len(cloudy_demands), 1), "그릇")

# 방법 1: 평균 수요로 생산
print("\n=== 방법 1: 평균 수요 생산 ===")

total_profit_1 = 0
total_production_1 = 0

for i in range(n):
    temp = temp_list[i]
    weather = weather_list[i]
    actual_demand = demand_list[i]

    # 생산량 결정
    if weather == 0:  # 맑은 날
        production = 100 + 3 * temp
    else:  # 흐린 날
        production = 30 + 4 * temp

    # 이익 계산
    cost = production_cost * production  # 생산비용

    if actual_demand <= production:
        revenue = selling_price * actual_demand  # 판매수익
    else:
        revenue = selling_price * production  # 품절시

    profit = revenue - cost

    total_profit_1 += profit
    total_production_1 += production

avg_production_1 = total_production_1 / n
avg_profit_1 = total_profit_1 / n

print("평균 생산량:", round(avg_production_1, 1))
print("평균 이익:", round(avg_profit_1, 0), "원")

# 방법 2: 좀 더 많이 생산해보기
print("\n=== 방법 2: 좀 더 많이 생산 ===")

total_profit_2 = 0
total_production_2 = 0

for i in range(n):
    temp = temp_list[i]
    weather = weather_list[i]
    actual_demand = demand_list[i]

    # 생산량을 15% 더 생산 (20%는 너무 많을것 같아서...)
    if weather == 0:
        production = (100 + 3 * temp) * 1.15
    else:
        production = (30 + 4 * temp) * 1.15

    # 이익 계산
    cost = production_cost * production

    if actual_demand <= production:
        revenue = selling_price * actual_demand
    else:
        revenue = selling_price * production

    profit = revenue - cost

    total_profit_2 += profit
    total_production_2 += production

avg_production_2 = total_production_2 / n
avg_profit_2 = total_profit_2 / n

print("평균 생산량:", round(avg_production_2, 1))
print("평균 이익:", round(avg_profit_2, 0), "원")

# 방법 3: 좀 덜 생산해보기
print("\n=== 방법 3: 좀 덜 생산 ===")

total_profit_3 = 0

for i in range(n):
    temp = temp_list[i]
    weather = weather_list[i]
    actual_demand = demand_list[i]

    # 생산량을 25% 덜 생산
    if weather == 0:
        production = (100 + 3 * temp) * 0.75
    else:
        production = (30 + 4 * temp) * 0.75

    # 이익 계산
    cost = production_cost * production

    if actual_demand <= production:
        revenue = selling_price * actual_demand
    else:
        revenue = selling_price * production

    profit = revenue - cost

    total_profit_3 += profit

avg_profit_3 = total_profit_3 / n

print("평균 이익:", round(avg_profit_3, 0), "원")

# 결과 비교
print("\n" + "=" * 40)
print("결과 비교")
print("=" * 40)

print("방법 1 (평균 생산):", round(avg_profit_1, 0), "원")
print("방법 2 (많이 생산):", round(avg_profit_2, 0), "원")
print("방법 3 (적게 생산):", round(avg_profit_3, 0), "원")

# 어떤 방법이 제일 좋은지 확인
profits = [avg_profit_1, avg_profit_2, avg_profit_3]
best_method = profits.index(max(profits)) + 1

print(f"\n가장 좋은 방법: 방법 {best_method}")

# 온도별 분석 (시간이 없어서 간단하게만...)
print("\n=== 온도별 분석 ===")

low_temp_demands = []  # 0-15도
high_temp_demands = []  # 15-30도

for i in range(n):
    if temp_list[i] < 15:
        low_temp_demands.append(demand_list[i])
    else:
        high_temp_demands.append(demand_list[i])

if len(low_temp_demands) > 0:
    print("낮은 온도(0-15도) 평균 수요:", round(sum(low_temp_demands)/len(low_temp_demands), 1))

if len(high_temp_demands) > 0:
    print("높은 온도(15-30도) 평균 수요:", round(sum(high_temp_demands)/len(high_temp_demands), 1))

print("\n프로그램 완료!")

# 참고: 교수님이 말씀하신 공식들
print("\n[참고 공식]")
print("맑은 날: 평균수요 = 100 + 3×온도")
print("흐린 날: 평균수요 = 30 + 4×온도")
print("예) 온도 20도, 맑은 날 → 100 + 3×20 =", 100 + 3*20, "그릇")