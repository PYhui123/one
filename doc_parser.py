# -*- coding: utf-8 -*-
"""
文档解析与语义切块模块（接在你的 script1.py 建库脚本前面用）

功能：
1. 解析 PDF（PyMuPDF）和 Word（python-docx），逐页 / 逐段提取纯文本
2. 语义切块：优先在段落 / 标题边界断开，块间带重叠，避免把一条完整建议切两半
3. 每个 chunk 附带元数据（来源文件、章节、页码），方便后续按设备型号 / 故障类型过滤
4. 输出格式直接对齐 ChromaDB 的 add 接口（documents / metadatas / ids）

依赖安装：
    pip install pymupdf python-docx

用法（在你的建库脚本里）：
    from 文档解析与切块 import build_chunks_from_paths
    docs, metas = build_chunks_from_paths(["压缩机维修手册.pdf", "风机手册.docx"])
    collection.add(documents=docs, metadatas=metas,
                   ids=[f"doc_{i}" for i in range(len(docs))])
"""

import os
import re
from typing import List, Tuple


# ============ 一、单文档解析：统一输出 [(text, page, heading), ...] ============

def parse_pdf(path: str) -> List[Tuple[str, int, str]]:
    """解析 PDF。返回每页的 (文本, 页码, 页内首个标题)。"""
    import fitz  # PyMuPDF
    items = []
    doc = fitz.open(path)
    try:
        for page_index, page in enumerate(doc, start=1):
            # 用 dict 模式拿字体大小，字号明显偏大的短行判为标题
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
            sizes = []
            for b in blocks["blocks"]:
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        if s["text"].strip():
                            sizes.append(round(s["size"], 1))
            body_size = _median(sizes) if sizes else 10.5

            lines, heading = [], ""
            for b in blocks["blocks"]:
                for l in b.get("lines", []):
                    text = "".join(s["text"] for s in l.get("spans", [])).strip()
                    if not text:
                        continue
                    max_size = max((s["size"] for s in l.get("spans", [])), default=body_size)
                    if max_size > body_size * 1.2 and len(text) < 40:
                        if not heading:
                            heading = text
                    lines.append(text)
            page_text = "\n".join(lines).strip()
            if page_text:
                items.append((page_text, page_index, heading))
    finally:
        doc.close()
    return items


def parse_docx(path: str) -> List[Tuple[str, int, str]]:
    """解析 Word。返回 (段落文本, 序号, 所属标题)。docx 无真实页码，用序号占位。"""
    import docx
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    document = docx.Document(path)
    items = []
    current_heading = ""
    order = 0
    body = document.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            para = Paragraph(child, document)
            text = para.text.strip()
            if not text:
                continue
            style = (para.style.name or "").lower()
            if style.startswith("heading") or style.startswith("标题"):
                current_heading = text
                continue
            order += 1
            items.append((text, order, current_heading))
        elif isinstance(child, CT_Tbl):
            table = Table(child, document)
            rows = []
            for r in table.rows:
                cells = [c.text.strip().replace("\n", " ") for c in r.cells]
                rows.append(" | ".join(cells))
            table_text = "\n".join(rows).strip()
            if table_text:
                order += 1
                items.append((table_text, order, current_heading))
    return items


# ============ 二、语义切块（带重叠）============

def semantic_chunk(items: List[Tuple[str, int, str]],
                   source: str,
                   max_chars: int = 500,
                   overlap: int = 50) -> Tuple[List[str], List[dict]]:
    """把解析结果切成 chunks，优先在标题 / 段落边界断开，块间保留 overlap 重叠。"""
    docs: List[str] = []
    metas: List[dict] = []
    buffer = ""
    buf_heading = ""
    buf_page = None

    def flush():
        nonlocal buffer, buf_heading, buf_page
        if not buffer.strip():
            return
        prefix = _make_prefix(source, buf_heading)
        docs.append((prefix + buffer).strip())
        metas.append({
            "source": source,
            "section": buf_heading or "",
            "page": buf_page if buf_page is not None else -1,
        })
        tail = buffer[-overlap:] if overlap > 0 and len(buffer) > overlap else ""
        buffer = tail

    for text, page, heading in items:
        if heading != buf_heading and buffer.strip():
            flush()
            buffer = ""  # 章节切换，丢弃上一章重叠尾巴，避免污染
        if buf_page is None:
            buf_page = page
        buf_heading = heading or buf_heading

        for piece in _split_long(text, max_chars):
            if len(buffer) + len(piece) + 1 > max_chars and buffer.strip():
                flush()
                if buf_page is None:
                    buf_page = page
            buffer += (piece + "\n")
    flush()
    return docs, metas


def _split_long(text: str, max_chars: int) -> List[str]:
    """超长段落按句子边界切成 <= max_chars 的片段。"""
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r'(?<=[。！？；;\n])', text)
    pieces, cur = [], ""
    for s in sentences:
        if not s:
            continue
        if len(cur) + len(s) > max_chars and cur:
            pieces.append(cur)
            cur = s
        else:
            cur += s
    for piece in ([cur] if cur else []):
        while len(piece) > max_chars:
            pieces.append(piece[:max_chars])
            piece = piece[max_chars:]
        if piece:
            pieces.append(piece)
    return pieces


def _make_prefix(source: str, heading: str) -> str:
    name = os.path.splitext(os.path.basename(source))[0]
    if heading:
        return f"【{name} > {heading}】\n"
    return f"【{name}】\n"


def _median(nums: List[float]) -> float:
    s = sorted(nums)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


# ============ 三、对外总入口 ============

def build_chunks_from_paths(paths: List[str],
                            max_chars: int = 500,
                            overlap: int = 50) -> Tuple[List[str], List[dict]]:
    """解析多个文档并切块，返回 (documents, metadatas)，直接喂给 ChromaDB。"""
    all_docs: List[str] = []
    all_metas: List[dict] = []
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            items = parse_pdf(path)
        elif ext in (".docx", ".doc"):
            items = parse_docx(path)
        else:
            print(f"[跳过] 暂不支持的格式: {path}")
            continue
        docs, metas = semantic_chunk(items, source=path,
                                     max_chars=max_chars, overlap=overlap)
        all_docs.extend(docs)
        all_metas.extend(metas)
        print(f"[完成] {os.path.basename(path)} -> {len(docs)} 个 chunk")
    return all_docs, all_metas


if __name__ == "__main__":
    demo = [
        ("离心式压缩机在夏季高负荷运行时，排气温度容易偏高。首先检查冷却水温是否超过 32℃。", 1, "故障排查 > 温度异常"),
        ("若冷却水正常，则检查进气过滤器是否堵塞，堵塞会导致压缩比升高进而推高排气温度。", 1, "故障排查 > 温度异常"),
        ("轴承温度报警时，应优先确认润滑油油位与油压，油位低于下限会造成轴承干摩擦。", 2, "故障排查 > 轴承"),
    ]
    d, m = semantic_chunk(demo, source="demo.pdf", max_chars=60, overlap=15)
    for i, (t, meta) in enumerate(zip(d, m)):
        print(f"--- chunk {i} | 章节={meta['section']} | 页={meta['page']} ---")
        print(t)
