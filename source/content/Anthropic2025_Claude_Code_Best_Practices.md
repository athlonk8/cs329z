---
title: Best practices for Claude Code
title_zh: Claude Code 最佳实践
authors: Anthropic
venue: "Anthropic · Claude Code Docs"
kind: blog
importance: must
tags: Claude Code,编程智能体,上下文管理,智能体工程,最佳实践,人机协作
summary: Anthropic 官方总结的 Claude Code 使用最佳实践:从环境配置、验证闭环、上下文管理到并行扩展的完整工程方法论。
---

## 导读

本文是第 9 周「编程智能体」的实操配套材料。前几份材料(SWE-bench、SWE-agent、OpenHands)回答的是"编程智能体如何被评测、如何设计接口与平台";这篇 Anthropic 官方最佳实践则回答"作为工程师,如何真正驾驭一个生产级编程智能体"。它把编程智能体的使用从"聊天式问答"升级为一种工程工作流:给智能体可自验的检查闭环、用计划模式分离探索与执行、把项目约定沉淀进 CLAUDE.md、用子智能体和并行会话规模化产出。全文所有建议都围绕一条核心约束展开——**上下文窗口是最重要、最易耗尽的资源**。这一视角与本课程此前的上下文工程、智能体设计模式等主题一脉相承,是"must 级"必读。

## 全文中译

# Claude Code 最佳实践

> 从配置环境到跨并行会话扩展,帮助你从 Claude Code 中获得最大收益的技巧与模式。

Claude Code 是一个智能体式编程环境(agentic coding environment)。与只回答问题然后等待的聊天机器人不同,Claude Code 可以读取你的文件、运行命令、做出修改,并自主地推进问题解决——期间你可以旁观、随时纠偏,也可以完全走开。

这改变了你的工作方式。你不再自己写代码然后让 Claude 审查,而是描述你想要什么,由 Claude 决定如何构建。Claude 负责探索、规划与实现。

但这种自主性也伴随着学习曲线。Claude 在一定的约束条件下工作,你需要理解这些约束。

本指南汇总了在 Anthropic 内部团队以及各类代码库、语言与环境中使用 Claude Code 的工程师们被验证有效的模式。关于智能体循环(agentic loop)的底层工作原理,请参阅《How Claude Code works》。

大多数最佳实践都基于同一条约束:**Claude 的上下文窗口填充得很快,而且随着填充程度上升,性能会下降。**

Claude 的上下文窗口容纳你的整段对话,包括每一条消息、Claude 读过的每一个文件、每一条命令输出。但它很容易被填满。单次调试会话或代码库探索就可能产生并消耗数万个 token。

这一点很重要,因为 LLM 的性能会随着上下文被填满而退化。当上下文窗口接近满载时,Claude 可能开始"遗忘"较早的指令或犯更多错误。上下文窗口是最需要管理的资源。若想直观了解一个会话如何被填满,可以观看交互式演示,看看启动时加载了什么、每读取一个文件花费多少。可以用自定义状态行(custom status line)持续跟踪上下文用量,并参考"Reduce token usage"了解减少 token 使用的策略。

## 给 Claude 一种验证自己工作的方式

给 Claude 一个它能运行的检查:测试、构建、可供比对的截图。这是"你盯着的会话"与"你能走开的会话"之间的分水岭。

Claude 在工作"看起来完成"时就会停下。如果没有它能运行的检查,"看起来完成"就是唯一可用的信号,于是你自己变成了验证环节:每个错误都要等你来发现。给 Claude 一个能输出通过或失败的东西,这个闭环就能自行收拢:Claude 做事、运行检查、读取结果、反复迭代,直到检查通过。

这个"检查"可以是任何能在对话中返回 Claude 可读信号的东西:测试套件、构建退出码、linter、一个将输出与 fixture 做比对的脚本,或一张与设计稿对比的浏览器截图。在 Claude 的检查通过后,你自己再运行 `/verify`,对照运行中的应用确认这次改动。

| 策略 | 之前 | 之后 |
| --- | --- | --- |
| 提供验证标准 | "实现一个验证邮箱地址的函数" | "写一个 `validateEmail` 函数。示例测试用例:`user@example.com` 为 true,`invalid` 为 false,`user@.com` 为 false。实现后运行测试" |
| 用视觉方式验证 UI 改动 | "把仪表盘做好看点" | "[粘贴截图] 实现这个设计。对结果截图并与原图比较,列出差异并修复" |
| 解决根因而非症状 | "构建失败了" | "构建报了这个错:[粘贴错误]。修复它并验证构建成功。要解决根因,不要压制报错" |

一旦有了检查,还要决定它对"停止"的约束强度:

- **在一个提示里**:让 Claude 在同一条消息中运行检查并迭代,如上表所示。
- **跨整个会话**:把检查设为 `/goal` 条件。一个独立的评估器会在每轮之后重新检查,Claude 会持续工作直到目标达成。如果 Claude 卡住,Claude Code 最终会在目标仍设置的状态下停止运行——参见 /goal 的评估机制。
- **作为确定性闸门**:Stop hook 会以脚本方式运行你的检查,并阻止本轮结束,直到检查通过。Claude Code 会在连续 8 次拦截后越过该 hook 并结束本轮。
- **借助第二意见**:验证子智能体(verification subagent)或能自查结论的动态工作流(dynamic workflow),让一个全新的模型尝试反驳结果——做事的智能体不再是给自己打分的那个。

以上每一档都在"搭建成本"与"省下的注意力"之间做交换。提示词版本今天就能用于任何任务;`/goal` 与 Stop hook 版本则让无人值守的运行也能正确收尾。

让 Claude 出示证据而不是断言成功:测试输出、它运行了什么命令、返回了什么,或结果截图。审查证据比你自己重跑验证更快,而且适用于你没在旁盯着的会话。

## 先探索,再规划,再编码

把研究与规划同实现分开,避免解决错误的问题。

让 Claude 直接上手写代码,可能产出"解决了错误问题"的代码。使用计划模式(plan mode)把探索与执行分开。

推荐的工作流有四个阶段:

**1. 探索(Explore)**

按 `Shift+Tab` 切换到状态栏显示 `⏸ plan mode on` 的计划模式,或以 `claude --permission-mode plan` 启动会话。Claude 只读文件、回答问题,不做任何修改。

```
claude (plan mode)
读取 /src/auth,理解我们如何处理会话与登录。
另外看看我们如何管理 secrets 相关的环境变量。
```

**2. 规划(Plan)**

让 Claude 制定详细的实现计划。

```
claude (plan mode)
我想添加 Google OAuth。需要改哪些文件?
会话流程是什么?给我一份计划。
```

按 `Ctrl+G` 可在文本编辑器中直接编辑该计划,然后才让 Claude 继续。

**3. 实现(Implement)**

通过批准计划或按 `Shift+Tab` 退出计划模式,然后让 Claude 按计划编码,并对照计划验证。

```
claude
按照你的计划实现 OAuth 流程。为回调处理器写测试,
运行测试套件并修复所有失败。
```

**4. 提交(Commit)**

让 Claude 用描述性的提交信息提交并创建 PR。

```
claude
用描述性的提交信息提交,并开一个 PR
```

计划模式很有用,但也有开销。对于范围明确、改动很小的任务(修 typo、加一行日志、重命名变量),直接让 Claude 去做即可。规划最有用的场景是:你对方案还不确定、改动涉及多个文件、或者你对要改的代码不熟悉。如果你能用一句话描述出那个 diff,就不用做计划。

## 在提示词中提供具体的上下文

指令越精确,你需要纠正的次数就越少。

Claude 能推断意图,但读不了你的心。引用具体文件、说明约束、指向示例模式。

| 策略 | 之前 | 之后 |
| --- | --- | --- |
| 限定任务范围:指明哪个文件、什么场景、测试偏好 | "给 foo.py 加测试" | "给 foo.py 写一个测试,覆盖用户已登出的边界情况。避免使用 mock。" |
| 指向信息源:把 Claude 引向能回答问题的源头 | "为什么 ExecutionFactory 的 API 这么怪?" | "翻一下 ExecutionFactory 的 git 历史,总结它的 API 是怎么变成这样的" |
| 引用已有模式:指向你代码库中的范例 | "加一个日历组件" | "看看首页已有组件是怎么实现的,理解其中的模式,HotDogWidget.php 是个好例子。照这个模式实现一个新的日历组件,让用户能选月份并前后翻页选年份。除代码库已在用的库外不要引入其他库,从零构建" |
| 描述症状:给出症状、可能位置与"修好"的标准 | "修一下登录 bug" | "用户反馈会话超时后登录失败。检查 src/auth/ 中的认证流程,尤其是 token 刷新。先写一个能复现该问题的失败测试,再修复它" |

在探索阶段、且你能承受纠偏成本时,模糊的提示词也有用。比如"你觉得这个文件里有什么可以改进的?"就可能挖出你没想到要问的问题。

## 提供丰富的内容

用 `@` 引用文件、粘贴截图/图片,或直接管道输入数据。

你可以通过多种方式向 Claude 提供丰富数据:

- **用 `@` 引用文件**,而不是描述代码在哪里。Claude 会在响应前先读取该文件。
- **直接粘贴图片**:复制粘贴或把图片拖入提示框。
- **给 URL**,用于文档和 API 参考。用 `/permissions` 把常用域名加入白名单。
- **管道输入数据**:运行 `cat error.log | claude`,把文件内容直接送入。
- **让 Claude 自己取**:让 Claude 用 Bash 命令、MCP 工具或读文件的方式自行拉取上下文。

## 配置你的环境

几个初始设置能让 Claude Code 在你所有会话中的效率显著提升。关于各类扩展功能及适用时机的全貌,参见《Extend Claude Code》。

### 写一份有效的 CLAUDE.md

运行 `/init` 基于当前项目结构生成一份 CLAUDE.md 起点,再随时间打磨。

CLAUDE.md 是一个特殊文件,Claude 在每段对话开始时都会读取。把 Bash 命令、代码风格、工作流规则写进去,给 Claude 提供它无法仅凭代码推断的持久上下文。

CLAUDE.md 没有强制格式,但要保持简短、人类可读。例如:

```markdown
# Code style

- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow

- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

运行 `/context` 确认 Claude 加载了该文件。CLAUDE.md 每个会话都会加载,所以只写普遍适用的内容。至于只在某些时候相关的领域知识或工作流,用 skills 代替——Claude 按需加载它们,不会撑大每一段对话。

保持精炼。对每一行问一句:"删掉它会导致 Claude 犯错吗?"如果不会,就删。臃肿的 CLAUDE.md 会导致 Claude 忽略你真正的指令!

| 应当包含 | 应当排除 |
| --- | --- |
| Claude 猜不到的 Bash 命令 | Claude 读代码就能明白的东西 |
| 偏离默认值的代码风格规则 | Claude 已知的标准语言惯例 |
| 测试说明与首选测试运行器 | 详细的 API 文档(改为给链接) |
| 仓库礼仪(分支命名、PR 规范) | 经常变动的信息 |
| 项目特有的架构决策 | 冗长的解释或教程 |
| 开发环境的坑(必需的环境变量) | 逐文件的代码库描述 |
| 常见坑与非直观行为 | "写干净的代码"这类不言自明的实践 |

如果 Claude 在已有规则的情况下仍反复做你不想让它做的事,多半是文件太长、规则淹没在噪音里了。如果 Claude 问的问题其实在 CLAUDE.md 里有答案,可能是表述有歧义。像对待代码一样对待 CLAUDE.md:出了问题就复查,定期修剪,并通过观察 Claude 行为是否真的变化来测试改动。对于已提交到仓库的 CLAUDE.md,运行 `/doctor`,Claude 会为其能从代码库推导出的内容提出删减建议。

如果 Claude 总是跳过某一条指令,可以只给那一行加"IMPORTANT"之类的强调。如果你强调了很多行,就没有任何一行突出了。把 CLAUDE.md 提交进 git,让团队都能贡献,这个文件的价值会随时间复利增长。

CLAUDE.md 文件可以用 `@path/to/import` 语法导入其他文件。导入规则及 CLAUDE.md 可存放的位置,参见 CLAUDE.md 相关文档。

### 配置权限

要想少弹确认又不失控,用 `/permissions` 预批准你信任的工具,用 `/sandbox` 让沙箱内的命令免确认运行。想亲自审批编辑与命令时,切换到 Manual 模式。

在 Pro、Max 和 Team 计划上,auto 模式是交互式终端与 VS Code 会话的内置默认权限模式:一个独立的分类器模型会代替你审查大多数操作,只拦截看起来有风险的行为,比如权限范围升级、未知基础设施、或由恶意内容驱动的动作。

在其他计划的内置默认模式 Manual 下,Claude Code 会在可能修改你系统的操作(写文件、Bash 命令、MCP 工具)前询问。这安全但繁琐——批到第十次,你已经在机械点击而不是审查。以下两个工具能减少这类打断(在 auto 模式下同样适用):

- **权限白名单(permission allowlists)**:许可你确定安全的特定工具,如 `npm run lint` 或 `git commit`。
- **沙箱(sandboxing)**:启用操作系统级隔离,限制文件系统与网络访问,让 Claude 能在明确边界内更自由地工作。

更多内容参见权限模式、权限规则与沙箱的文档。

### 使用 CLI 工具

与外部服务交互时,告诉 Claude Code 使用 `gh`、`aws`、`gcloud`、`sentry-cli` 这类 CLI 工具。

CLI 工具是与外部服务交互时上下文效率最高的方式。如果你用 GitHub,就装 `gh` CLI。Claude 知道怎么用它创建 issue、开 PR、读评论。没有 `gh` 时 Claude 也能用 GitHub API,但未认证的请求常会撞限流。

Claude 也擅长学习它还不认识的 CLI 工具。可以试试这样的提示词:"Use 'foo-cli-tool --help' to learn about foo tool, then use it to solve A, B, C."(先用 --help 学习 foo 工具,再用它解决 A、B、C。)

### 接入 MCP 服务器

运行 `claude mcp add`,带上服务器名称与 URL 或命令,即可接入 Notion、Figma 或你的数据库等外部工具。例如:

```
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

有了 MCP 服务器,你可以让 Claude 根据 issue 跟踪器实现功能、查询数据库、分析监控数据、集成 Figma 设计、自动化工作流。

### 设置 hooks

对于"每次必须发生、零例外"的动作,用 hooks。

Hooks 会在 Claude 工作流的特定节点自动运行脚本。与仅具建议性的 CLAUDE.md 指令不同,hooks 是确定性的,能保证动作发生。

Claude 可以替你写 hooks。试试这样的提示词:"写一个每次文件编辑后都运行 eslint 的 hook",或"写一个阻止向 migrations 文件夹写入的 hook"。也可以直接编辑 `.claude/settings.json` 手工配置,运行 `/hooks` 浏览当前配置。

### 创建 skills

在 `.claude/skills/` 下创建 `SKILL.md` 文件,为 Claude 提供领域知识与可复用工作流。

Skills 为 Claude 扩展了项目、团队或领域特有的知识。Claude 会在相关时自动应用,你也可以用 `/skill-name` 直接调用。

在 `.claude/skills/` 下添加一个含 `SKILL.md` 的目录即可创建技能:

```
.claude/skills/api-conventions/SKILL.md
---
name: api-conventions
description: REST API design conventions for our services
---

# API Conventions

- Use kebab-case for URL paths
- Use camelCase for JSON properties
- Always include pagination for list endpoints
- Version APIs in the URL path (/v1/, /v2/)
```

(中文说明:上面是一份 API 约定技能——URL 路径用 kebab-case,JSON 属性用 camelCase,列表端点必须分页,API 版本号放在 URL 路径中。)

Skills 也可以定义你直接调用的可复用工作流:

```
.claude/skills/fix-issue/SKILL.md
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Analyze and fix the GitHub issue: $ARGUMENTS.

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
6. Ensure code passes linting and type checking
7. Create a descriptive commit message
8. Push and create a PR
```

(中文说明:这是一个"修复 GitHub issue"的工作流技能——查看 issue、理解问题、检索代码、实现修复、写测试并运行、通过 lint 与类型检查、生成提交信息、推送并开 PR。运行 `/fix-issue 1234` 即可调用。)

对有副作用、希望手动触发的工作流,使用 `disable-model-invocation: true`。

### 创建自定义子智能体

在 `.claude/agents/` 下定义专门的助手,让 Claude 可以把隔离任务委托出去。

子智能体(subagents)在各自的上下文中运行,拥有各自允许的工具集。它们适合处理需要读大量文件、或需要专门聚焦的任务,且不会弄乱你的主对话。

```
.claude/agents/security-reviewer.md
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---

You are a senior security engineer. Review code for:

- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

(中文说明:这是一个安全审查子智能体——资深安全工程师角色,检查注入漏洞(SQL/XSS/命令注入)、认证与授权缺陷、代码中的密钥凭据、不安全的数据处理,并给出具体行号引用与修复建议。)

明确告诉 Claude 使用子智能体:"Use a subagent to review this code for security issues."(用子智能体审查这段代码的安全问题。)

### 安装插件

运行 `/plugin` 浏览插件市场。插件无需配置即可添加技能、工具与集成。

插件(plugins)把技能、hooks、子智能体和 MCP 服务器打包成来自社区与 Anthropic 的单一可安装单元。如果你使用静态类型语言,可以安装代码智能(code intelligence)插件,让 Claude 获得精确的符号导航与编辑后的自动错误检测。

如何在 skills、子智能体、hooks 与 MCP 之间选择,参见《Extend Claude Code》。

## 有效沟通

像问另一位工程师那样问 Claude 问题;对较大的功能,先让 Claude 面试你、写出规格说明,再开始实现。

### 问代码库问题

把你会问资深工程师的问题拿来问 Claude。

接手新代码库时,把 Claude Code 用于学习与探索。你可以问 Claude 那些你会问其他工程师的问题:

- 日志是怎么工作的?
- 我怎么加一个新的 API 端点?
- `foo.rs` 第 134 行的 `async move { ... }` 是什么意思?
- `CustomerOnboardingFlowImpl` 处理了哪些边界情况?
- 为什么第 333 行这里调用 `foo()` 而不是 `bar()`?

这样用 Claude Code 是一种高效的上手方式,能缩短磨合期、减少对其他工程师的打扰。不需要特殊提示技巧,直接问即可。

### 让 Claude 面试你

对较大的功能,先让 Claude 来面试你。从一个最小提示词开始,让 Claude 用 AskUserQuestion 工具向你提问。

Claude 会问到你可能还没想到的方面,包括技术实现、UI/UX、边界情况与权衡取舍。发送前把 `[brief description]` 替换成你的功能描述:

> I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.
>
> Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask obvious questions, dig into the hard parts I might not have considered.
>
> Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.

(中文说明:我想构建[简要描述]。用 AskUserQuestion 工具详细面试我。问技术实现、UI/UX、边界情况、顾虑与权衡;不要问显而易见的问题,深挖我可能没考虑到的难点;一直问到覆盖全部,然后把完整规格写入 SPEC.md。)

规格完成后,开一个全新会话去执行它。新会话拥有专注于实现的干净上下文,而且你有一份可引用的书面规格。

最有用的规格是自包含的:点名涉及的文件与接口、声明哪些不在范围内、并以一个证明功能可用的端到端验证步骤收尾。把时间花在把规格写精确上,比花在盯着实现过程上回报更高。

## 管理你的会话

对话是持久且可回退的。要善用这一点!

### 尽早、频繁纠偏

一发现 Claude 跑偏就立刻纠正。

最好的结果来自紧密的反馈循环。虽然 Claude 偶尔能一次完美解决问题,但快速纠偏通常能更快产出更好的方案。

- `Esc`:按 Esc 可在动作进行中打断 Claude。上下文会保留,你可以重新指派方向。
- `Esc + Esc` 或 `/rewind`:按两次 Esc 或运行 `/rewind` 打开回退菜单,恢复之前的对话与代码状态,或从选中消息开始做摘要。
- "Undo that":让 Claude 撤销它的改动。
- `/clear`:在不相关的任务之间重置上下文。塞满无关内容的长会话会降低性能。

如果同一问题上你已纠正 Claude 超过两次,说明上下文已被失败的尝试污染。运行 `/clear`,带着你学到的经验、用更具体的提示词重新开始。一个带着更好提示词的干净会话,几乎总是胜过一个积累了层层纠正的长会话。

### 积极管理上下文

在不相关的任务之间运行 `/clear` 重置上下文。

接近上下文上限时,Claude Code 会自动压缩(compact)对话历史,在保留重要代码与决策的同时释放空间。

长会话中,Claude 的上下文窗口可能被无关对话、文件内容与命令填满,这会降低性能,有时还会让 Claude 分心。

- 在任务之间频繁使用 `/clear`,彻底重置上下文窗口。
- 自动压缩触发时,Claude 会摘要最重要的内容,包括代码模式、文件状态与关键决策。
- 想要更多控制,运行 `/compact <instructions>`,例如 `/compact Focus on the API changes`(聚焦 API 改动)。
- 只想压缩对话的一部分时,用 `Esc + Esc` 或 `/rewind` 选中某个消息检查点,选择 "Summarize from here"(从这里开始摘要,压缩其后、保留之前的上下文)或 "Summarize up to here"(摘要到此处,压缩之前、保留最近的完整内容)。
- 在 CLAUDE.md 中自定义压缩行为,比如写上 "When compacting, always preserve the full list of modified files and any test commands"(压缩时始终保留已修改文件完整清单与测试命令),确保关键上下文在摘要中幸存。
- 对不需要留在上下文里的问题,用 `/btw`。答案永远不会进入对话历史,查个细节也不会撑大上下文。

### 用子智能体做调查

用 "use subagents to investigate X" 把研究工作委托出去。它们在独立上下文中探索,让你的主对话保持干净、专注实现。

既然上下文是根本约束,就用子智能体把调查研究挡在主上下文之外。Claude 研究一个代码库时会读大量文件,全部消耗你的上下文。子智能体在独立的上下文窗口中运行,只返回摘要报告:

> Use subagents to investigate how our authentication system handles token refresh, and whether we have any existing OAuth utilities I should reuse.

(中文说明:用子智能体调查我们的认证系统如何处理 token 刷新,以及是否已有可复用的 OAuth 工具。)

在 Claude 完成实现后,也可以用子智能体做验证,见下文"添加对抗性审查步骤"。

### 用检查点回退

你发出的每一个开启新回合的提示都会创建一个检查点(checkpoint)。你可以把对话、代码或两者一起恢复到任何之前的检查点。

Claude 会在每次改动前自动对文件做快照,因此检查点能够恢复。双击 Esc 或运行 `/rewind` 打开回退菜单:可以只恢复对话、只恢复代码、两者都恢复,或从选中消息开始摘要。细节见 Checkpointing 文档。

你不必步步为营地规划,可以放手让 Claude 尝试有风险的做法;不行就回退,换一条路。检查点随对话一起保存,所以你可以关掉终端、之后再恢复会话,依然能回退。

检查点只追踪通过 Claude 文件编辑工具做出的改动,通过 Bash 命令或外部进程产生的改动不会被捕获。它不能替代 git。

### 恢复对话

用 `/rename` 给会话命名,把它们当成分支对待:每条工作流都有自己的持久上下文。

Claude Code 在本地保存对话,因此跨多次坐席的任务不必重新交代背景。运行 `claude --continue` 从上次中断处继续,或 `claude --resume` 从列表中选择。给会话起描述性名字(如 `oauth-migration`),方便日后查找。完整的恢复、分支与命名控制参见 Manage sessions。

## 自动化与规模化

当你用一个 Claude 已经得心应手,就可以用并行会话、非交互模式与扇出模式成倍放大产出。

### 运行非交互模式

在 CI、pre-commit hook 或脚本中使用 `claude -p "prompt"`。加上 `--output-format stream-json --verbose` 可获得流式 JSON 输出。

`claude -p "your prompt"` 让 Claude 以非交互方式运行,不进入交互式提示。除非传 `--no-session-persistence`,运行仍会创建可恢复的会话。非交互模式是你把 Claude 集成进 CI 流水线、pre-commit hook 或任何自动化工作流的方式。输出格式支持程序化解析:纯文本、JSON 或流式 JSON。

```
# One-off queries —— 一次性查询
claude -p "Explain what this project does"

# Structured output for scripts —— 供脚本使用的结构化输出
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing —— 实时处理的流式输出
claude -p "Analyze this log file" --output-format stream-json --verbose
```

(中文说明:第一条打印纯文本;`json` 格式返回单个含 `result` 字段的 JSON 对象;`stream-json` 格式逐行打印 JSON 对象,以一个 init 事件开头。)

### 运行多个 Claude 会话

并行运行多个 Claude 会话,可以加速开发、做隔离实验或启动复杂工作流。

根据你愿意亲自做多少协调,选择合适的并行方式,并在会话之间需要传递结论时加上消息机制:

- **Worktrees**:在隔离的 git 检出中运行多个 CLI 会话,编辑互不冲突。
- **跨会话消息(cross-session messaging)**:让你自己启动的会话互相传递发现。
- **桌面应用**:可视化管理多个本地会话,可选让每个会话独占一个 worktree。
- **Claude Code on the web**:在云端、默认由 Anthropic 管理的基础设施上运行会话。
- **Agent view**(研究预览):运行 `claude agents` 派发在后台持续运行的会话,并在一个界面中统览。
- **Agent teams**(实验性,默认关闭):带共享任务、消息与 team lead 的多会话自动协调。

除了并行做事,多会话还能支撑以质量为导向的工作流。新鲜上下文能改善代码审查,因为 Claude 不会偏袒自己刚写的代码。例如 Writer/Reviewer 模式:

| 会话 A(Writer) | 会话 B(Reviewer) |
| --- | --- |
| Implement a rate limiter for our API endpoints(为 API 端点实现限流器) | Review the rate limiter implementation in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions, and consistency with our existing middleware patterns.(审查限流器实现,找边界情况、竞态条件,检查与现有中间件模式的一致性) |
| Here's the review feedback: [Session B output]. Address these issues.(这是审查反馈,处理这些问题) | |

测试也可以如法炮制:让一个 Claude 写测试,另一个写通过测试的代码。

### 跨文件扇出

循环遍历任务,对每个任务调用 `claude -p`。批量操作时用 `--allowedTools` 限定权限。

对大规模迁移或分析,可以把工作分摊到多个并行 Claude 调用上。在 git 仓库中,运行 `/batch <instruction>` 让 Claude 把改动拆分给 5 到 30 个子智能体,每个子智能体在自己的 worktree 中工作并开一个 PR。想用你自己的脚本驱动扇出,可以循环调用 `claude -p`:

**1. 生成任务清单**

让 Claude 把需要迁移的文件列表写入文件,供下一步的循环读取,提示词如:"list all 2,000 Python files that need migrating and save the list to files.txt"。

**2. 写一个遍历清单的脚本**

```bash
for file in $(cat files.txt); do
  claude -p "Migrate $file from Python 2 to Python 3. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

**3. 先在几个文件上测试,再全量运行**

根据前 2-3 个文件上暴露的问题打磨提示词,然后跑全量。`--allowedTools` 限制 Claude 能做什么——在无人值守运行时这很关键。

也可以把 Claude 集成进既有的数据/处理流水线:

```bash
claude -p "<your prompt>" --output-format json | your_command
```

开发调试时用 `--verbose`,生产环境关掉。

### 用 auto 模式自主运行

要 uninterrupted 执行、同时保留后台安全检查,使用 auto 模式。一个分类器模型会在命令运行前审查,拦截权限升级、未知基础设施与恶意内容驱动的动作,同时让例行工作免提示通过。

```bash
claude --permission-mode auto -p "fix all lint errors"
```

当分类器在带 `-p` 标志的非交互运行中反复拦截动作时,Claude Code 并不会停止运行;具体会发生什么及阈值,参见 auto 模式的回退机制说明。

### 添加对抗性审查步骤

在把任务当作完成之前,让一个子智能体在全新上下文中审查 diff 并报告缺口。

Claude 无人值守工作的时间越长,在认定工作完成前做一次独立检查就越重要。运行在全新子智能体上下文中的审查者只看到 diff 与你给的标准,看不到产生改动的那套推理,因此它能按自己的标准评判结果。

做正确性检查,可直接运行内置的 `/code-review` 技能:它会在全新子智能体中审查当前 diff 的 bug,并把发现带回会话。要按你的计划来检查 diff,就自己写审查提示词——点名要检查的工作、对照的计划、什么算一条 finding:

> Use a subagent to review the rate limiter diff against PLAN.md. Check that every requirement is implemented, the listed edge cases have tests, and nothing outside the task's scope changed. Report gaps, not style preferences.

(中文说明:用子智能体对照 PLAN.md 审查限流器的 diff。检查每条需求都已实现、列出的边界情况都有测试、任务范围之外没有改动。报告缺口,不报告风格偏好。)

因为审查者以子智能体运行,实现会话能直接收到缺口列表、修复并复审,无需你在窗口间搬运结论。

被要求找缺口的审查者通常总会报出一些,哪怕工作本身是可靠的——因为这就是它被要求做的事。追逐每条 finding 会导致过度工程:多余的抽象层、防御性代码、为不可能场景写的测试。告诉审查者只标记影响正确性或既定需求的缺口,其余视为可选。

## 避免常见的失败模式

以下是常见错误,早识别能省时间:

- **大杂烩会话(the kitchen sink session)**:你从一个任务开始,中途问了个不相关的问题,然后又回到第一个任务。上下文里塞满无关信息。**修法**:不相关任务之间 `/clear`。
- **反复纠正**:Claude 做错了,你纠正,还是错,再纠正。上下文被失败尝试污染。**修法**:两次纠正失败后,`/clear` 并结合所学写一个更好的初始提示词。
- **过度膨胀的 CLAUDE.md**:CLAUDE.md 太长时,Claude 会忽略其中一半——重要规则淹没在噪音里。**修法**:狠心修剪。如果某条指令删掉后 Claude 照样做对,就删掉或转成 hook。
- **先信任后验证的空档(the trust-then-verify gap)**:Claude 产出一个看起来合理、但没处理边界情况的实现。**修法**:永远提供验证手段(测试、脚本、截图)。无法验证的东西就不要上线。
- **无限探索**:你让 Claude"调查一下"某事却没限定范围。Claude 读了几百个文件,填满了上下文。**修法**:把调查范围收窄,或改用子智能体,别让探索消耗主上下文。

## 培养你的直觉

本指南中的模式并非金科玉律。它们是一般情况下行之有效的起点,未必对每种情况都最优。

有时你**应当**让上下文积累——因为你正深陷一个复杂问题,历史是有价值的。有时你应当跳过规划,让 Claude 自己想办法——因为任务是探索性的。有时模糊的提示词恰恰是对的——因为你想先看 Claude 如何理解这个问题,再去约束它。

留意什么有效。当 Claude 产出优秀结果时,回顾你做了什么:提示词结构、你提供的上下文、你所在的模式。当 Claude 卡壳时,问问为什么:上下文太吵?提示词太模糊?任务太大而不适合一轮完成?

假以时日,你会形成任何指南都无法囊括的直觉。你会知道何时该具体、何时该开放,何时该规划、何时该探索,何时该清空上下文、何时该让它积累。

## 相关资源

- **How Claude Code works**:智能体循环、工具与上下文管理
- **Extend Claude Code**:skills、hooks、MCP、子智能体与插件
- **Common workflows**:调试、测试、PR 等的分步配方
- **CLAUDE.md**:存放项目约定与持久上下文

## 要点速览

- 一条总纲:Claude 的上下文窗口填得快、性能随填充而降,上下文是最需要管理的资源;几乎所有最佳实践都由此推出。
- 给 Claude 一个可自运行的验证检查(测试、构建、截图),把"你当验证环节"变成"闭环自动收敛";可用 `/goal`、Stop hook、验证子智能体逐级加强约束强度。
- 推荐四阶段工作流:探索(plan mode)→ 规划 → 实现 → 提交;一句话能描述 diff 的小任务可跳过规划。
- 提示词要具体:点名文件、说明约束、指向代码库中的范例模式;`@` 引用文件、贴图、给 URL、管道输入都是喂上下文的高效方式。
- 环境配置是复利投资:精炼的 CLAUDE.md(只写删掉会导致犯错的内容)、权限白名单与沙箱、`gh` 等 CLI 工具、MCP 服务器、hooks(确定性)、skills(按需知识)、子智能体(隔离上下文)各有分工。
- 大功能先让 Claude 用 AskUserQuestion"面试"你并写出自包含的 SPEC.md,再开新会话执行,规格精度比盯梢更值钱。
- 会话管理:早纠偏(Esc/rewind/Undo)、两纠不过就 `/clear` 重开、自动压缩与 `/compact` 定向摘要、检查点让 risky 尝试零成本回退、`/rename` 把会话当分支用。
- 规模化:`claude -p` 非交互模式接 CI 与脚本,worktrees/多会话做 Writer-Reviewer 与测试先行,`/batch` 或 shell 循环做 5-30 个子智能体的文件级扇出,auto 模式用分类器兜底安全。
- 无人值守前加一道对抗性审查:全新上下文的子智能体只看 diff 与标准来挑缺口,但要求它只报影响正确性的问题,避免过度工程。
- 警惕五大失败模式:大杂烩会话、反复纠正、CLAUDE.md 过长、信任-验证空档、无限探索;对应的修法几乎都是 `/clear`、修剪与限定范围。
