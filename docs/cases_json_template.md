# Cases JSON 模板

本文档提供可复制的 case 模板。正式 `gold_cases/operation_legality_cases.jsonl` 中每一行必须是一个完整 JSON object，不写 `//` 或 `/* */` 注释。
格式化人工审阅镜像保存在 `gold_cases/json/caseNNN.json`，并必须与主 JSONL 对应对象完全一致。

字段含义、允许值、`operation_type` 与 `effect_features` 固定枚举见：

```text
schema.md
```

---

# 1. 发动 / 连锁合法性模板

用于判断某张卡或某个效果是否可以在当前窗口发动，或是否可以连锁当前连锁块。

```json
{
  "id": "case_xxx",
  "task_type": "operation_legality_judgment",
  "schema_version": "2.1.0",
  "question": "当前这个操作是否在规则内合法？",
  "natural_language_context": "",
  "rule_context": {
    "game": "Yu-Gi-Oh!",
    "format": "OCG",
    "language": "zh",
    "rule_version": "unspecified"
  },
  "pre_state": {
    "phase": "main_phase_1",
    "step": null,
    "damage_step_timing": null,
    "turn_player": "opponent",
    "chain_state": {
      "is_chain_building": true,
      "is_chain_resolving": false,
      "current_chain_links": [
        {
          "chain_id": "C1",
          "player": "opponent",
          "card": "",
          "operation_type": "activate_card",
          "effect_id": "main_effect",
          "effect_summary": "",
          "effect_features": [],
          "activation_start_location": "",
          "activation_location": "",
          "activation_zone": "",
          "activation_column_index": null
        }
      ]
    },
    "resolution_history": [],
    "self_state": {
      "hand": [],
      "field": {
        "monster_zones": {
          "m1": { "column_index": 1, "card": null },
          "m2": { "column_index": 2, "card": null },
          "m3": { "column_index": 3, "card": null },
          "m4": { "column_index": 4, "card": null },
          "m5": { "column_index": 5, "card": null }
        },
        "spell_trap_zones": {
          "s1": { "column_index": 1, "card": null },
          "s2": { "column_index": 2, "card": null },
          "s3": { "column_index": 3, "card": null },
          "s4": { "column_index": 4, "card": null },
          "s5": { "column_index": 5, "card": null }
        },
        "field_spell_zone": null,
        "extra_monster_zones": {
          "emz_left": { "column_index": null, "card": null },
          "emz_right": { "column_index": null, "card": null }
        }
      },
      "graveyard": [],
      "banished": [],
      "used_effects_this_turn": []
    },
    "opponent_state": {
      "hand": [],
      "field": {
        "monster_zones": {
          "m1": { "column_index": 5, "card": null },
          "m2": { "column_index": 4, "card": null },
          "m3": { "column_index": 3, "card": null },
          "m4": { "column_index": 2, "card": null },
          "m5": { "column_index": 1, "card": null }
        },
        "spell_trap_zones": {
          "s1": { "column_index": 5, "card": null },
          "s2": { "column_index": 4, "card": null },
          "s3": { "column_index": 3, "card": null },
          "s4": { "column_index": 2, "card": null },
          "s5": { "column_index": 1, "card": null }
        },
        "field_spell_zone": null,
        "extra_monster_zones": {
          "emz_left": { "column_index": null, "card": null },
          "emz_right": { "column_index": null, "card": null }
        }
      },
      "graveyard": [],
      "banished": [],
      "used_effects_this_turn": []
    },
    "known_constraints": []
  },
  "attempted_operation": {
    "player": "self",
    "operation_type": "activate_effect",
    "card": "",
    "effect_id": "main_effect",
    "activation_location": "",
    "chain_response_to": "C1",
    "declared_cost": [],
    "declared_targets": [],
    "declared_effect_purpose": ""
  },
  "gold_answer": {
    "label": "depends",
    "conclusion": "",
    "failed_check": "unknown_missing_info",
    "reasoning_steps": [],
    "missing_info": [],
    "required_sources": [
      {
        "id": "src_case_xxx_01",
        "source_type": "official_card_text",
        "authority": "KONAMI",
        "title": "官方卡片详情标题",
        "url": "https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid=12950&request_locale=ja",
        "official_id": "cid:12950",
        "language": "ja",
        "accessed_at": "YYYY-MM-DD",
        "supports_reasoning_steps": [1],
        "lookup_query": "卡片名"
      }
    ]
  },
  "case_notes": ""
}
```

---

# 2. 效果处理合法性模板

用于判断某个连锁块在处理时，声明的处理方式是否合法。

```json
{
  "id": "case_xxx",
  "task_type": "effect_resolution_judgment",
  "schema_version": "2.1.0",
  "question": "当前这个处理是否在规则内合法？",
  "natural_language_context": "",
  "rule_context": {
    "game": "Yu-Gi-Oh!",
    "format": "OCG",
    "language": "zh",
    "rule_version": "unspecified"
  },
  "pre_state": {
    "state_timing": "before_resolving_C1",
    "phase": "main_phase_1",
    "step": null,
    "damage_step_timing": null,
    "turn_player": "opponent",
    "chain_state": {
      "is_chain_building": false,
      "is_chain_resolving": true,
      "current_chain_links": [
        {
          "chain_id": "C1",
          "player": "opponent",
          "card": "",
          "operation_type": "activate_card",
          "effect_id": "main_effect",
          "effect_summary": "",
          "effect_features": [],
          "activation_start_location": "",
          "activation_location": "",
          "activation_zone": "",
          "activation_column_index": null
        }
      ]
    },
    "resolution_history": [],
    "self_state": {
      "hand": [],
      "field": {
        "monster_zones": {
          "m1": { "column_index": 1, "card": null },
          "m2": { "column_index": 2, "card": null },
          "m3": { "column_index": 3, "card": null },
          "m4": { "column_index": 4, "card": null },
          "m5": { "column_index": 5, "card": null }
        },
        "spell_trap_zones": {
          "s1": { "column_index": 1, "card": null },
          "s2": { "column_index": 2, "card": null },
          "s3": { "column_index": 3, "card": null },
          "s4": { "column_index": 4, "card": null },
          "s5": { "column_index": 5, "card": null }
        },
        "field_spell_zone": null,
        "extra_monster_zones": {
          "emz_left": { "column_index": null, "card": null },
          "emz_right": { "column_index": null, "card": null }
        }
      },
      "graveyard": [],
      "banished": [],
      "used_effects_this_turn": []
    },
    "opponent_state": {
      "hand": [],
      "field": {
        "monster_zones": {
          "m1": { "column_index": 5, "card": null },
          "m2": { "column_index": 4, "card": null },
          "m3": { "column_index": 3, "card": null },
          "m4": { "column_index": 2, "card": null },
          "m5": { "column_index": 1, "card": null }
        },
        "spell_trap_zones": {
          "s1": { "column_index": 5, "card": null },
          "s2": { "column_index": 4, "card": null },
          "s3": { "column_index": 3, "card": null },
          "s4": { "column_index": 2, "card": null },
          "s5": { "column_index": 1, "card": null }
        },
        "field_spell_zone": null,
        "extra_monster_zones": {
          "emz_left": { "column_index": null, "card": null },
          "emz_right": { "column_index": null, "card": null }
        }
      },
      "graveyard": [],
      "banished": [],
      "used_effects_this_turn": []
    },
    "known_constraints": []
  },
  "attempted_operation": {
    "player": "opponent",
    "operation_type": "resolve_effect",
    "card": "",
    "effect_id": "main_effect",
    "effect_label": "",
    "chain_id_to_resolve": "C1",
    "activation_location_at_activation": "",
    "activation_zone_at_activation": "",
    "activation_column_index": null,
    "current_card_location": "",
    "declared_resolution": "",
    "declared_effect_purpose": ""
  },
  "gold_answer": {
    "label": "depends",
    "conclusion": "",
    "failed_check": "unknown_missing_info",
    "reasoning_steps": [],
    "missing_info": [],
    "required_sources": [
      {
        "id": "src_case_xxx_01",
        "source_type": "official_ruling",
        "authority": "KONAMI",
        "title": "官方Q&A标题",
        "url": "https://www.db.yugioh-card.com/yugiohdb/faq_search.action?ope=5&fid=23173&request_locale=ja",
        "official_id": "fid:23173",
        "language": "ja",
        "source_updated_at": "YYYY-MM-DD",
        "accessed_at": "YYYY-MM-DD",
        "supports_reasoning_steps": [1]
      }
    ]
  },
  "case_notes": ""
}
```

---

# 3. 填写规则速查

- `operation_type` 只能使用 `schema.md` 中的固定枚举。
- `effect_features` 只能使用 `schema.md` 中的固定枚举。
- `schema_version` 当前固定为 `"2.1.0"`。
- `required_sources` 必须是已解析到 URL 的证据对象，不能只填写 `query`。
- 正式 gold case 至少包含一项官方卡片文本，以及一项官方 Q&A 或规则书。
- 连锁编号统一使用 `"C1"`、`"C2"`、`"C3"`，不要使用 `1`、`2`、`3`。
- 场地区域使用固定槽位对象，不使用空数组表达区域。
- 空位统一写 `"card": null`。
- 判断同纵列只比较 `column_index`。
- 发动类 case 通常使用 `is_chain_building: true`、`is_chain_resolving: false`。
- 所有 case 都必须显式填写 `resolution_history`；没有已处理连锁块时写 `[]`。
- 效果处理类 case 通常使用 `is_chain_building: false`、`is_chain_resolving: true`，并填写 `state_timing`、`resolution_history`。
- `resolution_history` 只记录当前判断点之前已经按连锁逆顺处理完成的连锁块；未处理的计划、持续限制和规则解释不要写入这里。
- 正式 JSONL 中不要写 Markdown，不要写注释，每个 case 压成单行 JSON。
