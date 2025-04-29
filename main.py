# LangChain 관련 패키지
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain.tools import Tool

# 도구(Tools) 관련 패키지
from tools.finance_condition_retriever import FinanceConditionRetriever
from tools.customer_info_retriever import CustomerInfoRetriever

# UI 관련 패키지
from ui.app import create_interface
import gradio as gr

# 시스템 및 환경변수 관련 패키지
import os
from dotenv import load_dotenv

# 타입 힌트 관련 패키지
from typing import Optional
import json

def main(customer_id: str = "0000000000"):
    """메인 함수
    
    Args:
        customer_id (str, optional): 고객 번호. 기본값은 "0000000000".
    """
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")

    # 고객 정보 관리자 초기화
    customer_retriever = CustomerInfoRetriever()
    
    # 고객 정보 조회
    customer_info = customer_retriever.get_customer_info(customer_id)

    # 차량 정보 조회
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local("car_vector_index_multi", embedding, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="similarity", k=3)

    def car_retrieval_tool(query: str) -> str:
        results = retriever.get_relevant_documents(query)
        return "\n\n".join([r.page_content for r in results])

    # Initialize tools
    tools = [
        # CarInfoRetriever(),
        Tool(
            name="CarInfoTool",
            func=car_retrieval_tool,
            description="차량의 가격, 트림, 옵션 정보를 검색하는 도구입니다. 차량 관련한 질문에 사용하세요."
        ),
        FinanceConditionRetriever()
    ]

    # Create memory
    memory = ConversationBufferMemory(
        input_key="input",
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3
    )

    # Read system prompt from file
    with open("prompt/master_agent_system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create agent
    agent = create_openai_functions_agent(llm, tools, prompt)

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=10,
        early_stopping_method="force",    # 반복 제한 및 강제 종료
        handle_parsing_errors=True       # 파싱 오류 시 재시도 금지
    )

    def process_user_input(user_input: str) -> str:
        response = agent_executor.invoke({
            "input": user_input,
            "customer_info": json.dumps(customer_info, ensure_ascii=False, indent=2),
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        })
        return response["output"]

    # Create and launch interface
    interface = create_interface(process_user_input)
    interface.launch(share=True, show_api=False)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        print("Usage: python main.py [customer_id]")
        sys.exit(1)
    customer_id = sys.argv[1] if len(sys.argv) == 2 else "0000000000"
    main(customer_id)