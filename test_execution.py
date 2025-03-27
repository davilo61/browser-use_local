
# test_execution.py - Example script to verify SauceDemo test cases
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def run_sauce_demo_tests():
    # Initialize the driver
    driver = webdriver.Chrome()  # Or whichever browser you prefer
    
    try:
        # Navigate to the login page
        driver.get("https://www.saucedemo.com/v1/index.html")
        
        # Login
        driver.find_element(By.ID, "user-name").send_keys("standard_user")
        driver.find_element(By.ID, "password").send_keys("secret_sauce")
        driver.find_element(By.ID, "login-button").click()
        
        # Verify we're on the inventory page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
        )
        print("✅ Login successful")
        
        # Get all products
        products = driver.find_elements(By.CLASS_NAME, "inventory_item")
        print(f"Found {len(products)} products")
        
        # Test adding first product to cart
        add_buttons = driver.find_elements(By.CLASS_NAME, "btn_primary.btn_inventory")
        if add_buttons:
            add_buttons[0].click()
            
            # Verify cart badge updated
            cart_badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
            assert cart_badge.text == "1"
            print("✅ Add to cart functionality works")
        
        # More tests could be added here
        
        print("All tests completed successfully!")
        
    finally:
        # Clean up
        time.sleep(2)  # Just to see the final state
        driver.quit()

if __name__ == "__main__":
    run_sauce_demo_tests()
