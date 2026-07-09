# YGO_PROJECT 开发环境

本项目使用独立的 Anaconda 环境 `YGO_PROJECT`。

## 首次创建

在仓库根目录执行：

```powershell
conda env create -f environment.yml
conda activate YGO_PROJECT
python check_jsonlschema.py --self-test
```

## 已存在环境时同步依赖

```powershell
conda env update -n YGO_PROJECT -f environment.yml --prune
```

也可在不激活环境的情况下运行：

```powershell
conda run -n YGO_PROJECT python check_jsonlschema.py --self-test
```

## 验证解释器与依赖

```powershell
python --version
python -c "import sys, importlib.metadata; print(sys.executable); print(sys.version); print(importlib.metadata.version('jsonschema'))"
```

Schema 默认路径为 `docs/operation_case.schema.json`；校验器默认读取
`gold_cases/operation_legality_cases.jsonl`，通常无需额外传参。
格式化镜像 JSON 位于 `gold_cases/json/`，默认自测会检查其与主 JSONL 一致。
