from duckduckgo_search import DDGS
from crewai.tools import tool

class DuckSearchTool:
    @tool("web search")
    def web_search(query: str):
        """
        Perform a web search using DuckDuckGo based on query.
        Useful for searching for information and articles.
        Args: query (str): The search query.
        Returns: list: List of search results with content and url sources.
        """
        return DDGS().text(query, max_results=10, timelimit="y")

    @tool("recent search")
    def recent_search(query: str):
        """
        Retrieve instant last and up to date answers from DuckDuckGo.
        Useful for getting up to date information for a query.
        Args: query (str): The search query.
        Returns: list: List of instant answers results.
        """
        return DDGS().text(query, max_results=5, timelimit="d")

    @tool("summary search")
    def summary_search(query: str):
        """
        Retrieve summary from DuckDuckGo for a query.
        Useful for getting summarization for a query or topic.
        Args: query (str): The search query.
        Returns: list: List of instant answers results.
        """
        return DDGS().answers(query)

    @tool("news search")
    def news_search(query: str):
        """
        Search for recent news about a topic using DuckDuckGo.
        Useful for finding latest news articles about any subject.
        Args: query (str): The search query (e.g., 'artificial intelligence', 'climate change')
        Returns: list: List of news results with title, body, date, source and url.
        """
        try:
            return DDGS().news(query, timelimit="w", max_results=10)
        except Exception as e:
            return f"Error searching news: {str(e)}"

    @tool("translate text")
    def translate_text(text: str):
        """
        Translate text to French using DuckDuckGo translator.
        Args: text (str): The text to translate.
        Returns: str: Translated text.
        """
        return DDGS().translate(text, source_language='auto', target_language='fr')

    @tool("ai chat")
    def ai_chat(query: str, model: str = 'gpt-3.5'):
        """
        Chat with DuckDuckGo AI.
        Args:
            query (str): The question to ask the AI.
            model (str): AI model to use ('gpt-3.5', 'claude-3-haiku', 'llama-3-70b', 'mixtral-8x7b').
        Returns: str: AI response.
        """
        return DDGS().chat(query, model=model)

    @tool("image search")
    def image_search(query: str, max_results: int = 10):
        """
        Search for images using DuckDuckGo.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results.
        Returns: list: List of image search results.
        """
        return DDGS().images(query, max_results=max_results)

    @tool("video search")
    def video_search(query: str, max_results: int = 10):
        """
        Search for videos using DuckDuckGo.
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results.
        Returns: list: List of video search results.
        """
        return DDGS().videos(query, max_results=max_results)

    @tool("map search")
    def map_search(query: str, max_results: int = 10):
        """
        Search for locations using DuckDuckGo Maps.
        Args:
            query (str): The location search query.
            max_results (int): Maximum number of results.
        Returns: list: List of map search results.
        """
        return DDGS().maps(query, max_results=max_results)
