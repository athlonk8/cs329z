---
title: "Stanford Just Put an $850K/Year Skill on YouTube for Free"
title_zh: "年薪 85 万美元的绝活,斯坦福免费公开了——为什么值得学这门课"
authors: 中译全文转载(微信公众号文章)
venue: "Medium 原文 · dare-to-be-better(2026)"
kind: blog
importance: recommended
tags: 课程背景,CS329A,职业发展,自我改进智能体
summary: Anthropic 为能构建自我进化型 AI 智能体的工程师开出最高 85 万美元年薪;斯坦福把教这门手艺的 CS329A 课程完整免费公开。本文是这门课为什么值钱的最好注脚。
---

## 导读

本页是学习站的背景阅读:一篇在中文圈广泛传播的课程评论文章。它解释了 CS 329Z / CS329A 这类"智能体工程"课程背后的产业现实——Anthropic 的 Research Engineer, Agents 岗位年薪 50-85 万美元,需要的正是本站所覆盖的技能:设计 agent harness、建立严格的智能体 benchmark、优化训练数据。文章同时介绍了 CS 329Z 的"前身" **CS 329A《Self-Improving AI Agents》**(斯坦福 2025 秋,Aakanksha Chowdhery 与 Azalia Mirhoseini 主讲,17 讲视频全部免费公开)。读它,你就知道接下来 17 个专题的学习终点在哪里。

## 全文中译

> 以下为文章全文(图片略)。原文链接见本页底部"延伸资源"。

Anthropic 愿意为能构建自我进化型 AI 智能体的工程师开出最高 85 万美元年薪。斯坦福刚刚把教这门手艺的课程完整公开,而主讲人之一参与过 Claude 的研发。

先说个数:Anthropic 正在招的「Research Engineer, Agents」岗位,年薪标的是 50 万到 85 万美元。不含股票期权那套算法,就是实打实的工资。同序列的 Code RL 岗位——教 Claude 写代码、发布真正可用的软件——也是这个区间。

更夸张的是:就在一周前,斯坦福把教这门手艺的整套课程原样公开了。免费,不用申请,不用交七万美元学费。

你不得不服。知识已经便宜到这种地步,我们再也没借口了。

### 这门课

课程代号 CS329A:Self-Improving AI Agents,斯坦福 2025 年秋季研究生课,由 Aakanksha Chowdhery 和 Azalia Mirhoseini 主讲。最近被完整放出,第一部分播放量已破 20 万,显然不只有我一个人盯着它。

主讲人值得一提。

Aakanksha Chowdhery 主导过 Google 540B 参数 PaLM 模型的训练,那是当时全球最大的稠密训练语言模型;她还推动了 Gemini MoE 模型的预训练。Azalia Mirhoseini 现在执掌斯坦福 Scaling Intelligence 实验室,此前先后在 Google Brain、Google DeepMind 和 Anthropic 工作过——没错,她参与过 Claude 的研发。

再看一遍这句话:这门免费课程的主讲人之一,亲自参与过 Claude 的研发。Anthropic 愿意为这门手艺开出最高 85 万美元年薪,而会做这件事的人,现在免费给你讲课。

### "自我进化型智能体"到底指什么

说实话,「AI agents」这个词现在已经被用滥了,说什么都像,说什么又都不像。这门课讲的是更具体的东西:能通过交互不断变强的智能体,既跟工具交互,也跟环境交互,还跟它自己交互。

课程内容包括:测试时算力扩展(靠让模型想得更久来变聪明,无需重新训练)、验证器与奖励信号、训练阶段的强化学习、多步推理与规划、给智能体加上记忆和工具,还有我觉得最有趣的一块——长程任务评估。这个方向上,大多数智能体现在还默默翻车。

如果你用过 Claude Code 或者其他深度研究工具,其实早就摸到过这些技术的产物。第一讲完整走了这条弧线:从单次对话的聊天机器人,到编排器加工人的智能体模式,拿 Claude Code 当活例子。

### 这门手艺,为什么现在值钱

整套课程共 17 讲。嘉宾讲师包括 Google DeepMind 的 Denny Zhou、Thang Luong,Reflection AI 的 Misha Laskin,以及 Physical Intelligence 的 Danny Driess。里面没有「十个 ChatGPT 提示词让你效率翻十倍」那种水货,全是正儿八经的硬货。

看看 Anthropic 那则招聘到底要什么:设计 agent harness、为大规模 agentic 任务建立严格 benchmark、优化训练数据以提升智能体表现。这已经超出提示工程的范畴,是一门介于研究与工程之间的新学科,现在几乎没人真正掌握——所以它才能给出六位数的年薪。

各家实验室现在押的是同一个注:下一波突破不只靠更大的基座模型,而是靠能自我提升的智能体——靠搜索、靠验证、靠真实任务上的强化学习。谁把这个闭环吃透了,就是各大前沿实验室抢着要的人。

### 再没有借口了

十年前,这套知识可能只掌握在三五家公司和少数几个博士项目手里。五年前,你得坐在斯坦福的教室里才能听。今天,教室变成了一份公开播放清单,课程大纲和阅读列表都挂在公开网页上。

这正是「旧时王谢堂前燕,飞入寻常百姓家」——昔日王侯府邸的燕子,如今也飞进了寻常人家。

我不是说听完 17 讲就能拿 85 万美元年薪。不能。真正拿到 offer 的人,背后都有多年的动手训练经验。但你和那份工作之间,原本有一道门槛叫「有没有门路拿到知识」,现在这道门槛已经薄得像张纸。剩下的,是你真正能掌控的部分:去做。

### 我会怎么学

别像追剧一样一次性刷完,那样你什么都留不住。每周完整听完一讲,旁边开着课程页面,同步看论文。每听完一讲,就动手做一个用到这个点子的小东西。公开做、边做边记。

如果刚听完测试时算力那讲,周末就用个简单验证器实现 best-of-N 采样。如果刚听完记忆那讲,给你已有的智能体接上一层记忆。

课程大纲、日程和阅读清单都已公开。如果你想要带学分的版本,斯坦福也提供在线研究生课程 XCS329,但真正的干货——讲课视频本身——已经放在那里等你。

知识已经免费。接下来值钱的是行动。

纸上得来终觉浅,绝知此事要躬行。

## 要点速览

- **产业信号**:Anthropic「Research Engineer, Agents」与 Code RL 岗位年薪 50-85 万美元,要求正是:设计 agent harness、建严格 benchmark、优化训练数据——恰好对应本站第 5/7/8/9 周的内容。
- **CS 329A**(2025 秋)是 CS 329Z(2026 秋,本站材料)的前身课程:同属"智能体工程"脉络,17 讲视频免费公开于 Stanford Online 的 YouTube 频道。
- 讲师阵容:Aakanksha Chowdhery(PaLM 540B 训练负责人、Gemini MoE 预训练)+ Azalia Mirhoseini(斯坦福 Scaling Intelligence 实验室,曾参与 Claude 研发)。
- **"自我进化智能体"的技术栈** = 本站学习路径:测试时计算扩展(第 5 周 Snell)→ 验证器与奖励(第 5/8 周)→ RL 训练 → 多步推理与规划(ReAct,第 4 周)→ 记忆与工具(第 3/4 周)→ 长程任务评估(第 7/9 周)。
- 学习方法建议:每周一讲 + 同步读论文 + 动手做小项目,公开做、边做边记——与本站"精读 + 原文对照"的用法一致。

## 延伸资源

- **CS 329A 课程官网**(大纲、日程、阅读清单):https://cs329a.stanford.edu/
- **讲课视频**:Stanford Online 的 YouTube 频道(搜索 "Stanford CS329A Self-Improving AI Agents")
- **带学分在线版 XCS329**:见 Stanford Online(online.stanford.edu)
- **本文原文(Medium)**:https://medium.com/dare-to-be-better/stanford-just-put-an-850k-year-skill-on-youtube-for-free-2f131d993219
- **本课(CS 329Z)官网**:https://cs329z.stanford.edu/
