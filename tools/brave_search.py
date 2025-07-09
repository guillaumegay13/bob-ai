import os
import re
import requests
from .base import Tool, ToolParameter

# Brave Search API key
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

def _brave_search_function(**kwargs):
    """Search the web using Brave Search API"""
    query = kwargs.get('query', kwargs.get('q', ''))
    count = kwargs.get('count', 5)
    country = kwargs.get('country', 'US')
    language = kwargs.get('language', 'en')
    safesearch = kwargs.get('safesearch', 'moderate')
    freshness = kwargs.get('freshness', None)
    result_types = kwargs.get('result_types', ['web'])
    
    if not query:
        return "Error: query parameter is required"
    
    if not BRAVE_API_KEY:
        return "Brave Search API key not configured. Please set BRAVE_SEARCH_API_KEY environment variable."
    
    if count < 1 or count > 20:
        return "Error: count must be between 1 and 20"
    
    try:
        # API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        # Build parameters
        params = {
            'q': query,
            'count': count,
            'country': country,
            'lang': language,
            'safesearch': safesearch
        }
        
        # Add optional parameters
        if freshness:
            params['freshness'] = freshness
            
        # Headers with API key
        headers = {
            'Accept': 'application/json',
            'X-Subscription-Token': BRAVE_API_KEY
        }
        
        # Make API request
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Process web results
            if 'web' in data and 'results' in data['web']:
                web_results = data['web']['results'][:count]
                
                for idx, result in enumerate(web_results, 1):
                    title = result.get('title', 'No title')
                    url = result.get('url', '')
                    description = result.get('description', 'No description')
                    
                    # Clean HTML tags from title and description
                    title = re.sub(r'<[^>]+>', '', title)
                    description = re.sub(r'<[^>]+>', '', description)
                    
                    # Clean up extra whitespace
                    title = ' '.join(title.split())
                    description = ' '.join(description.split())
                    
                    # Extract domain from URL for easier reading
                    domain = url.split('/')[2] if '/' in url else url
                    
                    results.append(f"{idx}. {title}\n   Source: {domain}\n   {description}\n   Full URL: {url}")
            
            # Add news results if requested
            if 'news' in result_types and 'news' in data:
                results.append("\n📰 News Results:")
                for news in data['news'].get('results', [])[:3]:
                    title = news.get('title', 'No title')
                    url = news.get('url', '')
                    age = news.get('age', '')
                    results.append(f"- {title} ({age})\n  {url}")
            
            # Add video results if requested
            if 'videos' in result_types and 'videos' in data:
                results.append("\n🎥 Video Results:")
                for video in data['videos'].get('results', [])[:3]:
                    title = video.get('title', 'No title')
                    url = video.get('url', '')
                    results.append(f"- {title}\n  {url}")
            
            # Add a note about the search query for context
            if results:
                header = f"Search results for '{query}'"
                if country != 'US' or language != 'en':
                    header += f" (country: {country}, language: {language})"
                
                # Add a summary at the top for easier parsing
                summary = f"\nFound {len([r for r in results if r.strip() and not r.startswith('📰') and not r.startswith('🎥')])} web results"
                if any('📰' in r for r in results):
                    summary += ", plus news articles"
                if any('🎥' in r for r in results):
                    summary += ", plus videos"
                
                return header + summary + ":\n\n" + "\n\n".join(results)
            else:
                # Check if we got any data at all
                if 'web' in data:
                    return f"No results found for '{query}'. The API returned data but no results matched."
                else:
                    return f"No results found for '{query}'. The API response was empty."
                
        elif response.status_code == 401:
            return "Invalid API key. Please check your BRAVE_SEARCH_API_KEY environment variable."
        elif response.status_code == 429:
            return "Rate limit exceeded. Please try again later."
        else:
            return f"Search failed with error code: {response.status_code}"
            
    except Exception as e:
        return f"Error performing search: {str(e)}"

# Create the tool instance
brave_search = Tool(
    name="brave_search",
    description="Search the web using Brave Search API for current information",
    function=_brave_search_function,
    parameters=[
        ToolParameter(
            name="query",
            type="string",
            description="Search query (e.g., 'latest AI news', 'python tutorials')",
            required=True
        ),
        ToolParameter(
            name="count",
            type="integer",
            description="Number of results to return (1-20)",
            required=False,
            default=5
        ),
        ToolParameter(
            name="country",
            type="string",
            description="Country code for localized results (e.g., 'US', 'GB', 'FR')",
            required=False,
            default="US"
        ),
        ToolParameter(
            name="language",
            type="string",
            description="Language code for results (e.g., 'en', 'fr', 'es')",
            required=False,
            default="en"
        ),
        ToolParameter(
            name="safesearch",
            type="string",
            description="Safe search level: 'off', 'moderate', or 'strict'",
            required=False,
            default="moderate"
        ),
        ToolParameter(
            name="freshness",
            type="string",
            description="Time range for results: 'pd' (past day), 'pw' (past week), 'pm' (past month), 'py' (past year)",
            required=False,
            default=None
        ),
        ToolParameter(
            name="result_types",
            type="array",
            description="Types of results to include: ['web', 'news', 'videos']",
            required=False,
            default=['web']
        )
    ]
)