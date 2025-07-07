import json
from openai import OpenAI
import os
import requests
from urllib.parse import quote

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Set your API key as environment variable
)    

# OpenWeatherMap API key
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Define available functions
def get_weather(location):
    """Get real weather data from OpenWeatherMap API"""
    if not WEATHER_API_KEY:
        return "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    try:
        
        # API endpoint - exact format as provided
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}"
        
        # Make API request
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather information
            temp_kelvin = data['main']['temp']
            temp_celsius = round(temp_kelvin - 273.15, 1)  # Convert from Kelvin to Celsius
            feels_like_celsius = round(data['main']['feels_like'] - 273.15, 1)
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return f"Weather in {location}: {description}, Temperature: {temp_celsius}°C (feels like: {feels_like_celsius}°C), Humidity: {humidity}%, Wind: {wind_speed} m/s"
        elif response.status_code == 401:
            return "Invalid API key. Please check your OPENWEATHER_API_KEY environment variable."
        elif response.status_code == 404:
            return f"City '{location}' not found. Please check the city name and try again."
        else:
            return f"Unable to get weather for {location}. Error code: {response.status_code}"
            
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

def get_time(timezone="UTC"):
    import time
    return f"Il est {time.strftime('%H:%M:%S')} ({timezone})"

def calculate(expression):
    try:
        result = eval(expression)
        return f"Le résultat est: {result}"
    except:
        return "Erreur de calcul"

# Function mapping
functions = {
    "get_weather": get_weather,
    "get_time": get_time,
    "calculate": calculate
}

def call_llm(prompt):
    """Call OpenAI API and get response in specified JSON format"""
    
    system_prompt = """You are an AI assistant with access to real-time tools and functions. You can help users by either answering directly or by calling specific functions to get accurate, up-to-date information.

        You must ALWAYS respond in valid JSON format with this exact structure:
        {
            "response": "your response text to the user",
            "function_called": true or false,
            "function_name": "name_of_function_to_call",
            "function_argument": "argument_to_pass_to_function"
        }

        Available functions you can call:
        1. get_weather(location) - Get real-time weather information for any city
        - Example: get_weather("Paris") or get_weather("New York")
        
        2. get_time(timezone) - Get current time in a specific timezone
        - Example: get_time("Europe/Paris") or get_time("America/New_York")
        - Default is UTC if no timezone specified
        
        3. calculate(expression) - Perform mathematical calculations
        - Example: calculate("2 + 2 * 3") or calculate("sqrt(16)")

        Guidelines:
        - Set "function_called" to true ONLY when you need to call a function to answer the user
        - Set "function_called" to false when you can answer directly without calling a function
        - When calling a function, provide clear and accurate arguments
        - Always provide a helpful "response" text explaining what you're doing
        - If the user asks about weather, time, or calculations, use the appropriate function
        - Be conversational and helpful in your responses

        Examples:
        User: "What's the weather in London?"
        Response: {"response": "I'll check the current weather in London for you.", "function_called": true, "function_name": "get_weather", "function_argument": "London"}

        User: "Hello, how are you?"
        Response: {"response": "Hello! I'm doing well, thank you for asking. I'm here to help you with weather information, time zones, calculations, or just to chat. How can I assist you today?", "function_called": false, "function_name": "", "function_argument": ""}
        """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return json.loads(response.choices[0].message.content)

# Main chat loop
print("🤖 AI Agent Started! Type '/exit' to quit.\n")

while True:
    # Get user input
    user_input = input("You: ")
    
    # Check for exit command
    if user_input.strip().lower() == '/exit':
        print("\n👋 Goodbye!")
        break
    
    # Process with LLM
    prompt = user_input
    function_called = True
    
    # Function calling loop
    while function_called:
        # Call LLM
        response = call_llm(prompt)
        
        # Extract the response text
        print(f"\nAI: {response['response']}")
        
        function_called = response["function_called"]
        
        if function_called:
            # Extract function info
            function_name = response["function_name"].replace("()", "")
            argument = response["function_argument"]
            
            print(f"\n🔧 Calling: {function_name}({argument})")
            
            # Execute function
            if function_name in functions:
                result = functions[function_name](argument)
                print(f"✅ Result: {result}")
                
                # Update prompt with result for next iteration
                prompt = f"The function {function_name} returned: {result}. Please provide a final response to the user."
            else:
                print(f"❌ Unknown function: {function_name}")
                function_called = False
    
    print()  # Empty line for readability