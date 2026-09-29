---
title: "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"
title_zh: "AutoGen:以多智能体对话构建下一代 LLM 应用"
authors: Qingyun Wu, Gagan Bansal, Jieyu Zhang, et al.
venue: "COLM 2024 · Microsoft Research / Penn State 等"
kind: paper
importance: recommended
tags: 多智能体,框架,对话编程,人机协同,代码生成
summary: 微软开源的多智能体对话框架:可对话、可定制的智能体(LLM/人/工具混合后端)+ 对话编程范式,六个应用展示其在数学、RAG、决策、编码等任务上开箱即用的竞争力。
---

## 导读

本文是第 5 周「多智能体系统」一讲的框架代表作(COLM 2024,微软研究院)。在 LangChain 式链式编排之外,AutoGen 提出用**多智能体对话**作为构建 LLM 应用的统一抽象:任何复杂工作流都被简化为一组可以互相收发消息的智能体。两个核心概念:①**可对话智能体(conversable agent)**——统一的消息收发/回复接口,后端可以是 LLM、人类、工具或三者的任意组合,由此派生出 AssistantAgent、UserProxyAgent 等预置角色;②**对话编程(conversation programming)**——用自然语言与编程语言混合控制"以对话为中心的计算"与"由对话驱动的控制流",auto-reply 机制让会话一旦初始化就自然推进、无需中央控制平面。论文用六个应用(数学解题、RAG 问答、ALFWorld 决策、带安全护栏的编码、动态群聊、对话式国际象棋)证明:开箱即用的两智能体组合在 MATH 上超过 ChatGPT+Code Interpreter 等商业方案,多智能体抽象在安全编码上带来 8-35% 的 F1 提升,OptiGuide 核心代码从 430 行减到 100 行。它与同讲《Why Do Multi-Agent LLM Systems Fail?》互为表里:一个给锤子,一个告诉你钉子在哪里。

## 全文对照翻译

> **译注**:本页覆盖论文正文全部内容(标题、图 1、摘要、第 1-4 节、伦理声明)与附录 A-D 全译(相关工作、扩展讨论、默认系统消息、应用细节含全部表格);附录 E(表 8-19,各系统原始输出转录)为原始示例输出,以译注概述,未逐行收录;References 不收录。原文脚注以"(原文脚注:……)"形式并入相应中文译文。

**AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation**(AutoGen:以多智能体对话构建下一代 LLM 应用)
Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Awadallah, Ryen W. White, Doug Burger, Chi Wang(微软研究院、宾夕法尼亚州立大学、华盛顿大学、西安电子科技大学)

[图 1: AutoGen enables diverse LLM-based applications using multi-agent conversations. (Left) AutoGen agents are conversable, customizable, and can be based on LLMs, tools, humans, or even a combination of them. (Top-middle) Agents can converse to solve tasks. (Right) They can form a chat, potentially with humans in the loop. (Bottom-middle) The framework supports flexible conversation patterns.]

图 1:AutoGen 用多智能体对话支撑多样的 LLM 应用。**左**:智能体定制——AutoGen 智能体是"可对话的(conversable)"、可定制的,后端可以是 LLM、工具、人类,甚至是它们的组合。**上中**:多智能体会话解决问题——示例对话为"画出 META 和 TESLA 今年以来的股价变化图"→智能体生成并请求执行代码→执行报错"package yfinance is not installed"→回复"请先 pip install yfinance 再执行"→安装后给出修正代码,先后输出按月股价($)与涨跌幅(%)两张图。**右**:智能体可以组成聊天,其中可以有人类在环(humans in the loop)。**下中**:框架支持灵活的会话模式,如层级聊天(Hierarchical chat)、联合聊天(Joint chat)等。

### 摘要

::: en
AutoGen² is an open-source framework that allows developers to build LLM applications via multiple agents that can converse with each other to accomplish tasks. AutoGen agents are customizable, conversable, and can operate in various modes that employ combinations of LLMs, human inputs, and tools. Using AutoGen, developers can also flexibly define agent interaction behaviors. Both natural language and computer code can be used to program flexible conversation patterns for different applications. AutoGen serves as a generic framework for building diverse applications of various complexities and LLM capacities. Empirical studies demonstrate the effectiveness of the framework in many example applications, with domains ranging from mathematics, coding, question answering, operations research, online decision-making, entertainment, etc.
:::

AutoGen 是一个开源框架,允许开发者通过多个可相互对话以完成任务的智能体来构建 LLM 应用。AutoGen 智能体可定制、可对话,并能以组合 LLM、人类输入与工具的多种模式运行。使用 AutoGen,开发者还可以灵活定义智能体交互行为:自然语言与计算机代码都可用于为不同应用编程灵活的对话模式。AutoGen 是构建各种复杂度、各种 LLM 能力之应用的通用框架。实证研究在许多示例应用上展示了框架的有效性,领域涵盖数学、编码、问答、运筹、在线决策与娱乐等。(原文脚注:² 即 https://github.com/microsoft/autogen;¹ 通讯作者邮箱 auto-gen@outlook.com。)

### 1 引言

::: en
Large language models (LLMs) are becoming a crucial building block in developing powerful agents that utilize LLMs for reasoning, tool usage, and adapting to new observations (Yao et al., 2022; Xi et al., 2023; Wang et al., 2023b) in many real-world tasks. Given the expanding tasks that could benefit from LLMs and the growing task complexity, an intuitive approach to scale up the power of agents is to use multiple agents that cooperate. Prior work suggests that multiple agents can help encourage divergent thinking (Liang et al., 2023), improve factuality and reasoning (Du et al., 2023), and provide validation (Wu et al., 2023). In light of the intuition and early evidence of promise, it is intriguing to ask the following question: how can we facilitate the development of LLM applications that could span a broad spectrum of domains and complexities based on the multi-agent approach?
:::

大语言模型(LLM)正成为构建强大智能体的关键积木——这些智能体在许多真实世界任务中利用 LLM 进行推理、使用工具并适应新的观察(Yao et al., 2022; Xi et al., 2023; Wang et al., 2023b)。鉴于能从 LLM 获益的任务不断扩张、任务复杂度持续上升,扩展智能体能力的一条直观路径就是让**多个智能体协作**。已有工作表明,多智能体有助于促进发散思维(divergent thinking)(Liang et al., 2023)、提高事实性与推理质量(Du et al., 2023)、并提供验证(Wu et al., 2023)。基于这一直觉与早期的有效性证据,一个引人入胜的问题随之而来:**如何基于多智能体方法,推动能横跨广泛领域与复杂度的 LLM 应用开发?**

::: en
Our insight is to use multi-agent conversations to achieve it. There are at least three reasons confirming its general feasibility and utility thanks to recent advances in LLMs: First, because chat-optimized LLMs (e.g., GPT-4) show the ability to incorporate feedback, LLM agents can cooperate through conversations with each other or human(s), e.g., a dialog where agents provide and seek reasoning, observations, critiques, and validation. Second, because a single LLM can exhibit a broad range of capabilities (especially when configured with the correct prompt and inference settings), conversations between differently configured agents can help combine these broad LLM capabilities in a modular and complementary manner. Third, LLMs have demonstrated ability to solve complex tasks when the tasks are broken into simpler subtasks. Multi-agent conversations can enable this partitioning and integration in an intuitive manner. How can we leverage the above insights and support different applications with the common requirement of coordinating multiple agents, potentially backed by LLMs, humans, or tools exhibiting different capacities? We desire a multi-agent conversation framework with generic abstraction and effective implementation that has the flexibility to satisfy different application needs. Achieving this requires addressing two critical questions: (1) How can we design individual agents that are capable, reusable, customizable, and effective in multi-agent collaboration? (2) How can we develop a straightforward, unified interface that can accommodate a wide range of agent conversation patterns? In practice, applications of varying complexities may need distinct sets of agents with specific capabilities, and may require different conversation patterns, such as single- or multi-turn dialogs, different human involvement modes, and static vs. dynamic conversation. Moreover, developers may prefer the flexibility to program agent interactions in natural language or code. Failing to adequately address these two questions would limit the framework's scope of applicability and generality.
:::

我们的洞见是:用**多智能体对话**来实现它。得益于 LLM 的最新进展,至少有三个理由确认其总体可行性与效用。**第一**,聊天优化的 LLM(如 GPT-4)已展现出吸收反馈的能力,因此 LLM 智能体可以通过与彼此或人类的对话来协作——例如在一段对话中,智能体提供并寻求推理、观察、批评与验证。**第二**,单个 LLM(尤其在配置了正确的提示与推理设置时)能展现广谱能力,而不同配置的智能体之间的对话,能以模块化、互补的方式组合这些广谱的 LLM 能力。**第三**,LLM 已证明:当复杂任务被拆解为更简单的子任务时,它们有能力解决复杂任务;多智能体对话能以直观的方式实现这种拆分与整合。那么,如何利用上述洞见,支撑那些共同需求是"协调多个智能体"(后端可能是能力各异的 LLM、人类或工具)的不同应用?我们期望一个具备通用抽象与有效实现的多智能体对话框架,有满足不同应用需求的灵活性。要做到这一点,必须回答两个关键问题:(1) 如何设计**有能力、可复用、可定制**且在多智能体协作中有效的个体智能体?(2) 如何开发一个**简明、统一的接口**,能容纳广泛的智能体对话模式?实践中,复杂度各异的应用可能需要具有特定能力的不同智能体集合,也可能需要不同的对话模式——单轮或多轮对话、不同的人类介入模式、静态或动态会话;此外,开发者可能希望灵活地用自然语言或代码来编程智能体交互。不能妥善回答这两个问题,就会限制框架的适用范围与通用性。

::: en
While there is contemporaneous exploration of multi-agent approaches,³ we present AutoGen, a generalized multi-agent conversation framework (Figure 1), based on the following new concepts.

**1 Customizable and conversable agents.** AutoGen uses a generic design of agents that can leverage LLMs, human inputs, tools, or a combination of them. The result is that developers can easily and quickly create agents with different roles (e.g., agents to write code, execute code, wire in human feedback, validate outputs, etc.) by selecting and configuring a subset of built-in capabilities. The agent's backend can also be readily extended to allow more custom behaviors. To make these agents suitable for multi-agent conversation, every agent is made conversable – they can receive, react, and respond to messages. When configured properly, an agent can hold multiple turns of conversations with other agents autonomously or solicit human inputs at certain rounds, enabling human agency and automation. The conversable agent design leverages the strong capability of the most advanced LLMs in taking feedback and making progress via chat and also allows combining capabilities of LLMs in a modular fashion. (Section 2.1)

**2 Conversation programming.** A fundamental insight of AutoGen is to simplify and unify complex LLM application workflows as multi-agent conversations. So AutoGen adopts a programming paradigm centered around these inter-agent conversations. We refer to this paradigm as conversation programming, which streamlines the development of intricate applications via two primary steps: (1) defining a set of conversable agents with specific capabilities and roles (as described above); (2) programming the interaction behavior between agents via conversation-centric computation and control. Both steps can be achieved via a fusion of natural and programming languages to build applications with a wide range of conversation patterns and agent behaviors. AutoGen provides ready-to-use implementations and also allows easy extension and experimentation for both steps. (Section 2.2)
:::

尽管多智能体方法已有同时期的探索(原文脚注:³ 详见附录 A 的讨论),我们仍提出 **AutoGen**——一个泛化的多智能体对话框架(图 1),它基于以下新概念。

**1 可定制、可对话的智能体(customizable and conversable agents)。** AutoGen 采用通用的智能体设计,可以调用 LLM、人类输入、工具或它们的组合。其结果是,开发者只需选择并配置一部分内置能力,就能轻松快速地创建承担不同角色的智能体(如写代码、执行代码、接入人类反馈、验证输出等)。智能体后端也可以被轻松扩展以支持更多自定义行为。为了让这些智能体适合多智能体对话,**每个智能体都被做成"可对话的"——它们能接收、反应并回复消息**。配置得当时,一个智能体可以自主地与其他智能体进行多轮对话,也可以在特定轮次征求人类输入,从而同时实现人类能动性与自动化。"可对话智能体"设计既利用了最先进 LLM 通过聊天吸收反馈、取得进展的强大能力,也允许以模块化方式组合 LLM 的能力。(见 2.1 节)

**2 对话编程(conversation programming)。** AutoGen 的一个根本洞见是:把复杂的 LLM 应用工作流简化并统一为多智能体对话。因此 AutoGen 采用一种以智能体间对话为中心的编程范式。我们把这一范式称为**对话编程**,它通过两个主要步骤简化复杂应用的开发:(1) 定义一组具有特定能力与角色的可对话智能体(如上文所述);(2) 通过以对话为中心的计算与控制来编程智能体间的交互行为。这两步都可以通过自然语言与编程语言的融合来完成,从而构建具有广泛对话模式与智能体行为的应用。AutoGen 为两步都提供了开箱即用的实现,也允许轻松扩展与实验。(见 2.2 节)

::: en
AutoGen also provides a collection of multi-agent applications created using conversable agents and conversation programming. These applications demonstrate how AutoGen can easily support applications of various complexities and LLMs of various capabilities. Moreover, we perform both evaluation on benchmarks and a pilot study of new applications. The results show that AutoGen can help achieve outstanding performance on many tasks, and enable innovative ways of using LLMs, while reducing development effort. (Section 3 and Appendix D)
:::

AutoGen 还提供了一组用可对话智能体与对话编程创建的多智能体应用。这些应用展示了 AutoGen 如何轻松支撑各种复杂度的应用与各种能力的 LLM。此外,我们既在基准上做了评测,也对新应用做了试点研究。结果表明,AutoGen 能帮助在许多任务上取得出色性能、开创使用 LLM 的新方式,同时降低开发投入。(见第 3 节与附录 D)

### 2 AutoGen 框架

::: en
To reduce the effort required for developers to create complex LLM applications across various domains, a core design principle of AutoGen is to streamline and consolidate multi-agent workflows using multi-agent conversations. This approach also aims to maximize the reusability of implemented agents. This section introduces the two key concepts of AutoGen: conversable agents and conversation programming.
:::

为了降低开发者跨领域创建复杂 LLM 应用的成本,AutoGen 的一个核心设计原则是:用多智能体对话来精简并整合多智能体工作流。这一方法也旨在最大化已实现智能体的可复用性。本节介绍 AutoGen 的两个关键概念:可对话智能体与对话编程。

#### 2.1 可对话智能体

::: en
In AutoGen, a conversable agent is an entity with a specific role that can pass messages to send and receive information to and from other conversable agents, e.g., to start or continue a conversation. It maintains its internal context based on sent and received messages and can be configured to possess a set of capabilities, e.g., enabled by LLMs, tools, or human input, etc. The agents can act according to programmed behavior patterns described next.
:::

在 AutoGen 中,**可对话智能体(conversable agent)是一个具有特定角色的实体**,能向其他可对话智能体传递消息、收发信息,例如发起或继续一段对话。它基于发送与接收的消息维护自己的内部上下文,并可通过配置拥有一组能力——例如由 LLM、工具或人类输入等赋予的能力。智能体可以按照下文描述的被编程行为模式行动。

::: en
**Agent capabilities powered by LLMs, humans, and tools.** Since an agent's capabilities directly influence how it processes and responds to messages, AutoGen allows flexibility to endow its agents with various capabilities. AutoGen supports many common composable capabilities for agents, including 1) LLMs. LLM-backed agents exploit many capabilities of advanced LLMs such as role playing, implicit state inference and progress making conditioned on conversation history, providing feedback, adapting from feedback, and coding. These capabilities can be combined in different ways via novel prompting techniques⁴ to increase an agent's skill and autonomy. AutoGen also offers enhanced LLM inference features such as result caching, error handling, message templating, etc., via an enhanced LLM inference layer. 2) Humans. Human involvement is desired or even essential in many LLM applications. AutoGen lets a human participate in agent conversation via human-backed agents, which could solicit human inputs at certain rounds of a conversation depending on the agent configuration. The default user proxy agent allows configurable human involvement levels and patterns, e.g., frequency and conditions for requesting human input including the option for humans to skip providing input. 3) Tools. Tool-backed agents have the capability to execute tools via code execution or function execution. For example, the default user proxy agent in AutoGen is able to execute code suggested by LLMs, or make LLM-suggested function calls.
:::

**由 LLM、人类与工具驱动的能力。** 由于智能体的能力直接决定它如何处理与回复消息,AutoGen 允许灵活地赋予智能体各种能力。AutoGen 支持许多常见的可组合能力,包括:**1) LLM。** LLM 后端(LLM-backed)的智能体利用先进 LLM 的诸多能力:角色扮演、基于会话历史的隐式状态推断与推进、提供反馈、从反馈中调整、以及编码。这些能力可以通过新颖的提示技术(原文脚注:⁴ 附录 C 给出了此类新颖提示技术的一个例子,它使 AutoGen 默认的 LLM 后端助手智能体能在多步问题求解中与其他智能体对话)以不同方式组合,以提升智能体的技能与自主性。AutoGen 还通过增强的 LLM 推理层提供结果缓存、错误处理、消息模板等增强推理特性。**2) 人类。** 在许多 LLM 应用中,人类介入是被期望甚至必需的。AutoGen 让人类通过"人类后端"(human-backed)智能体参与智能体对话,后者可依配置在对话的特定轮次征求人类输入。默认的**用户代理智能体(user proxy agent)**支持可配置的人类介入级别与模式,例如请求人类输入的频率与条件,并包含"允许人类跳过输入"的选项。**3) 工具。** 工具后端(tool-backed)的智能体能通过代码执行或函数执行来使用工具。例如,AutoGen 默认的用户代理智能体可以执行 LLM 建议的代码,或发起 LLM 建议的函数调用。

::: en
**Agent customization and cooperation.** Based on application-specific needs, each agent can be configured to have a mix of basic back-end types to display complex behavior in multi-agent conversations. AutoGen allows easy creation of agents with specialized capabilities and roles by reusing or extending the built-in agents. The yellow-shaded area of Figure 2 provides a sketch of the built-in agents in AutoGen. The ConversableAgent class is the highest-level agent abstraction and, by default, can use LLMs, humans, and tools. The AssistantAgent and UserProxyAgent are two pre-configured ConversableAgent subclasses, each representing a common usage mode, i.e., acting as an AI assistant (backed by LLMs) and acting as a human proxy to solicit human input or execute code/function calls (backed by humans and/or tools).
:::

**智能体定制与协作。** 依据应用的特定需要,每个智能体都可以配置为多种基本后端类型的混合,从而在多智能体对话中展现复杂行为。通过复用或扩展内置智能体,AutoGen 让创建具有专门能力与角色的智能体变得容易。图 2 的黄色区域给出了 AutoGen 内置智能体的概览:**ConversableAgent 类是最高层的智能体抽象**,默认可同时使用 LLM、人类与工具;**AssistantAgent 与 UserProxyAgent 是两个预配置的 ConversableAgent 子类**,各自代表一种常见使用模式——前者充当 AI 助手(LLM 后端),后者充当人类代理,负责征求人类输入或执行代码/函数调用(人类和/或工具后端)。

::: en
In the example on the right-hand side of Figure 1, an LLM-backed assistant agent and a tool- and human-backed user proxy agent are deployed together to tackle a task. Here, the assistant agent generates a solution with the help of LLMs and passes the solution to the user proxy agent. Then, the user proxy agent solicits human inputs or executes the assistant's code and passes the results as feedback back to the assistant.
:::

在图 1 右侧的例子中,一个 LLM 后端的助手智能体与一个工具+人类后端的用户代理智能体被共同部署来完成任务:助手智能体在 LLM 帮助下生成解法并传给用户代理智能体;随后,用户代理智能体征求人类输入、或执行助手的代码,并把结果作为反馈回传给助手。

[图 2: Illustration of how to use AutoGen to program a multi-agent conversation. The top sub-figure illustrates the built-in agents provided by AutoGen, which have unified conversation interfaces and can be customized. The middle sub-figure shows an example of using AutoGen to develop a two-agent system with a custom reply function. The bottom sub-figure illustrates the resulting automated agent chat from the two-agent system during program execution.]

图 2:如何用 AutoGen 编程一段多智能体对话。**上**:AutoGen 提供的内置智能体——具有统一的会话接口(send / receive / generate_reply),且可定制。**中**:用 AutoGen 开发一个带自定义回复函数的双智能体系统的示例。**下**:程序执行期间,该双智能体系统产生的自动智能体聊天结果。图中的开发者代码(Agent Customization 与 Initiate Conversations 部分)如下:

```python
# 1.1 定义智能体(Defining agents):
# AssistantAgent —— 预配置的 LLM 后端助手
#   DEFAULT_SYSTEM_MESSAGE = "You are a helpful AI assistant…
#   In the following cases, suggest python code…"
#   (默认系统消息:"你是一个乐于助人的 AI 助手……
#    在下列情况下,建议 python 代码……")
# UserProxyAgent —— 人类+工具后端的用户代理
#   human_input_mode = "ALWAYS"   # 每轮都征求人类输入
# ConversableAgent —— 最高层抽象;GroupChatManager —— 群聊管理者
#   human_input_mode = "NEVER"
#   group_chat = [ ... ]          # 参与群聊的智能体列表

# 1.2 注册自定义回复函数(Register a custom reply func):
A.register_reply(B, reply_func_A2B)   # 为"来自 B 的消息"注册回复函数

def reply_func_A2B(msg):              # 该函数将在 generate_reply 中被调用
    ouput = input_from_human()        # 先征求人类输入
    ...
    if not ouput:                     # 人类没有输入时
        if msg includes code:         # 若消息中包含代码
            output = execute(msg)     # 则执行代码
    return output

# 注:未注册回复函数时,将使用一组默认回复函数
# (Note: when no reply func is registered, a list of default
#  reply functions will be used.)

# 2. 发起对话(Initiate conversations):
A.initiate_chat("Plot a chart of META and TESLA stock price change YTD.", B)
# (用户代理 A 向助手 B 发起对话:"画出 META 和 TESLA 今年以来
#  的股价变化图。")
```

::: en
By allowing custom agents that can converse with each other, conversable agents in AutoGen serve as a useful building block. However, to develop applications where agents make meaningful progress on tasks, developers also need to be able to specify and mold these multi-agent conversations.
:::

通过允许自定义智能体彼此对话,AutoGen 的可对话智能体构成了有用的积木。但要开发出智能体能在任务上取得实质进展的应用,开发者还需要能够**指定并塑造**这些多智能体对话。

#### 2.2 对话编程

::: en
As a solution to the above problem, AutoGen utilizes conversation programming, a paradigm that considers two concepts: the first is computation – the actions agents take to compute their response in a multi-agent conversation. And the second is control flow – the sequence (or conditions) under which these computations happen. As we will show in the applications section, the ability to program these helps implement many flexible multi-agent conversation patterns. In AutoGen, these computations are conversation-centric. An agent takes actions relevant to the conversations it is involved in and its actions result in message passing for consequent conversations (unless a termination condition is satisfied). Similarly, control flow is conversation-driven – the participating agents' decisions on which agents to send messages to and the procedure of computation are functions of the inter-agent conversation. This paradigm helps one to reason intuitively about a complex workflow as agent action taking and conversation message-passing between agents.
:::

作为对上述问题的解决,AutoGen 采用对话编程——一个包含两个概念的范式:其一是**计算(computation)**,即智能体在多智能体对话中为算出回复所采取的动作;其二是**控制流(control flow)**,即这些计算发生的顺序(或条件)。正如应用部分将展示的,对两者的编程能力有助于实现许多灵活的多智能体对话模式。在 AutoGen 中,这些计算是**以对话为中心的(conversation-centric)**:智能体采取与其参与的对话相关的行动,其行动产生后续对话所需的消息传递(除非满足终止条件)。类似地,控制流是**由对话驱动的(conversation-driven)**——参与智能体"向谁发消息"的决策以及计算过程,都是智能体间对话的函数。这一范式帮助人们直观地把复杂工作流理解为"智能体的行动执行"与"智能体间的对话消息传递"。

::: en
Figure 2 provides a simple illustration. The bottom sub-figure shows how individual agents perform their role-specific, conversation-centric computations to generate responses (e.g., via LLM inference calls and code execution). The task progresses through conversations displayed in the dialog box. The middle sub-figure demonstrates a conversation-based control flow. When the assistant receives a message, the user proxy agent typically sends the human input as a reply. If there is no input, it executes any code in the assistant's message instead.
:::

图 2 给出一个简单示例。下方子图展示各智能体如何执行其角色特定的、以对话为中心的计算来生成回复(例如通过 LLM 推理调用与代码执行);任务随着对话框中显示的对话而推进。中间子图演示了基于对话的控制流:当收到助手消息时,用户代理智能体通常把人类输入作为回复发出;如果没有输入,则转而执行助手消息中的代码。

::: en
AutoGen features the following design patterns to facilitate conversation programming:

**1. Unified interfaces and auto-reply mechanisms for automated agent chat.** Agents in AutoGen have unified conversation interfaces for performing the corresponding conversation-centric computation, including a send/receive function for sending/receiving messages and a generate reply function for taking actions and generating a response based on the received message. AutoGen also introduces and by default adopts an agent auto-reply mechanism to realize conversation-driven control: Once an agent receives a message from another agent, it automatically invokes generate reply and sends the reply back to the sender unless a termination condition is satisfied. AutoGen provides built-in reply functions based on LLM inference, code or function execution, or human input. One can also register custom reply functions to customize the behavior pattern of an agent, e.g., chatting with another agent before replying to the sender agent. Under this mechanism, once the reply functions are registered, and the conversation is initialized, the conversation flow is naturally induced, and thus the agent conversation proceeds naturally without any extra control plane, i.e., a special module that controls the conversation flow. For example, with the developer code in the blue-shaded area (marked "Developer Code") of Figure 2, one can readily trigger the conversation among the agents, and the conversation would proceed automatically, as shown in the dialog box in the grey shaded area (marked "Program Execution") of Figure 2. The auto-reply mechanism provides a decentralized, modular, and unified way to define the workflow.

**2. Control by fusion of programming and natural language.** AutoGen allows the usage of programming and natural language in various control flow management patterns: 1) Natural-language control via LLMs. In AutoGen, one can control the conversation flow by prompting the LLM-backed agents with natural language. For instance, the default system message of the built-in AssistantAgent in AutoGen uses natural language to instruct the agent to fix errors and generate code again if the previous result indicates there are errors. It also guides the agent to confine the LLM output to certain structures, making it easier for other tool-backed agents to consume. For example, instructing the agent to reply with "TERMINATE" when all tasks are completed to terminate the program. More concrete examples of natural language controls can be found in Appendix C. 2) Programming-language control. In AutoGen, Python code can be used to specify the termination condition, human input mode, and tool execution logic, e.g., the max number of auto replies. One can also register programmed auto-reply functions to control the conversation flow with Python code, as shown in the code block identified as "Conversation-Driven Control Flow" in Figure 2. 3) Control transition between natural and programming language. AutoGen also supports flexible control transition between natural and programming language. One can achieve transition from code to natural-language control by invoking an LLM inference containing certain control logic in a customized reply function; or transition from natural language to code control via LLM-proposed function calls (Eleti et al., 2023).
:::

AutoGen 具备以下设计模式来便利对话编程:

**1. 统一接口与面向自动智能体聊天的 auto-reply(自动回复)机制。** AutoGen 中的智能体拥有统一的会话接口来执行相应的以对话为中心的计算,包括用于发送/接收消息的 send/receive 函数,以及基于收到的消息采取行动并生成回复的 generate_reply 函数。AutoGen 还引入并默认采用智能体自动回复机制来实现对话驱动的控制:**一旦某智能体收到来自另一智能体的消息,它会自动调用 generate_reply 并把回复发回发送者,除非满足终止条件。** AutoGen 提供基于 LLM 推理、代码或函数执行、人类输入的内置回复函数;也可以注册自定义回复函数来定制智能体的行为模式,例如"先与另一个智能体聊天、再回复发送者"。在这一机制下,一旦回复函数注册完毕、会话初始化完成,对话流就被自然诱导出来——智能体对话自然推进,无需任何额外的控制平面(即专门控制对话流的特殊模块)。例如,用图 2 蓝色区域(标注 "Developer Code")中的开发者代码即可轻松触发智能体间的对话,对话会自动进行,如图 2 灰色区域(标注 "Program Execution")的对话框所示。auto-reply 机制提供了一种**去中心化、模块化、统一**的工作流定义方式。

**2. 编程语言与自然语言融合的控制。** AutoGen 允许以多种控制流管理模式混合使用编程语言与自然语言:**(1) 经由 LLM 的自然语言控制。** 在 AutoGen 中,可以用自然语言提示 LLM 后端智能体来控制对话流。例如,内置 AssistantAgent 的默认系统消息用自然语言指示智能体:若上一次结果表明有错误,则修复错误并重新生成代码;它还引导智能体把 LLM 输出限制在特定结构中,便于其他工具后端智能体消费——例如指示智能体在全部任务完成后回复 "TERMINATE" 以终止程序。更多自然语言控制的具体例子见附录 C。**(2) 编程语言控制。** 在 AutoGen 中,可以用 Python 代码指定终止条件、人类输入模式与工具执行逻辑,例如最大自动回复次数;也可以注册编程式的自动回复函数,用 Python 代码控制对话流,如图 2 中标注 "Conversation-Driven Control Flow" 的代码块所示。**(3) 自然语言与编程语言之间的控制转移。** AutoGen 还支持两者间灵活的控制转移:在自定义回复函数内发起含特定控制逻辑的 LLM 推理,可实现"代码→自然语言"的转移;通过 LLM 发起的函数调用(Eleti et al., 2023),可实现"自然语言→代码"的转移。

::: en
In the conversation programming paradigm, one can realize multi-agent conversations of diverse patterns. In addition to static conversation with predefined flow, AutoGen also supports dynamic conversation flows with multiple agents. AutoGen provides two general ways to achieve this: 1) Customized generate reply function: within the customized generate reply function, one agent can hold the current conversation while invoking conversations with other agents depending on the content of the current message and context. 2) Function calls: In this approach, LLM decides whether or not to call a particular function depending on the conversation status. By messaging additional agents in the called functions, the LLM can drive dynamic multi-agent conversation. In addition, AutoGen supports more complex dynamic group chat via built-in GroupChatManager, which can dynamically select the next speaker and then broadcast its response to other agents. We elaborate on this feature and its application in Section 3. We provide implemented working systems to showcase all these different patterns, with some of them visualized in Figure 3.
:::

在对话编程范式下,可以实现多种模式的多智能体对话。除预定义流程的静态对话外,AutoGen 还支持多智能体的动态对话流,并提供两种通用实现方式:**(1) 自定义 generate_reply 函数**:在自定义的 generate_reply 函数内,一个智能体可以挂起当前对话,依据当前消息内容与上下文,转而发起与其他智能体的对话;**(2) 函数调用**:由 LLM 依据对话状态决定是否调用某个函数,并在被调用函数中给其他智能体发消息,从而驱动动态多智能体对话。此外,AutoGen 通过内置的 **GroupChatManager** 支持更复杂的动态群聊——动态选出下一个发言者,再将其回复广播给其他智能体。我们将在第 3 节详述该特性及其应用。我们提供了可运行的工作系统来展示所有这些不同模式,其中一部分如图 3 所示。

### 3 AutoGen 的应用

::: en
We demonstrate six applications using AutoGen (see Figure 3) to illustrate its potential in simplifying the development of high-performance multi-agent applications. These applications are selected based on their real-world relevance (A1, A2, A4, A5, A6), problem difficulty and solving capabilities enabled by AutoGen (A1, A2, A3, A4), and innovative potential (A5, A6). Together, these criteria showcase AutoGen's role in advancing the LLM-application landscape.
:::

我们用 AutoGen 演示六个应用(见图 3),以说明它在简化高性能多智能体应用开发方面的潜力。这些应用的选择依据是:真实世界相关性(A1、A2、A4、A5、A6)、问题难度与 AutoGen 带来的解题能力(A1、A2、A3、A4)、以及创新潜力(A5、A6)。这些标准共同展示了 AutoGen 在推进 LLM 应用版图上的作用。

[图 3: Six examples of diverse applications built using AutoGen. Their conversation patterns show AutoGen's flexibility and power.]

图 3:用 AutoGen 构建的六个多样化应用示例,它们的对话模式展示了 AutoGen 的灵活性与威力。六个应用分别为:**A1 数学解题**(学生 Student + 助手 Assistant,可询问专家 Expert);**A2 检索增强聊天**(Retrieval-augmented Assistant + Retrieval-augmented User Proxy);**A3 ALF 聊天**(Assistant + 执行器 Executor + 锚定智能体 Grounding Agent);**A4 多智能体编码**(Commander 协调 Writer 与 Safeguard);**A5 动态群聊**(Manager 管理发言并广播);**A6 对话式国际象棋**(棋盘 Chess Board + 人/AI 棋手 A/B)。

#### A1:数学解题

::: en
Mathematics is a foundational discipline and the promise of leveraging LLMs to assist with math problem solving opens up a new plethora of applications and avenues for exploration, including personalized AI tutoring, AI research assistance, etc. This section demonstrates how AutoGen can help develop LLM applications for math problem solving, showcasing strong performance and flexibility in supporting various problem-solving paradigms.

(Scenario 1) We are able to build a system for autonomous math problem solving by directly reusing two built-in agents from AutoGen. We evaluate our system and several alternative approaches, including open-source methods such as Multi-Agent Debate (Liang et al., 2023), LangChain ReAct (LangChain, 2023), vanilla GPT-4, and commercial products ChatGPT + Code Interpreter, and ChatGPT + Plugin (Wolfram Alpha), on the MATH (Hendrycks et al., 2021) dataset and summarize the results in Figure 4a. We perform evaluations over 120 randomly selected level-5 problems and on the entire⁵ test dataset from MATH. The results show that the built-in agents from AutoGen already yield better performance out of the box compared to the alternative approaches, even including the commercial ones. (Scenario 2) We also showcase a human-in-the-loop problem-solving process with the help of AutoGen. To incorporate human feedback with AutoGen, one only needs to set human input mode='ALWAYS' in the UserProxyAgent of the system in scenario 1. We demonstrate that this system can effectively incorporate human inputs to solve challenging problems that cannot be solved without humans. (Scenario 3) We further demonstrate a novel scenario where multiple human users can participate in the conversations during the problem-solving process. Our experiments and case studies for these scenarios show that AutoGen enables better performance or new experience compared to other solutions we experimented with. Due to the page limit, details of the evaluation, including case studies in three scenarios are in Appendix D.
:::

数学是一门基础学科,利用 LLM 辅助数学解题的前景开辟了大量新的应用与探索途径,包括个性化 AI 辅导、AI 研究助理等。本节展示 AutoGen 如何帮助开发数学解题的 LLM 应用,展现其在支撑多种解题范式上的强劲性能与灵活性。

**(场景 1:自主解题)** 我们只需直接复用 AutoGen 的两个内置智能体,就能搭出一个自主数学解题系统。我们在 MATH 数据集(Hendrycks et al., 2021)上评测该系统与多个替代方案——包括开源方法 Multi-Agent Debate(Liang et al., 2023)、LangChain ReAct(LangChain, 2023)、原生 GPT-4,以及商业产品 ChatGPT + Code Interpreter 和 ChatGPT + Plugin(Wolfram Alpha)——结果汇总于图 4a。我们在随机抽取的 120 道 level-5 难题以及 MATH 整个⁵测试集上评测。结果表明:AutoGen 的内置智能体**开箱即用**就已取得优于各替代方案(包括商业方案)的性能。**(场景 2:人机回环解题)** 我们还展示了借助 AutoGen 的人机回环(human-in-the-loop)解题过程:要把人类反馈接入 AutoGen,只需把场景 1 系统中 UserProxyAgent 的 human_input_mode 设为 'ALWAYS'。我们证明该系统能有效吸收人类输入,解决没有人类就解不出的难题。**(场景 3:多用户参与)** 我们进一步演示了一个新颖场景:多个真实用户可以在解题过程中参与对话。这些场景的实验与案例研究表明,与我们所实验的其他方案相比,AutoGen 能带来更好的性能或全新体验。限于篇幅,评测细节(含三个场景的案例研究)见附录 D。(原文脚注:⁵ 未在整个数据集上评测 ChatGPT,因为这需要大量人工且受其每小时消息数限制;Multi-Agent Debate 与 LangChain ReAct 也未在整个数据集上评测,因为它们在较小的测试集上就已不如原生 GPT-4。)

#### A2:检索增强的代码生成与问答

::: en
Retrieval augmentation has emerged as a practical and effective approach for mitigating the intrinsic limitations of LLMs by incorporating external documents. In this section, we employ AutoGen to build a Retrieval-Augmented Generation (RAG) system (Lewis et al., 2020; Parvez et al., 2021) named Retrieval-augmented Chat. The system consists of two agents: a Retrieval-augmented User Proxy agent and a Retrieval-augmented Assistant agent, both of which are extended from built-in agents from AutoGen. The Retrieval-augmented User Proxy includes a vector database (Chroma, 2023) with SentenceTransformers (Reimers & Gurevych, 2019) as the context retriever. A detailed workflow description of the Retrieval-augmented Chat is provided in Appendix D.
:::

通过引入外部文档,检索增强(retrieval augmentation)已成为缓解 LLM 固有局限的一种实用而有效的方法。本节用 AutoGen 构建一个检索增强生成(Retrieval-Augmented Generation,RAG)系统(Lewis et al., 2020; Parvez et al., 2021),命名为 **Retrieval-augmented Chat(检索增强聊天)**。系统由两个智能体组成:检索增强用户代理智能体(Retrieval-augmented User Proxy)与检索增强助手智能体(Retrieval-augmented Assistant),二者都是从 AutoGen 内置智能体扩展而来。检索增强用户代理内置一个向量数据库(Chroma, 2023),并以 SentenceTransformers(Reimers & Gurevych, 2019)作为上下文检索器。检索增强聊天的详细工作流见附录 D。

::: en
We evaluate Retrieval-augmented Chat in both question-answering and code-generation scenarios. (Scenario 1) We first perform an evaluation regarding natural question answering on the Natural Questions dataset (Kwiatkowski et al., 2019) and report results in Figure 4b. In this evaluation, we compare our system with DPR (Dense Passage Retrieval) following an existing evaluation⁶ practice (Adlakha et al., 2023). Leveraging the conversational design and natural-language control, AutoGen introduces a novel interactive retrieval feature in this application: whenever the retrieved context does not contain the information, instead of terminating, the LLM-based assistant would reply "Sorry, I cannot find any information about... UPDATE CONTEXT." which will invoke more retrieval attempts. We conduct an ablation study in which we prompt the assistant agent to say "I don't know" instead of "UPDATE CONTEXT." in cases where relevant information is not found, and report results in Figure 4b. The results show that the interactive retrieval mechanism indeed plays a non-trivial role in the process. We give a concrete example and results using this appealing feature in Appendix D. (Scenario 2) We further demonstrate how Retrieval-augmented Chat aids in generating code based on a given codebase that contains code not included in GPT-4's training data. Evaluation and demonstration details for both scenarios are included in Appendix D.
:::

我们在问答与代码生成两个场景下评测检索增强聊天。**(场景 1)** 首先在 Natural Questions 数据集(Kwiatkowski et al., 2019)上做自然问答评测,结果见图 4b。此次评测遵循既有评测实践(Adlakha et al., 2023),将我们的系统与 DPR(稠密段落检索)对比(原文脚注:⁶ 图 4b 中 DPR+GPT-3.5 的结果取自 Adlakha et al., 2023;文中 GPT-3.5 是 GPT-3.5-turbo 的简写)。利用对话式设计与自然语言控制,AutoGen 在该应用中引入了新颖的**交互式检索(interactive retrieval)**特性:每当检索到的上下文不含所需信息,LLM 助手不是终止对话,而是回复 "Sorry, I cannot find any information about... UPDATE CONTEXT.",从而触发更多检索尝试。我们做了消融实验:提示助手智能体在找不到相关信息时改说 "I don't know" 而非 "UPDATE CONTEXT.",结果见图 4b。结果表明,交互式检索机制在过程中确实发挥了不可忽视的作用。附录 D 给出了使用这一诱人特性的具体例子与结果。**(场景 2)** 我们进一步演示检索增强聊天如何帮助基于某个代码库生成代码——该代码库包含未出现在 GPT-4 训练数据中的代码。两个场景的评测与演示细节均见附录 D。

[图 4: Performance on four applications A1-A4. (a) shows that AutoGen agents can be used out of the box to achieve the most competitive performance on math problem solving tasks; (b) shows that AutoGen can be used to realize effective retrieval augmentation and realize a novel interactive retrieval feature to boost performance on Q&A tasks; (c) shows that AutoGen can be used to introduce a three-agent system with a grounding agent to improve performance on ALFWorld; (d) shows that a multi-agent design is helpful in boosting performance in coding tasks that need safeguards.]

图 4:四个应用 A1-A4 的性能。**(a)** AutoGen 智能体开箱即用即可在数学解题任务上取得最具竞争力的性能;**(b)** AutoGen 可用于实现有效的检索增强,并实现新颖的交互式检索特性以提升问答任务性能;**(c)** AutoGen 可用于引入带锚定智能体的三智能体系统以提升 ALFWorld 性能;**(d)** 多智能体设计有助于提升需要安全护栏的编码任务性能。图 4 数据如下:

**(a) A1:MATH 上的成功率(使用 GPT-4)**

| 方法 | 120 道 level-5 难题 | 整个测试集 |
| --- | --- | --- |
| **AutoGen** | **52.5%** | **69.48%** |
| GPT-4(原生) | 48.33% | 55.18% |
| ChatGPT + Code Interpreter | 45.0% | — |
| Multi-Agent Debate | 30.0% | — |
| LangChain ReAct | 26.67% | — |
| ChatGPT + Plugin(Wolfram) | 23.33% | — |

**(b) A2:问答任务(使用 GPT-3.5)**

| 方法 | F1 | Recall |
| --- | --- | --- |
| **AutoGen(含交互式检索)** | **25.88%** | **66.65%** |
| AutoGen 无交互式检索 | 15.12% | 58.56% |
| DPR | 22.79% | 62.59% |

**(c) A3:ALFWorld 上的成功率**

| 方法 | 平均 | 3 次中最佳(best of 3) |
| --- | --- | --- |
| AutoGen(三智能体) | **69%** | **77%** |
| AutoGen(两智能体) | 54% | 63% |
| ReAct | 54% | 66% |

**(d) A4:OptiGuide 上识别不安全代码的性能**

| 方法 | F1 | Recall |
| --- | --- | --- |
| Multi-GPT4(多智能体 + GPT-4) | **96.00%** | **98.00%** |
| Single-GPT4(单智能体 + GPT-4) | 88.00% | 78.00% |
| Multi-GPT3.5(多智能体 + GPT-3.5) | 83.00% | 72.00% |
| Single-GPT3.5(单智能体 + GPT-3.5) | 48.00% | 32.00% |

#### A3:文本世界环境中的决策

::: en
In this subsection, we demonstrate how AutoGen can be used to develop effective applications that involve interactive or online decision making. We perform the study using the ALFWorld (Shridhar et al., 2021) benchmark, which includes a diverse collection of synthetic language-based interactive decision-making tasks in household environments.
:::

本小节演示如何用 AutoGen 开发涉及交互式或在线决策的有效应用。我们使用 ALFWorld 基准(Shridhar et al., 2021)进行研究,它包含一组多样的、基于合成语言的家用环境交互式决策任务。

::: en
With AutoGen, we implemented a two-agent system to solve tasks from ALFWorld. It consists of an LLM-backed assistant agent responsible for suggesting plans to conduct a task and an executor agent responsible for executing actions in the ALFWorld environments. This system integrates ReAct prompting (Yao et al., 2022), and is able to achieve similar performance. A common challenge encountered in both ReAct and the AutoGen-based two-agent system is their occasional inability to leverage basic commonsense knowledge about the physical world. This deficiency can lead to the system getting stuck in a loop due to repetitive errors. Fortunately, the modular design of AutoGen allows us to address this issue effectively: With AutoGen, we are able to introduce a grounding agent, which supplies crucial commonsense knowledge–such as "You must find and take the object before you can examine it. You must go to where the target object is before you can use it."–whenever the system exhibits early signs of recurring errors. It significantly enhances the system's ability to avoid getting entangled in error loops. We compare the task-solving performance of the two variants of our system with GPT-3.5-turbo and ReAct⁷ on the 134 unseen tasks from ALFWorld and report results in Figure 4c. The results show that introducing a grounding agent could bring in a 15% performance gain on average. Upon examining the systems' outputs, we observe that the grounding agent, by delivering background commonsense knowledge at the right junctures, significantly mitigated the tendency of the system to persist with a flawed plan, thereby avoiding the creation of error loops. For an example trajectory comparing the systems see Appendix D, Figure 10.
:::

用 AutoGen,我们实现了一个求解 ALFWorld 任务的双智能体系统:一个 LLM 后端的助手智能体负责提出执行任务的计划,一个执行器智能体(executor agent)负责在 ALFWorld 环境中执行动作。该系统集成了 ReAct 提示(Yao et al., 2022),能达到与之相当的性能。ReAct 与基于 AutoGen 的双智能体系统共同面临的一个挑战是:它们偶尔无法利用关于物理世界的基本常识。这一缺陷可能导致系统因重复犯错而陷入循环。幸运的是,AutoGen 的模块化设计让我们能有效解决这一问题:借助 AutoGen,我们可以引入一个**锚定智能体(grounding agent)**——每当系统出现重复错误的早期迹象,它就提供关键的常识知识,例如"你必须先找到并拿起物体,才能检查它;你必须先走到目标物体所在的位置,才能使用它"。这显著增强了系统避免纠缠于错误循环的能力。我们在 ALFWorld 的 134 个未见任务上,比较了系统的两个变体(使用 GPT-3.5-turbo)与 ReAct⁷ 的任务求解性能,结果见图 4c:引入锚定智能体平均可带来 **15%** 的性能提升。检查系统输出后我们观察到:锚定智能体在恰当时机递送背景常识,显著缓解了系统坚持错误计划的倾向,从而避免形成错误循环。对比两个系统的示例轨迹见附录 D 图 10。(原文脚注:⁷ ReAct 的结果由直接运行其官方代码(默认设置)得到;该代码使用 text-davinci-003 作为后端 LM,不支持 GPT-3.5-turbo 或 GPT-4。)

#### A4:多智能体编码

::: en
In this subsection, we use AutoGen to build a multi-agent coding system based on OptiGuide (Li et al., 2023a), a system that excels at writing code to interpret optimization solutions and answer user questions, such as exploring the implications of changing a supply-chain decision or understanding why the optimizer made a particular choice. The second sub-figure of Figure 3 shows the AutoGen-based implementation. The workflow is as follows: the end user sends questions, such as "What if we prohibit shipping from supplier 1 to roastery 2?" to the Commander agent. The Commander coordinates with two assistant agents, including the Writer and the Safeguard, to answer the question. The Writer will craft code and send the code to the Commander. After receiving the code, the Commander checks the code safety with the Safeguard; if cleared, the Commander will use external tools (e.g., Python) to execute the code, and request the Writer to interpret the execution results. For instance, the writer may say "if we prohibit shipping from supplier 1 to roastery 2, the total cost would increase by 10.5%." The Commander then provides this concluding answer to the end user. If, at a particular step, there is an exception, e.g., security red flag raised by Safeguard, the Commander redirects the issue back to the Writer with debugging information. The process might be repeated multiple times until the user's question is answered or timed-out.
:::

本小节用 AutoGen 基于 OptiGuide(Li et al., 2023a)构建一个多智能体编码系统。OptiGuide 擅长编写代码来解释优化方案并回答用户问题,例如探索改变某项供应链决策的影响,或理解优化器为何做出特定选择。图 3 的第二个子图展示了基于 AutoGen 的实现。工作流如下:终端用户把诸如"如果禁止从供应商 1 向烘焙厂 2 运货会怎样?"的问题发给 **Commander(指挥者)智能体**;Commander 与两个助手智能体——**Writer(撰写者)**与 **Safeguard(安全护栏)**——协作来回答问题。Writer 编写代码并发给 Commander;Commander 收到代码后,先请 Safeguard 检查代码安全性;通过检查后,Commander 使用外部工具(如 Python)执行代码,并请 Writer 解释执行结果——例如 Writer 可能说"如果禁止从供应商 1 向烘焙厂 2 运货,总成本将上升 10.5%"。随后 Commander 把这个结论性答案提供给终端用户。如果某一步出现异常(例如 Safeguard 亮起安全红旗),Commander 会带着调试信息把问题退回给 Writer。该过程可能重复多次,直到用户的问题得到回答或超时。

::: en
With AutoGen the core workflow code for OptiGuide was reduced from over 430 lines to 100 lines, leading to significant productivity improvement. We provide a detailed comparison of user experience with ChatGPT+Code Interpreter and AutoGen-based OptiGuide in Appendix D, where we show that AutoGen-based OptiGuide could save around 3x of user's time and reduce user interactions by 3 - 5 times on average. We also conduct an ablation showing that multi-agent abstraction is necessary. Specifically, we construct a single-agent approach where a single agent conducts both the code-writing and safeguard processes. We tested the single- and multi-agent approaches on a dataset of 100 coding tasks, which is crafted to include equal numbers of safe and unsafe tasks. Evaluation results as reported in Figure 4d show that the multi-agent design boosts the F-1 score in identifying unsafe code by 8% (with GPT-4) and 35% (with GPT-3.5-turbo).
:::

借助 AutoGen,OptiGuide 的核心工作流代码从 430 多行缩减到 **100 行**,带来显著的生产力提升。附录 D 给出了 ChatGPT+Code Interpreter 与基于 AutoGen 的 OptiGuide 的用户体验详细对比:基于 AutoGen 的 OptiGuide 可为用户节省约 3 倍时间,平均减少 3-5 倍用户交互。我们还做了一个证明多智能体抽象之必要性的消融实验:构造一个单智能体方案,让单个智能体同时承担写代码与安全护栏两个过程。我们在一个包含 100 个编码任务(安全与不安全任务各半)的数据集上测试了单/多智能体两种方案。图 4d 报告的评测结果显示:多智能体设计把识别不安全代码的 F1 分数提升了 **8%**(GPT-4)与 **35%**(GPT-3.5-turbo)。

#### A5:动态群聊

::: en
AutoGen provides native support for a dynamic group chat communication pattern, in which participating agents share the same context and converse with the others in a dynamic manner instead of following a pre-defined order. Dynamic group chat relies on ongoing conversations to guide the flow of interaction among agents. These make dynamic group chat ideal for situations where collaboration without strict communication order is beneficial. In AutoGen, the GroupChatManager class serves as the conductor of conversation among agents and repeats the following three steps: dynamically selecting a speaker, collecting responses from the selected speaker, and broadcasting the message (Figure 3-A5). For the dynamic speaker-selection component, we use a role-play style prompt. Through a pilot study on 12 manually crafted complex tasks, we observed that compared to a prompt that is purely based on the task, utilizing a role-play prompt often leads to more effective consideration of both conversation context and role alignment during the problem-solving and speaker-selection process. Consequently, this leads to a higher success rate and fewer LLM calls. We include detailed results in Appendix D.
:::

AutoGen 原生支持**动态群聊**通信模式:参与智能体共享同一上下文,以动态方式相互交谈,而不是遵循预定义顺序。动态群聊依赖持续进行的对话来引导智能体间的交互流。这些特点使动态群聊非常适合"无严格通信顺序的协作反而更有益"的场景。在 AutoGen 中,**GroupChatManager 类**充当智能体对话的指挥,循环执行三步:动态选择发言者、收集所选发言者的回复、广播该消息(图 3-A5)。动态发言者选择组件使用**角色扮演式(role-play)提示**。通过对 12 个手工构造的复杂任务的试点研究,我们观察到:与纯粹基于任务的提示相比,使用角色扮演提示往往能在解题与发言者选择过程中更有效地兼顾对话上下文与角色对齐,从而带来更高的成功率与更少的 LLM 调用。详细结果见附录 D。

#### A6:对话式国际象棋

::: en
Using AutoGen, we developed Conversational Chess, a natural language interface game shown in the last sub-figure of Figure 3. It features built-in agents for players, which can be human or LLM, and a third-party board agent to provide information and validate moves based on standard rules. With AutoGen, we enabled two essential features: (1) Natural, flexible, and engaging game dynamics, enabled by the customizable agent design in AutoGen. Conversational Chess supports a range of game-play patterns, including AI-AI, AI-human, and human-human, with seamless switching between these modes during a single game. An illustrative example of these entertaining game dynamics can be found in Figure 15, Appendix D. (2) Grounding, which is a crucial aspect to maintain game integrity. During gameplay, the board agent checks each proposed move for legality; if a move is invalid, the agent responds with an error, prompting the player agent to re-propose a legal move before continuing. This process ensures that only valid moves are played and helps maintain a consistent gaming experience. As an ablation study, we removed the board agent and instead only relied on a relevant prompt "you should make sure both you and the opponent are making legal moves" to ground their move. The results highlighted that without the board agent, illegitimate moves caused game disruptions. The modular design offered flexibility, allowing swift adjustments to the board agent in response to evolving game rules or varying chess rule variants. A comprehensive demonstration of this ablation study is in Appendix D.
:::

用 AutoGen,我们开发了 **Conversational Chess(对话式国际象棋)**——一个自然语言接口的游戏(图 3 最后一个子图)。它内置棋手智能体(可以是人类或 LLM)与一个第三方**棋盘智能体(board agent)**,后者提供信息并依据标准规则验证走法。借助 AutoGen,我们实现了两个关键特性:**(1) 自然、灵活、有趣的游戏动态**,由 AutoGen 可定制的智能体设计支撑:对话式国际象棋支持 AI-AI、AI-人类、人类-人类等多种对弈模式,且可在同一局游戏中无缝切换。这些有趣游戏动态的示例见附录 D 图 15。**(2) 锚定(grounding)**——维持游戏公正性的关键:对弈中,棋盘智能体检查每一个提议走法是否合法;若走法无效,它会回复错误,促使棋手智能体重新提议合法走法后再继续。该过程确保只有合法走法被执行,有助于维持一致的游戏体验。作为消融实验,我们移除棋盘智能体,只依赖相关提示"你应确保你和对手的走法都合法"来锚定走法。结果表明:没有棋盘智能体时,非法走法会破坏游戏。模块化设计提供了灵活性,可随游戏规则演进或不同棋规变体迅速调整棋盘智能体。该消融实验的完整演示见附录 D。

### 4 讨论

::: en
We introduced an open-source library, AutoGen, that incorporates the paradigms of conversable agents and conversation programming. This library utilizes capable agents that are well-suited for multi-agent cooperation. It features a unified conversation interface among the agents, along with an auto-reply mechanisms, which help establish an agent-interaction interface that capitalizes on the strengths of chat-optimized LLMs with broad capabilities while accommodating a wide range of applications. AutoGen serves as a general framework for creating and experimenting with multi-agent systems that can easily fulfill various practical requirements, such as reusing, customizing, and extending existing agents, as well as programming conversations between them.
:::

我们介绍了融合可对话智能体与对话编程两大范式的开源库 AutoGen。该库使用的智能体能力强大、非常适合多智能体合作;它具备智能体间的统一会话接口与 auto-reply 机制,共同建立起一个能发挥聊天优化 LLM 广谱能力优势、同时容纳广泛应用的智能体交互接口。AutoGen 是创建与实验多智能体系统的通用框架,可以轻松满足各种实际需求:复用、定制、扩展现有智能体,以及编程它们之间的对话。

::: en
Our experiments, as detailed in Section 3, demonstrate that this approach offers numerous benefits. The adoption of AutoGen has resulted in improved performance (over state-of-the-art approaches), reduced development code, and decreased manual burden for existing applications. It offers flexibility to developers, as demonstrated in A1 (scenario 3), A5, and A6, where AutoGen enables multi-agent chats to follow a dynamic pattern rather than fixed back-and-forth interactions. It allows humans to engage in activities alongside multiple AI agents in a conversational manner. Despite the complexity of these applications (most involving more than two agents or dynamic multi-turn agent cooperation), the implementation based on AutoGen remains straightforward. Dividing tasks among separate agents promotes modularity. Furthermore, since each agent can be developed, tested, and maintained separately, this approach simplifies overall development and code management.
:::

如第 3 节所述,我们的实验表明这一方法带来诸多收益:对既有应用而言,采用 AutoGen 带来了(超过最先进方法的)性能提升、更少的开发代码与更低的人工负担。它也给开发者带来灵活性——如 A1(场景 3)、A5、A6 所示,AutoGen 使多智能体聊天可以遵循动态模式而非固定的来回交互;它允许人类以对话方式与多个 AI 智能体一同参与活动。尽管这些应用很复杂(多数涉及两个以上智能体或动态多轮智能体协作),基于 AutoGen 的实现依然简洁。把任务拆分给独立的智能体促进了模块化;而且由于每个智能体可以单独开发、测试与维护,这种方式简化了整体开发与代码管理。

::: en
Although this work is still in its early experimental stages, it paves the way for numerous future directions and research opportunities. For instance, we can explore effective integration of existing agent implementations into our multi-agent framework and investigate the optimal balance between automation and human control in multi-agent workflows. As we further develop and refine AutoGen, we aim to investigate which strategies, such as agent topology and conversation patterns, lead to the most effective multi-agent conversations while optimizing the overall efficiency, among other factors. While increasing the number of agents and other degrees of freedom presents opportunities for tackling more complex problems, it may also introduce new safety challenges that require additional studies and careful consideration.
:::

尽管本工作仍处于早期实验阶段,它为众多未来方向与研究机会铺平了道路。例如,可以探索把既有的智能体实现有效整合进我们的多智能体框架,并研究多智能体工作流中自动化与人类控制的最佳平衡。随着进一步开发与完善 AutoGen,我们打算研究哪些策略(如智能体拓扑与对话模式)能带来最有效的多智能体对话,同时优化整体效率等因素。增加智能体数量与其他自由度虽为处理更复杂问题带来机会,也可能引入需要额外研究与审慎考虑的新安全挑战。

::: en
We provide more discussion in Appendix B, including guidelines for using AutoGen and direction of future work. We hope AutoGen will help improve many LLM applications in terms of speed of development, ease of experimentation, and overall effectiveness and safety. We actively welcome contributions from the broader community.
:::

我们在附录 B 提供更多讨论,包括 AutoGen 的使用指南与未来工作方向。我们希望 AutoGen 能帮助改进许多 LLM 应用的开发速度、实验便利性以及整体有效性与安全性,并积极欢迎更广泛社区的贡献。

### 伦理声明

::: en
There are several potential ethical considerations that could arise from the development and use of the AutoGen framework.

**• Privacy and Data Protection:** The framework allows for human participation in conversations between agents. It is important to ensure that user data and conversations are protected, and that developers use appropriate measures to safeguard privacy.

**• Bias and Fairness:** LLMs have been shown to exhibit biases present in their training data (Navigli et al., 2023). When using LLMs in the AutoGen framework, it is crucial to address and mitigate any biases that may arise in the conversations between agents. Developers should be aware of potential biases and take steps to ensure fairness and inclusivity.

**• Accountability and Transparency:** As discussed in the future work section, as the framework involves multiple agents conversing and cooperating, it is important to establish clear accountability and transparency mechanisms. Users should be able to understand and trace the decision-making process of the agents involved in order to ensure accountability and address any potential issues or biases.

**• Trust and Reliance:** AutoGen leverages human understanding and intelligence while providing automation through conversations between agents. It is important to consider the impact of this interaction on user experience, trust, and reliance on AI systems. Clear communication and user education about the capabilities and limitations of the system will be essential (Cai et al., 2019).

**• Unintended Consequences:** As discussed before, the use of multi-agent conversations and automation in complex tasks may have unintended consequences. In particular, allowing LLM agents to make changes in external environments through code execution or function calls, such as installing packages, could be risky. Developers should carefully consider the potential risks and ensure that appropriate safeguards are in place to prevent harm or negative outcomes.
:::

AutoGen 框架的开发与使用可能引发若干伦理考量:

**• 隐私与数据保护**:该框架允许人类参与智能体间的对话。必须确保用户数据与对话受到保护,开发者应使用适当措施保障隐私。

**• 偏见与公平**:已有研究表明 LLM 会表现出训练数据中存在的偏见(Navigli et al., 2023)。在 AutoGen 框架中使用 LLM 时,必须处理并缓解智能体对话中可能出现的任何偏见。开发者应意识到潜在偏见,并采取措施确保公平与包容。

**• 问责与透明**:如未来工作部分所讨论,该框架涉及多个智能体对话与协作,建立清晰的问责与透明机制十分重要。用户应能理解并追溯相关智能体的决策过程,以确保问责、处理任何潜在问题或偏见。

**• 信任与依赖**:AutoGen 在通过智能体间对话提供自动化的同时,也利用着人类的理解力与智能。必须考虑这种交互对用户体验、信任以及对 AI 系统依赖的影响。就系统能力与局限进行清晰的沟通和用户教育将至关重要(Cai et al., 2019)。

**• 意外后果**:如前所述,在复杂任务中使用多智能体对话与自动化可能产生意外后果。尤其是允许 LLM 智能体通过代码执行或函数调用改变外部环境(例如安装软件包)可能有风险。开发者应仔细考虑潜在风险,确保有适当的防护措施以防止伤害或负面结果。

> **致谢(译注)**:作者感谢 Peter Lee、Johannes Gehrke、Eric Horvitz 等众多微软研究院同事的讨论与反馈(完整名单见原文),并感谢宾州州立大学信息科学与技术学院对 Qingyun Wu 的资助支持。人名列表从略。

### 附录 A 相关工作

::: en
We examine existing LLM-based agent systems or frameworks that can be used to build LLM applications. We categorize the related work into single-agent and multi-agent systems and specifically provide a summary of differentiators comparing AutoGen with existing multi-agent systems in Table 1. Note that many of these systems are evolving open-source projects, so the remarks and statements about them may only be accurate as of the time of writing. We refer interested readers to detailed LLM-based agent surveys (Xi et al., 2023; Wang et al., 2023b).

**Single-Agent Systems:**

• **AutoGPT:** AutoGPT is an open-source implementation of an AI agent that attempts to autonomously achieve a given goal (AutoGPT, 2023). It follows a single-agent paradigm in which it augments the AI model with many useful tools, and does not support multi-agent collaboration.

• **ChatGPT+ (with code interpreter or plugin):** ChatGPT, a conversational AI service or agent, can now be used alongside a code interpreter or plugin (currently available only under the premium subscription plan ChatGPT Plus) (OpenAI, 2023). The code interpreter enables ChatGPT to execute code, while the plugin enhances ChatGPT with a wide range of curated tools.

• **LangChain Agents:** LangChain is a general framework for developing LLM-based applications (LangChain, 2023). LangChain Agents is a subpackage for using an LLM to choose a sequence of actions. There are various types of agents in LangChain Agents, with the ReAct agent being a notable example that combines reasoning and acting when using LLMs (mainly designed for LLMs prior to ChatGPT) (Yao et al., 2022). All agents provided in LangChain Agents follow a single-agent paradigm and are not inherently designed for communicative and collaborative modes. A significant summary of its limitations can be found in (Woolf, 2023). Due to these limitations, even the multi-agent systems in LangChain (e.g., re-implementation of CAMEL) are not based on LangChain Agents but are implemented from scratch. Their connection to LangChain lies in the use of basic orchestration modules provided by LangChain, such as AI models wrapped by LangChain and the corresponding interface.

• **Transformers Agent:** Transformers Agent (HuggingFace, 2023) is an experimental natural-language API built on the transformers repository. It includes a set of curated tools and an agent to interpret natural language and use these tools. Similar to AutoGPT, it follows a single-agent paradigm and does not support agent collaboration.

AutoGen differs from the single-agent systems above by supporting multi-agent LLM applications.

**Multi-Agent Systems:**

• **BabyAGI:** BabyAGI (BabyAGI, 2023) is an example implementation of an AI-powered task management system in a Python script. In this implemented system, multiple LLM-based agents are used. For example, there is an agent for creating new tasks based on the objective and the result of the previous task, an agent for prioritizing the task list, and an agent for completing tasks/sub-tasks. As a multi-agent system, BabyAGI adopts a static agent conversation pattern, i.e., a predefined order of agent communication, while AutoGen supports both static and dynamic conversation patterns and additionally supports tool usage and human involvement.

• **CAMEL:** CAMEL (Li et al., 2023b) is a communicative agent framework. It demonstrates how role playing can be used to let chat agents communicate with each other for task completion. It also records agent conversations for behavior analysis and capability understanding. An Inception-prompting technique is used to achieve autonomous cooperation between agents. Unlike AutoGen, CAMEL does not natively support tool usage, such as code execution. Although it is proposed as an infrastructure for multi-agent conversation, it only supports static conversation patterns, while AutoGen additionally supports dynamic conversation patterns.

• **Multi-Agent Debate:** Two recent works investigate and show that multi-agent debate is an effective way to encourage divergent thinking in LLMs (Liang et al., 2023) and to improve the factuality and reasoning of LLMs (Du et al., 2023). In both works, multiple LLM inference instances are constructed as multiple agents to solve problems with agent debate. Each agent is simply an LLM inference instance, while no tool or human is involved, and the inter-agent conversation needs to follow a pre-defined order. These works attempt to build LLM applications with multi-agent conversation, while AutoGen, designed as a generic infrastructure, can be used to facilitate this development and enable more applications with dynamic conversation patterns.

• **MetaGPT:** MetaGPT (Hong et al., 2023) is a specialized LLM application based on a multi-agent conversation framework for automatic software development. They assign different roles to GPTs to collaboratively develop software. They differ from AutoGen by being specialized solutions to a certain scenario, while AutoGen is a generic infrastructure to facilitate building applications for various scenarios.

There are a few other specialized single-agent or multi-agent systems, such as Voyager (Wang et al., 2023a) and Generative Agents (Park et al., 2023), which we skip due to lower relevance. In Table 1, we summarize differences between AutoGen and the most relevant multi-agent systems.
:::

我们考察既有的、可用于构建 LLM 应用的基于 LLM 的智能体系统或框架,把相关工作分为单智能体与多智能体系统两类,并在表 1 中专门总结 AutoGen 与既有**多智能体**系统的差异。注意:其中许多系统是持续演进的开源项目,相关评述仅截至论文撰写时可能准确。有兴趣的读者可参阅详细的 LLM 智能体综述(Xi et al., 2023; Wang et al., 2023b)。

**单智能体系统:**

- **AutoGPT**:一个开源 AI 智能体实现,尝试自主达成给定目标(AutoGPT, 2023)。它遵循单智能体范式,用许多有用工具增强 AI 模型,不支持多智能体协作。
- **ChatGPT+(代码解释器或插件)**:对话式 AI 服务/智能体 ChatGPT 现可搭配代码解释器或插件使用(目前仅在付费订阅 ChatGPT Plus 下可用)(OpenAI, 2023)。代码解释器使 ChatGPT 能执行代码;插件则为 ChatGPT 增加大量精选工具。
- **LangChain Agents**:LangChain 是开发 LLM 应用的通用框架(LangChain, 2023);LangChain Agents 是其用于"让 LLM 选择动作序列"的子包,包含多种智能体类型,其中 ReAct 智能体是结合推理与行动的著名例子(主要面向 ChatGPT 之前的 LLM 设计)(Yao et al., 2022)。LangChain Agents 提供的所有智能体都遵循单智能体范式,本质上并非为"可交流、可协作"模式设计;(Woolf, 2023) 对其局限有很好的总结。受这些局限所累,LangChain 生态中的多智能体系统(如 CAMEL 的复实现)甚至并不基于 LangChain Agents,而是从零实现——它们与 LangChain 的联系仅在于使用 LangChain 提供的基础编排模块,如被 LangChain 封装的 AI 模型及相应接口。
- **Transformers Agent**:建立在 transformers 仓库上的实验性自然语言 API(HuggingFace, 2023),包含一组精选工具与一个解释自然语言并使用这些工具的智能体。与 AutoGPT 类似,它遵循单智能体范式,不支持智能体协作。

AutoGen 与上述单智能体系统的差异在于:它支持**多智能体** LLM 应用。

**多智能体系统:**

- **BabyAGI**:一个用 Python 脚本实现的 AI 任务管理系统示例(BabyAGI, 2023)。该实现使用了多个 LLM 智能体:例如根据目标与上一任务结果创建新任务的智能体、给任务列表排优先级的智能体、完成任务/子任务的智能体。作为多智能体系统,BabyAGI 采用**静态**智能体对话模式(即预定义的智能体通信顺序),而 AutoGen 同时支持静态与动态对话模式,并额外支持工具使用与人类介入。
- **CAMEL**:一个交流式智能体框架(Li et al., 2023b),展示了如何用角色扮演让聊天智能体相互交流以完成任务;它还记录智能体对话用于行为分析与能力理解,并用"Inception-prompting"技术实现智能体间自主合作。与 AutoGen 不同,CAMEL 原生不支持工具使用(如代码执行);虽然它被提出作为多智能体对话的基础设施,但只支持静态对话模式,而 AutoGen 还支持动态对话模式。
- **Multi-Agent Debate(多智能体辩论)**:两项近期工作研究并表明,多智能体辩论能有效促进 LLM 的发散思维(Liang et al., 2023)、提高 LLM 的事实性与推理(Du et al., 2023)。两项工作都把多个 LLM 推理实例构造成多个智能体进行辩论解题;每个智能体只是一个 LLM 推理实例,不涉及工具或人类,智能体间对话须遵循预定义顺序。这些工作尝试用多智能体对话构建 LLM 应用;而 AutoGen 作为通用基础设施设计,可用来辅助这类开发,并通过动态对话模式支持更多应用。
- **MetaGPT**:一个基于多智能体对话框架的专门化 LLM 应用,用于自动软件开发(Hong et al., 2023)。他们给 GPT 分配不同角色来协作开发软件。与 AutoGen 的差异在于:它们是面向特定场景的专门化解决方案,而 AutoGen 是便于构建各种场景应用的通用基础设施。

还有少数其他专门化的单/多智能体系统,如 Voyager(Wang et al., 2023a)与 Generative Agents(Park et al., 2023),因相关性较低而略过。表 1 总结了 AutoGen 与最相关多智能体系统的差异。

**表 1:AutoGen 与其他相关多智能体系统的差异总结**(infrastructure:是否被设计为构建 LLM 应用的通用基础设施;conversation pattern:已实现系统支持的对话模式类型——"静态(static)"模式下智能体拓扑不随输入变化,AutoGen 支持包括静态与动态、可按应用需求定制的灵活对话模式;execution-capable:能否执行 LLM 生成的代码;human involvement:是否(以及如何)允许人类在系统执行过程中参与——AutoGen 允许人类灵活介入多智能体对话,并允许人类跳过输入)

| 维度 | AutoGen | Multi-agent Debate | CAMEL | BabyAGI | MetaGPT |
| --- | --- | --- | --- | --- | --- |
| 通用基础设施(Infrastructure) | ✓ | ✗ | ✓ | ✗ | ✗ |
| 对话模式(conversation pattern) | 灵活(flexible) | 静态 | 静态 | 静态 | 静态 |
| 可执行代码(execution-capable) | ✓ | ✗ | ✗ | ✗ | ✓ |
| 人类介入(human involvement) | 对话/可跳过(chat/skip) | ✗ | ✗ | ✗ | ✗ |

### 附录 B 扩展讨论

::: en
The applications in Section 3 show how AutoGen not only enables new applications but also helps renovate existing ones. For example, in A1 (scenario 3), A5, and A6, AutoGen enabled the creation of multi-agent conversations that follow a dynamic pattern instead of a fixed back-and-forth. And in both A5 and A6, humans can participate in the activities together with multiple other AI agents in a conversational manner. Similarly, A1-A4 show how popular applications can be renovated quickly with AutoGen. Despite the complexity of these applications (most of them involve more than two agents or dynamic multi-turn agent cooperation), our AutoGen-based implementation remains simple, demonstrating promising opportunities to build creative applications and a large space for innovation. In reflecting on why these benefits can be achieved in these applications with AutoGen, we believe there are a few reasons:

**• Ease of use:** The built-in agents can be used out-of-the-box, delivering strong performance even without any customization. (A1, A3)

**• Modularity:** The division of tasks into separate agents promotes modularity in the system. Each agent can be developed, tested, and maintained independently, simplifying the overall development process and facilitating code management. (A3, A4, A5, and A6)

**• Programmability:** AutoGen allows users to extend/customize existing agents to develop systems satisfying their specific needs with ease. (A1-A6). For example, with AutoGen, the core workflow code in A4 is reduced from over 430 lines to 100 lines, for a 4x saving.

**• Allowing human involvement:** AutoGen provides a native mechanism to achieve human participation and/or human oversight. With AutoGen, humans can seamlessly and optionally cooperate with AIs to solve problems or generally participate in the activity. AutoGen also facilitates interactive user instructions to ensure the process stays on the desired path. (A1, A2, A5, and A6)

**• Collaborative/adversarial agent interactions:** Like many collaborative agent systems (Dong et al., 2023), agents in AutoGen can share information and knowledge, to complement each other's abilities and collectively arrive at better solutions. (A1, A2, A3, and A4). Analogously, in certain scenarios, some agents are required to work in an adversarial way. Relevant information is shared among different conversations in a controlled manner, preventing distraction or hallucination. (A4, A6). AutoGen supports both patterns, enabling effective utilization and augmentation of LLMs.
:::

第 3 节的应用展示了 AutoGen 不仅支持新应用,也能翻新既有应用。例如在 A1(场景 3)、A5、A6 中,AutoGen 实现了遵循动态模式而非固定来回的多智能体对话;在 A5 与 A6 中,人类还能以对话方式与多个 AI 智能体一同参与活动。类似地,A1-A4 展示了流行应用如何用 AutoGen 快速翻新。尽管这些应用复杂(多数涉及两个以上智能体或动态多轮智能体协作),我们基于 AutoGen 的实现依然简洁,显示出构建创意应用的可观机会与巨大的创新空间。反思为什么这些应用能借 AutoGen 获得这些收益,我们认为有以下几个原因:

- **易用性**:内置智能体可开箱即用,无需任何定制就能交付强劲性能(A1、A3)。
- **模块化**:把任务拆分给独立智能体促进了系统模块化。每个智能体可独立开发、测试与维护,简化整体开发流程并便利代码管理(A3、A4、A5、A6)。
- **可编程性**:AutoGen 允许用户轻松扩展/定制既有智能体,开发满足特定需求的系统(A1-A6)。例如在 A4 中,核心工作流代码从 430 多行减至 100 行,节省约 4 倍。
- **允许人类介入**:AutoGen 提供实现人类参与和/或人类监督的原生机制。借助 AutoGen,人类可以无缝且可选地与 AI 合作解决问题或参与活动;AutoGen 还便于交互式用户指令,确保过程沿期望路径进行(A1、A2、A5、A6)。
- **协作/对抗式智能体交互**:与许多协作式智能体系统一样(Dong et al., 2023),AutoGen 中的智能体可共享信息与知识,互补能力、共同得到更好的解(A1、A2、A3、A4)。类似地,某些场景中需要一些智能体以对抗方式工作:相关信息在不同对话间以受控方式共享,防止分心或幻觉(A4、A6)。AutoGen 同时支持这两种模式,实现对 LLM 的有效利用与增强。

#### B.1 使用 AutoGen 的一般指南

::: en
Below we give some recommendations for using agents in AutoGen to accomplish a task.

1. **Consider using built-in agents first.** For example, AssistantAgent is pre-configured to be backed by GPT-4, with a carefully designed system message for generic problem-solving via code. The UserProxyAgent is configured to solicit human inputs and perform tool execution. Many problems can be solved by simply combining these two agents. When customizing agents for an application, consider the following options: (1) human input mode, termination condition, code execution configuration, and LLM configuration can be specified when constructing an agent; (2) AutoGen supports adding instructions in an initial user message, which is an effective way to boost performance without needing to modify the system message; (3) UserProxyAgent can be extended to handle different execution environments and exceptions, etc.; (4) when system message modification is needed, consider leveraging the LLM's capability to program its conversation flow with natural language.

2. **Start with a simple conversation topology.** Consider using the two-agent chat or the group chat setup first, as they can often be extended with the least code. Note that the two-agent chat can be easily extended to involve more than two agents by using LLM-consumable functions in a dynamic way.

3. **Try to reuse built-in reply methods based on LLM, tool, or human before implementing a custom reply method** because they can often be reused to achieve the goal in a simple way (e.g., the built-in agent GroupChatManager's reply method reuses the built-in LLM-based reply function when selecting the next speaker, ref. A5 in Section 3).

4. **When developing a new application with UserProxyAgent, start with humans always in the loop**, i.e., human input mode='ALWAYS', even if the target operation mode is more autonomous. This helps evaluate the effectiveness of AssistantAgent, tuning the prompt, discovering corner cases, and debugging. Once confident with small-scale success, consider setting human input mode = 'NEVER'. This enables LLM as a backend, and one can either use the LLM or manually generate diverse system messages to simulate different use cases.

5. Despite the numerous advantages of AutoGen agents, there could be cases/scenarios where other libraries/packages could help. For example: (1) For (sub)tasks that do not have requirements for back-and-forth trouble-shooting, multi-agent interaction, etc., a unidirectional (no back-and-forth message exchange) pipeline can also be orchestrated with LangChain (LangChain, 2023), LlamaIndex (Liu, 2022), Guidance (Guidance, 2023), Semantic Kernel (Semantic-Kernel, 2023), Gorilla (Patil et al., 2023) or low-level inference API ('autogen.oai' provides an enhanced LLM inference layer at this level) (Dibia, 2023). (2) When existing tools from LangChain etc. are helpful, one can use them as tool backends for AutoGen agents. For example, one can readily use tools, e.g., Wolfram Alpha, from LangChain in AutoGen agent. (3) For specific applications, one may want to leverage agents implemented in other libraries/packages. To achieve this, one could wrap those agents as conversable agents in AutoGen and then use them to build LLM applications through multi-agent conversation. (4) It can be hard to find an optimal operating point among many tunable choices, such as the LLM inference configuration. Blackbox optimization packages like 'flaml.tune' (Wang et al., 2021) can be used together with AutoGen to automate such tuning.
:::

下面给出用 AutoGen 智能体完成任务的一些建议。

1. **优先考虑内置智能体。** 例如,AssistantAgent 预配置为 GPT-4 后端,带有为"用代码进行通用问题求解"精心设计的系统消息;UserProxyAgent 则配置为征求人类输入并执行工具。许多问题只需组合这两个智能体即可解决。为应用定制智能体时,可考虑:(1) 构造智能体时指定人类输入模式、终止条件、代码执行配置与 LLM 配置;(2) AutoGen 支持在初始用户消息中加入指令,这是无需修改系统消息即可提升性能的有效方式;(3) 可扩展 UserProxyAgent 以处理不同执行环境与异常等;(4) 需要修改系统消息时,考虑利用 LLM 用自然语言编程其对话流的能力。
2. **从简单的会话拓扑开始。** 优先考虑双智能体聊天或群聊设定,它们往往能用最少的代码扩展。注意:通过以动态方式使用 LLM 可消费的函数,双智能体聊天可轻松扩展到两个以上智能体。
3. **实现自定义回复方法之前,先尝试复用基于 LLM、工具或人类的内置回复方法**——它们往往能以简单方式复用来达成目标(例如内置智能体 GroupChatManager 的回复方法在选择下一个发言者时,就复用了内置的基于 LLM 的回复函数,参见第 3 节 A5)。
4. **用 UserProxyAgent 开发新应用时,从"人类始终在环"开始**,即 human_input_mode='ALWAYS',哪怕目标运行模式更自主。这有助于评估 AssistantAgent 的有效性、调优提示、发现边界情况与调试。在小规模成功建立信心后,再考虑设 human_input_mode='NEVER'——这会启用 LLM 作为后端,既可以直接用 LLM,也可以手工生成多样的系统消息来模拟不同用例。
5. 尽管 AutoGen 智能体优势众多,也有些场景是其他库/包更合适的。例如:(1) 对不需要来回排障、多智能体交互等的(子)任务,单向(无来回消息交换)流水线也可以用 LangChain(LangChain, 2023)、LlamaIndex(Liu, 2022)、Guidance(Guidance, 2023)、Semantic Kernel(Semantic-Kernel, 2023)、Gorilla(Patil et al., 2023)或低层推理 API 编排(此层面 'autogen.oai' 提供了增强的 LLM 推理层)(Dibia, 2023);(2) 当 LangChain 等既有工具有用时,可以把它们当作 AutoGen 智能体的工具后端——例如可以方便地在 AutoGen 智能体中使用 LangChain 的 Wolfram Alpha 等工具;(3) 对特定应用,可能想利用其他库/包实现的智能体:可以把那些智能体包装成 AutoGen 的可对话智能体,再通过多智能体对话构建 LLM 应用;(4) 在许多可调选项(如 LLM 推理配置)中找最优点可能很难,可把 'flaml.tune'(Wang et al., 2021)这类黑盒优化包与 AutoGen 结合,自动化此类调优。

#### B.2 未来工作

::: en
This work raises many research questions and future directions and .

**Designing optimal multi-agent workflows:** Creating a multi-agent workflow for a given task can involve many decisions, e.g., how many agents to include, how to assign agent roles and agent capabilities, how the agents should interact with each other, and whether to automate a particular part of the workflow. There may not exist a one-fits-all answer, and the best solution might depend on the specific application. This raises important questions: For what types of tasks and applications are multi-agent workflows most useful? How do multiple agents help in different applications? For a given task, what is the optimal (e.g., cost-effective) multi-agent workflow?

**Creating highly capable agents:** AutoGen can enable the development of highly capable agents that leverage the strengths of LLMs, tools, and humans. Creating such agents is crucial to ensuring that a multi-agent workflow can effectively troubleshoot and make progress on a task. For example, we observed that CAMEL, another multi-agent LLM system, cannot effectively solve problems in most cases primarily because it lacks the capability to execute tools or code. This failure shows that LLMs and multi-agent conversations with simple role playing are insufficient, and highly capable agents with diverse skill sets are essential. We believe that more systematic work will be required to develop guidelines for application-specific agents, to create a large OSS knowledge base of agents, and to create agents that can discover and upgrade their skills (Cai et al., 2023).

**Enabling scale, safety, and human agency:** Section 3 shows how complex multi-agent workflows can enable new applications, and future work will be needed to assess whether scaling further can help solve extremely complex tasks. However, as these workflows scale and grow more complex, it may become difficult to log and adjust them. Thus, it will become essential to develop clear mechanisms and tools to track and debug their behavior. Otherwise, these techniques risk resulting in incomprehensible, unintelligible chatter among agents (Lewis et al., 2017).

Our work also shows how complex, fully autonomous workflows with AutoGen can be useful, but fully autonomous agent conversations will need to be used with care. While the autonomous mode AutoGen supports could be desirable in many scenarios, a high level of autonomy can also pose potential risks, especially in high-risk applications (Amodei et al., 2016; Weld & Etzioni, 1994). As a result, building fail-safes against cascading failures and exploitation, mitigating reward hacking, out of control and undesired behaviors, maintaining effective human oversight of applications built with AutoGen agents will become important. While AutoGen provides convenient and seamless involvement of humans through a user proxy agent, developers and stakeholders still need to understand and determine the appropriate level and pattern of human involvement to ensure the safe and ethical use of the technology (Horvitz, 1999; Amershi et al., 2019).
:::

本工作引出许多研究问题与未来方向。

**设计最优的多智能体工作流**:为给定任务创建多智能体工作流涉及许多决策,例如包含多少智能体、如何分配智能体角色与能力、智能体之间应如何交互、是否自动化工作流的某一部分。可能不存在万能答案,最优解可能取决于具体应用。由此引出重要问题:多智能体工作流对哪些类型的任务与应用最有用?多个智能体在不同应用中如何提供帮助?对给定任务,什么是最优(如性价比最高)的多智能体工作流?

**创建高能力智能体**:AutoGen 能支持开发结合 LLM、工具与人类之长的高能力智能体。创建这样的智能体,对确保多智能体工作流能有效排障并在任务上取得进展至关重要。例如,我们观察到另一个多智能体 LLM 系统 CAMEL 在多数情况下不能有效解题,主要原因就是它缺乏执行工具或代码的能力。这一失败说明:仅有 LLM 与简单角色扮演的多智能体对话是不够的,拥有多样技能的高能力智能体不可或缺。我们相信,还需要更系统的工作来制定面向特定应用的智能体开发指南、构建大型开源智能体知识库、以及创造能发现并升级自身技能的智能体(Cai et al., 2023)。

**实现规模、安全与人类能动性**:第 3 节展示了复杂多智能体工作流如何催生新应用;未来还需评估进一步扩展规模能否帮助解决极复杂任务。然而,随着工作流规模扩大、复杂度提升,记录与调整它们可能变得困难。因此,开发清晰的机制与工具来追踪与调试其行为将变得不可或缺——否则这些技术有可能沦为智能体之间难以理解、不知所云的闲聊(Lewis et al., 2017)。

我们的工作也表明,基于 AutoGen 的复杂全自动工作流可以很有用,但完全自主的智能体对话需要谨慎使用。AutoGen 支持的自主模式在许多场景中是理想的,但高自主性也可能带来潜在风险,尤其在高风险应用中(Amodei et al., 2016; Weld & Etzioni, 1994)。因此,构建防止级联失败与被利用的失效保护、缓解奖励黑客行为、失控与不良行为,以及对基于 AutoGen 智能体的应用保持有效的人类监督,都将变得重要。虽然 AutoGen 通过用户代理智能体提供了便捷无缝的人类介入,开发者与利益相关者仍需理解并确定恰当的人类介入级别与模式,以确保技术的安全与合乎伦理的使用(Horwitz, 1999; Amershi et al., 2019)。

### 附录 C 助手智能体的默认系统消息

[图 5: Default system message for the built-in assistant agent in AutoGen (v0.1.1). This is an example of conversation programming via natural language. It contains instructions of different types, including role play, control flow, output confine, facilitate automation, and grounding.]

图 5:AutoGen 内置助手智能体(v0.1.1)的默认系统消息。这是**用自然语言进行对话编程**的一个例子,包含多种类型的指令:角色扮演(role play)、控制流(control flow)、输出约束(output confine)、便利自动化(facilitate automation)与锚定(grounding)——原文中不同颜色的文字对应不同指令类型。系统消息原文(一字未改)如下:

```text
You are a helpful AI assistant. Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply "TERMINATE" in the end when everything is done.
```

**中文全译**:

> 你是一个乐于助人的 AI 助手。请用你的编码与语言技能解决任务。
> 在下列情况下,建议 python 代码(放在 python 代码块中)或 shell 脚本(放在 sh 代码块中)供用户执行:
> 1. 当你需要收集信息时,用代码输出所需信息,例如浏览或搜索网页、下载/读取文件、打印网页或文件内容、获取当前日期/时间。在打印出足够信息、任务可以基于你的语言技能解决后,你可以自行解决任务。
> 2. 当你需要用代码执行某项任务时,用代码执行任务并输出结果。聪明地完成任务。
> 如有需要,请一步一步地解决任务。若未提供计划,先解释你的计划。说清楚哪一步用代码、哪一步用你的语言技能。
> 使用代码时,必须在代码块中标明脚本类型。用户无法提供执行你建议的代码之外的任何其他反馈或行动;用户不能修改你的代码,所以不要建议需要用户修改的不完整代码。若不打算让用户执行,就不要使用代码块。
> 若希望用户先把代码保存为文件再执行,把 # filename: <文件名> 作为代码块的第一行。一条回复中不要包含多个代码块。不要让用户复制粘贴结果,而是相关时用 'print' 函数输出。检查用户返回的执行结果。
> 如果结果表明有错误,修复错误并再次输出代码。建议完整代码而非部分代码或代码改动。如果错误无法修复、或代码成功执行后任务仍未解决,分析问题、重新审视你的假设、收集你需要的额外信息,并尝试想出不同的方法。
> 找到答案时,仔细验证答案。尽可能在回复中附上可验证的证据。
> 全部完成后,最后回复 "TERMINATE"。

::: en
Figure 5 shows the default system message for the built-in assistant agent in AutoGen (v0.1.1), where we introduce several new prompting techniques and highlight them accordingly. When combining these new prompting techniques together, we can program a fairly complex conversation even with the simplest two-agent conversation topology. This approach tries to exploit the capability of LLMs in implicit state inference to a large degree. LLMs do not follow all the instructions perfectly, so the design of the system needs to have other mechanisms to handle the exceptions and faults. Some instructions can have ambiguities, and the designer should either reduce them for preciseness or intentionally keep them for flexibility and address the different situations in other agents. In general, we observe that GPT-4 follows the instructions better than GPT-3.5-turbo.
:::

图 5 展示了 AutoGen 内置助手智能体(v0.1.1)的默认系统消息,其中我们引入了若干新的提示技术并做了相应标注。把这些新提示技术组合起来,即便用最简单的双智能体会话拓扑,也能编程出相当复杂的对话。这一做法试图在很大程度上利用 LLM 的隐式状态推断能力。LLM 并不会完美遵循所有指令,因此系统设计需要有其他机制来处理异常与故障。有些指令可能有歧义,设计者要么为精确性而消除歧义,要么为灵活性而有意保留,并在其他智能体中处理不同情形。总体上,我们观察到 GPT-4 比 GPT-3.5-turbo 更好地遵循指令。

### 附录 D 应用细节

#### A1:数学解题(附录 D)

::: en
**Scenario 1: Autonomous Problem Solving.** We perform both qualitative and quantitative evaluations in this scenario. For all evaluations, we use GPT-4 as the base model, and pre-install the "sympy" package in the execution environment. We compare AutoGen with the following LLM-based agent systems:

• **AutoGPT:** The out-of-box AutoGPT is used. We initialize AutoGPT by setting the purpose to "solve math problems", resulting in a "MathSolverGPT" with auto-generated goals.

• **ChatGPT+Plugin:** We enable the Wolfram Alpha plugin (a math computation engine) in the OpenAI web client.

• **ChatGPT+Code Interpreter:** This is a recent feature in OpenAI web client. Note that the above two premium features from ChatGPT require a paid subscription to be accessed and are the most competitive commercial systems.

• **LangChain ReAct+Python:** We use Python agent from LangChain. To handle parsing errors, we set "handle_parsing_errors=True", and use the default zero-shot ReAct prompt.

• **Multi-Agent Debate (Liang et al., 2023):** We modified the code of the multi-agent debate to perform evaluation. By default, there are three agents: an affirmative agent, a negative agent, and a moderator.

We also conducted preliminary evaluations on several other multi-agent systems, including BabyAGI, CAMEL, and MetaGPT. The results indicate that they are not suitable choices for solving math problems out of the box. For instance, when MetaGPT is tasked with solving a math problem, it begins developing software to address the problem, but most of the time, it does not actually solve the problem. We have included the test examples in Appendix E.
:::

**场景 1:自主解题。** 我们在此场景中同时进行定性与定量评测。所有评测均用 GPT-4 作基座模型,并在执行环境中预装 "sympy" 包。我们将 AutoGen 与以下基于 LLM 的智能体系统对比:

- **AutoGPT**:使用开箱即用的 AutoGPT,把用途设为"解决数学问题"来初始化,得到一个目标自动生成的 "MathSolverGPT"。
- **ChatGPT+Plugin**:在 OpenAI 网页客户端启用 Wolfram Alpha 插件(数学计算引擎)。
- **ChatGPT+Code Interpreter**:OpenAI 网页客户端的新功能。注意上述两项 ChatGPT 高级功能均需付费订阅,是最有竞争力的商业系统。
- **LangChain ReAct+Python**:使用 LangChain 的 Python 智能体;为处理解析错误,设 "handle_parsing_errors=True",并使用默认 zero-shot ReAct 提示。
- **Multi-Agent Debate(Liang et al., 2023)**:我们修改了多智能体辩论的代码来执行评测。默认有三个智能体:正方、反方与主持人。

我们还对 BabyAGI、CAMEL、MetaGPT 等其他几个多智能体系统做了初步评测。结果表明它们都不适合开箱即用地解数学题。例如,让 MetaGPT 解数学题时,它开始开发软件来"解决"问题,但大多数时候并没有真正解题。测试示例见附录 E。

**表 2:自主解题场景下 MATH 数据集两道题的定性评测(每个系统每题测 3 次;报告解题正确性并总结失败原因)**

**(a) 第一题:化简含平方根的分数**

| 系统 | 正确性 | 失败原因 |
| --- | --- | --- |
| AutoGen | 3/3 | 无 |
| AutoGPT | 0/3 | LLM 给出的代码没有 print 函数,结果未被打印 |
| ChatGPT+Plugin | 1/3 | Wolfram Alpha 返回 2 个化简结果(含正确答案),但 GPT-4 总是选错 |
| ChatGPT+Code Interpreter | 2/3 | 返回错误的十进制结果 |
| LangChain ReAct | 0/3 | 三次给出三个不同的错误答案 |
| Multi-Agent Debate | 0/3 | 因计算错误三次给出不同错误答案 |

**(b) 第二题:数论题**

| 系统 | 正确性 | 失败原因 |
| --- | --- | --- |
| AutoGen | 2/3 | 一次代码执行的最终答案错误 |
| AutoGPT | 0/3 | LLM 给出的代码没有 print 函数,结果未被打印 |
| ChatGPT+Plugin | 1/3 | 一次试验中 GPT-4 不断给出错误查询、陷入卡死而被迫停止;另一次直接给出错误答案 |
| ChatGPT+Code Interpreter | 0/3 | 三次给出三个不同的错误答案 |
| LangChain ReAct | 0/3 | 三次给出三个不同的错误答案 |
| Multi-Agent Debate | 0/3 | 三次给出三个不同的错误答案 |

::: en
For the qualitative evaluation, we utilize two level-5 problems from the MATH dataset, testing each problem three times. The first problem involves simplifying a square root fraction, and the second problem involves solving a number theory issue. The correctness counts and reasons for failure are detailed in Table 2. For the quantitative evaluation, we conduct two sets of experiments on the MATH dataset to assess the correctness of these systems: (1) an experiment involving 120 level-5 (the most challenging level) problems, including 20 problems from six categories, excluding geometry, and (2) an experiment on the entire test set, which includes 5000 problems. We exclude AutoGPT from this evaluation as it cannot access results from code executions and does not solve any problems in the qualitative evaluation. Our analysis of the entire dataset reveals that AutoGen achieves an overall accuracy of 69.48%, while GPT-4's accuracy stands at 55.18%. From these evaluations, we have the following observations regarding the problem-solving success rate and user experience of these systems:

• **Problem-solving success rate:** Results from the quantitative evaluations show that AutoGen can help achieve the highest problem-solving success rate among all the compared methods. The qualitative evaluations elucidate common failure reasons across several alternative approaches. ChatGPT+Code Interpreter fails to solve the second problem, and ChatGPT+Plugin struggles to solve both problems. AutoGPT fails on both problems due to code execution issues. The LangChain agent also fails on both problems, producing code that results in incorrect answers in all trials.

• Based on the qualitative evaluation, we analyze the user experience concerning the verbosity of the response and the ability of the LLM-based system to run without unexpected behaviors. ChatGPT+Plugin is the least verbose, mainly because Wolfram queries are much shorter than Python code. AutoGen, ChatGPT+Code Interpreter, and LangChain exhibit similar verbosity, although LangChain is slightly more verbose due to more code execution errors. AutoGPT is the most verbose system owing to predefined steps like THOUGHTS, REASONING, and PLAN, which it includes in replies every time. Overall, AutoGen and ChatGPT+Code Interpreter operate smoothly without exceptions. We note the occurrences of undesired behaviors from other LLM-based systems that could affect user experience: AutoGPT consistently outputs code without the 'print' statement and cannot correct this, requiring the user to run them manually; ChatGPT with Wolfram Alpha plugin has the potential to become stuck in a loop that must be manually stopped; and Langchain ReAct could exit with a parse error, necessitating the passing of a 'handle_parse_error' parameter.
:::

定性评测使用 MATH 数据集的两道 level-5 难题,每题测 3 次:第一题化简含平方根的分数,第二题是数论问题,正确次数与失败原因详见表 2。定量评测在 MATH 数据集上做两组实验来评估各系统的正确性:(1) 120 道 level-5(最难级别)题,含六个类别各 20 题(不含几何);(2) 整个测试集(5000 题)。AutoGPT 被排除在这项评测外,因为它无法获取代码执行结果,且在定性评测中一题未解。对整个数据集的分析显示:AutoGen 总体准确率 **69.48%**,GPT-4 为 **55.18%**。从这些评测中,我们对各系统的解题成功率与用户体验有以下观察:

- **解题成功率**:定量评测结果表明 AutoGen 帮助取得了所有对比方法中最高的解题成功率。定性评测阐明了若干替代方案的常见失败原因:ChatGPT+Code Interpreter 解不出第二题,ChatGPT+Plugin 两题都吃力;AutoGPT 因代码执行问题两题皆败;LangChain 智能体也两题皆败,所有试验中产生的代码都算出错误答案。
- 基于定性评测,我们从"回复冗长度"与"系统能否无异常行为地运行"两方面分析用户体验。ChatGPT+Plugin 最不冗长,主要因为 Wolfram 查询比 Python 代码短得多;AutoGen、ChatGPT+Code Interpreter 与 LangChain 冗长度相近,LangChain 因代码执行错误更多而略冗长;AutoGPT 最冗长,因为每次回复都包含 THOUGHTS、REASONING、PLAN 等预定义步骤。总体上,AutoGen 与 ChatGPT+Code Interpreter 运行顺畅、无异常。我们注意到其他系统的若干影响体验的不良行为:AutoGPT 始终输出没有 'print' 语句的代码且无法改正,需要用户手动运行;带 Wolfram Alpha 插件的 ChatGPT 有陷入必须手动停止的死循环的可能;LangChain ReAct 可能因解析错误退出,必须传 'handle_parse_error' 参数。

[图 6: Examples of three settings utilized to solve math problems using AutoGen: (Gray) Enables a workflow where a student collaborates with an assistant agent to solve problems, either autonomously or in a human-in-the-loop mode. (Gray + Orange) Facilitates a more sophisticated workflow wherein the assistant, on the fly, can engage another user termed "expert", who is in the loop with their own assistant agent, to aid in problem-solving if its own solutions are not satisfactory.]

图 6:用 AutoGen 解数学题的三种设定示例。**(灰色)**:学生(Student)经学生代理(Student Proxy)与助手智能体(Student Assistant)协作解题,可自主运行也可人机回环;**(灰+橙)**:更复杂的工作流——助手在飞行中(on the fly)可以请出另一位用户"专家(Expert)"(该专家在自己的专家代理与专家助手的环中)来协助解题,适用于自己的解不满意时:学生助手调用预定义的 "Ask for expert" 函数,专家收到问题陈述或验证请求,专家与其助手对话后,最终消息回传给学生助手,再继续与学生的对话。

::: en
**Scenario 2: Human-in-the-loop Problem Solving.** For challenging problems that these LLM systems cannot solve autonomously, human feedback during the problem-solving process can be helpful. To incorporate human feedback with AutoGen, one can set human input mode='ALWAYS' in the user proxy agent. We select one challenging problem that none of these systems can solve autonomously across three trials. We adhere to the process outlined below to provide human inputs for all the compared methods:

1. Input the problem: Find the equation of the plane which bisects the angle between the planes 3x−6y+2z+5=0 and 4x−12y+3z−3=0, and which contains the point (−5,−1,−5). Enter your answer in the form Ax+By+Cz+D=0, where A, B, C, D are integers such that A>0 and gcd(|A|,|B|,|C|,|D|)=1.
2. The response from the system does not solve the problem correctly. We then give a hint to the model: Your idea is not correct. Let's solve this together. Suppose P=(x,y,z) is a point that lies on a plane that bisects the angle, the distance from P to the two planes is the same. Please set up this equation first.
3. We expect the system to give the correct distance equation. Since the equation involves an absolute sign that is hard to solve, we would give the next hint: Consider the two cases to remove the abs sign and get two possible solutions.
4. If the system returns the two possible solutions and doesn't continue to the next step, we give the last hint: Use point (−5,−1,−5) to determine which is correct and give the final answer.
5. Final answer is 11x+6y+5z+86=0.
:::

**场景 2:人机回环解题。** 对这些 LLM 系统无法自主解决的难题,解题过程中的人类反馈会有帮助。要向 AutoGen 接入人类反馈,只需在用户代理智能体中设 human_input_mode='ALWAYS'。我们选了一道这些系统三次试验都无法自主解出的难题,并按下述流程为所有对比方法提供人类输入:

1. 输入问题:求平分两平面 3x−6y+2z+5=0 与 4x−12y+3z−3=0 所成角、且过点 (−5,−1,−5) 的平面方程。答案写成 Ax+By+Cz+D=0 的形式,其中 A、B、C、D 为整数,A>0 且 gcd(|A|,|B|,|C|,|D|)=1。
2. 系统的回复未能正确解题。于是给模型提示:你的思路不对,我们一起解。设 P=(x,y,z) 是角平分面上一点,它到两个平面的距离相等。请先列出这个方程。
3. 我们期望系统给出正确的距离方程。由于方程含绝对值、难以求解,继续提示:分两种情况去掉绝对值符号,得到两个可能的解。
4. 若系统返回了两个可能的解却没有继续下一步,给最后一条提示:用点 (−5,−1,−5) 判断哪个正确并给出最终答案。
5. 最终答案为 11x+6y+5z+86=0。

::: en
We observed that AutoGen consistently solved the problem across all three trials. ChatGPT+Code Interpreter and ChatGPT+Plugin managed to solve the problem in two out of three trials, while AutoGPT failed to solve it in all three attempts. In its unsuccessful attempt, ChatGPT+Code Interpreter failed to adhere to human hints. In its failed trial, ChatGPT+Plugin produced an almost correct solution but had a sign discrepancy in the final answer. AutoGPT was unable to yield a correct solution in any of the trials. In one trial, it derived an incorrect distance equation. In the other two trials, the final answer was incorrect due to code execution errors.
:::

我们观察到:AutoGen 三次试验都稳定解出该题;ChatGPT+Code Interpreter 与 ChatGPT+Plugin 三次中解出两次;AutoGPT 三次全部失败。ChatGPT+Code Interpreter 失败的那次没有遵循人类提示;ChatGPT+Plugin 失败的那次给出几乎正确的解,但最终答案差一个正负号;AutoGPT 没有一次得到正确解——一次推出了错误的距离方程,另外两次因代码执行错误导致最终答案错误。

::: en
**Scenario 3: Multi-User Problem Solving.** Next-generation LLM applications may necessitate the involvement of multiple real users for collectively solving a problem with the assistance of LLMs. We showcase how AutoGen can be leveraged to effortlessly construct such a system. Specifically, building upon scenario 2 mentioned above, we aim to devise a simple system involving two human users: a student and an expert. In this setup, the student interacts with an LLM assistant to address some problems, and the LLM automatically resorts to the expert when necessary.

The overall workflow is as follows: The student chats with the LLM-based assistant agent through a student proxy agent to solve problems. When the assistant cannot solve the problem satisfactorily, or the solution does not match the expectation of the student, it would automatically hold the conversation and call the pre-defined ask-for-expert function via the function call feature of GPT in order to resort to the expert. Specifically, it would automatically produce the initial message for the ask-for-expert function, which could be the statement of the problem or the request to verify the solution to a problem, and the expert is supposed to respond to this message with the help of the expert assistant. After the conversation between the expert and the expert's assistant, the final message would be sent back to the student assistant as the response to the initial message. Then, the student assistant would resume the conversation with the student using the response from the expert for a better solution. A detailed visualization is shown in Figure 6.

With AutoGen, constructing the student/expert proxy agent and the assistant agents is straightforward by reusing the built-in UserProxyAgent and AssistantAgent through appropriate configurations. The only development required involves writing several lines of code for the ask-for-expert function, which then becomes part of the configuration for the assistant. Additionally, it's easy to extend such a system to include more than one expert, with a specific ask-for-expert function for each, or to include multiple student users with a shared expert for consultation.
:::

**场景 3:多用户解题。** 下一代 LLM 应用可能需要多个真实用户在 LLM 辅助下共同解决一个问题。我们展示 AutoGen 如何被轻松用来构建这样的系统。具体地,在场景 2 基础上,我们设计一个涉及两个人类用户——学生与专家——的简单系统:学生与 LLM 助手交互解题,LLM 在必要时自动求助专家。

整体工作流如下:学生经学生代理与 LLM 助手智能体对话解题。当助手不能令人满意地解出问题、或解不符合学生期望时,它会自动挂起当前对话,通过 GPT 的函数调用特性调用预定义的 ask-for-expert(求助专家)函数来求助于专家。具体而言,它会自动为 ask-for-expert 函数生成初始消息(可以是问题陈述,或验证某问题解法的请求),专家应在专家助手的帮助下回复该消息。专家与其助手的对话结束后,最终消息会作为对初始消息的回复发回给学生助手;学生助手随后利用专家的回复继续与学生的对话,得到更好的解。详细可视化见图 6。

用 AutoGen,通过适当配置复用内置的 UserProxyAgent 与 AssistantAgent,构造学生/专家代理与助手智能体都很直接。唯一需要的开发就是为 ask-for-expert 函数写几行代码,之后它就成为助手配置的一部分。此外,把该系统扩展到多位专家(每位各有一个 ask-for-expert 函数)、或多个学生用户共享一位咨询专家,都很容易。

#### A2:检索增强的代码生成与问答(附录 D)

[图 7: Overview of Retrieval-augmented Chat which involves two agents, including a Retrieval-augmented User Proxy and a Retrieval-augmented Assistant. Given a set of documents, the Retrieval-augmented User Proxy first automatically processes documents—splits, chunks, and stores them in a vector database. Then for a given user input, it retrieves relevant chunks as context and sends it to the Retrieval-augmented Assistant, which uses LLM to generate code or text to answer questions. Agents converse until they find a satisfactory answer.]

图 7:检索增强聊天总览,含两个智能体:检索增强用户代理与检索增强助手。给定一组文档,检索增强用户代理先自动处理文档——切分、分块、存入向量数据库;然后针对给定用户输入,检索相关块作为上下文发给检索增强助手,后者用 LLM 生成代码或文本来回答问题。智能体持续对话直到找到满意的答案。图中流程为:① 问题与上下文;② 满意的答案或 "Update Context";③ 终止、反馈或 "Update Context";④ 满意的答案或终止。

::: en
**Detailed Workflow.** The workflow of Retrieval-Augmented Chat is illustrated in Figure 7. To use Retrieval-augmented Chat, one needs to initialize two agents including Retrieval-augmented User Proxy and Retrieval-augmented Assistant. Initializing the Retrieval-Augmented User Proxy necessitates specifying a path to the document collection. Subsequently, the Retrieval-Augmented User Proxy can download the documents, segment them into chunks of a specific size, compute embeddings, and store them in a vector database. Once a chat is initiated, the agents collaboratively engage in code generation or question-answering adhering to the procedures outlined below:

1. The Retrieval-Augmented User Proxy retrieves document chunks based on the embedding similarity, and sends them along with the question to the Retrieval-Augmented Assistant.
2. The Retrieval-Augmented Assistant employs an LLM to generate code or text as answers based on the question and context provided. If the LLM is unable to produce a satisfactory response, it is instructed to reply with "Update Context" to the Retrieval-Augmented User Proxy.
3. If a response includes code blocks, the Retrieval-Augmented User Proxy executes the code and sends the output as feedback. If there are no code blocks or instructions to update the context, it terminates the conversation. Otherwise, it updates the context and forwards the question along with the new context to the Retrieval-Augmented Assistant. Note that if human input solicitation is enabled, individuals can proactively send any feedback, including "Update Context", to the Retrieval-Augmented Assistant.
4. If the Retrieval-Augmented Assistant receives "Update Context", it requests the next most similar chunks of documents as new context from the Retrieval-Augmented User Proxy. Otherwise, it generates new code or text based on the feedback and chat history. If the LLM fails to generate an answer, it replies with "Update Context" again. This process can be repeated several times. The conversation terminates if no more documents are available for the context.
:::

**详细工作流。** 检索增强聊天的工作流如图 7 所示。使用时需初始化两个智能体:检索增强用户代理与检索增强助手。初始化检索增强用户代理需要指定文档集路径;随后它可以下载文档、按特定大小切块、计算嵌入并存入向量数据库。聊天发起后,两个智能体按以下流程协作进行代码生成或问答:

1. 检索增强用户代理基于嵌入相似度检索文档块,连同问题一起发给检索增强助手。
2. 检索增强助手用 LLM 基于所给问题与上下文生成代码或文本作为答案。若 LLM 无法给出令人满意的回复,它被指示向检索增强用户代理回复 "Update Context"。
3. 若回复包含代码块,检索增强用户代理执行代码并把输出作为反馈发回;若既无代码块也无更新上下文的指令,则终止对话;否则更新上下文,把问题连同新上下文再转发给检索增强助手。注意:若启用了人类输入征求,人可以主动发送任何反馈(包括 "Update Context")给检索增强助手。
4. 若检索增强助手收到 "Update Context",它向检索增强用户代理请求相似度次高的文档块作为新上下文;否则基于反馈与聊天历史生成新的代码或文本;若 LLM 仍给不出答案,就再次回复 "Update Context"。该过程可重复多次;当没有更多文档可用作上下文时,对话终止。

::: en
We utilize Retrieval-Augmented Chat in two scenarios. The first scenario aids in generating code based on a given codebase. While LLMs possess strong coding abilities, they are unable to utilize packages or APIs that are not included in their training data, e.g., private codebases, or have trouble using trained ones that are frequently updated post-training. Hence, Retrieval-Augmented Code Generation is considered to be highly valuable. The second scenario involves question-answering on the Natural Questions dataset (Kwiatkowski et al., 2019), enabling us to obtain comparative evaluation metrics for the performance of our system.
:::

我们在两个场景中使用检索增强聊天。第一个场景辅助基于给定代码库生成代码:LLM 虽编码能力强,却无法使用训练数据中未包含的包或 API(如私有代码库),对训练后频繁更新的已学包也可能用不好,因此检索增强代码生成被认为很有价值。第二个场景是在 Natural Questions 数据集(Kwiatkowski et al., 2019)上问答,使我们可以获得系统性能的对比评测指标。

::: en
**Scenario 1: Evaluation on Natural Questions QA dataset.** In this case, we evaluate the Retrieval-Augmented Chat's end-to-end question-answering performance using the Natural Questions dataset (Kwiatkowski et al., 2019). We collected 5,332 non-redundant context documents and 6,775 queries from HuggingFace. First, we create a document collection based on the entire context corpus and store it in the vector database. Then, we utilize Retrieval-Augmented Chat to answer the questions. An example (Figure 8) from the NQ dataset showcases the advantages of the interactive retrieval feature: "who carried the usa flag in opening ceremony". When attempting to answer this question, the context with the highest similarity to the question embedding does not contain the required information for a response. As a result, the LLM assistant (GPT-3.5-turbo) replies "Sorry, I cannot find any information about who carried the USA flag in the opening ceremony. UPDATE CONTEXT." With the unique and innovative ability to update context in Retrieval-Augmented Chat, the user proxy agent automatically updates the context and forwards it to the assistant agent again. Following this process, the agent is able to generate the correct answer to the question.
:::

**场景 1:Natural Questions 问答数据集上的评测。** 此案例用 Natural Questions 数据集(Kwiatkowski et al., 2019)评测检索增强聊天的端到端问答性能。我们从 HuggingFace 收集了 5,332 篇非冗余上下文文档与 6,775 条查询;先基于整个上下文库建文档集并存入向量数据库,再用检索增强聊天答题。NQ 数据集的一个例子(图 8)展示了交互式检索的优势:"who carried the usa flag in opening ceremony"(开幕式上谁举着美国国旗)。尝试回答时,与问题嵌入相似度最高的上下文并不包含所需信息,于是 LLM 助手(GPT-3.5-turbo)回复 "Sorry, I cannot find any information about who carried the USA flag in the opening ceremony. UPDATE CONTEXT."。凭借检索增强聊天独特创新的上下文更新能力,用户代理智能体自动更新上下文并再次转发给助手智能体;经过这一过程,智能体成功生成了正确答案。

[图 8: Retrieval-augmented Chat without (W/O) and with (W/) interactive retrieval.]

图 8:无交互式检索(W/O)与有交互式检索(W/)的检索增强聊天对比。**(a) 无交互式检索**:系统消息指示助手"若凭当前上下文(无论有无)都无法回答,请准确回复 'sorry, I don't know'"——助手在无关上下文(1899 年的棒球新闻段落)下只能回答 "Sorry, I don't know"。**(b) 有交互式检索**:系统消息指示"若无法回答请准确回复 'UPDATE CONTEXT'"——第一轮助手回复 "...UPDATE CONTEXT",用户代理自动检索新上下文(含 "Erin Hamlin" 的表格段落),第二轮助手即正确答出 "Erin Hamlin carried the USA flag in the opening ceremony."。

::: en
In addition, we conduct an experiment using the same prompt as illustrated in (Adlakha et al., 2023) to investigate the advantages of AutoGen W/O interactive retrieval. The F1 score and Recall for the first 500 questions are 23.40% and 62.60%, respectively, aligning closely with the results reported in Figure 4b. Consequently, we assert that AutoGen W/O interactive retrieval outperforms DPR due to differences in the retrievers employed. Specifically, we utilize a straightforward vector search retriever with the all-MiniLM-L6-v2 model for embeddings.

Furthermore, we analyze the number of LLM calls in experiments involving both AutoGen and AutoGen W/O interactive retrieval, revealing that approximately 19.4% of questions in the Natural Questions dataset trigger an "Update Context" operation, resulting in additional LLM calls.
:::

此外,我们用与(Adlakha et al., 2023)相同的提示做了一个实验,考察"无交互式检索的 AutoGen"的表现:前 500 个问题的 F1 与 Recall 分别为 23.40% 与 62.60%,与图 4b 报告的结果高度一致。因此我们断言,无交互式检索的 AutoGen 优于 DPR 应归因于所用检索器的差异——具体来说,我们用的是以 all-MiniLM-L6-v2 模型做嵌入的朴素向量检索器。

进一步,我们分析了 AutoGen 与无交互式检索版 AutoGen 实验中的 LLM 调用次数,发现 Natural Questions 数据集中约 **19.4%** 的问题触发了 "Update Context" 操作,产生了额外的 LLM 调用。

::: en
**Scenario 2: Code Generation Leveraging Latest APIs from the Codebase.** In this case, the question is "How can I use FLAML to perform a classification task and use Spark for parallel training? Train for 30 seconds and force cancel jobs if the time limit is reached.". FLAML (v1) (Wang et al., 2021) is an open-source Python library designed for efficient AutoML and tuning. It was open-sourced in December 2020, and is included in the training data of GPT-4. However, the question necessitates the use of Spark-related APIs, which were added in December 2022 and are not encompassed in the GPT-4 training data. Consequently, the original GPT-4 model is unable to generate the correct code, due to its lack of knowledge regarding Spark-related APIs. Instead, it erroneously creates a non-existent parameter, spark, and sets it to 'True'. Nevertheless, with Retrieval-Augmented Chat, we provide the latest reference documents as context. Then, GPT-4 generates the correct code blocks by setting use_spark and force_cancel to 'True'.
:::

**场景 2:利用代码库最新 API 的代码生成。** 此案例的问题是:"如何用 FLAML 做分类任务并用 Spark 并行训练?训练 30 秒,到达时限就强制取消作业。"FLAML (v1)(Wang et al., 2021)是一个面向高效 AutoML 与调参的开源 Python 库,2020 年 12 月开源,已包含在 GPT-4 训练数据中。但该问题需要使用 Spark 相关 API——它们是 2022 年 12 月才加入的,不在 GPT-4 训练数据里。因此原生 GPT-4 因不了解 Spark 相关 API 而无法生成正确代码:它错误地编造了一个不存在的参数 spark 并设为 'True'。而借助检索增强聊天,我们提供最新参考文档作为上下文,GPT-4 随即生成了正确的代码块——正确地把 use_spark 与 force_cancel 设为 'True'。

#### A3:文本世界环境中的决策(附录 D)

[图 9: We use AutoGen to solve tasks in the ALFWorld benchmark, which contains household tasks described in natural language. We propose two designs: a two-agent design where the assistant agent suggests the next step, and the Executor executes actions and provides feedback. The three-agent design adds a grounding agent that supplies commonsense facts to the executor when needed.]

图 9:我们用 AutoGen 求解 ALFWorld 基准中用自然语言描述的家务任务,提出两种设计:**两智能体设计(ALFChat,两智能体)**——助手智能体建议下一步,执行器(Executor)执行动作并反馈环境观察(如"在书桌 2 上,你看到闹钟 3、碗 3、信用卡 2、马克杯 1、铅笔 2"),助手据此做动作决策(如"从书桌 2 拿起铅笔 2"),执行器再返回奖励与状态;**三智能体设计(ALFChat,三智能体)**——在助手与执行器之外增加一个锚定智能体(GroundingAgent),在需要时向执行器提供常识事实。

::: en
ALFWorld (Shridhar et al., 2021) is a synthetic language-based interactive decision-making task. It comprises textual environments that aim to simulate real-world household scenes. Given a high-level goal (e.g., putting a hot apple in the fridge) and the description of the household environment, the agent needs to explore and interact with the simulated household environment through a textual interface. A typical task environment contains various types of locations and could require more than 40 steps to finish, which highlights the need for agents to decompose the goal into subtasks and tackle them one by one, while effectively exploring the environments.

**Detailed Workflow.** We first propose a straightforward two-agent system with AutoGen, illustrated on the left-hand side of Figure 9, to tackle tasks from this benchmark. The system consists of an assistant agent and an executor agent. The assistant agent generates plans and makes action decisions to solve the tasks. The executor agent is tailored specifically for ALFWorld. It performs actions proposed by the assistant and reports action execution results in the household environment as feedback to the assistant. Due to the strict format requirements for the output format, we use the BLEU metric to evaluate the similarity of the output to all valid action options. The option with the highest similarity will be chosen as the action for this round.

One major challenge encompassed in ALFWorld is commonsense reasoning. The agent needs to extract patterns from the few-shot examples provided and combine them with the agent's general knowledge of household environments to fully understand task rules. More often than not, the assistant tends to neglect some basic knowledge of the household environment. Thanks to the easy-to-implement multi-agent conversational feature of AutoGen, enhancing the assistant agent's reasoning ability by adding a new grounding agent to provide commonsense facts for the decision-making agent's reference becomes straightforward. By scrutinizing the failed attempts and summarizing the reasons for failure, we obtained a holistic understanding of the commonsense knowledge that the assistant agent lacks. Then, we set a grounding agent to provide this general knowledge when the task begins and whenever the assistant outputs the same action three times in a row. This ensures the assistant takes this commonsense knowledge into consideration and prevents it from getting stuck in outputting the same content or constantly apologizing.

We compare our system's performance with ReAct, which treats ALFWorld as a text-completion task. ReAct (Yao et al., 2022) is a few-shot prompting technique that interleaves reasoning and acting, allowing for greater synergy between the two and significantly improving performance on both language and decision-making tasks. We integrate ReAct into AutoGen by modifying the prompts in a conversational manner. Following ReAct, we employ a two-shot setting. The few-shot prompts are obtained from the corresponding repository. As shown in Table 3, the two-agent design matches the performance of ReAct, while the three-agent design significantly outperforms ReAct. We surmise that the performance discrepancy is caused by the inherent difference between dialogue-completion and text-completion tasks. On the other hand, introducing a grounding agent as a knowledge source remarkably advances performance on all types of tasks.
:::

ALFWorld(Shridhar et al., 2021)是一个基于合成语言的交互式决策任务,由旨在模拟真实家居场景的文本环境组成。给定一个高层目标(如"把一个热苹果放进冰箱")与家居环境描述,智能体需要通过文本界面探索并交互于模拟家居环境。一个典型任务环境包含多种位置类型,可能需要 40 步以上才能完成——这凸显了智能体把目标分解为子任务、逐一解决并有效探索环境的需求。

**详细工作流。** 我们先用 AutoGen 提出一个简洁的双智能体系统(图 9 左侧)来求解该基准任务。系统由助手智能体与执行器智能体组成:助手智能体生成计划并做动作决策;执行器智能体专为 ALFWorld 定制,执行助手提议的动作,并把家居环境中的执行结果作为反馈报告给助手。由于对输出格式有严格要求,我们用 BLEU 指标评估输出与所有合法动作选项的相似度,选相似度最高的选项作为本轮动作。

ALFWorld 的一大挑战是常识推理:智能体需要从提供的少样本示例中提取模式,并结合对家居环境的一般知识来完整理解任务规则;而助手往往忽略家居环境的一些基本知识。得益于 AutoGen 易于实现的多智能体对话特性,增加一个新的锚定智能体来为决策智能体提供常识参考、从而增强助手推理能力,变得很直接。通过仔细检视失败尝试并总结失败原因,我们全面掌握了助手智能体所缺的常识知识;然后设置一个锚定智能体,在任务开始时、以及每当助手连续三次输出同一动作时提供这些通用知识。这确保助手把常识纳入考虑,防止它卡在重复输出同样内容或不停道歉上。

我们把该系统与把 ALFWorld 当作文本补全任务的 ReAct 比较。ReAct(Yao et al., 2022)是一种交错推理与行动的少样本提示技术,让两者更好地协同,在语言与决策任务上都显著提升性能。我们以对话方式修改提示,把 ReAct 集成进 AutoGen,并沿用 ReAct 的 two-shot 设定,少样本提示取自相应仓库。如表 3 所示:两智能体设计与 ReAct 性能相当,而三智能体设计显著超越 ReAct。我们推测性能差异源于对话补全与文本补全任务的固有差别;另一方面,引入作为知识源的锚定智能体,在所有类型任务上都显著推进了性能。

**表 3:ReAct 与 ALFChat 两个变体在 ALFWorld 基准上的对比**(每任务报告 3 次尝试的成功率;成功率 = 成功完成的任务数 ÷ 总任务数)

| 方法 | Pick | Clean | Heat | Cool | Look | Pick 2 | 全部(All) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ReAct(平均) | 63 | 52 | 48 | 71 | 61 | 24 | 54 |
| ALFChat 两智能体(平均) | 61 | 58 | 57 | 67 | 50 | 19 | 54 |
| ALFChat 三智能体(平均) | **79** | **64** | **70** | **76** | **78** | **41** | **69** |
| ReAct(3 次中最佳) | 75 | 62 | 61 | 81 | 78 | 35 | 66 |
| ALFChat 两智能体(3 次中最佳) | 71 | 61 | 65 | 76 | 67 | 35 | 63 |
| ALFChat 三智能体(3 次中最佳) | **92** | **74** | **78** | **86** | **83** | **41** | **77** |

::: en
**Case study.** Figure 10 exemplifies how a three-agent design eliminates one root cause for failure cases. Most of the tasks involve taking an object and then performing a specific action with it (e.g., finding a vase and placing it on a cupboard). Without a grounding agent, the assistant frequently conflates finding an object with taking it, as illustrated in Figure 10a). This leads to most of the failure cases in 'pick' and 'look' type tasks. With the introduction of a grounding agent, the assistant can break out of this loop and successfully complete the task

**Takeaways.** We introduced a grounding agent to serve as an external commonsense knowledge source, which significantly enhanced the assistant's ability to make informed decisions. This proves that providing necessary commonsense facts to the decision-making agent can assist it in making more informed decisions, thus effectively boosting the task success rate. AutoGen brings both simplicity and modularity when adding the grounding agent.
:::

**案例研究。** 图 10 例示了三智能体设计如何消除失败案例的一个根因。多数任务涉及先拿起物体、再对其执行特定动作(如找到花瓶并放上橱柜)。没有锚定智能体时,助手经常把"找到物体"与"拿起物体"混为一谈(如图 10a),这导致 'pick' 与 'look' 类任务的大部分失败;引入锚定智能体后,助手能跳出循环并成功完成任务。

[图 10: Comparison of results from two designs: (a) Two-agent design which consists of an assistant and an executor, (b) Three-agent design which adds a grounding agent that serves as a knowledge source. For simplicity, we omit the in-context examples and part of the exploration trajectory, and only show parts contributing to the failure/success of the attempt.]

图 10:两种设计的结果对比(为简洁起见,省略了上下文示例与部分探索轨迹,只展示导致该次失败/成功的部分)。任务为"在台灯下看碗"。**(a) 两智能体**:助手想看碗,却只走到台灯前反复"打开台灯"(use desklamp 1)——执行器反复回应"You turn on the desklamp 1",助手陷入开灯死循环,任务失败,只能回复 TERMINATE。**(b) 三智能体**:助手同样陷入开灯循环时,锚定智能体(GroundingAgent)注入常识:"你必须先找到并拿起物体,才能检查它;你必须先到目标物体所在处,才能使用它。"执行器把提示转告助手后,助手改变计划:走到书桌 2 → 拿起碗 1(take bowl 1 from desk 2)→ 走到书桌 1 → 打开台灯 → 在台灯下看碗,任务成功。

**要点(Takeaways)。** 我们引入充当外部常识知识源的锚定智能体,显著增强了助手做出知情决策的能力。这证明:向决策智能体提供必要的常识事实,能帮助它做出更明智的决策,从而有效提升任务成功率。在增加锚定智能体这件事上,AutoGen 同时带来了简洁性与模块化。

#### A4:多智能体编码(附录 D)

[图 11: Our re-implementation of OptiGuide with AutoGen streamlining agents' interactions. The Commander receives user questions (e.g., What if we prohibit shipping from supplier 1 to roastery 2?) and coordinates with the Writer and Safeguard. The Writer crafts the code and interpretation, the Safeguard ensures safety (e.g., not leaking information, no malicious code), and the Commander executes the code. If issues arise, the process can repeat until resolved. Shaded circles represent steps that may be repeated multiple times.]

图 11:我们用 AutoGen 对 OptiGuide 的重新实现,精简了智能体交互。Commander 接收用户问题(如"如果禁止从供应商 1 向烘焙厂 2 运货会怎样?"),并与 Writer、Safeguard 协调:Writer 编写代码与解释;Safeguard 确保安全(如不泄露信息、无恶意代码);Commander 执行代码。若出现问题,流程可重复直至解决。带阴影的圆圈表示可能重复多次的步骤。流程编号:① 用户提问 → ② 问题与日志给 Writer → ③ 代码回传 → ④ 送 Safeguard 审查 → ⑤ 通过放行(或亮红旗)→ ⑥ 执行代码/异常回炉 → ⑦ 答案解释 → ⑧ 最终答案给用户;"③→⑥ 重复直到回答用户问题或超时"。

::: en
**Detailed Workflow.** The workflow can be described as follows. The end user initiates the interaction by posing a question, such as "What if we prohibit shipping from supplier 1 to roastery 2?", marked by ① to the Commander agent. The Commander manages and coordinates with two LLM-based assistant agents: the Writer and the Safeguard. Apart from directing the flow of communication, the Commander has the responsibility of handling memory tied to user interactions. This capability enables the Commander to capture and retain valuable context regarding the user's questions and their corresponding responses. Such memory is subsequently shared across the system, empowering the other agents with context from prior user interactions and ensuring more informed and relevant responses.

In this orchestrated process, the Writer, who combines the functions of a "Coder" and an "Interpreter" as defined in (Li et al., 2023a), will craft code and also interpret execution output logs. For instance, during code writing (② and ③), the Writer may craft code "model.addConstr(x['supplier1', 'roastery2'] == 0, 'prohibit')" to add an additional constraint to answer the user's question. After receiving the code, the Commander will communicate with the Safeguard to screen the code and ascertain its safety (④); once the code obtains the Safeguard's clearance, marked by ⑤, the Commander will use external tools (e.g., Python) to execute the code and request the Writer to interpret the execution results for the user's question (⑥ and ⑦). For instance, the writer may say "if we prohibit shipping from supplier 1 to roastery 2, the total cost would increase by 10.5%." Bringing this intricate process full circle, the Commander furnishes the user with the concluding answer (⑧).

If at a point there is an exception - either a security red flag raised by Safeguard (in ⑤) or code execution failures within Commander, the Commander redirects the issue back to the Writer with essential information in logs (⑥). So, the process from ③ to ⑥ might be repeated multiple times, until each user query receives a thorough and satisfactory resolution or until the timeout. This entire complex workflow of multi-agent interaction is elegantly managed via AutoGen.

The core workflow code for OptiGuide was reduced from over 430 lines to 100 lines using AutoGen, leading to significant productivity improvement. The new agents are customizable, conversable, and can autonomously manage their chat memories. This consolidation allows the coder and interpreter roles to merge into a single "Writer" agent, resulting in a clean, concise, and intuitive implementation that is easier to maintain.
:::

**详细工作流。** 流程如下:终端用户以问题(如"如果禁止从供应商 1 向烘焙厂 2 运货会怎样?")发起交互,记为 ①,送达 Commander 智能体。Commander 管理并协调两个 LLM 助手智能体:Writer 与 Safeguard。除引导通信流外,Commander 还负责管理与用户交互相关的记忆——这使它能捕捉并保留关于用户问题及其回应的宝贵上下文;该记忆随后在系统内共享,让其他智能体也拥有此前用户交互的上下文,确保更知情、更相关的回应。

在这一编排过程中,Writer(合并了 Li et al., 2023a 定义的"Coder(编码者)"与"Interpreter(解释者)"职能)负责编写代码并解释执行输出日志。例如在写代码阶段(② 与 ③),Writer 可能编写代码 "model.addConstr(x['supplier1', 'roastery2'] == 0, 'prohibit')" 来添加额外约束以回答用户问题。Commander 收到代码后,与 Safeguard 沟通审查代码、确认其安全性(④);一旦代码获得 Safeguard 放行(⑤),Commander 将使用外部工具(如 Python)执行代码,并请 Writer 就执行结果为用户问题作解释(⑥ 与 ⑦)——例如 Writer 可能说"如果禁止从供应商 1 向烘焙厂 2 运货,总成本将上升 10.5%"。最后,Commander 把结论性答案交付给用户(⑧),使这一复杂过程闭环。

若某处出现异常——要么是 Safeguard 亮起安全红旗(⑤),要么是 Commander 内代码执行失败——Commander 会带着日志中的关键信息把问题退回 Writer(⑥)。因此 ③ 到 ⑥ 的过程可能重复多次,直到每个用户查询得到彻底满意的解决或超时。这整个复杂的多智能体交互工作流由 AutoGen 优雅地管理。

用 AutoGen,OptiGuide 的核心工作流代码从 430 多行减至 100 行,带来显著生产力提升。新智能体可定制、可对话,并能自主管理自己的聊天记忆。这种整合让编码者与解释者两个角色合并为单一 "Writer" 智能体,实现干净、简洁、直观、更易维护的实现。

::: en
**Manual Evaluation Comparing ChatGPT + Code Interpreter and AutoGen-based OptiGuide.** ChatGPT + Code Interpreter is unable to execute code with private or customized dependencies (e.g., Gurobi), which means users need to have engineering expertise to manually handle multiple steps, disrupting the workflow and increasing the chance for mistakes. If users lack access or expertise, the burden falls on supporting engineers, increasing their on-call time.

We carried out a user study that juxtaposed OpenAI's ChatGPT coupled with a Code Interpreter against AutoGen-based OptiGuide. The study focused on a coffee supply chain scenario, and an expert Python programmer with proficiency in Gurobi participated in the test. We evaluated both systems based on 10 randomly selected questions, measuring time and accuracy. While both systems answered 8 questions correctly, the Code Interpreter was significantly slower than OptiGuide because the former requires more manual intervention. On average, users needed to spend 4 minutes and 35 seconds to solve problems with the Code Interpreter, with a standard deviation of approximately 2.5 minutes. In contrast, OptiGuide's average problem-solving time was around 1.5 minutes, most of which was spent waiting for responses from the GPT-4 model. This indicates a 3x saving on the user's time with AutoGen-based OptiGuide.

While using ChatGPT + Code Interpreter, users had to read through the code and instructions to know where to paste the code snippets. Additionally, running the code involves downloading it and executing it in a terminal, a process that was both time-consuming and prone to errors. The response time from the Code Interpreter is also slower, as it generates lots of tokens to read the code, read the variables line-by-line, perform chains of thought analysis, and then produce the final answer code. In contrast, AutoGen integrates multiple agents to reduce user interactions by 3 - 5 times on average as reported in Table 4, where we evaluated our system with 2000 questions across five OptiGuide applications and measured how many prompts the user needs to type.
:::

**ChatGPT + Code Interpreter 与基于 AutoGen 的 OptiGuide 的人工评测对比。** ChatGPT + Code Interpreter 无法执行带私有或定制依赖(如 Gurobi)的代码,这意味着用户需要具备工程专业知识来手工处理多个步骤,打断工作流并增加出错机会;若用户没有权限或专长,负担就落在支持工程师身上,增加他们的值班时间。

我们做了一项把 ChatGPT+Code Interpreter 与基于 AutoGen 的 OptiGuide 并置对比的用户研究:聚焦咖啡供应链场景,由一位精通 Gurobi 的 Python 专家程序员参与测试;基于 10 个随机选取的问题评测两个系统,测量时间与准确性。两个系统都答对了 8 题,但 Code Interpreter 明显慢于 OptiGuide,因为前者需要更多人工干预:用户用 Code Interpreter 平均需 4 分 35 秒解题(标准差约 2.5 分钟),而 OptiGuide 平均解题时间约 1.5 分钟,其中大部分是在等 GPT-4 模型响应——这表明基于 AutoGen 的 OptiGuide 为用户节省约 3 倍时间。

使用 ChatGPT + Code Interpreter 时,用户必须通读代码与说明才知道把代码片段粘贴到哪里;而且运行代码还需下载并在终端执行,既耗时又易错。Code Interpreter 的响应也更慢:它要生成大量 token 来读代码、逐行读变量、做思维链分析,然后才产出最终答案代码。相比之下,AutoGen 集成多个智能体,平均减少 3-5 倍用户交互(见表 4)——我们在五个 OptiGuide 应用的 2000 个问题上评测了系统,测量用户需要输入多少条提示。

**表 4:OptiGuide(使用 GPT-4)在保持同等编码性能下节省的人工**(数据含均值与标准差(括号内))

| 数据集 | netflow | facility | tsp | coffee | diet |
| --- | --- | --- | --- | --- | --- |
| 节省倍数 | 3.14x (0.65) | 3.14x (0.64) | 4.88x (1.71) | 3.38x (0.86) | 3.03x (0.31) |

::: en
Table 13 and 15 provide a detailed comparison of user experience with ChatGPT+Code Interpreter and AutoGen-based OptiGuide. ChatGPT+Code Interpreter is unable to run code with private packages or customized dependencies (such as Gurobi); as a consequence, ChatGPT+Code Interpreter requires users to have engineering expertise and to manually handle multiple steps, disrupting the workflow and increasing the chance of mistakes. If customers lack access or expertise, the burden falls on supporting engineers, increasing their on-call time. In contrast, the automated chat by AutoGen is more streamlined and autonomous, integrating multiple agents to solve problems and address concerns. This results in a 5x reduction in interaction and fundamentally changes the overall usability of the system. A stable workflow can be potentially reused for other applications or to compose a larger one.

**Takeaways:** The implementation of the multi-agent design with AutoGen in the OptiGuide application offers several advantages. It simplifies the Python implementation and fosters a mixture of collaborative and adversarial problem-solving environments, with the Commander and Writer working together while the Safeguard acts as a virtual adversarial checker. This setup allows for proper memory management, as the Commander maintains memory related to user interactions, providing context-aware decision-making. Additionally, role-playing ensures that each agent's memory remains isolated, preventing shortcuts and hallucinations
:::

表 13 与表 15 给出了 ChatGPT+Code Interpreter 与基于 AutoGen 的 OptiGuide 的用户体验详细对比。ChatGPT+Code Interpreter 无法运行带私有包或定制依赖(如 Gurobi)的代码;因此它要求用户具备工程专业知识并手工处理多个步骤,打断工作流、增加出错机会;若客户缺乏权限或专长,负担就落在支持工程师身上,增加其值班时间。相比之下,AutoGen 的自动聊天更精简、更自主,集成多个智能体来解决问题、处理关切,带来 5 倍的交互减少,从根本上改变了系统的整体可用性。稳定的工作流还有望复用于其他应用或组合成更大的工作流。

**要点(Takeaways):** 在 OptiGuide 应用中用 AutoGen 实现多智能体设计有若干优势:它简化了 Python 实现,并促成协作与对抗并存的问题求解环境——Commander 与 Writer 协同工作,而 Safeguard 充当虚拟的对抗性审查者。这一设定支持妥善的记忆管理:Commander 维护与用户交互相关的记忆,提供上下文感知的决策。此外,角色扮演确保各智能体的记忆相互隔离,防止走捷径与幻觉。

#### A5:动态群聊(附录 D)

[图 12: A5: Dynamic Group Chat: Overview of how AutoGen enables dynamic group chats to solve tasks. The Manager agent, which is an instance of the GroupChatManager class, performs the following three steps–select a single speaker (in this case Bob), ask the speaker to respond, and broadcast the selected speaker's message to all other agents.]

图 12:A5 动态群聊:AutoGen 如何实现动态群聊解题的总览。Manager 智能体(GroupChatManager 类的实例)执行三步:① 选择一个发言者(本例中是 Bob);② 请该发言者回应;③ 把所选发言者的消息广播给所有其他智能体(图中含 Alice、Bob、User Proxy)。

::: en
To validate the necessity of multi-agent dynamic group chat and the effectiveness of the role-play speaker selection policy, we conducted a pilot study comparing a four-agent dynamic group chat system with two possible alternatives across 12 manually crafted complex tasks. An example task is "How much money would I earn if I bought 200 $AAPL stocks at the lowest price in the last 30 days and sold them at the highest price? Save the results into a file." The four-agent group chat system comprised the following group members: a user proxy to take human inputs, an engineer to write code and fix bugs, a critic to review code and provide feedback, and a code executor for executing code. One of the possible alternatives is a two-agent system involving an LLM-based assistant and a user proxy agent, and another alternative is a group chat system with the same group members but a task-based speaker selection policy. In the task-based speaker selection policy, we simply append role information, chat history, and the next speaker's task into a single prompt. Through the pilot study, we observed that compared with a task-style prompt, utilizing a role-play prompt in dynamic speaker selection often leads to more effective consideration of both conversation context and role alignment during the process of generating the subsequent speaker, and consequently a higher success rate as reported in Table 5, fewer LLM calls and fewer termination failures, as reported in Table 6.
:::

为验证多智能体动态群聊的必要性以及角色扮演式发言者选择策略的有效性,我们做了一项试点研究:在 12 个手工构造的复杂任务上,把四智能体动态群聊系统与两个备选方案对比。示例任务:"如果我以最近 30 天最低价买入 200 股 $AAPL、以最高价卖出,能赚多少钱?把结果存入文件。"四智能体群聊系统的成员是:接收人类输入的用户代理、写代码修 bug 的工程师(engineer)、审查代码并提反馈的批评者(critic)、执行代码的代码执行器。备选方案一是一个双智能体系统(LLM 助手 + 用户代理);备选方案二是成员相同、但采用**基于任务的发言者选择策略**的群聊系统——该策略只是把角色信息、聊天历史与下一个发言者的任务拼进单个提示。试点研究观察到:与任务式提示相比,在动态发言者选择中使用角色扮演提示,往往能在生成下一个发言者的过程中更有效地兼顾对话上下文与角色对齐,从而带来更高的成功率(表 5)、更少的 LLM 调用与更少的终止失败(表 6)。

**表 5:12 个任务上的成功数(越高越好)**

| 模型 | 双智能体 | 群聊 | 群聊(基于任务的发言者选择策略) |
| --- | --- | --- | --- |
| GPT-3.5-turbo | 8 | 9 | 7 |
| GPT-4 | 9 | **11** | 8 |

**表 6:12 个任务上的平均 LLM 调用次数与终止失败次数(越低越好)**

| 模型 | 双智能体 | 群聊 | 群聊(基于任务的发言者选择策略) |
| --- | --- | --- | --- |
| GPT-3.5-turbo | 9.9 次调用,9 次终止失败 | 5.3,0 | 4,0 |
| GPT-4 | 6.8,3 | **4.5,0** | 4,0 |

[图 13: Comparison of two-agent chat (a) and group chat (b) on a given task. The group chat resolves the task successfully with a smoother conversation, while the two-agent chat fails on the same task and ends with a repeated conversation.]

图 13:同一任务上双智能体聊天 (a) 与群聊 (b) 的对比。群聊以更顺畅的对话成功解决任务,而双智能体聊天在同一任务上失败,以重复对话收场。(图示为具体对话转录,内容从略。)

#### A6:对话式国际象棋(附录 D)

[图 14: A6: Conversational Chess: Our conversational chess application can support various scenarios, as each player can be an LLM-empowered AI, a human, or a hybrid of the two. Here, the board agent maintains the rules of the game and supports the players with information about the board. Players and the board agent all use natural language for communication.]

图 14:A6 对话式国际象棋:我们的对话式国际象棋应用支持多种场景——每个棋手可以是 LLM 驱动的 AI、人类或两者的混合。棋盘智能体维护游戏规则,并为棋手提供棋盘信息;棋手与棋盘智能体全部用自然语言交流(图中示例对话:"挑战你中心的兵,该你了。""把我的马走到好位置,该你了。")。

::: en
In Conversational Chess, each player is a AutoGen agent and can be powered either by a human or an AI. A third party, known as the board agent, is designed to provide players with information about the board and ensure that players' moves adhere to legal chess moves. Figure 14 illustrates the scenarios supported by Conversational Chess: AI/human vs. AI/human, and demonstrates how players and the board agent interact. This setup fosters social interaction and allows players to express their moves creatively, employing jokes, meme references, and character-playing, thereby making chess games more entertaining for both players and observers (Figure 15 provides an example of conversational chess).

To realize these scenarios, we constructed a player agent with LLM and human as back-end options. When human input is enabled, before sending the input to the board agent, it first prompts the human player to input the message that contains the move along with anything else the player wants to say (such as a witty comment). If human input is skipped or disabled, LLM is used to generate the message. The board agent is implemented with a custom reply function, which employs an LLM to parse the natural language input into a legal move in a structured format (e.g., UCI), and then pushes the move to the board. If the move is not legitimate, the board agent will reply with an error. Subsequently, the player agent needs to resend a message to the board agent until a legal move is made. Once the move is successfully pushed, the player agent sends the message to the opponent. As shown in Figure 15, the conversation between AI players can be natural and entertaining. When the player agent uses LLM to generate a message, it utilizes the board state and the error message from the board agent. This helps reduce the chance of hallucinating an invalid move. The chat between one player agent and the board agent is invisible to the other player agent, which helps keep the messages used in chat completion well-managed.

There are two notable benefits of using AutoGen to implement Conversational Chess. Firstly, the agent design in AutoGen facilitates the natural creation of objects and their interactions needed in our chess game. This makes development easy and intuitive. For example, the isolation of chat messages simplifies the process of making a proper LLM chat completion inference call. Secondly, AutoGen greatly simplifies the implementation of agent behaviors using composition. Specifically, we utilized the register_reply method supported by AutoGen agents to instantiate player agents and a board agent with custom reply functions. Concentrating the extension work needed at a single point (the reply function) simplifies the reasoning processes, and development and maintenance effort.
:::

在对话式国际象棋中,每个棋手都是一个 AutoGen 智能体,后端可以是人类或 AI。第三方**棋盘智能体**为棋手提供棋盘信息,并确保棋手走法符合国际象棋规则。图 14 展示了支持的场景(AI/人类 对 AI/人类)以及棋手与棋盘智能体的交互方式。这一设定促进社交互动,允许棋手创造性地表达走法——用笑话、梗、角色扮演,使棋局对棋手与观战者都更有趣(图 15 给出一个对话式国际象棋的例子)。

为实现这些场景,我们构造了以 LLM 与人类为后端选项的棋手智能体。启用人类输入时,它先提示人类棋手输入包含走法及其他想说内容(如俏皮评论)的消息,再发给棋盘智能体;若跳过或禁用人类输入,则由 LLM 生成消息。棋盘智能体用自定义回复函数实现:先用 LLM 把自然语言输入解析成结构化格式的合法走法(如 UCI),再把走法推到棋盘;若走法不合法,棋盘智能体回复错误,棋手智能体须重新发消息直到走出合法着。走法成功推送后,棋手智能体把消息发给对手。如图 15 所示,AI 棋手之间的对话可以自然又有趣。棋手智能体用 LLM 生成消息时会利用棋盘状态与棋盘智能体的错误信息,这有助于减少幻觉出非法走法的几率。一个棋手智能体与棋盘智能体之间的聊天对另一个棋手智能体不可见,有助于保持聊天补全所用消息的良好管理。

用 AutoGen 实现对话式国际象棋有两大显著收益。第一,AutoGen 的智能体设计让自然地创建棋类游戏所需的对象及其交互变得容易,开发简单直观——例如聊天消息的隔离简化了进行规范 LLM 聊天补全推理调用的过程。第二,AutoGen 用组合(composition)大幅简化了智能体行为的实现:我们利用 AutoGen 智能体支持的 register_reply 方法,以自定义回复函数实例化棋手智能体与棋盘智能体。把所需扩展集中在单一点(回复函数)上,简化了推理过程与开发维护成本。

[图 15: Example conversations during a game involving two AI player agents and a board agent.]

图 15:两个 AI 棋手智能体与一个棋盘智能体的一局示例对话。**(a) 两个 AI 棋手之间的对话**:"好,开局吧。我把兵从 e2 走到 e4——棋盘中心可是战局的心脏,不是吗?""啊,王兵开局,经典。我把兵从 e7 走到 e5……我一直很欣赏国际象棋如何映照人生:全在于做战略性决策,不是吗?该你了。""确实,棋如人生的写照——每一步都重要,就像人生的每个决定。我把马从 g1 走到 f3,瞄准控制中心。"**(b) AI 棋手(执白)与棋盘智能体的对话**:棋手自然语言提议走法,棋盘智能体解析验证;若非法(如 "Error: illegal uci: 'e4e5'")则报错,棋手改走合法着(如 "我把兵从 d2 走到 d4,为后与象打开线路")。

::: en
To illustrate the effect facilitated by this board agent, we provide a demonstration of conversational chess without a board agent in Figure 16. In this demonstration, instead of employing an additional board agent for grounding, the system utilizes prompting for grounding by including the sentence "You should make sure both you and the opponent are making legal moves." in the system messages directed to both players.
:::

为说明棋盘智能体带来的效果,我们在图 16 中提供了一段**没有**棋盘智能体的对话式国际象棋演示。该演示不用额外的棋盘智能体做锚定,而是在发给双方棋手的系统消息中加入句子 "You should make sure both you and the opponent are making legal moves."(你应确保你和对手的走法都合法),用提示做锚定。

[图 16: Comparison of two designs–(a) without a board agent, and (b) with a board agent–in Conversational Chess.]

图 16:对话式国际象棋两种设计的对比。**(a) 无棋盘智能体**:玩家系统消息为"你的名字是 {name},你是一名棋手,与 {opponent_name} 对弈,执 {color}。你用通用棋类接口语言(UCI)传达走法,传达走法时可与对手闲聊活跃气氛。你应确保你和对手的走法都合法……"。演示中执白棋手声称"把马从 b8 走到 c6"并自行打印"更新后的棋盘"——但实际上把 a8 的车改成了马再挪到 c6,棋面状态已错乱,游戏被非法走法破坏。**(b) 有棋盘智能体**:棋盘智能体回复 "Your move is illegal. You changed the rock (rook) at a8 to knight and move it to c6. Please check your decision and re-make your move.",棋手道歉后改走真正合法的 "把马从 b8 走到 c6",棋盘状态保持一致。

#### A7:浏览器交互的在线决策

> **译注**:A7 未出现在正文第 3 节的六个应用中,是附录 D 里追加的第七个应用示例。

[图 17: We use AutoGen to build MiniWobChat, which solves tasks in the MiniWob++ benchmark. MiniWobChat consists of two agents: an assistant agent and an executor agent. The assistant agent suggests actions to manipulate the browser while the executor executes the suggested actions and returns rewards/feedback. The assistant agent records the feedback and continues until the feedback indicates task success or failure.]

图 17:我们用 AutoGen 构建 **MiniWobChat** 来求解 MiniWoB++ 基准任务。MiniWobChat 由两个智能体组成:助手智能体建议操纵浏览器的动作;执行器执行建议的动作并返回奖励/反馈;助手记录反馈并继续,直到反馈表明任务成功或失败。环境状态是当前网页的 HTML 代码,奖励为 Success/Fail/Ongoing,动作决策形如"点击 xpath 为 '//button[id=\"subbtn\"]' 的按钮"(示例 HTML 含 "Click button ONE, then click button TWO." 的任务指令与 ONE/TWO 两个按钮)。

::: en
In practice, many applications require the presence of agents capable of interacting with environments and making decisions in an online context, such as in game playing (Mnih et al., 2013; Vinyals et al., 2017), web interactions (Liu et al., 2018; Shi et al., 2017), and robot manipulations (Shen et al., 2021). With the multi-agent conversational framework in AutoGen, it becomes easy to decompose the automatic agent-environment interactions and the development of a decision-making agent by constructing an executor agent responsible for handling the interaction with the environment, thereby delegating the decision-making part to other agents. Such a decomposition allows developers to reuse the decision-making agent for new tasks with minimal effort rather than building a specialized decision-making agent for every new environment.

**Workflow.** We demonstrate how to use AutoGen to build a working system for handling such scenarios with the MiniWoB++ benchmark (Shi et al., 2017). MiniWoB++ comprises browser interaction tasks that involve utilizing mouse and keyboard actions to interact with browsers. The ultimate objective of each task is to complete the tasks described concisely in natural language, such as "expand the web section below and click the submit button." Solving these tasks typically requires a sequence of web manipulation actions rather than a single action, and making action decisions at each time step requires access to the web status (in the form of HTML code) online. For the example above, clicking the submit button requires checking the web status after expanding the web section. We designed a straightforward two-agent system named MiniWobChat using AutoGen, as shown in Figure 17. The assistant agent is an instance of the built-in AssistantAgent and is responsible for making action decisions for the given task. The second agent, the executor agent, is a customized UserProxyAgent, which is responsible for interacting with the benchmark by executing the actions suggested by the AssistantAgent and returning feedback.
:::

实践中,许多应用需要能与环境交互并在线做决策的智能体,例如游戏(Mnih et al., 2013; Vinyals et al., 2017)、网页交互(Liu et al., 2018; Shi et al., 2017)与机器人操作(Shen et al., 2021)。借助 AutoGen 的多智能体对话框架,可以很容易地把"智能体-环境自动交互"与"决策智能体的开发"解耦:构造一个负责与环境交互的执行器智能体,把决策部分交给其他智能体。这种分解让开发者能以最小代价把决策智能体复用到新任务上,而不必为每个新环境构建专门的决策智能体。

**工作流。** 我们演示如何用 AutoGen 在 MiniWoB++ 基准(Shi et al., 2017)上为此类场景构建可运行的系统。MiniWoB++ 包含需要用鼠标键盘动作与浏览器交互的任务;每个任务的最终目标是完成用自然语言简要描述的事情,如"展开下方网页区块并点击提交按钮"。解此类任务通常需要一串网页操纵动作而非单一动作,且每个时间步做动作决策都需要在线获取网页状态(HTML 代码形式)——对上例而言,点击提交按钮前需要先检查展开区块后的网页状态。我们用 AutoGen 设计了简洁的双智能体系统 **MiniWobChat**(图 17):助手智能体是内置 AssistantAgent 的实例,负责为给定任务做动作决策;第二个智能体——执行器智能体——是定制的 UserProxyAgent,负责通过执行 AssistantAgent 建议的动作与基准交互并返回反馈。

::: en
To assess the performance of the developed working system, we compare it with RCI (Kim et al., 2023), a recent solution for the MiniWoB++ benchmark that employs a set of self-critiquing prompts and has achieved state-of-the-art performance. In our evaluation, we use all available tasks in the official RCI code, with varying degrees of difficulty, to conduct a comprehensive analysis against MiniWobChat. Figure 18 illustrates that MiniWobChat achieves competitive performance in this evaluation⁸. Specifically, among the 49 available tasks, MiniWobChat achieves a success rate of 52.8%, which is only 3.6% lower than RCI, a method specifically designed for the MiniWoB++ benchmark. It is worth noting that in most tasks, the difference between the two methods is mirrored as shown in Figure 18. If we consider 0.1 as a success rate tolerance for each task, i.e., two methods that differ within 0.1 are considered to have the same performance, both methods outperform the other on the same number of tasks. For illustration purposes, we provide a case analysis in Table 7 on four typical tasks.

Additionally, we also explored the feasibility of using Auto-GPT for handling the same tasks. Auto-GPT faces challenges in handling tasks that involve complex rules due to its limited extensibility. It provides an interface for setting task goals using natural language. However, when dealing with the MiniWoB++ benchmark, accurately instructing Auto-GPT to follow the instructions for using MiniWoB++ proves challenging. There is no clear path to extend it in the manner of the two-agent chat facilitated by AutoGen.

**Takeaways:** For this application, AutoGen stood out as a more user-friendly option, offering modularity and programmability: It streamlined the process with autonomous conversations between the assistant and executor, and provided readily available solutions for agent-environment interactions. The built-in AssistantAgent was directly reusable and exhibited strong performance without customization. Moreover, the decoupling of the execution and assistant agent ensures that modifications to one component do not adversely impact the other. This convenience simplifies maintenance and future updates.
:::

为评估该系统的性能,我们将其与 RCI(Kim et al., 2023)对比——RCI 是 MiniWoB++ 基准的新近方案,使用一组自我批评提示,达到了最先进性能。评测中,我们使用官方 RCI 代码中全部可用任务(难度各异),对 MiniWobChat 做全面分析。图 18 显示 MiniWobChat 在该评测中取得了有竞争力的性能(原文脚注:⁸ RCI 的结果由运行其官方代码(默认设置)得到):在 49 个可用任务上,MiniWobChat 成功率 **52.8%**,仅比专为 MiniWoB++ 设计的 RCI 低 3.6%。值得注意的是,如图 18 所示,多数任务上两种方法的差距呈镜像分布;若把 0.1 视为每任务的成功率容差(差距在 0.1 内即视为性能相同),两方法互有胜负的任务数相等。为便于说明,表 7 给出四个典型任务的案例分析。

此外,我们还探索了用 Auto-GPT 处理相同任务的可行性。Auto-GPT 因可扩展性有限,在处理涉及复杂规则的任务时面临挑战:它提供用自然语言设定任务目标的接口,但在 MiniWoB++ 基准上,要准确指示 Auto-GPT 遵循 MiniWoB++ 的使用说明颇为困难;也不存在以 AutoGen 双智能体聊天方式扩展它的清晰路径。

**要点(Takeaways):** 在该应用中,AutoGen 是更易用的选择,提供模块化与可编程性:它用助手与执行器之间的自主对话精简了流程,并为智能体-环境交互提供了现成方案。内置 AssistantAgent 可直接复用,无需定制就有强劲表现;而且执行智能体与助手智能体的解耦,确保对一个组件的修改不会对另一个组件产生不利影响——这一便利简化了维护与未来更新。

[图 18: Comparisons between RCI (state-of-the-art prior work) and MiniWobChat on the MiniWob++ benchmark are elucidated herein. We utilize all available tasks in the official RCI code, each with varying degrees of difficulty, to conduct comprehensive comparisons. For each task, the success rate across ten different instances is reported. The results reveal that MiniWobChat attains a performance comparable to that of RCI. When a success rate tolerance of 0.1 is considered for each task, both methods outperform each other on an equal number of tasks.]

图 18:RCI(此前的最先进工作)与 MiniWobChat 在 MiniWoB++ 基准上的对比。我们使用官方 RCI 代码中全部可用任务(难度各异)做全面比较;每个任务报告 10 个不同实例上的成功率,覆盖 click-button、click-checkboxes、enter-text、login-user、navigate-tree、search-engine、social-media、terminal、use-spinner 等 49 个任务。结果表明 MiniWobChat 达到与 RCI 相当的性能;当对每任务考虑 0.1 的成功率容差时,两方法互有胜负的任务数相等。

**表 7:MiniWoB++ 四个典型任务的案例分析**

| 任务 | 正确性 | 主要失败原因 |
| --- | --- | --- |
| click-dialog | AutoGen:10/10;RCI:10/10 | 无 |
| click-checkboxes-large | AutoGen:5/10;RCI:0/10 | AutoGen:AssistantAgent 给出的动作含不可行字符;RCI:执行了计划之外的动作 |
| count-shape | AutoGen:2/10;RCI:0/10 | AutoGen:AssistantAgent 给出的动作含冗余内容、无法转换为基准动作;RCI:多数情况给出错误计划 |
| use-spinner | AutoGen:0/10;RCI:1/10 | AutoGen:AssistantAgent 返回计划之外的动作;RCI:多数情况给出错误计划 |

### 附录 E 各应用的示例输出(译注)

> **译注**:附录 E(原文表 8-19)收录各系统的完整原始输出转录,均为直接对话/日志记录,此处概述要点、不逐行转录,细节请查阅原文 PDF:
>
> - **表 8(ChatGPT+Plugin 解第一道化简题)**:Wolfram 返回两个化简结果 (5√42)/27 与 (5√(14/3))/9,其中前者正确;ChatGPT 却选择了后者,答错。
> - **表 9(AutoGen 解同一题)**:助手生成 sympy 代码(用 sqrt/Rational/simplify 化简分数),用户代理执行成功,输出 `5*sqrt(42)/27`,回复 TERMINATE——正确解决。
> - **表 10(LangChain ReAct)**:生成 math 库代码只算出小数 1.200137…,未按要求给出精确化简形式——答错。
> - **表 11(AutoGPT)**:先误用 `math.simplify` 报错,改用 sympy 后代码又因缺少 print 而无输出,反复两轮无果后被用户 Ctrl+C 中止;过程中每次回复都带 THOUGHTS/REASONING/PLAN/CRITICISM 等冗长模板。
> - **表 12(Multi-Agent Debate)**:正反双方经推导均得出 7√1050/189 的"最终答案",主持人裁定反方推理更好——但该答案本身是错的(正确为 5√42/27),展示纯语言辩论无法自查计算错误。
> - **表 13(ChatGPT+Code Interpreter 做 OptiGuide)**:围绕"烘焙成本上涨 5%"问题,用户须手动下载代码、经 Safeguard 检查两次 DANGER 后才获 SAFE,再手动运行并把终端输出复制粘贴回去,最终得出成本从 2470 涨到 2526.5——过程繁琐、人工步骤多。
> - **表 14(ChatGPT+Code Interpreter 解第一道化简题)**:同样只返回小数近似 1.200…,答错。
> - **表 15(AutoGen 版 OptiGuide 同题)**:一句话提问后直接得到结论:"烘焙成本上涨 5% 后,新最优总成本 2526.5,较初始 2470.0 上升 56.5 个单位"。
> - **表 16(BabyAGI)**:解出一半后自创出 10 道同型新题加入任务列表,在任务优先级排序阶段被中止——并未解决原问题。
> - **表 17(CAMEL)**:构造"Math Solver"与"Python Programmer"双角色,角色扮演对话逐条索要代码片段(import 库、定义函数骨架……),始终不执行代码、不给最终答案,被人工中止。
> - **表 18(MetaGPT)**:面对数学题输出了产品目标、用户故事、竞品分析等"软件开发文档",完全答非所问,被中止。
> - **表 19(MiniWobChat 解 click-button-sequence)**:执行器把网页 HTML 与任务说明发给助手,助手给出两步计划并逐条发出 `clickxpath //button[@id='subbtn']`、`clickxpath //button[@id='subbtn2']` 指令,执行成功后返回 SUCCESS!!!! 并 TERMINATE。

## 要点速览

- 两大抽象:**可对话智能体**(send/receive/generate_reply 统一接口,LLM/人/工具混合后端)+ **对话编程**(计算对话中心化、控制流对话驱动)。
- **auto-reply 机制**是关键工程:注册好回复函数后,会话自动推进,无需中央控制平面——工作流即对话。
- 控制流三态:自然语言(提示词)、编程语言(Python)、以及通过函数调用/自定义回复函数在两者间切换;动态会话靠自定义 generate_reply 或函数调用实现。
- 实证亮点:MATH 上开箱即用超商业方案(52.5% vs ChatGPT+Code Interpreter 45.0%);交互式检索 +11 F1;grounding agent +15%;安全护栏拆分独立智能体 +8~35% F1;OptiGuide 代码 430→100 行。
- 设计哲学:与其为每种工作流写专门编排,不如提供"对话"这一个原语,让工作流在对话中涌现。
- 与课程关联:是"多智能体框架侧"的代表;读完后应接着读同讲《Why Do Multi-Agent LLM Systems Fail?》(失败分类学)与 Neubig 博客(单智能体辩护),形成完整判断;GroupChatManager 的动态发言者选择与 DyLAN 的动态团队构成互为参照。
