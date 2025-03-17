from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import random
import sqlite3

base_url = "https://www.carrefour.tn/"

################################################
# Create a database in RAM
conn = sqlite3.connect('data.db')

cursor = conn.cursor()


# Creating necessary tables
query = '''
CREATE TABLE IF NOT EXISTS categories
             (id INTEGER PRIMARY KEY, name TEXT, img TEXT);
'''
query1 = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY, 
    name TEXT NOT NULL, 
    price TEXT NOT NULL, 
    img TEXT, 
    category_id INTEGER, 
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
'''

cursor.execute(query)
cursor.execute(query1)
conn.commit()
################################################

import undetected_chromedriver as uc

options = uc.ChromeOptions()
    
options.user_data_dir = "c:\\temp\\profile"
options.binary_location="/home/aziz/Downloads/chrome-linux64/chrome"

driver = uc.Chrome(
        options=options
      
)  
driver.get(base_url)

# Wait for categories to load
ll=WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.XPATH, "/html/body/div/main/div[2]/article/div[4]/div/div/div[1]/div/div/div"))
)[0]
categories = WebDriverWait(ll, 10).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "div"))
)[:8]
categorie_before_five=None
c= 1
for i, category in enumerate(categories):
    try:
        if i != 0:
            time.sleep(1)
            categories = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "slick-slide"))
            )
            if i >= 5:
                    ActionChains(driver).move_to_element(categories[i-c]).perform()
                    c+=1
                    next_button = driver.find_element(By.CLASS_NAME, "slick-next")
                    ActionChains(driver).move_to_element(next_button).click().perform()
            
            category = categories[i]
        
        category_name = category.text
        img = category.find_element(By.TAG_NAME, "img")
        src = img.get_attribute("src")

        id_category = random.randint(1, 1000)
        category_name_exist = cursor.execute(
            "SELECT * FROM categories WHERE name=?", (category_name,)
        ).fetchone()
        if category_name_exist is None:
            cursor.execute("INSERT INTO categories (id, name,img) VALUES (?, ?,?)", (id_category, category_name,src))
            conn.commit()

        ActionChains(driver).move_to_element(category).click().perform()

        # Wait for products to load
        products = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "category-categoryItem-7pb"))
        )

    except Exception as e:
        print(f"Error processing category: {e}")
        continue
    track_products = []
    time.sleep(2)  # Allow time for products to load
    for product in products:
        try:
            img = product.find_element(By.TAG_NAME, "img")
            src = img.get_attribute("src")
            product_name = product.find_element(By.CLASS_NAME, "item-name-LPg").text

            price_element = product.find_element(By.CLASS_NAME, "price-fraction-dIQ")
            price_text = price_element.text.strip().replace(",", ".")  # Convert price format
            price = price_text.replace("\n", "")

            product_exist = cursor.execute(
                "SELECT * FROM products WHERE name=?", (product_name,)
            ).fetchone()

            if product_exist is None:
                cursor.execute(
                    "INSERT INTO products (name, price, img, category_id) VALUES (?, ?, ?, ?)",
                    (product_name, price, src, id_category)
                )
                conn.commit()
            track_products.append(product_name)
    

        except Exception as e:
            print(f"Error processing product: {e}")
            continue
    driver.back()

    

driver.quit()
