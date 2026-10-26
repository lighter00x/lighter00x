# 个人主页维护

这是 `lighter00x/lighter00x` 同名公开仓库，根目录 README 会显示在 GitHub 个人主页。

## 修改内容

- `README.md`：个人介绍、链接和项目入口。项目展示由你自行选择，避免用自动排名代替个人重点。
- `assets/header.svg`：原创横幅，SVG 可直接编辑文字、颜色和形状。
- `scripts/update_profile.py`：从 GitHub 公开接口生成紧凑概览 SVG，仅展示仓库数量和主要语言；不读取活动事件、博客或修改 README。
- `assets/projects.svg`：自动生成，请优先修改脚本。

整体配色为午夜蓝、亮蓝与纯白；项目卡片用原生 Markdown/HTML，适应 GitHub 明暗主题。不依赖第三方统计卡片服务。

## 自动更新

GitHub Actions 每日北京时间约 06:17 运行，也可在 Actions → Refresh profile → Run workflow 手动执行。推送 README、横幅、脚本或工作流修改也会更新。

使用 GitHub 自动提供的 `GITHUB_TOKEN`，不需要额外保存个人访问令牌。只请求公开数据。

本地运行：

```bash
python scripts/update_profile.py
```

不需要安装第三方 Python 包。不设置令牌也能读取公开数据，但受未认证接口速率限制。需要时可通过环境变量 `GITHUB_TOKEN` 提供凭据，请勿提交凭据。

## 数据口径

- 公开仓库：当前账号拥有且公开的仓库数量。
- 语言：非 fork 公开仓库的主要语言，每个仓库计一次；不是代码行数或熟练度排名。

概览不显示活动柱状图、提交排行或最近更新时间；仓库数据没有变化时，不产生新的自动提交。

若接口请求失败，工作流失败并保留现有展示文件，不会用零数据覆盖。GitHub 定时任务可能延迟；长时间不活跃的公开仓库，定时任务可能被平台停用，可手动重新启用。
