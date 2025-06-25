# --- 필요한 패키지 불러오기 ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import FinanceDataReader as fdr
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# --- 주가 데이터 불러오기 ---
df = fdr.DataReader('KO', '2010')   # 코카콜라 티커, 2010년 이후 데이터
print(df.head())

# --- 종가만 추출하여 시각화 ---
y = df['Close'].values
plt.plot(y)
plt.title('Coca-Cola Stock Price (Close)')
plt.show()

# --- 종가 데이터 정규화 (0~1 범위로) ---
scaler = MinMaxScaler()
y_scaled = scaler.fit_transform(y.reshape(-1, 1))

# --- 시계열 학습 데이터 구조로 변형 ---
window_size = 60
data_length = len(y_scaled) - window_size

x_data = np.zeros((data_length, window_size, 1))
y_data = np.zeros((data_length,))

for i in range(data_length):
    x_data[i] = y_scaled[i:i + window_size].reshape(window_size, 1)
    y_data[i] = y_scaled[i + window_size]

# --- 학습용/테스트용 데이터 분할 ---
# 시계열이므로 순서 유지, shuffle=False
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(
    x_data, y_data, test_size=0.3, shuffle=False
)

# --- LSTM 모델링 ---
model = Sequential()
model.add(LSTM(30, return_sequences=True, input_shape=(window_size, 1)))
model.add(LSTM(30))
model.add(Dense(1, activation=None))  # 회귀이므로 활성화 함수 없음

# --- 모델 컴파일 및 학습 ---
model.compile(optimizer='adam', loss='mse')
model.fit(x_train, y_train, epochs=20, batch_size=10)

# --- 예측 및 결과 시각화 ---
pred = model.predict(x_test)
plt.plot(y_test, label='Actual')
plt.plot(pred, label='Prediction')
plt.title('LSTM Predicted vs Actual Stock Price')
plt.legend()
plt.show()