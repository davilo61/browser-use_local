from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from dotenv import load_dotenv
import asyncio
import os
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Configure browser settings
browser_config = BrowserConfig(
    headless=False,
    disable_security=True
)

# Define browser context configuration
context_config = BrowserContextConfig(
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={'width': 1280, 'height': 1100},
    locale='en-US',
    highlight_elements=True,
    viewport_expansion=500,
)

def format_test_cases(text):
    """Format the test cases with proper line breaks."""
    # Replace literal '\n' strings with actual newlines
    text = text.replace('\\n', '\n')
    
    # Make sure test case numbers start on new lines
    text = re.sub(r'(\d+\.\s+\*\*Test Case Title\*\*)', r'\n\1', text)
    
    # Make sure sections start on new lines
    text = re.sub(r'(\s+-\s+\*\*Preconditions\*\*)', r'\n\1', text)
    text = re.sub(r'(\s+-\s+\*\*Steps to Execute\*\*)', r'\n\1', text)
    text = re.sub(r'(\s+-\s+\*\*Expected Results\*\*)', r'\n\1', text)
    
    # Make sure numbered steps are on new lines with proper indentation
    text = re.sub(r'(\d+\.\s+[^\n]+?)(?=\d+\.|$|\n\s+-\s+\*\*)', r'\n     \1\n', text)
    
    # Clean up any multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

async def main():
    # Initialize browser and context
    browser = Browser(config=browser_config)
    context = BrowserContext(browser=browser, config=context_config)
    
    try:
        # Initialize the AI model
        llm = ChatOpenAI(model="gpt-4o")

        # Step 1: Use the agent to explore the website with specific instructions for output format
        exploration_task = """
        Visit https://www.saucedemo.com/v1/ and explore all accessible pages of the website.
        
        After your exploration, create a list of functional E2E test cases.
        
        Format each test case exactly like this example:
        
        1. **Test Case Title**: Login with Valid Credentials
           - **Preconditions**: Access to the internet and a browser. User account credentials.
           - **Steps to Execute**:
             1. Open the browser and go to 'https://www.saucedemo.com/v1/'.
             2. Enter the username 'standard_user'.
             3. Enter the password 'secret_sauce'.
             4. Click on the 'Login' button.
           - **Expected Results**: User should be logged into the inventory page.
        
        Create at least 10 test cases covering login, product browsing, cart operations, checkout process, and user account functions.
        
        IMPORTANT: Your final response must ONLY contain the numbered and formatted test cases, with no introduction or conclusion text.
        """

        agent = Agent(
            browser_context=context,
            task=exploration_task,
            llm=llm,
        )
        
        print("Starting website exploration and test case generation...")
        exploration_result = await agent.run()
        print("Process completed.")
        
        # Get a string representation of the result
        raw_output = str(exploration_result)
        
        # Try to extract test cases using regex patterns
        test_case_pattern = r'(\d+\.\s+\*\*Test Case Title\*\*:.*?)(?=\d+\.\s+\*\*Test Case Title\*\*:|$)'
        matches = re.findall(test_case_pattern, raw_output, re.DOTALL)
        
        if matches:
            # If we found structured test cases in the output
            test_cases = "\n".join(matches)
        else:
            # If we can't find formatted test cases, use a fallback approach
            # Extract any content that might resemble test cases
            fallback_content = raw_output[-10000:] if len(raw_output) > 10000 else raw_output
            test_cases = fallback_content
        
        # Format the test cases with proper line breaks
        formatted_test_cases = format_test_cases(test_cases)
        
        # Save the extracted test cases
        with open("testcases.txt", "w", encoding="utf-8") as file:
            file.write(formatted_test_cases)
        
        print("Test cases have been saved to testcases.txt")
        print("Please check the file contents to ensure they match the expected format.")
        
    finally:
        # Make sure to properly close the browser context
        await context.close()
        await browser.close()

# Run the asynchronous function
if __name__ == "__main__":
    asyncio.run(main())