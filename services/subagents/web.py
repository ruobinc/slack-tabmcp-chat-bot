from langchain_tavily import TavilySearch

WEB_DESCRIPTION = (
    "インターネットで最新情報を検索する。"
    "Tableauやslack以外の外部情報、業界ニュース、"
    "一般知識の補足が必要な場合に使う。"
)

WEB_SYSTEM_PROMPT = """\
あなたはWebリサーチャーです。
Tavily検索ツールでインターネットから最新情報を収集します。

## ルール
- ツール呼び出しは最大3回以内で完了すること
- 信頼性の高いソースを優先し、情報源を明記する
- 日本語で回答する"""


def build_web_subagent():
    """Web検索SubAgent定義を構築する。"""
    return {
        "name": "web-researcher",
        "description": WEB_DESCRIPTION,
        "system_prompt": WEB_SYSTEM_PROMPT,
        "tools": [TavilySearch(max_results=5)],
    }
