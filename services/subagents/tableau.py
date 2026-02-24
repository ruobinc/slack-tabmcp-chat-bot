TABLEAU_DESCRIPTION = (
    "Tableauのデータを取得・分析し、インサイトやアクション提案を行う。"
    "データソースへのクエリやメタデータ確認が必要な場合に使う。"
)

TABLEAU_SYSTEM_PROMPT = """\
あなたはTableauデータアナリストです。
Tableau MCPツールでデータを取得し、質問に回答します。

## ルール
- ツール呼び出しは最大5回以内で完了すること
- 1回のquery-datasourceで可能な限り多くの情報を取得する（集計・フィルタを活用）
- データに基づかない推測は行わず、取得した事実に基づいて回答する
- 結果は日本語で簡潔に"""

TABLEAU_ALLOWED_TOOLS = {
    "list-datasources",
    "get-datasource-metadata",
    "query-datasource",
}


def build_tableau_subagent(tools):
    """Tableau MCPツール群からSubAgent定義を構築する。"""
    filtered = [t for t in tools if t.name in TABLEAU_ALLOWED_TOOLS]
    return {
        "name": "tableau-analyst",
        "description": TABLEAU_DESCRIPTION,
        "system_prompt": TABLEAU_SYSTEM_PROMPT,
        "tools": filtered,
    }
