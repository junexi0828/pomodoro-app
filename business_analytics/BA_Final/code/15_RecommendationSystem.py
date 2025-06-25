import pandas as pd
import numpy as np

# --- CSV 파일 불러오기 ---
movie = pd.read_csv('tmdb_5000_movies.csv')

# --- 필요한 열만 추출 (제목과 장르) ---
movie = movie[['original_title', 'genres']]

# --- 문자열을 리스트로 변환 ---
movie['genres'] = movie['genres'].apply(eval)                # 문자열 → 리스트(dict)
movie['genres'] = movie['genres'].apply(lambda x: [d['name'] for d in x])  # dict → 장르명 리스트

# --- 존재하는 모든 장르 모으기 ---
all_genres = []
for i in range(len(movie)):
    mv = movie.loc[i]
    for g in mv['genres']:
        if g not in all_genres:
            all_genres.append(g)

# --- 장르 벡터 생성 ---
movie['gvec'] = None
for i in range(len(movie)):
    mv = movie.loc[i]
    vec = []
    for g in all_genres:
        if g in mv['genres']:
            vec.append(1)
        else:
            vec.append(0)
    movie.at[i, 'gvec'] = np.array(vec)

# --- 코사인 유사도 함수 정의 ---
def similarity(v1, v2):
    dot = np.dot(v1, v2)
    if dot == 0:
        return 0
    return dot / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- 영화 번호 입력 받기 ---
movie_num_str = input("영화 번호를 입력하세요 (0~{}): ".format(len(movie)-1))
movie_num = int(movie_num_str)
print("입력한 영화 제목:", movie.loc[movie_num, 'original_title'])

# --- 유사도 계산 ---
sim_list = []
for i in range(len(movie)):
    sim = similarity(movie.loc[movie_num, 'gvec'], movie.loc[i, 'gvec'])
    sim_list.append(sim)

# --- 유사도 높은 상위 10개 추천 출력 ---
y = list(np.argsort(sim_list)[::-1])  # 유사도 내림차순 정렬 인덱스
for i in y[1:11]:                     # 자기 자신 제외 (0번), 상위 10개 출력
    print(sim_list[i], movie.loc[i, 'original_title'])

    # =============================================
# 📘 예습: 콘텐츠 기반 필터링 (Content-Based Filtering)
# TMDB 영화 데이터의 장르 정보를 바탕으로 영화 추천
# 강의노트 내에는 수록되어 있지 않음 (심화/예습용)
# =============================================

import pandas as pd
import numpy as np

# --- CSV 파일 불러오기 ---
movie = pd.read_csv('tmdb_5000_movies.csv')

# --- 필요한 열만 추출 (제목과 장르) ---
movie = movie[['original_title', 'genres']]

# --- 문자열을 리스트로 변환 ---
movie['genres'] = movie['genres'].apply(eval)  # 문자열 → 리스트(dict)
movie['genres'] = movie['genres'].apply(lambda x: [d['name'] for d in x])  # dict → 장르명 리스트

# --- 존재하는 모든 장르 모으기 ---
all_genres = []
for i in range(len(movie)):
    mv = movie.loc[i]
    for g in mv['genres']:
        if g not in all_genres:
            all_genres.append(g)

# --- 장르 벡터 생성 ---
movie['gvec'] = None
for i in range(len(movie)):
    mv = movie.loc[i]
    vec = []
    for g in all_genres:
        vec.append(1 if g in mv['genres'] else 0)
    movie.at[i, 'gvec'] = np.array(vec)

# --- 코사인 유사도 함수 정의 ---
def similarity(v1, v2):
    dot = np.dot(v1, v2)
    if dot == 0:
        return 0
    return dot / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- 영화 번호 입력 받기 ---
movie_num_str = input("영화 번호를 입력하세요 (0~{}): ".format(len(movie)-1))
movie_num = int(movie_num_str)
print("입력한 영화 제목:", movie.loc[movie_num, 'original_title'])

# --- 유사도 계산 ---
sim_list = []
for i in range(len(movie)):
    sim = similarity(movie.loc[movie_num, 'gvec'], movie.loc[i, 'gvec'])
    sim_list.append(sim)

# --- 유사도 높은 상위 10개 추천 출력 ---
y = list(np.argsort(sim_list)[::-1])  # 유사도 내림차순 정렬 인덱스
for i in y[1:11]:                     # 자기 자신 제외
    print(sim_list[i], movie.loc[i, 'original_title'])