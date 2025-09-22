# 📝 `Weekly News Letter` Crew AI Agents 🖋️
### 🖋️ Streamlit App : NewsLetter Writer Crew AI Agents to Get `Last Weekly News` based on a specific `Topic`.
### 🤖 Powered by Google Gemini AI models

## NEWS LETTER : DuckDuckGo Search & CREW AI
- News Letter Writer assistant to help generate a LLM powered update Weekly News based on your topic.

![](https://github.com/Abhiojiki/Newsletter-CrewAiAgent/blob/main/Animation.gif)

![alt](https://github.com/user-attachments/assets/d257df7d-b334-4861-ba35-fefa8b0e179a)

![alt](https://github.com/user-attachments/assets/b7343abb-f640-4392-b1a4-eaec8e0b12a7)


## 📝 Streamlit Ai Crew :

- `CrewAi` : Framework for Agents, Tasks and Tools (2x2 Agents/Tasks)
- `Callbacks` : To render the Agents processing and final outputs
- `DuckSearchTools` : Get the last week informations from DuckDuckGo Search Class
- `Google Gemini API` : for Inference
- `Available Models` : Gemini 2.0 Flash, Gemini 2.0 Flash Lite, Gemini 2.5 Flash Lite, Gemini 2.5 Pro

## CREW AI AGENT :
- An advanced research assistant by leveraging LangChain-powered tools into a CrewAI-powered multi-agent setup.
- LangChain is a framework enabling developers to easily build LLM-powered applications over their data; it contains production modules for indexing, retrieval, and prompt/agent orchestration.
- A core use case is building a generalized QA interface enabling knowledge synthesis over complex questions.
- Plugging a LangChain RAG pipeline as a tool into a CrewAI agent setup enables even more sophisticated/advanced research flows

## ✈️ Run the App Locally

### Using UV (Recommended)
```bash
# Install UV if not already installed
pip install uv

# Install dependencies
uv sync

# Run the app
uv run streamlit run news_app.py
```

### Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run news_app.py
```

## 🚀 Deploy to Streamlit Cloud

### Using UV Package Management

1. **Prepare for deployment**:
   ```bash
   python prepare_deployment.py
   ```
   This script will:
   - Sync dependencies with UV
   - Run basic checks
   - Generate requirements.txt as backup

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository  
   - Set main file path: `news_app.py`
   - **Streamlit Cloud will automatically use `pyproject.toml`** for UV-managed dependencies

### Manual Deployment

If you prefer manual steps:

```bash
# Sync dependencies
uv sync

# Run checks
uv run python -c "import streamlit, crewai, langchain_google_genai"

# Generate requirements.txt (optional backup)
uv pip compile pyproject.toml -o requirements.txt

# Commit and push
git add .
git commit -m "Ready for deployment"
git push origin main
```

## 🔑 API Setup
- Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Enter it in the app when prompted (no secrets.toml needed)
