from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from dotenv import load_dotenv
import asyncio
import os

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

async def main():
    # Initialize browser and context
    browser = Browser(config=browser_config)
    context = BrowserContext(browser=browser, config=context_config)
    
    try:
        # Initialize the AI model
        llm = ChatOpenAI(model="gpt-4o")

        # Define the task for the AI agent
        task = """
        Visit https://www.saucedemo.com/v1/ and explore all accessible pages of the website.
        Create a comprehensive list of functional E2E test cases covering all major user flows and features.
        Each test case should include:
        1. A clear title
        2. Preconditions
        3. Steps to execute
        4. Expected results

        Focus only on functional aspects of the website, not visual or performance testing.
        """

        agent = Agent(
            browser_context=context,
            task=task,
            llm=llm,
        )
        result = await agent.run()
        
        # Extract the final response or content from the AgentHistoryList
        if hasattr(result, "final_response"):
            content = result.final_response
        elif hasattr(result, "to_string"):
            content = result.to_string()
        elif hasattr(result, "__str__"):
            content = str(result)
        else:
            content = str(result)
        
        # Print information about the result for debugging
        print(f"Result type: {type(result)}")
        
        # Save the results to testcases.txt using UTF-8 encoding
        with open("testcases.txt", "w", encoding="utf-8") as file:
            file.write(content)
        
        print("Test Cases Generation Result:")
        print(content[:500] + "..." if len(content) > 500 else content)  # Print a preview
        print("\nTest cases have been saved to testcases.txt")
        
    finally:
        # Make sure to properly close the browser context
        await context.close()
        await browser.close()

# Run the asynchronous function
if __name__ == "__main__":
    asyncio.run(main())