/**
 * Recreate 16 skipped issues as fresh ones for Jules to pick up
 */
import { execSync } from 'child_process';
import { writeFileSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

const REPO = 'muumuu8181/ai-stress-test';

function gh(cmd) {
  try { return execSync(`gh ${cmd}`, { encoding: 'utf8', shell: 'bash' }); }
  catch (e) { return e.stdout || e.message; }
}

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

const issues = [
  {
    title: '[004-csv-toolkit] CSV Processing Toolkit',
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
  src/csvtool/  tests/  README.md
\`\`\`
${qualityTemplate}`
  },
  {
    title: '[011-http-server] HTTP Server from Scratch',
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
${qualityTemplate}`
  },
  {
    title: '[013-sudoku-solver] Sudoku Solver & Generator',
    body: `Python標準ライブラリのみで、数独ソルバー・ジェネレーターを構築してください。

### 機能要件
- バックトラッキングによる解法
- 制約伝播（Constraint Propagation）の高速解法
- 複数解の列挙（全解モード）
- パズル生成（難易度指定: easy/medium/hard/expert）
- パズルのバリデーション
- ヒント機能（次の一手を返す）
- 盤面のpretty print
- ファイル入出力

### テスト要件
- 既知の解を持つパズルでの正解確認
- 解なしパズルの検出
- 生成パズルの一意解確認
- 最難パズル（17ヒント）の解法性能
${qualityTemplate}`
  },
  {
    title: '[018-reactive-store] Reactive State Store (RxJS-like)',
    body: `外部ライブラリを使わず、TypeScriptでリアクティブステートストアを構築してください。

### 機能要件
- Observable / Observer パターン
- オペレーター: map, filter, reduce, debounce, throttle, merge, combineLatest
- BehaviorSubject, ReplaySubject
- ストア: dispatch(action) → reducer → state更新 → 通知
- ミドルウェアチェーン
- セレクター（メモ化付き）
- タイムトラベルデバッグ（状態履歴の記録・復元）
${qualityTemplate}`
  },
  {
    title: '[020-router] Client-side Router',
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
${qualityTemplate}`
  },
  {
    title: '[022-log-analyzer] Log File Analyzer',
    body: `Python標準ライブラリのみで、ログファイルアナライザーを構築してください。

### 機能要件
- 対応形式: Apache Combined, nginx, JSON lines, カスタム正規
- ログのパースと構造化
- フィルタリング: レベル、時間範囲、キーワード、正規表現
- 集約: エラー率、レスポンスタイム統計、IP別アクセス数
- 異常検知: エラースパイク、レイテンシ急増
- タイムライン表示（分/時間/日別）
- トップN表示
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
    title: '[039-event-emitter] Event Emitter with Wildcards',
    body: `Python標準ライブラリのみで、Node.js EventEmitter風のイベントシステムを構築してください。

### 機能要件
- ワイルドカード(event.*)によるイベントリスニング
- 名前空間(event.namespace.sub)
- once() / on() / off() / emit()
- リスナー上限設定
- 非同期emit対応
- エラーハンドリング（リスナー内例外の捕捉）
- リスナーの自動クリーンアップ
- イベント履歴（オプション）
${qualityTemplate}`
  },
  {
    title: '[042-template-literal] Template String Engine',
    body: `Python標準ライブラリのみで、テンプレート文字列エンジンを構築してください。

### 機能要件
- 変数展開: \${variable}, \${user.name}
- 式評価: \${price * quantity}
- フィルターパイプ: \${name | upper}, \${price | currency}
- ネストしたテンプレート
- HTMLエスケープ: 自動 + safe フィルター
- 条件分岐: {?condition}...{/?}
- ループ: {@each items as item}...{/each}
- カスタムフィルター登録
- エラー行番号付きメッセージ
${qualityTemplate}`
  },
  {
    title: '[043-ring-buffer] Ring Buffer & Double-Ended Queue',
    body: `Python標準ライブラリのみで、リングバッファとDequeを実装してください。

### 機能要件
- 固定サイズリングバッファ
- ダブルエンデッドキュー（Deque）
- オーバーフロー戦略: 上書き / 例外 / 古いものを破棄
- append / appendleft / pop / popleft
- peek / peekleft
- maxlen プロパティ
- イテレータサポート
- スレッドセーフ版
- ブロッキング版（タイムアウト付きput/get）
- from_iterable() クラスメソッド
${qualityTemplate}`
  },
  {
    title: '[044-profiler] Python Code Profiler',
    body: `Python標準ライブラリのみで、コードプロファイラーを構築してください。

### 機能要件
- 関数レベルのプロファイリング
- 実行時間測定（累積・自己）
- 呼び出し回数カウント
- コールスタック記録
- コンテキストマネージャー対応: with profiler.profile():
- デコレーター対応: @profile
- 統計出力: テーブル / JSON / フレームグラフ（テキスト）
- ソート: 累積時間 / 自己時間 / 呼び出し回数
- 関数フィルタリング（正規表現）
- メモリ使用量の追跡（tracemalloc使用可）
${qualityTemplate}`
  },
  {
    title: '[045-mock-server] HTTP Mock Server',
    body: `Python標準ライブラリのみで、テスト用HTTPモックサーバーを構築してください。

### 機能要件
- リクエストマッチング（メソッド・パス・ヘッダー・ボディ）
- 固定レスポンス返却
- 動的レスポンス（コールバック関数）
- レスポンス遅延シミュレーション
- ステートフルモック（シーケンシャルレスポンス）
- リクエスト記録（全リクエスト履歴）
- リクエスト再生（記録から再テスト）
- 期待値検証（特定リクエストが来たか）
- コンテキストマネージャー対応
- pytest フィクスチャ対応
${qualityTemplate}`
  },
  {
    title: '[046-consistent-hash] Consistent Hashing',
    body: `Python標準ライブラリのみで、分散システム用Consistent Hashingを実装してください。

### 機能要件
- ハッシュ関数: MD5, SHA-1, SHA-256（切り替え可能）
- 仮想ノード（VNode）サポート
- ノード追加・削除
- キーのノード割り当て（O(log n)）
- ノード追加時の再分配最小化確認
- ノード削除時の再分配確認
- ノードの重み付け（weight）
- レプリカ数指定（同一キーをN個のノードに配置）
- ノード負荷統計
- シリアライズ/デシリアライズ
${qualityTemplate}`
  },
  {
    title: '[047-state-machine] Finite State Machine Engine',
    body: `Python標準ライブラリのみで、汎用有限状態マシンエンジンを構築してください。

### 機能要件
- 状態定義と遷移テーブル（DSLまたはdict）
- ガード条件（遷移の可否判定）
- アクション: on_enter, on_exit, on_transition
- 階層的状態（ネストされたFSM）
- 並行状態（複数の状態マシンを同時実行）
- イベントキュー
- 状態履歴（トラッキング）
- ビジュアライゼーション（DOT形式出力）
- JSON定義からのFSM生成
- 型安全な状態・イベント定義
${qualityTemplate}`
  },
  {
    title: '[048-merkle-tree] Merkle Tree',
    body: `Python標準ライブラリのみで、Merkle Treeを実装してください。

### 機能要件
- SHA-256ベースのハッシュツリー構築
- 葉の追加・削除
- 部分更新（単一葉の変更→ルートまで再計算）
- Proof of Inclusion（包含証明の生成・検証）
- Proof of Exclusion（非包含証明）
- 差分検出（2つのツリーのルート比較→異なる葉を特定）
- バッチ更新（複数葉の同時変更）
- ツリーのシリアライズ（JSON）
- 大規模データ対応（ストリーミング構築）
- ノード数・深さの統計
${qualityTemplate}`
  },
  {
    title: '[049-lexer-gen] Lexer Generator',
    body: `Python標準ライブラリのみで、DSLからレキサーを自動生成するツールを構築してください。

### 機能要件
- トークン定義DSL（名前 + 正規表現パターン）
- 優先度指定（複数マッチ時の解決）
- トークンタイプの自動生成
- 行・列のトラッキング（ソースマッピング）
- ホワイトスペース・コメントのスキップ設定
- 複数行トークン対応
- エラー回復（不正文字のスキップ・報告）
- 生成されたレキサーのPythonコード出力
- Unicode対応
- カスタムアクション（マッチ時のコールバック）
${qualityTemplate}`
  },
  {
    title: '[050-ci-runner] Simple CI Pipeline Runner',
    body: `Python標準ライブラリのみで、YAML定義のCIパイプラインランナーを構築してください。

### 機能要件
- YAMLパース（標準ライブラリのみの簡易パーサー、またはdict定義）
- ステージ定義（順次実行）
- ジョブの並列実行（同一ステージ内）
- 環境変数の受け渡し
- 成果物の定義
- 失敗時の継続/停止設定
- タイムアウト設定
- 条件付き実行（if/unless）
- ワークフロー変数
- 実行ログのリアルタイム出力
- JSON形式の実行レポート

### 定義例
\`\`\`yaml
stages:
  - name: test
    jobs:
      - run: pytest tests/
      - run: mypy src/
  - name: build
    jobs:
      - run: python setup.py sdist
\`\`\`
${qualityTemplate}`
  }
];

let created = 0;
for (const issue of issues) {
  const tmpFile = join(tmpdir(), `issue-recreate-${Date.now()}.md`);
  writeFileSync(tmpFile, issue.body);
  const result = gh(`issue create --repo ${REPO} --title "${issue.title}" --body-file "${tmpFile}" --label "jules"`);
  if (result.includes('github.com')) {
    console.log(`Created: ${issue.title} → ${result.trim()}`);
    created++;
  } else {
    console.log(`FAILED: ${issue.title}: ${result.substring(0, 100)}`);
  }
}

console.log(`\nDone: ${created}/${issues.length} issues recreated`);
