from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Sample car data
car_data = [
    {
        "model": "현대 아반떼",
        "year": "2024",
        "price": "2000만원",
        "description": "현대 아반떼는 경제적이고 실용적인 준중형 세단입니다. 연비가 우수하고 첨단 안전 사양을 갖추고 있어 출퇴근용으로 적합합니다."
    },
    {
        "model": "기아 K5",
        "year": "2024",
        "price": "2500만원",
        "description": "기아 K5는 중형 세단으로 넓은 실내 공간과 고급스러운 디자인이 특징입니다. 가족용 차량으로 인기가 높습니다."
    },
    {
        "model": "현대 투싼",
        "year": "2024",
        "price": "3000만원",
        "description": "현대 투싼은 실용적인 중형 SUV입니다. 높은 차체와 넓은 적재 공간으로 가족용 차량으로 적합합니다."
    }
]

# Sample finance data
finance_data = [
    {
        "type": "할부",
        "description": "36개월 무이자 할부 가능, 선수금 20% 필요"
    },
    {
        "type": "리스",
        "description": "36개월 리스, 월 납입금 50만원부터, 보증금 20%"
    },
    {
        "type": "렌트",
        "description": "장기렌트 36개월, 월 납입금 60만원부터, 보증금 없음"
    }
]

def load_car_data():
    embeddings = OpenAIEmbeddings()
    car_db = Chroma(
        collection_name="car_info",
        embedding_function=embeddings,
        persist_directory="./database"
    )
    
    # Add car data
    texts = [car["description"] for car in car_data]
    car_db.add_texts(texts)
    car_db.persist()
    print("Car data loaded successfully")

def load_finance_data():
    embeddings = OpenAIEmbeddings()
    finance_db = Chroma(
        collection_name="finance_info",
        embedding_function=embeddings,
        persist_directory="./database"
    )
    
    # Add finance data
    texts = [finance["description"] for finance in finance_data]
    finance_db.add_texts(texts)
    finance_db.persist()
    print("Finance data loaded successfully")

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set your OpenAI API key in the .env file")
        exit(1)
    
    load_car_data()
    load_finance_data() 