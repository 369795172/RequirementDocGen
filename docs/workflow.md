# RequirementDocGen: 需求文档生成工作流 (Requirement Document Generation Workflow)

本项目旨在通过 **AI 辅助分析** 机制，帮助用户从模糊的项目需求中生成结构化的、完整的需求文档。

## 1. 核心循环 (The Loop)

系统采用“反馈-进化-探索”的闭环逻辑：

1.  **初始演化 (Warm-up)**: 系统生成 9 个具有高度差异性的原始机型（Archetypes），用于探测用户的审美底色。
2.  **交互反馈 (Human-in-the-loop)**: 用户通过自然语言（文本或语音）表达对当前轮次图片的喜好或厌恶。
3.  **需求状态更新 (Requirement State Update)**: 后端 **AI 需求分析器** 实时解析输入，纠正并合并用户的需求信息（Requirement Genome），生成一份清晰的 **"需求摘要 (AI Summary)"**。
4.  **7+2 进化策略**:
    *   **7 个进化位 (Exploitation)**: 提取 DNA 中的优胜基因，通过杂交和变异生成更符合用户口味的设计。
    *   **2 个探索位 (Exploration)**: 故意引入偏离当前偏好的设计方案，用于突破局部最优，发现潜在的惊喜。
5.  **并行渲染**: 采用并行架构同时调用图像生成 API，极大缩短等待时间。

## 2. 累积学习机制 (Cumulative Learning)

*   **需求基因组 (Requirement Genome)**: 系统不仅存储关键词，还理解需求背后的业务逻辑和用户意图。
*   **非侵入性 HUD**: 采用静默 HUD 提示进度，确保用户在每一轮生成期间都能持续沉淀审美思考，无须等待遮罩消失。

## 3. 设计原则 (Design Philosophy)

*   **数字单体感 (Digital Monolithism)**: 强调几何的纯粹性和体块感。
*   **极简主义 (Linear Minimalism)**: 消除冗余，用最精炼的线条表达动态。
*   **无感交互**: 界面采用沉浸式暗色调，让图片（设计本身）成为绝对的主角。
