import asyncio
import logging
import os

from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent

from services.mcp_client import get_mcp_client
from services.subagents import (
    build_tableau_subagent,
    build_slack_subagent,
    build_web_subagent,
)

logger = logging.getLogger(__name__)

_agent = None
_mcp_client = None


async def _load_mcp_tools(client, server_name):
    """指定サーバーのツールを取得する。失敗時は空リストを返す。"""
    try:
        tools = await client.get_tools(server_name)
        logger.info("%sから%d個のツールを取得", server_name, len(tools))
        return tools
    except Exception:
        logger.exception("%sのツール取得に失敗", server_name)
        return []


async def init_agent():
    """DeepAgent + SubAgentを非同期で初期化する。"""
    global _agent, _mcp_client

    if _agent is not None:
        return _agent

    # MCPクライアント起動
    _mcp_client = get_mcp_client()
    subagents = []

    if _mcp_client is not None:
        await _mcp_client.__aenter__()

        # MCPツール取得（並列）
        tableau_tools, slack_tools = await asyncio.gather(
            _load_mcp_tools(_mcp_client, "tableau"),
            _load_mcp_tools(_mcp_client, "slack"),
        )

        if tableau_tools:
            subagents.append(build_tableau_subagent(tableau_tools))
        if slack_tools:
            subagents.append(build_slack_subagent(slack_tools))

    # Web検索SubAgent（MCP不要）
    subagents.append(build_web_subagent())

    logger.info("SubAgent %d個を登録: %s", len(subagents), [s["name"] for s in subagents])

    model = ChatBedrockConverse(
        model=os.environ.get(
            "BEDROCK_MODEL_ID",
            "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        ),
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-2"),
    )

    checkpointer = InMemorySaver()

    _agent = create_deep_agent(
        model=model,
        system_prompt=(
            "あなたはデータ分析チームのリーダーです。\n"
            "ユーザーの質問を分析し、適切なサブエージェントに作業を委譲します。\n\n"
            "## あなたの役割\n"
            "- ユーザーの意図を理解し、最適なサブエージェントを選択・指示する\n"
            "- サブエージェントの結果を統合し、分かりやすい回答を作成する\n"
            "- 複数のサブエージェントの結果を組み合わせてインサイトを提供する\n\n"
            "## サブエージェント\n"
            "- tableau-analyst: Tableauデータの取得・分析\n"
            "- slack-operator: Slack上の検索・投稿・Canvas作成\n"
            "- web-researcher: インターネットでの最新情報検索\n\n"
            "## 回答方針\n"
            "- データに基づく客観的な分析を優先する\n"
            "- アクション可能な提案を含める\n"
            "- 日本語で簡潔に回答する"
        ),
        checkpointer=checkpointer,
        subagents=subagents,
        name="slack-bot-agent",
    )
    return _agent


async def shutdown_agent():
    """MCPクライアントをクリーンアップする。"""
    global _mcp_client
    if _mcp_client is not None:
        try:
            await _mcp_client.__aexit__(None, None, None)
        except Exception:
            logger.exception("MCPクライアントのシャットダウンに失敗")
        _mcp_client = None


async def invoke_agent(message: str, thread_id: str) -> str:
    """DeepAgentを呼び出してテキスト応答を返す。"""
    agent = await init_agent()
    config = {"configurable": {"thread_id": thread_id}}
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    last_message = result["messages"][-1]
    if hasattr(last_message, "content_blocks") and last_message.content_blocks:
        texts = [
            block["text"]
            for block in last_message.content_blocks
            if block.get("type") == "text"
        ]
        return "\n".join(texts) if texts else last_message.content
    return last_message.content
