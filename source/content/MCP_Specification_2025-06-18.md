---
title: "Model Context Protocol Specification (Version 2025-06-18)"
title_zh: 模型上下文协议（MCP）规范（2025-06-18 版）
authors: Model Context Protocol 项目（modelcontextprotocol.io）
venue: "官方规范网页 · modelcontextprotocol.io · Version 2025-06-18"
kind: blog
importance: must
tags: MCP, 协议规范, JSON-RPC, 工具调用, Host/Client/Server, 安全与信任
summary: MCP 官方规范概览页全文中译：开放协议以 JSON-RPC 2.0 连接 Host/Client/Server 三角色，定义 Server 与 Client 双方能力及安全信任原则。
---

## 导读

本文是第 3 周"工具调用与 MCP"专题的核心材料。MCP（Model Context Protocol，模型上下文协议）是一个开放协议，为 LLM 应用接入外部数据源与工具提供标准化方式，被称为"AI 应用的 USB-C 接口"。本页是 2025-06-18 版官方规范站的概览页（Specification/Overview），它规定了整个协议的骨架：架构上的三种角色（Host、Client、Server）、通信基础（JSON-RPC 2.0 消息、有状态连接、能力协商）、Server 提供的三类能力（Resources、Prompts、Tools）与 Client 提供的三类能力（Sampling、Roots、Elicitation），以及贯穿协议的安全与信任原则。

这份概览值得逐句精读：它定义了工具调用的信任边界（工具即任意代码执行、工具描述应视为不可信）、采样的用户控制权（用户须批准每次 LLM 采样并能看到实际发出的提示），这些原则直接决定构建 Agent 工具层的安全设计。下文完整翻译该概览页的全部内容，未补充存档之外的规范细节；各子规范的深入内容（Architecture、Base Protocol、Server Features、Client Features）可按文末"延伸阅读"所列条目在官网继续查阅。

## 全文中译

> 译注：本存档仅包含规范站 Specification 页面（即协议概览）的完整内容。以下译文覆盖该页全部实质内容，并按原文结构整理。

### 规范说明

**模型上下文协议（Model Context Protocol，MCP）是一个开放协议**，支持 LLM 应用与外部数据源和工具之间的无缝集成。无论你是在构建 AI 加持的 IDE、增强一个聊天界面，还是创建自定义的 AI 工作流，MCP 都提供了一种标准化的方式，把 LLM 与它们所需的上下文连接起来。

本规范定义了权威的协议要求，其依据是 `schema.ts` 中的 TypeScript 模式（schema）。实现指南与示例请访问 modelcontextprotocol.io。

本文档中的关键词"必须（MUST）"、"绝不可以（MUST NOT）"、"要求（REQUIRED）"、"应当（SHALL）"、"不应（SHALL NOT）"、"建议（SHOULD）"、"不建议（SHOULD NOT）"、"推荐（RECOMMENDED）"、"不推荐（NOT RECOMMENDED）"、"可以（MAY）"和"可选（OPTIONAL）"，当且仅当它们以全大写形式出现时，应按 BCP 14 [RFC2119] [RFC8174] 的描述进行解释。

### 概览（Overview）

MCP 为应用程序提供了一种标准化的方式来：

- 与语言模型共享上下文信息；
- 向 AI 系统暴露工具与能力；
- 构建可组合的集成与工作流。

该协议使用 JSON-RPC 2.0 消息在以下三者之间建立通信：

- **主机（Hosts）**：发起连接的 LLM 应用程序；
- **客户端（Clients）**：主机应用程序内部的连接器；
- **服务器（Servers）**：提供上下文与能力的服务。

MCP 的部分设计灵感来自语言服务器协议（Language Server Protocol, LSP）——LSP 标准化了如何在整个开发工具生态中为编程语言添加支持。与此类似，MCP 标准化了如何将额外的上下文和工具集成到 AI 应用生态之中。

### 关键细节（Key Details）

#### 基础协议（Base Protocol）

- JSON-RPC 消息格式；
- 有状态连接（Stateful connections）；
- 服务器与客户端的能力协商（capability negotiation）。

#### 功能（Features）

服务器（Servers）可向客户端提供以下任意功能：

- **资源（Resources）**：供用户或 AI 模型使用的上下文与数据；
- **提示（Prompts）**：面向用户的模板化消息与工作流；
- **工具（Tools）**：供 AI 模型执行的函数。

客户端（Clients）可向服务器提供以下功能：

- **采样（Sampling）**：由服务器发起的智能体行为与递归式 LLM 交互；
- **根（Roots）**：由服务器发起的、对 URI 或文件系统边界（即服务器可在其中操作的范围）的询问；
- **引导填写（Elicitation）**：由服务器发起的、向用户请求补充信息的机制。

#### 附加工具（Additional Utilities）

- 配置（Configuration）；
- 进度追踪（Progress tracking）；
- 取消（Cancellation）；
- 错误报告（Error reporting）；
- 日志（Logging）。

### 安全与信任及安全（Security and Trust & Safety）

模型上下文协议通过任意的数据访问与代码执行路径，提供了强大的能力。伴随这种能力而来的，是所有实现者都必须认真对待的重要安全与信任考量。

#### 关键原则（Key Principles）

**用户同意与控制（User Consent and Control）**

- 用户必须明确同意并理解所有的数据访问与操作；
- 用户必须保持对"共享哪些数据、执行哪些操作"的控制权；
- 实现者应提供清晰的界面（UI），供用户审阅和授权相关活动。

**数据隐私（Data Privacy）**

- 主机在向服务器暴露用户数据之前，必须获得用户的明确同意；
- 未经用户同意，主机不得将资源数据传输到其他地方；
- 用户数据应通过适当的访问控制加以保护。

**工具安全（Tool Safety）**

- 工具代表任意代码执行（arbitrary code execution），必须以相应的谨慎态度对待；
- 特别地，对工具行为的描述（例如注解/annotations）应被视为不可信，除非其来自可信任的服务器；
- 主机在调用任何工具之前，必须获得用户的明确同意；
- 用户在授权使用某个工具之前，应当了解该工具的功能。

**LLM 采样控制（LLM Sampling Controls）**

- 用户必须明确批准任何 LLM 采样请求；
- 用户应当控制：
  - 是否进行采样；
  - 实际发送的提示（prompt）内容；
  - 服务器能看到哪些结果；
- 协议有意限制服务器对提示内容的可见性。

#### 实施指南（Implementation Guidelines）

尽管 MCP 本身无法在协议层面强制执行这些安全原则，实现者**应当（SHOULD）**：

- 在应用中内建健壮的同意与授权流程；
- 提供清晰的安全影响说明文档；
- 实现适当的访问控制与数据保护；
- 在集成中遵循安全最佳实践；
- 在功能设计中考虑隐私影响。

### 延伸阅读（Learn More）

可以进一步探索协议各组件的详细规范：

- 架构（Architecture）；
- 基础协议（Base Protocol）；
- 服务器功能（Server Features）；
- 客户端功能（Client Features）；
- 参与贡献（Contributing）。

## 要点速览

- MCP 是开放协议，目标是让 LLM 应用与外部数据源、工具无缝集成：无论 AI IDE、聊天界面还是自定义 AI 工作流，都以同一标准化方式接入上下文。
- 通信地基是 JSON-RPC 2.0 消息；连接是有状态的，并且服务器与客户端之间进行能力协商（capability negotiation）。附加工具层提供配置、进度追踪、取消、错误报告与日志。
- 架构三角色：Host（发起连接的 LLM 应用，如 IDE 或聊天客户端）、Client（Host 内部的连接器，通常与 Server 一一相连）、Server（提供上下文与能力的服务）。
- 设计灵感来自语言服务器协议（LSP）：如同 LSP 统一了编程语言在开发工具生态中的接入，MCP 统一了上下文与工具在 AI 应用生态中的接入。
- Server 三大能力：Resources（给用户/模型用的上下文数据）、Prompts（模板化消息与工作流）、Tools（供模型执行的函数）。
- Client 三大能力：Sampling（服务器发起的智能体行为与递归 LLM 交互）、Roots（询问 URI/文件系统操作边界）、Elicitation（向用户征求补充信息）。
- 安全第一原则：用户必须明确同意并理解所有数据访问与操作，且保留对共享数据和所执行操作的最终控制权。
- 工具即任意代码执行：工具的行为描述（如 annotations）应视为不可信（除非来自可信服务器）；调用任何工具前 Host 必须获得用户明确同意。
- 采样必须由用户批准：用户控制是否采样、实际发出的提示内容、以及服务器可见的结果；协议有意限制服务器对提示的可见性——这是 MCP 设计中防提示泄露的关键边界。
- 协议本身无法在协议层强制执行安全原则，因此规范用 SHOULD 级别要求实现者内建同意/授权流程、访问控制、数据保护并遵循安全最佳实践。
