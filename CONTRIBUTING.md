# 贡献指南

感谢你愿意帮忙改进这个翻译项目!错译在所难免,每一处纠错都会让数千读者受益。

## 报告错译(最简单的方式)

1. 打开 [Issues](https://github.com/athlonk8/cs329z/issues/new/choose),选择「译文纠错」模板
2. 填写:阅读页面链接、原文位置(小节名即可)、现有译文、建议译文
3. 提交即可,无需会写代码

## 直接提交译文修改(PR)

### 全译对照文件的格式

论文源文件在 `source/content/bilingual/*.md`,每段是「英文原文块 + 中文段落」成对出现:

```markdown
::: en
Original English paragraph...
:::

对应的中文译文段落……
```

修改时**只改中文段落,不要动 `::: en` 块**(它是对照的原文)。

### 翻译守则

- **术语对照**(常见约定,保持一致):
  - agent → 智能体;benchmark → 基准(测试)
  - tool use → 工具调用;prompt → 提示(词);in-context learning → 上下文学习
  - 首次出现的专有名词、系统名、数据集名保留英文(如 ReAct、SWE-bench、DSPy)
- **数字、模型名、引用标记**(如 [12]、Figure 3)**与原文严格一致**
- **公式不翻译**,保持 LaTeX 原样
- 长句优先拆分,不为通顺牺牲准确性,也不为准确牺牲可读性

### 构建与验证

```bash
cd source
pip install -r ../requirements.txt
python3 build.py                    # 构建到 source/site/
python3 -m http.server -d site 8329 # 本地预览 http://127.0.0.1:8329
```

确认改动渲染正常后提交 PR。如果是 UI/排版改动,请在 PR 里附截图。

## 同步新讲义 / 新材料

课程官网会随进度放出讲义和作业:

1. 下载 PDF 放入仓库根目录 `slides/`(命名 `lectureNN.pdf`)
2. 在 `source/build.py` 的 `LECTURES` 列表加一行(讲次/日期/主题/文件名/官网链接)
3. 维护者本地重新构建并推送,线上自动部署

## 其他

- 新功能想法、网站问题、合作意向都欢迎开 Issue 讨论
- 保持友善,对事不对人 🤝
