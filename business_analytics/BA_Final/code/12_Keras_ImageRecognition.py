# ==========================================
# [1단계] 필요한 라이브러리 불러오기
# ==========================================
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# [2단계] 손글씨 이미지 분류 (홀/짝 분류 예제)
# ==========================================

# 모델 생성
model = keras.Sequential([
    layers.Dense(2, activation='sigmoid', input_shape=(64,)),  # 은닉층
    layers.Dense(1, activation='sigmoid')  # 출력층
])

# 모델 컴파일 (손실함수 및 최적화 알고리즘 설정)
model.compile(loss='binary_crossentropy', optimizer='SGD', metrics=['accuracy'])

# 학습 데이터: x_train, y_train이 있다고 가정
# model.fit(x_train, y_train, epochs=2000)  # 실제 학습시 사용

# ==========================================
# [3단계] Fashion MNIST 데이터 불러오기
# ==========================================
fashion_mnist = keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

print("학습 데이터 모양:", train_images.shape)  # (60000, 28, 28)
print("테스트 데이터 모양:", test_images.shape)  # (10000, 28, 28)

print("0번 이미지 배열:")
print(train_images[0])  # 실제 이미지 배열 값 출력

# 이미지 출력
plt.imshow(train_images[0], cmap='gray')
plt.title("Label: {}".format(train_labels[0]))
plt.show()

# ==========================================
# [4단계] 데이터 전처리 (0~1 사이 정규화)
# ==========================================
train_images = train_images / 255.0
test_images = test_images / 255.0

# 입력을 1차원 벡터로 변환
train_images = train_images.reshape((60000, 784))
test_images = test_images.reshape((10000, 784))

# ==========================================
# [5단계] 신경망 모델 정의 (이미지 분류용)
# ==========================================
model = keras.Sequential([
    layers.Dense(100, activation='relu', input_shape=(784,)),  # 은닉층
    layers.Dense(10, activation='softmax')  # 출력층 (10 클래스)
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 모델 학습
model.fit(train_images, train_labels, epochs=10)

# ==========================================
# [6단계] 예측 및 결과 시각화
# ==========================================
predictions = model.predict(test_images)

# 0번 이미지 예측 결과 출력
print("예측 확률값:", predictions[0])
print("예측한 클래스:", np.argmax(predictions[0]))
print("실제 라벨:", test_labels[0])

# 이미지 출력
plt.imshow(test_images[0].reshape(28, 28), cmap='gray')
plt.title(f"예측: {np.argmax(predictions[0])}, 실제: {test_labels[0]}")
plt.show()

# ==========================================
# [7단계] 확률 막대 그래프로 출력
# ==========================================
plt.bar(range(10), predictions[0])
plt.xlabel('클래스')
plt.ylabel('예측 확률')
plt.title('클래스별 예측 확률 분포')
plt.show()

# ==========================================
# [8단계] 성능 평가
# ==========================================
predicted_labels = np.argmax(predictions, axis=1)

from sklearn.metrics import classification_report, accuracy_score
print("정확도:", accuracy_score(test_labels, predicted_labels))
print("분류 리포트:\n", classification_report(test_labels, predicted_labels))