---
title: "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines"
title_zh: DSPy：将声明式语言模型调用编译为自我改进的流水线
authors: Omar Khattab et al.
venue: "ICLR 2024 · Stanford / UC Berkeley / CMU 等"
kind: paper
importance: must
tags: DSPy, 提示优化, LM 流水线, 声明式编程, 自举, 框架与编排
summary: DSPy 把 LM 流水线抽象为文本变换图，用"签名 + 模块 + 优化器"替代手写提示模板，自动编译出超越人工提示工程的系统。
---

## 导读

本文是第 3 周"框架与编排"专题的核心论文。当时 LM 流水线（LangChain、LlamaIndex 等）普遍依赖手写的"提示模板"——一大段试错凑出的长字符串。论文视之为"手工调权重"式的脆弱做法：换个模型或领域就可能失效。DSPy 把这些技术"编程化"：像 PyTorch 之于神经网络，为 LM 流水线提供可组合的抽象与自动优化器。

DSPy 的三大抽象是：**签名（signatures）**——用自然语言类型化的声明描述一次文本变换的输入输出；**模块（modules）**——把 Chain of Thought、ReAct 等提示技术改造成可配签名的参数化组件；**提示优化器（teleprompters）**——把"提示"当作优化问题，通过自举（bootstrapping）示教例证自动编译整个流水线。两个案例研究（GSM8K 数学题、HotPotQA 多跳问答）显示：几行 DSPy 代码在数分钟编译后，GPT-3.5 与 llama2-13b-chat 上的流水线普遍比标准少样本提示高出 25% 与 65% 以上，甚至能让 770M 参数的 T5-Large 与依赖专家提示链的 GPT-3.5 方案掰手腕。理解它就抓住了 Agent 工程从手工提示走向系统化优化的转向。

## 论文精读

### 摘要（Abstract，全译）

机器学习社区正在快速探索为语言模型（LM）编写提示的技术，以及把它们堆叠成解决复杂任务的流水线。遗憾的是，现有的 LM 流水线通常用硬编码的"提示模板"实现，即通过反复试错发现的长字符串。为了给开发和优化 LM 流水线提供更系统化的路径，我们提出 DSPy——一个把 LM 流水线抽象为**文本变换图（text transformation graphs）**的编程模型，即通过声明式模块调用 LM 的命令式计算图。DSPy 模块是参数化的，意味着它们可以（通过创建和收集示教例证/demonstrations 来）学习如何组合运用提示、微调、增强与推理技术。我们设计了一个编译器来优化任意 DSPy 流水线以最大化给定指标。我们进行了两个案例研究，表明简洁的 DSPy 程序即可表达并优化复杂的 LM 流水线：推理数学应用题、完成多跳检索、回答复杂问题、控制智能体循环。在几分钟的编译之内，几行 DSPy 代码即可让 GPT-3.5 与 llama2-13b-chat 自举出超越标准少样本提示（分别普遍高出 25% 与 65% 以上）以及专家编写示教例证的流水线（分别高出至多 5–46% 与 16–40%）的系统。此外，编译到开放且相对较小的 LM（如 770M 参数的 T5 与 llama2-13b-chat）上的 DSPy 程序，可与依赖专家编写提示链、调用专有 GPT-3.5 的方案相竞争。DSPy 已开源于 https://github.com/stanfordnlp/dspy。

### 1. 引言（Introduction）

LM 让研究者能以更高的抽象层级、更低的数据要求构建 NLP 系统，催生了爆炸式增长的"提示"与轻量微调技术：适配新任务、激发系统化推理（思维链、自一致性等）、用检索源或工具增强模型。这些技术大多被孤立地研究，而社区日益增长的兴趣是把复杂任务分解为多次 LM 调用的多阶段流水线与智能体。问题在于：LM 对提示方式高度敏感，这在多次调用必须有效协作的流水线中被急剧放大。结果，现有流水线与主流开发框架中的 LM 调用普遍由手工试错得到的硬编码提示模板实现——作者认为这虽然普遍，却脆弱且不可扩展。

DSPy 的解法是把构建 LM 流水线从操纵自由字符串推向编程：像神经网络领域达成共识的抽象那样——(1) 通用层可模块化地组合成任意复杂架构；(2) 模型权重靠优化器训练而非手工调整。具体地，DSPy 先把基于字符串的提示技术（包括思维链、ReAct 这类复杂且任务相关的技术）翻译为携带自然语言类型化签名的声明式模块；模块是任务自适应组件，如同神经网络的层；每个模块被参数化，可在流水线内迭代自举有用的示教例证来学习期望行为。受 PyTorch 直接启发，模块以 define-by-run 的命令式计算图使用：先声明所需模块，再在任意逻辑控制流（if、for、异常等）中调用它们连接成流水线。

**DSPy 编译器**输入程序、少量带可选标签的训练输入和一个验证指标，在输入上模拟程序的多份版本、自举各模块的执行轨迹（traces）用于自我改进，再用它们构造高质量少样本提示或微调流水线中的小型 LM。优化由 teleprompters（提示优化器）执行——这是决定各模块如何从数据中学习的通用优化策略；编译器由此自动把声明式模块映射为提示、微调、推理与增强的高质量组合。

两个案例研究覆盖数学应用题（GSM8K）与多跳问答（HotPotQA），涉及思维链、多链反思、多跳检索、检索增强问答与智能体循环。论文的总体主张是：这是第一个把提示技术转化为参数化声明式模块、并配以通用优化策略编译器编译任意模块流水线的编程模型；无需手写提示、数分钟到数十分钟的编译内，模块组合能把 GPT-3.5 上的简单程序从 33% 提到 82%、从 32% 提到 46%，把 llama2-13b-chat 上从 9% 提到 47%、从 22% 提到 41%。（DSPy 读作 dee-ess-pie，是早期 Demonstrate–Search–Predict 框架的第二代；teleprompter 之名取"把提示任务抽象化、自动化、远程化，无需人工干预"之意。）

### 2. 相关工作（Related Work）

DSPy 借鉴 Torch、Theano、Chainer 在深度学习中提供强大抽象的角色，希望为作者所称的**基础模型编程（foundation model programming）**提供概念框架；借用可微编程的思想但应用于 LM 调用而非神经网络，语法元素取自 PyTorch。上下文学习（in-context learning）是关键机制，配合指令微调可经提示激发复杂行为；以往需要任务专用或人工启发式的弱监督，如今可由 LM 完成。工具调用催生了连接检索模型与 API 的流水线，LangChain、Semantic Kernel、LlamaIndex 等工具包提供预打包的链与智能体，但它们都通过手写提示模板表达任务行为——正是 DSPy 要解决的核心难题（附录 B 给出定量对比：2023 年 9 月，LangChain 代码库中有 50 条超过 1000 字符的字符串（多为提示）、12 个 `prompts.py` 与 42 个 `prompt.py` 文件；DSPy 当时不含任何一条手写的任务示教提示）。另一线工作用离散优化或 RL 搜索单次 LM 调用的有效提示；DSPy 将其推广为从高级声明式签名优化任意流水线，可结合交叉验证、RL/反馈式技术或贝叶斯超参优化。

### 3. DSPy 编程模型

DSPy 把 LM 视为文本生成的抽象设备，在其上优化任意计算图。程序用 Python 表达：接收任务输入（问题、待摘要论文等），经若干步骤返回输出。DSPy 贡献三大抽象：签名抽象模块的输入/输出行为；模块取代现有手工提示技术、可组合成任意流水线；提示优化器优化流水线中全部模块以最大化某指标。

#### 3.1 自然语言签名：抽象提示与微调

DSPy 程序不用自由字符串提示，而用**签名**分配工作。签名是对函数的**自然语言类型化声明**：一段简短的声明式规格，告诉 DSPy 这个文本变换需要做什么（如"输入问题、返回答案"），而不是具体某个 LM 应被怎样提示。形式上，签名是输入字段与输出字段（外加可选指令）的元组；字段由字段名和可选元数据构成，字段的角色由 DSPy 根据字段名推断——编译器会用上下文学习区分 `question` 与 `answer` 的用法并迭代细化。签名相对提示有两大好处：可被编译为自适应流水线的提示或微调（主要通过自举示教例证）；并接管结构化格式化与解析，减少用户程序中脆弱的字符串操作。实践中有简写记法，如：

```python
qa = dspy.Predict("question -> answer")
qa(question="Where is Guaraní spoken?")
# Out: Prediction(answer='Guaraní is spoken mainly in South America.')
```

`english document -> french translation` 这样的签名会被 DSPy 展开为英译法的指令；需要更明确的约束时可用 Python 类写出显式签名（附录 A：字段可带描述与数据类型，输出字段可声明 bool/int/list/dict 等，尚在进行中）。

#### 3.2 参数化与模板化的模块：抽象提示技术

签名像类型签名一样只定义接口；使用签名要声明一个持有该签名的**模块**。核心模块 `Predict`（伪码见附录 D.1）内部保存签名、可选的模块级 LM 覆盖、以及初始为空的示教例证列表；像 PyTorch 层一样可调用：接收签名输入字段的关键字参数、格式化提示（含示教例证）、调用 LM、解析输出字段；在编译模式下还会透明地记录输入/输出轨迹，供提示优化器自举示教例证。

内置模块还有 `ChainOfThought`、`ProgramOfThought`、`MultiChainComparison`、`ReAct` 等，可互换地实现任一签名——把 `Predict` 换成 `ChainOfThought` 即得到先分步思考再给出输出的系统。重要的是这些模块都只需几行代码：在用户签名上做扩展、然后一次或多次调用 `Predict`。`ChainOfThought` 的实现只是在输出字段前加上前缀为 "Reasoning: Let's think step by step." 的 rationale 字段，再交给 `Predict`——对比附录 C 中从论文与流行库抄来的数千字符手写推理提示，可见抽象层级差异。

**参数化**是 DSPy 的独特之处：任何实现某签名的 LM 调用需要指定 (1) 调用哪个 LM；(2) 提示指令与各字段前缀；(3) 最关键的——用作少样本提示（冻结 LM）或训练数据（微调）的**示教例证**。DSPy 聚焦于自动生成与选择有用的示教例证。**工具**方面，检索模型经 `dspy.Retrieve` 模块支持（内置 ColBERTv2、Pyserini、Pinecone），另有实验性的 `dspy.SQL` 与沙箱执行的 `dspy.PythonInterpreter`。**程序**：模块在 define-by-run 接口中组成任意流水线——初始化时声明模块（便于 DSPy 跟踪以便优化），在 `forward` 方法中以任意代码调用。论文给出一个完整但极简的 RAG 系统：

```python
class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)
```

若把签名换成 `"context, question -> search query"`，同一个程序就变成生成搜索查询的系统——签名与模块解耦的直观体现。

#### 3.3 提示优化器：为任意流水线自动化提示

编译 DSPy 程序时通常调用一个 **teleprompter**：一个接收程序、训练集与指标并返回优化后新程序的优化器。训练集可以很小（少量例子即可，更大则优化更强）；训练例子可以不完整——只需要输入值，各流水线步骤的标签并非必需，通常假设（至多）只有程序最终输出有标签。这种标签效率对模块化至关重要：搭一条新流水线只需重新编译新代码，无需为新流水线标注数据。指标可以是精确匹配（EM）、F1 这类简单概念，也可以是平衡多重考量的完整 DSPy 程序（例如要求答案既是正确的、又是某段检索段落的子串）。

```python
teleprompter = dspy.BootstrapFewShot(metric=dspy.evaluate.answer_exact_match)
compiled_rag = teleprompter.compile(RAG(), trainset=qa_trainset)
```

`BootstrapFewShot` 会在训练例上模拟 RAG，收集那些整体通过指标与签名约束的各模块输入—输出示教例证。提示优化器可通过指定 **teacher 程序**来组合：昂贵的教师程序（如大 LM 集成）监督廉价的学生程序（如微调 Flan-T5-large），且学生的训练集可以完全无标签：

```python
finetuning_teleprompter = BootstrapFinetune(metric=dspy.evaluate.answer_passage_match)
compiled_rag_via_finetune = finetuning_teleprompter.compile(
    RAG(), teacher=compiled_rag, trainset=unlabeled_questions, target='google/flan-t5-large')
```

### 4. DSPy 编译器

编译依赖提示优化器，经提示或微调（二者在 DSPy 中被统一）改进模块质量（或成本）。典型优化器经历三个阶段：

**阶段 1：候选生成。** 编译器先（递归地）找出程序中所有唯一的 `Predict` 模块（predictor，包括嵌套在其他模块下的），为每个 predictor 的参数生成候选值：指令、字段描述、以及最重要的示教例证（输入—输出样例对）。本版 DSPy 聚焦示教例证，发现类似拒绝采样的简单做法即可自举出高效的多阶段系统。以 `BootstrapFewShot`（附录 E.1 伪码）为例：它在训练输入上（可多次、高温地）模拟 teacher 程序（未设则用零样本版本），编译模式下以线程安全方式全程跟踪多阶段轨迹；用指标过滤出整体通过的多阶段轨迹，丢弃坏例、把好例留作潜在示教例证（这些设计均在用户掌控下）。LM 虽高度不可靠，但作者发现它们搜索多阶段解空间相当高效：分解良好的程序通常能找到至少几个通过签名与指标约束的训练例，从而支持迭代自举。

**阶段 2：参数优化。** 此时每个参数有离散候选集，可套用任意超参调优算法（随机搜索、HyperOpt/Optuna 的 TPE 等；`BootstrapFewShotWithRandomSearch` 与 `BootstrapFewShotWithOptuna` 的简化伪码见附录 E.2/E.3）。另一类优化是 `BootstrapFinetune`：用示教例证更新各 predictor 的 LM 权重，随后模块的 LM 参数指向新权重。通常在训练集上交叉验证或在验证集上按指标优化平均质量；依据指标性质，各阶段完全无标签也适用。

**阶段 3：高阶程序优化。** 修改程序控制流，最简单的是**集成（ensemble）**：自举同一程序的多个副本，替换为并行运行全部副本、再用自定义函数（如多数投票）归约预测的新程序。未来此阶段还可容纳测试时自举与自动回溯类逻辑。

### 5. 评估目标

编程框架可沿计算效率、开发效率、直觉性等维度评估，本文聚焦当下最紧迫的问题：**手写的任务专用提示在系统性能中的角色**。三个假设：H1——用简洁良定义的模块替代手写提示串，不损失质量与表达力；H2——模块参数化、把提示当优化问题，使 DSPy 更好地适配不同 LM，可能超过专家提示；H3——由此获得的模块化能更充分地探索具备有用性能特征或契合细致指标的复杂流水线。作者希望评估范式从"不同 LM 在 GSM8K 上谁强"这种欠规定的问题，转向"在 GSM8K 上用程序 P、以策略 S 编译后表现如何"这种定义良好、可复现的问法。

### 6. 案例研究一：GSM8K 数学应用题

设置：从官方训练集抽 200 对做训练、300 对做开发，最终在 1.3k 官方测试集上评估；按惯例只评输出中最后出现的数值是否正确。

**程序**：三个程序全部由通用模块构成、无一为数学或特定 LM 定制——`vanilla`（一步 `dspy.Predict("question -> answer")`）、`CoT`（`dspy.ChainOfThought(...)`）、`reflection`（`ThoughtReflection`：先用 `ChainOfThought(..., n=5)` 采样 5 条推理链，再交给泛化自 Yoran et al. 的 `MultiChainComparison` 并行比较、综合五次尝试的模式生成新答案，共几行代码）。

**编译策略**：`LabeledFewShot(k=8)`（从带标签训练集随机抽 8 个示教例，随机采样结果取 3–5 次平均）；`BootstrapFewShotWithRandomSearch`（为训练例生成示教链，以随机搜索优化示教例选择）；嵌套自举 `bootstrap×2`（用优化后的 bootstrap 程序作 teacher 再自举一次，对零样本起点弱的程序尤其有用）；以及对候选程序 top-7 做多数投票的 `Ensemble`。GSM8K 自带人工推理链，作者另评估把人工推理串并入训练集的 `trainset human CoT` 变体。编译一般在分钟到数十分钟量级（较贵设置也只是把程序跑几千次，如 10–20 轮 × 150–300 个验证例，且可并行）。

**结果**（准确率，Dev/Test）：

| 程序（编译） | GPT-3.5 Dev | GPT-3.5 Test | Llama2-13b-chat Dev | Test |
|---|---|---|---|---|
| vanilla（none，零样本） | 24.0 | 25.2 | 7.0 | 9.4 |
| vanilla（bootstrap×2） | 64.7 | 61.7 | 37.3 | 36.5 |
| CoT（none） | 50.0 | - | 26.7 | - |
| CoT（fewshot +human CoT） | 78.6 | 72.4 | 34.3 | 33.7 |
| CoT（bootstrap） | 80.3 | 72.9 | 43.3 | - |
| CoT（bootstrap + ensemble） | 88.3 | 81.6 | 43.7 | - |
| reflection（none） | 65.0 | - | 36.7 | - |
| reflection（bootstrap） | 83.0 | 76.0 | 44.3 | 40.2 |
| reflection（bootstrap + ensemble） | 86.7 | - | 49.0 | 46.9 |

要点：直接预测答案时两个 LM 都很挣扎（GPT-3.5 24.0、llama2 7.0）；`vanilla` 经 bootstrap 与 bootstrap×2 大幅提升——检查自举出的提示（附录 F）发现，它允许 LM 先利用 answer 字段做推理，因为指标只取最终数值。`CoT` 上专家人工推理链（+human CoT）确实有大帮助，但 **bootstrap 可匹配甚至超过它**，支持了"减少手写提示需求"的假设；`reflection` 程序只多几行却是最大赢家。总体而言，表中所有程序都由 2–4 个模块与优化器组合而成：在新范式下，是**组合正确的通用模块、而非操纵提示字符串**，把各 LM 从 4–20% 的准确率提升到 49–88%。与文献非正式对比：text-davinci-002 报告 48%、codex 手工 CoT 59.4%、自动 CoT 62.8%；PaLM-540B CoT 57%、加自一致性 74%；llama2 官方 13b/34b/70b 分别为 28.7%/42.2%/56.8%——本文 13b 程序在不用人工推理链的情况下即可与其 34b 结果竞争；gpt-3.5-turbo CoT 报告 80.8%；GPT-4 达 92%（但官方注明 GPT-4 预训练见过 GSM8K 训练集子集）。

### 7. 案例研究二：HotPotQA 复杂问答

设置：多跳问答，HotPotQA 开放域"fullwiki"设定；检索用官方维基百科 2017"abstracts"转储的搜索索引，由 ColBERTv2 检索器执行。官方测试集隐藏，故把官方验证集留作测试（抽 1000 例），训练集按 70%/30% 分为训练/验证，并只保留"hard"标注样本；训练与开发各取 200/300 例。

**程序**：（1）`vanilla`——"question -> answer"签名足够通用；（2）基线 RAG 程序（§3.2 的两模块版本），作者直言它在此任务表现不佳，从而引出两个多跳程序；（3）`react`——多步工具使用智能体，在 DSPy 中是内置模块：`dspy.ReAct("question -> answer", tools=[dspy.Retrieve(k=1)], max_iters=5)`；（4）`multihop`——模拟 Baleen 与 IRRR 信息流、与 IRCoT 相似的多跳程序：两跳循环，每跳用 `ChainOfThought("context, question -> search_query")` 生成查询、检索并累加上下文，最后作答。

**编译**：沿用 GSM8K 的编译器并做两种组合——ReAct 用"先 bootstrap、再以其为起点的 BootstrapFewShotWithRandomSearch"；multihop 另加微调：`BootstrapFinetune(metric=answer_exact_match).compile(program, teacher=bootstrap, trainset=trainset, target='t5-large')`。

**结果**（答案 EM = Ans，段落对检索准确率 = Psg）：

| 程序（编译） | GPT-3.5 Dev Ans | GPT-3.5 Test Ans | Llama2 Dev Ans | Llama2 Test Ans |
|---|---|---|---|---|
| vanilla（fewshot） | 34.3 | 31.5 | 27.5 | 21.8 |
| CoT RAG（fewshot） | 36.4 (Psg 36.0) | 29.8 (34.4) | 34.5 (36.0) | 28.0 (34.4) |
| CoT RAG（bootstrap） | 42.3 (36.0) | - | 38.3 (36.0) | 32.9 (34.4) |
| react（none） | 20.3 | - | 20.0 | - |
| react（+human r，专家提示） | 33.0 | - | 28.3 | - |
| react（bootstrap×2） | 39.0 | - | 40.0 | - |
| multihop（fewshot） | 36.9 (38.3) | 31.2 (40.8) | 34.7 (32.0) | 31.3 (30.8) |
| **multihop（bootstrap）** | **48.7 (47.0)** | 39.6 (43.8) | 42.0 (48.3) | 36.4 (43.5) |
| multihop（bootstrap + ensemble） | 54.7 | 45.6* | 50.0 | 41.0 |

（*因成本只评估测试集的 50%。）解读：CoT RAG 的答案 EM 提升明显，但完全依赖 ColBERTv2 直接从原问题检索，段落召回受限；react 与 multihop 通过多"跳"迭代生成检索查询解决这一问题，简单的 multihop 表现最好。bootstrap（及 bootstrap×2）在两个 LM 上都能超过 fewshot（multihop 情形）与专家人工推理（react 情形，专家提示改编自 Yao et al. 并适配本文检索设置）；更重要的是，**仅靠编译就能让 llama2-13b-chat 与 GPT-3.5 竞争**。微调方面，`multihop_t5` 产出 T5-Large（770M 参数）模型：仅用 200 个带标签示例与 800 个无标签示例，dev 上答案 EM 39.3%、段落准确率 46.0%；考虑到体量与本地可得性，其推理成本比 GPT-3.5 这类专有 LM 低若干数量级（teacher 为两个 llama2-13b-chat multihop 的并集集成）。与文献对比（方法学差异较大、仅供参考）：CoT 提示 25.2% EM；PaLM-62B "recite-and-answer" 26.5%；PaLM-540B 自一致性 33.8% EM / 44.6% F1；ReAct + Wikipedia 搜索工具在 PaLM-540B 上 27.4%、text-davinci-002 上 30.8%、加自一致性 CoT 推至 35.1%；code-davinci-002 流水线在 500 例样本上报 49%。

### 8. 结论与附录要点

**结论**：本文提出用于以预训练 LM 与工具流水线构建 AI 系统的编程模型 DSPy 及其三大新概念（签名、模块、提示优化器），并在两个迥异的案例研究中表明它支持快速开发出使用相对较小 LM 的高效系统。框架开源近一年间，大量程序被 DSPy 编译为高质量系统，任务从信息抽取到低资源合成数据生成（受篇幅所限未在本文受控实验中报告）。作者的核心论点：过去 2–3 年上下文学习已被证明是变革性的，但这一新兴范式的真正表达力在于构建**精巧的文本变换图**——让可组合模块与优化器（teleprompters）协同，以更系统、更可靠的方式利用 LM。

**附录要点**：附录 B 对比 LangChain/LlamaIndex：二者聚焦为应用开发者提供预打包组件与链（各数据库连接、记忆实现等），与 DSPy 的核心可组合算子（签名/模块/优化器）定位不同；定量上 LangChain 有 50 条超 1000 字符的提示串（PAL 链模板长 3982 字符、含 8 道数学题示教；面向 Oracle/GoogleSQL/DuckDB 等各写一份 SQL 提示，平均 1058 字符），而 DSPy 一条手写任务示教都没有。附录 D/E 给出 Predict、ChainOfThought 与三个提示优化器的简化伪码——如 BootstrapFewShotWithRandomSearch 以 16 轮随机种子分别自举候选程序、在验证集上评分后取最优。附录 F 展示 DSPy 自动生成的真实提示（GSM8K 与 HotPotQA），其格式与示教例证的选择完全由 llama2-13b-chat 自举产生。

## 要点速览

- 问题定位：主流 LM 流水线与框架依赖手工试错的长提示模板，脆弱且不可迁移——论文将其类比为"手调分类器权重"。
- 三大抽象：签名（自然语言类型化的输入/输出声明，如 `question -> answer`）抽象提示；模块（Predict、ChainOfThought、ReAct、MultiChainComparison、Retrieve 等可互换组件）抽象提示技术；teleprompter（提示优化器）把提示当作可优化参数。
- 模块参数包括：用哪个 LM、指令与字段前缀、以及最关键的示教例证（few-shot 演示或微调数据）；DSPy 聚焦自动生成与选择示教例证。
- 编译器三阶段：候选生成（模拟程序、按指标过滤出通过的多阶段轨迹作示教例证）→ 参数优化（随机搜索/Optuna 选示教例证，或 BootstrapFinetune 微调小 LM）→ 高阶优化（集成、多数投票；未来可扩展测试时自举与回溯）。
- 标签效率：通常只需最终输出的少量标签（GSM8K 用 200 例、HotPotQA 用 200 例），中间步骤标签全部自举；teacher 程序可监督无标签学生程序完成微调。
- GSM8K：编译正确的通用模块（而非提示字符串）把各 LM 从 4–20% 提升到 49–88%；GPT-3.5 的 CoT+集成达 88.3%（Dev）/81.6%（Test），llama2-13b-chat 的 reflection+集成达 49.0%/46.9%；自举示教例证还能匹配甚至超过自带的人工推理链（bootstrap 80.3 vs fewshot+human CoT 78.6）。
- HotPotQA：简单 multihop 程序（两跳查询生成 + 检索）最强，bootstrap 后 GPT-3.5 Dev 答案 EM 48.7、集成 54.7；llama2-13b-chat 集成达 Dev 50.0——编译让 13b 开源模型与 GPT-3.5 竞争。
- 仅用 200 带标签示例 + 800 无标签示例即可把 multihop 微调进 T5-Large（770M），dev 答案 EM 39.3%、段落准确率 46.0%，推理成本比专有 LM 低若干数量级。
- 与 LangChain/LlamaIndex 的分工：它们提供预打包链与工具连接（内部仍是手写提示）；DSPy 提供核心算子与自动优化——两者互补而非替代。
- 编译成本可控：一般分钟到数十分钟（几千次程序执行、可并行），使"程序 + 编译策略"成为定义良好、可复现的评估单元。
