def generate_reply(text: str) -> str:
    """ユーザーのメッセージに対する回答を生成する。
    現在は固定文字列を返す。将来的にLLM連携に置き換える。
    """
    return f"メッセージを受け取りました: {text}"
