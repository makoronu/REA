"""
エラーメッセージ定数

ADR-0001に基づき、エラーメッセージを定数ファイルで一元管理。
メタデータ駆動ではなく定数化の理由:
- 開発者のみが変更
- 変更頻度が年1回以下
- 変更時にテストが必要
"""


class ErrorMessages:
    """HTTPエラーメッセージ定数"""

    # 認証・認可（401, 403）
    AUTH_REQUIRED = "認証が必要です"
    INVALID_CREDENTIALS = "メールアドレスまたはパスワードが正しくありません"
    ACCOUNT_DISABLED = "アカウントが無効です"
    ADMIN_REQUIRED = "管理者権限が必要です"

    # トークン関連（400）
    INVALID_TOKEN = "無効なトークンです"
    TOKEN_ALREADY_USED = "このトークンは既に使用されています"
    TOKEN_EXPIRED = "トークンの有効期限が切れています"

    # リソース未検出（404）
    PROPERTY_NOT_FOUND = "物件が見つかりません"
    USER_NOT_FOUND = "ユーザーが見つかりません"
    REGISTRY_NOT_FOUND = "登記情報が見つかりません"
    TITLE_SECTION_NOT_FOUND = "表題部が見つかりません"
    KOU_ENTRY_NOT_FOUND = "甲区エントリが見つかりません"
    OTSU_ENTRY_NOT_FOUND = "乙区エントリが見つかりません"
    INTEGRATION_NOT_FOUND = "連携先が見つかりません"
    MAPPING_FILE_NOT_FOUND = "マッピングファイルが見つかりません"

    # バリデーション（400）
    PROPERTY_NAME_REQUIRED = "物件名は必須です"
    PROPERTY_NAME_NULL_FORBIDDEN = "物件名をnullにすることはできません"
    PUBLICATION_STATUS_NULL_FORBIDDEN = "公開ステータスをnullにすることはできません"
    NO_UPDATE_DATA = "更新データがありません"
    EMAIL_ALREADY_EXISTS = "このメールアドレスは既に登録されています"
    CANNOT_DELETE_SELF = "自分自身は削除できません"
    PROPERTY_IDS_REQUIRED = "物件IDの指定が必要です"
    LAT_LON_NOT_SET = "物件に緯度経度が設定されていません"

    # 連携先関連（400）
    INTEGRATION_DISABLED = "連携先が無効です"
    INTEGRATION_ENDPOINT_NOT_SET = "同期エンドポイントが設定されていません"

    # 外部サービス（500, 502）
    GEOCODE_FAILED = "住所から座標を取得できませんでした"
    REGULATION_FETCH_FAILED = "規制情報の取得に失敗しました"
    ZONE_FETCH_FAILED = "用途地域の取得に失敗しました"
    HAZARD_FETCH_FAILED = "ハザード情報の取得に失敗しました"
    TILE_FETCH_FAILED = "タイルデータの取得に失敗しました"
    PRICE_FETCH_FAILED = "価格情報の取得に失敗しました"
    MAISOKU_GENERATION_FAILED = "マイソク生成に失敗しました"
    FLYER_GENERATION_FAILED = "チラシ生成に失敗しました"
    TEMPLATE_LIST_FAILED = "テンプレート一覧の取得に失敗しました"
    PREVIEW_GENERATION_FAILED = "プレビュー生成に失敗しました"

    # 汎用（500）
    DELETE_FAILED = "削除に失敗しました"
    CONFIG_FILE_ERROR = "設定ファイルエラー"


# フォーマット付きメッセージ用
def integration_not_found(code: str) -> str:
    """連携先未検出メッセージ"""
    return f"連携先 {code} が見つかりません"


def integration_disabled(code: str) -> str:
    """連携先無効メッセージ"""
    return f"連携先 {code} は無効です"


def integration_endpoint_not_set(code: str) -> str:
    """連携先エンドポイント未設定メッセージ"""
    return f"連携先 {code} の同期エンドポイントが設定されていません"


def geocode_failed(address: str) -> str:
    """ジオコード失敗メッセージ"""
    return f"住所から座標を取得できませんでした: {address}"
