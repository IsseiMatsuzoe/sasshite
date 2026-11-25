# 調査と設計上の対応

確認日: 2026-11-25。ここでは、原典が述べていることと、sasshite で採用した設計判断を分けて記録する。先行研究の数値を、現在の GPT・Claude・Gemini の比較結果として流用しない。

## OpenAI の一次資料

### O1. Skills とプロンプトを見直す指針

Eric Provencher, [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), 2026-09-11。

短く適用範囲の明確な description、必要に応じた資料の読み込み、過剰な手順や矛盾する指示の見直しを勧めている。特定モデルについての開発指針であり、長いユーザー向け回答の否定ではない。

**採用:** 伝達内容を選ぶ少数の判断基準を本文に置く。詳しい調査資料を毎回読ませず、応答の形式は固定しない。

### O2. Skill の構造と発火

OpenAI, [Build skills](https://learn.chatgpt.com/docs/build-skills)。旧 Codex Skills URL からの転送先も確認した。

`name` と `description` を入口として、選択時に `SKILL.md` 全文が読み込まれる。明示指定と暗黙的な選択を区別する。指示だけの Skill、必要に応じた補助ファイル、`agents/openai.yaml` を説明している。

**採用:** `skills/sasshite/SKILL.md` と UI メタデータを実装する。常時実行される処理系とは説明しない。比較試験では本文を明示的に与え、自動選択を評価したことにはしない。

### O3. Reasoning model の指示

OpenAI, [Reasoning best practices](https://developers.openai.com/api/docs/guides/reasoning-best-practices)。

単純で直接的な指示、明確な制約と到達点、まず例なしでの試行を勧める。一般的な「段階的に考えよ」という指示は改善を保証しない。本文に含まれる古いモデルの説明は、今回のモデル選択の根拠に使っていない。

**採用:** 判断してほしい対象を明示し、思考の長さや段階数を増やすことを要求しない。回答例をランタイムに並べてその文体を学習させない。

### O4. 評価

OpenAI, [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills) および [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)。

前者は成功条件を定め、実行結果と成果物を記録し、機械的検査と判断を要する評価を区別する。後者は実際の用途に沿う課題、明確な基準、人による較正、候補順や冗長さによる評価バイアスを扱う。

**採用:** 生成側から採点基準を隠す。評価側から条件名を隠し、候補順を変える。内容の充足と脱線の両方を見る。文字数は診断値としてのみ扱う。ファイル構造の検証と応答品質の評価を分ける。

## コミュニケーションと認知の原典

### C1. その時点の会話に必要な寄与

H. P. Grice (1975), *Logic and Conversation*, pp. 45–47。[大学公開の抜粋](https://www.sfu.ca/~jeffpell/Cogs300/GriceLogicConvers75.pdf)。

会話で受け入れられている目的・方向と、その段階に合う寄与を論じる。過剰な情報は、受け手に余分な論点や「これを述べた意図」を考えさせ得ると指摘する。

**採用:** 正しく、話題に関係しているだけでは十分とせず、現在の発話に何をもたらすかを見る。これは語用論の説明枠組みで、機械的な削除規則ではない。

### C2. 処理労力と認知的効果

Deirdre Wilson & Dan Sperber (2004), *Relevance Theory*, *The Handbook of Pragmatics*, pp. 607–632。[著者公開本文](https://www.dan.sperber.fr/?p=93)。

関連性を、得られる認知的効果と処理に必要な労力から比較的に捉える。既存の理解の強化や訂正も効果に含まれる。本文は定量的な定義ではないことを明記している。

**採用:** 相手に負担をかけるだけの情報を減らし、理解に必要な説明を保持する。「関連性 = 価値 / 文字数」のような数式や、短ければよいという基準にはしない。

### C3. 共通基盤と共同労力

Herbert H. Clark & Susan E. Brennan (1991), *Grounding in Communication*, pp. 127–149。[著者公開 PDF](https://web.stanford.edu/~clark/1990s/Clark,%20H.H.%20_%20Brennan,%20S.E.%20_Grounding%20in%20communication_%201991.pdf)。

相互理解を共同で成立させる過程を扱う。十分な理解の基準は目的や媒体によって変わる。寄与の開始から受け入れまでの共同労力を考えるため、短い一発回答が常に有利とは限らない。

**採用:** 実際に共有された内容を使う。確認や言い直しに役割がある場合は残す。相手の知識や合意を勝手に仮定せず、理解のずれを修復する。

### C4. 現在の問い

Craige Roberts (2012), *Information Structure: Towards an integrated formal theory of pragmatics*, *Semantics and Pragmatics*, 5(6)。[掲載誌](https://semprag.org/index.php/sp/article/view/sp.5.6)、[著者公開 PDF](https://www.asc.ohio-state.edu/roberts.21/LSA/Roberts.InfoStr.2012.pdf)。

談話の文脈を、現在議論されている問いを中心に整理する。発言だけでなく、その問いに答えるための質問や部分的な寄与も扱える。

**採用:** 最後の疑問文の字面だけでなく、継続中の目的、訂正、話題の変更を捉える。隣接する別の質問に勝手に答えない。必要な前提や反論まで除かない。

### C5. 認知負荷と知識の違い

John Sweller (2023), [The Development of Cognitive Load Theory: Replication Crises and Incorporation of Other Theories Can Lead to Theory Expansion](https://link.springer.com/article/10.1007/s10648-023-09817-2), *Educational Psychology Review*, 35, 95。

課題の認知的な難しさは、課題の構造だけでなく学習者の知識にも依存する。熟達によって支援の効果が消えたり逆転したりすることを扱う。主な対象は教育と学習である。

**採用:** 初学者向けの説明と既知事項の再説明を、会話の証拠から区別する。職業だけで専門知識を決めない。研究を「箇条書きは最大何個」といった形式制約に変換しない。

### C6. Grounding を増やせばよいわけではない

Omar Shaikh et al. (2024), [Grounding Gaps in Language Model Generations](https://aclanthology.org/2024.naacl-long.348/), NAACL, pp. 6279–6296。[PDF](https://aclanthology.org/2024.naacl-long.348.pdf)。

対象のモデルとデータでは、相互理解の確認を人間ほど行わず、共有前提を仮定する傾向を報告する。一方、確認・追加質問・相づちを促す介入は、それらの過剰な使用を生み、適切な場面で行う点まで改善するとは限らなかった。

**採用:** 確認や共感の回数を目標にしない。会話への適合で評価する。日本語や現在のモデルでの効果は今回の試験で別に扱う。

### C7. 過剰応答と必要な次の一手

Omar Shaikh et al. (2025), [Navigating Rifts in Human-LLM Grounding: Study and Benchmark](https://aclanthology.org/2025.acl-long.1016/), ACL, pp. 20832–20847。[PDF](https://aclanthology.org/2025.acl-long.1016.pdf)。

明示された依頼を越えて予想される追加質問にまで答える overresponse を分類している。物語の依頼に対して、物語を書く計画を先に返す例がある。相互理解に関わる次の発話には、回答、意見、謝罪、確認など複数の役割がある。

**採用:** 現在必要な発話と、後で役立つかもしれない内容を分ける。会話を進めることを行動計画の提示と同一視しない。論文の限定された課題・モデルによる結果を、sasshite の効果の証明にはしない。

## tsuzuri から参照したもの

MaryCache, [tsuzuri](https://github.com/MaryCache/tsuzuri)。確認したコミット: [`61e346b5d491b6b25b9b4be28f9496fdfc14789a`](https://github.com/MaryCache/tsuzuri/commit/61e346b5d491b6b25b9b4be28f9496fdfc14789a)。原典は MIT License、Copyright (c) 2026 MaryCache。

- [SKILL.md](https://github.com/MaryCache/tsuzuri/blob/61e346b5d491b6b25b9b4be28f9496fdfc14789a/skills/tsuzuri/SKILL.md): 執筆前に意図を定める工程。原典の対象から通常の返答は除外されている。
- [intent-quality.md](https://github.com/MaryCache/tsuzuri/blob/61e346b5d491b6b25b9b4be28f9496fdfc14789a/skills/tsuzuri/references/intent-quality.md): 読み手が得るものと、書き手の思考順・都合を区別する。意図の問題を言い回しだけで修正しない。
- [requirements-and-design.md](https://github.com/MaryCache/tsuzuri/blob/61e346b5d491b6b25b9b4be28f9496fdfc14789a/skills/tsuzuri/references/requirements-and-design.md): 内部で範囲を決めることと、それを本文で断るかを分ける。sasshite には原典の冒頭指定を採用していない。

sasshite の本文は対話向けに独立して記述した。tsuzuri のコード、一文単位の記録機構、文書用テンプレートは同梱していない。

## 研究から今回の実装へ

以上は、何を評価すべきか、どのような失敗を避けるべきかの根拠になる。回答前にこの判断を指示することの追加効果は実験上の問いである。[試験手順](../evals/README.md) では、問いへの適合だけを高めて必要な留保や詳しい説明を失っていないかも確認する。
