# Endocrine Knowledge Base Operations Guide

## 环境要求
- Python 3.9+，已安装项目根目录下 `requirements.txt` 所列依赖
- 命令需在目录 `01_主题验证/08_AI与数据科学/Knowledge_Graph/` 内执行

## 一键生成/更新流程
运行脚本 `run_knowledge_pipeline.sh` 可完成以下动作：
1. 读取 `comprehensive_endocrine_knowledge_graph.json`
2. 重新生成 `modular_endocrine_knowledge/` 目录下全部 CSV，并写入 `evidence_source`
3. 构建专题子集
   - `subsets/pregnancy_endocrine.csv`
   - `subsets/endocrine_bone.csv`
   - `subsets/pediatric_endocrine.csv`

```bash
./run_knowledge_pipeline.sh
```

## 示例：带检索的运行方式
脚本最后会在有查询参数时调用 `rag_demo.py` 做检索演示：

```bash
./run_knowledge_pipeline.sh "妊娠期糖尿病 管理要点"
```

输出将显示最相关的知识条目及其来源文件、`evidence_source` 字段。

## 自定义子集
使用 `create_subset.py` 可基于关键词生成其他主题包：

```bash
python3 create_subset.py <output.csv> <keyword1> <keyword2> ...
```

生成文件保存在 `modular_endocrine_knowledge/subsets/`，字段与主 CSV 一致。

## 数据校验与版本管理
- 所有生成脚本和 CSV 均纳入 Git 管理；更新后运行 `git status` 查看变动。
- 可在提交说明中注明引用指南版本，便于后续审计。
