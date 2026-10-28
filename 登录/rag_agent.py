# rag_agent.py
from langgraph.checkpoint.memory import MemorySaver  # 生产环境可替换为 SqliteSaver 或 Redis
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 假设你已经构建好了 RAG 的 graph 或 chain
# checkpointer 负责自动保存和加载历史消息
memory = MemorySaver()
agent = create_rag_agent(checkpointer=memory)


async def chat_with_rag(user_query: str, user_id: str):
    # 核心隔离逻辑：将 user_id 作为 thread_id 传入 config
    config = {"configurable": {"thread_id": user_id}}

    # 调用 Agent，LangGraph 会自动根据 thread_id 隔离并加载该用户的历史消息
    response = await agent.ainvoke(
        {"messages": [("user", user_query)]},
        config=config
    )
    return response["messages"][-1].content