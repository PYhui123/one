import chromadb
from openai import OpenAI
import os

# --- 1. 初始化配置 (保持不变) ---
print("正在初始化系统...")

# 初始化 OpenAI 客户端 (阿里云 DashScope)
client = OpenAI(
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 定义向量化函数
def embed(text):
    resp = client.embeddings.create(model="text-embedding-v3", input=[text])
    return resp.data[0].embedding

# 连接本地知识库
try:
    chroma_client = chromadb.PersistentClient(path="./kb")
    collection = chroma_client.get_collection("equipment")
    print("✅ 知识库连接成功！\n")
except Exception as e:
    print(f"❌ 连接知识库失败: {e}")
    print("请确保你已经运行了 script1.py 构建了知识库。")
    exit()

# --- 2. 交互式问答循环 ---
print("=" * 50)
print("欢迎使用工业设备维修助手 (CLI版)")
print("输入问题开始提问，输入 'q' 或 'quit' 退出")
print("=" * 50)

while True:
    # 获取用户输入
    question = input("\n👤 请输入你的问题: ").strip()

    # 退出条件
    if question.lower() in ['q', 'quit', 'exit', '退出']:
        print("👋 再见！")
        break

    if not question:
        continue

    try:
        # A. 检索相关文档
        # n_results=3 稍微增加一点检索数量，防止信息遗漏
        results = collection.query(query_embeddings=[embed(question)], n_results=3)

        # B. 构建上下文
        documents = results["documents"][0]
        if not documents:
            context = "未检索到相关资料。"
        else:
            context = "\n".join(documents)

        # C. 构建提示词 (Prompt)
        prompt = f"""你是工业设备维修助手。仅根据以下参考资料回答问题，如果资料中没有相关信息，请说“资料中未找到相关内容”。

参考资料：
{context}

问题：{question}
回答："""

        # D. 调用大模型生成回答
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}]
        )

        # E. 输出结果
        answer = response.choices[0].message.content
        print(f"\n🤖 助手回答:\n{answer}")
        print("-" * 50)

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")