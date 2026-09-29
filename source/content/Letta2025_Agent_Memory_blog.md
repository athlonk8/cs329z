---
title: "Agent Memory: How to Build Agents That Learn and Remember"
title_zh: "Agent 记忆：如何构建能学习与记忆的 Agent"
authors: "Letta Team"
venue: "Letta Blog (Concepts) · 2025-07-07"
kind: blog
importance: recommended
tags: Agent 记忆, 上下文工程, 记忆块, MemGPT, 睡眠时计算
summary: Letta 团队系统讲解 Agent 记忆的分类（消息缓冲、核心/召回/归档记忆）与构建技术，并给出"记忆即上下文工程"的统一视角。
---

## 导读

这篇博客来自 MemGPT 原班团队创办的 Letta 公司（2025 年 7 月 7 日发布于其 Concepts 栏目），是第 4 周「Agent 记忆」专题的配套工程视角材料（importance: recommended）。如果说 MemGPT 论文给出了"LLM 即操作系统"的学术原型，这篇博文则把它沉淀为一套可直接照着做的工程分类法：Agent 记忆由消息缓冲（message buffer）、核心记忆（core memory）、召回记忆（recall memory）、归档记忆（archival memory）四类组件构成，分别对应"最近消息、常驻上下文的记忆块、可检索的对话历史、外部知识库"。

全文最有价值的观点是把记忆问题统一为**上下文工程（context engineering）**：Agent"记住"什么，本质上由推理那一刻上下文窗口里有什么 token 决定；因此设计记忆就是决定"哪些 token 进入窗口、如何组织"。博文还介绍了逐出与递归摘要、记忆块管理、向量/图数据库外部存储等具体技术，以及 MemGPT 的"操作系统方法"与"睡眠时计算（sleep-time compute）"两种系统化方案，是连接本讲三篇论文（MemGPT、Mem0、生成式 Agent）与生产实践的桥梁。

## 全文中译

> 原文：Agent Memory: How to Build Agents That Learn and Remember · Letta Blog · CONCEPTS · 2025 年 7 月 7 日。以下按原文标题层级与段落结构完整翻译。

传统 LLM 运行在**无状态（stateless）**范式之中——每次交互都是孤立存在的，不会从先前的对话中携带任何知识前行。这种方式对基础任务和短生命周期的 Agent 尚可应付，但它从根本上限制了 AI 系统所能达到的高度。从无状态 LLM 向**有状态 Agent（stateful agents）**的转变，代表着一场向"真正能够随时间学习与适应的系统"的进化。

### 什么是 Agent 记忆？（What is Agent Memory?）

Agent 记忆是指你的 Agent 随时间推移**记住什么、如何记住**信息。基础的记忆可能只是回忆先前的交互，而先进的记忆系统能让 Agent 随时间学习与改进，基于累积的经验调整自身行为。

### Agent 记忆即上下文管理（Agent Memory as Context Management）

你的 Agent"记住"的东西，从根本上说是由任一时刻其**上下文窗口（context window）**中存在的内容决定的。可以把上下文窗口理解为 Agent 的**工作记忆（working memory）**——即可立即用于回答问题、推理和采取动作的信息。

因此，设计 Agent 的记忆本质上就是**上下文工程（context engineering）**：决定哪些 token 进入上下文窗口、以及它们如何被组织。记忆系统组合多种技术（如摘要 summarization、上下文改写 context rewriting、检索 retrieval）来管理多样的记忆组件（消息、记忆块 memory blocks、外部数据库）。

### Agent 记忆的类型（Types of Agent Memory）

Agent 记忆系统通常由若干各司其职的不同组件构成：

#### 消息缓冲：最近的消息（Message Buffer: Recent Messages）

消息缓冲存储对话中最近的消息。在 Letta 中，每个 Agent 维护**单一持久线程（perpetual thread）**，表示一段连续的消息序列。它提供即时的会话上下文并维持对话的连贯。

#### 核心记忆：上下文内记忆块（Core Memory: In-Context Memory Blocks）

核心记忆由**上下文内记忆块（in-context memory blocks）**构成，这些块可以由 Agent 自己管理，也可以由其他 Agent 管理。各块聚焦于特定主题，例如关于用户、组织或当前任务的记忆。比如，一个块可能存放用户偏好，另一个块维护 Agent 的人格（persona）或当前目标。关键特性在于：这些块可通过 API 编辑，并始终**固定（pinned）**在 Agent 的上下文窗口中，为"被管理的上下文单元"提供了一层抽象。

#### 召回记忆：对话历史（Recall Memory: Conversational History）

召回记忆保存完整的交互历史，可在需要时被搜索与检索——即使这些内容并不在当前活跃的上下文窗口中（也就是不在消息缓冲里）。在 Letta 中，召回记忆自动保存到磁盘，而其他框架则要求开发者手动处理持久化。

#### 归档记忆：显式存储的知识（Archival Memory: Explicitly Stored Knowledge）

归档记忆代表显式整理后、存储在外部数据库中的知识。与存储原始对话历史的召回记忆不同，归档记忆包含经过处理与索引的信息。它可以采用不同的存储形式，例如向量数据库或图数据库，并配备专门的工具将数据查询、检索回上下文窗口。

### Agent 记忆的技术（Techniques for Agent Memory）

#### 消息逐出与摘要（Message Eviction & Summarization）

Agent 记忆的一个根本挑战是管理有限的上下文窗口。摘要技术帮助在保留关键细节的同时压缩信息：

**逐出方法（Eviction Methods）：**
当上下文窗口达到容量上限时，智能逐出策略决定移除哪些信息。这可能包括：先把重要细节摘要并存储起来，再将其从活跃上下文中移除。一般来说，你应当只逐出一部分（例如 70%）消息，以保证连续性。

**递归摘要（Recursive Summarization）：**
被逐出的消息会经历递归摘要——它们会与此前已摘要消息的既有摘要一起被再次摘要。随着对话越来越长，较旧的消息对摘要的影响会逐渐小于较新的消息。

#### 管理记忆块（Managing Memory Blocks）

记忆块在 Agent 的上下文窗口内提供结构化、可编辑的存储。每个块包含：

- 一个**标签（label）**
- 一段**描述（description）**（说明该块存放什么）
- 一个**值（value）**（实际放入上下文的 token）
- 一个**字符上限（character limit）**（定义分配多少上下文窗口空间）

记忆块为自动化管理抽象了上下文窗口。Agent 可以基于新信息更新自己的记忆块，使用工具重写特定块；其他专精于记忆管理的 Agent（例如**睡眠时 Agent，sleep-time agents**）也可以修改这些块。由此形成了一种**上下文改写（context rewriting）**机制，让 Agent 能通过整合重要信息，随时间不断改进自己的上下文窗口。

#### 外部存储与检索（External Storage & Retrieval）

记忆也可以存储在外部数据库中，并通过**工具调用（tool calling）**检索。不同的存储与检索机制适用于不同的应用：

**向量数据库（Vector DBs）：** 记忆被保存、嵌入（embedding），并通过向量搜索查询。

**图数据库（Graph DBs）：** 记忆构成图结构，Agent 可以在其中遍历概念之间的关系，从而对相互关联的信息进行复杂推理。

需要强调：检索（或 RAG）是构建 Agent 记忆的一种**工具**，但它本身并不是"记忆"。

### 为 Agent 记忆构建工程系统（Engineering Systems for Agent Memory）

#### MemGPT：操作系统方法（MemGPT: The Operating System Approach）

MemGPT（MemoryGPT）是一个智能管理不同存储层级（storage tiers）的系统，能在 LLM 有限的上下文窗口内有效提供扩展上下文。MemGPT 把上下文窗口视为一种受限的内存资源，并实现了与操作系统类似的**记忆层级（memory hierarchy）**。

（原文此处配有 MemGPT 原始研究论文中的系统架构图。）

该系统提供函数调用（function calls），允许 LLM **自主管理自己的记忆**。Agent 可以在上下文内的核心记忆（类比内存 RAM）与外置存储的归档及召回记忆（类比磁盘存储）之间移动数据，从而在固定的上下文限制之内，营造出"无限记忆"的幻象。（译注：这正是本讲 MemGPT 论文的"主上下文/外置上下文 + 分页"设计在产品中的落地形态。）

#### 睡眠时计算：异步与专职的记忆 Agent（Sleep-time Compute: Asynchronous & Specialized Memory Agents）

另一种记忆思路是使用**睡眠时 Agent（sleep-time agents）**异步地管理记忆。睡眠时计算（sleep-time compute）范式对 MemGPT 原论文中的 Agent 设计做出了若干关键改进：

**非阻塞操作（Non-Blocking Operations）：**
在 MemGPT 中，记忆管理、对话和其他任务被打包在同一个 Agent 里（记忆操作期间可能导致响应变慢）；与之不同，睡眠时 Agent 异步处理记忆管理，同时改善了响应速度与记忆质量。

**前瞻式记忆精炼（Proactive Memory Refinement）：**
不再依赖对话期间懒惰的增量式更新，记忆可以在空闲时段被重新组织与改进。这种方式能产生更高质量的记忆块，实现随时间推进的学习与记忆形成，此外还与 Agent 的交互延迟相互解耦。

### 人类记忆与 Agent 记忆的类比（Analogies Between Human and Agent Memory）

虽然把人类记忆与人工记忆直接类比很诱人，但必须记住：LLM 本质上是"文本进、文本出"的系统。它们的"记忆"仅由其上下文窗口中存在的内容构成。

与其硬编码仿人类的记忆结构，我们应当专注于**上下文工程**——设计能在推理时有效管理模型可用信息的系统。这包括设计：

- 上下文窗口如何组织（决定消息缓冲大小与记忆块设计）；
- 检索归档记忆的工具，把外部存储的上下文拉回窗口；
- 帮助 Agent 理解自身记忆局限、并利用上下文内与外部记忆加以克服的提示词。

目标不是复刻人类记忆的机制，而是构建能让 Agent 在 LLM 的 token 范式内真正有用、保持一致、并具备学习能力的记忆系统。

### 短期 vs. 长期 Agent 记忆（Short-term vs. Long-term Agent Memory）

Agent 的"短期"记忆由消息缓冲中的一切内容构成，因为这些内容终将被逐出；其余所有记忆类型都算"长期"。不过，更有用的方式是把 Agent 记忆概念化为上下文工程：理解什么在、什么不在上下文窗口中，以及 token 如何被拉回上下文窗口。归根结底，记忆就是关于"在任一时刻选择把哪些 token 放进你的上下文窗口"。

### 结论（Conclusion）

Agent 记忆是 AI 发展中最关键的前沿之一。Agent 记忆的未来不在于任何单一技术，而在于多种思路的审慎组合：细致的逐出与摘要、智能的记忆块管理，以及复杂的外部上下文存取系统。

如果你想构建能形成记忆、随时间学习并变得更智能、更个性化的 Agent，可以了解 Letta API 与 Letta Code。

（原文页尾为邮件订阅入口：MAILING LIST — SUBSCRIBE →）

## 要点速览

- 核心命题：Agent"记住"什么 = 推理时上下文窗口里有什么；设计记忆就是上下文工程——决定哪些 token 进窗口、如何组织。
- 四类记忆组件：消息缓冲（最近消息，Letta 中是单一持久线程）、核心记忆（常驻上下文、可经 API 编辑的记忆块）、召回记忆（可搜索的完整对话历史）、归档记忆（外部数据库中经过处理与索引的知识）。
- 记忆块的四个要素：标签、描述、值（真正进上下文的 token）、字符上限；Agent 可用工具自行重写记忆块，专职的记忆管理 Agent（如睡眠时 Agent）也能代改。
- 容量管理技术：窗口满时智能逐出（一般只逐约 70% 以保持连续性）+ 递归摘要（旧消息对摘要的影响随对话变长而递减）。
- 外部存储两条路线：向量数据库（嵌入 + 向量搜索）与图数据库（遍历概念关系做复杂推理）；RAG 只是实现记忆的工具，本身不等于记忆。
- 系统化方案一：MemGPT 操作系统方法——LLM 通过函数调用在核心记忆（RAM）与归档/召回记忆（磁盘）间自主搬移数据，营造无限记忆幻象。
- 系统化方案二：睡眠时计算——记忆管理异步化、非阻塞，并在空闲期前瞻式重组记忆，同时提升响应速度与记忆质量。
- 不要照搬人类记忆结构：LLM 是文本进文本出的系统，应从上下文组织、检索工具、元认知提示词三方面做工程设计。
- 短期记忆 = 消息缓冲（终将被逐出），其余皆长期；但更实用的心智模型是"上下文工程"而非"短期/长期"二分。
- 本文与课程材料的呼应：MemGPT 论文是分级存储的源头，Mem0 是抽取-更新式记忆管理的实例，本文给出统一的概念框架。
