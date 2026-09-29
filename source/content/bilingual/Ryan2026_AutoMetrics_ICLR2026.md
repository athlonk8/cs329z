---
title: "AutoMetrics: Approximate Human Judgments with Automatically Generated Evaluators"
title_zh: "AutoMetrics:用自动生成的评估器逼近人类判断"
authors: "Michael J. Ryan et al."
venue: "ICLR 2026 · Stanford University / American Express"
kind: paper
importance: recommended
tags: 自动指标合成, LLM-as-a-Judge, MetricBank, 低数据评测, 代理奖励, 评测有效性
summary: "提出 AutoMetrics 框架:以少于 100 条人类反馈为输入,自动生成并从 48 个指标的 MetricBank 中检索候选,经 PLS 回归合成与人类判断高相关(最高提升 33.4% Kendall τ)的可解释指标,并可充当代理奖励。"
---

## 导读

Zheng et al. (2023) 证明了「GPT-4 评审可以逼近人类偏好」,但留下一个实践难题:评审的 rubric 从哪里来?对旅行规划、临床病历生成这类新型主观任务,从业者手里往往只有用户点赞/点踩这类稀疏、非描述性信号,既写不出可靠的标准,也没有几千条标注去训练奖励模型。本篇正是本周主题「评测的自适应化」的代表工作:让指标本身从少量人类反馈中自动归纳出来。

AutoMetrics 的流水线只有四步——生成、检索、回归、报告:先用 LLM 批量生成候选评审准则(单准则 / rubric / 示例型 / 提示优化型),再从作者整理的 MetricBank(48 个 NLP 经典指标 + 模型卡)中检索,然后用偏最小二乘(PLS)回归把候选指标加权组合成与人类信号最相关的合成指标,最后输出带权重与相关性的可读报告。它的两个卖点直接回应课程两条主线:数据效率(约 80 条反馈即饱和)与可优化性(在 τ-Bench 上作为代理奖励,优化效果追平可验证奖励)。方法论上,论文借用心理测量学的「内容 / 准则 / 构念效度」三框架与 Sensitivity / Stability 两个新测量,为「如何评一个自动指标好不好」提供了范式,值得写自己评测的同学借鉴。

## 全文对照翻译

> **译注**:以下对照覆盖论文正文全部内容(摘要、第 1–6 节、可复现性声明、局限与致谢,原文第 1–10 页),英文原段与中文全译逐段交替,不跳段、不并段;页眉(Preprint)、页码与 arXiv 编号行从略。References 与附录 A–G 不收录,文末另有译注说明。图 1–6 以「[图 N: 英文图题] + 中文说明」收录;表 1(任务总览)、表 2(主结果)、表 3(消融)转为 markdown,数据一概保留。术语首现时给出中英对照,如指标归纳(metric induction)、准则效度(criterion validity)等。

### 摘要(Abstract)

::: en
Evaluating user-facing AI applications remains a central challenge, especially in open-ended domains such as travel planning, clinical note generation, or dialogue. The gold standard is user feedback (e.g., thumbs up/down) or behavioral signals (e.g., retention), but these are often scarce in prototypes and research projects, or too-slow to use for system optimization. We present AutoMetrics, a framework for synthesizing evaluation metrics under low-data constraints. AutoMetrics combines retrieval from MetricBank, a collection of 48 metrics we curate, with automatically generated LLM-as-a-Judge criteria informed by lightweight human feedback. These metrics are composed via regression to maximize correlation with human signal. AutoMetrics takes you from expensive measures to interpretable automatic metrics. Across 5 diverse tasks, AutoMetrics improves Kendall correlation with human ratings by up to 33.4% over LLM-as-a-Judge while requiring fewer than 100 feedback points. We show that AutoMetrics can be used as a proxy reward to equal effect as a verifiable reward. We release the full AutoMetrics toolkit and MetricBank to accelerate adaptive evaluation of LLM applications.
:::

评测面向用户的 AI 应用仍是一项核心挑战,在旅行规划、临床病历生成、对话等开放领域尤为如此。金标准是用户反馈(如点赞/点踩)或行为信号(如留存),但在原型与研究项目中它们往往稀缺,或者对系统优化而言太慢。我们提出 AutoMetrics——一个在低数据约束下合成评测指标(evaluation metric)的框架。AutoMetrics 把从 MetricBank(我们整理的 48 个指标的合集)中的检索,与由轻量人类反馈驱动的自动生成 LLM 评审(LLM-as-a-Judge)准则相结合,再通过回归将这些指标组合起来,以最大化与人类信号的相关性。AutoMetrics 带你从昂贵的度量走向可解释的自动指标。在 5 个多样任务上,AutoMetrics 相对 LLM-as-a-Judge 将与人类评分的 Kendall 相关系数最高提升 33.4%,同时只需不到 100 条反馈。我们还展示 AutoMetrics 可以用作代理奖励(proxy reward),达到与可验证奖励(verifiable reward)同等的效果。我们开源完整的 AutoMetrics 工具包与 MetricBank,以加速 LLM 应用的自适应评测。

[图 1: AutoMetrics takes you from expensive measures to interpretable automatic metrics. Here AutoMetrics generates useful metrics for evaluating LLM written product descriptions from user reviews from EvalGen (Shankar et al., 2024b). Percentages indicate relative importance of each metric derived from regression coefficients.]

图 1:AutoMetrics 从昂贵度量走向可解释的自动指标。图中以 EvalGen(Shankar et al., 2024b)的用户评论为人类反馈,AutoMetrics 为「LLM 撰写的电商商品描述」生成了有用的评测指标:左侧三行示例展示了商品(如 Yardley of London 保湿香皂)与对应的 LLM 生成描述及其人类反馈,右侧列出归纳出的评审准则片段——提示优化型评审(检查任务要求分析、结构评估、内容准确性、SEO 与语气等)、语气与语态量表(主动语态、积极措辞、不提产品弱点)、违禁内容规避(不得包含链接、套话或提及产品弱点)、搜索引擎优化(策略性地纳入关键词)、基于示例的评审(给出两条带分值的金标准示例)等;「Top 5 AutoMetrics」一栏的 26.3%、23.6%、19.9%、15.3%、14.9% 为由回归系数导出的各指标相对重要性。

### 1 引言(Introduction)

::: en
Modern AI systems now demonstrate massively multitask capabilities imparted through extensive pretraining (Radford et al., 2019; Brown et al., 2020). Practitioners can rapidly prototype new AI-enabled tasks – from travel planning to code completion – at a pace much faster than the community can craft domain specific metrics (Papineni et al., 2002; Lin, 2004; Xu et al., 2016). This new era, in which large language models can be adapted to virtually any domain, places mounting pressure on evaluation practices. A divide is growing between tasks with easily verifiable rewards, such as math (Glazer et al., 2024; Shao et al., 2024) and coding (Chen et al., 2021), while subjective and open-ended tasks such as writing (Gurung & Lapata, 2025) remain difficult to measure. For these tasks, human evaluation remains the gold standard (Shankar et al., 2024b; Chiang et al., 2024). Unfortunately, human evaluation is costly, slow, and not scalable for every prototype or user population. Reward models offer an alternative (Mnih et al., 2015; Christiano et al., 2017), but they typically require thousands of labels. The common alternative is rubric-based LLM-as-a-Judge methods (Li et al., 2023; Zheng et al., 2023; Liu et al., 2024), which rely on the assumption that system behavior is clearly defined and are not guaranteed to follow given rubrics strictly (Tripathi et al., 2025). In reality, practitioners typically have access only to non-descriptive human signals (e.g., thumbs up/thumbs down collected from users). In this setting, the problem is not only formulating the rubric, but also discovering the underlying criteria that matter.
:::

现代 AI 系统通过大规模预训练获得了多任务能力(Radford et al., 2019; Brown et al., 2020)。从业者可以快速原型化新的 AI 任务——从旅行规划到代码补全——其速度远快于社区打磨领域特定指标(如 BLEU、ROUGE、SARI,Papineni et al., 2002; Lin, 2004; Xu et al., 2016)。这个大语言模型几乎可被适配到任何领域的新时代,给评测实践带来了与日俱增的压力。一道鸿沟正在拉大:数学(Glazer et al., 2024; Shao et al., 2024)与编程(Chen et al., 2021)等任务拥有易验证的奖励,而写作等主观、开放的任务(Gurung & Lapata, 2025)仍然难以度量。对这些任务,人类评测仍是金标准(Shankar et al., 2024b; Chiang et al., 2024)。遗憾的是,人类评测昂贵、缓慢,且无法覆盖每一个原型或用户群体。奖励模型(reward model)提供了一种替代(Mnih et al., 2015; Christiano et al., 2017),但它们通常需要数千条标注。常见的替代是基于量表的 LLM-as-a-Judge 方法(Li et al., 2023; Zheng et al., 2023; Liu et al., 2024),这类方法依赖「系统行为已被清晰定义」的假设,且不保证严格遵循给定的量表(rubric)(Tripathi et al., 2025)。现实中,从业者通常只能拿到非描述性的人类信号(例如从用户那里收集的点赞/点踩)。在这种情境下,问题不只是「如何表述量表」,还包括「发现真正重要的底层标准」。(脚注:本文反映作者的学术工作,不代表亦不构成美国运通或其关联方的观点、政策、立场或实践。)

::: en
This highlights the need for dynamic, task-specific metric learning. Instead of relying exclusively on human judgment or fixed rubrics, evaluation itself must become adaptive. Current efforts have emphasized making LLMs better evaluators of task-specific criteria (Liu et al., 2024; Kim et al., 2025; Anugraha et al., 2025) or leveraging rubrics to optimize LLMs (Gunjal et al., 2025; Viswanathan et al., 2025) but comparatively little work has focused on automatically generating the rubrics and criteria to be adaptively aligned with human judgment (Biyani et al., 2024; Ryan et al., 2025; Dunlap et al., 2025). Such adaptive evaluation is essential not only for easily assessing new tasks but also for optimizing evaluated systems based on real-time user feedback.
:::

这凸显了对动态、任务特定的指标学习(metric learning)的需求:评测本身必须变得自适应,而不是仅仅依赖人类判断或固定量表。当前的努力侧重于让 LLM 更好评判任务特定的准则(Liu et al., 2024; Kim et al., 2025; Anugraha et al., 2025),或利用量表来优化 LLM(Gunjal et al., 2025; Viswanathan et al., 2025);相比之下,聚焦于「自动生成能自适应对齐人类判断的量表与准则」的工作相当少(Biyani et al., 2024; Ryan et al., 2025; Dunlap et al., 2025)。这种自适应评测不仅对轻松评估新任务至关重要,也是基于实时用户反馈去优化被评测系统所必需的。

::: en
We introduce AutoMetrics, a method for dynamic metric induction that turns sparse, non-descriptive human feedback into actionable and interpretable evaluators (Figure 1). Starting from a task description and fewer than 100 human signals, AutoMetrics synthesizes candidate criteria, retrieves and adapts existing metrics, and composes them through regression into predictive measures of quality. Beyond simply identifying criteria, AutoMetrics grounds and weighs them, producing metrics that are both predictive and interpretable. This approach achieves up to 33.4% higher Kendall correlation with human judgments than LLM-as-a-Judge baselines (§4), is data-efficient only requiring ∼80 feedback points (§4.6), and even matches verifiable rewards when optimizing downstream AI systems (§5). Beyond accuracy, AutoMetrics reveals actionable insights into what users value. We release AutoMetrics as an open-source toolkit 1, offering the community a powerful new way to evaluate and optimize AI applications at the speed of modern development.
:::

我们提出 AutoMetrics,一种动态指标归纳(metric induction)方法,把稀疏、非描述性的人类反馈转化为可行动、可解释的评估器(Figure 1)。从一份任务描述与不到 100 条人类信号出发,AutoMetrics 合成候选准则、检索并适配既有指标,再通过回归把它们组合成对质量的预测性度量。AutoMetrics 不只是识别准则,还会为准则落地(ground)并加权,产出既有预测力又可解释的指标。这一方法相对 LLM-as-a-Judge 基线将与人类判断的 Kendall 相关系数最高提升 33.4%(§4);数据高效,只需约 80 条反馈(§4.6);在优化下游 AI 系统时甚至能匹敌可验证奖励(§5)。在准确率之外,AutoMetrics 还揭示「用户看重什么」的可行动洞见。我们将 AutoMetrics 以开源工具包发布(脚注 1:https://github.com/SALT-NLP/autometrics ),为社区提供一种以现代开发速度评测并优化 AI 应用的强大新方式。

### 2 相关工作(Related Work)

::: en
Metric Collections Prior work has organized collections of metrics primarily for the ease of use on the part of the practitioner. When already using a library such as PyTorch (Paszke et al., 2019) or Huggingface (Wolf et al., 2020) it's simple to utilize TorchMetrics (Nicki Skafte Detlefsen et al., 2022) or HuggingFace lighteval (Fourrier et al., 2023). Scikit Learn Metrics (Pedregosa et al., 2011) and NLTK metrics (Bird & Loper, 2004) were created with the same intentions. All text-generation metrics covered by these collections are also contained in our MetricBank collection. Beyond integrating with existing open source libraries, some metric collections are part of ML observability frameworks like Evidently (EvidentlyAI, 2025), Galileo (Galileo, 2025), Scorecard.io (Doe & Devireddy, 2024), and DeepEval (ConfidentAI, 2025). Most metrics are tightly coupled with their observability platform, although Evidently and DeepEval offer open-source versions. While DeepEval offers a metric recommendation feature, it is based on a predefined decision tree of questions like "Does your LLM application use Retrieval-Augmented Generation (RAG)?" and "Is LLM safety a priority for you?". Most similar to our work is the MetaMetrics collection (Winata et al., 2025), which computes a regression over multiple task-specific metrics for tasks like image captioning and summarization to select the best combination of metrics. We compare our approach with MetaMetrics in Section 4 and find that our core thesis of adaptive metric generation is critical for evaluation in the low-data, novel task settings of interest.
:::

**指标合集(Metric Collections)。** 以往工作整理指标合集,主要是为了方便从业者使用。如果已经在用 PyTorch(Paszke et al., 2019)或 Huggingface(Wolf et al., 2020)这类库,那么使用 TorchMetrics(Nicki Skafte Detlefsen et al., 2022)或 HuggingFace lighteval(Fourrier et al., 2023)很简单;Scikit Learn Metrics(Pedregosa et al., 2011)与 NLTK metrics(Bird & Loper, 2004)也是出于同样的意图创建的。这些合集覆盖的全部文本生成类指标,也都收录在我们的 MetricBank 合集之中。除与既有开源库集成外,一些指标合集是 ML 可观测性(observability)框架的一部分,如 Evidently(EvidentlyAI, 2025)、Galileo(Galileo, 2025)、Scorecard.io(Doe & Devireddy, 2024)与 DeepEval(ConfidentAI, 2025)。其中的指标大多与其可观测性平台紧耦合,不过 Evidently 与 DeepEval 提供开源版本。DeepEval 虽提供指标推荐功能,但它基于预定义的问题决策树,例如「你的 LLM 应用是否使用检索增强生成(RAG)?」「LLM 安全对你是否是优先事项?」。与我们的工作最相似的是 MetaMetrics 合集(Winata et al., 2025),它对图像描述、摘要等任务的多个任务特定指标做回归,以选出最优的指标组合。我们在第 4 节与 MetaMetrics 做了对比,并发现我们的核心论点——自适应指标生成(adaptive metric generation)——对我们所关注的低数据、新任务场景下的评测至关重要。

[图 2: AutoMetrics comprises four steps. (1) Generate: create task-specific candidate metrics (Single criteria, Rubric, Examples, MIPROv2). (2) Retrieve: from the generated candidates plus MetricBank, use ColBERT to prefilter to k′ metric cards and an LLM to select the final k. (3) Regress: fit a PLS model on the training set to weight and select metrics that predict human judgments. (4) Report: produce a writeup with weights and correlations and details to guide adoption.]

图 2:AutoMetrics 包含四个步骤(以旅行规划任务为例)。(1)生成(Generate):创建任务特定的候选指标——单准则(Single Criteria)、量表(Rubric)、示例型(Examples)、MIPROv2 提示优化型;(2)检索(Retrieve):在生成的候选加上 MetricBank(含 INFORM 奖励模型、LDL 奖励模型、SummaQA、Toxicity、本地文化整合量表、住宿选择、具体性与细节量表等指标)之中,先用 ColBERT 预筛到 k′ 张指标卡(所有指标都带有用于辅助检索的文档),再用一个 LLM 选出最终的 k 个;(3)回归(Regress):在人类数据训练集上拟合 PLS 模型,对能预测人类判断的指标加权并选择——图中五个人类评分样例(如 5/5、4/5、2/5)与最终旅行规划指标的权重(24.8%、20.4%、19.5%、17.8%、17.5%)对应各指标的回归系数;(4)报告(Report):产出一份带权重、相关性及细节的文档以指导采用。

::: en
LLM Based Evaluation LLM-as-a-Judge (Zheng et al., 2023) evaluation is increasingly popular with the frequent improvement of LLM capabilities. Several works devise task-specific prompts to enable LLM-based evaluation for storytelling (Chiang & Lee, 2023), summarization (Wang et al., 2023; Hada et al., 2024; Wu et al., 2023), dialogue (Lin & Chen, 2023; Fu et al., 2024), knowledge (Bai et al., 2023), translation (Kocmi & Federmann, 2023), and more (Brake & Schaaf, 2024). Another promising direction is devising frameworks and general methods for making LLM-as-a-Judge more reliable. G-Eval (Liu et al., 2023) proposes breaking LLM evaluation into a step-by-step chain of thought and taking a weighted sum over the log probabilities of generating different scores. ChatEval (Chan et al., 2024) simulates multiple perspectives by evaluating through multi-agent debate. SPADE (Shankar et al., 2024a) generates assertions for LLMs to verify based on labeled good and bad examples. VERDICT (Kalra & Tang, 2025) introduces judge-time scaling by decomposing judgments into composable units of reasoning, verification, debate, and aggregation steps. Though we take inspiration from many of these frameworks, the most directly similar to our LLM-as-a-Judge steps in the AutoMetrics pipeline are DnA-Eval (Li et al., 2025) and EvalGen (Shankar et al., 2024b). DnA-Eval (Li et al., 2025) decomposes evaluation into rubric criteria and aggregates the results across the criteria. EvalGen (Shankar et al., 2024b) elicits limited human feedback on generated outputs, proposes criteria for evaluation based on this feedback, and iteratively refines the criteria with a human-in-the-loop and LLM.
:::

**基于 LLM 的评测(LLM Based Evaluation)。** 随着 LLM 能力的频繁提升,LLM-as-a-Judge(Zheng et al., 2023)评测日益流行。若干工作设计了任务特定的提示,使 LLM 评测适用于讲故事(Chiang & Lee, 2023)、摘要(Wang et al., 2023; Hada et al., 2024; Wu et al., 2023)、对话(Lin & Chen, 2023; Fu et al., 2024)、知识(Bai et al., 2023)、翻译(Kocmi & Federmann, 2023)等更多任务(Brake & Schaaf, 2024)。另一个有前景的方向是设计让 LLM-as-a-Judge 更可靠的框架与通用方法:G-Eval(Liu et al., 2023)提出把 LLM 评测拆成逐步的思维链,并对生成不同分数的对数概率加权求和;ChatEval(Chan et al., 2024)通过多智能体辩论来评测,以模拟多种视角;SPADE(Shankar et al., 2024a)基于标注的好坏示例生成供 LLM 验证的断言(assertion);VERDICT(Kalra & Tang, 2025)引入评审时扩展(judge-time scaling),把判断分解为推理、验证、辩论、聚合等可组合的单元。尽管我们从这些框架中汲取了灵感,但与 AutoMetrics 流水线中 LLM-as-a-Judge 步骤最直接相似的仍是 DnA-Eval(Li et al., 2025)与 EvalGen(Shankar et al., 2024b)。DnA-Eval(Li et al., 2025)把评测分解为多条量表准则,再对准则上的结果做聚合;EvalGen(Shankar et al., 2024b)则在生成输出上征询有限的人类反馈,基于该反馈提出评测准则,并在人机回环(human-in-the-loop)与 LLM 的配合下迭代精炼这些准则。

### 3 AutoMetrics 方法(The AutoMetrics Method)

::: en
The purpose of AutoMetrics is to produce metrics for subjective and novel AI-enabled tasks. Our goal is to induce metrics that correlate strongly with human judgments while requiring minimal data collection. To accomplish this, we present a general pipeline with four stages: (1) generate, (2) retrieve, (3) regress, and (4) report. These steps are visualized in Figure 2. Each stage involves design choices among several alternatives, which we empirically validate (§4.5).
:::

AutoMetrics 的目的是为主观、新颖的 AI 任务产出指标。我们的目标是在只需最少数据收集的前提下,归纳出与人类判断强相关的指标。为此,我们提出一个包含四个阶段的通用流水线:(1)生成(generate)、(2)检索(retrieve)、(3)回归(regress)、(4)报告(report)。这些步骤如图 2 所示。每个阶段都涉及在若干备选方案之间做设计抉择,我们对其逐一做了实证验证(§4.5)。

#### 3.1 指标生产(Metric Production)

::: en
Generate For sufficiently novel settings, generating criteria for LLM-as-a-Judge evaluation is essential. Broad coverage of evaluation criteria allows us to later filter down to what matters most. Accordingly, our default configuration generates 10 Single Criterion LLM Judge metrics, 5 Rubric LLM-Judge metrics, 1 Example-based optimized LLM-Judge metric (fewshot), and 1 Prompt-Optimized LLM-Judge metric per run of AutoMetrics 2. Optimized metrics require more LLM calls/tokens to produce, while criteria and rubrics are relatively inexpensive. Unless otherwise specified, we use this configuration throughout the paper. Empirically, we find this mix of generated metrics generalizes across diverse domains and tasks. For each metric, we also generate a Metric Card documenting its description, intended use, implementation details, and limitations (Appendix B).
:::

**生成(Generate)。** 对足够新颖的场景而言,为 LLM-as-a-Judge 评测生成准则是必需的。评测准则的宽覆盖让我们之后能筛选出最重要的部分。因此,我们的默认配置在每次运行 AutoMetrics 时生成:10 个单准则(Single Criterion)LLM 评审指标、5 个量表(Rubric)LLM 评审指标、1 个基于示例优化(Example-based optimized,即 few-shot)的 LLM 评审指标,以及 1 个提示优化(Prompt-Optimized)的 LLM 评审指标(脚注 2:设计细节与消融见附录 E.2;我们在近 30 个设置上验证了这些选择)。优化型指标需要更多 LLM 调用/token 来生产,而准则与量表相对便宜。除非另有说明,全文均使用该配置。经验上,我们发现这种生成指标的组合能跨多样领域与任务泛化。对每个指标,我们还生成一张指标卡(Metric Card),记录其描述、预期用途、实现细节与局限(附录 B)。

::: en
Retrieve In addition to generated metrics, we leverage our MetricBank: a collection of 48 metrics (Appendix Table 4) drawn from the NLP literature, each implemented and documented with a Metric Card. Directly evaluating all metrics would be prohibitively expensive, so we instead use retrieval as a filtering step. We treat Metric Cards as documents, and use a description of the evaluation setting or task as the search query. Retrieval is performed using a hybrid ColBERT + LLM approach, 3 narrowing the candidate pool to metrics most relevant to the task at hand.
:::

**检索(Retrieve)。** 除生成指标外,我们还利用我们的 MetricBank:一个从 NLP 文献中选取的 48 个指标(附录表 4)的合集,每个指标都有实现并配有指标卡文档。直接评测全部指标的代价将难以承受,因此我们改用检索作为过滤步骤:把指标卡当作文档,把评测场景或任务的描述当作搜索查询。检索采用 ColBERT + LLM 混合方法(脚注 3:我们在附录 E.1 中对选择算法做了消融),把候选池收窄到与手头任务最相关的指标。

::: en
Regress The filtered pool of candidate metrics must still be combined into a predictive signal for human judgment. We normalize all metric scores to their z-scores and fit a Partial Least Squares (PLS) regression model. Intuitively, PLS projects the metric space onto the direction most predictive of human labels, then regresses labels along that axis. We choose PLS regression because it works well under the constraints of our setting that: (1) the number of predictors (metrics) may be comparable to or larger than the number of observations (data points), and (2) the predictors are often highly correlated. Concretely, with a single latent component, PLS finds a unit weight vector $w^\star \in \mathbb{R}^d$ that maximizes

$$w^\star = \arg\max_{\|w\|_2=1} \operatorname{cov}(Xw, y)^2,$$

where $X$ is the matrix of normalized metric scores and $y$ is the vector of human labels. The latent score is $t = Xw^\star$, and PLS then regresses the human labels on this latent score, yielding predictions $\hat{y} = t\beta$ with coefficient $\beta = \frac{t^\top y}{t^\top t}$.

We apply this procedure in two stages. In the first stage, we fit PLS using all candidate metrics and rank them by the magnitude of their weights in $w^\star$. We then select the top $n$ metrics according to this ranking. In the second stage, we refit PLS on this reduced set of $n$ metrics to obtain a new projection $t$ and corresponding predictions $\hat{y}$. As a final step, we remove negatively correlated LLM-generated metrics, as they are designed to target positive correlation. We don't apply this to existing measures (e.g., length can negatively correlate with conciseness).
:::

**回归(Regress)。** 筛选后的候选指标池仍需组合成对人类判断的预测信号。我们把所有指标分数归一化为 z 分数(z-score),并拟合偏最小二乘(Partial Least Squares, PLS)回归模型。直观地说,PLS 把指标空间投影到对人类标签最具预测性的方向上,然后沿该轴对标签做回归。我们选择 PLS 回归,是因为它在本文场景的两个约束下表现良好:(1)预测变量(指标)的数量可能与观测(数据点)数量相当甚至更多;(2)预测变量之间常常高度相关。具体地,采用单个隐分量(latent component)时,PLS 求解如下优化问题的单位权重向量 $w^\star \in \mathbb{R}^d$:

$$w^\star = \arg\max_{\|w\|_2=1} \operatorname{cov}(Xw, y)^2,$$

其中 $X$ 是归一化指标分数矩阵,$y$ 是人类标签向量。隐变量得分(latent score)为 $t = Xw^\star$,随后 PLS 把人类标签对该隐变量得分回归,得到预测 $\hat{y} = t\beta$,系数为 $\beta = \frac{t^\top y}{t^\top t}$。

我们把该过程分两个阶段应用。第一阶段,用全部候选指标拟合 PLS,并按其权重在 $w^\star$ 中的幅值对指标排序,再按此排序选出前 $n$ 个指标。第二阶段,在这个缩小后的 $n$ 个指标集上重新拟合 PLS,得到新的投影 $t$ 与相应预测 $\hat{y}$。最后一步,我们移除负相关的 LLM 生成指标,因为它们被设计为追求正相关。我们不对既有度量应用此步骤(例如,长度可以与简洁度负相关)。

#### 3.2 指标评测(Metric Evaluation)

::: en
To evaluate the quality of induced metrics, we draw on concepts of measurement validity from research (Borsboom et al., 2004) and testing (American Educational Research Association et al., 2014). We focus on three forms: "Content Validity", "Criterion Validity", and "Construct Validity". Content Validity asks whether a metric represents the construct it is intended to measure. Although direct quantification is difficult, we encourage transparency by releasing metric reports. Because our generated metrics rely on LLM judges, we also expose the reasoning traces of the judge LLM, allowing users to inspect whether assessments appear justified. These traces can further aid system optimization with AutoMetrics (§5).
:::

为评估归纳出的指标的质量,我们借鉴了科学研究(Borsboom et al., 2004)与测验(American Educational Research Association et al., 2014)中测量效度(measurement validity)的概念,聚焦三种形式:「内容效度(Content Validity)」「准则效度(Criterion Validity)」与「构念效度(Construct Validity)」。**内容效度**问的是:一个指标是否代表了它意图测量的构念(construct)。虽然难以直接量化,我们通过发布指标报告来鼓励透明。由于我们生成的指标依赖 LLM 评审,我们还暴露评审 LLM 的推理轨迹(reasoning trace),让用户可以检查评估是否有依据。这些轨迹还能进一步辅助用 AutoMetrics 做系统优化(§5)。

::: en
Criterion Validity Criterion validity measures correlation with a reference standard. In NLP, correlation with human labels has been the most widely used criterion (Banerjee & Lavie, 2005; Xu et al., 2016; Gehrmann et al., 2021). We assess criterion validity by comparing AutoMetrics to ground-truth human labels. We report Kendall's τ, which makes no distributional assumptions and simply checks whether the rank order induced by a metric matches that of human judgments. This provides a conservative estimate compared to Spearman's ρ or Pearson's r.
:::

**准则效度(Criterion Validity)** 度量与参考标准的相关性。在 NLP 中,与人类标签的相关性一直是最广泛使用的准则(Banerjee & Lavie, 2005; Xu et al., 2016; Gehrmann et al., 2021)。我们通过把 AutoMetrics 与真值人类标签做比较来评估准则效度。我们报告 Kendall's τ:它不做任何分布假设,只检查一个指标诱导出的排序是否与人类判断的排序一致。相比 Spearman's ρ 或 Pearson's r,这提供了一种更保守的估计。

::: en
Construct Validity measures whether a metric captures an underlying abstract concept, such as "quality." Both human judgments and AutoMetrics attempt to approximate "quality". We draw from convergent–discriminant validity (Campbell & Fiske, 1959) and operationalize construct validity as robustness. A useful metric should penalize quality degradations (sensitivity) while remaining stable under equivalent-quality variation. In order to quantify convergent-discriminant validity, we introduce two measurements: Sensitivity and Stability. To construct test cases, we use an LLM to generate strategies for degrading outputs on a given dataset, and apply these to produce worse-quality perturbations. In contrast, same-quality perturbations are produced from a fixed set of hand-crafted transformations—such as rephrasing, reordering, synonym replacement, or stylistic edits—that are designed to preserve the target evaluation dimension. Prompts are provided in Appendix C.
:::

**构念效度(Construct Validity)** 度量一个指标是否捕捉了「质量」这类底层抽象概念。人类判断与 AutoMetrics 都在尝试逼近「质量」。我们借鉴聚合-区分效度(convergent–discriminant validity, Campbell & Fiske, 1959)的思想,把构念效度操作化为鲁棒性:一个有用的指标应当惩罚质量降质(敏感度),同时在等效质量的变化下保持稳定。为量化聚合-区分效度,我们引入两个测量:**敏感度(Sensitivity)**与**稳定度(Stability)**。构造测试样例时,我们用一个 LLM 生成在给定数据集上「降质输出」的策略,并应用这些策略产出质量更差的扰动;与之相对,**等效质量扰动(same-quality perturbation)**则产自一组固定的手工变换——如改写、重排、同义替换或文体编辑——它们被设计为保持目标评测维度不变。提示词见附录 C。

::: en
• Sensitivity measures whether a metric assigns lower scores to degraded outputs. Let $s^{(i)}_{\text{orig}}$ and $s^{(i)}_{\text{worse}}$ denote the normalized scores for the original and worse-quality perturbed outputs of sample $i$ from a dataset of size $|N|$. Sensitivity is defined as:

$$\text{Sensitivity} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[ s^{(i)}_{\text{worse}} < s^{(i)}_{\text{orig}} \right]$$

• Stability measures whether a metric produces consistent scores when quality should be preserved. Let $s^{(i)}_{\text{same}}$ be the normalized score for a same-quality perturbation of sample $i$ from a dataset of size $|N|$. Stability is defined as:

$$\text{Stability} = 1 - \frac{1}{N} \sum_{i=1}^{N} \left| s^{(i)}_{\text{orig}} - s^{(i)}_{\text{same}} \right|.$$
:::

- **敏感度**度量一个指标是否给降质输出打更低的分。设 $s^{(i)}_{\text{orig}}$ 与 $s^{(i)}_{\text{worse}}$ 分别为大小为 $|N|$ 的数据集中样本 $i$ 的原始输出与更差质量扰动输出的归一化分数。敏感度定义为:

$$\text{Sensitivity} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}\left[ s^{(i)}_{\text{worse}} < s^{(i)}_{\text{orig}} \right]$$

- **稳定度**度量当质量理应保持不变时,一个指标是否产生一致的分数。设 $s^{(i)}_{\text{same}}$ 为大小为 $|N|$ 的数据集中样本 $i$ 的等效质量扰动的归一化分数。稳定度定义为:

$$\text{Stability} = 1 - \frac{1}{N} \sum_{i=1}^{N} \left| s^{(i)}_{\text{orig}} - s^{(i)}_{\text{same}} \right|.$$

::: en
High sensitivity indicates strong penalization of degraded outputs, while high stability indicates invariance to irrelevant variation. Both are desirable, and together they provide a general-purpose lens for evaluating how well a metric generalizes.
:::

高敏感度表示对降质输出的强惩罚,高稳定度表示对无关变化的不变性。二者皆为我们所期望,合在一起,它们为评估一个指标泛化得好不好提供了一个通用视角。

### 4 实验与评估:验证 AutoMetrics 有效(Experiments and Evaluations: Showing AutoMetrics are Valid)

::: en
For our experiments, we focus on showing that our AutoMetrics are valid across many tasks/domains and that they correlate better with human judgements than competitive baselines. We showcase AutoMetrics have high Criterion Validity and Construct Validity across several tasks.
:::

在实验部分,我们聚焦于展示:我们的 AutoMetrics 在许多任务/领域上有效,并且与有竞争力的基线相比,它们与人类判断的相关性更好。我们将展示 AutoMetrics 在若干任务上具有高准则效度与构念效度。

#### 4.1 任务(Tasks)

表 1:任务总览(Table 1: Overview of tasks. Icons: Code Generation; Data-to-Text Generation; Dialogue/Chat; Education/Readability; Travel Planning.)——图标含义:代码生成、数据到文本生成、对话/聊天、教育/可读性、旅行规划;Refs 列表示是否有参考文本:

| 数据集(引用)| 任务 / 领域 | 数据量 | 反馈类型 | 评测维度数 | 参考文本 |
| --- | --- | --- | --- | --- | --- |
| **分布内任务**:MetricBank 中部分指标即为直接评测这些任务而设计。 |
| SimpEval(Maddela et al., 2023)| 句式简化 / 教育·可读性 | 360 | 1–100 Likert | 1 | ✓ |
| HelpSteer2(Wang et al., 2024)| 对话 / 对话·聊天 | 20,324 | 1–5 Likert | 5 | ✗ |
| **分布外任务**:没有任何指标专为这些任务设计——检验泛化与指标生成能力。 |
| EvalGen(Shankar et al., 2024b)| 商品描述 / 数据到文本 | 100 | 二元 | 1 | ✗ |
| RealHumanEval(Mozannar et al., 2025)| 代码补全 / 代码生成 | 5,204 | 行为信号 | 1 | ✗ |
| Co-Gym(Shao et al., 2025)| 旅行规划 / 旅行规划 | 72 | 1–5 Likert | 3 | ✗ |

::: en
In order to evaluate our AutoMetrics method, we collect two types of tasks: In-Distribution Tasks, which are tasks where some of the metrics in our Metric Bank were designed to directly evaluate the task, and Out-of-Distribution Tasks, which are tasks where no metric in particular was designed to assess the task. All of our tasks utilize human feedback for evaluation, encompassing behavioral feedback, binary feedback (thumbs up/down), and Likert scale feedback, which is already collected as part of the dataset. We introduce all tasks in Table 1. In our main tables we present results for five datasets and a single evaluation dimension from each: SimpEval (Maddela et al., 2023) (sentence simplification score 1–100), HelpSteer2 (Wang et al., 2024) (Chatbot helpfulness 1–5), EvalGen (Shankar et al., 2024b) (Product Review Thumbs Up/Down), RealHumanEval (Mozannar et al., 2025) (accepted or rejected code edit), CoGym (Shao et al., 2025) (travel plan outcome rating 1–5). We report evaluations on more settings in the Appendix results.
:::

为评估我们的 AutoMetrics 方法,我们收集了两类任务:**分布内任务(In-Distribution Tasks)**,即 MetricBank 中部分指标就是为直接评测该任务而设计的任务;以及**分布外任务(Out-of-Distribution Tasks)**,即没有任何特定指标专为评估该任务而设计的任务。我们所有任务都使用人类反馈做评测,涵盖行为反馈、二元反馈(点赞/点踩)与 Likert 量表反馈——这些反馈均为数据集自带、已经收集好的。我们在表 1 中介绍全部任务。在主表中,我们给出五个数据集、每个数据集单一评测维度的结果:SimpEval(Maddela et al., 2023)(句子简化得分 1–100)、HelpSteer2(Wang et al., 2024)(聊天机器人有用性 1–5)、EvalGen(Shankar et al., 2024b)(商品评论点赞/点踩)、RealHumanEval(Mozannar et al., 2025)(代码编辑被接受或拒绝)、CoGym(Shao et al., 2025)(旅行规划结果评级 1–5)。更多设置上的评测见附录结果。

#### 4.2 基线(Baselines)

::: en
We include the following baselines: Best Existing Metric, where we run all 48 metrics (or 19 metrics for reference-free tasks), record their Kendall correlation on the validation set, and select the best metric to use for the task based on the validation correlation. MetaMetrics, where we take all the metrics from the MetaMetrics paper and compute an XGBoost Regression on the metrics on the trainset (Winata et al., 2025). Finetuned LLM refers to training a ModernBERT-large (Warner et al., 2024) to predict the human annotation. We implement it by training LoRA adapters (Hu et al., 2021) with rank = 16 on all the attention, dense layers, and regression head, using a learning rate of 5e−5 and a batch size of 16 for three epochs over the training data. For the LLM-Judge baseline, we use the original human annotation prompt for each task and provide it to an LLM. We include all of these prompts in Appendix C. DnA-Eval (Li et al., 2025) involves using an LLM to generate three dimensions where a user request may benefit from evaluation, along with weights for how to aggregate these dimensions. Then each of those dimensions is scored with an LLM-as-a-Judge, and finally aggregated based on the LLM-generated weights.
:::

我们纳入以下基线:**Best Existing Metric**(最优既有指标):跑全部 48 个指标(免参考任务为 19 个),记录它们在验证集上的 Kendall 相关,并按验证集相关性为任务选出最佳指标使用。**MetaMetrics**:取 MetaMetrics 论文的全部指标,在训练集上对指标计算 XGBoost 回归(Winata et al., 2025)。**Finetuned LLM**(微调 LLM)指训练一个 ModernBERT-large(Warner et al., 2024)来直接预测人类标注;实现上,我们在全部注意力层、全连接层与回归头上训练 rank = 16 的 LoRA 适配器(Hu et al., 2021),学习率 5e−5、batch size 16,在训练数据上跑三个 epoch。**LLM-Judge** 基线:把每个任务原始的人工标注提示直接提供给一个 LLM;这些提示全部收录在附录 C。**DnA-Eval**(Li et al., 2025)则先用一个 LLM 生成「用户请求可能在哪些维度上受益于评测」的三个维度,以及聚合这些维度的权重;随后每个维度各由一个 LLM-as-a-Judge 打分,最后按 LLM 生成的权重聚合。

#### 4.3 准则效度(相关性)(Criterion Validity (Correlation))

::: en
We report Kendall's τ of all methods with GPT-4o-mini and Qwen-3-32B Reasoning in Table 2.
:::

我们在表 2 中报告所有方法在 GPT-4o-mini 与 Qwen-3-32B Reasoning 两种骨干下的 Kendall's τ。

表 2:准则效度结果,5 次独立运行的 Kendall's Tau 与 95% 置信区间(Table 2: Criterion Validity results showing Kendall's Tau with 95% confidence intervals over 5 independent runs. AutoMetrics outperforms the baselines on all five tasks with Qwen3-32B and is within 95% confidence of the best for 4/5 tasks with GPT-4o-mini. On EvalGen, AutoMetrics improves performance by 33.4% over the closest baseline (LLM Judge).)——AutoMetrics 以 Qwen3-32B 骨干在全部五个任务上超过基线,以 GPT-4o-mini 骨干在 4/5 任务上处于最优的 95% 置信区间之内;在 EvalGen 上,AutoMetrics 相对最接近的基线(LLM Judge)提升 33.4%:

| 方法 | SimpEval(分布内)| HelpSteer2(分布内)| EvalGen(分布外)| RealHumanEval(分布外)| CoGym(分布外)|
| --- | --- | --- | --- | --- | --- |
| **模型无关(Model Agnostic)** | | | | | |
| Best Existing Metric | 0.246±0.00 | 0.327±0.00 | 0.193±0.00 | 0.138±0.00 | 0.074±0.00 |
| MetaMetrics(Winata et al., 2025)| 0.127±0.01 | 0.204±0.00 | −0.214±0.01 | 0.025±0.01 | −0.119±0.02 |
| Finetuned LLM | 0.076±0.08 | 0.039±0.03 | 0.054±0.05 | 0.049±0.06 | 0.223±0.20 |
| **GPT-4o-mini 骨干** |
| LLM-Judge | 0.272±0.02 | 0.259±0.01 | 0.161±0.14 | 0.069±0.01 | 0.199±0.13 |
| DnA Eval(Li et al., 2025)| 0.234±0.03 | 0.255±0.02 | 0.174±0.16 | 0.152±0.01 | 0.185±0.10 |
| AutoMetrics(本文)| 0.321±0.04 | 0.324±0.01 | 0.334±0.06 | 0.160±0.00 | −0.034±0.17 |
| **Qwen-3-32B 骨干** |
| LLM-Judge | 0.294±0.04 | 0.334±0.02 | 0.272±0.13 | 0.025±0.01 | 0.276±0.19 |
| DnA Eval(Li et al., 2025)| 0.042±0.04 | 0.260±0.02 | 0.232±0.19 | 0.071±0.15 | 0.353±0.25 |
| AutoMetrics(本文)| 0.316±0.02 | 0.342±0.01 | 0.382±0.05 | 0.145±0.00 | 0.365±0.08 |

[图 3: Sensitivity/Stability of AutoMetrics for SimpEval, HelpSteer2, and CoGym. AutoMetrics are sensitive to negative perturbations and stable on neutral perturbations.]

图 3:AutoMetrics 在 SimpEval(得分)、HelpSteer2(有用性)与 CoGym(结果评级)上的敏感度/稳定度。三组柱状图各含 Sensitivity 与 Stability 两根柱(30 次试验,纵轴为分数的均值 ± 95% 置信区间,范围 0–1.0),并与正态基线(Normal Baseline)对照:AutoMetrics 对负向扰动(质量降质)敏感,在中性扰动(等效质量变换)上稳定。

::: en
AutoMetrics correlates better than all baselines across all five tasks. We find that AutoMetrics outperforms all other existing baselines on all five tasks. While the best performing baseline is both inconsistent on dataset (LLM Judge on SimpEval, HelpSteer, EvalGen; DnA Eval on RealHumanEval and CoGym) and on the underlying model used (Existing Metrics outperform GPT-4o-mini but not Qwen3-32B). In contrast, AutoMetrics is consistently the best option regardless of dataset or underlying model. On all datasets besides HelpSteer and CoGym, the AutoMetrics performance exceeds all baselines by greater than the 95% confidence interval. In general, AutoMetrics is the best choice for higher correlation with human ratings.
:::

**AutoMetrics 在全部五个任务上都比所有基线相关性更好。**我们发现 AutoMetrics 在全部五个任务上均优于其他所有既有基线。而表现最好的基线既在数据集上不一致(LLM Judge 在 SimpEval、HelpSteer、EvalGen 上好;DnA Eval 在 RealHumanEval 与 CoGym 上好),也在所用底层模型上不一致(既有指标在 GPT-4o-mini 上胜出,在 Qwen3-32B 上则不能)。相比之下,无论数据集还是底层模型,AutoMetrics 始终是最佳选项。在除 HelpSteer 与 CoGym 之外的所有数据集上,AutoMetrics 的性能以大于 95% 置信区间的幅度超过全部基线。总体而言,若追求与人类评分更高的相关性,AutoMetrics 是最佳选择。

#### 4.4 构念效度(鲁棒性)(Construct Validity (Robustness))

::: en
To measure construct validity, we take inspiration from convergent-discriminant validity and show that AutoMetrics are strong predictors when output quality degrades and that they are stable under unimportant perturbations. To do so we introduced Sensitivity and Stability (§3.2). Sensitivity measures the rate of detection of negative perturbations and Stability measures the magnitude of score preservation under meaningless changes. We report Sensitivity and Stability for all metrics on 30 trials in Figure 3. We compare against a normal distribution baseline.
:::

为度量构念效度,我们从聚合-区分效度中汲取灵感,展示 AutoMetrics 在输出质量降质时是强预测器,且在不重要的扰动下保持稳定。为此,我们在 §3.2 引入了敏感度与稳定度:敏感度度量对负向扰动的检出率,稳定度度量在无意义变化下分数保持的幅度。我们在图 3 中报告所有指标在 30 次试验上的敏感度与稳定度,并与一个正态分布基线作比较。

::: en
AutoMetrics are sensitive and stable. AutoMetrics are sensitive to degradation in output quality in 81.0-97.8% of cases, depending on the dataset, which is significantly greater than the 50% baseline. AutoMetrics can be a strong tool for identifying degradations in output quality. Similarly, AutoMetrics also always outperforms the baseline for stability by greater than 95% confidence intervals. Under insignificant modifications to evaluated outputs, AutoMetrics are consistently stable.
:::

**AutoMetrics 既敏感又稳定。**依数据集不同,AutoMetrics 在 81.0%–97.8% 的情形中对输出质量降质敏感,显著高于 50% 的基线。AutoMetrics 可以成为识别输出质量降质的有力工具。类似地,在稳定度上,AutoMetrics 也总是以大于 95% 置信区间的幅度胜过基线:面对被评测输出的无关紧要修改,AutoMetrics 始终保持稳定。

#### 4.5 设计决策(超参数扫描)(Design Decisions (Hyperparameter Sweeps))

::: en
Our sweeps/ablations test three parts of the AutoMetrics method: the MetricBank, the retrieval step, and the regression step. We report Kendall's τ rank correlation across our six main tasks with 95% confidence intervals over five runs in Table 3. All sweeps and ablations are instead done on the dev set for all datasets. We never make design decisions based on runs of our test sets.
:::

我们的扫描/消融检验 AutoMetrics 方法的三个部分:MetricBank、检索步骤与回归步骤。我们在表 3 中报告主要任务上的 Kendall's τ 秩相关(5 次运行、95% 置信区间)。所有扫描与消融均在各数据集的开发集(dev set)上进行;我们从不基于测试集上的运行来做设计决策。

表 3:分布内与分布外数据集上的 Kendall 相关(5 次运行、95% 置信区间,Qwen3 32B (Reasoning) 骨干)(Table 3: Kendall correlation with 95% confidence intervals on in-distribution and out-of-distribution datasets over five runs with Qwen3 32B (Reasoning). The Full MetricBank and Metric Cards prove useful, and the best settings for retrieval and regression are k=30 and n=5 respectively.)——Full MetricBank 与指标卡(Metric Cards)被证明有用;检索与回归的最佳设置分别为 k=30 与 n=5:

| 方法 | SimpEval | HelpSteer2 | EvalGen | RealHumanEval | CoGym |
| --- | --- | --- | --- | --- | --- |
| **MetricBank 消融(k=30; n=5)** |
| 仅既有指标(Existing Metrics Only)| 0.238±0.04 | 0.376±0.00 | 0.389±0.00 | 0.155±0.00 | 0.258±0.00 |
| 仅生成指标(Generated Metrics Only)| 0.276±0.03 | 0.308±0.01 | 0.503±0.03 | 0.132±0.00 | 0.433±0.04 |
| 完整 MetricBank(Full MetricBank)| 0.275±0.02 | 0.387±0.00 | 0.474±0.03 | 0.152±0.01 | 0.329±0.02 |
| **检索消融(n=5)** |
| 检索 k=5 | 0.257±0.03 | 0.336±0.03 | 0.414±0.12 | 0.124±0.02 | 0.385±0.04 |
| 检索 k=10 | 0.245±0.02 | 0.352±0.01 | 0.469±0.06 | 0.128±0.01 | 0.371±0.02 |
| 无指标卡(k=20)| 0.281±0.04 | 0.328±0.02 | 0.427±0.09 | 0.134±0.01 | 0.292±0.06 |
| 检索 k=20 | 0.286±0.02 | 0.378±0.01 | 0.522±0.02 | 0.141±0.01 | 0.302±0.06 |
| 检索 k=30 | 0.275±0.02 | 0.387±0.00 | 0.474±0.03 | 0.152±0.01 | 0.329±0.02 |
| **回归消融(k=30)** |
| 无回归(n=1)| 0.232±0.08 | 0.393±0.00 | 0.353±0.23 | 0.145±0.00 | 0.356±0.00 |
| 回归 n=3 | 0.255±0.02 | 0.389±0.02 | 0.503±0.10 | 0.152±0.01 | 0.302±0.04 |
| 回归 n=5 | 0.275±0.02 | 0.387±0.00 | 0.474±0.03 | 0.152±0.01 | 0.329±0.02 |
| 回归 n=10 | 0.309±0.01 | 0.358±0.01 | 0.461±0.05 | 0.147±0.01 | 0.297±0.05 |
| 回归 n=20 | 0.268±0.03 | 0.350±0.01 | 0.498±0.04 | 0.153±0.01 | 0.361±0.02 |

::: en
Both Generated and Existing Metrics Help. In all of our tasks, the Full MetricBank was either the best or second-best performing setting for the ablations. When it was second best, it was typically within 95% confidence intervals. The primary exception is CoGym, where "Full MetricBank" fell 0.104 below "Generated Metrics Only" and, to a lesser extent, EvalGen, where "Full MetricBank" was short by 0.029. CoGym and EvalGen are also our smallest training sets (37 and 57 training samples respectively). We hypothesize this is because on out-of-distribution tasks, existing metrics tend to be noisy predictors which can spuriously correlate during the regression. Generated metrics tend to be less noisy predictors. Larger training sets provide a more effective filter for identifying useful metrics. We further explore this hypothesis in our data scaling experiment (§4.6).
:::

**生成指标与既有指标都有贡献。**在我们所有任务中,Full MetricBank 在消融设置里要么是最佳、要么是次佳表现;当它是次佳时,通常也落在 95% 置信区间之内。主要的例外是 CoGym——「Full MetricBank」比「Generated Metrics Only」低 0.104;其次是 EvalGen,「Full MetricBank」低了 0.029。CoGym 与 EvalGen 也是我们最小的训练集(分别只有 37 与 57 个训练样本)。我们推测,这是因为在分布外任务上,既有指标往往是噪声预测器,可能在回归中产生伪相关(spurious correlation);生成指标则往往是噪声更小的预测器。更大的训练集能为识别有用指标提供更有效的过滤。我们在数据规模实验(§4.6)中进一步探讨了这一假设。

::: en
Metric Cards Help Retrieval and Larger k Is Better. Across all five tasks, retrieval with Metric Cards (k=20) is better than retrieval without metric cards (using a single sentence description of the metric). Furthermore, we see roughly linear growth of correlation with higher k metrics retrieved to run on the train set. The single exception to this trend is CoGym, which can be attributed to the noisiness of the small dataset and the generated metrics being less noisy predictors. The top 5 retrieved metrics are often generated ones, reducing the risk of recommending spuriously correlated existing metric on the small dataset. We ran all retrieval experiments by regressing with n = 5, so it is worth noting that future improvements to the retrieval algorithm (possibly including historical usage data) mean that it is feasible for k = 5 numbers to match our k = 30 results, so long as the proper metrics are recommended.
:::

**指标卡有助于检索,且更大的 k 更好。**在全部五个任务上,带指标卡的检索(k=20)都优于不带指标卡(只用一句话描述指标)的检索。此外,我们看到相关性随检索到训练集上运行的指标数 k 的增大而大致线性增长。这一趋势的唯一例外是 CoGym,可归因于小数据集的噪声以及生成指标是噪声更小的预测器——检索出的前 5 个指标往往是生成指标,从而降低了在小数据集上推荐伪相关既有指标的风险。我们所有检索实验都以 n = 5 做回归,因此值得注意的是:未来若检索算法改进(可能纳入历史使用数据),k = 5 的数量是有可能追上我们 k = 30 的结果的——只要推荐出的是恰当的指标。

::: en
Number to regress to varies from dataset to dataset, but five is a good average case. The best case for regression only repeats once (with n=20), suggesting that the number of metrics needed is highly dependent on the complexity of the evaluation task and domain. Since there is no clear winner, we select n=5 as a default because it is the second best in two of five tasks, and it is the cheapest option that still maintains lower variance from run to run. A higher N means producing more expensive metrics to run downstream, so n=5 is a useful compromise of cost and performance.
:::

**回归保留的个数因数据集而异,但五个是不错的平均情形。**回归的最佳情形只出现了一次(n=20),这提示所需指标的数量高度依赖评测任务与领域的复杂度。既然没有明显的赢家,我们选择 n=5 作为默认:它在五个任务中的两个上位列第二,而且是仍能保持较低运行间方差的最便宜选项。更高的 N 意味着要在下游运行更昂贵的指标,因此 n=5 是成本与性能之间一个有用的折中。

#### 4.6 使用 AutoMetrics 需要多少数据?(How Much Data do you Need to Use AutoMetrics?)

::: en
To test how much data is needed to use AutoMetrics, we test on three distinct datasets large enough to be useful in this experiment. We take a relatively simple In-Distribution dataset, SimpEval, a more challenging In-Distribution dataset, HelpSteer2, and an Out-of-Distribution dataset RealHumanEval. We vary the train set size from N=5, 10, 20, 40, 80, 160, and (for RealHumanEval and Helpsteer2) 320 and 640. We run these settings for both the "Generated Only" Metric Bank and "Full" Metric Bank (with existing metrics). We plot the correlation on the full test set in Figure 4.
:::

为测试使用 AutoMetrics 需要多少数据,我们在三个足够大、适合本实验的不同数据集上测试:一个相对简单的分布内数据集 SimpEval、一个更具挑战的分布内数据集 HelpSteer2,以及一个分布外数据集 RealHumanEval。我们把训练集大小从 N=5、10、20、40、80、160,以及(对 RealHumanEval 与 Helpsteer2)320、640 依次变化。我们对「Generated Only」与「Full」(含既有指标)两种 Metric Bank 都运行这些设置,并在图 4 中绘制它们在完整测试集上的相关系数。

[图 4: All correlations plotted for various training set sizes with "Generated Only" and "Full" Metric Banks. Individual trials are translucent while average performance at a scale is solid.]

图 4:「Generated Only」与「Full」两种 Metric Bank 在不同训练集大小(横轴 5–160,HelpSteer2 与 RealHumanEval 至 640)下的全部相关系数(纵轴为 Kendall correlation,范围约 0.0–0.4)。单次试验以半透明点绘制,同一规模下的平均性能以实线表示——三个子图分别为 SimpEval(得分)、HelpSteer2(有用性)与 RealHumanEval(接受率)。

::: en
About 80 samples saturates performance. Across all three datasets and both settings, performance levels off after about 80 samples. It is possible with more sophisticated metric generation/learning methods more data could continue to help, however with the current architecture between 80-100 examples is all you need. Below 80 examples most of the lower performance is due to the high variance of fitting a regression to a small training set.
:::

**约 80 个样本即可使性能饱和。**在全部三个数据集与两种设置下,性能在约 80 个样本后趋于平稳。如果用更精巧的指标生成/学习方法,更多数据或许还能继续带来帮助,但就当前架构而言,80–100 个示例就是所需的全部。低于 80 个示例时,性能的下降大多来自「往小训练集上拟合回归」的高方差。

::: en
On out-of-distribution datasets "Generated Only" can outperform "Full" with low-resources. Looking to the RealHumanEval plot we see at training size 10 and 20 the "Generated Only" metrics outperform the "Full" Bank. Recall back to the ablations (§4.5) where we observed on the small, out-of-distribution datasets, CoGym and EvalGen, that "Generated Only" outperformed the "Full" MetricBank. Since most tasks will be out of distribution by nature, we default to using "Generated Only" when the user provides less than 80 training samples. Beyond 80, both "Generated Only" and "Full" level off, however "Full" asymptotes higher than "Generated Only" on all datasets. We argue this is a product of the high-p, low-n problem in regression where having too many weak predictors and not enough datapoints can lead to spurious correlations. By limiting to generated metrics for low-n settings we enforce the use of stronger predictor signals.
:::

**在分布外数据集上,低资源时「Generated Only」可以胜过「Full」。**看 RealHumanEval 的曲线图:在训练集大小为 10 与 20 时,「Generated Only」指标优于「Full」库。回想消融实验(§4.5)——我们在 CoGym 与 EvalGen 这两个小规模分布外数据集上观察到「Generated Only」胜过「Full」MetricBank。由于大多数任务天然就是分布外的,当用户提供的训练样本少于 80 时,我们默认使用「Generated Only」。超过 80 之后,「Generated Only」与「Full」都趋于平稳,但在所有数据集上「Full」的渐近线都高于「Generated Only」。我们认为这是回归中高 p 低 n(high-p, low-n)问题的产物:太弱的预测器太多、数据点不足,会导致伪相关。在低 n 设置下限制为生成指标,等于强制使用更强的预测信号。

### 5 案例研究:用 AutoMetrics 优化智能体任务(Case Study: AutoMetrics for Optimizing an Agentic Task)

::: en
A natural extension to using AutoMetrics is to take the limited data one has available in order to learn a useful set of metrics that can then be used for optimizing a system. In this way AutoMetrics would operate similar to the purpose of a Reward Model or a Verifiable Reward. In order to test if AutoMetrics can be useful in this setting we optimize an airline assistance agent for τ-bench (Yao et al., 2024), a testbed for tool-use agents to interact with simulated users to accomplish tasks. We split the 50 τ-airline tasks into 25 for training and 25 for evaluation.
:::

使用 AutoMetrics 的一个自然延伸,是把手头有限的可用数据用来学出一组有用的指标,再把这些指标用于优化系统。这样,AutoMetrics 的角色就类似奖励模型或可验证奖励(Verifiable Reward)。为检验 AutoMetrics 在这一场景下是否有用,我们优化一个航空客服智能体,对应 τ-bench(Yao et al., 2024)——一个让工具使用型智能体(tool-use agent)与模拟用户交互以完成任务的测试台。我们把 50 个 τ-airline 任务拆成 25 个用于训练、25 个用于评测。

::: en
Simulating a verifiable reward. To run AutoMetrics we rollout the 25 training examples 8 times each with temperatures [0.0, 0.01, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2]. Then we obtain the true reward signal for each of these rollouts. In practice rather than a verifiable reward this could be a subjective human label. We run AutoMetrics in "Generate Only" mode and allocate more resources to generated metrics (10→20 llm judge metrics; 5→8 rubric metrics). Otherwise we run with default hyperparameters (k=30; n=5). We show the generated metrics in Figure 5.
:::

**模拟一个可验证奖励(Simulating a verifiable reward)。**为运行 AutoMetrics,我们对 25 个训练样例各做 8 次 rollout(采样运行),温度取 [0.0, 0.01, 0.02, 0.03, 0.05, 0.1, 0.15, 0.2];随后获取每个 rollout 的真实奖励信号——实践中它不必是可验证奖励,也可以是主观的人类标签。我们以「Generate Only」模式运行 AutoMetrics,并为生成指标分配更多资源(单准则 LLM 评审指标 10→20 个;量表指标 5→8 个),其余使用默认超参数(k=30;n=5)。生成的指标见图 5。

[图 5: AutoMetrics produces three metrics for τ-Bench. Regression coefficients in yellow.]

图 5:AutoMetrics 为 τ-Bench 产出三个指标,黄色标注为回归系数。三个指标分别是:**会员权益适用**(Membership Benefit Application,量表型,系数 0.08)——「根据会员等级正确执行免费行李额度、保险资格与补偿规则」;**转人工时机恰当性**(Escalation Appropriateness,量表型,系数 0.0599)——「在达到政策上限或需要例外处理时转接人工客服」;**政策合规**(Policy Compliance,单准则型,系数 0.0567)——「遵守航空公司规则(例如,无保险或不在 24 小时窗口内的基础经济舱机票不可退改)」。

::: en
AutoMetrics recommends three metrics for Tau-Bench evals: two rubric based metrics and one single criterion metric. Originally our (n=5) setting recommended five metrics, however our final filtering step removed two metrics for having negative coefficients. Since the trajectories are only derived from 25 examples it is likely that metrics will begin to learn things about the data itself. This reflects the importance of both human oversight and our metric filtering.
:::

AutoMetrics 为 τ-Bench 评测推荐了三个指标:两个量表型指标与一个单准则型指标。最初我们的(n=5)设置推荐了五个指标,但最终过滤步骤因负系数移除了其中两个。由于轨迹只来自 25 个样例,指标很可能会开始学到关于数据本身的东西(而非泛化的质量标准)。这反映出人工监督(human oversight)与我们的指标过滤二者的重要性。

::: en
Optimizing without a Verifiable Reward We implement a simple ReAct (Yao et al., 2023) agent in DSPy (Khattab et al., 2024) for performing the τ-Airline task. Our baseline agent gets 60% accuracy on the 25 test examples averaged over five trials. We then run a baseline optimization where we use the DSPy GEPA optimizer (Agrawal et al., 2025) to optimize an agent on the 25 training tasks with Verifiable Reward. Next we run optimization with our AutoMetrics as the metric for GEPA optimization. We show the performance on the test set after N rollouts in Figure 6.
:::

**无可验证奖励的优化(Optimizing without a Verifiable Reward)。**我们用 DSPy(Khattab et al., 2024)实现了一个简单的 ReAct 智能体(Yao et al., 2023)来执行 τ-Airline 任务。基线智能体在 25 个测试样例上的准确率为 60%(五次试验平均)。随后我们先跑一个基线优化:用 DSPy 的 GEPA 优化器(Agrawal et al., 2025)在 25 个训练任务上、以**可验证奖励**优化智能体;接着再换成以我们的 **AutoMetrics** 作为 GEPA 优化的度量来运行优化。N 次 rollout 之后在测试集上的性能见图 6。

[图 6: τ-Bench performance over GEPA optimization steps when using AutoMetrics.]

图 6:以 AutoMetrics 为度量做 GEPA 优化时,τ-Bench(Qwen3 32B)性能随优化进程的变化。横轴为 rollout 数量(0–2000),纵轴为平均 Pass^1 测试得分(0.50–0.80);三条曲线分别是 AutoMetrics、可验证奖励(Verifiable Reward)与未优化基线(Unoptimized Baseline)。

::: en
We find that AutoMetrics can match performance of a verifiable reward. After 2000 rollouts the GEPA optimization with verifiable reward achieves 0.680±0.11 accuracy over 5 trials while the AutoMetrics run gets 0.720±0.06. AutoMetrics statistically significantly exceeds the baseline performance (p<0.05) of 0.6. This demonstrates that AutoMetrics can match or exceed Verifiable Rewards as optimization signal.
:::

**我们发现 AutoMetrics 能匹敌可验证奖励的性能。**2000 次 rollout 之后,以可验证奖励做 GEPA 优化在 5 次试验中取得 0.680±0.11 的准确率,而 AutoMetrics 版本取得 0.720±0.06。AutoMetrics 以统计显著性(p<0.05)超过 0.6 的基线性能。这证明:作为优化信号,AutoMetrics 可以匹敌乃至超越可验证奖励。

### 6 讨论与结论(Discussion and Conclusion)

::: en
In this paper, we introduced AutoMetrics, a method for producing metrics that correlate with human judgments on subjective tasks. Requiring only ∼80 human-labeled examples, AutoMetrics achieve high criterion validity (§4.3) and construct validity (§4.4). AutoMetrics improve upon existing baselines by up to 33.4% in Kendall correlation with human ratings. In a case study on Tau-Bench, AutoMetrics matched or exceeded gains obtained from optimizing on a verifiable reward (§5).
:::

本文提出了 AutoMetrics——一种在主观任务上产出与人类判断相关的指标的方法。只需约 80 条人类标注样本,AutoMetrics 即可取得高准则效度(§4.3)与构念效度(§4.4),与人类评分的 Kendall 相关系数相对既有基线最高提升 33.4%。在 τ-Bench 案例研究中,AutoMetrics 追平乃至超过了基于可验证奖励进行优化所获得的收益(§5)。

::: en
We draw two key lessons for practitioners. First, data diversity is critical: while only ∼80 feedback points suffice for moderate correlation (§4.6), scaling up synthetic data from limited sources can produce metrics that reflect dataset artifacts rather than system quality (§5). Second, human oversight remains essential: domain experts can help remove spuriously correlated metrics which the automatic filtering process misses. When using metrics for optimization, practitioners should monitor metric feedback and improvement with observability tools (Chavez, 2025).
:::

我们为从业者总结两条关键教训。**其一,数据多样性至关重要(data diversity is critical)**:虽然约 80 条反馈即可获得中等程度的相关(§4.6),但从有限来源放大合成数据,可能让指标反映的是数据集伪迹(dataset artifacts)而非系统质量(§5)。**其二,人工监督仍然不可或缺(human oversight remains essential)**:领域专家能帮忙移除自动过滤过程漏掉的伪相关指标。当把指标用于优化时,从业者应当借助可观测性工具监控指标反馈与改进情况(Chavez, 2025)。

::: en
Overall, AutoMetrics provides a practical first step for exploring data and guiding optimization when collecting preliminary human evaluation in new domains. The metrics it produces are interpretable, actionable, and informative for system improvement. We release AutoMetrics publicly and invite community contributions of new metrics and methods to strengthen the framework.
:::

总体而言,在新领域收集初步人类评测时,AutoMetrics 为探索数据与指导优化提供了一个务实的第一步。它产出的指标可解释、可行动,并为系统改进提供信息。我们公开发布 AutoMetrics,并邀请社区贡献新的指标与方法,共同强化这一框架。

### 可复现性声明(Reproducibility Statement)

::: en
AutoMetrics is intended to be an open source library and framework. As such we take great effort to make the running and evaluation of AutoMetrics user-friendly. We have attached an anonymized repository for AutoMetrics with this submission. In addition to the core algorithm, the repository also contains the python scripts to reproduce all experimental results in this paper. All of our design decisions, hyperparameters, and ablations are rigorously documented throughout the paper across Section 4.5 and Appendix E. We provide system-specs needed to run the metrics in Table 5. We also share the exact prompts and DSPy signatures used in calling LLMs in Appendix C. For all main experimental results (e.g. Table 2 and Table 3) results are reported over five independent random seeds to ensure findings are robust and statistically significant.
:::

AutoMetrics 定位为一个开源库与框架,因此我们下了很大功夫让 AutoMetrics 的运行与评测对用户友好。我们随投稿附上了一个匿名的 AutoMetrics 代码仓库;除核心算法外,仓库还包含复现本文全部实验结果的 Python 脚本。所有设计决策、超参数与消融均在文中第 4.5 节与附录 E 里做了严谨记录。运行指标所需的系统规格见表 5;调用 LLM 所用的确切提示词与 DSPy 签名也在附录 C 中共享。对全部主实验结果(如表 2 与表 3),我们都报告五个独立随机种子上的结果,以确保结论稳健且具有统计显著性。

### 局限(Limitations)

::: en
As a part of the AutoMetrics framework we construct and optimize metrics with particular LLMs. Because the metric generation process involves optimizing to a particular model we have found that producing metrics with one model and running them with another reduces performance. This suggests that when better models are released it will be important to reoptimize automatic metrics using AutoMetrics rather than just swap out the underlying LLM.
:::

在 AutoMetrics 框架中,我们是用特定 LLM 来构建并优化指标的。由于指标生成过程包含面向特定模型的优化,我们发现:用一个模型产出的指标换另一个模型来运行,性能会下降。这意味着,当更强的模型发布时,重要的是用 AutoMetrics 重新归纳(优化)自动指标,而不是仅仅替换底层 LLM。

::: en
AutoMetrics may only generalize as far as the provided data enables it. Collecting real, diverse human data is still an essential part of evaluation. The more representative and generalizable the input data is, the better and more general the AutoMetrics will be. Users should collect data that is representative of the opinions and population that they want their evaluation to cover.
:::

AutoMetrics 的泛化上限受限于所提供的数据。收集真实、多样的人类数据仍是评测中不可或缺的一环:输入数据越有代表性、越可泛化,得到的 AutoMetrics 就越好、越通用。用户应当收集能代表其评测想覆盖的意见与人群的数据。

::: en
AutoMetrics depends on running a regression for many predictors on a limited number of data points. Although we took this into account with the design of our Regression step, it is still possible to run into a high-P low-N regression problem that risks spurious correlations. To counteract accidental misuse of AutoMetrics leading to poor evaluation, we add warnings to the metric reports when the significance of the correlation with human judgments of the recommended metric is low (p>0.05).
:::

AutoMetrics 依赖在有限数据点上对大量预测变量做回归。尽管我们在回归(Regress)步骤的设计中考虑到了这一点,但仍然可能遇到有伪相关风险的高 P 低 N 回归问题。为防止 AutoMetrics 被误用而导致糟糕的评测,当推荐指标与人类判断的相关性不显著(p>0.05)时,我们会在指标报告中加入告警。

::: en
Finally, as a part of this work we do not conduct a formal user study to demonstrate the adoption of AutoMetrics among practitioners. We have collected positive feedback on the metrics through informal tests with AI developers. We hope that by releasing and open sourcing this library, we will have the opportunity to work with the community to test and improve AutoMetrics.
:::

最后,本工作并未开展正式的用户研究来证明 AutoMetrics 在从业者中的采用情况。我们已通过与 AI 开发者的非正式测试收集到对指标的正面反馈。我们希望通过开源发布这个库,获得与社区一起测试并改进 AutoMetrics 的机会。

### 致谢(Acknowledgements)

::: en
This work has been supported in part through the Stanford HAI Corporate Affiliate Program, with membership funding provided by American Express. This work was also funded through a grant from the Sloan Foundation. The authors would like to thank Omar Khattab, William Held, Saurabh Shah, Aryaman Arora, Ken Liu, David Anugraha, Vishakh Padmakumar, Hao Zhu, Lakshya Agrawal, Yu Fei, Seungone Kim, and Jonathan Hilgart for their insightful comments and thoughts at various stages of the project. We would also like to thank SALT Lab and the Stanford NLP Group for help with review and revision of the manuscript. Finally we would like to thank Yijia Shao and Alex Spangher for testing and offering feedback on the AutoMetrics system.
:::

本工作部分受到 Stanford HAI 企业联属计划(Corporate Affiliate Program)的支持,会员经费由美国运通(American Express)提供;另获 Sloan 基金会资助。作者感谢 Omar Khattab、William Held、Saurabh Shah、Aryaman Arora、Ken Liu、David Anugraha、Vishakh Padmakumar、Hao Zhu、Lakshya Agrawal、Yu Fei、Seungone Kim 与 Jonathan Hilgart 在项目各阶段提出的深刻评论与想法;感谢 SALT Lab 与 Stanford NLP Group 协助审阅与修订稿件;最后感谢 Yijia Shao 与 Alex Spangher 对 AutoMetrics 系统的测试与反馈。

> **译注(附录未收录部分)**:References(参考文献)与附录 A–G 未收录,可查原文 PDF,要点如下——**附录 A** LLM 使用声明(论文由人类初撰、LLM 协助润色与编写代码,均经第一作者严格核验);**附录 B** MetricBank 详解:指标源自 Schmidtova et al. (2024) 对 INLG 2023 与 ACL 2023 Generation track 共 110 篇论文的调研(283 个自动指标、34 个指标族),实现其中最热门 16 族的前 28 个,再补充 NLTK / PyTorch / HF Lighteval / MetaMetrics 中的 12 个及最新论文中的 8 个,共 48 个(表 4:29 个参考型 + 19 个免参考型,覆盖 12 个领域);指标卡(Metric Card)仿 Model Card / Data Card 设计,含指标详情、预期用途、实现、已知局限等七个板块;**附录 C** 全部提示词与 DSPy 签名;**附录 D** BLEU 指标卡完整样例;**附录 E** 设计消融(E.1 检索算法对比 BM25 / ColBERT / Faiss 等,E.2 生成器设计细节与约 30 个设置上的消融);**附录 F** 补充实验(F.1 全部基线指标的敏感度/稳定度结果:Best Metric 相当稳定,LLM 系指标如 DnA-Eval、LLM-Judge、AutoMetrics 在鲁棒性上突出;另含更多任务/维度结果);**附录 G** AutoMetrics 指标报告示例(如 SimpEval 的 Top 5 指标与回归系数)。

## 要点速览

- 问题定位:主观开放任务(旅行规划、病历生成)没有可验证奖励,人类反馈稀疏且非描述性(点赞点踩),rubric 式 LLM-as-a-Judge 既难写也不保证被遵循——需要「自适应指标归纳」。
- 四步流水线:生成(10 单准则 + 5 量表 + 1 示例型 + 1 提示优化)→ 检索(MetricBank 48 指标,ColBERT+LLM 混合检索,k=30)→ 回归(两阶段 PLS,保留 n=5,剔除负相关生成指标)→ 报告(带权重、相关性与局限的可读文档)。
- MetricBank:48 个 NLP 指标(29 参考型 + 19 免参考型、12 领域),每个附「指标卡」记录描述、用途、实现与局限;指标卡本身被证明能改善检索效果。
- 评测方法论:借用心理测量学三效度——内容效度(透明报告 + 评审推理轨迹)、准则效度(Kendall τ 对人类标签)、构念效度(操作化为 Sensitivity/Stability 两个新测量,检验对降质敏感、对等价变换稳定)。
- 主结果:5 个任务(2 分布内 + 3 分布外)上,AutoMetrics 以 Qwen-3-32B 骨干全面最优(如 EvalGen τ=0.382 vs LLM-Judge 0.272),相对最强基线最高提升 33.4%(EvalGen,GPT-4o-mini 骨干)。
- 鲁棒性:对质量降质的敏感度 81.0%-97.8%(基线 50%),对无关扰动的稳定度也显著高于基线。
- 数据效率:约 80 条人类反馈即饱和;少于 80 条时默认「仅生成」模式,避免小样本下既有指标引入伪相关(高 p 低 n 问题)。
- 代理奖励验证:τ-Bench 航空任务上,以 AutoMetrics 为 GEPA 优化目标(2000 rollouts 后 0.720±0.06)追平甚至略优于可验证奖励(0.680±0.11),显著超过 0.6 基线(p<0.05)。
- 实践教训与局限:数据多样性 > 数量;人工监督剔除伪相关指标不可省;指标与骨干模型绑定,换模型需重新归纳;相关性不显著(p>0.05)时系统会告警。
- 与本周其他材料的呼应:AutoMetrics 是 Zheng2023「评审从哪来」的自动化答案,与 AutoLibra 同属「从人类反馈归纳评测标准」路线——前者用回归加权组合标量指标,后者用主题分析式聚类归纳行为指标。
