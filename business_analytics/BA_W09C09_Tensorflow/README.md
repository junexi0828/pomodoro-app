# W09C09 Tensorflow 실습

이 폴더는 W09C09 Tensorflow 장의 실습을 완벽히 재현한 코드들을 포함합니다.

## 📁 폴더 구조

```
BA_W09C09_Tensorflow/
├── softdrink.csv              # 예제 데이터 (기온-매출 데이터)
├── tensor_operations.py       # Tensor 기본 연산 실습 코드
├── regression_tf.py           # 회귀분석 전체 실습 코드
├── requirements.txt           # 필요한 패키지 목록
└── README.md                  # 이 파일
```

## 🚀 설치 및 실행

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Tensorflow 기본 연산 실습
```bash
python tensor_operations.py
```

### 3. 회귀분석 실습
```bash
python regression_tf.py
```

## 📊 실습 내용

### Part 1: Tensorflow 기본 연산 (tensor_operations.py)
- Tensor 생성 및 데이터 타입 이해
- 행렬 생성 및 기본 연산
- 단위행렬 및 역행렬 계산
- Tensorflow의 기본 수학 연산 학습

### Part 2: 선형 회귀분석 (regression_tf.py)
- 기온-매출 데이터 로드 및 탐색
- 산점도를 통한 데이터 시각화
- 초기 모델 설정 (y = ax + b)
- 평균제곱오차(MSE) 손실 함수 정의
- 그래디언트 계산 및 경사하강법 구현
- 모델 학습 과정 시각화
- 최종 회귀선 및 성능 평가

## 🎯 예상 결과

### 회귀분석 결과
- **최종 파라미터**: a ≈ 16.00, b ≈ 811.62
- **회귀식**: y = 16.00 × x + 811.62
- **최종 MSE**: ≈ 13896.5
- **결정계수 (R²)**: 높은 값 (데이터에 따라 다름)

### 시각화 결과
- 기온과 매출 간의 양의 상관관계 확인
- 학습 전후 회귀선 비교
- 최종 회귀선이 데이터에 잘 맞는지 확인

## 📈 학습 알고리즘

### 경사하강법 (Gradient Descent)
1. **초기화**: a = 20.0, b = 650.0
2. **반복**:
   - 예측값 계산: y_pred = a × x + b
   - 손실 계산: MSE = mean((y - y_pred)²)
   - 그래디언트 계산: ∂MSE/∂a, ∂MSE/∂b
   - 파라미터 업데이트: a = a - lr × ∂MSE/∂a, b = b - lr × ∂MSE/∂b
3. **종료 조건**: 그래디언트가 충분히 작을 때 (|∂MSE/∂a| < 0.05, |∂MSE/∂b| < 0.05)

## 🔧 주요 개념

- **Tensor**: Tensorflow의 기본 데이터 구조
- **Variable**: 학습 가능한 파라미터
- **GradientTape**: 자동 미분을 위한 컨텍스트 매니저
- **손실 함수**: 모델 성능을 측정하는 함수 (MSE)
- **경사하강법**: 손실을 최소화하는 최적화 알고리즘

## 📝 참고사항

- Python 3.7+ 권장
- Tensorflow 2.x 버전 사용
- matplotlib 백엔드 설정이 필요한 경우: `export MPLBACKEND=Agg`