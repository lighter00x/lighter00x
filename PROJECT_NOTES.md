# 项目简介依据

整理日期：2026-10-26。简介概括仓库所提供的功能，不宣称代码全部原创、实验已独立复现或效果优于基线。此文件用于以后维护主页文案。

| 项目 | 本次读取的材料 | 简介重点 |
| --- | --- | --- |
| OPD-Rethinker | `compose.yaml`、`data/OPD/on_policy_distillation.sh`、`data/OPD/run_opd_verl09.sh`、脚本目录 | 在线策略蒸馏、GRPO、多节点教师/学生部署配置、推理评测及指标同步脚本。顶层没有 README，不能直接把内置 LlamaFactory 或 verl 的功能当作本项目独立贡献。 |
| BitCons-AT | 顶层 README、训练/评测/攻击配置目录 | 位平面、对抗训练、低位视图搜索与一致性约束、消融及攻击评测。不采用未经核实的性能与 SOTA 宣称。 |
| PaperParser | 顶层 README、解析/检测/识别/处理目录 | LLM 论文信息提取、化合物及构效关系、分子检测识别、批量与连续处理。 |
| doc_operation | 顶层 README、流水线及布局合并模块 | MinerU 解析、VLM 页内/跨页布局合并、Markdown/PDF 导出。 |
| SearchAgent-Ascend | 顶层 README | SearchAgent-Zero 在昇腾 NPU 上的适配，保留上游归属；多轮工具、远端检索和训练监控。 |
| hot100 | 顶层 README、题库与索引脚本目录 | 内置 100 题、名称/编号/关键词匹配、题解与复杂度、ACM Python 参考代码。 |
| legacy_mineru_merge | 顶层 README、服务/客户端/流水线模块 | 独立旧版 MinerU 流水线、VLM 布局合并、HTTP 服务与批处理。 |
| paper_extract | 顶层 README、入口与处理模块目录 | 医药分子论文处理；部分权重、路径及 API 配置需自行准备，不写为开箱即用。 |
| BitCons | 仓库接口返回空仓库 | 不添加虚构功能介绍，也不列为主要展示项目。 |
| lighter00x.github.io | 已维护的个人博客 | 作为博客与文章入口，不重复列成研究项目。 |

修改项目功能后，先更新相应仓库 README，再同步本主页的简介。不要把仓库语言统计理解成研究成果或熟练度排名。
