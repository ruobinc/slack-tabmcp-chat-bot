import os
from langchain_aws import ChatBedrockConverse
from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent

_agent = None


def get_agent():
    """DeepAgentのシングルトンインスタンスを返す。"""
    global _agent
    if _agent is not None:
        return _agent

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
        system_prompt="あなたは親切な日本語アシスタントです。簡潔で分かりやすい回答をしてください。",
        checkpointer=checkpointer,
        subagents=[],
        name="slack-bot-agent",
    )
    return _agent


def invoke_agent(message: str, thread_id: str) -> str:
    """DeepAgentを呼び出してテキスト応答を返す。"""
    agent = get_agent()
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
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
