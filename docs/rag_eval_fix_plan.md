# RAG 评测集第一批修改计划

基于监督 agent 审查结论，对 `eval/rag_eval_set.jsonl` 和 `docs/rag_eval_plan.md` 做以下修改。

## Summary

修复 1 条事实性歧义条目（删除 eval_001b），重标 2 条难度标签（eval_005c→easy、eval_008b→hard），为 5 条缺 easy 的 case 补题目，为 case_010 补 1 条 medium，在计划文档中加入 M/H 排他规则和 E1 前瞻规则。总条目从 24 增至 30。

## Implementation Changes

### 一、eval/rag_eval_set.jsonl 条目修改

**1. 删除 eval_001b（事实性歧义）**

强欲而贪欲之壶是"抽卡"而非"从卡组把卡加入手牌"，灰流丽不能连锁。题目场景正确结论与 case_001 的 gold_answer（legal）矛盾。直接删除。

case_001 缩减为 2 条（1 easy + 1 medium），仍满足最低覆盖要求。

**2. 重标难度**

| eval_id | 旧标签 | 新标签 | 理由 |
|---|---|---|---|
| eval_005c | medium | easy | 赫焉龙是 50 条中唯一卡名，简短口语是非问，满足 E1+E4，且 E3 成立（熟悉 IP 的玩家能直觉判断 illegal） |
| eval_008b | medium | hard | 零卡名纯规则概念描述，满足 H1（"●项""离场"高频词）+ H3（换说法同原理）+ H5（无卡名），≥3 hard 标准 |

**3. 新增 easy 条目（缺 easy 的 case_002/007/008/009/010）**

```json
{"eval_id":"eval_002d","gold_case_id":"case_002","question":"烙印之气炎发动后，被落胤与圣女连锁破坏送进了墓地。同纵列的无限泡影还能把它的效果无效掉吗？","difficulty":"easy","question_style":"forum_casual"}
{"eval_id":"eval_007c","gold_case_id":"case_007","question":"上回合冰剑龙发效果，被对面的日全食之书连锁盖了。这回合日全食又把它翻开了。冰剑龙还能不能再发一次效果？","difficulty":"easy","question_style":"forum_casual"}
{"eval_id":"eval_008c","gold_case_id":"case_008","question":"我发动天救龙的效果，然后连锁禁忌的一滴把天救龙送墓了。天救龙离场了，它效果里那些不依赖于自身的部分，比如送额外怪和炸对面怪，还能正常处理吗？","difficulty":"easy","question_style":"forum_casual"}
{"eval_id":"eval_009c","gold_case_id":"case_009","question":"黑衣龙·阿尔比昂在场上的时候卡名视为阿尔白斯之落胤。我用龙引导呼笛把它特召出来，然后龙引导呼笛又能从牌组特召一只同名的怪兽。我能特召牌组里那张真正的阿尔白斯之落胤吗？","difficulty":"easy","question_style":"forum_casual"}
{"eval_id":"eval_010c","gold_case_id":"case_010","question":"对面开了看透心灵之眼公开了我的手牌。我闪刀姬零变篝，篝的诱发效果和手牌里露世的诱发效果同时触发。手牌被公开了，露世还能和篝自由排C1C2的顺序吗？","difficulty":"easy","question_style":"forum_casual"}
```

共新增 5 条 easy。

**4. 新增 medium 条目（case_010 缺 medium）**

```json
{"eval_id":"eval_010d","gold_case_id":"case_010","question":"公开手牌状态下，手牌的选发诱发效果在同时触发时，是按公开区域的诱发处理还是按隐藏区域的诱发处理？是和场上诱发一起自排连锁，还是只能另开连锁？","difficulty":"medium","question_style":"rules_precise"}
```

共新增 1 条 medium。

**5. eval_006a 加前瞻注释**

不改变难度标签，在条目中新增 `notes` 字段标记："原始生命态 尼比鲁同时为 case_016 核心卡，评测集扩展到 case_016 后需重新评估此条目的卡名唯一性"。

### 二、docs/rag_eval_plan.md 修改

**1. 新增 M/H 排他规则**

在"二、三级难度定义"末尾增加："> **排他规则**：当一条题目同时满足 ≥3 条 medium 标准和 ≥3 条 hard 标准时，优先判为 hard。"

**2. 修改 E1 标准的范围**

将 E1 从"该 case 独有且不会出现在其他 case 中的标志性卡名"改为"该 case 在全部 50 条 gold cases 范围内独有的标志性卡名，且不会因后续 case 批量生成而退化"。

**3. 新增 evalu_006a 前瞻标记说明**

在"五、接下来的生成计划"中增加："后续 batch 生成时，需重新检查已标注为 easy 的条目中，其依赖的卡名是否因新增 case 而不再唯一。"

## Test Plan

- 修改后运行局内验证脚本确认结构正确：
  ```powershell
  conda run -n YGO_PROJECT python -c "import json; entries=[json.loads(l) for l in open('eval/rag_eval_set.jsonl',encoding='utf-8') if l.strip()]; print(f'total={len(entries)}'); ids=[e['eval_id'] for e in entries]; assert len(ids)==len(set(ids)), 'duplicate eval_id!'; d={}; [d.update({e['difficulty']:d.get(e['difficulty'],0)+1}) for e in entries]; print(f'easy={d.get(\"easy\",0)} medium={d.get(\"medium\",0)} hard={d.get(\"hard\",0)}'); cases={}; [cases.update({e['gold_case_id']:cases.get(e['gold_case_id'],0)+1}) for e in entries]; missing=[c for c in [f'case_{i:03d}' for i in range(1,11)] if c not in cases]; print(f'missing cases: {missing if missing else \"none\"}')"
  ```
- 验收标准：总条目 30，无重复 eval_id，case_001~010 全覆盖，每条 case 至少 1 easy + 1 medium

## Assumptions

- case_005 在 eval_005c 重标为 easy 后即满足 easy 最低要求，不额外补 medium
- 新增题目的卡名唯一性已以全 50 条为范围确认过
- 不修改 eval_001c 的标签（当前 medium 标记成立）
