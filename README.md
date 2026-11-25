# sasshite

**会話の文脈から、いま伝えることを組み立てる Agent Skill。**

*Think thoroughly. Communicate selectively.*

調査や推論で分かったことを、相手がこの会話で必要としている内容へ組み替えます。GPT の reasoning model と Codex を念頭に、返答前の伝達判断を促す指示として実装しています。

## 何をするか

- 現在の問い、継続中の目的、ユーザーの訂正を捉える。
- 共有済みの前提を利用し、必要な説明・反論・確認・共感を選ぶ。
- 読み手の判断に影響する不確実性を残し、文脈から明らかな範囲外の断りを省く。
- 調べた順序をそのまま話すのではなく、相手が理解して使える内容へ整理する。

相談、対話、議論、報告、レポートでは、適切な返答が異なります。sasshite は、回答の見出し、長さ、結論の位置、語調、締めの質問を固定しません。詳しい説明や、ユーザーが指定した表・JSONなども、その依頼に応じて生成します。

## 使う

Skill 本体は [skills/sasshite/SKILL.md](skills/sasshite/SKILL.md) です。ランタイムは指示と OpenAI 用 UI メタデータだけで、外部 API や追加スクリプトを必要としません。

Codex では、`$skill-installer` にこのリポジトリの `skills/sasshite` を指定してインストールできます。

```text
$skill-installer https://github.com/IsseiMatsuzoe/sasshite/tree/main/skills/sasshite
```

インストール後は、通常の依頼に `$sasshite` を添えて使います。

```text
$sasshite さっきの議論の続きを考えたい。
```

対応するホストの Skill ローダーを通じて使ってください。Skills の自動選択はホストに依存するため、まず明示指定で試すと適用の有無を区別できます。[OpenAI の Skills 文書](https://learn.chatgpt.com/docs/build-skills)も参照してください。

## 設計と根拠

[設計メモ](docs/design.md)では、何を残し、何を省くかの判断と、文書用の tsuzuri から変更した点を説明しています。[研究メモ](docs/research.md)には、OpenAI の公式指針、Grice、関連性理論、グラウンディング、QUD、認知負荷理論、LLM の過剰応答の研究を記録しています。

[MaryCache/tsuzuri](https://github.com/MaryCache/tsuzuri) の、言い回しを作る前に読み手に渡すものを定める考えを参考にしました。sasshite の本文は対話向けに独立して記述しています。

## 比較試験

[試験手順](evals/README.md)と、[2026-11-25 の初回結果](evals/runs/2026-11-25-pilot/RESULTS.md)を公開しています。合成した12場面で、追加指示なし・簡潔さの指示・sasshite を比較します。生成時には採点基準を渡さず、評価時には条件名を隠します。

短さや見た目を得点にせず、問いへの適合、必要な情報の保持、前提の適用、会話上の働きを評価します。初回は内容上の挙動を確認する小規模な試験です。

初回は3条件とも12例すべてで合格し、条件名を隠した2回のモデル評価でも同率でした。形式の自由や必要な情報を保つ動作は確認できましたが、この試験では追加効果は示せていません。

## 開発用の確認

```bash
python -B -m unittest discover -s tests -v
```

この検査は比較用スクリプトの入力漏れ、条件の漏えい、集計などを確認します。Skill の内容への効果は、上記の比較試験で別に扱います。

## License

[CC0 1.0 Universal](LICENSE)。参照した文献と外部プロジェクトの権利は、それぞれの原典に従います。
