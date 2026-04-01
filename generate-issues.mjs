/**
 * Issue generator for ai-stress-test
 * Quality-first: each issue includes test requirements from the checklist
 * Categories: utility, parser, algorithm, game, data-structure, api, tool
 */
import { execSync } from 'child_process';
import { writeFileSync, mkdirSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const REPO = 'muumuu8181/ai-stress-test';
const LABEL = 'jules';
const DRY_RUN = process.argv.includes('--dry-run');
const TMP = tmpdir();

function gh(cmd) {
  if (DRY_RUN) {
    console.log(`[DRY] gh ${cmd}`);
    return;
  }
  return execSync(`gh ${cmd}`, { encoding: 'utf8', shell: 'bash' });
}

// Quality template appended to every issue
const qualityTemplate = `
### 品質要件（必須）

**テスト:**
- 全パブリック関数のユニットテスト（正常系+異常系+境界値）
- インテグレーションテスト（コンポーネント間連携）
- エッジケースのテスト（空入力、NULL、境界値、不正入力）
- テストカバレッジ80%以上を目標
- pytest または jest/vitest を使用

**コード品質:**
- 型ヒント/TypeScript型を全パブリックAPIに付与
- docstring/JSDoc を全パブリック関数に記載
- README.md に使用例を含める

**提出前確認:**
- テストランナーを実行して全テストパスを確認
- リンター/フォーマッターを通す
`;

const components = [
  // === Utility Tools (Python) ===
  {
    id: '001-cron-parser',
    dir: '001-cron-parser',
    lang: 'Python',
    title: 'Cron Expression Parser & Validator',
    body: `外部ライブラリを使わず、Pythonでcron式のパーサー・バリデーターを構築してください。

### 機能要件
- cron式（5フィールド: 分 時 日 月 曜日）のパース
- 次回実行時刻の計算（基準時刻を指定可能）
- 式のバリデーション（不正な値・範囲外の検出）
- 特殊文字対応: *, ?, -, /, ,(カンマ区切り), L, W, #
- 人間が読める形式への変換（例: "0 9 * * 1-5" → "平日の9:00"）

### パッケージ構成
\`\`\`
components/001-cron-parser/
  src/cronparser/
    __init__.py
    lexer.py
    parser.py
    calculator.py
    formatter.py
  tests/
    test_parser.py
    test_calculator.py
    test_formatter.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '002-template-engine',
    dir: '002-template-engine',
    lang: 'Python',
    title: 'Template Engine (Jinja-like subset)',
    body: `Python標準ライブラリのみで、シンプルなテンプレートエンジンを構築してください。

### 機能要件
- 変数展開: {{ variable }}, {{ user.name }}
- 条件分岐: {% if %} / {% elif %} / {% else %} / {% endif %}
- ループ: {% for item in items %} / {% endfor %}
- フィルター: {{ name | upper }}, {{ price | currency }}, {{ items | join(", ") }}
- テンプレート継承: {% extends "base.html" %} / {% block content %}
- コメント: {# comment #}
- HTMLエスケープ: 自動エスケープ + {{ raw | safe }}

### エラー処理
- 未定義変数アクセス時のエラーメッセージ（行番号付き）
- 構文エラーの行・列報告
- テンプレートが見つからない場合のエラー

### パッケージ構成
\`\`\`
components/002-template-engine/
  src/templateengine/
    __init__.py
    lexer.py
    parser.py
    engine.py
    filters.py
    nodes.py
  tests/
    test_lexer.py
    test_parser.py
    test_engine.py
    test_filters.py
    test_inheritance.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '003-markdown-parser',
    dir: '003-markdown-parser',
    lang: 'Python',
    title: 'Markdown to HTML Converter',
    body: `Python標準ライブラリのみで、Markdown→HTML変換器を構築してください。

### 機能要件
- 見出し: # ~ ######
- 段落・改行
- 強調: **bold**, *italic*, ~~strike~~, \`code\`
- リンク: [text](url), 画像: ![alt](url)
- リスト: 順序付き/なし、ネスト対応
- コードブロック: \`\`\`言語指定付き
- 引用: > 引用文
- テーブル: | header | header |
- 水平線: ---, ***
- HTML出力

### パッケージ構成
\`\`\`
components/003-markdown-parser/
  src/md2html/
    __init__.py
    lexer.py
    parser.py
    renderer.py
    nodes.py
  tests/
    test_lexer.py
    test_parser.py
    test_renderer.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '004-csv-toolkit',
    dir: '004-csv-toolkit',
    lang: 'Python',
    title: 'CSV Processing Toolkit',
    body: `Python標準ライブラリのみで、高度なCSV処理ツールキットを構築してください。

### 機能要件
- CSV/TSV読み書き（自動区切り文字検出）
- カラム選択・フィルタリング・ソート
- 集約: groupby + sum/avg/min/max/count
- JOIN: 2つのCSVをキーカラムで結合（INNER/LEFT）
- 型推論: 数値・日付・真偽値を自動検出
- スキーマ定義とバリデーション
- 大きなファイル対応（ストリーミング処理）

### CLI
\`\`\`bash
python -m csvtool select --columns name,age data.csv
python -m csvtool filter --where "age > 20" data.csv
python -m csvtool join --on id left.csv right.csv
python -m csvtool stats data.csv
\`\`\`

### パッケージ構成
\`\`\`
components/004-csv-toolkit/
  src/csvtool/
    __init__.py
    __main__.py
    reader.py
    writer.py
    filter.py
    aggregator.py
    joiner.py
    schema.py
    types.py
  tests/
    test_reader.py
    test_writer.py
    test_filter.py
    test_aggregator.py
    test_joiner.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '005-json-path',
    dir: '005-json-path',
    lang: 'Python',
    title: 'JSONPath Query Engine',
    body: `Python標準ライブラリのみで、JSONPathクエリエンジンを構築してください。

### 機能要件
- 基本パス: \$.store.book[0].title
- 配列インデックス: [0], [-1], [0:5], [:3]
- ワイルドカード: \$.store.book[*].author
- フィルター: \$.book[?(@.price < 10)]
- 再帰下降: \$..author
- 複数セレクタ: \$['store', 'office']
- スクリプト: [?(@.length > 5)]
- 結果の更新・削除

### パッケージ構成
\`\`\`
components/005-json-path/
  src/jsonpath/
    __init__.py
    lexer.py
    parser.py
    evaluator.py
    nodes.py
  tests/
    test_lexer.py
    test_parser.py
    test_evaluator.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  // === Data Structures ===
  {
    id: '006-btree',
    dir: '006-btree',
    lang: 'Python',
    title: 'B-Tree Implementation',
    body: `Python標準ライブラリのみで、B木を実装してください。

### 機能要件
- 挿入・検索・削除
- オーダー（最小次数）をコンストラクタで指定可能
- レンジクエリ: 指定範囲のキーを全て取得
- イテレータサポート: in-order traversal
- ノードのダンプ（デバッグ用）
- シリアライズ/デシリアライズ（JSON形式で永続化）

### テスト要件
- 全操作の正常系
- 削除後の再平衡を確認（マージ・再分配）
- レンジクエリの境界値
- 大量データ（10,000件）での挿入・検索性能確認
- 重複キーの処理
${qualityTemplate}`
  },
  {
    id: '007-lru-cache',
    dir: '007-lru-cache',
    lang: 'Python',
    title: 'LRU Cache with TTL',
    body: `Python標準ライブラリのみで、TTL付きLRUキャッシュを実装してください。

### 機能要件
- get(key) / put(key, value, ttl=None)
- デフォルトTTL、キーごとのカスタムTTL
- 容量制限（超過時の自動退避）
- キャッシュ統計: hit_rate, miss_count, eviction_count
- スレッドセーフ（threading.Lock使用）
- イベントコールバック: on_evict, on_expire
- persist()/restore(): ディスクへの保存・復元

### テスト要件
- TTL期限切れの正確な判定
- 並行アクセスでの安全性
- メモリリークの確認（大量put後に適切に解放されるか）
${qualityTemplate}`
  },
  {
    id: '008-graph-lib',
    dir: '008-graph-lib',
    lang: 'Python',
    title: 'Graph Algorithm Library',
    body: `Python標準ライブラリのみで、グラフアルゴリズムライブラリを構築してください。

### 機能要件
- グラフ構築: 有向/無向、重み付き/なし
- 探索: BFS, DFS
- 最短経路: Dijkstra, Bellman-Ford
- 最小全域木: Kruskal, Prim
- トポロジカルソート
- 連結成分の検出
- サイクル検出
- 隣接リスト/隣接行列の両表現

### パッケージ構成
\`\`\`
components/008-graph-lib/
  src/graphlib/
    __init__.py
    graph.py
    search.py
    shortest_path.py
    mst.py
    topology.py
  tests/
    test_graph.py
    test_search.py
    test_shortest_path.py
    test_mst.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  // === Parsers & Compilers ===
  {
    id: '009-regex-engine',
    dir: '009-regex-engine',
    lang: 'Python',
    title: 'Regex Engine (NFA-based)',
    body: `Python標準ライブラリのみで、正規表現エンジンをNFAベースで構築してください。

### 機能要件
- 基本パターン: リテラル、., ^, $
- 量指定子: *, +, ?, {n,m}
- 文字クラス: [abc], [a-z], [^abc], \\d, \\w, \\s
- グループ: (abc), キャプチャグループ
- 選択: a|b
- エスケープ: \\\\, \\., \\*
- match(), search(), findall(), sub()
- マッチオブジェクト: グループ参照

### パッケージ構成
\`\`\`
components/009-regex-engine/
  src/regexengine/
    __init__.py
    lexer.py
    parser.py
    nfa.py
    matcher.py
  tests/
    test_lexer.py
    test_parser.py
    test_matcher.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '010-toml-parser',
    dir: '010-toml-parser',
    lang: 'Python',
    title: 'TOML Parser & Writer',
    body: `Python標準ライブラリのみで、TOMLパーサー・ライターを構築してください。

### 機能要件
- TOML v1.0仕様準拠
- キー・バリュー, テーブル, テーブル配列
- データ型: 文字列, 整数, 浮動小数点, 真偽値, 日付時刻, 配列, インラインテーブル
- マルチライン文字列, リテラル文字列
- ドット付きキー: physical.color = "orange"
- TOML→dict, dict→TOML変換
- バリデーション（重複キー検出など）

### パッケージ構成
\`\`\`
components/010-toml-parser/
  src/tomlparser/
    __init__.py
    lexer.py
    parser.py
    writer.py
    datetime_util.py
  tests/
    test_parser.py
    test_writer.py
    test_types.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  // === CLI Tools ===
  {
    id: '011-http-server',
    dir: '011-http-server',
    lang: 'Python',
    title: 'HTTP Server from Scratch',
    body: `Python標準ライブラリのみ（http.server除く）、ソケットレベルからHTTPサーバーを構築してください。

### 機能要件
- HTTP/1.1対応: GET, POST, PUT, DELETE, HEAD
- ルーティング: パス・メソッドベース
- リクエストパース: ヘッダー、ボディ、クエリパラメータ
- レスポンス構築: ステータスコード、ヘッダー、ボディ
- 静的ファイル配信（MIMEタイプ判定）
- JSON API サポート
- ミドルウェア: ロギング、CORS、認証
- マルチスレッド対応

### パッケージ構成
\`\`\`
components/011-http-server/
  src/httpserver/
    __init__.py
    __main__.py
    server.py
    request.py
    response.py
    router.py
    middleware.py
    static.py
  tests/
    test_request.py
    test_response.py
    test_router.py
    test_server.py
    test_integration.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '012-task-runner',
    dir: '012-task-runner',
    lang: 'Python',
    title: 'Task Runner (Make-like)',
    body: `Python標準ライブラリのみで、Make風タスクランナーを構築してください。

### 機能要件
- YAML/DSL形式のタスク定義ファイル
- タスク間の依存関係（DAG）
- ファイルタイムスタンプベースの差分実行
- 変数と環境変数のサポート
- 並列実行（独立タスク）
- タスクのdry-runモード
- 進捗表示
- タスクの強制再実行

### CLI
\`\`\`bash
python -m taskrunner           # デフォルトタスク実行
python -m taskrunner build     # buildタスク実行
python -m taskrunner -l        # タスク一覧
python -m taskrunner -n build  # dry-run
\`\`\`
${qualityTemplate}`
  },
  // === Games ===
  {
    id: '013-sudoku-solver',
    dir: '013-sudoku-solver',
    lang: 'Python',
    title: 'Sudoku Solver & Generator',
    body: `Python標準ライブラリのみで、数独ソルバー・ジェネレーターを構築してください。

### 機能要件
- バックトラッキングによる解法
- 制約伝播（Constraint Propagation）の高速解法
- 複数解の列挙（全解モード）
- パズル生成（難易度指定: easy/medium/hard/expert）
- パズルのバリデーション
- ヒント機能（次の一手を返す）
- 盤面のpretty print
- ファイル入出力（.sdk形式）

### テスト要件
- 既知の解を持つパズルでの正解確認
- 解なしパズルの検出
- 生成パズルの一意解確認
- 最難パズル（17ヒント）の解法性能
${qualityTemplate}`
  },
  {
    id: '014-maze-gen',
    dir: '014-maze-gen',
    lang: 'Python',
    title: 'Maze Generator & Solver',
    body: `Python標準ライブラリのみで、迷路ジェネレーター・ソルバーを構築してください。

### 機能要件
- 生成アルゴリズム: 棒倒し法, 穴掘り法, Kruskal, Prim, Eller
- ソルバー: BFS（最短経路）, DFS, A*, 壁追従法
- 迷路のサイズ指定（幅×高さ）
- ASCII表示 + PNG画像出力（pngwriterまたはPBM形式）
- スタート・ゴール地点の指定
- 経路のステップ数表示
- 迷路のシリアライズ（JSON形式）

### テスト要件
- 全アルゴリズムで生成→解けることの確認
- 生成された迷路が正当であること（全セル到達可能）
- 最短経路の正確性
${qualityTemplate}`
  },
  // === Cryptography & Encoding ===
  {
    id: '015-encoding-toolkit',
    dir: '015-encoding-toolkit',
    lang: 'Python',
    title: 'Encoding & Hash Toolkit',
    body: `Python標準ライブラリのみ（hashlibは使用可）で、エンコーディング・ハッシュツールキットを構築してください。

### 機能要件
- Base64: エンコード/デコード（標準/URL-safe）
- URL エンコード/デコード
- Hex エンコード/デコード
- ROT13
- ハッシュ: MD5, SHA-1, SHA-256, HMAC
- CRC32 チェックサム
- 文字コード変換: UTF-8, Shift-JIS, EUC-JP
- ファイルのハッシュ計算（ストリーミング対応）

### CLI
\`\`\`bash
python -m enctool base64 encode "hello"
python -m enctool hash sha256 file.txt
python -m enctool detect file.bin  # 文字コード検出
\`\`\`
${qualityTemplate}`
  },
  // === Text Processing ===
  {
    id: '016-diff-engine',
    dir: '016-diff-engine',
    lang: 'Python',
    title: 'Diff Engine (unified diff)',
    body: `Python標準ライブラリのみで、差分エンジンを構築してください。

### 機能要件
- LCS（最長共通部分列）ベースの行差分
- 文字レベルの差分（インラインdiff）
- Unified diff形式の出力
- Side-by-side表示
- 差分統計: 追加/削除/変更行数
- パッチ適用: diffから元ファイルを復元
- 3-way merge（共通祖先 + 2つの変更）
- ディレクトリ差分（再帰的ファイル比較）

### パッケージ構成
\`\`\`
components/016-diff-engine/
  src/diffengine/
    __init__.py
    lcs.py
    diff.py
    patch.py
    merge.py
    format.py
  tests/
    test_lcs.py
    test_diff.py
    test_patch.py
    test_merge.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '017-search-engine',
    dir: '017-search-engine',
    lang: 'Python',
    title: 'Full-text Search Engine',
    body: `Python標準ライブラリのみで、全文検索エンジンを構築してください。

### 機能要件
- インverted indexの構築
- トークナイズ: 形態素解析風（N-gramベース）、空白分割
- ランキング: TF-IDF スコアリング
- ブーリアンクエリ: AND, OR, NOT
- フレーズ検索: "exact phrase"
- 前方一致・後方一致
- ドキュメントの追加・削除・更新
- 検索結果のハイライト
- インデックスの永続化（JSON）

### パッケージ構成
\`\`\`
components/017-search-engine/
  src/searchengine/
    __init__.py
    tokenizer.py
    index.py
    query.py
    ranker.py
    storage.py
  tests/
    test_tokenizer.py
    test_index.py
    test_query.py
    test_ranker.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  // === JavaScript/TypeScript Components ===
  {
    id: '018-reactive-store',
    dir: '018-reactive-store',
    lang: 'TypeScript',
    title: 'Reactive State Store (RxJS-like)',
    body: `外部ライブラリを使わず、TypeScriptでリアクティブステートストアを構築してください。

### 機能要件
- Observable / Observer パターン
- オペレーター: map, filter, reduce, debounce, throttle, merge, combineLatest
- BehaviorSubject, ReplaySubject
- ストア: dispatch(action) → reducer → state更新 → 通知
- ミドルウェアチェーン
- セレクター（メモ化付き）
- タイムトラベルデバッグ（状態履歴の記録・復元）

### パッケージ構成
\`\`\`
components/018-reactive-store/
  src/
    observable.ts
    subject.ts
    operators.ts
    store.ts
    middleware.ts
    selector.ts
    devtools.ts
  tests/
    observable.test.ts
    store.test.ts
    operators.test.ts
    devtools.test.ts
  README.md
  tsconfig.json
\`\`\`
${qualityTemplate}`
  },
  {
    id: '019-virtual-dom',
    dir: '019-virtual-dom',
    lang: 'TypeScript',
    title: 'Virtual DOM Engine',
    body: `外部ライブラリを使わず、TypeScriptでVirtual DOMエンジンを構築してください。

### 機能要件
- Virtual DOM ノードの作成（h関数/JSX風）
- diff アルゴリズム（効率的なパッチ生成）
- 実DOMへのパッチ適用
- キー付きリストの差分更新
- イベント委譲
- コンポーネント（関数コンポーネント + state）
- フラグメント対応
- SVG要素のサポート

### パッケージ構成
\`\`\`
components/019-virtual-dom/
  src/
    h.ts
    diff.ts
    patch.ts
    component.ts
    events.ts
    types.ts
  tests/
    h.test.ts
    diff.test.ts
    patch.test.ts
    component.test.ts
  README.md
  tsconfig.json
\`\`\`
${qualityTemplate}`
  },
  {
    id: '020-router',
    dir: '020-router',
    lang: 'TypeScript',
    title: 'Client-side Router',
    body: `外部ライブラリを使わず、TypeScriptでクライアントサイドルーターを構築してください。

### 機能要件
- History API ベースのルーティング
- パスパラメータ: /users/:id
- クエリパラメータのパース
- ネストされたルート
- ルートガード（認証チェック等）
- リダイレクト
- 404フォールバック
- ハッシュルーティングモード
- プログラムによるナビゲーション
- ルート変更のフック（beforeEach, afterEach）

### パッケージ構成
\`\`\`
components/020-router/
  src/
    router.ts
    route.ts
    guard.ts
    history.ts
    types.ts
  tests/
    router.test.ts
    route.test.ts
    guard.test.ts
  README.md
  tsconfig.json
\`\`\`
${qualityTemplate}`
  },
  // === More Python Components ===
  {
    id: '021-config-loader',
    dir: '021-config-loader',
    lang: 'Python',
    title: 'Multi-format Config Loader',
    body: `Python標準ライブラリのみで、マルチフォーマット設定ローダーを構築してください。

### 機能要件
- 対応形式: JSON, YAML(サブセット), TOML, INI, .env
- 自動形式検出（拡張子ベース）
- 設定のマージ: デフォルト < ファイル < 環境変数 < CLI引数
- スキーマバリデーション（型・必須・範囲チェック）
- 設定のホットリロード（ファイル変更監視）
- ドット記法アクセス: config.get("database.host")
- プロファイルサポート: dev/staging/prod
- 設定のdiff表示（現在使用中 vs ファイル）
${qualityTemplate}`
  },
  {
    id: '022-log-analyzer',
    dir: '022-log-analyzer',
    lang: 'Python',
    title: 'Log File Analyzer',
    body: `Python標準ライブラリのみで、ログファイルアナライザーを構築してください。

### 機能要件
- 対応形式: Apache Combined, nginx, JSON lines, カスタム正規
- ログのパースと構造化
- フィルタリング: レベル、時間範囲、キーワード、正規表現
- 集約: エラー率、レスポンスタイム統計、IP別アクセス数
- 異常検知: エラースパイク、レイテンシ急増
- タイムライン表示（分/時間/日別）
- トップN表示（最頻出エラー、最遅エンドポイント等）
- 大きなファイル対応（ストリーミング）
- レポート出力（テキスト/JSON）

### CLI
\`\`\`bash
python -m logalyzer analyze access.log --top-errors 10
python -m logalyzer timeline error.log --by hour
python -m logalyzer detect-anomaly app.log
\`\`\`
${qualityTemplate}`
  },
  {
    id: '023-socket-chat',
    dir: '023-socket-chat',
    lang: 'Python',
    title: 'TCP Socket Chat Server',
    body: `Python標準ライブラリのみで、TCPソケットチャットサーバーを構築してください。

### 機能要件
- マルチクライアント対応（select または threading）
- チャットルーム: 作成・参加・退出
- プライベートメッセージ
- ユーザー登録・認証（シンプルなユーザー名/パスワード）
- メッセージ履歴（ルームごと）
- コマンド: /join, /leave, /list, /msg, /nick, /quit
- ブロードキャスト
- クライアント実装（REPLベース）

### テスト要件
- 複数クライアントの同時接続
- クライアント切断時のクリーンアップ
- ルームが空になった時の自動削除
${qualityTemplate}`
  },
  {
    id: '024-scheduler',
    dir: '024-scheduler',
    lang: 'Python',
    title: 'Job Scheduler',
    body: `Python標準ライブラリのみで、ジョブスケジューラーを構築してください。

### 機能要件
- スケジュール指定: cron風、間隔指定、ワンショット
- ジョブの優先度
- ジョブの依存関係（先行ジョブ完了後に実行）
- タイムアウトとリトライ（指数バックオフ）
- ジョブのステータス: pending, running, success, failed, retrying
- 並列実行（スレッドプール）
- ジョブ履歴の記録
- グレースフルシャットダウン
- ジョブのキャンセル

### テスト要件
- スケジュール精度の確認
- リトライ時の指数バックオフ検証
- 依存関係のあるジョブの実行順序
- シャットダウン中のジョブ完了待ち
${qualityTemplate}`
  },
  {
    id: '025-formula-evaluator',
    dir: '025-formula-evaluator',
    lang: 'Python',
    title: 'Spreadsheet Formula Evaluator',
    body: `Python標準ライブラリのみで、スプレッドシートの数式評価エンジンを構築してください。

### 機能要件
- セル参照: A1, B2, Sheet2!A1
- 範囲参照: A1:B5, A:A
- 四則演算: +, -, *, /
- 関数: SUM, AVG, MIN, MAX, COUNT, IF, VLOOKUP
- セルの依存関係解決（トポロジカルソート）
- 循環参照の検出
- エラータイプ: #REF!, #VALUE!, #DIV/0!, #NAME?, #CIRC!
- セル更新時の自動再計算
- セルの書式設定（表示のみ）

### パッケージ構成
\`\`\`
components/025-formula-evaluator/
  src/formula/
    __init__.py
    lexer.py
    parser.py
    evaluator.py
    cell.py
    sheet.py
    functions.py
  tests/
    test_parser.py
    test_evaluator.py
    test_functions.py
    test_circular.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  // === More diverse components ===
  {
    id: '026-audio-synth',
    dir: '026-audio-synth',
    lang: 'Python',
    title: 'Audio Synthesizer (WAV output)',
    body: `Python標準ライブラリのみ（waveモジュール使用可）で、オーディオシンセサイザーを構築してください。

### 機能要件
- 波形生成: sine, square, sawtooth, triangle, noise
- 周波数・振幅・位相の指定
- ADSR エンベロープ (Attack, Decay, Sustain, Release)
- オシレーターの重ね合わせ
- フィルター: ローパス, ハイパス（簡易版）
- WAV出力（16bit PCM）
- 音階定数: C4=261.63Hz など
- 簡易シーケンサー: メロディーの定義と再生
- ノート表記: "C4", "D#5", "Bb3"

### テスト要件
- 生成WAVのヘッダー検証
- 周波数の正確性（FFT不要、サンプル値の周期で確認）
- ADSRエンベロープの振幅変化確認
${qualityTemplate}`
  },
  {
    id: '027-qr-encoder',
    dir: '027-qr-encoder',
    lang: 'Python',
    title: 'QR Code Generator (basic)',
    body: `Python標準ライブラリのみで、QRコードジェネレーターを構築してください。

### 機能要件
- QRコードバージョン1-10（数値モード）
- リード・ソロモン誤り訂正
- マスクパターンの適用と最適化
- ファインダーパターン、タイミングパターン、アライメントパターン
- ASCII出力（■□で表示）
- PBM/PNM画像出力
- エンコーディングモード: 数値, 英数字, バイト
- エラー訂正レベル: L, M, Q, H

### テスト要件
- 既知のQRコードとの一致確認
- 小さいメッセージ（"HELLO"等）の正確なエンコード
- エラー訂正の確認（データの一部を破損→復元）
${qualityTemplate}`
  },
  {
    id: '028-interpreter',
    dir: '028-interpreter',
    lang: 'Python',
    title: 'Simple Programming Language Interpreter',
    body: `Python標準ライブラリのみで、シンプルなプログラミング言語のインタープリターを構築してください。

### 言語仕様
- 変数代入: let x = 10
- 型: 整数, 浮動小数点, 文字列, 真偽値, 配列
- 演算子: +, -, *, /, %, ==, !=, <, >, <=, >=, and, or, not
- 制御構文: if/elif/else, while, for..in
- 関数定義: fn name(params) { body }
- 組み込み関数: print, len, type, push, pop
- スコープ: グローバル + ローカル
- 配列: [1, 2, 3], インデックスアクセス

### パッケージ構成
\`\`\`
components/028-interpreter/
  src/interpreter/
    __init__.py
    __main__.py
    lexer.py
    parser.py
    evaluator.py
    environment.py
    builtins.py
    types.py
  tests/
    test_lexer.py
    test_parser.py
    test_evaluator.py
    test_functions.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '029-schema-validator',
    dir: '029-schema-validator',
    lang: 'Python',
    title: 'JSON Schema Validator',
    body: `Python標準ライブラリのみで、JSON Schemaバリデーターを構築してください。

### 機能要件
- 型チェック: string, number, integer, boolean, array, object, null
- 文字列: minLength, maxLength, pattern, format (email, uri, date)
- 数値: minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf
- 配列: minItems, maxItems, uniqueItems, items, contains
- オブジェクト: required, properties, additionalProperties, minProperties
- allOf, anyOf, oneOf, not
- $ref の解決（内部参照）
- 再帰的スキーマ対応
- 分かりやすいエラーメッセージ（JSONパス付き）

### パッケージ構成
\`\`\`
components/029-schema-validator/
  src/schemavalidator/
    __init__.py
    validator.py
    format.py
    keywords.py
    errors.py
    types.py
  tests/
    test_basic_types.py
    test_string.py
    test_number.py
    test_array.py
    test_object.py
    test_combinators.py
    test_ref.py
    test_edge_cases.py
  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    id: '030-dns-client',
    dir: '030-dns-client',
    lang: 'Python',
    title: 'DNS Client (from scratch)',
    body: `Python標準ライブラリのみ（socket使用可）で、DNSクライアントを構築してください。

### 機能要件
- DNSクエリの構築（バイナリパケット）
- UDP/TCPでのクエリ送信
- レコードタイプ: A, AAAA, CNAME, MX, NS, TXT, SOA
- DNSレスポンスのパース
- 再帰的解決（ルート→TLD→権威）
- キャッシュ（TTL付き）
- 逆引き（PTR）
- クエリのトレース表示（dig風）

### CLI
\`\`\`bash
python -m dnsclient example.com A
python -m dnsclient example.com MX --trace
python -m dnsclient 8.8.8.8 PTR
\`\`\`
${qualityTemplate}`
  },
];

// Generate remaining issues dynamically
const additionalComponents = [
  { id: '031-expression-parser', title: 'Mathematical Expression Parser & Evaluator', desc: '四則演算、括弧、関数呼び出し(sin, cos, log)、変数代入をサポートする数式パーサー。AST生成と評価を分離。' },
  { id: '032-rate-limiter', title: 'Rate Limiter (Token Bucket + Sliding Window)', desc: 'トークンバケットとスライディングウィンドウの両アルゴリズムを実装。スレッドセーフ。' },
  { id: '033-png-writer', title: 'PNG Image Writer from Scratch', desc: 'PythonのstructモジュールのみでPNG画像を生成。IHDR, IDAT(zlib), IENDチャンク。基本的な図形描画。' },
  { id: '034-websocket-server', title: 'WebSocket Server', desc: 'RFC 6455準拠のWebSocketサーバー。ハンドシェイク、フレームのパース/生成、ping/pong、close。' },
  { id: '035-mail-parser', title: 'Email (MIME) Parser', desc: 'MIMEメールのパーサー。マルチパート、添付ファイル、エンコーディング(Base64/Quoted-Printable)対応。' },
  { id: '036-i18n-tool', title: 'Internationalization (i18n) Toolkit', desc: '翻訳ファイル管理、複数形ルール、日付/数値フォーマット、フォールバックチェーン。' },
  { id: '037-permission-engine', title: 'RBAC Permission Engine', desc: 'ロールベースアクセス制御。ロールの継承、リソース・アクションの組み合わせ、ポリシーキャッシュ。' },
  { id: '038-undo-manager', title: 'Undo/Redo Manager', desc: 'コマンドパターンベースのUndo/Redo。マージ可能な操作、ブランチ（redo後にundo分岐）、メモリ上限。' },
  { id: '039-event-emitter', title: 'Event Emitter with Wildcards', desc: 'Node.js EventEmitter風。ワイルドカード(event.*)、名前空間、once、リスナー上限、非同期emit。' },
  { id: '040-avl-tree', title: 'AVL Tree (Self-balancing BST)', desc: 'AVL木の実装。挿入・削除時の回転(LL, RR, LR, RL)、マージ・分割。' },
  { id: '041-promise-lib', title: 'Promise/A+ Implementation (TypeScript)', desc: 'Promise/A+仕様準拠。then, catch, finally, Promise.all, race, allSettled, any。' },
  { id: '042-template-literal', title: 'Template String Engine', desc: 'JSのテンプレートリテラル風エンジン。式評価、フィルターパイプ、ネスト、エスケープ。' },
  { id: '043-ring-buffer', title: 'Ring Buffer & Double-Ended Queue', desc: '固定サイズリングバッファとDeque。オーバーフロー戦略（上書き/例外）。スレッドセーフ版。' },
  { id: '044-profiler', title: 'Python Code Profiler', desc: '関数レベルのプロファイラー。実行時間、呼び出し回数、コールスタック。コンテキストマネージャー/デコレーター。' },
  { id: '045-mock-server', title: 'HTTP Mock Server', desc: 'テスト用モックサーバー。リクエストマッチング、固定レスポンス、遅延、記録再生。' },
  { id: '046-consistent-hash', title: 'Consistent Hashing', desc: '分散システム用consistent hashing。仮想ノード、ノード追加/削除時のキー再分配最小化。' },
  { id: '047-state-machine', title: 'Finite State Machine Engine', desc: '汎用FSM。状態定義、遷移テーブル、ガード条件、アクション(enter/exit/transition)、階層的状態。' },
  { id: '048-merkle-tree', title: 'Merkle Tree', desc: 'データ整合性確認用Merkle Tree。葉の追加、部分更新、差分検出、証明(Proof of Inclusion)。' },
  { id: '049-lexer-gen', title: 'Lexer Generator', desc: 'DSLからレキサーを自動生成。トークン定義（正規表現）、優先度、行・列のトラッキング。' },
  { id: '050-ci-runner', title: 'Simple CI Pipeline Runner', desc: 'YAML定義のCIパイプライン。ステージ、並列ジョブ、環境変数、成果物、失敗時の継続/停止。' },
];

// Process additional components
for (const comp of additionalComponents) {
  components.push({
    id: comp.id,
    dir: comp.id,
    lang: comp.id.startsWith('041') ? 'TypeScript' : 'Python',
    title: comp.title,
    body: `${comp.desc}

### パッケージ構成
\`\`\`
components/${comp.id}/
  src/
  tests/
  README.md
\`\`\`

**※パッケージ構成は適切に設計してください。**

### 機能要件
- 上記の説明を満たす完全な実装
- CLIまたはREPL（該当する場合）

${qualityTemplate}`
  });
}

// Main
console.log(`Total issues to create: ${components.length}`);

let created = 0;
let failed = 0;

for (const comp of components) {
  const title = `[${comp.id}] ${comp.title}`;
  const body = comp.body;

  if (DRY_RUN) {
    console.log(`[${created + 1}] ${title}`);
    created++;
    continue;
  }

  try {
    // Write body to temp file to avoid shell escaping issues
    const tmpFile = join(TMP, `issue-${comp.id}.md`);
    writeFileSync(tmpFile, body);

    const result = execSync(
      `gh issue create --repo ${REPO} --title "${title.replace(/"/g, '\\"')}" --body-file "${tmpFile}" --label "${LABEL}"`,
      { encoding: 'utf8', shell: 'bash' }
    );
    console.log(`[${created + 1}] ${comp.id}: ${result.trim()}`);
    created++;
  } catch (e) {
    console.error(`[${created + 1}] ${comp.id}: FAILED - ${e.message.slice(0, 100)}`);
    failed++;
  }
}

console.log(`\nDone: ${created} created, ${failed} failed`);
