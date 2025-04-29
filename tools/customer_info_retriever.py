import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CustomerInfoRetriever:
    """고객 정보 관리 클래스
    
    고객 정보의 생성, 조회, 수정을 담당하는 클래스입니다.
    샘플 고객 데이터를 생성하고 관리하며, 캐시를 통해 조회 성능을 최적화합니다.
    
    Attributes:
        customer_cache (Dict[str, Dict[str, Any]]): 고객 정보 캐시
        customer_data (pd.DataFrame): 기본 고객 데이터셋
    """
    
    def __init__(self):
        """CustomerInfoRetriever 초기화
        
        샘플 고객 데이터를 생성하고 캐시를 초기화합니다.
        """
        self.customer_cache: Dict[str, Dict[str, Any]] = {}
        self.customer_data = self._generate_sample_customer_data()

    def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """고객 정보를 조회합니다.
        
        캐시에서 먼저 조회하고, 없는 경우 기본 데이터셋에서 조회합니다.
        고객 정보가 없는 경우 새로운 고객 프로필을 생성합니다.
        
        Args:
            customer_id (str): 조회할 고객 번호
            
        Returns:
            Dict[str, Any]: 고객 정보 딕셔너리
        """
        # 캐시에 있는 경우 바로 반환
        if customer_id in self.customer_cache:
            return self.customer_cache[customer_id]
        
        # 저장된 데이터에서 고객 정보 조회
        customer_data = self.customer_data[self.customer_data["고객번호"] == customer_id]
        
        if customer_data.empty:
            # 고객 정보가 없는 경우 새 프로필 생성
            customer_info = self._create_new_customer_profile()
            customer_info["고객번호"] = customer_id
        else:
            # 기존 고객 정보를 딕셔너리로 변환
            customer_info = customer_data.iloc[0].to_dict()
            # 추가 정보 필드 초기화
            customer_info.update({
                "대화이력": [],
                "관심차종": [],
                "추가정보": {}
            })
        
        # 캐시에 저장
        self.customer_cache[customer_id] = customer_info
        return customer_info

    def update_customer_info(self, customer_id: str, new_info: Dict[str, Any]) -> None:
        """고객 정보를 업데이트합니다.
        
        캐시에 저장된 고객 정보를 업데이트합니다.
        
        Args:
            customer_id (str): 업데이트할 고객 번호
            new_info (Dict[str, Any]): 업데이트할 정보
        """
        if customer_id in self.customer_cache:
            self.customer_cache[customer_id].update(new_info)

    def _create_new_customer_profile(self) -> Dict[str, Any]:
        """새로운 고객 프로필을 생성합니다.
        
        모든 필드가 비어있는 기본 고객 프로필을 생성합니다.
        
        Returns:
            Dict[str, Any]: 기본 고객 프로필
        """
        return {
            "고객번호": "0000000000",  # 기본 고객번호
            "이름": "",                # 고객 이름
            "나이": 0,                # 고객 나이
            "성별": "",               # 고객 성별
            "전화번호": "",           # 연락처
            "이메일": "",             # 이메일 주소
            "최근방문일": datetime.now().strftime("%Y-%m-%d"),  # 현재 날짜로 설정
            "선호차종": "",           # 선호하는 차량 종류
            "예산": 0,                # 구매 예산
            "구매이력": 0,            # 과거 구매 횟수
            "시승횟수": 0,            # 시승 경험 횟수
            "가족구성원": 0,          # 가족 구성원 수
            "통근거리": 0,            # 일일 통근 거리(km)
            "선호연료": "",           # 선호하는 연료 타입
            "대화이력": [],           # 상담 대화 이력
            "관심차종": [],           # 관심 있는 차량 목록
            "추가정보": {}            # 기타 추가 정보
        }

    def _generate_sample_customer_data(self) -> pd.DataFrame:
        """샘플 고객 데이터를 생성합니다.
        
        테스트 및 개발용 샘플 고객 데이터를 생성합니다.
        실제 환경에서는 이 메서드 대신 실제 데이터베이스 연동이 필요합니다.
        
        Returns:
            pd.DataFrame: 샘플 고객 데이터
        """
        np.random.seed(42)  # 재현 가능한 결과를 위한 시드 설정
        
        # 기본 고객 정보 생성
        customer_ids = [f"{i:010d}" for i in range(1000000000, 1000000010)]
        names = ["김철수", "이영희", "박민수", "정지영", "최동욱", 
                "강미영", "윤성민", "장수진", "임태호", "한지은"]
        ages = np.random.randint(25, 60, 10)
        genders = np.random.choice(["남성", "여성"], 10)
        phone_numbers = [f"010-{np.random.randint(1000, 9999):04d}-{np.random.randint(1000, 9999):04d}" for _ in range(10)]
        emails = [f"customer{i}@example.com" for i in range(10)]
        
        # 차량 관련 정보 생성
        last_visit_dates = [(datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime("%Y-%m-%d") for _ in range(10)]
        preferred_car_types = np.random.choice(["SUV", "세단", "해치백", "전기차", "하이브리드"], 10)
        budgets = np.random.randint(30000000, 70000000, 10)
        purchase_histories = np.random.randint(0, 5, 10)
        test_drive_counts = np.random.randint(0, 3, 10)
        
        # 고객 특성 정보 생성
        family_sizes = np.random.randint(1, 5, 10)
        commute_distances = np.random.randint(5, 50, 10)
        preferred_fuel_types = np.random.choice(["가솔린", "디젤", "전기", "하이브리드"], 10)
        
        # 데이터프레임 생성 및 반환
        return pd.DataFrame({
            "고객번호": customer_ids,
            "이름": names,
            "나이": ages,
            "성별": genders,
            "전화번호": phone_numbers,
            "이메일": emails,
            "최근방문일": last_visit_dates,
            "선호차종": preferred_car_types,
            "예산": budgets,
            "구매이력": purchase_histories,
            "시승횟수": test_drive_counts,
            "가족구성원": family_sizes,
            "통근거리": commute_distances,
            "선호연료": preferred_fuel_types
        })        