from langchain_tavily import TavilySearch

WEB_DESCRIPTION = (
    "インターネットで最新情報を検索する。"
    "Tableauやslack以外の外部情報、業界ニュース、"
    "一般知識の補足が必要な場合に使う。"
)

WEB_SYSTEM_PROMPT = """\
あなたはWebリサーチャーです。
Tavily検索ツールを使ってインターネットから最新情報を収集します。

## 作業フロー
1. ユーザーの質問に適した検索クエリを作成する
2. 検索結果を分析して関連情報を抽出する
3. 情報源を明記して要約を作成する

## 注意事項
- 信頼性の高いソースを優先する
- 検索結果の日付に注意し、最新情報かどうか確認する
- 日本語で回答する"""


def build_web_subagent():
    """Web検索SubAgent定義を構築する。"""
    return {
        "name": "web-researcher",
        "description": WEB_DESCRIPTION,
        "system_prompt": WEB_SYSTEM_PROMPT,
        "tools": [TavilySearch(max_results=5)],
    }
