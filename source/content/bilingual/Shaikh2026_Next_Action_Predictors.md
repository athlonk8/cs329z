---
title: "Learning Next Action Predictors from Human-Computer Interaction"
title_zh: 从人机交互中学习下一动作预测器
authors: "Omar Shaikh, Valentin Teutschbein, Kanishk Gandhi, et al."
venue: "arXiv 2026 (Preprint) · Stanford University & HPI"
kind: paper
importance: recommended
tags: "下一动作预测, 主动式智能体, 强化学习, 用户建模, 被动数据标注, LLM-as-a-Judge"
summary: 形式化"下一动作预测(NAP)"任务,发布被动标注流水线 NAPsack(20 用户、1800 小时、36 万动作),并提出用 GRPO 端到端训练的 LongNAP 模型。
---

## 导读

本文是 GUM(通用用户模型)论文的直接续作,同属第 11 周"主动式智能体"专题。GUM 回答了"如何从观察中理解用户现在是谁",本文则更进一步:预测"用户接下来会做什么"。真正主动式 AI 系统必须在用户开口之前预判其需求,而这需要推理用户看到和做的一切,而不是只看提示词里那点稀疏信号。

论文做了两件事。**数据上**,作者形式化了下一动作预测(Next Action Prediction, NAP)任务,并开源 NAPsack 流水线:不要求用户手动标注,而是被动录制自然使用行为,再用视觉-语言模型(VLM)事后标注。他们据此标注了 20 名用户一个月的连续手机使用,共 36 万余条动作、1800 小时亮屏时间。**模型上**,作者提出 LongNAP(Long-context Next Action Predictor):结合参数化学习与上下文学习,先"为检索而推理"、再"为预测而推理",用 GRPO 策略梯度端到端训练。单用户训练时 LongNAP 比监督微调高 79%、比最强提示基线高 39%;在无限可能的动作空间中,17.1% 的预测轨迹与用户真实行为高度对齐(LLM 评审分 ≥0.5),高置信预测下升至约 26%。对于关心"智能体如何获得并利用长期用户记忆"的读者,这篇论文展示了从用户建模走向用户行为预测的完整技术路径。

## 全文对照翻译

> 译注:以下为中英对照全文翻译,英文部分为论文原文逐段照录(仅还原 PDF 提取时丢失的换行、斜体与公式排版,原文个别拼写笔误按原样保留),中文部分为对应段落的完整忠实翻译。页眉"Preprint."与 arXiv 标记行从略;References(参考文献)按站点惯例不收录;附录 A、B 含实质内容,照常收录。

### 标题与作者

::: en
Learning Next Action Predictors from Human-Computer Interaction

Omar Shaikh¹ Valentin Teutschbein²* Kanishk Gandhi¹*
Yikun Chi¹ Nick Haber¹ Thomas Robinson¹ Nilam Ram¹
Byron Reeves¹ Sherry Yang¹³ Michael S. Bernstein¹ Diyi Yang¹
¹Stanford University ²Hasso Plattner Institute ³New York University

\* Equal contribution. Correspondence to oshaikh@stanford.edu.
:::

从人机交互中学习下一动作预测器。作者:Omar Shaikh(斯坦福大学)、Valentin Teutschbein(哈索·普拉特纳研究所,\*同等贡献)、Kanishk Gandhi(斯坦福大学,\*同等贡献)、Yikun Chi、Nick Haber、Thomas Robinson、Nilam Ram、Byron Reeves、Sherry Yang(斯坦福大学/纽约大学)、Michael S. Bernstein、Diyi Yang(均为斯坦福大学)。通讯作者:oshaikh@stanford.edu。

### Abstract(摘要)

::: en
Truly proactive AI systems must anticipate what we will do next. This foresight demands far richer information than the sparse signals we type into our prompts — it demands reasoning over the entire context of what we see and do. We formalize this task as next action prediction (NAP): given a sequence of a user's multimodal interactions with a computer (screenshots, clicks, sensor data), predict that user's next action. Progress on this task requires both new data and modeling approaches. To scale data collection, we annotate longitudinal, naturalistic computer use with vision-language models. We release an open-source pipeline for performing this labeling on private infrastructure, and label over 360K actions across one month of continuous phone usage from 20 users, amounting to 1,800 hours of screen time. We then introduce LongNAP, a user model that combines parametric and in-context learning to reason over long interaction histories. LongNAP is trained via policy gradient methods to generate user-specific reasoning traces given some context; retrieve relevant traces from a library of past traces; and then apply retrieved traces in-context to predict future actions. Using an LLM-as-judge evaluation metric (0-1 similarity to ground truth), LongNAP significantly outperforms supervised finetuning and prompted baselines on held-out data (by 79% and 39% respectively). Additionally, LongNAP generalizes to held out users when trained across individuals. The space of next actions a user might take at any moment is unbounded, spanning thousands of possible outcomes. Despite this, 17.1% of LongNAP's predicted trajectories are well-aligned with what a user does next (LLM-judge score ≥ 0.5). This rises to 26% when we filter to highly confident predictions. In sum, we argue that learning from the full context of user behavior to anticipate user needs is now a viable task with substantial opportunity.
:::

真正主动式 AI 系统必须能预判我们下一步会做什么。这种远见所需的信息远比我们敲进提示框的稀疏信号丰富——它需要对"我们所见所做"的完整上下文进行推理。作者将这一任务形式化为**下一动作预测(next action prediction, NAP)**:给定用户与计算机的多模态交互序列(截图、点击、传感数据),预测该用户的下一个动作。该任务的进展同时需要新数据与新的建模范式。为扩展数据收集,作者用视觉-语言模型(vision-language models)对纵向(longitudinal)、自然主义的计算机使用进行标注:发布了一个可在私有基础设施上运行的开源标注流水线,并标注了 20 名用户一个月连续手机使用中的超过 36 万个动作,合计 1800 小时亮屏时间。随后,作者提出 LongNAP——一个结合参数化学习与上下文学习、在长交互历史上进行推理的用户模型。LongNAP 经策略梯度方法训练,流程为:给定上下文生成用户专属的推理轨迹(reasoning trace);从过去的轨迹库中检索相关轨迹;再将检索到的轨迹应用于上下文以预测未来动作。在用 LLM-as-a-judge(与真实未来动作的 0-1 相似度)的评估下,LongNAP 在留出数据上显著超过监督微调与提示基线(分别高出 79% 与 39%)。此外,跨多个用户训练的 LongNAP 能泛化到留出的新用户。任一时刻用户可能的下一动作空间是无界的,横跨数千种可能结果;尽管如此,17.1% 的 LongNAP 预测轨迹与用户实际行为高度对齐(LLM 评审分 ≥ 0.5),过滤高置信预测后升至 26%。总之,作者论证:从用户行为的完整上下文中学习、从而预判用户需求,如今已是一个可行且机会巨大的任务。

### 1 Introduction(引言)

::: en
Language models today are hopelessly restricted to seeing us through a narrow keyhole. They see our prompts to follow instructions (Ouyang et al., 2022), and they construct memories to make sense of these instructions (Packer et al., 2023). But the models know nothing of what brought us to them in the first place, and they know even less about us in general. Truly context-aware AIs should instead understand us deeply. What problems are we trying to solve? What constraints are we operating under? How do we act in the world, and how can our models best support us in those actions?
:::

今天的语言模型无可救药地被困在一个狭窄的"钥匙孔"里看我们:它们看到我们为下达指令而输入的提示(Ouyang et al., 2022),并为理解这些指令而构建记忆(Packer et al., 2023)。但模型对我们最初为何而来一无所知,对我们一般是什么样的人知道得更少。真正情境感知(context-aware)的 AI 应当转而深刻地理解我们:我们正在试图解决什么问题?我们在什么约束下运作?我们如何在世界上行动,而模型又如何在这些行动中最好地支持我们?

[图 1: Long-Context Next Action Predictors (LongNAPs) draw from the entirety of a user's multimodal context (e.g. screenshots)—retrieving over an unbounded history—to predict what they will do next. We train LongNAP end-to-end on data from 20 users over a month, spanning 1.9M screenshots or 1,800 hours of screen on-time. Predictions are rewarded based on LLM-judged similarity to a set of ground truth future actions.]

图 1(中文说明):长上下文下一动作预测器(LongNAP)从用户多模态上下文(如截图)的整体中提取信息——在一个无界历史上进行检索——以预测用户接下来会做什么。作者在 20 名用户一个月的数据上端到端训练 LongNAP,涵盖 190 万张截图、即 1800 小时亮屏时间;预测依据"与一组真值未来动作的 LLM 评审相似度"获得奖励。此图为全文的概念总览图:一位研究者收到通知、查看邮件、阅读论文评审,LongNAP 推理后预测其将查看 Weights and Biases 实验日志、再到 Slack 上与合作者分摊修改工作。

::: en
To achieve this goal, we need models that learn about us from our general interaction with computers—predicting what we are likely to need or do next—to enable proactive support. These models should reason over a broad history of our past interactions with our devices (not just our past prompts!) in order to forecast what we need help with before we ask. Success at this task requires training on rich, longitudinal behavioral data, enough to understand our patterns accurately and predict what we will do next. Much of this can run on infrastructure managed or owned by the user, preserving privacy.¹

¹ To enable running our work on local infrastructure, code and artifacts for this paper are available at https://generalusermodels.github.io/nap.
:::

要实现这一目标,我们需要能从我们与计算机的一般交互中学习"我们可能需要什么、接下来会做什么"的模型,从而提供主动式支持。这些模型应当在我们与设备交互的宽泛历史(而不只是我们过去的提示!)上推理,以便在我们开口**之前**预判我们需要什么帮助。这一任务的成功需要在丰富的纵向行为数据上训练,才能准确理解我们的行为模式并预测我们下一步会做什么。这一流程的大部分可以运行在用户自管或自有的基础设施上,以保护隐私。¹(¹ 为支持在本地基础设施上运行本文工作,论文代码与工件见 https://generalusermodels.github.io/nap 。)

::: en
We formalize this goal as a concrete prediction task we call next action prediction (NAP): given a sequence of the user's multimodal interactions with a computer (screenshots, keystrokes, clicks), predict that particular user's next action. For example (Fig. 1), consider a researcher who receives a notification, checks their email, then reads a set of paper reviews. A good next action predictor should be able to reason over this sequence, and over what it knows about the user's past habits, to predict that the user will: look through outstanding experiments on their experiment tracking log (e.g., Weights and Biases), then message their helpful coauthors² on Slack to divide up revisions.

² We extract this trajectory from the first author's user model, who depends heavily on their helpful coauthors for feedback.
:::

作者将这一目标具体化为一个明确的预测任务,称为**下一动作预测(NAP)**:给定用户与计算机多模态交互的序列(截图、键击、点击),预测该特定用户的下一个动作。例如(图 1),考虑一位研究者:他收到一条通知、查看邮件、然后读了一批论文评审。一个好的下一动作预测器应当能在这个序列、以及它所知的该用户过往习惯之上进行推理,预测该用户接下来会:翻看实验追踪日志(如 Weights and Biases)上尚在进行的实验,然后在 Slack 上联系他那几位乐于助人的合作者²分摊修改工作。(² 这条轨迹提取自第一作者本人的用户模型——他非常依赖其乐于助人的合作者的反馈。)

::: en
In this paper, we make progress on two fronts for next action prediction:

• Data. How do we collect and annotate the right kind of data for next action prediction at scale?

• Models. How do we train specialized models for contextual next action prediction that reason effectively over our long-context, multimodal interactions?
:::

本文在下一动作预测的两条战线上取得进展:

- **数据(Data)**:如何大规模地收集并标注适合下一动作预测的正确类型的数据?
- **模型(Models)**:如何训练能在长上下文、多模态交互上进行有效推理的专用上下文下一动作预测模型?

::: en
Collecting the right data is a prerequisite for progress on this task. Learning accurate models will require large, naturalistic datasets of low-level behavior traces. However, asking users to annotate everything they do is both impractical and expensive. We address this through passive supervision: rather than instructing users to complete specific tasks, we simply observe what they naturally do on their devices, and annotate traces post-hoc using a vision language model (VLM) pipeline. This approach lets us see not what people say they do, but what they actually do. We annotate a dataset of month-long phone use from 20 users, yielding over 360K actions over 1.8K hours of screen on-time. We release this passive data collection pipeline, NAPsack, as an open source package for users to install for themselves.
:::

收集合适的数据是这一任务取得进展的先决条件。学习准确的模型将需要大规模、自然主义的底层行为轨迹数据集。然而,要求用户标注自己做的一切,既不现实又昂贵。作者通过**被动监督(passive supervision)**解决这一问题:不去指示用户完成特定任务,而是单纯观察他们在设备上自然做了什么,再用视觉-语言模型(VLM)流水线事后标注轨迹。这一方式让我们看到的不是人们**说**自己做什么,而是他们**实际**做什么。作者标注了 20 名用户为期一个月的手机使用数据集,得到 1800 小时亮屏时间内的超过 36 万条动作。作者将这一被动数据收集流水线以 **NAPsack** 之名作为开源包发布,供用户自行安装使用。

::: en
With a dataset in hand, how should we train models that reason effectively over these long, multimodal interaction histories? A natural approach would be to learn user patterns directly in model weights through finetuning, building on LLMs that already exhibit social reasoning capabilities (Gandhi et al., 2023; Ziems et al., 2024). However, parametric models struggle with latent learning: the ability to acquire and retain information that has no immediate relevance to the current task, but that can be retrieved and applied when it becomes useful for future tasks (Lampinen et al., 2025). Patterns in model weights often fail to transfer flexibly to new situations, even when models readily use the same information in-context (Chan et al., 2022). Weight updates also require substantially more data than in-context learning to encode new patterns, limiting rapid adaptation to evolving user behavior (Brown et al., 2020; Bertsch et al., 2025). Placing all of a user's interaction history into the context window is also impractical. Context lengths are bounded, and indiscriminately including everything introduces noise that can degrade performance (Liu et al., 2024).
:::

有了数据集,又该如何训练能在这些长而多模态的交互历史上有效推理的模型?一种自然的做法是通过微调把用户模式直接学进模型权重,以本就具备社会推理能力的 LLM 为基础(Gandhi et al., 2023; Ziems et al., 2024)。然而,参数化模型在**潜伏学习(latent learning)**上有困难:即获取并保留那些对当前任务没有直接用处、但在未来任务中变得有用时可以被检索与应用的信息的能力(Lampinen et al., 2025)。模型权重中的模式常常无法灵活迁移到新情境,哪怕模型在上下文中能随时使用同样的信息(Chan et al., 2022)。权重更新也需要比上下文学习多得多的数据才能编码新模式,限制了对不断演变的用户行为的快速适应(Brown et al., 2020; Bertsch et al., 2025)。把用户全部交互历史塞进上下文窗口同样不现实:上下文长度有界,而且不加区分地全放入会引入噪声、损害性能(Liu et al., 2024)。

[图 2: LongNAP significantly outperforms all baselines by at least 39.4% relative to the strongest baseline. We evaluate with LLM-judge, which outputs similarity to ground truth future actions (0-1 score). Performance is averaged across 20 models trained on individual users.]

图 2(中文说明):LongNAP 相对最强基线至少高出 39.4%,显著超过所有基线。评估采用 LLM 评审,输出与真值未来动作的相似度(0-1 分);性能为在单个用户数据上训练的 20 个模型的平均值。

::: en
Rather than relying solely on parametric or in-context learning, we train models that learn to retrieve relevant past reasoning and observations into context, allowing them to leverage strong in-context learning capabilities during the training process. We instantiate this insight in a two-stage model we call LongNAP (Long-context Next Action Predictor), trained end-to-end via policy gradient algorithms. In the first phase, LongNAP reasons to retrieve: the model reasons about what the user is currently doing, then uses that reasoning to search a memory of past observations and inferences. For example (see Fig. 1), seeing that the user just opened difficult paper reviews, LongNAP might retrieve a reasoning trace that it previously generated, noting that the user will message coauthors to divide work. In the second phase, LongNAP reasons to predict: the model integrates retrieved traces to refine its reasoning and predict future actions. Traces that lead to good predictions are saved back into memory, so the library improves over time. To score predictions, we introduce a temporal reward: since we can simply wait and see what the user actually does, we use an LLM-as-a-judge to measure semantic similarity between predicted and actual future actions. This lets us optimize both stages end-to-end through policy optimization.
:::

作者不单纯依赖参数化学习或上下文学习,而是训练模型**学会把相关的过往推理与观察检索进上下文**,从而在训练过程中利用强大的上下文学习能力。作者将这一思路实例化为一个两阶段模型 **LongNAP(Long-context Next Action Predictor,长上下文下一动作预测器)**,经策略梯度算法端到端训练。第一阶段,LongNAP **为检索而推理(reason to retrieve)**:模型先推理用户当前正在做什么,再用该推理去搜索由过往观察与推断构成的记忆。例如(见图 1),看到用户刚打开一堆棘手的论文评审,LongNAP 可能会检索出它此前生成过的一条推理轨迹,其中记着"该用户会发消息给合作者分摊工作"。第二阶段,LongNAP **为预测而推理(reason to predict)**:模型整合检索到的轨迹,精炼其推理并预测未来动作。能带来好预测的轨迹会被写回记忆,因此轨迹库会随时间改善。为给预测打分,作者引入**时间性奖励(temporal reward)**:既然只需等一等就能看到用户实际做了什么,就用 LLM-as-a-judge 度量预测与真实未来动作之间的语义相似度。这使两个阶段都能通过策略优化进行端到端训练。

::: en
In our evaluations, we show that LongNAPs successfully predict future actions when trained on data from a single user, significantly outperforming supervised finetuning (by 79%) and prompted baselines (by 39%). In addition, we show that LongNAPs can generalize to entirely new users when trained on multiple users, again outperforming baselines (by 13% over our best baseline—a few-shot prompted, closed-source model). The space of next actions a user might take at any moment is unbounded, spanning thousands of possible outcomes. Despite this, 17.1% of LongNAP's predicted trajectories are well-aligned with what a user actually does next (LLM-judge score ≥ 0.5 on a 0–1 scale). This rises to 26% when we filter to highly-confident predictions.
:::

在评估中,作者证明:只用单个用户的数据训练,LongNAP 就能成功预测未来动作,显著超过监督微调(高 79%)与提示基线(高 39%)。此外,在多个用户上训练的 LongNAP 能泛化到全新用户,同样超过各基线(比最强基线——few-shot 提示的闭源模型——高 13%)。任一时刻用户可能采取的下一动作空间是无界的,横跨数千种可能结果;尽管如此,17.1% 的 LongNAP 预测轨迹与用户实际接下来做的事高度对齐(LLM 评审分在 0-1 尺度上 ≥ 0.5)。过滤到高置信预测时,这一比例升至 26%。

::: en
In sum, we contribute a Long-context Next Action Predictor (LongNAP): a model that retrieves and reasons over rich, multimodal interaction histories to predict what a user will do next. To collect data for LongNAP, we contribute NAPsack: a pipeline that collects and annotates naturalistic behavior traces passively with VLMs, demonstrating that labeled interaction data can be obtained without any active user effort. LongNAPs trained on this data show strong single-user and moderate cross-user generalization. Finally, we discuss applications of LongNAP, along with privacy considerations and implications of deploying personalized predictive models on user devices.
:::

总之,作者贡献了 LongNAP(长上下文下一动作预测器):一个在丰富、多模态的交互历史上检索并推理、以预测用户下一步行为的模型。为给 LongNAP 收集数据,作者贡献了 NAPsack:一条用 VLM 被动收集并标注自然主义行为轨迹的流水线,证明无需用户任何主动付出即可获得带标注的交互数据。在该数据上训练的 LongNAP 展现出强大的单用户泛化与中等的跨用户泛化。最后,作者讨论了 LongNAP 的应用,以及在用户设备上部署个性化预测模型的隐私考量与影响。

### 2 Next Action Prediction(下一动作预测)

::: en
In this section, we formalize the next action prediction task and walk through a concrete example. NAP requires operating over a temporal stream of user interaction events $E = \{e_1, e_2, \ldots, e_T\}$, where each event $e_t = (a_t, I_t)$ consists of an action $a_t$ and optional visual observations $I_t$. Here, actions are at the granularity of tasks described in natural language that could be delegated to a computer-use agent (Anthropic, 2024; Xie et al., 2024; Wang et al., 2025b). Below is an example of what $E$ might look like for a user who needs a NAP:

$$E = \begin{cases} e_1 = (\text{snoozes alarm},\ \texttt{img 1.png})\ 07{:}00, \\ e_2 = (\text{snoozes alarm},\ \texttt{img 2.png})\ 07{:}01, \\ e_3 = (\text{snoozes alarm},\ \texttt{img 3.png})\ 07{:}02, \\ \ldots \end{cases}$$

Given a query time $t$ and a context window containing $k$ recent events $E_{t-k:t} = \{e_{t-k}, \ldots, e_t\}$, the goal is to predict future events $\hat{E}_{t+1:t+h} = \{\hat{e}_{t+1}, \ldots, \hat{e}_{t+h}\}$ that may occur over some horizon $h$, where $h$ and $k$ are parameters set by the user. $E$ is completely unstructured interaction data—the event stream consists of an arbitrary collection of natural language and images.
:::

本节形式化下一动作预测任务,并走查一个具体例子。NAP 要求在用户交互事件的时间流 $E = \{e_1, e_2, \ldots, e_T\}$ 上操作,其中每个事件 $e_t = (a_t, I_t)$ 由一个动作 $a_t$ 与可选的视觉观察 $I_t$ 组成。这里,动作的粒度是"可以用自然语言描述、并且可以委托给计算机使用智能体(computer-use agent)执行的任务"(Anthropic, 2024; Xie et al., 2024; Wang et al., 2025b)。下面是一个"需要 NAP 的用户"的 $E$ 可能的样子:

$$E = \begin{cases} e_1 = (\text{贪睡闹钟},\ \texttt{img 1.png})\ 07{:}00, \\ e_2 = (\text{贪睡闹钟},\ \texttt{img 2.png})\ 07{:}01, \\ e_3 = (\text{贪睡闹钟},\ \texttt{img 3.png})\ 07{:}02, \\ \ldots \end{cases}$$

给定查询时刻 $t$ 与包含 $k$ 个近期事件的上下文窗口 $E_{t-k:t} = \{e_{t-k}, \ldots, e_t\}$,目标是预测在某个视野(horizon)$h$ 内可能发生的未来事件 $\hat{E}_{t+1:t+h} = \{\hat{e}_{t+1}, \ldots, \hat{e}_{t+h}\}$,其中 $h$ 与 $k$ 是由用户设定的参数。$E$ 是完全非结构化的交互数据——事件流由自然语言与图像的任意组合构成。

::: en
We can model this process using a vision-language model (VLM) policy $\pi_\theta$ that generates future event trajectories $\hat{E}_{t+1:t+h}$ given recent context $E_{t-k:t}$. A model trained for contextual behavior prediction would sample from the distribution $\hat{E}_{t+1:t+h} \sim p^\pi_\theta(\cdot \mid E_{t-k:t})$, where $p^\pi_\theta(E_{t-k:t})$ gives the likelihood of a trajectory $\hat{E}_{t+1:t+h}$ under $\pi$. For example, conditioned on repeated alarm-snoozing behavior, a $p^\pi_\theta(E_{t-k:t})$ might predict the following future trajectory:

$$\begin{aligned} &(\text{snoozes alarm}),\ (\text{dismisses alarm}),\ (\text{opens phone}) \\ \sim\ & p^\pi_\theta(\cdot) \; \big|\; (\text{snoozes alarm}, \texttt{img 1.png}),\ (\text{snoozes alarm}, \texttt{img 2.png}),\ (\text{snoozes alarm}, \texttt{img 3.png}) \end{aligned}$$

Two challenges arise from this problem statement. The first concerns data: how do we scalably collect and annotate a large sample of action data $E$ across many users? Once we have enough data, we must also effectively train $p^\pi_\theta(E_{t-k:t})$. We cover both challenges in (§3; data) and (§4; model) respectively.
:::

可以用一个视觉-语言模型(VLM)策略 $\pi_\theta$ 来建模这一过程:给定近期上下文 $E_{t-k:t}$,生成未来事件轨迹 $\hat{E}_{t+1:t+h}$。一个为上下文行为预测而训练的模型会从分布 $\hat{E}_{t+1:t+h} \sim p^\pi_\theta(\cdot \mid E_{t-k:t})$ 中采样,其中 $p^\pi_\theta(E_{t-k:t})$ 给出轨迹 $\hat{E}_{t+1:t+h}$ 在 $\pi$ 下的似然。例如,以反复贪睡闹钟的行为为条件,某个 $p^\pi_\theta(E_{t-k:t})$ 可能预测出如下未来轨迹:

$$\begin{aligned} &(\text{贪睡闹钟}),\ (\text{关闭闹钟}),\ (\text{拿起手机}) \\ \sim\ & p^\pi_\theta(\cdot) \; \big|\; (\text{贪睡闹钟}, \texttt{img 1.png}),\ (\text{贪睡闹钟}, \texttt{img 2.png}),\ (\text{贪睡闹钟}, \texttt{img 3.png}) \end{aligned}$$

这一问题陈述引出两大挑战。第一关涉数据:如何跨大量用户可扩展地收集并标注大规模动作数据 $E$?有了足够数据之后,还必须有效地训练 $p^\pi_\theta(E_{t-k:t})$。作者分别在(§3;数据)与(§4;模型)中处理这两个挑战。

### 3 Labeling Interaction Data At Scale(大规模标注交互数据)

::: en
Success on next action prediction requires large-scale, action-labeled data derived from real computer usage. Such data is scarce due to a high collection cost and practical constraints. It is also impractical to ask individual users to manually segment and annotate everything. We draw inspiration from systems that leverage existing data sources, such as tutorial videos for training computer use agents (Baker et al., 2022; Wang et al., 2025b; Lu et al., 2025) or passive trajectory data for learning world models in robotics (Yang et al., 2023). These approaches often rely on curated datasets, synthetic environments, or narrow task distributions. In our setting, we instead want to collect naturalistic, longitudinal, and open-ended computer use that reflects a particular user's behavior. To address this challenge, we introduce NAPsack: a passive tool for labeling interaction data from a user at scale.
:::

下一动作预测的成功需要源自真实计算机使用的大规模、带动作标注的数据。此类数据因高昂的收集成本与现实约束而稀缺;要求个体用户手动分段并标注一切同样不现实。作者从那些利用既有数据源的系统汲取灵感,例如用教学视频训练计算机使用智能体(Baker et al., 2022; Wang et al., 2025b; Lu et al., 2025),或用被动轨迹数据学习机器人世界模型(Yang et al., 2023)。这些方法往往依赖精选数据集、合成环境或狭窄的任务分布。而在本文的场景中,作者要收集的是自然主义、纵向、开放式、且反映**特定用户**行为的计算机使用。为此,作者提出 **NAPsack**:一个被动地大规模标注用户交互数据的工具。

#### 3.1 构建 NAPsack(Building NAPsack)

::: en
NAPsack first continuously records screenshots from computer use; this can include I/O events like mouse clicks, mouse movements, scroll events, and keyboard inputs. I/O events are first grouped into bursts of adjacent interactions of the same type (e.g. if a user clicks twice within ϵ time of each click, it is grouped; see §A.2 for more details). For each burst, NAPsack collects visual context in the form of screenshots of the currently active display before and after the interaction. This serves as a compression strategy; screenshots are only stored when the user actively interacts with the system.
:::

NAPsack 首先持续录制计算机使用的截图;还可以采集 I/O 事件,如鼠标点击、鼠标移动、滚动事件与键盘输入。I/O 事件先被分组成"突发(burst)"——相邻的同类交互(例如,若用户两次点击彼此相隔不超过 ϵ 时间,则归为一组;详见 §A.2)。对每个突发,NAPsack 以"交互前后当前活动显示器的截图"形式采集视觉上下文。这是一种**压缩策略**:只有当用户主动与系统交互时才保存截图。

::: en
Because bursts corresponding to different event types may temporally overlap, all input events and screenshots are merged into a single, time-ordered sequence. This sequence is first split into 60-frame chunks, which are provided as input to a VLM. We split to keep context lengths short, since VLMs often forget details as context length increases (Chandrasegaran et al., 2024). The VLM is tasked with aggregating one or more consecutive screenshots, optionally annotated with low-level input events that follow (IO, such as keypresses and mouse movements), into higher-level user actions and generating a natural-language action caption.
:::

由于不同事件类型对应的突发可能在时间上重叠,所有输入事件与截图被合并为一个按时间排序的单一序列。该序列先被**切分(split)**成 60 帧的块,再交给 VLM。之所以切块,是为了保持上下文长度短,因为 VLM 常会随上下文变长而遗忘细节(Chandrasegaran et al., 2024)。VLM 的任务是:把一张或多张连续截图(可选地附带其后发生的低层输入事件,即 IO,如按键与鼠标移动)聚合为更高层的用户动作,并生成自然语言的动作描述(action caption)。

::: en
Each resulting data sample consists of a screenshot, a generated action description (e.g., Clicked the 'Downloads' folder in the sidebar.), and the associated input events recorded after that screenshot and before the next one. We intentionally adopt this level of granularity to describe a user's actions because it is better suited for downstream training and directly compatible with prior work on computer-use agents (Wang et al., 2025b). To ensure consistent caption granularity and style, we few-shot prompt the VLM (see §A.3).³

³ One can change the underlying prompts to target higher levels of abstraction in the labeled actions, but there is a tradeoff: higher-level labels require more longitudinal screenshot data.
:::

每条最终数据样本由一张截图、一条生成的动作描述(如 "Clicked the 'Downloads' folder in the sidebar.",点击了侧栏中的 "Downloads" 文件夹)、以及在该截图之后、下一张截图之前记录的关联输入事件组成。作者有意采用这一粒度来描述用户动作,因为它更适合下游训练,且与计算机使用智能体的既有工作直接兼容(Wang et al., 2025b)。为确保描述粒度与风格一致,作者对 VLM 采用 few-shot 提示(见 §A.3)。³(³ 也可以更换底层提示,把标注动作对准更高的抽象层级,但存在权衡:层级更高的标签需要更多的纵向截图数据。)

#### 3.2 用 LLM 评审评估与真实标注的相似度(Evaluating Ground-Truth Similarity with an LLM Judge)

[图 3: NAPsack enables passive collection of human-computer interaction data. It ingests screenshots and input events, compresses them to retain only meaningful frames, and annotates with action descriptions.]

图 3(中文说明):NAPsack 支持被动地收集人机交互数据。它摄取截图与输入事件,压缩以只保留有意义的帧,并用动作描述加以标注。

::: en
We evaluate NAPsack by comparing generated action captions against ground-truth annotations, testing different data collection and preprocessing strategies for quality and storage efficiency. To benchmark performance, three 10-minute personal computer usage sessions were recorded by an author. Then, two authors produced a total of 354 human-annotated ground-truth action descriptions across the raw screen recordings and input event logs (details in §A.4)

Conditions From these recordings, four captioning variants were constructed: (1) naively captioning the full 10-minute inputs with a single prompt, (2) splitting the raw input into 60 frame segments before captioning, (3) applying NAPsack's event based heuristic for data compression with temporal splitting, and (4) additionally conditioning caption generation on captured input events (IO).

Similarity with an LLM Judge For each chunk, we used Gemini 3.0 Flash as a judge, producing a continuous similarity score from 0 (no match) to 1 (perfect match) between ground-truth and a candidate trajectory. Let $H^*_{t+1:t+h} = \{e^*_{t+1}, \ldots, e^*_{t+h}\}$ denote the ground-truth events that actually occurred after time $t$. Given a candidate set of labels $\hat{E}_{t+1:t+h} = \{\hat{e}_{t+1}, \ldots, \hat{e}_{t+h}\}$, we can use an LLM to compute a similarity $\mathrm{sim}(\hat{E}_{t+1:t+h}, E^*_{t+1:t+h})$ that measures how well the ground-truth events align with labels produced by each of our baselines. The judge model is prompted to holistically assess similarity to the reference actions.
:::

作者通过把生成的动作描述与真值标注作对比来评估 NAPsack,检验不同数据收集与预处理策略的质量与存储效率。为建立基准,一位作者录制了三段各 10 分钟的个人电脑使用;随后两位作者在原始录屏与输入事件日志上共产出 **354 条人工标注**的真值动作描述(细节见 §A.4)。

**条件(Conditions)**:从这些录屏构造四种标注变体:(1)**naive**,用单条提示直接标注全部 10 分钟输入;(2)**splitting**,标注前先把原始输入切成 60 帧的段;(3)在时间切分之上应用 NAPsack 的基于事件启发式做数据**压缩**;(4)再额外以采集到的输入事件(IO)条件化描述生成。

**与 LLM 评审的相似度(Similarity with an LLM Judge)**:对每个块,作者用 Gemini 3.0 Flash 作为评审(judge),在真值与候选轨迹之间输出 0(完全不匹配)到 1(完美匹配)的连续相似度分。设 $H^*_{t+1:t+h} = \{e^*_{t+1}, \ldots, e^*_{t+h}\}$ 表示时刻 $t$ 之后实际发生的真值事件。给定一组候选标签 $\hat{E}_{t+1:t+h} = \{\hat{e}_{t+1}, \ldots, \hat{e}_{t+h}\}$,可以用 LLM 计算相似度 $\mathrm{sim}(\hat{E}_{t+1:t+h}, E^*_{t+1:t+h})$,度量真值事件与各基线产出的标签的吻合程度。评审模型被提示从整体上评估与参考动作的相似度。

**表 1:不同 LLM 评审相似度分下候选轨迹 $\hat{E}$ 的定性示例(自左至右分数递减),均与同一条人工标注的真值轨迹 $H^*$ 对比评估。为便于阅读,原文用红色标出意图严重错误的动作。**

| # | 真值(Ground-Truth) | 预测(Score = 0.72) | 预测(Score = 0.52) | 预测(Score = 0.15) |
|---|---|---|---|---|
| 1 | 切到 "Australia vs Zimbabwe" 标签页,进入全屏 | 切到 "Australia vs Zimbabwe" 标签页,进入全屏 | 切到 "Australia vs Zimbabwe" 标签页,点击播放器 | 点击 YouTube 主页,浏览推荐视频 |
| 2 | 点击 "Key Moments" 区域的缩略图 | 点击视频播放器时间轴以快进 | 按 "f" 在板球视频上进入全屏 | 点击标题为 "Best Cricket Catches of 2025" 的视频 |
| 3 | 按 "esc" 退出全屏 | 按 "esc" 退出全屏 | 按 "esc" 退出全屏 | 按 "esc" 退出全屏 |
| 4 | 切到 W&B 工作区,点击 "Runs" 图标 | 切到 W&B 工作区,滚动浏览仪表盘 | 打开新标签页,在地址栏输入 "wandb.ai" | 在 Google 搜索栏输入 "australia cricket schedule" |
| 5 | 切到 "Australia vs Zimbabwe",进入全屏 | 切到 "Australia vs Zimbabwe" 标签页,进入全屏 | 滚动浏览 W&B 的训练指标图表 | 点击搜索结果中的 ESPN Cricinfo 链接 |
| 6 | 按 "esc" 退出全屏 | 按 "esc" 退出全屏 | 点击 W&B 仪表盘的 "Table" 视图 | 在 ESPN Cricinfo 上滚动浏览即将进行的比赛 |
| 7 | 切到 W&B 标签页,滚动浏览图表 | 切到 W&B 标签页,点击某张图表 | 切到 YouTube,点击推荐视频 | 点击 Chrome 后退按钮返回搜索结果 |
| 8 | 滚动浏览 W&B 仪表盘 | 点击 W&B 工作区的 "Table" 视图 | 在 YouTube 上滚动浏览评论区 | 切到 Gmail 标签页查看新邮件 |

(表 1 中文说明:第一列为人工真值;三列预测的评审分依次为 0.72、0.52、0.15。0.72 分的预测与真值逐步对应、只有细节偏差;0.52 分保留核心意图(板球视频与 W&B 交替)但具体交互漂移;0.15 分整体意图错误——把工作流预测成了看板球集锦与查赛程。译注:原文表格另有 Score = 1.0 一列,因与真值列内容一致,在 PDF 文本提取中被并入真值列,故此处从略;按定义 1.0 分即完美匹配。)

::: en
Qualitatively, we observe that LLM judges generate more useful scores compared to embedding based or lexical metrics (Zheng et al., 2023). To get a sense for judge scores, we highlight examples of similarity scores in Tab. 1 across various ground-truth/candidate pairs. The exact judge prompt along with additional scored pairs are provided in §A.3.

LLM Judge Results For LLM judge results, we first sample a trajectory of 8 ground-truth, human-annotated labels $H^*$, along with a candidate subsequence that covers the same timespan $\hat{E}$ from each condition. We generate 45 ground-truth sequences, each with a complementary candidate sequence from each condition. Tab. 2 reports mean LLM-as-a-judge scores comparing each candidate to the ground truth, together with the corresponding data storage requirements.⁴

⁴ File sizes are computed by concatenating final selected frames into an .mp4 video.

Our judge shows that splitting input (+ split) substantially improves caption quality compared to providing the entire session at once (naive; 0.48 → 0.57). Using only frames where a user interacts with their computer (+ compress) achieves comparable caption quality while reducing storage by approximately 70% (295 MB → 76 MB). Finally, conditioning on input events further improves scores (IO; 0.60 → 0.70); I/O data may provide complementary supervision beyond visual context alone.
:::

定性上看,作者观察到 LLM 评审比基于嵌入或词法的指标产生更有用的分数(Zheng et al., 2023)。为了让读者对评审分有感觉,表 1 罗列了多组真值/候选对上的相似度分示例。确切的评审提示与更多已评分对见 §A.3。

**LLM 评审结果(LLM Judge Results)**:作者先采样一条含 8 条人工标注真值标签的轨迹 $H^*$,并从每个条件各取覆盖同一时间跨度的候选子序列 $\hat{E}$。共生成了 45 条真值序列,每条都配有来自各条件的互补候选序列。表 2 报告了各候选与真值对比的平均 LLM-as-a-judge 分数,以及相应的数据存储需求。⁴(⁴ 文件大小按把最终选出的帧拼接成一段 .mp4 视频计算。)

评审结果显示:与一次性提供整段会话(naive;0.48 → 0.57)相比,切分输入(+ split)显著提升描述质量;只保留用户与计算机交互的帧(+ compress)可获得相当的描述质量,同时把存储降低约 70%(295 MB → 76 MB);最后,以输入事件条件化进一步提升分数(IO;0.60 → 0.70)——I/O 数据或许能提供视觉上下文之外的互补监督。

**表 2:NAPsack 在不损害质量的前提下,把有效标注需要保存的数据量减少约 75%。事件驱动的压缩(只在用户与计算机交互时保存帧)带来效率提升;I/O 信号进一步提升性能。性能以 LLM 评审分([0, 1])与人工评估(胜率)度量;95% 置信区间经 bootstrap 计算。**

| 方法 | 评审分(↑) | 人工胜率 %(↑) | 大小(↓) |
|---|---|---|---|
| naive | 0.48±0.03 | 19.2±6.7 | 295 MB |
| + split | 0.57±0.03 | 45.4±8.7 | 295 MB |
| + split + compress | 0.60±0.03 | 49.6±8.9 | 76 MB |
| + split + compress + IO | 0.70±0.03 | 85.8±6.0 | 76 MB |

(表 2 中文说明:四种标注条件逐级提升——naive 即单条提示标注全部输入;+split 先切 60 帧段;+compress 加入基于事件的压缩;+IO 再以输入事件条件化生成。)

::: en
Human Validation To validate our LLM judge, two authors independently labeled pairwise preferences across conditions. For each pair, annotators were shown a ground-truth sequence alongside one sample from each condition and asked to select the better match (ties counted as 0.5 wins for each). Altogether, this results in 240 total comparisons across both annotators. We report aggregate win rates averaged across both annotators (Tab. 2). Human win-rates validate our LLM judge evaluation. Splitting inputs provides a significant improvement over naively providing an entire video session as input (19.2% → 45.4%); compression does not significantly affect quality (45.4% → 49.6%); and adding IO input significantly improves quality (49.6% → 85.8%). We attribute these gains to the ability to capture short, keyboard-heavy interactions (single terminal commands or window switching) when I/O is available, a detail overlooked in purely frame-based variants. Together, our evaluation justifies NAPsack's use for future scaling of accurate, action-labeled trajectories.
:::

**人工验证(Human Validation)**:为验证 LLM 评审,两位作者独立地对各条件做两两偏好标注。对每一对,标注者会看到一条真值序列与来自各条件的一个样本,并被要求选出更匹配者(平局各计 0.5 胜)。合计两位标注者共进行 240 次比较;表 2 报告了两位标注者的平均总胜率。人工胜率验证了 LLM 评审的结论:切分输入相对"直接提供整段视频会话"有显著提升(19.2% → 45.4%);压缩不显著影响质量(45.4% → 49.6%);加入 IO 输入则显著提升质量(49.6% → 85.8%)。作者把这些增益归因于:I/O 可用时能够捕捉短促、键盘密集的交互(单条终端命令或窗口切换)——这是纯帧方法忽略的细节。综合起来,这一评估证明了用 NAPsack 去规模化产出准确、带动作标注轨迹的正当性。

#### 3.3 用 NAPsack 标注数据集(Annotating a Dataset with NAPsack)

::: en
We now turn to annotating a large-scale dataset for training models and experimentation.

Screenomics Collecting a large scale dataset of real-world computer interaction is challenging. As a starting point, we draw on Screenomics (Reeves et al., 2021), and a study from the Human Screenome Project (Reeves et al., 2020), a repository of ≈ 170M continuous timelapse screenshots collected from 257 adult users' mobile phone activity over time. Given the highly sensitive nature of the data, collection and annotation of the Screenomics data was first approved by the Stanford Institutional Review Board. All modeling was done on secure servers approved for processing personal data at the first author's institution.

Subsampling Screenomics We begin by sampling a set of 20 users who used their devices for at least an hour every day for a month. Demographic details on the 20 users are in §A.5. Our final sampled time window occurs between March 16, 2021 and April 12, 2021, and consists of 1.9M screenshots, covering 1,837 hours of total screen on-time.
:::

现在转向为模型训练与实验标注一个大规模数据集。

**Screenomics**:收集大规模的真实世界计算机交互数据集很有挑战。作为起点,作者利用 Screenomics(Reeves et al., 2021)以及"人类屏幕组学计划"(Human Screenome Project;Reeves et al., 2020)的一项研究——一个由 257 名成年用户随时间推移的手机活动收集而来的、约 1.7 亿张连续延时截图的仓库。鉴于数据高度敏感,Screenomics 数据的收集与标注首先获得了斯坦福机构审查委员会(Institutional Review Board, IRB)的批准;所有建模都在第一作者所在机构经批准处理个人数据的安全服务器上完成。

**抽样(Subsampling Screenomics)**:作者先抽取 20 名"一个月内每天至少使用设备一小时"的用户;这 20 名用户的人口统计细节见 §A.5。最终抽样的时间窗口为 2021 年 3 月 16 日至 2021 年 4 月 12 日,包含 190 万张截图,覆盖总计 1837 小时的亮屏时间。

::: en
Annotating with NAPsack We feed each user's screenshot data into NAPsack, yielding a total of 360K event descriptions. Screenomics does not capture IO data, so we omit this from the input to NAPsack, compressing instead with a difference in image hash (see §A.5). On average, each event description $E_i$ covers ≈ 15 seconds of time, yielding a total of 359,219 actions. Events describe a diverse set of activities, from gaming and shopping, to banking, messaging, and social media browsing. Across 20 users over 28 days, average daily screen time was 4h 32m, ranging from 2h 17m (lightest) to 6h 52m (heaviest). While we validate our captioning processes, labels from NAPsack are model-generated, and can still be noisy. Alignment with human ground-truth is not perfect. This may introduce errors later in training; we revisit this in our limitations section (§10).
:::

**用 NAPsack 标注(Annotating with NAPsack)**:作者把每位用户的截图数据喂入 NAPsack,共得到 36 万条事件描述。Screenomics 不采集 IO 数据,因此 NAPsack 输入中省略了 IO,改用图像哈希差异做压缩(见 §A.5)。平均而言,每条事件描述 $E_i$ 覆盖约 15 秒,总计产出 **359,219 条动作**。事件描述了多样的活动:从游戏、购物到银行、消息与社交媒体浏览。28 天内、20 名用户的平均每日亮屏时间为 4 小时 32 分,最轻 2 小时 17 分、最重 6 小时 52 分。尽管作者验证了标注流程,NAPsack 的标签仍是模型生成的,仍可能有噪声;与人工真值的对齐并不完美,这可能在后续训练中引入误差——作者在局限一节(§10)再作讨论。

### 4 Long-Context Next Action Predictors (LongNAP)(长上下文下一动作预测器)

[图 4: Predictions from LongNAP are generated in a two-phase process. In the first phase, LongNAP Reasons to Retrieve: conditioned on what the user sees right now (e.g. a set of paper reviews), LongNAP generates a reasoning trace and uses it to retrieve past traces. Using retrieved traces, LongNAP Reasons to Predict: generating a final reasoning trace, adding it back to memory, and then predicting the next steps a user might take. The predicted trajectory is compared against a ground truth (with an LLM-as-a-judge similarity score), and then LongNAP is optimized with GRPO (Shao et al., 2024b).]

图 4(中文说明):LongNAP 的预测经两阶段流程生成。第一阶段,LongNAP **为检索而推理**:以用户当前所见(如一批论文评审)为条件,生成一条推理轨迹并用它检索过往轨迹。利用检索到的轨迹,LongNAP 再**为预测而推理**:生成最终推理轨迹、写回记忆,然后预测用户可能采取的后续步骤。预测轨迹与真值对比(得到 LLM-as-a-judge 相似度分),再用 GRPO(Shao et al., 2024b)优化 LongNAP。

::: en
To predict what a user might do next, we must be able to reason effectively over the entirety of their context—retrieving and re-using specific details or insights across potentially infinite observations. This is challenging with just weight-based learning, as a model must be able to use new information immediately: if a user checks their calendar and sees a 2 P.M. meeting, that detail should inform predictions right away, not after further gradient updates. Our model must learn from a single observation, and many relevant details (a new appointment, a message from a collaborator) appear only once and are never repeated in the training data (Chan et al., 2022).

We instead exploit the ability of LLMs to quickly adapt via in-context learning (Brown et al., 2020). While it would be ideal for the context window to be unbounded, we are constrained by practical context limitations of LLMs. Thus, we design a learning architecture for LongNAPs and train them with a two phase generation process. They reason to retrieve relevant past context (old observations and reasoning traces); then reason to predict the final set of next actions.
:::

要预测用户接下来可能做什么,我们必须能对其上下文的**整体**进行有效推理——在可能无限的观察中检索并复用具体的细节或洞见。仅靠基于权重的学习很难做到这一点,因为模型必须能**立即**使用新信息:如果用户查了日历、看到下午两点有个会,这一细节应当马上影响预测,而不是等若干次梯度更新之后。模型必须能从单次观察中学习,而许多相关细节(一个新的日程、一条来自合作者的消息)只出现一次,在训练数据中再也不会重复(Chan et al., 2022)。

作者转而利用 LLM 通过上下文学习快速适应的能力(Brown et al., 2020)。虽然上下文窗口最好是无界的,但 LLM 的实际上下文限制摆在那里。因此,作者为 LongNAP 设计了一种学习架构,以两阶段生成流程训练:先**为检索而推理**,找到相关的过往上下文(旧的观察与推理轨迹);再**为预测而推理**,得到最终的下一动作集合。

#### 4.1 为检索而推理、为预测而推理(Reasoning to Retrieve and Predict)

::: en
Implementing this generation requires a few prerequisites. First, we need a VLM policy π—we instantiate this VLM using Qwen-2.5-VL-7B (Bai et al., 2025). LongNAP maintains a memory $M_t$ of past entries available up to time $t$. Each memory entry pairs a set of observations with a reasoning trace: a chain-of-thought, $z$, generated by the model during a previous prediction (e.g., User received paper reviews; based on past behavior, they tend to procrastinate on writing but eventually coordinate with coauthors via Slack; Fig. 1). To search over this memory, we instantiate a lexical retriever $R$, using BM25 (Robertson et al., 1995). Only entries with timestamps $\tau \leq t$ are accessible, preventing access to future information. The policy $\pi$ is then tasked with continuously retrieving from and updating this memory as new events occur and new reasoning traces are generated. Below, we walk through how LongNAP processes the example in Fig. 4.
:::

实现这一生成需要一些前置条件。首先需要一个 VLM 策略 $\pi$——作者用 Qwen-2.5-VL-7B 实例化(Bai et al., 2025)。LongNAP 维护一个截至时刻 $t$ 可用的过往条目记忆 $M_t$。每个记忆条目把一组观察与一条**推理轨迹(reasoning trace)**配对:$z$ 是模型在以往某次预测中生成的思维链(例如:"User received paper reviews; based on past behavior, they tend to procrastinate on writing but eventually coordinate with coauthors via Slack",用户收到了论文评审;根据过去行为,他们倾向于拖延写作,但最终会通过 Slack 与合作者协调;见图 1)。为在这份记忆上检索,作者实例化了一个词法检索器(lexical retriever)$R$,采用 BM25(Robertson et al., 1995)。只有时间戳 $\tau \leq t$ 的条目可被访问,以杜绝"偷看未来"信息。策略 $\pi$ 的任务是:随着新事件发生、新推理轨迹生成,持续地检索并更新这份记忆。下面走查 LongNAP 如何处理图 4 中的例子。

::: en
Phase 1: Reasoning to Retrieve. Suppose a user browses aimlessly, receives a notification, checks their email, and reads a set of paper reviews. Given these k recent observations, the model first generates reasoning about what might come next: $z_{\text{retrieve}} \sim p_\theta(\cdot \mid E_{t-k:t})$ (Fig. 4; top). Reasoning traces from the model speculate on the user's context and stable traits; in our example, the model might reason: Received reviews on paper with collaborators . . . user may revise paper after viewing feedback. This reasoning serves a dual purpose: it makes the model's current thinking explicit, and it provides a semantic query for retrieving relevant history. Using $z_{\text{retrieve}}$ as a query, we retrieve entries $D = R(z_{\text{retrieve}}, M_t)$ from memory. Here, the retriever might surface past (abridged) traces such as Procrastinates heavily on paper writing and figures, Prefers using Slack to collaborate, and Delegates work amongst collaborators.
:::

**阶段一:为检索而推理。** 设想一位用户先是漫无目的地浏览,随后收到一条通知、查看邮件、并读了一批论文评审。给定这 $k$ 条近期观察,模型先生成关于接下来可能发生什么的推理:$z_{\text{retrieve}} \sim p_\theta(\cdot \mid E_{t-k:t})$(图 4 上)。模型的推理轨迹会对用户的情境与稳定特质进行推测;在本例中,模型可能推理:"Received reviews on paper with collaborators . . . user may revise paper after viewing feedback"(收到了合作论文的评审……用户可能在看完反馈后修改论文)。这段推理一石二鸟:既显式化了模型当前的思考,又为检索相关历史提供了语义查询。以 $z_{\text{retrieve}}$ 为查询,从记忆中检索条目 $D = R(z_{\text{retrieve}}, M_t)$。这里,检索器可能命中的过往(节选)轨迹包括:"Procrastinates heavily on paper writing and figures"(在论文写作和图表上严重拖延)、"Prefers using Slack to collaborate"(偏好用 Slack 协作)、"Delegates work amongst collaborators"(在合作者间分派工作)。

::: en
Phase 2: Reasoning to Predict. The model then revises its initial prediction by integrating the retrieved context (Fig. 4; bottom): $z_{\text{predict}} \sim p_\theta(\cdot \mid E_{t-k:t}, z_{\text{retrieve}}, D)$. In Phase 1, the model already speculated about what comes next, but it did so without any historical context from the memory about the user. Now, the retrieved traces about this user's procrastination habits, preference for Slack, and tendency to delegate allow the model to revise. What started as a generic Received reviews . . . user may revise paper after viewing feedback becomes: Based on past patterns, user will message coauthors to divide tasks, check which experiments have been run. Conditioned on this revised reasoning, the model predicts concrete future actions: $\hat{E}_{t+1:t+h} \sim \pi_\theta(\cdot \mid E_{t-k:t}, D, z_{\text{predict}})$, predicting the user will scroll through Weights & Biases, open Slack and navigate to #research, and message collaborators with outstanding TODOs.
:::

**阶段二:为预测而推理。** 模型随后整合检索到的上下文来修订其初始预测(图 4 下):$z_{\text{predict}} \sim p_\theta(\cdot \mid E_{t-k:t}, z_{\text{retrieve}}, D)$。在阶段一,模型已经对"接下来会发生什么"做过推测,但当时没有任何关于该用户的记忆历史可用。现在,检索到的关于该用户拖延习惯、Slack 偏好与分派倾向的轨迹让模型得以修订。最初那句泛泛的 "Received reviews . . . user may revise paper after viewing feedback" 变成了:"Based on past patterns, user will message coauthors to divide tasks, check which experiments have been run"(基于过往模式,用户会联系合作者分派任务、查看哪些实验已经跑过)。以这段修订后的推理为条件,模型预测具体的未来动作:$\hat{E}_{t+1:t+h} \sim \pi_\theta(\cdot \mid E_{t-k:t}, D, z_{\text{predict}})$,预测用户将滚动查看 Weights & Biases、打开 Slack 并进入 #research 频道、给合作者发去尚未完成的 TODO。

::: en
During training, we sample 4 candidate traces for each phase, producing 4 complete retrieve-and-predict rollouts. After prediction, we save the prediction trace with the highest reward back to memory, updating $M_{t+1} = M_t \cup \{(E_{t-k:t}, z^*_{\text{predict}}, t)\}$. This ensures the memory accumulates the model's best reasoning over time.
:::

训练时,每个阶段采样 4 条候选轨迹,组成 4 个完整的"检索+预测"展开(rollout)。预测结束后,把**奖励最高**的预测轨迹写回记忆,更新为 $M_{t+1} = M_t \cup \{(E_{t-k:t}, z^*_{\text{predict}}, t)\}$。这确保记忆随时间累积模型的最佳推理。

#### 4.2 优化 LongNAP(Optimizing LongNAPs)

::: en
LongNAP is trained end-to-end, learning how to generate initial reasoning, what to retrieve from memory, and how to revise its reasoning for accurate predictions. Because generation involves discrete steps (reasoning in language, calling a retriever), we optimize via policy gradients, using GRPO (Shao et al., 2024b; Liu et al., 2025) for variance reduction with a group size of 4. We use LoRA (Hu et al., 2022) due to memory constraints, where RL results generally match full finetuning (Schulman & Lab, 2025). Additional hyperparameter details for both training and calling our retriever are in §B.1

Temporal Reward Formulation The temporal structure of our task provides a natural training signal: we can verify rollout quality by comparing predicted actions against observed future behavior. In other words, we can just wait and see if the user does what we predict. Here, we re-use the same validated LLM Judge for NAPsack (in §3.2, Gemini 3.0 Flash as the underlying LLM) and apply this as our reward. To allow the LLM to distinguish between each completion more effectively, we also pass the entire group at once to the model, and prompt the model to assign rewards all at once.
:::

LongNAP 端到端训练:学会如何生成初始推理、从记忆中检索什么、以及如何修订推理以做出准确预测。由于生成包含离散步骤(用语言推理、调用检索器),作者采用策略梯度优化,用 GRPO(Shao et al., 2024b; Liu et al., 2025)做方差缩减,组大小(group size)为 4。受内存限制使用 LoRA(Hu et al., 2022)——RL 的结果通常与全量微调相当(Schulman & Lab, 2025)。训练与调用检索器的其余超参数细节见 §B.1。

**时间性奖励表述(Temporal Reward Formulation)**:任务的时间性结构提供了天然的训练信号:可以通过把预测动作与观察到的未来行为对比来验证 rollout 质量。换句话说,只需等一等,看用户是否做了我们预测的事。这里作者复用 NAPsack 中那个经验证的 LLM 评审(§3.2,底层 LLM 为 Gemini 3.0 Flash),将其作为奖励。为了让 LLM 更有效地区分各条补全,作者还把整组展开一次性交给模型,并提示它一次性赋予奖励。

::: en
Training With Memory There are a handful of complications that come with adding memory. First, we want historical reasoning and observations to accrue over time in memory. Predicting what a user will do next by starting immediately in the middle of the dataset (e.g. after a shuffle) is challenging. We instead train over the data chronologically, and reset memory at the end of each epoch. Second, we mask retrieved tokens since they come from the environment, following search engine tool-use (Jin et al., 2025). Finally, we apply a form of "dropout" to our retriever. We randomly drop (10% of the time), re-order (10%), or provide no items (10%) as context. We find that this generally stabilizes training, preventing collapse when memory is reset at the start of an epoch.
:::

**带记忆训练(Training With Memory)**:加入记忆会带来一些麻烦。其一,作者希望历史推理与观察能随时间在记忆中累积;直接从数据集中段(例如打乱之后)开始预测用户下一步做什么非常困难,因此作者按时间顺序在数据上训练,并在每个 epoch 结束时重置记忆。其二,对检索到的 token 做**掩码(mask)**,因为它们来自环境——沿用搜索引擎工具使用的做法(Jin et al., 2025)。最后,对检索器施加一种"**dropout**":以 10% 的概率随机丢弃、10% 的概率乱序、10% 的概率什么都不给作为上下文。作者发现这总体上能稳定训练,防止 epoch 开始时记忆重置导致的崩塌。

### 5 Experimental Setup(实验设置)

::: en
With our dataset (§3.3) and model (§4), we turn to evaluating LongNAPs in two settings. First, we evaluate if a LongNAP trained on a single user generalizes over time, predicting what that single user will do in the future. Second, we test if LongNAPs trained on many users generalize to entirely new ones. In both settings, we evaluate LongNAP against prompted and supervised-finetuned baselines, and show that LongNAP significantly outperforms baselines.
:::

有了数据集(§3.3)与模型(§4),作者在两种设置下评估 LongNAP。第一,评估在单个用户上训练的 LongNAP 能否随时间泛化,预测该用户未来会做什么。第二,检验在多个用户上训练的 LongNAP 能否泛化到全新用户。两种设置下,作者都把 LongNAP 与提示基线及监督微调基线对比,并证明 LongNAP 显著优于基线。

#### 5.1 实验与评估切分(Experiments and Evaluation Splits)

::: en
Prediction Event Horizon Before we outline experiments, we fix a few parameters for consistency across experiments. LongNAP samples $\hat{E}_{t+1:t+h} \sim p^\pi_\theta(\cdot \mid E_{t-k:t})$, so we need to define both how many events we should predict $h$ and how many events should be in the context window $k$. We take a sliding window over all our ground truth events $E$ to generate this dataset. Both the future action horizon $h$ and past actions $k$ are hyperparameters that can change depending on the prediction task. For now, we set the context window to 16 events, and future prediction to 8 events. We leave exploring different horizons and contexts to future work.

Generalizing Over Time Here, we aim to understand if LongNAP generalizes over time, predicting actions one user might do in the future. This requires training 20 models, one for each participant. We split temporally within participants: the first two weeks of data are for training (9.1K actions on average per user), the third week for validation (4.4K), and the fourth week for test (4.4K).

Generalizing to New Users In this setup, we aim to see if LongNAP can generalize to entirely new users. We train a single model over many users, and then evaluate on new, unseen users. To do this, we split our annotated data of 20 users into 10 randomly-selected users in train, 5 in validation, and 5 in test. While we have a single policy $\pi_\theta$, we cannot share memory between users, so we also instantiate a separate memory per-user (e.g. 10 separate memories are maintained during training). During the generation process, a model only indexes into the retriever for the specific user.
:::

**预测事件视野(Prediction Event Horizon)**:在展开实验之前,先固定几个参数以保持各实验一致。LongNAP 采样 $\hat{E}_{t+1:t+h} \sim p^\pi_\theta(\cdot \mid E_{t-k:t})$,因此需要同时定义要预测多少个事件 $h$、以及上下文窗口里放多少个事件 $k$。作者对所有真值事件 $E$ 做滑动窗口来生成该数据集。未来动作视野 $h$ 与过去动作数 $k$ 都是超参数,可依预测任务而变。目前,作者把上下文窗口设为 16 个事件、未来预测设为 8 个事件;不同视野与上下文的探索留作未来工作。

**时间泛化(Generalizing Over Time)**:这里要理解 LongNAP 能否随时间泛化,预测某个用户未来可能做的动作。这需要训练 20 个模型,每位参与者一个。作者在参与者内部按时间切分:前两周数据用于训练(人均 9.1K 条动作),第三周用于验证(4.4K),第四周用于测试(4.4K)。

**泛化到新用户(Generalizing to New Users)**:此设置旨在考察 LongNAP 能否泛化到全新用户:在多个用户上训练单一模型,再在未见过的新用户上评估。为此,作者把 20 名用户的标注数据切分为随机抽取的 10 名训练、5 名验证、5 名测试。虽然只有单一策略 $\pi_\theta$,但记忆不能跨用户共享,因此还要为每名用户实例化独立记忆(例如训练期间维护 10 份独立记忆)。生成过程中,模型只在该特定用户自己的检索器上索引。

#### 5.2 自动化指标与人工验证(Automated Metrics and Human Validation)

::: en
To measure the closeness of our predicted events $\hat{E}_{t+1:t+h}$ to the ground truth $E^*_{t+1:t+h}$, we employ two metrics. First, we again re-use our validated LLM-judge for comparing similarity between ground truth and predicted trajectories (§3.2). The LLM judge provides us with a more granular sense for low-level correctness. To understand the upper bound in LongNAP performance, we also report pass@k performance. The pass@k evaluation involves drawing k samples (temp = 1.0) from each model, and scoring an instance "correct" if any of the k samples is deemed close enough to the ground truth. Here, we pick a high cut-off for our LLM judge score (judge > 0.50).

At a threshold of 0.50, our calibrated judge (§3.2) indicates that the predicted and actual trajectories share the same actions, though some details or ordering may differ. For example, a predicted trajectory of Opens Chrome, navigates to a Weights & Biases dashboard, adjusts a chart slider, inspects training metrics and a ground truth of Opens Chrome, scrolls through the Weights & Biases dashboard, clicks into a specific pipeline chart, switches to the terminal are rated 0.6—the core workflow (examining experiment metrics) overlaps, but specific interactions and subsequent steps differ. In contrast, Opens YouTube, watches music videos, browses recommended content and Opens Chrome, analyzes experiment dashboards, switches to the terminal to debug a pipeline are rated 0.0, with no meaningful overlap in intent or activity. A cutoff of 0.50 for our judge enables us to roughly identify which trajectories are mostly correct.
:::

为度量预测事件 $\hat{E}_{t+1:t+h}$ 与真值 $E^*_{t+1:t+h}$ 的接近程度,作者采用两个指标。第一,再次复用那个经验证的 LLM 评审来比较真值与预测轨迹的相似度(§3.2);它为我们提供了对底层正确性更细粒度的感知。第二,为理解 LongNAP 性能的上界,作者还报告 **pass@k**。pass@k 评估从每个模型抽取 $k$ 个样本(temp = 1.0),若任一样本被认为与真值足够接近,该实例即记"正确"。这里,作者为 LLM 评审分选了一个较高的截断(judge > 0.50)。

在 0.50 这一阈值下,作者校准过的评审(§3.2)表明:预测轨迹与实际轨迹共享相同的动作,只是某些细节或顺序可能不同。例如,预测轨迹 "Opens Chrome, navigates to a Weights & Biases dashboard, adjusts a chart slider, inspects training metrics"(打开 Chrome、进入 W&B 仪表盘、调整图表滑块、查看训练指标)与真值 "Opens Chrome, scrolls through the Weights & Biases dashboard, clicks into a specific pipeline chart, switches to the terminal"(打开 Chrome、滚动 W&B 仪表盘、点进某个流水线图表、切到终端)被评为 0.6——核心工作流(查看实验指标)重叠,但具体交互与后续步骤不同。相比之下,"Opens YouTube, watches music videos, browses recommended content"(打开 YouTube、看音乐视频、浏览推荐内容)与 "Opens Chrome, analyzes experiment dashboards, switches to the terminal to debug a pipeline"(打开 Chrome、分析实验仪表盘、切到终端调试流水线)被评为 0.0,意图与活动没有任何有意义的重叠。评审的 0.50 截断使我们能粗略识别哪些轨迹大体正确。

::: en
We also measure model confidence for a given trajectory. We compute the intra-cluster variance of 20 sampled predictions. First, we embed each sample using a sentence transformer (using the all-MiniLM-L6-v2 model; Wang et al. (2020); Reimers & Gurevych (2019)). We then compute the average squared Euclidean distance from each embedding to their centroid (similar to Farquhar et al. (2024)). Lower variance indicates higher agreement among samples, which we interpret as higher model confidence. We convert these values to per-user percentile ranks to account for individual differences in baseline spread.

Finally, we conduct a small-scale human eval to validate our LLM judge. Two authors independently labeled pairwise preferences across methods, resulting in 300 total comparisons. For each pair, annotators were shown a ground-truth sequence alongside one output from each method and asked to select the better match based on overall quality (ties counted as 0.5 wins for each). Pairs were sampled in a stratified fashion across users to ensure each user is well-represented. We report aggregate win rates averaged across both annotators.
:::

作者还为每条轨迹度量**模型置信度(model confidence)**:计算 20 次采样预测的簇内方差。首先用句向量转换器(all-MiniLM-L6-v2 模型;Wang et al. (2020); Reimers & Gurevych (2019))嵌入每个样本;然后计算各嵌入到其质心的平均平方欧氏距离(类似 Farquhar et al. (2024))。方差越低说明样本间一致性越高,作者将其解释为模型置信度越高。再把这些值转换为用户内百分位排名,以消除个体间基线离散度的差异。

最后,作者做了一次小规模**人工评估**来验证 LLM 评审。两位作者独立地对各方法做两两偏好标注,合计 300 次比较。对每一对,标注者会看到一条真值序列与来自每种方法的各一条输出,并被要求按总体质量选出更匹配者(平局各计 0.5 胜)。样本对跨用户分层抽样,以确保每名用户都被充分代表。作者报告两位标注者的平均总胜率。

#### 5.3 基线(Baselines)

::: en
Our baselines consist of closed and open models, both across prompting and finetuning methods. For prompting, we have a zero-shot baseline, where we give the model the immediate past actions the user took, and simply prompt it to predict what the user would do next. We additionally implement a basic few-shot RAG baseline, where we use past actions as a query for retrieving. Prompts for the above baselines are in §B.2. For finetuned baselines, we evaluate supervised finetuning, testing if simply finetuning over the set of actions is helpful. For closed models, we evaluate prompted baselines with Gemini's 3.0 Flash.⁵ For open models, we prompt and finetune Qwen-2.5-VL-7B (Bai et al., 2025).

⁵ We use Flash since preliminary experiments show marginal improvements over Pro for a fraction of the cost.
:::

基线涵盖闭源与开源模型,以及提示与微调两类方法。提示类包括一个 **zero-shot** 基线:把用户刚做过的近期动作给模型,直接提示它预测用户下一步会做什么;另外实现了一个基础 **few-shot RAG** 基线:用过往动作作为检索查询。上述基线的提示见 §B.2。微调类基线评估**监督微调(supervised finetuning, SFT)**,检验单纯在动作集合上微调是否有帮助。闭源模型方面,用 Gemini 3.0 Flash 做提示基线评估;⁵ 开源模型方面,对 Qwen-2.5-VL-7B 做提示与微调(Bai et al., 2025)。(⁵ 选用 Flash 是因为初步实验显示其相对 Pro 的提升微乎其微,而成本只是零头。)

### 6 Results(结果)

::: en
We synthesize takeaways from our evaluation, with main results summarized in Tab. 3 and Tab. 5.

LongNAP can learn from just a single user, predicting their future interaction When we train on just a single user, LongNAP is able to predict what the user does next with significantly higher accuracy compared to baselines. When we compare against SFT on Qwen-2.5-VL-7B, LongNAP achieves 79% higher performance (0.21 → 0.38). LongNAP also substantially outperforms prompted baselines. LongNAP achieves 106% higher performance than zero-shot prompting (0.18 → 0.38) and 88% higher performance compared to few-shot prompting (0.20 → 0.38). These gains extend to closed-source models: LongNAP achieves 43% and 39% higher performance than zero-shot (0.26 → 0.38) and few-shot (0.27 → 0.38) prompted Gemini 3.0 Flash, respectively.

Our human evaluation further validates these findings (Tab. 4). LongNAP achieves a 79% win rate against other methods, substantially outperforming SFT (29.5%), zero-shot (33%), and RAG (45%) baselines on Qwen 2.5 VL. Notably, LongNAP also surpasses stronger closed-source baselines, beating both zero-shot (55%) and RAG-prompted (59%) Gemini.
:::

作者提炼评估中的关键结论,主要结果汇总于表 3 与表 5。

**LongNAP 能只从单个用户学习,预测其未来交互。** 只在单个用户上训练时,LongNAP 能以显著高于基线的准确率预测该用户接下来做什么。与 Qwen-2.5-VL-7B 上的 SFT 相比,LongNAP 性能高出 79%(0.21 → 0.38)。LongNAP 也大幅超过提示基线:比 zero-shot 提示高 106%(0.18 → 0.38),比 few-shot 提示高 88%(0.20 → 0.38)。这些增益同样延伸到闭源模型:LongNAP 分别比 zero-shot(0.26 → 0.38)与 few-shot(0.27 → 0.38)提示的 Gemini 3.0 Flash 高 43% 与 39%。

人工评估进一步验证了这些发现(表 4)。LongNAP 对其他方法取得 79% 的胜率,大幅超过 Qwen 2.5 VL 上的 SFT(29.5%)、zero-shot(33%)与 RAG(45%)基线;值得注意的是,LongNAP 也超过了更强的闭源基线,战胜了 zero-shot(55%)与 RAG 提示(59%)的 Gemini。

**表 3:在单个用户上训练显著优于基线方法,相对最强基线(Gemini Few-shot RAG)平均性能提升 39.4%(+0.11)。报告的是由 LLM 评审(§3.2)判定的与真值未来动作的相似度分(0-1)。$u_i$ 表示在 20 用户数据集中单个用户上训练的 LongNAP 实例,$u_\mu$ 表示全部 20 个单独训练模型的平均性能。**

| 用户 | Gemini Zero-shot | Gemini RAG | Qwen-2.5-VL-7B Zero-shot | Qwen-2.5-VL-7B RAG | Qwen-2.5-VL-7B SFT | LongNAP |
|---|---|---|---|---|---|---|
| u1 | 0.28 | 0.29 | 0.21 | 0.23 | 0.23 (+0.12) | **0.41** |
| u2 | 0.21 | 0.22 | 0.15 | 0.17 | 0.18 (+0.12) | **0.34** |
| u3 | 0.23 | 0.23 | 0.19 | 0.18 | 0.17 (+0.10) | **0.33** |
| u4 | 0.24 | 0.23 | 0.14 | 0.16 | 0.17 (+0.09) | **0.32** |
| u5 | 0.23 | 0.24 | 0.18 | 0.16 | 0.16 (+0.10) | **0.34** |
| u6 | 0.24 | 0.25 | 0.16 | 0.20 | 0.19 (+0.12) | **0.37** |
| u7 | 0.40 | 0.42 | 0.20 | 0.22 | 0.40 (+0.04) | **0.46** |
| u8 | 0.23 | 0.24 | 0.15 | 0.18 | 0.17 (+0.15) | **0.39** |
| u9 | 0.25 | 0.25 | 0.18 | 0.21 | 0.22 (+0.12) | **0.37** |
| u10 | 0.29 | 0.29 | 0.24 | 0.26 | 0.24 (+0.10) | **0.39** |
| u11 | 0.26 | 0.26 | 0.17 | 0.17 | 0.19 (+0.04) | **0.30** |
| u12 | 0.25 | 0.27 | 0.18 | 0.22 | 0.26 (+0.13) | **0.40** |
| u13 | 0.26 | 0.26 | 0.18 | 0.20 | 0.19 (+0.11) | **0.37** |
| u14 | 0.27 | 0.28 | 0.20 | 0.21 | 0.18 (+0.08) | **0.36** |
| u15 | 0.23 | 0.25 | 0.17 | 0.20 | 0.20 (+0.11) | **0.36** |
| u16 | 0.24 | 0.24 | 0.17 | 0.18 | 0.21 (+0.17) | **0.41** |
| u17 | 0.25 | 0.25 | 0.17 | 0.18 | 0.15 (+0.10) | **0.34** |
| u18 | 0.27 | 0.27 | 0.17 | 0.22 | 0.16 (+0.11) | **0.38** |
| u19 | 0.41 | 0.41 | 0.28 | 0.27 | 0.30 (+0.05) | **0.46** |
| u20 | 0.24 | 0.26 | 0.15 | 0.17 | 0.24 (+0.15) | **0.41** |
| uµ | 0.26 | 0.27 | 0.18 | 0.20 | 0.21 (+0.11) | **0.38** |

(表 3 中文说明:SFT 列括号内为相对其自身 zero-shot 基线的增量。LongNAP 在全部 20 个用户上都取得最高分,范围 0.30-0.46。)

**表 4:人工评估显示 LongNAP 的胜率显著更高。展示各方法的两两人工评估胜率(2 位标注者合计、共 300 次比较、95% bootstrap 置信区间)。**

| 模型 | 方法 | 胜率(%) |
|---|---|---|
| Qwen 2.5 VL | LongNAP | **79.0±6.6** |
| | SFT | 29.5±6.9 |
| | Few-shot RAG | 45.0±7.6 |
| | Zero-shot | 33.0±7.2 |
| Gemini | Few-shot RAG | 58.5±6.8 |
| | Zero-shot | 55.0±7.7 |

::: en
LongNAP can learn from many users, generalizing to entirely new users. We find that LongNAP, when trained on many users at once, generalizes to new users. While the gains are not as large as in the single-user setting, LongNAP still substantially outperforms prompted open-source baselines. In particular, LongNAP achieves 66% higher performance than zero-shot prompting Qwen-2.5-VL-7B and 53% higher performance than few-shot prompting. Improvements over the closed-source baseline (Gemini 3.0 Flash) are more modest: LongNAP achieves 19% and 13% higher performance than zero-shot and few-shot prompting, respectively. These are smaller gains relative to the single-user setting, so we suspect user-specific weights are especially effective for NAP. Scaling users may close this gap; we leave this to future work.

We also suspect that this variant of LongNAP relies more heavily on the reasoning to retrieve process. At inference time, LongNAP must learn general strategies for saving and retrieving user-specific inferences, depending less on parametric memorization and more on retrieval and in-context learning.
:::

**LongNAP 能从多个用户学习,泛化到全新用户。** 作者发现,同时在多个用户上训练时,LongNAP 能泛化到新用户。虽然增益不如单用户设置大,LongNAP 仍大幅超过开源提示基线:比 zero-shot 提示的 Qwen-2.5-VL-7B 高 66%,比 few-shot 提示高 53%。相对闭源基线(Gemini 3.0 Flash)的改进更温和:LongNAP 分别比 zero-shot 与 few-shot 提示高 19% 与 13%。这些增益小于单用户设置,因此作者推测**用户专属权重对 NAP 尤其有效**;扩大用户规模或许能缩小这一差距,留作未来工作。

作者还推测,这一 LongNAP 变体更依赖"为检索而推理"过程:推理时,LongNAP 必须学会保存与检索用户专属推断的**通用**策略——更少依赖参数化记忆,更多依赖检索与上下文学习。

[图 5: Some users are more predictable than others. When LongNAP is trained on a single user (in our generalizing over time experiments, §5.1), LLM-as-a-judge evals vary substantially from one user's LongNAP to another user's. In the above figure, we re-evaluate across checkpoints from training epochs for each user, highlighting variance.]

图 5(中文说明):有些用户比其他用户更可预测。当 LongNAP 在单个用户上训练时(即 §5.1 的时间泛化实验),LLM 评审评估结果在一个用户的 LongNAP 与另一个用户的 LongNAP 之间差异很大。图中对每个用户在各训练 epoch 的 checkpoint 上重新评估,以突出方差。

**表 5:在多个用户上联合训练时,LongNAP 对未见用户表现出适度的泛化,相对最强基线(同样是 Gemini Few-Shot RAG)平均性能提升 13.0%。报告由 LLM 评审(§3.2)判定的与真值未来动作的相似度。为检验对未见用户的泛化,随机在 10 个用户上训练、5 个上验证、5 个上测试(即上表所报)。$u_\mu$ 表示各评估用户上的平均性能,$u_i$ 表示在用户 $i$ 上的性能。**

| 模型 | 方法 | $u_\mu$ | u2 | u6 | u12 | u14 | u16 |
|---|---|---|---|---|---|---|---|
| Gemini | Zero-shot | 0.22 | 0.27 | 0.22 | 0.20 | 0.20 | 0.21 |
| | Few-shot RAG | 0.23 | 0.26 | **0.23** | 0.22 | 0.21 | 0.22 |
| Qwen VL | Zero-shot | 0.16 | 0.22 | 0.13 | 0.14 | 0.16 | 0.14 |
| | Few-shot RAG | 0.17 | 0.23 | 0.15 | 0.18 | 0.14 | 0.18 |
| | SFT | 0.17 | 0.22 | 0.14 | 0.16 | 0.15 | 0.17 |
| LongNAP | | **0.26** | **0.31** | **0.28** | **0.22** | **0.21** | **0.26** |

::: en
LongNAP's most confident predictions are aligned with what users actually do 26% of the time. To provide a more interpretable measure of performance, we report pass@k: the probability that at least one of k independent samples from a model exceeds a similarity threshold against the ground truth future trajectory. We selected an LLM-judge threshold of 0.5; trajectories that get this score are often well aligned with the actual intent of the user, but miss details or skip a few actions (see §5.2 for an example). At this threshold, LongNAP achieves 17.1% at pass@1 across users, rising to 36.3% at pass@20 (Fig. 9). In addition, we observe that model confidence, measured as intra-cluster variance among the 20 sampled trajectories, is correlated with accuracy (Fig. 10). For prompts in the 90th percentile of confidence (lowest variance), pass@1 rises to 25.9%.
:::

**LongNAP 最高置信的预测有 26% 的时间与用户实际行为对齐。** 为给出更可解释的性能度量,作者报告 pass@k:模型 $k$ 次独立采样中至少有一次超过与真值未来轨迹的相似度阈值的概率。作者选取 LLM 评审阈值 0.5;得到该分的轨迹往往与用户实际意图高度对齐,只是漏掉细节或跳过个别动作(示例见 §5.2)。在该阈值下,LongNAP 跨用户的 pass@1 为 **17.1%**,pass@20 升至 **36.3%**(图 9)。此外,作者观察到以 20 条采样轨迹簇内方差度量的模型置信度与准确率相关(图 10):在置信度第 90 百分位(方差最低)的提示上,pass@1 升至 **25.9%**。

[图 9: Pass@k scores for LongNAP. To count as a "pass," we selected an LLM-judge threshold of 0.5; trajectories that get this score are often well aligned with the actual intent of the user, but miss minor details or skip a few actions (see §5.2 for an example). At this threshold, LongNAP achieves 17.1% at pass@1 across users, rising to 36.3% at pass@20.]

图 9(中文说明):LongNAP 的 pass@k 分数。记为"通过(pass)"的标准取 LLM 评审阈值 0.5;得到该分的轨迹往往与用户实际意图高度对齐,只是漏掉次要细节或跳过个别动作(示例见 §5.2)。在该阈值下,LongNAP 跨用户的 pass@1 为 17.1%,pass@20 升至 36.3%。

[图 10: Empirical calibration of LongNAP. Confidence percentiles are computed per-user from intra-cluster variance of 20 sampled trajectories. Higher confidence prompts yield substantially higher pass@1 accuracy (25.9% vs. 10.3%).]

图 10(中文说明):LongNAP 的经验校准(empirical calibration)。置信度百分位按用户分别计算,依据是 20 条采样轨迹的簇内方差。置信度更高的提示带来显著更高的 pass@1 准确率(25.9% 对 10.3%)。

::: en
Predictability across users and generalization. While LongNAP results are on average better than our baselines, there is still substantial variability across users. For some users, relative improvement against the strongest baseline is limited, while for others, improvement is substantial. On u11, for example, the strongest baseline is Gemini (few-shot), which achieves a score of 0.26 with the LLM judge; LongNAP improves modestly to 0.30 – an absolute gain of 4 points (15% relative improvement). In contrast, on u8, the strongest baseline is Gemini few-shot (0.24), and LongNAP reaches 0.39, corresponding to a 15-point absolute gain (63% relative improvement). We suspect that some users are inherently more predictable. They repeat similar tasks each day, making them easier to model with finetuning or prompting alone, limiting the additional benefit of RL (Chu et al., 2025).
:::

**跨用户的可预测性与泛化。** 虽然 LongNAP 平均优于基线,用户间仍存在显著差异:有些用户相对最强基线的提升有限,有些则提升巨大。例如 u11,最强基线是 Gemini(few-shot),LLM 评审分 0.26;LongNAP 温和地提升到 0.30——绝对增益 4 个点(相对提升 15%)。相比之下,u8 的最强基线是 Gemini few-shot(0.24),LongNAP 达到 0.39,相当于绝对增益 15 个点(相对提升 63%)。作者怀疑部分用户**本质上更可预测**:他们每天重复相似的任务,仅靠微调或提示就易于建模,从而限制了 RL 的额外收益(Chu et al., 2025)。

### 7 What Makes LongNAP Work?(什么让 LongNAP 生效?)

::: en
In this section, we analyze the impact of various decisions in designing LongNAP (§7.1) and analyze how reasoning traces evolve over the course of training and across users (§7.2).
:::

本节分析设计 LongNAP 时的各项决策的影响(§7.1),并分析推理轨迹在训练过程中与跨用户的演变(§7.2)。

#### 7.1 算法消融(Algorithm Ablations)

::: en
We apply a handful of targeted ablations to LongNAP, surfacing the impact of various components. First, we ablate reasoning: we optimize LongNAP without generating reasoning traces for retrieval and prediction. Without reasoning, we retrieve only past observations, directly using the current observation as a query. In a separate ablation, we remove the retriever entirely, skipping the reasoning-to-retrieve step. Finally, we analyze the impact of our training order. We suspect chronological training over user traces helps model performance—reasoning traces accumulate and evolve in the order of observed interaction—so we shuffle our train data. To evaluate these ablations, we select a random subset of 5 users: the same subset of test users from our across-user generalization experiments (see Tab. 5 and §5.1).
:::

作者对 LongNAP 做了若干针对性消融,以揭示各组件的影响。第一,消融**推理(reasoning)**:优化 LongNAP 时不生成用于检索与预测的推理轨迹;没有推理时,只检索过往观察,直接用当前观察作为查询。第二,在另一项消融中**完全移除检索器**,跳过"为检索而推理"这一步。最后,分析训练顺序的影响:作者怀疑在用户轨迹上按时间顺序训练有助于模型性能——推理轨迹按观察交互的顺序累积与演化——因此把训练数据**打乱(shuffle)**。为评估这些消融,作者选取 5 名用户的随机子集:即跨用户泛化实验中的同一批测试用户(见表 5 与 §5.1)。

[图 6: At a given time (top), LongNAP is likely to retrieve over a substantial part of its past context (bottom) to predict what a user will do next. The visualization above (for a random user) shows what context from the past is retrieved for a query at the current time.]

图 6(中文说明):在给定时刻(上),LongNAP 很可能检索其过往上下文的相当大一部分(下)来预测用户下一步。上图(对一名随机用户)展示了当前时刻的一条查询从过去检索到了哪些上下文。

::: en
All ablations reduce performance to varying degrees (main results in Tab. 6). First, removing reasoning degrades performance substantially (by 19.2%, from 0.38 → 0.30). The same applies to retrieval: removing the ability to observe past reasoning and observations also degrades performance by 15.2% (0.38 → 0.32). To illustrate the impact of the retriever, we additionally visualize how context is retrieved over the course of training compared to the non-retriever ablation (Fig. 6). LongNAP learns to retrieve context from across its full interaction history, drawing on observations spread days apart rather than relying only on recent activity. Finally, shuffling the training data also has an impact (albeit smaller) on final performance: we observe a 9.3% relative reduction in performance compared to LongNAP (0.38 → 0.34).
:::

所有消融都在不同程度上降低性能(主要结果见表 6)。首先,移除推理使性能大幅下降(19.2%,0.38 → 0.30)。检索同理:失去观察过往推理与观察的能力也使性能下降 15.2%(0.38 → 0.32)。为展示检索器的影响,作者还可视化了训练过程中上下文如何被检索、并与"无检索器"消融对比(图 6):LongNAP 学会了从其**完整**交互历史中检索上下文,引用相隔数天的观察,而非只依赖近期活动。最后,打乱训练数据对最终性能也有影响(尽管较小):相对 LongNAP 观察到 9.3% 的相对性能下降(0.38 → 0.34)。

**表 6:推理与检索对 LongNAP 的性能都至关重要。作者选取一个随机用户子集做消融。移除推理组件导致平均性能最大幅下降(绝对 −0.07),移除检索器平均降低 −0.06。打乱数据集同样损害结果(−0.04),说明保持时间结构很重要。$u_\mu$ 表示各评估用户的平均性能,$u_i$ 表示在用户 $i$ 上的性能;消融在 5 名用户的随机子集上进行。**

| 模型 | | $u_\mu$ | u2 | u6 | u12 | u14 | u16 |
|---|---|---|---|---|---|---|---|
| LongNAP | | 0.38 | 0.34 | 0.37 | 0.40 | 0.36 | 0.41 |
| 消融 | → Remove reasoning | 0.30 (−0.07) | 0.25 (−0.09) | 0.30 (−0.06) | 0.35 (−0.09) | 0.27 (−0.06) | 0.35 (−0.06) |
| | → Remove retriever | 0.32 (−0.06) | 0.27 (−0.07) | 0.30 (−0.07) | 0.39 (−0.01) | 0.29 (−0.08) | 0.42 (+0.01) |
| | → Shuffle dataset | 0.34 (−0.04) | 0.29 (−0.05) | 0.32 (−0.04) | 0.40 (+0.00) | 0.32 (−0.05) | 0.41 (−0.00) |

(表 6 中文说明:括号内为相对 LongNAP 的绝对变化。Remove reasoning = 去推理;Remove retriever = 去检索器;Shuffle dataset = 打乱数据集。)

#### 7.2 推理轨迹分析(Analyzing Reasoning Traces)

::: en
In our ablations, we find that allowing the model to reason plays a critical role in LongNAP's performance. In some cases, these traces may serve as explanations for a particular user's decisions (Zhu et al., 2025). Here, we study how reasoning traces evolve during the course of training, across both reasoning for retrieval and for prediction.

First, we analyze reasoning lengths from users for every epoch of training, for 10 full epochs. Across training, we find that reasoning traces generally get shorter, both for retrieval and prediction phases (Fig. 8). Generally, traces for retrieval are shorter than for prediction (avg. 10.11 retrieval tokens v.s. 85.34 prediction). Thinking to retrieve traces become query-like (e.g. message Michael Diyi reminder or ice cream salted caramel youtube), likely optimized for the underlying BM25 retriever.

Analyzing the content of the prediction traces themselves, we find substantial variance across—and often even within—users. Qualitatively, many of these traces describe a user's habits and preferences. To get a sense for this, we embed reasoning traces with sentence-transformers (using the all-MiniLM-L6-v2 model; Wang et al. (2020); Reimers & Gurevych (2019)) and then visualize the embeddings (in Fig. 7).
:::

在消融中,作者发现允许模型推理对 LongNAP 的性能起着关键作用。某些情况下,这些轨迹或许可以作为对特定用户决策的解释(Zhu et al., 2025)。这里,作者研究推理轨迹在训练过程中的演变,涵盖为检索的推理与为预测的推理。

首先,分析 10 个完整训练 epoch 中各 epoch 的推理轨迹长度。整个训练过程中,检索与预测两个阶段的推理轨迹总体都在变短(图 8)。总体上,检索轨迹比预测轨迹短(平均检索 10.11 个 token,预测 85.34 个)。"为检索而思考"的轨迹变得像查询语句(例如 "message Michael Diyi reminder" 或 "ice cream salted caramel youtube"),很可能是针对底层 BM25 检索器优化了。

[图 8: Reasoning traces grow shorter across model training. Traces for the retrieve phase grow far shorter than queries for the predict phase (avg. 10.11 retrieval tokens v.s. 85.34 prediction). Qualitatively, we find that reasoning for the retrieve phase resembles queries to a retriever; while reasoning for the prediction phase resembles higher order descriptions of a user's behavior.]

图 8(中文说明):推理轨迹随模型训练推进而变短。检索阶段的轨迹远短于预测阶段的查询(平均检索 10.11 个 token,预测 85.34 个)。定性来看,检索阶段的推理近似于发给检索器的查询,而预测阶段的推理近似于对用户行为的更高阶描述。

分析预测轨迹本身的内容,作者发现轨迹在用户之间、甚至常常在用户内部都差异巨大。定性地说,许多轨迹描述了用户的习惯与偏好。为获得直观感受,作者用句向量转换器(all-MiniLM-L6-v2 模型;Wang et al. (2020); Reimers & Gurevych (2019))嵌入推理轨迹,并可视化嵌入(图 7)。

[图 7: LongNAP learns diverse reasoning strategies when trained on different users. Different colors correspond to different users. We embed (using the all-MiniLM-L6-v2 model; Wang et al. (2020); Reimers & Gurevych (2019)) and visualize traces from the reasoning to predict phase across a subset of users with tSNE. For some users (e.g. u7, blue, almost exclusively takes online surveys), reasoning strategies are homogenous. For others, LongNAP generates a library of reasoning patterns for specific contexts (u8; in orange).]

图 7(中文说明):在不同用户上训练时,LongNAP 学到多样的推理策略。不同颜色对应不同用户。作者嵌入(all-MiniLM-L6-v2 模型)并用 tSNE 可视化一部分用户"为预测而推理"阶段的轨迹。对某些用户(如 u7,蓝色,几乎只做在线问卷),推理策略是同质的;对另一些用户,LongNAP 则生成针对特定情境的推理模式库(u8,橙色)。

::: en
Some users have limited spread in reasoning traces. As a measure of spread, we compute the mean distance of all the user's embedded traces to the user centroid ($r_{\text{avg}}$). Consider the following trace from u7, a user who uses their phone almost exclusively to complete surveys online ($r_{\text{avg}}$ = 4.94):

The user's actions suggest a habitual and possibly patterned behavior of completing surveys and managing their Yahoo Mail inbox. This could involve clicking "Next" on a survey to "Continue," possibly indicating the completion of a set of survey questions...

Many of this user's traces are similar in content and style. In contrast, other users have models that produce more diverse traces, capturing variance in their behavior. u8 ($r_{\text{avg}}$ = 16.26) regularly goes house-hunting during the day:

The user systematically goes through an interactive map, view detailed photos of houses on the listing details page, and then pan again through the [ANONYMIZED] area properties.

and switches between various social media apps at night:

Since communication on personal social media platforms is a common activity, following the successful completion of Instagram Stories, the user may turn to other notifications to check for any incoming emails, messages from their list of contacts, or potential bottom notifications from social media apps.

While reasoning improves our models' predictive power, exploring if the reasoning itself is indeed faithful or accurate is an avenue for future work.
:::

有些用户的推理轨迹离散度有限。作为离散度的度量,作者计算该用户全部嵌入轨迹到用户质心的平均距离($r_{\text{avg}}$)。看 u7(一个几乎只用手机完成在线问卷的用户,$r_{\text{avg}}$ = 4.94)的如下轨迹:

"该用户的行为提示了一种完成问卷并管理其 Yahoo 邮箱的习惯性、可能模式化的行为。这可能包括在问卷上点击 'Next' 到 'Continue',或表明一组问卷问题的完成……"

该用户的许多轨迹在内容与风格上都相似。相比之下,另一些用户的模型会产生更多样的轨迹,捕捉其行为中的方差。u8($r_{\text{avg}}$ = 16.26)白天定期看房:

"该用户系统性地遍历一幅交互式地图,在房源详情页查看房屋照片,然后继续平移浏览 [匿名化] 区域的房源。"

夜间则在各种社交媒体应用之间切换:

"由于在个人社交媒体平台上交流是常见活动,在成功看完 Instagram Stories 之后,用户可能转向其他通知,查看是否有新邮件、联系人列表发来的消息、或社交媒体应用底部的通知。"

虽然推理提升了模型的预测能力,但探究这些推理本身是否**忠实(faithful)**或准确,是未来工作的一个方向。

### 8 Beyond Next Action Prediction(超越下一动作预测)

::: en
We outline two applications enabled by our work; namely the ability to learn entirely online from user interactions, and the ability to generalize as helpful assistants.

Learning online The distribution of a person's behavior is always shifting. As the person changes over time, so does the work they do and the patterns they exhibit. LongNAP should be able to adapt to this drift as we observe additional interaction data. In our work, we present data collection and training as two processes that occur synchronously, but this need not be the case! Instead of storing data and training offline with multiple epochs, we can convert the entire pipeline to run online, where training proceeds continuously in the background; or overnight (Lin et al., 2025). We call this version powerNAP. In powerNAP, NAPsack and LongNAP operate asynchronously: NAPsack continuously tracks and labels user actions, enqueueing them for training, while LongNAP consumes labeled actions from the queue and trains on them in a single pass, discarding data after use. Crucially, memory is never reset and reasoning traces accumulate, allowing the model to continually build a better representation of the user over time. We release powerNAP as a demo⁶ for users to try on their own data.

⁶ Available at https://github.com/GeneralUserModels/powernap

Assistants Once a user has a good LongNAP, we can anticipate what they want and intend to do. This should enable an assistant that finishes predictable tasks for users by acting on predictions about what the user would do next. While LongNAP is not a computer use agent, we can easily use it to pilot one. We release a simple version of such an assistant, called SleepWalk, which relies on an off-the-shelf computer use agent (Anthropic, 2024) to execute on actions predicted by LongNAP.
:::

作者概述本文工作启用的两个应用:完全在线地从用户交互中学习的能力,以及泛化为有用助手的能力。

**在线学习(Learning online)**:一个人的行为分布总在漂移。随着人随时间变化,其工作与呈现的模式也在变化。随着观察到更多交互数据,LongNAP 应能适应这种漂移。论文中,作者把数据收集与训练呈现为两个**同步**发生的过程,但并非必须如此!与其存储数据、离线多 epoch 训练,可以把整条流水线改为在线运行:训练在后台持续进行,或夜间进行(Lin et al., 2025)。作者称这一版本为 **powerNAP**。在 powerNAP 中,NAPsack 与 LongNAP 异步运作:NAPsack 持续跟踪并标注用户动作、将其入队等待训练;LongNAP 从队列消费已标注动作、单遍训练、用后即弃。关键在于,**记忆永不重置**、推理轨迹持续累积,使模型得以随时间不断构建更好的用户表示。作者将 powerNAP 作为演示⁶ 发布,供用户在自己的数据上试用。(⁶ 见 https://github.com/GeneralUserModels/powernap 。)

**助手(Assistants)**:一旦用户拥有了一个好的 LongNAP,我们就能预判其想要什么、打算做什么。这应当能催生一种"依据对用户下一步会做什么的预测、替用户完成可预测任务"的助手。LongNAP 本身不是计算机使用智能体,但可以轻松用它为一个此类智能体**领航(pilot)**。作者发布了这类助手的一个简单版本,名为 **SleepWalk**,它依赖现成的计算机使用智能体(Anthropic, 2024)来执行 LongNAP 预测出的动作。

### 9 Related Work(相关工作)

::: en
World, Human, and User Models The ability to predict the dynamics of complex physical and social behaviors are longstanding goals in both human-computer interaction and artificial intelligence. Progress on large, multimodal models has revitalized this vision. Trained on enough video data, large-scale generative video models show promise in predicting world dynamics, for example through next frame prediction (Hafner et al., 2019; Bruce et al., 2024; Yang et al., 2023). These predictive world models have opened a range of research directions in robotics, enabling data efficient robotic learning (Sharma et al., 2023; Quevedo et al., 2025; Du et al., 2023). Similarly, LLMs have been used to simulate general human behavior (Park et al., 2023; Wu et al., 2026) for social science research (Argyle et al., 2023; Hewitt et al., 2024; Park et al., 2024) or to build proactive, question-asking assistants (Sun et al., 2025; Wu et al., 2025). Both approaches rely on a similar assumption: that the internet contains substantial amounts of realistic behavioral data to bootstrap simulation. While these methods are sometimes effective, they tend to suffer from a sim-to-real gap (Zhao et al., 2020). In other words, we apply these simulators in very specific situations (e.g. specific individuals, robots, etc.) that are out of distribution. And continually collecting new training data to mend this distribution shift is technically challenging (Mirchandani et al., 2024) and/or prohibitively expensive (Halevy et al., 2009).

In this paper, we train models directly at the level of an individual user—a user model. The user models cannot afford to suffer from the sim-to-real gap: they are immediately deployed to specific people. So instead of relying on datasets that serve as proxies, we directly collect data from individual interaction traces. We rely on work showing that VLMs can effectively describe individual behavior through observation (Shaikh et al., 2025; Wang et al., 2025c). We then validate and build infrastructure (§3) for continually labeling low-level trajectories of individual behavior at scale.
:::

**世界模型、人类模型与用户模型(World, Human, and User Models)**:预测复杂物理与社会行为动态的能力,是人机交互与人工智能两个领域的长期目标。大型多模态模型的进展让这一愿景重焕生机。在足够多的视频数据上训练后,大规模生成式视频模型在**预测世界动态**上展现出前景,例如通过下一帧预测(Hafner et al., 2019; Bruce et al., 2024; Yang et al., 2023)。这些预测式世界模型在机器人学中开启了一系列研究方向,实现了数据高效的机器人学习(Sharma et al., 2023; Quevedo et al., 2025; Du et al., 2023)。类似地,LLM 也被用于模拟一般人类行为(Park et al., 2023; Wu et al., 2026),服务于社会科学研究(Argyle et al., 2023; Hewitt et al., 2024; Park et al., 2024),或用于构建主动提问的助手(Sun et al., 2025; Wu et al., 2025)。这两条路线都依赖一个相似的假设:互联网上有大量现实行为数据可用于引导(bootstrap)仿真。这些方法虽然有时有效,但往往受**仿真-现实鸿沟(sim-to-real gap)**之苦(Zhao et al., 2020)。换句话说,我们把这些模拟器用在非常特定的情形(如特定个体、机器人等)中,而这些情形恰恰是分布外的;要持续收集新训练数据去修补这种分布漂移,要么技术上困难(Mirchandani et al., 2024)、要么昂贵得不可行(Halevy et al., 2009)。

本文在**个体用户**层面直接训练模型——即用户模型。用户模型承受不起仿真-现实鸿沟:它们会被即刻部署到具体的人身上。因此,作者不依赖充当代理的数据集,而是直接从个体交互轨迹收集数据;并依托"VLM 能通过观察有效描述个体行为"的既有工作(Shaikh et al., 2025; Wang et al., 2025c),验证并构建(§3)了大规模持续标注个体行为底层轨迹的基础设施。

::: en
Personal Reasoning Training models that understand what people want requires personal reasoning (Li et al., 2025a): the ability to flexibly reason over our opaque personal preferences and beliefs. In contrast, the predominant RL setting relies on tasks where the outcome is easily verifiable, like math or symbolic reasoning (Silver et al., 2016; 2017; Trinh et al., 2024). Most LLMs are similarly trained to reason on easily verifiable tasks (Zelikman et al., 2022; Cobbe et al., 2021). Because of this reliance on verifiability, LLM reasoning often fails to generalize beyond these domains (Shaikh et al., 2023; Sprague et al., 2024). Training a model that can instead reason effectively over everyday interaction enables a range of human-centered applications: from proactive assistants that know your context well enough to autonomously do "the right thing at the right time," (Weiser, 1991) to AI models that know when and how to defer effectively to users (Horvitz, 1999).

In our work, we train such a model (LongNAP) over everything a person sees and does on their computer. Most related to our work is Gandhi et al. (2026), where an LLM is trained to reason for dialogue simulation. We instead learn to predict a user's general actions over the entirety of their digital context. In addition, LongNAP takes inspiration from work on metacognitive reuse (Suzgun et al., 2025; Didolkar et al., 2025; Sarukkai et al., 2025) and reasoning abstractions (Qu et al., 2025), where reasoning traces are re-used over the course of learning. Likewise, LongNAP learns to both generate, retrieve, and re-use reasoning traces at the individual user level.
:::

**个性化推理(Personal Reasoning)**:训练"理解人们想要什么"的模型,需要**个性化推理**(Li et al., 2025a):对我们那些不透明的个人偏好与信念灵活推理的能力。相比之下,主流 RL 设定依赖结果易于验证的任务,如数学或符号推理(Silver et al., 2016; 2017; Trinh et al., 2024);大多数 LLM 也同样在易验证任务上训练推理(Zelikman et al., 2022; Cobbe et al., 2021)。由于这种对可验证性的依赖,LLM 推理常常无法泛化到这些领域之外(Shaikh et al., 2023; Sprague et al., 2024)。转而训练一个能在日常交互上有效推理的模型,将支撑一系列以人为中心的应用:从"对你的上下文了如指掌、足以自主地在正确时机做正确之事"的主动式助手(Weiser, 1991),到知道何时、如何有效地向用户**让渡(defer)**的 AI 模型(Horvitz, 1999)。

本文训练了这样一个模型(LongNAP),学习的对象是一个人在计算机上**所见与所做的一切**。与本文最相关的是 Gandhi et al. (2026),其中 LLM 被训练为对话模拟而推理;作者则改为在个体用户数字上下文的整体上学习预测其一般动作。此外,LongNAP 从**元认知复用(metacognitive reuse)**(Suzgun et al., 2025; Didolkar et al., 2025; Sarukkai et al., 2025)与**推理抽象(reasoning abstractions)**(Qu et al., 2025)研究中汲取灵感——这些工作中推理轨迹会在学习过程中被复用。类似地,LongNAP 学会在**个体用户**层面生成、检索并复用推理轨迹。

::: en
Memory and Retrieval To predict a user's next action, we must be able to use the entirety of their digital context, which can span months, years, or more. However, LLMs have practical context limitations. The context window is constrained to a finite number of tokens; and putting everything in-context can degrade model performance (Liu et al., 2024). One solution involves retrieval-augmented generation, where LLMs retrieve from a larger, external database (Chen et al., 2017; Lewis et al., 2020). Instead of jointly optimizing a dense retriever end-to-end, LLMs can also be trained to use retrievers by generating queries to retriever tools (Schick et al., 2023; Hsu et al., 2024; Jin et al., 2025). In addition, LLMs can judge the relevance of retrieved context for question-answering tasks (Asai et al., 2024). Similarly, we introduce models that can effectively retrieve context for next action prediction, querying a lexical retriever. Our setting is unique in a few ways. First, we are retrieving relevant context not from an external search index or a database, but from the user's own interaction history. Second, we reason to retrieve what context is relevant specifically for predicting a user's next action. This process is end-to-end optimized via policy gradient methods; and significantly improves LongNAP performance.
:::

**记忆与检索(Memory and Retrieval)**:要预测用户的下一动作,必须能使用其数字上下文的整体——那可能横跨数月、数年乃至更久。然而 LLM 有实际上的上下文限制:上下文窗口被约束在有限个 token 内,而且把一切都放进上下文会损害模型性能(Liu et al., 2024)。一种解决方案是检索增强生成(RAG):LLM 从更大的外部数据库检索(Chen et al., 2017; Lewis et al., 2020)。除端到端联合优化稠密检索器之外,LLM 也可以被训练成通过向"检索器工具"生成查询来使用检索器(Schick et al., 2023; Hsu et al., 2024; Jin et al., 2025);此外,LLM 还能评判检索到的上下文与问答任务的相关性(Asai et al., 2024)。同样地,作者引入了能为下一动作预测有效检索上下文的模型,查询一个词法检索器。本文设定有几个独特之处:第一,检索的相关上下文不是来自外部搜索索引或数据库,而是**用户自己的交互历史**;第二,作者是**为"预测用户下一动作"这一特定目的推理出**该检索什么上下文。整个过程经策略梯度方法端到端优化,并显著提升了 LongNAP 性能。

### 10 Discussion(讨论)

::: en
In our evaluations, we find that LongNAPs show promise in predicting what users will do next across their digital contexts. We discuss implications of deploying models like LongNAP from privacy and alignment perspectives, and outline avenues for future work.

Privacy Models like LongNAP operate over large swaths of our context. Inevitably, they will contain private and sensitive data about users. Our architecture does limit some of this exposure, since learning to retrieve keeps the traces local; at some performance cost, one could either build the entire model locally or ensure that the learning to reason stage is not finetuned on any specific user. In addition, in our work, we rely on an approved infrastructure for processing personally identifiable information (PII) and personal health data (PHI). At our institution, only Google Cloud services are approved for processing PHI; so we rely on vetted, private pipelines to access Google's Gemini models for annotation. All model training occurs on open models (Qwen-2.5-VL-7B), where compute instances are managed by the research team.
:::

在评估中,作者发现 LongNAP 在跨数字上下文预测用户下一步行为上展现出前景。作者从隐私与对齐视角讨论部署 LongNAP 一类模型的影响,并勾勒未来工作的方向。

**隐私(Privacy)**:LongNAP 一类模型运行于我们上下文的大片区域之上,不可避免地会包含用户的隐私敏感数据。作者的架构确实限制了一部分暴露:"学会检索"使轨迹得以留在本地;也可以付出一些性能代价,要么把整个模型完全构建在本地、要么保证"学会推理"阶段不在任何特定用户上微调。此外,本文依赖经批准的、处理个人身份信息(PII)与个人健康数据(PHI)的基础设施:在其机构,只有 Google Cloud 服务获准处理 PHI,因此作者经由审查过的私有管线访问 Google 的 Gemini 模型做标注。所有模型训练都在开源模型(Qwen-2.5-VL-7B)上进行,算力实例由研究团队自管。

::: en
We recognize that these precautions are very challenging to take for the individual user. The privacy paradox (Norberg et al., 2007) makes deploying models like LongNAP in a centralized fashion difficult. In other words, users are likely to disclose more to LongNAP, especially given (1) the ease of collecting data and (2) the benefits that come with a proactive AI system.

There are several promising approaches that can mitigate these privacy concerns. The first is decentralization. We suspect that models will continue to get cheaper and faster, enabling on-device inference and training. Methods like FlashAttention (Dao et al., 2022), effective quantization (Dettmers et al., 2023), or specialization via synthetic data (Shen et al., 2026) already save substantially on compute or memory. If local models remain difficult, we can still redact private information with a smaller local model (Li et al., 2025b), only share private data to a larger model (Nissenbaum, 2004; Mireshghallah et al., 2023; Shao et al., 2024a) based on a user's personal context (Shaikh et al., 2025), or decouple model requests from eachother through a VPN-like system (Liu & Chi, 2026).
:::

作者也认识到,这些防范措施对个人用户而言极难采取。**隐私悖论(privacy paradox)**(Norberg et al., 2007)使以中心化方式部署 LongNAP 一类模型变得困难:换言之,用户很可能向 LongNAP 披露越来越多——尤其考虑到(1)数据收集之容易,与(2)主动式 AI 系统带来的好处。

有几种有望缓解这些隐私顾虑的方向。其一是**去中心化**:作者推测模型会继续变得更便宜、更快,使端侧推理与训练成为可能;FlashAttention(Dao et al., 2022)、有效的量化(Dettmers et al., 2023)、或经合成数据的专业化(Shen et al., 2026)等方法已经大幅节省算力或内存。如果本地模型仍然困难,仍可以用更小的本地模型先脱敏私有信息(Li et al., 2025b)、基于用户个人情境只把该共享的私有数据交给更大模型(Nissenbaum, 2004; Mireshghallah et al., 2023; Shao et al., 2024a; Shaikh et al., 2025)、或经 VPN 式系统把模型请求彼此解耦(Liu & Chi, 2026)。

::: en
Aligning LongNAPs In our current instantiation of LongNAP, we train models to do what a user might do next. There are many instances where this may not be helpful. For example, a user who habitually procrastinates may not want to use a model that helps them procrastinate. This is a challenging alignment problem with parallels to both filter bubbles on social media (Pariser, 2011; Munson & Resnick, 2010; Bakshy et al., 2015) and sycophancy in chat-based LLMs (Cotra, 2021; Perez et al., 2023; Cheng et al., 2025). We want learned LongNAPs to complement users in ways that help. A promising avenue for future work involves applying methods for eliciting values to steer social media algorithms (Popowski et al., 2026). Similar methods could be applied to LongNAPs.
:::

**对齐 LongNAP(Aligning LongNAPs)**:在当前的 LongNAP 实例中,作者训练模型去做"用户接下来可能会做的事"。而很多情形下这并无帮助:例如,习惯性拖延的用户未必想用一个帮自己拖延的模型。这是一个棘手的对齐问题,与社交媒体的**过滤气泡(filter bubbles)**(Pariser, 2011; Munson & Resnick, 2010; Bakshy et al., 2015)和聊天式 LLM 的**谄媚(sycophancy)**(Cotra, 2021; Perez et al., 2023; Cheng et al., 2025)构成同构难题。我们希望学得的 LongNAP 以**有帮助的方式**补足用户。一个有前景的未来方向,是把"为引导社交媒体算法而引出价值观"的方法(Popowski et al., 2026)应用于 LongNAP。

::: en
Limitations and Future Work There are fundamental limitations to learning from just observation. In our setting, models will only be able to make inferences from what happens on a user's screen, which is still a narrow proxy for a user's general context (Dourish, 2004). We are still far from models that can draw from everyday action beyond our devices, but we suspect our approach can be generalized to interaction beyond screenshots.

Both our labeling and training processes rely on large pretrained models. First, our training data itself is generated by a VLM captioning user activity. We find that VLMs are fairly performant at this task, and we expect performance to improve as VLMs improve. Still, they are not perfect—errors in captioning will cascade down to training and prediction. Like prior work, we also rely on LLM-as-a-judge for both reward and optimization (Bai et al., 2022; Dubois et al., 2023). We find that this metric continues to correlate with human judgement—humans pick samples from LongNAP over all other training approaches (§6). For longer runs, however, the judge alone may be prone to reward hacking (Wang et al., 2025a; Gandhi et al., 2026). We leave experimenting with other rewards for future work.
:::

**局限与未来工作(Limitations and Future Work)**:仅从观察学习存在根本性限制。在本文设定中,模型只能从用户屏幕上发生的事做推断,而屏幕仍是用户一般情境的一个狭窄代理(Dourish, 2004)。我们离"能从设备之外的日常行为中取材"的模型还很远,但作者推测其方法可以泛化到截图之外的交互。

标注与训练两个流程都依赖大型预训练模型。首先,训练数据本身就是由 VLM 标注用户活动生成的;作者发现 VLM 在该任务上相当能干,并预期其性能会随 VLM 进步而提升。但它们并不完美——标注错误会级联传导到训练与预测。与既有工作一样,作者还依赖 LLM-as-a-judge 同时充当奖励与优化目标(Bai et al., 2022; Dubois et al., 2023)。作者发现该指标持续与人类判断相关——人类在所有训练方法中更偏好 LongNAP 的样本(§6)。然而在更长的训练下,仅靠评审可能易受**奖励黑客(reward hacking)**攻击(Wang et al., 2025a; Gandhi et al., 2026);尝试其他奖励留作未来工作。

::: en
We also presented a basic scaffold for training LongNAPs. This scaffold could be made more expressive by allowing LongNAP to interleave retrieval and reasoning within a single generation pass, and by equipping it with additional tools such as web search. While we validated our method on a small sample of users and showed that LongNAP generalizes both over time and across users, it would be valuable to study how performance scales over longer time horizons and with many more users. Training separate weights for every user also presents practical challenges. Future work could explore how to efficiently train and serve per user LoRAs at scale (Sheng et al., 2023; Chen et al., 2024). Further, while current mid-training and pretraining data (Olmo et al., 2025; Havrilla et al., 2024; Penedo et al., 2024) for LLMs are optimized to improve performance on science, code and math, one can imagine that other types of data and reasoning strategies (Gandhi et al., 2025) could be better for NAP.

Finally, a few training limitations. First, we experiment only with GRPO (Shao et al., 2024b) as our policy gradient objective, due to the added memory constraints of learning an entire value network for methods like PPO (Schulman et al., 2017). In addition, we were unable to train all models to convergence because of budget constraints (our validation scores from Fig. 5 continue to increase, for example). We suspect that performance estimates in this paper may be a lower bound, and leave continued training experiments to future work.
:::

作者呈现的也只是训练 LongNAP 的一个基础脚手架。可以让 LongNAP 在单次生成中**交错**检索与推理,并为其配备网页搜索等更多工具,使其更具表达力。虽然作者在小样本用户上验证了方法、证明 LongNAP 能随时间与跨用户泛化,但研究性能如何随更长时间视野与更多用户扩展仍有价值。为每个用户训练单独权重也带来实际挑战,未来工作可以探索如何大规模地高效训练与服务 per-user LoRA(Sheng et al., 2023; Chen et al., 2024)。此外,当前 LLM 的中期训练(mid-training)与预训练数据(Olmo et al., 2025; Havrilla et al., 2024; Penedo et al., 2024)面向科学、代码与数学优化,可以想见其他类型的数据与推理策略(Gandhi et al., 2025)或许更适合 NAP。

最后是几点训练层面的限制。其一,由于 PPO 一类方法(Schulman et al., 2017)需要学习一整个价值网络、带来额外内存开销,作者只实验了 GRPO(Shao et al., 2024b)作为策略梯度目标。其二,受预算限制,作者未能把所有模型训练到收敛(例如图 5 中的验证分数仍在上升)。作者怀疑本文中的性能估计可能是**下界**,持续训练的实验留作未来工作。

### 11 Conclusion(结论)

::: en
We introduced LongNAP, a long-context next action predictor that learns to anticipate what users will do next by reasoning over their full multimodal interaction history. To collect training data, we introduced NAPsack, a passive pipeline that annotates naturalistic behavior traces at scale using vision-language models—demonstrating that rich, labeled interaction data can be obtained without any active user effort. In evaluations across 20 users and 1,800 hours of screen time, LongNAP significantly outperforms supervised finetuning and prompted baselines when trained on individual users. We also observe modest generalization when training on many users and generalizing to new ones. Altogether, we argue that learning from the full context of user behavior to anticipate user needs is now a tractable direction.
:::

作者提出了 LongNAP——一个通过对用户完整多模态交互历史进行推理、来预判其下一步行为的长上下文下一动作预测器;以及 NAPsack——一条用视觉-语言模型大规模被动标注自然主义行为轨迹的流水线,证明无需用户任何主动付出即可获得丰富的带标注交互数据。在 20 名用户、1800 小时亮屏时间的评估中,单用户训练的 LongNAP 显著超过监督微调与提示基线;在多用户上训练并泛化到新用户时也观察到适度的泛化。总而言之,作者论证:从用户行为的完整上下文中学习、以预判用户需求,如今已是一个可行的研究方向。

### 贡献声明与致谢(Contribution Statement & Acknowledgements)

::: en
Contribution Statement: OS conceived the initial idea, and planned/evaluated all experiments. VT and KG helped develop data labeling code, proposed and tested critical modeling ideas, and helped with framing the paper. KG also built an online implementation (powerNAP) of the paper. YC helped with Screenomics infrastructure, labeling, and data collection. DY, MB, and SY were primary co-supervisors for this project. All authors discussed results and contributed in writing the final paper.

Acknowledgements: We thank Dora Zhao, Michael Li, Vindula Jayawardana, Shardul Sapkota, Matthew Jörke, Helena Vasconcelos, Gerard de Melo, Michelle Lam, Shan Rizvi, Chris Rytting, and Vishnu Sarukkai for helpful discussions and feedback. Omar Shaikh is supported by the HAI-HPI program. The Screenomics components of this study were supported in part by a grant from the National Heart, Lung, and Blood Institute of the National Institutes of Health, under Award number R01HL16901. The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health or other funders. Finally, we appreciate the support from Sloan Foundation, Laude Institue, Thinking Machines (for Tinker credit), and Stanford Institute for Human-Centered Artificial Intelligence, as well as ONR grant N00014-24-1-2532.
:::

贡献声明:OS(Omar Shaikh)构思了最初的想法,并计划/评估了所有实验。VT 与 KG 帮助开发数据标注代码、提出并检验了关键的建模想法、协助论文框架;KG 还构建了论文的在线实现(powerNAP)。YC 协助 Screenomics 基础设施、标注与数据收集。DY、MB 与 SY 是本项目的主要共同指导者。所有作者讨论了结果并参与撰写最终论文。

致谢:作者感谢 Dora Zhao、Michael Li、Vindula Jayawardana、Shardul Sapkota、Matthew Jörke、Helena Vasconcelos、Gerard de Melo、Michelle Lam、Shan Rizvi、Chris Rytting 与 Vishnu Sarukkai 的有益讨论与反馈。Omar Shaikh 受 HAI-HPI 计划资助。本研究的 Screenomics 部分受到美国国立卫生研究院国家心肺血液研究所拨款(R01HL16901)的部分资助;内容仅由作者负责,不一定代表国立卫生研究院或其他资助方的官方观点。最后,作者感谢 Sloan 基金会、Laude Institue、Thinking Machines(提供 Tinker 额度)、斯坦福以人为中心人工智能研究院的支持,以及 ONR 拨款 N00014-24-1-2532。(译注:"Laude Institue" 为原文拼写,应为 "Laude Institute"。)

> 译注:References(参考文献)按站点惯例不收录,正文中的作者-年份引用均对应原文参考文献列表。以下继续收录附录 A、B。

### 附录 A NAPsack(Appendix A: NAPsack)

::: en
To record a session with NAPsack and compare it to a baseline without event-driven compression, we implement current active screen capturing using ffmpeg and apply the same recording hyperparameters for both methods.
:::

为录制一段 NAPsack 会话、并与"无事件驱动压缩"的基线作对比,作者用 ffmpeg 实现了当前活动屏幕的捕获,并对两种方法采用相同的录制超参数。

#### A.1 超参数(A.1 Hyperparameters)

::: en
NAPsack uses thresholds to group input events and decide when screenshots should be persisted. All recordings are performed at 30 FPS and a resolution of 1920×1080. To ensure that interface states immediately before and after interactions are preserved, NAPsack stores screenshots 75ms before the first event of a burst and 75ms after its last event.
:::

NAPsack 用若干阈值来分组输入事件,并决定何时持久化截图。所有录制均在 30 FPS、1920×1080 分辨率下进行。为确保交互前后瞬间的界面状态得以保留,NAPsack 会在突发的第一个事件之前 75 毫秒与最后一个事件之后 75 毫秒各保存一张截图。

**表 7:NAPsack 使用的事件突发阈值。**

| 事件类型 | 间隔阈值 GAP(秒) | 最长持续 MAX(秒) |
|---|---|---|
| 点击(Click) | 0.2 | 0.3 |
| 移动(Move) | 0.5 | 4.0 |
| 滚动(Scroll) | 0.5 | 3.0 |
| 按键(Key) | 0.5 | 6.0 |

#### A.2 将相邻事件分组为突发(A.2 Grouping Nearby Events into Bursts)

::: en
NAPsack groups temporally adjacent input events of the same type into event bursts. An event is assigned to the current burst if the time since the preceding event of that type does not exceed the corresponding gap threshold and the elapsed time since the burst start remains within the max duration (see table 7). If the gap threshold is exceeded, a new burst is started. If the max duration is exceeded, the first half of the current burst is finalized and saved, while the second half becomes the active burst. A burst is force-restarted when the active monitor changes. All thresholds were determined qualitatively; and should be re-tuned for new interfaces.
:::

NAPsack 把时间上相邻的同类输入事件归并为**事件突发(event burst)**。若一个事件距该类型的上一个事件不超过相应的**间隔阈值(gap threshold)**、且距突发开始的耗时仍在**最长持续时间(max duration)**之内,该事件就被划入当前突发(见表 7)。超过间隔阈值,则开启一个新突发;超过最长持续时间,则当前突发的前半部分被定稿保存,后半部分成为新的活动突发。当活动显示器发生切换时,突发被强制重启。所有阈值均经定性确定,换用新界面时应重新调参。

#### A.3 标注提示(A.3 Label Prompts)

::: en
We include all prompts for NAPsack in the following repo: https://github.com/GeneralUserModels/napsack/tree/main/src/label/prompts
:::

NAPsack 的全部提示词收录在以下仓库:https://github.com/GeneralUserModels/napsack/tree/main/src/label/prompts 。(译注:提示词本体较长且随仓库演进,此处按原文指引给出链接,不再逐条照录。)

#### A.4 为 NAPsack 标注真值标签(A.4 Annotating Ground Truth Labels for NAPsack)

::: en
Both authors verified ground truth labels recorded from personal screen recordings. To construct ground truth labels, the authors selected the best outputs generated from each NAPsack condition, and manually corrected the trajectories to match ground truth. Both authors reviewed the ground truth trajectories and preference annotations for errors over discussion. The author from whom the recordings were sourced resolved mistakes in ground truth labels during annotation.
:::

两位作者都对来自个人录屏的真值标签进行了核验。构造真值标签时,作者先选出各 NAPsack 条件下生成的最佳输出,再人工修正轨迹使其与真值吻合;随后两位作者在讨论中共同复核真值轨迹与偏好标注有无错误。录屏来源的那位作者在标注过程中裁决真值标签中的错谬。

#### A.5 标注 Screenomics(A.5 Annotating Screenomics)

::: en
Demographics The Screenomics dataset we use comes from Reeves et al. (2021). We subsampled 20 participants, of which one had no demographic data. The remaining 19 participants (14 female, 5 male) were located across the United States and ranged in age from 22 to 70, with a mean of 44 and a median of 39. The majority identified as White (16/19), with 2 identifying as Asian and 1 as Black; 6 identified as Hispanic. Education levels varied across participants. 2 held a high school diploma, 7 had some college, 1 an associate's degree, 5 a bachelor's, and 4 a graduate degree.

Deduplicating Images Many images in the Screenomics dataset are duplicates. To identify and remove screenshots where screen content is unchanged, we compute a perceptual difference hash for each image (Krawetz, 2011). This works by resizing the image to a small fixed size, comparing adjacent pixel intensities to produce a fingerprint, and then measuring Hamming distance between fingerprints of consecutive screenshots. Qualitatively, pairs with a distance at or below a threshold of 5 (out of a 16x16 = 256-bit hash) are near-duplicates; so we filter these images.
:::

**人口统计(Demographics)**:作者使用的 Screenomics 数据集来自 Reeves et al. (2021)。作者子抽样出 20 名参与者,其中 1 人没有人口统计数据;其余 19 人(14 女、5 男)分布在美国各地,年龄从 22 岁到 70 岁,均值 44 岁、中位数 39 岁。多数自认为是白人(16/19),2 人自认为亚裔、1 人自认为黑人;6 人自认为拉美裔(Hispanic)。参与者受教育程度各异:2 人持高中文凭、7 人读过一些大学、1 人副学士、5 人学士、4 人研究生学位。

**图像去重(Deduplicating Images)**:Screenomics 数据集中许多图像是重复的。为识别并删除屏幕内容未变的截图,作者为每张图像计算**感知差异哈希(perceptual difference hash)**(Krawetz, 2011):把图像缩放到一个固定的小尺寸,比较相邻像素强度得到指纹,再度量连续截图指纹之间的汉明距离。定性来看,距离不超过阈值 5(16×16 = 256 位哈希)的图像对近似重复,因此把这些图像过滤掉。

#### A.6 评审提示(A.6 Judge Prompt)

::: en
We include our judge prompt for training here: https://github.com/GeneralUserModels/powernap/blob/main/src/powernap/longnap/verifiers/accuracy.txt
:::

训练所用的评审提示见:https://github.com/GeneralUserModels/powernap/blob/main/src/powernap/longnap/verifiers/accuracy.txt 。(译注:同 A.3,提示词本体见链接,不在此照录。)

### 附录 B LongNAP 细节(Appendix B: LongNAP details)

#### B.1 训练与检索器超参数(B.1 Training and Retriever Hyperparamters)

(译注:小节标题中 "Hyperparamters" 为原文拼写,应为 "Hyperparameters"。)

::: en
Training We include hyperparameter details for LongNAP and our SFT baseline in Tab. 8. We detail how many actions we place in context; how many we predict; and the number of images placed in context. Even with LoRA (hyperparameters also in Tab. 8), we find that images significantly increase contexts lengths. Because of memory limitations, we only keep images associated with the last 2 events in context. Across all models, we sample with temperature 1.0.
:::

**训练(Training)**:LongNAP 与 SFT 基线的超参数细节见表 8,其中写明了放入上下文的动作数、预测的动作数、以及放入上下文的图像数。即便用了 LoRA(超参数亦见表 8),作者仍发现图像会显著拉长上下文;受内存限制,上下文中只保留与最近 2 个事件关联的图像。所有模型采样温度均为 1.0。

**表 8:超参数设置。作者依据验证性能挑选最佳 checkpoint,并在合适时提前停止。受预算限制,只在基线(配合 SFT)上扫描学习率。训练使用 8 块 B200 GPU。**

| 超参数 | LongNAP | SFT |
|---|---|---|
| 有效批大小(Effective Batch Size) | 16 | 16 |
| 学习率(Learning Rate) | 3e-5 | 1e-4 |
| 组大小(Group Size) | 4 | - |
| 训练轮数(Epochs) | 10 | 10 |
| 历史中动作数(Actions in history) | 16 | 16 |
| 预测动作数(Actions to predict) | 8 | 8 |
| 历史中图像数(Images in history) | 2 | 2 |
| LoRA 秩(LoRA rank) | 8 | 8 |
| alpha | 32 | 32 |
| dropout | 0.05 | 0.05 |
| 作用模块(modules) | 仅 MLP | 仅 MLP |

(表 8 中文说明:LongNAP 与 SFT 的大部分设置一致;区别主要在学习率——SFT 用大一个数量级的 1e-4——以及 GRPO 所需的组大小 4,后者为 SFT 所无。)

::: en
Retriever LongNAP uses an in-memory BM25 retriever to retrieve old reasoning traces and observations. To start, we use standard BM25 parameters k1 = 1.5 and b = 0.75. In addition, we apply a temporal decay. At query time, each candidate's BM25 score is multiplied by exp(−λ·age), where age is the time difference between the query and the document's event measured in days. We set λ = 0.5, which strongly favors recent context over older history. We also apply a constraint to make sure that retrieved items are diverse. We first retrieve the top-k = 10 candidates from BM25, then apply Maximal Marginal Relevance (MMR) reranking to select kmmr = 5 results with diversity parameter α = 0.5, balancing relevance and diversity equally (Carbonell & Goldstein, 1998). Finally, to avoid redundancy in the retriever's memory, we deduplicate when we insert. We use trigram Jaccard similarity (threshold of 0.8), replacing older near-duplicate entries with newer ones.
:::

**检索器(Retriever)**:LongNAP 使用一个内存中的 BM25 检索器来检索旧的推理轨迹与观察。起步采用标准 BM25 参数 $k_1 = 1.5$、$b = 0.75$;此外还施加**时间衰减(temporal decay)**:查询时,每个候选的 BM25 分数乘以 $\exp(-\lambda \cdot \text{age})$,其中 age 是查询与文档事件之间的时间差(以天计)。取 $\lambda = 0.5$,强烈偏向较新的上下文而非更久远的历史。作者还施加约束以保证检索条目的**多样性**:先从 BM25 检索 top-$k = 10$ 个候选,再用**最大边际相关(Maximal Marginal Relevance, MMR)**重排选出 $k_{\text{mmr}} = 5$ 条结果,多样性参数 $\alpha = 0.5$,即相关性与多样性均等权衡(Carbonell & Goldstein, 1998)。最后,为避免检索器记忆冗余,插入时做去重:用三元组 Jaccard 相似度(阈值 0.8),以新条目替换较旧的近似重复条目。

#### B.2 提示基线(B.2 Prompting Baselines)

::: en
For prompting baselines, we try zero-shot and few-shot prompting. Few-shot prompts use our retriever (see details in §B.1) to retrieve and place relevant few-shot examples in-context. Below, we outline our prompt (few-shot additions are highlighted in red), used for both closed and open source models:

Prompt

You are an expert at analyzing user behavior patterns and predicting future actions based on historical context.

## Task

Analyze the following sequence of user actions and predict what they will do next. Pay attention to:

- The temporal patterns and timing of actions
- The logical flow and context of the user's workflow
- Common behavioral patterns that might indicate intent

## Previous Actions

<actions>
{past 16 actions}
</actions>

## Relevant Retrieved Actions

<actions>
{retrieved actions}
</actions>

## Instructions

Based on the actions above, predict the most likely next **8** actions the user will take. Output your predictions in the following format:

<actions>
{example actions}
</actions>

Be specific and realistic in your predictions. Consider the user's apparent goals and typical workflows. You MUST output exactly 8 actions.
:::

提示基线尝试 zero-shot 与 few-shot 两种提示。Few-shot 提示使用本文的检索器(细节见 §B.1)检索相关示例并放入上下文。以下是作者所用的提示(few-shot 增补部分原文以红色标出),闭源与开源模型通用:

**提示词(Prompt)**:

> 你是分析用户行为模式、并基于历史上下文预测未来动作的专家。
>
> ## 任务(Task)
>
> 分析以下用户动作序列,预测他们接下来会做什么。注意:
>
> - 动作的时间模式与时机
> - 用户工作流的逻辑脉络与上下文
> - 可能指示意图的常见行为模式
>
> ## 过往动作(Previous Actions)
>
> <actions>
> {过去 16 个动作}
> </actions>
>
> ## 检索到的相关动作(Relevant Retrieved Actions)〔译注:此节为 few-shot 增补部分〕
>
> <actions>
> {检索到的动作}
> </actions>
>
> ## 指令(Instructions)
>
> 基于以上动作,预测用户最可能采取的接下来 **8** 个动作。按以下格式输出你的预测:
>
> <actions>
> {示例动作}
> </actions>
>
> 预测要具体、现实。请考虑用户显见的目标与典型工作流。你必须恰好输出 8 个动作。

(译注:原文以红色高亮标出 few-shot 增补的"Relevant Retrieved Actions"一节,Markdown 无法呈现红色,此处以标注说明;zero-shot 版本不含该节。)

### 附录定性示例:不同评审分下的预测与真值(Qualitative Examples)

即 §3.2 所称"更多已评分对"(additional scored pairs),位于原文第 31-32 页。

**表 9:Gemini 评审给出的不同准确率分数下,预测动作与真值动作的定性示例(第 1 部分:低分)。前五行来自模型预测。**

| 分数 | 真值(Ground Truth) | 预测动作(Predicted Actions) |
|---|---|---|
| 0.05 | 1) 在搜索栏输入 "icc world cup";2) 点击 ICC T20 世界杯小组件中的 "STANDINGS" 标签;3) 滚动浏览积分榜表格;4) 点击积分榜中的 "SL"(斯里兰卡);5) 切到 W&B 仪表盘标签页;6) 滚动浏览 W&B 图表;7) 点击 W&B 中的 "train/entropy" 图表;8) 在 Slack 中点击与 "Omar Shaikh" 的聊天 | 1) 在地址栏输入 "x" 并回车;2) 点击左上角 Twitter 图标;3) 在 Twitter 搜索栏输入 "arch";4) 点击 "Arch Labor" 的搜索结果;5) 点击 Twitter 侧栏的 "Home" 按钮;6) 滚动浏览 Twitter 信息流;7) 点击 Twitter 的搜索按钮;8) 在 Twitter 搜索栏输入 "forms" |
| 0.12 | 1) 在 PyPI 上点击 "rouge-score",复制安装命令;2) 在终端运行 uv pip install rouge-score;3) 滚动浏览 "rouge-score" 的 PyPI 页面;4) 运行 accelerate launch 训练命令;5) 滚动浏览 "rouge-score" 的 PyPI 页面;6) 在 W&B、Google 文档与终端之间切换;7) 输入训练命令,用 Ctrl+C 取消;8) 运行 cd sim-v2 与 git pull | 1) 滚动浏览 "install rouge score" 的搜索结果;2) 点击一条 "install rouge score" 的搜索结果;3) 向下滚动 GitHub 上的 "crag" 仓库;4) 点击 GitHub 仓库中的 "hub/parouza" 链接;5) 在文件浏览器中点击 "eval" 目录;6) 按回车运行 evaluate qm9.py;7) 切换到 Google Chrome 窗口;8) 从 GitHub 复制 pip install 命令 |
| 0.20 | 1) 点击地图上的紫色房源图钉;2) 点击 "$3.5k+" 房源图钉;3) 点击 "$2.8k" 房源图钉;4) 点击 "$3.5k+" 房源图钉;5) 点击 "$3.3k" 房源图钉;6) 点击 "$3.9k" 房源图钉;7) 点击 "$5.3k" 房源图钉;8) 点击 "$2.8k" 房源图钉 | 1) 在 Zillow 上滚动浏览搜索结果与地图;2) 点击 Zillow 地图上的房源标记;3) 点击 "Down" 箭头展开价格筛选;4) 点击 "OK" 应用价格筛选设置;5) 滚动浏览筛选后的搜索结果;6) 从结果中选中一张房源卡片;7) 在房源页点击 "Show on map";8) 在 Zillow 地图上滚动浏览租房列表 |
| 0.35 | 1) 滚动浏览 W&B 仪表盘;2) 点击 W&B 中 "kanishkgandhi" 项目链接;3) 点击 W&B 侧栏中的一个 run;4) 点击 "kanishkgandhi's workspace" 标签;5) 滚动浏览与 Claude 的对话;6) 点击 Chrome 的 "New Tab" 按钮;7) 切到 W&B 标签页;8) 在 W&B 中滚动浏览 "context-distillation-goyal" | 1) 在 "NAP Time" 仪表盘上滚动浏览 W&B 图表;2) 在 Chrome 中关闭 W&B 仪表盘标签页;3) 切到 Claude.ai 标签页;4) 在 Chrome 中关闭当前标签页;5) 切到 Claude 标签页;6) 查看 Claude 聊天中的文本;7) 从 Claude 重新抓取所选视图内容;8) 从 Claude 重新抓取所选视图内容 |
| 0.42 | 1) 切到 "Australia vs Zimbabwe" 标签页,进入全屏;2) 点击 "Key Moments" 区域的缩略图;3) 按 "esc" 退出全屏;4) 切到 W&B 工作区,点击 "Runs" 图标;5) 切到 "Australia vs Zimbabwe",进入全屏;6) 按 "esc" 退出全屏;7) 切到 W&B 标签页,滚动浏览图表;8) 滚动浏览 W&B 仪表盘 | 1) 切到 "Australia vs Zimbabwe" 标签页;2) 点击板球视频的全屏按钮;3) 点击播放器栏底部的 History 频道图标;4) 在 Chrome 中按 "escape";5) 点击视频播放器;6) 点击播放器栏底部的 History 频道图标;7) 点击 History 频道图标,按 "space";8) 在 Chrome 中按 "space" |

(表 9 中文说明:低分段的五组对比——0.05 分把"查板球积分榜 + 看实验指标 + 联系合作者"的工作流完全预测成了刷 Twitter;0.12 分方向(装包、跑训练)对了但具体操作全然不同;0.20 分保留"看房"意图但交互方式漂移;0.35 分 W&B 与 Claude 交替的骨架接近、细节错位;0.42 分与真值逐步对应,只在具体点击对象上有出入。)

**表 10:定性示例(续,第 2 部分:高分)。这些示例为人工构造,用于说明分数段上端代表什么。**

| 分数 | 真值(Ground Truth) | 预测动作(Predicted Actions) |
|---|---|---|
| 0.52 | 1) 切到 "Australia vs Zimbabwe" 标签页,进入全屏;2) 点击 "Key Moments" 区域的缩略图;3) 按 "esc" 退出全屏;4) 切到 W&B 工作区,点击 "Runs" 图标;5) 切到 "Australia vs Zimbabwe",进入全屏;6) 按 "esc" 退出全屏;7) 切到 W&B 标签页,滚动浏览图表;8) 滚动浏览 W&B 仪表盘 | 1) 切到 "Australia vs Zimbabwe" 标签页,点击播放器;2) 按 "f" 在板球视频上进入全屏;3) 按 "esc" 退出全屏;4) 打开新标签页,在地址栏输入 "wandb.ai";5) 滚动浏览 W&B 的训练指标图表;6) 点击 W&B 仪表盘的 "Table" 视图;7) 切到 YouTube,点击推荐视频;8) 在 YouTube 上滚动浏览评论区 |
| 0.72 | 1) 切到 "Australia vs Zimbabwe" 标签页,进入全屏;2) 点击 "Key Moments" 区域的缩略图;3) 按 "esc" 退出全屏;4) 切到 W&B 工作区,点击 "Runs" 图标;5) 切到 "Australia vs Zimbabwe",进入全屏;6) 按 "esc" 退出全屏;7) 切到 W&B 标签页,滚动浏览图表;8) 滚动浏览 W&B 仪表盘 | 1) 切到 "Australia vs Zimbabwe" 标签页,进入全屏;2) 点击视频播放器时间轴以快进;3) 按 "esc" 退出全屏;4) 切到 W&B 工作区,滚动浏览仪表盘;5) 切到 "Australia vs Zimbabwe" 标签页,进入全屏;6) 按 "esc" 退出全屏;7) 切到 W&B 标签页,点击某张图表;8) 点击 W&B 工作区的 "Table" 视图 |
| 0.78 | 1) 点击地图上的紫色房源图钉;2) 点击 "$3.5k+" 房源图钉;3) 点击 "$2.8k" 房源图钉;4) 点击 "$3.5k+" 房源图钉;5) 点击 "$3.3k" 房源图钉;6) 点击 "$3.9k" 房源图钉;7) 点击 "$5.3k" 房源图钉;8) 点击 "$2.8k" 房源图钉 | 1) 点击地图上的紫色房源图钉;2) 点击 "$3.5k+" 房源图钉;3) 点击 "$2.8k" 房源图钉;4) 点击 "$3.5k+" 房源图钉;5) 点击 "$3.3k" 房源图钉;6) 点击 "$3.9k" 房源图钉;7) 点击 "$4.2k" 房源图钉;8) 点击 "$3.1k" 房源图钉 |
| 0.82 | 1) 在搜索栏输入 "icc world cup";2) 点击 ICC T20 世界杯小组件中的 "STANDINGS" 标签;3) 滚动浏览积分榜表格;4) 点击积分榜中的 "SL"(斯里兰卡);5) 切到 W&B 仪表盘标签页;6) 滚动浏览 W&B 图表;7) 点击 W&B 中的 "train/entropy" 图表;8) 在 Slack 中点击与 "Omar Shaikh" 的聊天 | 1) 在搜索栏输入 "icc world cup";2) 点击 ICC T20 世界杯小组件中的 "STANDINGS" 标签;3) 滚动浏览积分榜表格;4) 点击积分榜中的 "IND"(印度);5) 切到 W&B 仪表盘标签页;6) 滚动浏览 W&B 图表;7) 点击 W&B 中的 "train/loss" 图表;8) 在 Slack 中点击与 "Omar Shaikh" 的聊天 |
| 0.98 | 1) 在 PyPI 上点击 "rouge-score",复制安装命令;2) 在终端运行 uv pip install rouge-score;3) 滚动浏览 "rouge-score" 的 PyPI 页面;4) 运行 accelerate launch 训练命令;5) 滚动浏览 "rouge-score" 的 PyPI 页面;6) 在 W&B、Google 文档与终端之间切换;7) 输入训练命令,用 Ctrl+C 取消;8) 运行 cd sim-v2 与 git pull | 1) 在 PyPI 上点击 "rouge-score",复制安装命令;2) 在终端运行 uv pip install rouge-score;3) 滚动浏览 "rouge-score" 的 PyPI 页面;4) 运行带数据集参数的 accelerate launch;5) 滚动浏览 "rouge-score" 的 PyPI 页面;6) 在 W&B、Google 文档与终端之间切换;7) 输入 CUDA 训练命令,用 Ctrl+C 取消;8) 运行 cd sim-v2 与 git pull |

(表 10 中文说明:高分段的五组对比——0.52 分核心意图(看板球与查 W&B 交替)保留但具体交互与收尾漂移;0.72 分逐步对应、仅细节偏差;0.78 分几乎逐条一致、只有最后两个价格点不同;0.82 分仅把 "SL" 换成 "IND"、"train/entropy" 换成 "train/loss";0.98 分除训练命令的参数细节外与真值完全一致。表 9、表 10 的真值轨迹与正文表 1 一致,可对照阅读。)

## 要点速览

- **任务形式化**:NAP = 给定多模态交互事件流(动作+截图),以 k 个近期事件为上下文预测未来 h 个事件;论文固定 k=16、h=8;动作粒度对齐"可委托给计算机使用智能体"的自然语言任务。
- **被动监督**:不派任务、不让人标注,观察自然使用后用 VLM 事后标注——看到"人们实际做什么"而非"人们说自己做什么";NAPsack 以开源包发布,可在私有基础设施运行。
- **NAPsack 关键设计**:I/O 事件按 ε 时间聚类成 burst、只在交互时存截图(压缩约 70% 存储:295MB→76MB);60 帧切块保上下文短;few-shot 提示保持描述粒度一致;四种条件评审分 0.48/0.57/0.60/0.70,人工胜率 19.2%/45.4%/49.6%/85.8%。
- **数据集**:基于 Screenomics(总量约 1.7 亿截图/257 人),抽样 20 人一个月(2021-03-16 至 04-12):190 万截图、1837 小时亮屏、359,219 条动作,事件平均覆盖约 15 秒;人均日亮屏 4h32m(最轻 2h17m、最重 6h52m)。
- **LongNAP 架构**:Qwen-2.5-VL-7B + BM25 记忆检索;两阶段生成——reason to retrieve(推理即查询)→ reason to predict(整合检索修订推理再预测);最高奖励轨迹写回记忆;GRPO(组大小 4)+ LoRA 端到端训练。
- **训练技巧**:时间性奖励 = 与真实未来的 LLM 评审相似度;按时间顺序训练、每 epoch 重置记忆;检索 token 掩码;检索器 dropout(丢 10%/乱序 10%/空 10%)稳定训练。
- **单用户结果**:平均评审分 0.38,比 SFT(0.21)高 79%、比 zero-shot/few-shot Qwen(0.18/0.20)高 106%/88%、比 Gemini zero-shot/few-shot(0.26/0.27)高 43%/39%;人工评估胜率 79.0%。
- **跨用户结果**:10 训练/5 验证/5 测试,平均 0.26,仅比最强基线(few-shot Gemini 0.23)高 13%——用户专属权重对 NAP 尤其有效,跨用户泛化仍待扩展。
- **可解释性能**:pass@1 = 17.1%、pass@20 = 36.3%(阈值 0.5);置信度前 10% 的样本 pass@1 = 25.9%;用户间差异大(u8 相对提升 63%,u11 仅 15%)。
- **消融**:去推理 −19.2%(0.38→0.30)、去检索器 −15.2%(→0.32)、打乱时序 −9.3%(→0.34);检索轨迹平均仅 10.11 token 且被优化成 BM25 查询风格,预测轨迹平均 85.34 token。
- **延伸系统**:powerNAP(在线版:NAPsack 异步标注入队、LongNAP 单遍消费、记忆永不重置)与 SleepWalk(用现成计算机使用智能体执行 LongNAP 预测)。
- **开放问题**:屏幕仍是情境窄代理、VLM 标注噪声级联、LLM 评审可能被奖励黑客攻破、为每用户训权重难以规模化、以及"预测用户行为 ≠ 帮助用户"的对齐问题(拖延/谄媚/过滤气泡的同构难题)。
