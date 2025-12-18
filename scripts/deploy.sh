#!/bin/bash
#
# REA 本番デプロイスクリプト
# 使い方: ./scripts/deploy.sh
#
set -e  # エラーで即停止

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 設定
SERVER="rea-conoha"
REMOTE_DIR="/opt/REA"
BACKUP_DIR="/tmp/rea_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================"
echo "REA 本番デプロイ"
echo "========================================"
echo ""

# 1. ローカルのテスト
echo_info "1/7 ローカルTypeScriptチェック..."
cd ~/my_programing/REA/rea-admin
npx tsc --noEmit || { echo_error "TypeScriptエラー。デプロイ中止。"; exit 1; }
echo_info "TypeScript OK"

# 2. 未コミットの変更確認
echo_info "2/7 未コミット変更の確認..."
cd ~/my_programing/REA
if [[ -n $(git status --porcelain) ]]; then
    echo_warn "未コミットの変更があります:"
    git status --short
    read -p "続行しますか？ (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo_error "デプロイ中止"
        exit 1
    fi
fi

# 3. git push
echo_info "3/7 リモートにプッシュ..."
git push origin main || { echo_error "git push失敗"; exit 1; }

# 4. 本番DBバックアップ
echo_info "4/7 本番DBバックアップ..."
ssh $SERVER "mkdir -p $BACKUP_DIR && sudo -u postgres pg_dump real_estate_db > $BACKUP_DIR/backup_$TIMESTAMP.sql"
echo_info "バックアップ: $BACKUP_DIR/backup_$TIMESTAMP.sql"

# 5. 本番コード更新
echo_info "5/7 本番コード更新..."
ssh $SERVER "cd $REMOTE_DIR && git pull origin main"

# 6. フロントエンドビルド
echo_info "6/7 フロントエンドビルド..."
ssh $SERVER "cd $REMOTE_DIR/rea-admin && npm install && npm run build"

# 7. API再起動
echo_info "7/7 API再起動..."
ssh $SERVER "sudo systemctl restart rea-api"

# ヘルスチェック
echo_info "ヘルスチェック中..."
sleep 3
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://realestateautomation.net/api/v1/health)
if [[ "$HEALTH" == "200" ]]; then
    echo_info "ヘルスチェック OK (HTTP $HEALTH)"
else
    echo_error "ヘルスチェック失敗 (HTTP $HEALTH)"
    echo_warn "ロールバックが必要な場合:"
    echo "  ssh $SERVER \"cat $BACKUP_DIR/backup_$TIMESTAMP.sql | sudo -u postgres psql real_estate_db\""
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN}デプロイ完了${NC}"
echo "========================================"
echo "バックアップ: $BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "確認: https://realestateautomation.net/"
