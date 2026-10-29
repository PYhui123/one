# 项目名称 基于 RAG（检索增强生成） 技术的本地知识库问答系统

## 项目简介

本项目是一个基于 Python 开发的智能文档问答助手。它利用 RAG (Retrieval-Augmented Generation) 技术，允许用户上传本地文档（如维修手册、操作指南），并通过自然语言与这些文档进行交互问答。
项目核心使用了 阿里云 DashScope (通义千问) 提供的 Embedding 模型进行文本向量化，并使用 Chroma 作为向量数据库进行存储和检索

## 技术栈

- 编程语言：Python 3.14.7
- 开发工具：PyCharm
- 大模型服务：阿里云DashScope（兼容OpenAI SDK模式）
- 向量数据库：ChromaDB（chromadb）
- 核心库：openai、os、sys
- 自定义模块：doc_parser（用于文档解析和分块）

## 项目结构
欢迎界面/
├── .venv/                # 虚拟环境目录
├── kb/ # 知识库，可能用于存放处理后的数据或索引
├── app.py                # 主应用程序入口（可能是 UI 或 Web 服务）
├── ASK.py                # 问答逻辑模块
├── auth.py               # 认证或配置模块
├── doc_parser.py         # 文档解析器（负责读取 PDF/DOCX 并分块）
├── rag_agent.py          # RAG 代理逻辑
├── script1.py            # 当前激活脚本（用于测试文档入库流程）
├── 压缩机维修手册.pdf      # 示例数据文件
└── 风机手册.docx         # 示例数据文件
## 如何运行
请先运行 script1.py 将数据入库，然后才能运行 ASK.py 进行问答
## 作者

GitHub：https://github.com/PYhui123
