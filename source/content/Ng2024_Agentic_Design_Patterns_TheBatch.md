---
title: "Agentic Design Patterns Part 1: Four AI Agent Strategies That Improve GPT-4 and GPT-3.5 Performance"
title_zh: Agentic 设计模式(一):四种提升 GPT-4 与 GPT-3.5 表现的 AI Agent 策略
authors: Andrew Ng
venue: "The Batch 2024 · DeepLearning.AI"
kind: blog
importance: recommended
tags: Agent工作流,设计模式,Reflection,Tool Use,Planning,多智能体协作
summary: 吴恩达提出反思、工具使用、规划、多智能体协作四大 Agentic 设计模式,并指出迭代式 Agent 工作流的提升远超模型换代。
---

## 导读

本文是吴恩达(Andrew Ng)在 DeepLearning.AI《The Batch》通讯上发表的「Agentic 设计模式」系列开篇(2024 年 3 月 20 日),被安排在第 1 周课程导论中,用来建立对「什么是 Agentic 工作流」的第一印象。文章的核心论点是:今年 AI 的最大进步可能不是来自下一代基础模型,而是来自 Agent 工作流。作者用 HumanEval 编程基准的数据说明:GPT-3.5 零样本正确率为 48.1%,GPT-4 零样本为 67.0%,而把 GPT-3.5 包裹进迭代式 Agent 循环后最高可达 95.1%——工作流带来的增益远超模型换代。在此基础上,文章给出了一个日后被广泛引用的 Agentic 设计模式分类框架:反思(Reflection)、工具使用(Tool Use)、规划(Planning)与多智能体协作(Multi-agent collaboration),为整个课程的 Agent 主题提供了概念地图。

## 全文中译

# Agentic 设计模式(一):四种提升 GPT-4 与 GPT-3.5 表现的 AI Agent 策略

 Letters · Technical Insights
 发布时间:2024 年 3 月 20 日 · 阅读时长 2 分钟

各位朋友:

我认为 AI Agent 工作流将在今年推动大规模的 AI 进步——甚至可能超过下一代基础模型带来的进步。这是一个重要的趋势,我敦促每一位从事 AI 工作的人都加以关注。

如今,我们大多以零样本(zero-shot)方式使用 LLM:提示模型逐个 token 地生成最终输出,中途不修改自己的工作。这就好比要求一个人从头到尾一气呵成地写完一篇文章,不允许任何回退修改,却期望得到高质量的结果。尽管难度很大,LLM 在这项任务上的表现已经相当惊艳!

然而,借助 Agent 工作流,我们可以让 LLM 对一份文档进行多轮迭代。例如,它可以执行这样一系列步骤:

- 规划一份提纲。
- 判断是否需要进行网络搜索来收集更多信息。
- 撰写初稿。
- 通读初稿,找出论据不足或内容冗余之处。
- 根据发现的问题修改草稿。
- 依此往复。

对大多数人类作者而言,这种迭代过程是写出好文章的关键。对 AI 来说,这种迭代式工作流同样能带来远好于一次性写作的结果。

Devin 高调的演示最近在社交媒体上引发了大量讨论。我的团队一直在密切跟踪「会写代码的 AI」的演进。我们分析了多个研究团队的成果,关注算法在广泛使用的 HumanEval 编程基准上的表现。你可以在下图中看到我们的发现。

[图:各团队方法在 HumanEval 基准上的准确率对比——GPT-3.5(zero-shot)48.1%,GPT-4(zero-shot)67.0%,Agent 循环中的 GPT-3.5(AI Agent 训练)最高 95.1%]

GPT-3.5(zero-shot)的正确率为 48.1%,GPT-4(zero-shot)更好一些,为 67.0%。然而,与引入迭代式 Agent 工作流所带来的提升相比,从 GPT-3.5 到 GPT-4 的进步就显得微不足道了。事实上,在 Agent 循环的加持下,GPT-3.5 的正确率最高可达 95.1%。

开源 Agent 工具和关于 Agent 的学术文献正在快速涌现,这让当下既令人兴奋,也令人困惑。为了帮助大家正确地看待这些工作,我想分享一个用于归类 Agent 设计模式的框架。我的团队 AI Fund 已在许多应用中成功使用了这些模式,希望它们对你同样有用。

- **反思(Reflection)**:LLM 审视自己的工作,想出改进它的方法。
- **工具使用(Tool Use)**:为 LLM 提供网络搜索、代码执行或任何其他工具,帮助它收集信息、采取行动或处理数据。
- **规划(Planning)**:LLM 制定并执行一个多步骤计划来实现目标(例如,先为文章写提纲,然后上网调研,再写出草稿,依此类推)。
- **多智能体协作(Multi-agent collaboration)**:多个 AI Agent 协同工作,拆分任务、讨论并辩论想法,从而得出单个 Agent 难以企及的更优解决方案。

下周,我将详细展开这些设计模式,并为每个模式提供推荐阅读。

保持学习!

Andrew

**延伸阅读(本系列后续篇目):**
- 《Agentic 设计模式(二):反思》
- 《Agentic 设计模式(三):工具使用》
- 《Agentic 设计模式(四):规划》
- 《Agentic 设计模式(五):多智能体协作》

## 要点速览

- 吴恩达判断:2024 年 AI 的最大推动力可能是 Agent 工作流,甚至超过下一代基础模型。
- 零样本使用 LLM 类似于「一次成稿、不许回退」的写作方式;Agent 工作流则允许多轮「规划—起草—审阅—修改」的迭代。
- 关键数据:HumanEval 上 GPT-3.5 零样本 48.1%、GPT-4 零样本 67.0%,而 Agent 循环中的 GPT-3.5 最高达 95.1%,工作流增益远超模型升级。
- 四大 Agentic 设计模式:反思(Reflection)、工具使用(Tool Use)、规划(Planning)、多智能体协作(Multi-agent collaboration)。
- 反思 = 让模型审视并改进自己的输出;工具使用 = 赋予模型搜索、执行代码等能力。
- 规划 = 模型自主制定并执行多步骤计划;多智能体协作 = 多个 Agent 分工、讨论、辩论以获得更优解。
- 该分类框架是后续四周系列文章的总纲,也是本课程 Agent 部分的重要概念基础。
