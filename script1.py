import chromadb
from openai import OpenAI
import os
from doc_parser import build_chunks_from_paths   # ← 加这一行
import sys
print(sys.executable)
client = OpenAI(
    api_key=os.environ.get("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 模拟你的维修手册内容
docs, metas = build_chunks_from_paths(["压缩机维修手册.pdf", "风机手册.docx"])

# 用通义千问的 embedding 模型生成向量
def embed(text):
    resp = client.embeddings.create(model="text-embedding-v3", input=[text])
    return resp.data[0].embedding


# 存入 Chroma
chroma_client = chromadb.PersistentClient(path="./kb")
collection = chroma_client.get_or_create_collection("equipment")
collection.add(
    ids=[f"doc{i}" for i in range(len(docs))],
    documents=docs,
    embeddings=[embed(d) for d in docs]
)
print("知识库构建完成")
