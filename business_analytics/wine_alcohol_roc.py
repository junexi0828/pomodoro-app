# wine_alcohol_roc.py

import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# 와인 데이터셋 로드
wine = load_wine()
df = pd.DataFrame(wine.data, columns=wine.feature_names)
df['target'] = wine.target

"""이번에는 와인 데이터셋에서 등급이 0과 1인 데이터만을 남기고
등급이 2인 데이터는 제거한 데이터 셋을 준비하시오"""

# 클래스 0과 1만 선택
#d['target'] = dataset.target
df = df[df['target'].isin([0, 1])]

# alcoholed malic acid 계산
def calculate_alcoholed_malic_acid(alcohol, malic_acid):
    return np.sqrt(alcohol * malic_acid)

#𝑎𝑙𝑐𝑜ℎ𝑜𝑙𝑒𝑑 𝑚𝑎𝑙𝑖𝑐 𝑎𝑐𝑖𝑑 = √𝑎𝑙𝑐𝑜ℎ𝑜𝑙 ∙ (𝑚𝑎𝑙𝑖𝑐 𝑎𝑐𝑖𝑑)

df['alcoholed_malic_acid'] = calculate_alcoholed_malic_acid(
    df['alcohol'], df['malic_acid']
)

# ROC 커브를 위한 데이터 준비
y_true = df['target']
scores = df['alcoholed_malic_acid']

"""" alcoholed malic acid라는 지표를 아래의 식을 통해 계산하여
활용하자. alcoholed malic acid 값을 9.0 ~ 24.0까지 0.1씩 증가시키면서 등급이 1인 와인을 찾아내는
경우의 ROC 곡선을 그려내고, 와인의 등급을 0과 1로 분류할 때 가장 높은 성능을 보이는 alcoholed
malic acid의 기준값(threshold)을 제시하시오"""

# 임계값 범위 설정 (9.0 ~ 24.0, 0.1 간격으로 증가)
thresholds = np.arange(9.0, 24.1, 0.1)

"""
while은 필요없지않나? -> 그냥 범위 지정
# --- 예측값 생성 (몸무게가 threshold 이상이면 1, 아니면 0) ---
y_pred = []
for w in weight:
    if w >= threshold:
        y_pred.append(1)
    else:
        y_pred.append(0)
"""

# ROC 커브 계산
fpr, tpr, roc_thresholds = roc_curve(y_true, scores)
roc_auc = auc(fpr, tpr)

# ROC 커브 그리기 (auc 추가)
plt.figure(figsize=(10, 6))
plt.plot(fpr, tpr, color='orange', lw=2,
         label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='yellow', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc="lower right")

# 최적의 임계값 찾기
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = roc_thresholds[optimal_idx]

print(f"최적의 alcoholed malic acid 임계값: {optimal_threshold:.2f}")

plt.savefig('wine_roc_curve.png')
plt.show()

# 등급이 1인 와인을 찾아내는, 표시를 해주는 함수? 그냥 1까지 나타내고 끊으면?

