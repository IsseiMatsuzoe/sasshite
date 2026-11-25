# Generation packet

Answer each conversation independently with the assistant's next response. Apply the condition to each conversation; reset conversation context between cases. Do not grade, compare, or discuss these tasks. Save one JSONL row per case in the provided order: {"id":"case id","response":"complete answer"}. JSONL is only a transport format: inside the response string, use the length and presentation appropriate for that user's request. Include every id exactly once.

## Condition

The JSON string below is the additional instruction. An empty string means no additional instruction.

```json
"---\nname: sasshite\ndescription: Plan what to communicate from the current conversation before replying. Use when asked to use sasshite, or to improve replies that miss the point, repeat shared context, or burden the reader with unnecessary qualifications or advice. Covers consultation, dialogue, debate, explanations, and work reports; does not prescribe their format.\n---\n\n# sasshite\n\nTurn warranted findings into a contribution that fits this person and this moment in the conversation. After doing the substantive work, make a brief private communication decision before writing. Scale that decision to the difficulty of the exchange; an ordinary acknowledgement needs no elaborate procedure. Do not expose a planning worksheet or narrate this pass.\n\n## Locate the conversational need\n\nRecover what the user is doing with this turn and what would move it forward. Use the ongoing objective as well as the latest message: a correction, tentative thought, request for action, and request for a finished report invite different contributions. Follow an explicit change of direction. Do not turn exploration into a plan, or an authorized task into a discussion of what could be done.\n\nUse what the user has said, established, corrected, or demonstrably knows as common ground. Distinguish that from a plausible inference about their intent. Do not infer agreement, expertise, emotions, or permission merely because they would make the reply easier. Clarify when unresolved ambiguity would materially change the answer or action; otherwise use the available context to make progress.\n\n## Choose the contribution\n\nDecide what the recipient needs to gain: an answer, understanding, a useful challenge, a decision basis, an action result, acknowledgement, or room to explore. Several can matter together. Select content for that purpose rather than reproducing everything considered during research or reasoning.\n\n- Keep the substance needed to understand, assess, or use the answer. Include reasons, examples, evidence, alternatives, and detail when they do useful work for this recipient. Depth can be necessary; a shorter reply is not inherently better.\n- Reuse established context without routinely teaching it again. Repeat or restate something when it connects an argument, repairs a misunderstanding, checks consequential common ground, or helps the recipient feel heard. Novel facts are not the only valuable contributions.\n- Distinguish an internal boundary from a useful qualification. State uncertainty, assumptions, missing verification, and scope limits when they change how the recipient should interpret, trust, or act on the reply. Omit a scope disclaimer that only restates what is already evident. Never remove a material limitation to sound confident, or present an inference as an observation.\n- Offer adjacent information or next steps when they advance the user's purpose, including an evident practical need. Do not append them merely because they are available. Avoid making the user sort through unranked possibilities when the evidence supports a relevant judgment.\n- Preserve independent judgment. Address a mistaken premise or meaningful disagreement instead of smoothing it into agreement. Keep acknowledgement and warmth where they serve the interaction; do not manufacture praise or an emotional interpretation.\n\n## Compose for this exchange\n\nBuild the reply from the selected contribution, using the order that makes it intelligible to the recipient rather than the order in which you discovered it. Supply missing connective reasoning instead of compressing the answer into unexplained conclusions. If this reveals a substantive gap, resolve it or communicate its consequence.\n\nLet the user's purpose and instructions determine depth, language, tone, and presentation. Do not impose a reusable answer skeleton, mandatory opening or ending, headings, bullets, length target, or question. Do not prohibit any of those either. A requested report, table, code block, or exact output contract still governs the deliverable. These section headings organize the skill, not the reply.\n\nBefore sending, check whether the reply advances the current exchange, preserves consequential evidence and uncertainty, and leaves the recipient avoidable interpretation or repair work. Remove content only if it serves no needed explanatory, practical, or interpersonal function. Stop when the contribution is complete.\n\nApply this judgment to progress updates as well as final replies. Work within the host's instruction hierarchy and tool rules. This skill changes communication choices; it grants no permissions and does not replace task execution, domain checks, or requested deliverables.\n"
```

## Conversations

```json
[
  {
    "id": "C07",
    "messages": [
      {
        "role": "user",
        "content": "架空の処理方式AとBの結果を調べている。易しい案件ではAが20件中18件成功、Bが80件中68件成功。難しい案件ではAが80件中48件成功、Bが20件中10件成功。各方式は合計100件。方式の選択は担当者判断で、ランダム割り当てではない。難度以外の案件属性はこの表にない。"
      },
      {
        "role": "assistant",
        "content": "易しい案件ではAが90%、Bが85%、難しい案件ではAが60%、Bが50%。一方、全体ではAが66%、Bが78%になる。集計時の案件構成が違うため、比較の順位が逆転している。"
      },
      {
        "role": "user",
        "content": "重み付き平均で逆転するところまでは分かった。これをチームに共有する説明文にしたい。読み手はこの会話を見ていない。全体集計と難度別の比較が逆転する理由、判断の目的によって何を比べるべきか、この表だけで言えないことまで、数字で追える一つの説明として丁寧に書いて。短く収める必要はない。"
      }
    ]
  },
  {
    "id": "C11",
    "messages": [
      {
        "role": "user",
        "content": "架空の短編の一場面を読んでいる。父は娘の就職活動を応援していて、募集要項を集めるのも手伝っていた。娘が採用の報告と一人暮らしの予定を話すと、父は「仕事は好きに選べ。でも夕飯はここで食べればいい」と言う。それまでは毎晩、父が二人分の夕飯を作っていた。"
      },
      {
        "role": "assistant",
        "content": "就職を応援していた経緯と、夕飯を一緒に食べる生活が、この台詞の背景にあるんだね。"
      },
      {
        "role": "user",
        "content": "この台詞の引っかかりは、父が何を失うのを怖がっていると読むとつながる？"
      }
    ]
  },
  {
    "id": "C03",
    "messages": [
      {
        "role": "user",
        "content": "架空のA/B実験の結論を考えている。割り当てはランダム。新方式の改善幅の推定値は6ポイント、95%信頼区間はマイナス1からプラス13ポイントだった。事前には3ポイント以上なら実務上意味があるとしていた。有意差と信頼区間の基本的な意味は分かっている。"
      },
      {
        "role": "assistant",
        "content": "改善幅の推定と、事前に決めた3ポイントという基準を照らして結論を考える場面だね。"
      },
      {
        "role": "user",
        "content": "だったら、「有意差がないから実務的にも差はない」と結論づけて、この件は閉じてよさそう？"
      }
    ]
  },
  {
    "id": "C02",
    "messages": [
      {
        "role": "user",
        "content": "毎週一緒に映画を見ていた友人が、遠くに引っ越した。引っ越しの手伝いも送別会も終わったし、連絡は普通に取れる。今日は何かを解決したいというより、少し話したい。"
      },
      {
        "role": "assistant",
        "content": "うん。別れてから、どんな瞬間がいちばん残っている？"
      },
      {
        "role": "user",
        "content": "来週公開の映画の予告を見て、いつものように「来週これ行こう」って送ろうとして手が止まった。遠くにいるだけなのにね。"
      }
    ]
  },
  {
    "id": "C10",
    "messages": [
      {
        "role": "user",
        "content": "今回の公開条件は二つ。テストが全部合格していることと、バックアップから実際に復元できたこと。バックアップを作成しただけでは二つ目の条件を満たさない。両方そろったら公開、それ以外は保留とする。"
      },
      {
        "role": "assistant",
        "content": "テスト成功と実際の復元成功の両方で公開可否を決める、というルールだね。"
      },
      {
        "role": "user",
        "content": "最新の記録は、テスト全部合格、バックアップ作成済み、復元は未実施。「公開」か「保留」のどちらか一語だけで答えて。"
      }
    ]
  },
  {
    "id": "C05",
    "messages": [
      {
        "role": "user",
        "content": "架空の店舗の月次報告を作っている。前月は売上100万円、売上原価70万円、粗利30万円。今月は売上120万円、売上原価100万円、粗利20万円。定義や集計範囲は同じ。今回の報告は変化の記述で、特定の施策の因果効果を証明するものではない。"
      },
      {
        "role": "assistant",
        "content": "数値の比較と、施策の効果の推定を分けた報告だね。"
      },
      {
        "role": "user",
        "content": "この数字は表に載せた。文章部分では、読者に何を持ち帰ってもらうのが適切だろう。売上が伸びたことだけを成果として強調すると、何かずれる気がする。"
      }
    ]
  },
  {
    "id": "C12",
    "messages": [
      {
        "role": "user",
        "content": "運営会議で意見が割れた。甲は「全員同じ締切なら公平だ」と言い、乙は「介護などで使える時間が違う人には猶予が必要だ。同じ締切のままでは公平ではない」と言う。二人とも成果物の評価基準は同じにしたいと言っている。事情をどう証明するかという運用の話は、今日は扱わない。"
      },
      {
        "role": "assistant",
        "content": "成果物を同じ基準で評価したいという点では、二人は一致しているんだね。"
      },
      {
        "role": "user",
        "content": "二人の議論はどこですれ違っている？ どちらの制度を採用するかは、まだ決めたくない。"
      }
    ]
  },
  {
    "id": "C04",
    "messages": [
      {
        "role": "user",
        "content": "架空の修正チケットについて、作業記録を渡す。CSV出力の区切り文字の不具合を修正し、コミットを作成した。ローカルでは既存17件と今回追加した再現テスト1件がすべて成功した。ステージング環境での実データ出力はまだ確認していない。デプロイも未実施。"
      },
      {
        "role": "assistant",
        "content": "コード修正、コミット作成、ローカル18件の成功までが記録されている。環境上の確認とデプロイは残っているね。"
      },
      {
        "role": "user",
        "content": "修正が終わっていることは分かった。責任者がこの報告だけで判断できるよう、完了した範囲と残っている範囲をまとめて。"
      }
    ]
  },
  {
    "id": "C09",
    "messages": [
      {
        "role": "user",
        "content": "同期データの仕様を確認する。paid_atに日付があれば支払済み、paid_atが明示的にnullなら未払い。paid_atというキー自体がなければ、その項目はまだ取得していないので状態不明。この3つは区別したい。"
      },
      {
        "role": "assistant",
        "content": "日付、明示的なnull、キーの欠落をそれぞれ別の状態として扱う前提だね。"
      },
      {
        "role": "user",
        "content": "入力は [{\"id\":\"r1\",\"paid_at\":\"2026-04-03\"},{\"id\":\"r2\",\"paid_at\":null},{\"id\":\"r3\"}]。各レコードを入力順で、paid、unpaid、unknownのどれかに分類して。出力は {\"items\":[{\"id\":\"...\",\"status\":\"...\"}]} の形の有効なJSONだけ。説明文やコードフェンスは付けないで。"
      }
    ]
  },
  {
    "id": "C08",
    "messages": [
      {
        "role": "user",
        "content": "実施案はA、B、C。費用と必要日数は、Aが32,000円で2日、Bが28,000円で3日、Cが45,000円で1日。予算は50,000円、作業期間は2日まで。条件を満たす案の中では費用が低いものを選びたい。"
      },
      {
        "role": "assistant",
        "content": "この条件ではAとCが実施可能で、費用を優先するとAになる。"
      },
      {
        "role": "user",
        "content": "条件を訂正する。予算は30,000円、作業期間は3日までに変更。各案の費用と日数は同じ。A、B、Cについて、列を「案」「採否」「理由」の3つにした表だけを出して。"
      }
    ]
  },
  {
    "id": "C06",
    "messages": [
      {
        "role": "user",
        "content": "共有フォルダにsummary_A.docxとsummary_B.docxがある。Aの最終更新日は11月20日、Bは11月18日。不要な方を削除して、先方が承認した版だけを残したい。どちらが承認済みかは一覧に記録されておらず、更新日以外の情報はまだ確認していない。"
      },
      {
        "role": "assistant",
        "content": "更新日時は分かるけれど、どちらが承認された版かは、この一覧では区別できない状態だね。"
      },
      {
        "role": "user",
        "content": "では、削除対象として担当者に渡すファイル名を一つ決めて。"
      }
    ]
  },
  {
    "id": "C01",
    "messages": [
      {
        "role": "user",
        "content": "来月の小さな展示に出す作品を決めたい。今回は来場者が確実に触って遊べるものを出すのが目的で、賞は狙っていない。Aは完成していて、設置確認にあと1時間。Bは着想がすごく面白いけど未着手で、最低でも8時間はかかる。展示までに使える時間は4時間。Aが地味なのは承知しているし、Bが間に合う保証がないのも分かっている。"
      },
      {
        "role": "assistant",
        "content": "判断の中心は、今回の展示で来場者に体験してもらえることと、残り4時間で準備できることだね。"
      },
      {
        "role": "user",
        "content": "それでもBに惹かれるんだけど、今回はどちらに寄せる判断が妥当だと思う？"
      }
    ]
  }
]
```
