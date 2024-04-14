# https://thoughtfulautomation.notion.site/RPA-Challenge-Fresh-news-2-0-37e2db5f88cb48d5ab1c972973226eb4

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException

# Time Based Imports
from datetime import datetime

# Type Imports
from typing import Literal

from dataclasses import dataclass

@dataclass
class NewsStory:
    title:str
    content:str
    date_created:datetime

class NewsScraper():
    def __init__(self, web_driver='Firefox') -> None:
        self.webdriver = web_driver

    def connect_driver(self, web_driver:str = Literal['Firefox','Chrome','Safari','Edge'], url:str="https://apnews.com/") -> webdriver:
        if web_driver is not None:
            if web_driver == 'Firefox':
                driver = webdriver.Firefox()
            elif web_driver == 'Chrome':
                driver = webdriver.Chrome()
            elif web_driver == 'Safari':
                driver = webdriver.Safari()
            elif web_driver == 'Edge':
                driver = webdriver.Edge()
        else:
            driver = self.webdriver

        driver.get(url)
        return driver

    def find_story_elements(self, driver:webdriver):
        stories = {}

        try:
            search_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='SearchOverlay-search-button']")))
            search_button.click()


            searchbox = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='q' and @class='SearchOverlay-search-input']")))
            searchbox.send_keys("trump")
            
            searchbox_button_submit= WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//button[@class='SearchOverlay-search-submit' and @type='submit']")))
            searchbox_button_submit.click()

            filter = WebDriverWait(driver,2).until(EC.element_to_be_clickable((By.XPATH,"//select[@class='Select-input' and @name='s']")))
            Select(filter).select_by_visible_text('Newest')


            # story_items = driver.find_elements(By.XPATH,"//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")
            story_items = WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located((By.XPATH, "//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")))

            for index,story in enumerate(story_items):
                try:
                    story_content = story.find_element(By.XPATH,"./div[@class='PagePromo']/div[@class='PagePromo-content']") #.get_attribute('innerHTML')
                    story_title = story_content.find_element(By.XPATH,"./bsp-custom-headline[@custom-headline='div']/div[@class='PagePromo-title']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']").text
                    story_description = story_content.find_element(By.XPATH,"./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']").text

                    story_timestamp = story_content.find_element(By.XPATH,"./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp").get_attribute('data-timestamp')
                    timestamp = datetime.utcfromtimestamp(float(story_timestamp)/1000)


                    stories[index] = NewsStory(title=story_title,content=story_description,date_created=timestamp)
                except StaleElementReferenceException:
                    return None

        finally:
            driver.close()

        return stories

def main():
    news_scraper = NewsScraper(web_driver='Firefox')
    driver = news_scraper.connect_driver(web_driver=news_scraper.webdriver)
    stories = news_scraper.find_story_elements(driver=driver)

    if stories is None:
        print("No stories found - re-running web scraping activity")
        driver.close() # Close current open connection
        driver = news_scraper.connect_driver(web_driver=news_scraper.webdriver)
        stories = news_scraper.find_story_elements(driver=driver)
    else:
         for story in stories.values():
            print(story.title)

if __name__=="__main__":
    main()