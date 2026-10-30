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

## 🚀 如何运行

为了简化操作，项目提供了一键启动脚本 `start.py`，它会自动检查环境依赖并提供交互式菜单。

方式一：使用一键启动脚本（推荐）

在终端中运行以下命令：

```bash

python start.py

脚本将自动执行以下操作：
环境自检：自动检测并安装 chromadb, openai 等缺失的依赖库。
交互菜单：
选择 1：仅执行文档解析与入库（对应原 script1.py）。
选择 2：直接启动问答系统（对应原 ASK.py）。
选择 3：全量模式（先重新入库数据，紧接着启动问答）。

方式二：手动分步运行
如果您想单独调试某个环节，可以按顺序执行：
数据入库（首次运行或更新文档时必须执行）：
bash

python script1.py

启动问答：
bash

python ASK.py

⚠️ 注意事项
API Key 配置：请确保您已在 auth.py 文件或系统环境变量中正确配置了阿里云 DashScope 的 API Key。
Python 版本：建议使用 Python 3.10+ 以获得最佳兼容性

## 作者

GitHub：https://github.com/PYhui123
