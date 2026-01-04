# RequirementDocGen 📝✨

RequirementDocGen is an AI-driven requirement document generation system built on an **Active Learning** framework. It helps users transform vague project requirements into structured, comprehensive requirement documents through natural language input (voice or text) and intelligent multi-round clarification.

![Branding](frontend/public/favicon.png)

## 🌟 Key Features

### 1. Intelligent Requirement Analysis
The system employs a "Input-Analysis-Clarification-Documentation" cycle:
- **Natural Language Input**: Accept requirements via voice or text input
- **AI Understanding**: Uses Gemini 3 Flash to understand and parse requirements
- **Multi-round Clarification**: Automatically identifies ambiguities and asks clarifying questions
- **Structured Output**: Generates comprehensive JSON requirement documents

### 2. Requirement Genome Management
- **AI Summary**: Real-time synthesis of requirement understanding using Gemini 3 Flash
- **State Management**: Tracks features, user stories, constraints, and clarifications across rounds
- **Session Persistence**: Progress is automatically saved to local storage—never lose your requirement analysis even after a refresh

### 3. Voice-Driven Interaction
- **Seamless Transcription**: Integrated AI Builder Space speech-to-text API for effortless natural language input
- **Visual Feedback**: Real-time waveform visualization gives you confidence that the system is hearing your requirements
- **Intelligent Status**: Clear visual indicators during the transcribing phase ensure a smooth, transparent UX

### 4. High-Performance Engineering
- **Asynchronous Processing**: Utilizes async coroutines for efficient requirement analysis
- **Non-intrusive HUD**: A sleek status overlay keeps you informed without interrupting your workspace
- **Docker-Ready**: Optimized for deployment with a multi-stage Dockerfile and single-process/single-port configuration
- **Robustness**: Built-in **Exponential Backoff** retry logic to gracefully handle API rate limits and model overloads

## 🧠 Design Philosophy: Workflow over Plumbing

RequirementDocGen is a showcase of the **AI Architect** mindset. By leveraging the comprehensive AI capabilities of [AI Builder Space](https://space.ai-builders.com), the project focuses entirely on designing high-value AI workflows rather than managing low-level infrastructure.

Key AI orchestrations integrated via AI Builder Space:
- **Strategic Reasoning**: Analyzing vague requirements to synthesize a precise "Requirement Genome"
- **Intelligent Clarification**: Generating targeted questions to resolve ambiguities
- **Document Generation**: Creating structured JSON requirement documents with user stories, features, and constraints
- **Multimodal Feedback**: Real-time voice-to-text transcription to lower the barrier for requirement input

By offloading the "plumbing" (authentication, model scaling, deployment) to the [AI Builder Space](https://space.ai-builders.com) platform, the development energy was directed toward what matters most: **the requirement analysis workflow and user experience.**

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite (Vanilla CSS for premium aesthetics)
- **AI Engine**: AI Builder Space Platform
  - **Gemini 3 Flash Preview (Thinking Mode)**: For requirement analysis and clarification
  - **Audio Transcription API**: For real-time voice-to-text requirement input
- **Icons**: Lucide React

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js & npm (for building the frontend)
- An AI Builder Space API Token (`AI_BUILDER_TOKEN`)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/grapeot/RequirementDocGen.git
   cd RequirementDocGen
   ```

2. **Setup environment variables**:
   Create a `.env` file in the root directory:
   ```env
   AI_BUILDER_TOKEN=your_ai_builder_token_here
   PORT=8000
   ```
   
   **Note**: The application now uses the AI Builder Space platform instead of direct Gemini API calls.

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Build the frontend**:
   ```bash
   ./scripts/build-frontend.sh
   ```

5. **Run the application**:
   ```bash
   python3 main.py
   ```

### 🐳 Docker Deployment

The project is fully containerized for easy deployment:

```bash
docker build -t requirement-docgen .
docker run -p 8000:8000 -e AI_BUILDER_TOKEN=your_token requirement-docgen
```

Access the UI at `http://localhost:8000`.

## 📖 Documentation
- [Workflow Design](docs/workflow.md): Detailed explanation of the requirement analysis workflow (Chinese).
- [Engineering Design](docs/design.md): Technical architecture and state management (Chinese).

## 🛡️ License
MIT License. Feel free to use and modify for your projects!
