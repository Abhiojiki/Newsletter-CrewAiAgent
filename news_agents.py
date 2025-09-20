import streamlit as st
from crewai import Agent, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from DuckSearchTools import DuckSearchTool
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AGENTS
class NewsAgents():
    def __init__(self, model_name):
        self.model_name = model_name
        # Initialize tool instance
        self.search_tools = DuckSearchTool()
    
    def llm(self):
        api_key = os.getenv('GOOGLE_API')
        if not api_key:
            raise ValueError("GOOGLE_API environment variable not found. Please set it in your .env file.")
        
        llm = LLM(
            model=f"{self.model_name}",
            temperature=0.2,
            api_key=api_key
        )
        return llm
    
    # News aggregator agent
    def news_agent(self):
        return Agent(
            role="News Aggregator",
            goal="""Collect the most relevant and engaging 11 news stories for {topic}'s audience. 
            Provide the key news developments, trends, and insights related to {topic} for {topic}'s readers, 
            along with articles publication date, source and url.""",
            backstory="""You are a seasoned news aggregator for {topic}, a reputable publication known for its 
            insightful coverage. You have a keen eye for identifying the most impactful and interesting news stories 
            related to {topic}.""",
            verbose=True,
            memory=True,
            max_iter=5,
            allow_delegation=False,
            tools=[self.search_tools.news_search],  # Use instance method
            llm=self.llm(),
        )
    
    # Writer agent
    def writer_agent(self):
        return Agent(
            role="News Letter Writer",
            goal="Craft compelling and detailed News Letter on {topic} based on the collection of news articles",
            backstory="""You are a talented and experienced News Letter writer, a publication known for its 
            high-quality and engaging content. You have a knack for taking complex information and making it 
            accessible and interesting for a broad audience.""",
            verbose=True,
            memory=True,
            max_iter=5,
            allow_delegation=False,
            llm=self.llm()
        )

class StreamToExpander:
    """Custom stream handler for CrewAI output to Streamlit"""
    
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']
        self.color_index = 0
    
    def write(self, data):
        # Filter out ANSI escape codes
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)
        
        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()
        
        if task_value:
            st.toast(":robot_face: " + task_value)
        
        # Apply color formatting for different agent types
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)
            cleaned_data = cleaned_data.replace(
                "Entering new CrewAgentExecutor chain", 
                f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]"
            )
        
        # Replace agent names with colored versions
        agent_replacements = {
            "News Aggregator": f":{self.colors[self.color_index]}[News Aggregator]",
            "News Letter Writer": f":{self.colors[self.color_index]}[News Letter Writer]",
            "Finished chain.": f":{self.colors[self.color_index]}[Finished chain.]"
        }
        
        for old_text, new_text in agent_replacements.items():
            if old_text in cleaned_data:
                cleaned_data = cleaned_data.replace(old_text, new_text)
        
        self.buffer.append(cleaned_data)
        
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
    
    def flush(self):
        """Required method for CrewAI compatibility"""
        if self.buffer:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
    
    def isatty(self):
        """Required method for terminal compatibility"""
        return False
