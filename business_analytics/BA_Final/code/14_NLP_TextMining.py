# =============================
# ex14-1.py
# =============================
f = open('제6차_국가정보화기본계획.txt', 'r', encoding='UTF-8')
doc = f.read()
f.close()

# 특수기호들을 공백으로 치환
doc = doc.replace('\n', ' ')
doc = doc.replace('.', ' ')
doc = doc.replace(',', ' ')
doc = doc.replace('·', ' ')
doc = doc.replace('”', ' ')
doc = doc.replace('“', ' ')
doc = doc.replace('(', ' ')
doc = doc.replace(')', ' ')

words = dict()
for w in doc.split(' '):
    if len(w) == 0:
        continue
    if w not in words:
        words[w] = 1
    else:
        words[w] += 1

# 단어를 빈도수 기준으로 정렬
wlist = sorted(words.items(), key=lambda x: x[1], reverse=True)

# 불용어(stopword) 제거
stopwords = ['및', '위한', '등', '수', '것', '수준', '통해', '대한', '있다', '있는', '에서', '하여', '하고']
for w in stopwords:
    wlist = list(filter(lambda x: x[0] != w, wlist))

for w in wlist[:50]:
    print(w)

# =============================
# ex14-2.py
# =============================
from wordcloud import WordCloud
import matplotlib.pyplot as plt

wlist = [('데이터', 92), ('정보', 66), ('활용', 46), ('서비스', 39), ('국가', 37), ('디지털', 36), ('공공', 33)]

tmp = dict()
for word, freq in wlist:
    tmp[word] = freq

wc = WordCloud(font_path='KoPubWorld Dotum Medium.ttf', background_color='white', width=600, height=400)
cloud = wc.generate_from_frequencies(tmp)

plt.figure()
plt.imshow(cloud)
plt.axis('off')
plt.show()

# =============================
# ex14-3.py
# =============================
import numpy as np

def tf(w, d):
    return d.count(w)

def df(w, D):
    cnt = 0
    for d in D:
        if w in d:
            cnt += 1
    return cnt

def tfidf(w, d, D):
    return tf(w, d) * np.log(len(D) / df(w, D))

# =============================
# ex14-4.py
# =============================
import numpy as np

D = [['이', '영화', '완전', '감동'], ['완전', '다른', '영화'], ['진짜', '강추', '강추', '완전']]

# 고유 단어 추출
vocab = sorted(list(set(w for d in D for w in d)))

# TF-IDF 행렬
tfidf_matrix = []
for d in D:
    tfidf_vec = []
    for w in vocab:
        tfidf_vec.append(tfidf(w, d, D))
    tfidf_matrix.append(tfidf_vec)

# 코사인 유사도 계산
def norm(v):
    return np.sqrt(sum(x ** 2 for x in v))

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (norm(v1) * norm(v2))

print("A vs B:", cosine_similarity(tfidf_matrix[0], tfidf_matrix[1]))
print("A vs C:", cosine_similarity(tfidf_matrix[0], tfidf_matrix[2]))

# =============================
# ex14-5.py
# =============================
from tensorflow.keras.datasets import imdb
from tensorflow.keras import models, layers
import numpy as np

# 데이터 불러오기
(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=1000)

# BOW 벡터화
def vectorize(data):
    result = np.zeros((len(data), 1000))
    for i, d in enumerate(data):
        for w in d:
            if w < 1000:
                result[i, w] += 1
    return result

x_train = vectorize(train_data)
x_test = vectorize(test_data)

# 정규화
x_train = np.where(x_train >= 4, 1, x_train * 0.25)
x_test = np.where(x_test >= 4, 1, x_test * 0.25)

# 신경망 구성
model = models.Sequential()
model.add(layers.Dense(15, activation='relu', input_shape=(1000,)))
model.add(layers.Dense(15, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 학습
model.fit(x_train, train_labels, epochs=5, batch_size=512)

# 평가
results = model.evaluate(x_test, test_labels)
print("정확도:", results[1])

