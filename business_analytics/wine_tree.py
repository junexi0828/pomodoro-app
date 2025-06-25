# wine_tree.py

import pandas as pd
import numpy as np
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

# 와인 데이터셋 로드
wine = load_wine()
X = pd.DataFrame(wine.data, columns=wine.feature_names)[['alcohol', 'malic_acid']]
y = wine.target

"""이때 데이터 셋을 sklearn.model_selection 모듈의 train_test_split을 사용해
8:2의 비율로 train:test로 분할하되, 난수(random_state)로 2222 값을 적용"""

"""데이터셋 분리 (test_size=0.2, random_state 고정)
x_train, x_test, y_train, y_test = train_test_split(feature, target, test_size=0.2, random_state=2222)"""

# 데이터 8:2로 분할 (random_state=2222)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2222)

"""matplotlib.pyplot 모듈의
plot_tree를 사용하여 ‘depth=3’인 decision tree"""

# Decision Tree 모델 생성 및 학습 (max_depth=3)
dt_model = DecisionTreeClassifier(max_depth=3, random_state=2222)
dt_model.fit(X_train, y_train)

# 테스트 데이터로 예측
y_pred = dt_model.predict(X_test)

"""test
데이터 셋을 적용한 confusion matrix와 classification_report를 출력"""

# Confusion Matrix 출력
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Classification Report 출력
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

"""matplotlib.pyplot 모듈의
plot_tree를 사용하여 ‘depth=3’인 decision tree"""

# Decision Tree 시각화

# 그래프 크기 설정 와인등급 0~2
plt.figure(figsize=(24, 10))
plot_tree(dt_model,
          feature_names=['alcohol', 'malic_acid'],
          class_names=['0', '1', '2'],
          max_depth=3,
          filled=True,
          rounded=True,fontsize=6)
plt.savefig('wine_decision_tree.png')
plt.show()

"""max_depth=3,
          filled=True,
          rounded=True,
          fontsize=6)"""