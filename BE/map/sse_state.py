# 1단계: 전역 상태 저장 모듈 추가
# 이 모듈은 최신 위치 정보를 메모리에 저장하고 다른 곳에서 가져다 쓸 수 있게 함

import threading # threading 모듈은 멀티스레드 환경에서 데이터 동기화를 위해 사용됨

_latest_coords = [] # 위치 정보를 담아둘 전역 리스트 변수 (초기값은 빈 리스트)
_lock = threading.Lock() # 여러 스레드에서 동시에 접근할 때 충돌을 방지하기 위한 락(lock) 객체

# 최신 좌표 목록을 전역 변수에 안전하게 저장하는 함수
def set_latest_coords(coords):
    with _lock: # 락을 걸고 시작 (다른 스레드가 동시에 수정하지 못하게)
        global _latest_coords
        _latest_coords = coords # 새로운 좌표 리스트로 갱신

# 최신 좌표 목록을 전역 변수에서 안전하게 복사해서 가져오는 함수
def get_latest_coords():
    with _lock: # 읽을 때도 락을 걸어서 일관된 값을 보장
        return _latest_coords.copy() # 복사본을 반환 (원본이 변하지 않도록)