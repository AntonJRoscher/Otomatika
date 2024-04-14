# https://thoughtfulautomation.notion.site/RPA-Challenge-Fresh-news-2-0-37e2db5f88cb48d5ab1c972973226eb4

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Time Based Imports
import time 
from datetime import datetime

driver = webdriver.Firefox()
driver.get("https://apnews.com/")
start = time.process_time()
# try:
search_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='SearchOverlay-search-button']"))).click()
print(time.process_time() - start)
searchbox = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='q' and @class='SearchOverlay-search-input']")))
print(time.process_time() - start)
searchbox.send_keys("trump")
searcbox_button_submit= WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='SearchOverlay-search-submit' and @type='submit']"))).click()
filter = WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//select[@class='Select-input' and @name='s']")))
select_opions = Select(filter).select_by_visible_text('Newest')


# story_items = driver.find_elements(By.XPATH,"//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")
story_items = WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located((By.XPATH, "//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")))

for story in story_items:
    story_content = story.find_element(By.XPATH,"./div[@class='PagePromo']/div[@class='PagePromo-content']") #.get_attribute('innerHTML')
    story_title = story_content.find_element(By.XPATH,"./bsp-custom-headline[@custom-headline='div']/div[@class='PagePromo-title']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']").text
    story_description = story_content.find_element(By.XPATH,"./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']").text
    story_updated_date = story_content.find_element(By.XPATH,"./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp/span").text
    story_timestamp = story_content.find_element(By.XPATH,"./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp").get_attribute('data-timestamp')
    timestamp = datetime.utcfromtimestamp(float(story_timestamp)/1000)
    # story_title = story_content.find_element(By.XPATH,"//div[@class='PagePromo-title']/a/span[@class='PagePromoContentIcons-text']").text

    print(f""" 
            {story_title} \n
            {story_description} \n
            # {story_updated_date} \n
            {timestamp} \n
    
    """) # USE DATA CLASS TO STORE INFO 

# finally:

driver.close()

# SearchResultsModule-formInput