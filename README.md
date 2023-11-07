# UPPER HEAD
## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1
* 画像フォルダ(/ex05/fig)
* 音源フォルダ(/ex05/data)

## ゲームの概要
主人公キャラクターこうかとんをキーボード操作により敵と戦闘するUNDERTALEみたいなゲーム

## ゲームの実装
### 共通基本機能
* プレイヤーの行動や説明文の表示をする枠の描画

### 担当追加機能
* 敵の攻撃（担当：川地）：敵の攻撃を作成
* プレイヤーの動き（担当：大石）：枠内でのプレイヤーの動き（矢印キーの利用）
* 戦う・道具・話す・見逃す（担当：上田）：ボタンを押した判定やその後の行動（矢印キーとENTERキーの利用）
* ライフ管理（担当：小川省吾）：ライフの増減やUIの表示
* BGM・効果音、敵の描画（担当：小川幹）：BGMや行動の時の音、敵の描画をする
* 敵の攻撃とプレイヤーの衝突判定（担当：小川省吾）：敵の攻撃とプレイヤーがあたったときに当たり判定を表示させ、HPを減らす

### ToDo
- [ ] プレイヤーのジャンプ機能
- [ ] 音量の調整

### メモ
* すべての行動はENTERキーと矢印キーで行動できる

