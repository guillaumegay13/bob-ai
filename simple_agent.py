import json
from openai import OpenAI
import os
from tools import tools_registry, generate_tools_description

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # Set your API key as environment variable
)

def call_llm(prompt, messages_history=None, admin_mode=False):
    """Call OpenAI API and get response in specified JSON format"""
    
    # Dynamically generate tools description
    tools_description = generate_tools_description()
    
    response_format = """You must ALWAYS respond in valid JSON format with this exact structure:
{
    "response": "your response text to the user",
    "function_called": true or false,
    "function_name": "name_of_function_to_call",
    "function_args": {
        "arg_name1": "arg_value1",
        "arg_name2": "arg_value2"
    }
}

IMPORTANT: 
- The "response" field should contain your COMPLETE response to the user, including all analysis and details
- The "function_args" field should ONLY contain arguments for function calls, never analysis results
- When presenting search results, put ALL the information in the "response" field"""
    
    system_prompt = f"""You are an AI assistant with access to real-time tools and functions. You can help users by either answering directly or by calling specific functions to get accurate, up-to-date information.

{response_format}

Available functions you can call:

{tools_description}

Guidelines:
- When calling functions, provide arguments in "function_args" as key-value pairs
- Only provide required arguments and optional arguments you want to override
- Always provide a helpful "response" text explaining what you're doing
- If a user asks about available tools, describe them based on the information above
- IMPORTANT: When you receive search results, you MUST analyze and summarize them in a helpful way
- Extract the most relevant information and present it clearly to the user
- Focus on answering the user's specific question with the information from the results
- When presenting search results, include specific details like:
  * Restaurant/place names
  * Key descriptions or features
  * URLs when relevant
  * Any other concrete information that helps answer the user's question
- Set 'function_called' to true ONLY when you need to call a function, false when you can answer directly
- When you receive a "[FUNCTION RESULT]" message, analyze the results and provide a comprehensive response
- After receiving function results, set 'function_called' to false unless you need another function
- CRITICAL: When you receive search results, extract ALL the details (names, descriptions, URLs, etc.) and present them in a well-formatted response in the "response" field
- NEVER put analysis or search results in the "function_args" field - that's only for calling functions
"""
    
    # Add examples
    system_prompt += """
Examples:
User: "What's the weather in Paris in French?"
Response: {"response": "I'll check the current weather in Paris and provide it in French.", "function_called": true, "function_name": "get_weather", "function_args": {"location": "Paris", "lang": "fr"}}

User: "[FUNCTION RESULT] The get_weather function returned: Temperature: 15°C, Conditions: Partly cloudy, Humidity: 65%"
Response: {"response": "The current weather in Paris is 15°C (59°F) with partly cloudy skies and 65% humidity. It's a mild day with comfortable conditions for outdoor activities.", "function_called": false, "function_name": "", "function_args": {}}

User: "Hello!"
Response: {"response": "Hello! I'm here to help you with weather information, time zones, calculations, web searches, or just to chat. What can I do for you today?", "function_called": false, "function_name": "", "function_args": {}}
"""
    
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]
    
    if messages_history:
        messages.extend(messages_history)
    elif prompt:
        messages.append({"role": "user", "content": prompt})
    
    # Debug: show messages being sent
    if admin_mode:
        print(f"\n[DEBUG in call_llm: Total messages: {len(messages)}]")
        for i, msg in enumerate(messages[:3]):  # Show first 3 messages
            content_preview = msg.get('content', '')[:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', '')
            print(f"[DEBUG: Message {i} - Role: {msg.get('role')}, Content: '{content_preview}']")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        response_format={ "type": "json_object" }  # Force JSON response
    )
    
    # Print token usage in admin mode
    if admin_mode and response.usage:
        print(f"[DEBUG: Tokens - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}, Total: {response.usage.total_tokens}]")
    
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        # If JSON parsing fails, show the raw response for debugging
        print(f"\n❌ JSON Parse Error: {e}")
        print(f"Raw response: {response.choices[0].message.content[:500]}...")
        # Return a safe default response
        return {"response": "I encountered an error processing the results. Please try again.", "function_called": False, "function_name": "", "function_args": {}}

def get_user_friendly_message(function_name, function_args):
    """Get a user-friendly status message for a function call"""
    messages = {
        "brave_search": f"🔍 Searching the web for: {function_args.get('query', 'information')}...",
        "get_weather": f"🌤️ Checking weather in {function_args.get('location', function_args.get('city', 'the location'))}...",
        "get_time": f"🕐 Getting current time in {function_args.get('timezone', function_args.get('tz', 'UTC'))}...",
        "calculate": f"🧮 Calculating: {function_args.get('expression', function_args.get('expr', 'the expression'))}...",
        "dice_roll": f"🎲 Rolling dice..."
    }
    return messages.get(function_name, f"⚙️ Running {function_name}...")

# This function is no longer needed since we handle function calls inline
# Keeping it for potential future use but it's not called in the current implementation

# Main chat loop
def main():
    print("🤖 AI Agent Started! Type '/exit' to quit.")
    print(f"📋 Available tools: {', '.join(tools_registry.keys())}")
    print("💡 Tips:")
    print("   - Use '/mode' to switch between admin and user modes")
    print("   - Use '/clear' to clear conversation history and start fresh")
    print("   - Admin mode: See all function calls and results")
    print("   - User mode: See friendly status messages\n")
    
    admin_mode = True  # Start in admin mode by default
    messages_history = []  # Initialize conversation history once, outside the loop

    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for commands
        if user_input.strip().lower() == '/exit':
            print("\n👋 Goodbye!")
            break
        elif user_input.strip().lower() == '/clear':
            messages_history = []
            print("\n🗑️  Conversation history cleared! Starting fresh.\n")
            continue
        elif user_input.strip().lower() == '/mode':
            admin_mode = not admin_mode
            mode_name = 'Admin' if admin_mode else 'User'
            print(f"\n🔄 Switched to {mode_name} mode")
            if admin_mode:
                print("   You will see: function calls, arguments, and raw results")
            else:
                print("   You will see: friendly status messages only")
            print()
            continue
        
        # Process with LLM
        prompt = user_input
        
        try:
            # Add the new user message to conversation history
            messages_history.append({"role": "user", "content": prompt})
            
            # Single function mode
            function_called = True
            
            while function_called:
                if admin_mode:
                    print(f"\n[DEBUG: Conversation history length before call: {len(messages_history)}]")
                    print(f"[DEBUG: Last user message: '{messages_history[-1]['content']}']")
                
                # Always use conversation history
                response = call_llm(None, messages_history, admin_mode)
                
                if admin_mode:
                    print(f"[DEBUG: LLM Response Structure: {response}]")
                print(f"\nAI: {response['response']}")
                
                # Add assistant's response to history (just the text, not the full JSON)
                messages_history.append({"role": "assistant", "content": response['response']})
                
                function_called = response.get("function_called", False)
                
                # Debug: Show what's happening only if a function is being called
                if admin_mode and function_called:
                    print(f"[DEBUG: function_called = {function_called}]")
                
                if function_called:
                    # Extract function info
                    function_name = response.get("function_name", "")
                    function_args = response.get("function_args", {})
                    
                    if admin_mode:
                        print(f"\n🔧 Calling: {function_name}({', '.join([f'{k}={v}' for k, v in function_args.items()])})")
                    else:
                        print(f"\n{get_user_friendly_message(function_name, function_args)}")
                    
                    # Execute function
                    if function_name in tools_registry:
                        result = tools_registry[function_name](**function_args)
                        if admin_mode:
                            # Don't truncate results in admin mode - show everything
                            print(f"✅ Result: {result}")
                            print(f"[DEBUG: Will ask LLM to analyze these results...]")
                        
                        # Debug in user mode
                        if not admin_mode:
                            print(f"\n[Analyzing results...]")
                        
                        # Add function result to conversation history
                        function_result_message = f"""[FUNCTION RESULT]
The {function_name} function returned the following results:

{result}

Please analyze these results and provide a comprehensive response to the user. Include specific details like restaurant names, descriptions, and any other relevant information from the results."""
                        messages_history.append({"role": "user", "content": function_result_message})
                    else:
                        if admin_mode:
                            print(f"❌ Unknown function: {function_name}")
                        function_called = False
                            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        # Add a line break for readability
        print()  # Simple line break instead of separator

if __name__ == "__main__":
    main()