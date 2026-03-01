# コミット

## やること

### Step 1: Contaboからローカルに同期
Contaboはgitリポジトリではないため、ファイルをローカルにダウンロードする。
```bash
mkdir -p ~/my_programing/market-intelligence/mi-scraper/src/sites/{site_name}/
scp rea-contabo:/opt/market-intelligence/mi-scraper/src/sites/{site_name}/*.py \
    ~/my_programing/market-intelligence/mi-scraper/src/sites/{site_name}/
```

### Step 2: ローカルでgitコミット
```bash
cd ~/my_programing/market-intelligence
git status
git add mi-scraper/src/sites/{site_name}/ CLAUDE.md
git commit
```

## 完了条件
- [ ] ローカルのファイルがContaboと一致している
- [ ] コミットした

## 次 → log.md
