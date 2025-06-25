import tensorflow as tf

print("=== Tensorflow 기본 연산 실습 ===\n")

# Tensor 생성
print("1. Tensor 생성")
a = tf.constant(1)
print(f"a = {a}, dtype = {a.dtype}")

b = tf.constant(1.0, dtype=tf.float32)
print(f"b = {b}, dtype = {b.dtype}\n")

# 행렬 생성
print("2. 행렬 생성")
A = tf.constant([[1, 2], [3, 4]])
B = tf.constant([[5, 6], [7, 8]])

print(f"A = \n{A}")
print(f"B = \n{B}\n")

# 행렬 덧셈 및 곱셈
print("3. 행렬 연산")
print(f"A + B = \n{tf.add(A, B)}")
print(f"A × B = \n{tf.matmul(A, B)}\n")

# 단위행렬 및 역행렬
print("4. 단위행렬 및 역행렬")
I = tf.eye(2, dtype=tf.int32)  # int32 타입으로 생성
print(f"단위행렬 I = \n{I}")
print(f"A × I = \n{tf.matmul(A, I)}")

# 역행렬 계산 (float32로 변환 필요)
A_float = tf.cast(A, tf.float32)
A_inv = tf.linalg.inv(A_float)
print(f"A의 역행렬 = \n{A_inv}")
print(f"A × A^(-1) = \n{tf.matmul(A_float, A_inv)}")

print("\n=== Tensorflow 기본 연산 실습 완료 ===")