import sqlite3
from datetime import datetime

def check_database():
    try:
        conn = sqlite3.connect('pomodoro_data.db')
        cursor = conn.cursor()
        
        print("=== 데이터베이스 상태 확인 ===")
        
        # 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"테이블 목록: {[table[0] for table in tables]}")
        
        # daily_summary 테이블 데이터 확인
        print("\n--- daily_summary 테이블 ---")
        cursor.execute("SELECT * FROM daily_summary")
        daily_data = cursor.fetchall()
        if daily_data:
            for row in daily_data:
                print(f"날짜: {row[0]}, 완료된 뽀모도로: {row[1]}, 성공: {row[2]}, 실패: {row[3]}, 총 집중시간(초): {row[4]}")
        else:
            print("데이터가 없습니다.")
        
        # tasks 테이블 데이터 확인
        print("\n--- tasks 테이블 ---")
        cursor.execute("SELECT * FROM tasks")
        tasks_data = cursor.fetchall()
        if tasks_data:
            for row in tasks_data:
                print(f"ID: {row[0]}, 날짜: {row[1]}, 작업명: {row[2]}, 시작시간: {row[3]}, 종료시간: {row[4]}, 상태: {row[5]}")
        else:
            print("데이터가 없습니다.")
        
        conn.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    check_database()
