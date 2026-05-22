""" Paper Writing Service
Orchestrates single-step AI generation for the paper writing platform.
Embeds workflow node definitions to avoid DB dependency for template data.
"""
import logging

from engine.executor import WorkflowExecutor
from engine.nodes import WorkflowNode
from providers.base import LLMProvider
from storage.db import (
    get_article_section,
    upsert_article_section,
    list_article_sections,
)
from services.article_service import article_service

logger = logging.getLogger(__name__)

# Embedded workflow node definitions — mirrors the frontend template
RESEARCH_WORKFLOW_NODES = [
    {
        "id": "start",
        "type": "start",
        "data": {"label": "Start", "prompt": "开始科研论文写作流程"},
    },
    {
        "id": "lit-review",
        "type": "prompt",
        "data": {
            "label": "文献综述与研究现状",
            "prompt": "基于以下研究主题，进行文献综述和研究现状分析：\n\n{{start}}\n\n请输出以下内容：\n1. 研究背景与问题领域概述\n2. 国内外研究现状综述（分方向梳理）\n3. 现有研究的主要方法、发现与贡献\n4. 研究空白与不足之处\n5. 本研究的切入点与创新点\n6. 关键参考文献（作者、年份、主要发现）",
            "system_prompt": "你是一个科研领域的学术助手，擅长文献综述和研究现状分析。请用中文以结构化 Markdown 格式输出，引用格式使用 [作者, 年份]。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "research-q",
        "type": "prompt",
        "data": {
            "label": "研究问题与假设",
            "prompt": "基于以下文献综述，提出研究问题和假设：\n\n{{lit-review}}\n\n请输出以下内容：\n1. 核心研究问题（1-3 个明确、可研究的问题）\n2. 研究目标与子目标\n3. 研究假设（H1, H2, ...）\n4. 关键变量定义（自变量、因变量、控制变量）\n5. 研究范围与边界\n6. 理论框架/概念模型",
            "system_prompt": "你是一个科研方法专家，擅长帮助研究者构建研究问题和假设。请用中文以结构化 Markdown 格式输出。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "methodology",
        "type": "prompt",
        "data": {
            "label": "研究方法与实验设计",
            "prompt": "基于以下研究问题，设计研究方法：\n\n{{research-q}}\n\n请输出以下内容：\n1. 研究方法选择（定性/定量/混合方法）及理由\n2. 数据收集方案（样本量、采样方法、数据来源）\n3. 实验/研究设计（分组、流程、控制条件）\n4. 数据分析方法（统计方法、模型、软件工具）\n5. 评估指标与评价标准\n6. 效度与信度保障措施\n7. 伦理考虑（如涉及人类/动物实验）",
            "system_prompt": "你是一个实验设计和研究方法论专家。请用中文以结构化 Markdown 格式输出，包含具体可执行的方案。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "results",
        "type": "prompt",
        "data": {
            "label": "结果分析与发现",
            "prompt": "基于以下研究方法，呈现和分析实验结果：\n\n{{methodology}}\n\n请输出以下内容：\n1. 数据预处理和清洗过程\n2. 描述性统计分析结果\n3. 假设检验结果（含统计显著性）\n4. 可视化图表描述（建议图表类型与展示方式）\n5. 主要发现总结（与研究问题对应）\n6. 未预期的发现或副结果\n7. 结果可靠性分析（鲁棒性检验、敏感性分析等）",
            "system_prompt": "你是一个数据分析与科研结果呈现专家。请用中文以结构化 Markdown 格式输出，包含表格来描述统计结果。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "discussion",
        "type": "prompt",
        "data": {
            "label": "讨论与结果解读",
            "prompt": "基于以下结果分析，撰写讨论部分：\n\n{{results}}\n\n文献综述参考：\n{{lit-review}}\n\n请输出以下内容：\n1. 主要发现解读（与研究问题和假设对应）\n2. 与现有文献的比较（支持/矛盾的地方）\n3. 研究发现的理论贡献与实践意义\n4. 研究局限性（方法、样本、实验条件等）\n5. 未来研究方向\n6. 研究结论的推广条件与适用范围",
            "system_prompt": "你是一个学术论文写作指导专家，擅长帮助研究者撰写讨论部分。请用中文以结构化 Markdown 格式输出，保持学术严谨性。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "abstract-title",
        "type": "prompt",
        "data": {
            "label": "摘要与标题",
            "prompt": "基于完整的论文内容，生成摘要和标题：\n\n研究问题：\n{{research-q}}\n\n研究方法：\n{{methodology}}\n\n结果：\n{{results}}\n\n讨论：\n{{discussion}}\n\n请输出以下内容：\n1. 论文标题建议（3-5 个候选标题，含主副标题格式）\n2. 中文摘要（200-300 字，含背景、目的、方法、结果、结论）\n3. 英文摘要（Abstract，150-250 words，与中文对应）\n4. 关键词（3-5 个中文关键词 + 3-5 个英文关键词）\n5. 论文创新点简要陈述",
            "system_prompt": "你是一个学术论文写作专家，擅长撰写高质量的论文摘要和标题。请用中英文双语输出，Markdown 格式。",
            "provider": "claude", "model": "claude-sonnet-4-20250514",
        },
    },
    {
        "id": "gen-references",
        "type": "code",
        "data": {
            "label": "参考文献格式化",
            "description": "根据论文引用内容，生成标准参考文献列表（GB/T 7714 / APA 格式）",
            "file_path": "paper/references.bib",
        },
    },
    {
        "id": "final-output",
        "type": "output",
        "data": {"label": "完整论文输出"},
    },
]

# Topological ordering for compilation
WORKFLOW_EDGES = [
    {"source": "start", "target": "lit-review"},
    {"source": "lit-review", "target": "research-q"},
    {"source": "research-q", "target": "methodology"},
    {"source": "methodology", "target": "results"},
    {"source": "results", "target": "discussion"},
    {"source": "lit-review", "target": "discussion"},
    {"source": "research-q", "target": "abstract-title"},
    {"source": "methodology", "target": "abstract-title"},
    {"source": "results", "target": "abstract-title"},
    {"source": "discussion", "target": "abstract-title"},
    {"source": "abstract-title", "target": "gen-references"},
    {"source": "discussion", "target": "gen-references"},
    {"source": "results", "target": "final-output"},
    {"source": "discussion", "target": "final-output"},
    {"source": "abstract-title", "target": "final-output"},
    {"source": "gen-references", "target": "final-output"},
]


def _resolve_provider(node_data: dict) -> LLMProvider | None:
    provider_name = node_data.get("provider")
    api_key = node_data.get("api_key", "")
    model = node_data.get("model", "")
    if provider_name and api_key:
        try:
            return LLMProvider.get_provider(provider_name, api_key, model)
        except Exception:
            logger.exception("Failed to create provider %s", provider_name)
    return None


async def get_section(article_id: str, node_id: str) -> dict | None:
    section = await get_article_section(article_id, node_id)
    if section is None:
        return {"content": "", "status": "pending"}
    return section


async def update_section(
    article_id: str, node_id: str, content: str, status: str
) -> bool:
    article = await article_service.get_article(article_id)
    if not article:
        return False
    await upsert_article_section(article_id, node_id, content, status)
    return True


async def generate_section(
    article_id: str, node_id: str, upstream_ids: list[str]
) -> str | None:
    article = await article_service.get_article(article_id)
    if not article:
        return None

    target_node_def = next(
        (n for n in RESEARCH_WORKFLOW_NODES if n["id"] == node_id), None
    )
    if not target_node_def or target_node_def["type"] != "prompt":
        return None

    # Load upstream sections from DB
    sections = await list_article_sections(article_id)
    sections_by_node = {s["node_id"]: s for s in sections}

    # Build execution context with upstream content
    executor = WorkflowExecutor()
    for uid in upstream_ids:
        if uid in sections_by_node:
            executor.context.set_node_output(
                uid, sections_by_node[uid]["content"]
            )
        elif uid == "start":
            executor.context.set_node_output(
                uid, article.title or article.abstract or ""
            )

    # Resolve provider
    target_data = target_node_def.get("data", {})
    provider = _resolve_provider(target_data)

    # Execute single node
    node = WorkflowNode(
        id=target_node_def["id"],
        type=target_node_def["type"],
        position={"x": 0, "y": 0},
        data=target_data,
    )
    upstream = executor.context.get_upstream_outputs(
        node_id, WORKFLOW_EDGES
    )
    output = await executor.execute_node(node, upstream, provider)
    return output


async def compile_paper(article_id: str) -> dict | None:
    article = await article_service.get_article(article_id)
    if not article:
        return None

    sections = await list_article_sections(article_id)
    sections_by_node = {s["node_id"]: s for s in sections}

    # Build compile order using topological sort
    executor = WorkflowExecutor()
    node_ids = [n["id"] for n in RESEARCH_WORKFLOW_NODES]
    ordered = executor._topological_sort(node_ids, WORKFLOW_EDGES)

    parts = []
    for nid in ordered:
        section = sections_by_node.get(nid)
        if section and section.get("content", "").strip():
            label = next(
                (
                    n["data"].get("label", nid)
                    for n in RESEARCH_WORKFLOW_NODES
                    if n["id"] == nid
                ),
                nid,
            )
            parts.append(f"\n\n{'='*60}\n## {label}\n{'='*60}\n\n{section['content']}")

    compiled = "".join(parts).strip()

    return {"compiled": compiled, "sectionCount": len(parts)}


async def get_paper_status(article_id: str) -> list[dict] | None:
    article = await article_service.get_article(article_id)
    if not article:
        return None

    sections = await list_article_sections(article_id)
    sections_by_node = {s["node_id"]: s for s in sections}

    result = []
    for n in RESEARCH_WORKFLOW_NODES:
        if n["type"] not in ("prompt", "code", "output"):
            continue
        section = sections_by_node.get(n["id"])
        result.append({
            "node_id": n["id"],
            "label": n["data"].get("label", n["id"]),
            "type": n["type"],
            "status": section["status"] if section else "pending",
        })
    return result
