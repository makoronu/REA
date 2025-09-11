# scripts/auto_spec_generator/table_detail_generator.py
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, inspect, text
import json

class TableDetailGenerator:
    """分割済みテーブルの詳細仕様生成器"""
    
    def __init__(self):
        self.base_path = Path("/Users/yaguchimakoto/my_programing/REA")
        self.output_dir = self.base_path / "docs"
        self.db_url = "postgresql://rea_user:rea_password@localhost:5432/real_estate_db"
        self.engine = create_engine(self.db_url)
        
        # 分割済みテーブルの分類
        self.table_groups = {
            'core': {
                'tables': ['properties'],
                'icon': '🏢',
                'title': '基本情報',
                'description': '物件の核となる基本情報'
            },
            'pricing': {
                'tables': ['properties_pricing'],
                'icon': '💰',
                'title': '価格・収益',
                'description': '価格・賃料・利回り等の収益情報'
            },
            'location': {
                'tables': ['properties_location', 'properties_transportation'],
                'icon': '📍',
                'title': '所在地・交通',
                'description': '住所・駅・交通アクセス情報'
            },
            'images': {
                'tables': ['properties_images'],
                'icon': '📸',
                'title': '画像管理',
                'description': '物件画像の管理・表示機能'
            },
            'building': {
                'tables': ['properties_building', 'properties_floor_plans'],
                'icon': '🏗️',
                'title': '建物情報',
                'description': '建物構造・間取り・仕様情報'
            },
            'contract': {
                'tables': ['properties_contract'],
                'icon': '📋',
                'title': '契約情報',
                'description': '契約条件・入居・取引情報'
            },
            'land': {
                'tables': ['properties_roads', 'properties_other'],
                'icon': '🏞️',
                'title': '土地・法令',
                'description': '土地情報・用途地域・法的制限'
            },
            'facilities': {
                'tables': ['properties_facilities'],
                'icon': '🏫',
                'title': '周辺施設',
                'description': '学校・病院・商業施設等の周辺環境'
            }
        }
    
    def generate_all_table_details(self):
        """全テーブルの詳細仕様を生成"""
        print("🚀 テーブル詳細仕様生成開始...")
        
        try:
            inspector = inspect(self.engine)
            
            # 各機能グループの詳細仕様生成
            for group_name, group_info in self.table_groups.items():
                print(f"📊 {group_info['icon']} {group_info['title']} 生成中...")
                self._generate_group_specs(group_name, group_info, inspector)
            
            # テーブル一覧の更新
            self._generate_tables_overview(inspector)
            
            print("✅ 全テーブル詳細仕様生成完了！")
            self._print_summary()
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_group_specs(self, group_name: str, group_info: dict, inspector):
        """機能グループの仕様生成"""
        # グループディレクトリ作成
        group_dir = self.output_dir / "01_database" / "tables" / group_name
        group_dir.mkdir(parents=True, exist_ok=True)
        
        # グループ概要生成
        self._generate_group_overview(group_name, group_info, group_dir)
        
        # 各テーブルの詳細仕様生成
        for table_name in group_info['tables']:
            if table_name in inspector.get_table_names():
                self._generate_single_table_detail(table_name, group_name, group_dir, inspector)
    
    def _generate_group_overview(self, group_name: str, group_info: dict, group_dir: Path):
        """機能グループ概要生成"""
        content = f"""# {group_info['icon']} {group_info['title']} テーブル群

## 📋 概要
{group_info['description']}

## 🗂️ 含まれるテーブル
"""
        
        for table_name in group_info['tables']:
            try:
                inspector = inspect(self.engine)
                if table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    record_count = self._get_record_count(table_name)
                    content += f"- [{table_name}]({table_name}.md) - {len(columns)}カラム, {record_count:,}レコード\n"
            except:
                content += f"- [{table_name}]({table_name}.md) - 詳細不明\n"
        
        content += f"""
## 🎯 主な用途
{self._get_group_usage(group_name)}

## 🔗 関連テーブル
{self._get_related_tables(group_name)}

## 🚀 よく使うクエリ例
{self._get_common_queries(group_name)}
"""
        
        with open(group_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_single_table_detail(self, table_name: str, group_name: str, group_dir: Path, inspector):
        """単一テーブルの詳細仕様生成"""
        columns = inspector.get_columns(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        # レコード数・サイズ取得
        record_count = self._get_record_count(table_name)
        table_size = self._get_table_size(table_name)
        
        content = f"""# {self.table_groups[group_name]['icon']} {table_name} テーブル詳細仕様

## 📋 基本情報
- **テーブル名**: `{table_name}`
- **機能グループ**: {self.table_groups[group_name]['title']}
- **レコード数**: {record_count:,}件
- **テーブルサイズ**: {table_size:.2f}MB
- **カラム数**: {len(columns)}

## 🎯 テーブルの役割
{self._get_table_purpose_detailed(table_name)}

## 📊 カラム詳細仕様

| No | カラム名 | データ型 | NULL | デフォルト | 説明 | 備考 |
|----|----------|----------|------|------------|------|------|
"""
        
        for i, column in enumerate(columns, 1):
            null_ok = "✅" if column['nullable'] else "❌"
            default = self._format_default(column.get('default'))
            description = self._get_column_description_detailed(table_name, column['name'])
            notes = self._get_column_notes(table_name, column['name'])
            
            content += f"| {i} | `{column['name']}` | {column['type']} | {null_ok} | {default} | {description} | {notes} |\n"
        
        # 制約情報
        content += self._generate_constraints_section(table_name, foreign_keys, indexes)
        
        # 使用例
        content += self._generate_usage_examples(table_name, group_name)
        
        # パフォーマンス情報
        content += self._generate_performance_info(table_name)
        
        # API連携情報
        content += self._generate_api_integration_info(table_name, group_name)
        
        with open(group_dir / f"{table_name}.md", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ {table_name} 詳細仕様生成完了")
    
    def _generate_constraints_section(self, table_name: str, foreign_keys: list, indexes: list) -> str:
        """制約・インデックス情報セクション生成"""
        content = "\n## 🔗 制約・インデックス情報\n"
        
        # 外部キー
        if foreign_keys:
            content += "\n### 外部キー制約\n"
            for fk in foreign_keys:
                constraint_name = fk.get('name', 'unnamed')
                local_col = ', '.join(fk['constrained_columns'])
                foreign_col = f"{fk['referred_table']}.{', '.join(fk['referred_columns'])}"
                content += f"- **{constraint_name}**: `{local_col}` → `{foreign_col}`\n"
        
        # インデックス
        if indexes:
            content += "\n### インデックス\n"
            for idx in indexes:
                idx_type = "UNIQUE" if idx.get('unique') else "INDEX"
                columns = ', '.join(idx['column_names'])
                content += f"- **{idx['name']}** ({idx_type}): `{columns}`\n"
        
        return content
    
    def _generate_usage_examples(self, table_name: str, group_name: str) -> str:
        """使用例セクション生成"""
        content = "\n## 💾 使用例\n"
        
        examples = self._get_usage_examples_by_table(table_name, group_name)
        
        for example_title, sql_code in examples.items():
            content += f"\n### {example_title}\n```sql\n{sql_code}\n```\n"
        
        return content
    
    def _generate_performance_info(self, table_name: str) -> str:
        """パフォーマンス情報セクション生成"""
        content = "\n## 📈 パフォーマンス情報\n"
        
        # 基本統計
        record_count = self._get_record_count(table_name)
        table_size = self._get_table_size(table_name)
        
        content += f"- **レコード数**: {record_count:,}件\n"
        content += f"- **テーブルサイズ**: {table_size:.2f}MB\n"
        content += f"- **平均レコードサイズ**: {(table_size * 1024 * 1024 / max(record_count, 1)):.0f}bytes\n"
        
        # クエリパフォーマンス推定
        if record_count > 10000:
            content += "- **注意**: 大量データのため、WHERE句とインデックスの使用を推奨\n"
        elif record_count > 1000:
            content += "- **推奨**: 効率的な検索のためインデックス使用を推奨\n"
        else:
            content += "- **状況**: 小規模データのため高速アクセス可能\n"
        
        return content
    
    def _generate_api_integration_info(self, table_name: str, group_name: str) -> str:
        """API連携情報セクション生成"""
        content = "\n## 🔌 API連携情報\n"
        
        # 対応するAPIエンドポイント
        endpoints = self._get_related_api_endpoints(table_name, group_name)
        
        if endpoints:
            content += "### 関連APIエンドポイント\n"
            for endpoint in endpoints:
                content += f"- `{endpoint['method']} {endpoint['path']}` - {endpoint['description']}\n"
        
        # 使用例
        content += "\n### API使用例\n"
        content += f"```bash\n# {table_name} データ取得\n"
        content += f"curl http://localhost:8005/api/v1/{group_name}/\n```\n"
        
        return content
    
    def _get_record_count(self, table_name: str) -> int:
        """レコード数取得"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                return result.scalar()
        except:
            return 0
    
    def _get_table_size(self, table_name: str) -> float:
        """テーブルサイズ取得（MB）"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT pg_total_relation_size('{table_name}') / (1024.0 * 1024.0) as size_mb
                """))
                return result.scalar() or 0.0
        except:
            return 0.0
    
    def _format_default(self, default) -> str:
        """デフォルト値のフォーマット"""
        if default is None:
            return "-"
        return str(default)[:20] + "..." if len(str(default)) > 20 else str(default)
    
    def _get_table_purpose_detailed(self, table_name: str) -> str:
        """テーブルの詳細な役割説明"""
        purposes = {
            'properties': '物件の核となる基本情報を管理。他の全ての機能テーブルの基点となる重要なテーブル。',
            'properties_pricing': '物件の価格・賃料・利回り等の収益に関する情報を管理。投資判断に必要な数値データが集約されている。',
            'properties_location': '物件の住所・所在地情報を管理。郵便番号・住所・緯度経度等の位置特定に必要なデータを格納。',
            'properties_transportation': '物件の交通アクセス情報を管理。最寄り駅・路線・徒歩時間・バス情報等を格納。',
            'properties_images': '物件の画像情報を管理。外観・間取り・室内写真等の画像ファイルと関連情報を格納。',
            'properties_building': '建物の構造・仕様情報を管理。建築年・構造・階数・管理情報等の建物固有のデータを格納。',
            'properties_floor_plans': '物件の間取り詳細情報を管理。各部屋の種類・畳数・階数等の詳細な間取りデータを格納。',
            'properties_contract': '契約・取引に関する情報を管理。契約条件・入居時期・仲介手数料等の取引条件を格納。',
            'properties_facilities': '物件周辺の施設情報を管理。学校・病院・商業施設等への距離・アクセス情報を格納。',
            'properties_roads': '物件の接道情報を管理。道路の方向・幅員・種別等の法的要件に関わる重要なデータを格納。',
            'properties_other': 'その他の物件関連情報を管理。用途地域・地勢・法的制限等の分類困難な情報を格納。'
        }
        return purposes.get(table_name, 'このテーブルの詳細な用途は分析中です。')
    
    def _get_column_description_detailed(self, table_name: str, column_name: str) -> str:
        """カラムの詳細説明"""
        # column_labelsテーブルから日本語説明を取得
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT japanese_label, description 
                    FROM column_labels 
                    WHERE table_name = :table_name AND column_name = :column_name
                """), {"table_name": table_name, "column_name": column_name})
                row = result.fetchone()
                if row:
                    return row.description or row.japanese_label
        except:
            pass
        
        # フォールバック: カラム名から推測
        return self._infer_column_description(column_name)
    
    def _get_column_notes(self, table_name: str, column_name: str) -> str:
        """カラムの備考・注意事項"""
        # 特別な注意が必要なカラム
        special_notes = {
            'id': 'プライマリーキー',
            'property_id': '外部キー',
            'created_at': '自動設定',
            'updated_at': '自動更新',
            'homes_record_id': 'ホームズ連携用',
            'price': '円単位',
            'yield': '%単位'
        }
        
        return special_notes.get(column_name, '')
    
    def _infer_column_description(self, column_name: str) -> str:
        """カラム名から説明を推測"""
        descriptions = {
            'id': 'レコード識別ID',
            'property_id': '物件ID（外部キー）',
            'price': '価格・賃料',
            'address': '住所',
            'name': '名称',
            'type': '種別・タイプ',
            'date': '日付',
            'created_at': '作成日時',
            'updated_at': '更新日時'
        }
        
        for key, desc in descriptions.items():
            if key in column_name.lower():
                return desc
        
        return '詳細説明は準備中'
    
    def _get_group_usage(self, group_name: str) -> str:
        """グループの主な用途"""
        usages = {
            'core': '- 物件の基本識別・管理\n- 他テーブルとの関連付けの基点\n- 物件一覧表示での基本情報提供',
            'pricing': '- 物件価格・賃料の管理\n- 投資収益計算・利回り算出\n- 価格帯での物件検索・絞り込み',
            'location': '- 物件所在地の特定・表示\n- 地域・駅での物件検索\n- 地図表示・ルート案内',
            'images': '- 物件画像の保存・管理\n- 画像ギャラリーの表示\n- 画像の分類・最適化',
            'building': '- 建物仕様の詳細表示\n- 建築情報による検索・絞り込み\n- 管理・メンテナンス情報の管理',
            'contract': '- 契約条件の管理・表示\n- 入居時期・取引条件の確認\n- 仲介手数料・契約期間の管理',
            'land': '- 土地の法的情報管理\n- 用途地域・接道による検索\n- 建築可能性の判断材料',
            'facilities': '- 周辺環境の評価・表示\n- 生活利便性による物件評価\n- ファミリー向け物件の訴求'
        }
        return usages.get(group_name, '用途の詳細は分析中です。')
    
    def _get_related_tables(self, group_name: str) -> str:
        """関連テーブルの説明"""
        relations = {
            'core': '- 全ての properties_* テーブルから参照される中心テーブル',
            'pricing': '- properties（基本情報）\n- properties_building（建物情報から利回り計算）',
            'location': '- properties（基本情報）\n- properties_transportation（交通情報と連携）',
            'images': '- properties（基本情報）\n- image_types（画像種別マスター）',
            'building': '- properties（基本情報）\n- building_structure（建物構造マスター）',
            'contract': '- properties（基本情報）\n- current_status（現況マスター）',
            'land': '- properties（基本情報）\n- zoning_districts（用途地域マスター）',
            'facilities': '- properties（基本情報）'
        }
        return relations.get(group_name, '関連性の詳細は分析中です。')
    
    def _get_common_queries(self, group_name: str) -> str:
        """よく使うクエリ例"""
        queries = {
            'core': '''```sql
-- 物件基本情報取得
SELECT * FROM properties WHERE id = 12345;

-- 物件一覧（ページング）
SELECT id, building_property_name FROM properties 
ORDER BY id LIMIT 20 OFFSET 0;
```''',
            'pricing': '''```sql
-- 価格帯での検索
SELECT p.*, pp.price FROM properties p
JOIN properties_pricing pp ON p.id = pp.property_id
WHERE pp.price BETWEEN 100000 AND 200000;

-- 利回り順での並び替え
SELECT * FROM properties_pricing 
ORDER BY yield DESC LIMIT 10;
```''',
            'location': '''```sql
-- 住所での検索
SELECT * FROM properties_location 
WHERE address_name LIKE '%新宿%';

-- 緯度経度での範囲検索
SELECT * FROM properties_location 
WHERE latitude_longitude IS NOT NULL;
```''',
            'images': '''```sql
-- 物件の画像一覧
SELECT * FROM properties_images 
WHERE property_id = 12345 
ORDER BY image_order;

-- 特定種別の画像
SELECT * FROM properties_images 
WHERE image_type_1 = '外観';
```'''
        }
        return queries.get(group_name, '```sql\n-- 使用例は準備中\n```')
    
    def _get_usage_examples_by_table(self, table_name: str, group_name: str) -> dict:
        """テーブル別の使用例"""
        examples = {
            'properties': {
                '基本検索': f'SELECT * FROM {table_name} WHERE id = 12345;',
                '一覧取得': f'SELECT id, building_property_name FROM {table_name} ORDER BY id;'
            },
            'properties_pricing': {
                '価格範囲検索': f'SELECT * FROM {table_name} WHERE price BETWEEN 100000 AND 200000;',
                '利回り上位': f'SELECT * FROM {table_name} ORDER BY yield DESC LIMIT 10;'
            },
            'properties_images': {
                '物件画像一覧': f'SELECT * FROM {table_name} WHERE property_id = 12345;',
                '画像種別絞り込み': f'SELECT * FROM {table_name} WHERE image_type_1 = \'外観\';'
            }
        }
        
        return examples.get(table_name, {
            '基本操作': f'SELECT * FROM {table_name} WHERE property_id = 12345;'
        })
    
    def _get_related_api_endpoints(self, table_name: str, group_name: str) -> list:
        """関連APIエンドポイント"""
        endpoints = {
            'properties': [
                {'method': 'GET', 'path': '/api/v1/properties/', 'description': '物件一覧取得'},
                {'method': 'POST', 'path': '/api/v1/properties/', 'description': '物件作成'},
                {'method': 'GET', 'path': '/api/v1/properties/{id}', 'description': '物件詳細取得'}
            ],
            'properties_pricing': [
                {'method': 'GET', 'path': '/api/v1/properties/{id}/pricing', 'description': '価格情報取得'},
                {'method': 'PUT', 'path': '/api/v1/properties/{id}/pricing', 'description': '価格情報更新'}
            ],
            'properties_images': [
                {'method': 'GET', 'path': '/api/v1/properties/{id}/images', 'description': '画像一覧取得'},
                {'method': 'POST', 'path': '/api/v1/properties/{id}/images', 'description': '画像アップロード'}
            ]
        }
        
        return endpoints.get(table_name, [])
    
    def _generate_tables_overview(self, inspector):
        """テーブル一覧概要の更新"""
        content = f"""# 📊 REAデータベース テーブル一覧

## 📋 生成情報
- **生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **総テーブル数**: {len(inspector.get_table_names())}
- **機能グループ数**: {len(self.table_groups)}

## 🗂️ 機能別テーブル構成

"""
        
        for group_name, group_info in self.table_groups.items():
            content += f"### {group_info['icon']} {group_info['title']}\n"
            content += f"{group_info['description']}\n\n"
            
            for table_name in group_info['tables']:
                if table_name in inspector.get_table_names():
                    columns = inspector.get_columns(table_name)
                    record_count = self._get_record_count(table_name)
                    content += f"- [{table_name}]({group_name}/{table_name}.md) - {len(columns)}カラム, {record_count:,}レコード\n"
            
            content += "\n"
        
        # 機能別ディレクトリ作成
        tables_dir = self.output_dir / "01_database" / "tables"
        tables_dir.mkdir(parents=True, exist_ok=True)
        
        with open(tables_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _print_summary(self):
        """生成結果サマリー表示"""
        print("\n📋 テーブル詳細仕様生成結果:")
        print("─────────────────────────────")
        
        total_files = 0
        for group_name, group_info in self.table_groups.items():
            group_dir = self.output_dir / "01_database" / "tables" / group_name
            if group_dir.exists():
                md_files = list(group_dir.glob("*.md"))
                total_files += len(md_files)
                print(f"{group_info['icon']} {group_info['title']}: {len(md_files)}ファイル")
        
        print(f"\n📄 総生成ファイル数: {total_files}")
        print("\n🎯 次のステップ:")
        print("   1. docs/01_database/tables/ の内容確認")
        print("   2. Day 2: Claude用チャンク生成")
        print("   3. Day 3: リレーション・パフォーマンス分析")

if __name__ == "__main__":
    generator = TableDetailGenerator()
    generator.generate_all_table_details()