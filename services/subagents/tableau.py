TABLEAU_DESCRIPTION = (
    "Tableauのデータを取得・分析し、インサイトやアクション提案を行う。"
    "データソースへのクエリやメタデータ確認が必要な場合に使う。"
)

TABLEAU_SYSTEM_PROMPT = """\
あなたはTableauデータアナリストです。
Tableau MCPツールでデータを取得し、質問に回答します。

## ルール
- ツール呼び出しは最大5回以内で完了すること（エラー時のリトライ含む）
- ツールエラーが返ってきたら、クエリを修正して1回だけリトライする。2回連続で同じエラーなら諦めてエラー内容をユーザーに報告する
- 1回のquery-datasourceで可能な限り多くの情報を取得する（集計・フィルタを活用）
- データに基づかない推測は行わず、取得した事実に基づいて回答する
- 結果は日本語で簡潔に"""

TABLEAU_ALLOWED_TOOLS = {
    "list-datasources",
    "get-datasource-metadata",
    "query-datasource",
}


def _tableau_error_handler(e: Exception) -> str:
    """Tableauツールエラーをリトライのヒント付きメッセージに変換する。"""
    msg = str(e)
    hint = ""
    if "AGG" in msg and ("REAL" in msg or "FLOAT" in msg or "INT" in msg):
        hint = "\n[ヒント] 数値型フィールドにはAGG()を使わず、SUM()/AVG()/MIN()/MAX()を指定してください。"
    elif "validation" in msg.lower():
        hint = "\n[ヒント] クエリの構文やフィールド型を確認し、get-datasource-metadataで正しい型を確認してください。"
    return f"ツールエラー: {msg}{hint}"


def build_tableau_subagent(tools):
    """Tableau MCPツール群からSubAgent定義を構築する。"""
    filtered = [t for t in tools if t.name in TABLEAU_ALLOWED_TOOLS]
    for t in filtered:
        t.handle_tool_error = _tableau_error_handler
    return {
        "name": "tableau-analyst",
        "description": TABLEAU_DESCRIPTION,
        "system_prompt": TABLEAU_SYSTEM_PROMPT,
        "tools": filtered,
    }
