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

# Request Import For 

@dataclass
class NewsStory:
    title:str
    content:str
    date_created:datetime

class NewsScraper():
    def __init__(self, web_driver='Firefox') -> None:
        self.web_driver_type = web_driver
        self.webdriver = self.type_driver(web_driver=web_driver)

    # def child_driver(self, url:str) -> webdriver:
    #     child_driver = self.webdriver
    #     child_driver.get(url)
        
    #     return child_driver

    def type_driver(self, web_driver:str = Literal['Firefox','Chrome','Safari','Edge']) -> webdriver:
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
            driver = webdriver.Firefox()

        return driver

    def connect_driver(self, url:str="https://apnews.com/") -> webdriver:
        driver = self.webdriver
        driver.get(url)
        return driver

    def find_story_elements(self, driver: webdriver):
        stories = {}

        try:
            search_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='SearchOverlay-search-button']")
                )
            )
            search_button.click()

            searchbox = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[@name='q' and @class='SearchOverlay-search-input']",
                    )
                )
            )
            searchbox.send_keys("trump")

            searchbox_button_submit = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@class='SearchOverlay-search-submit' and @type='submit']",
                    )
                )
            )
            searchbox_button_submit.click()

            filter = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//select[@class='Select-input' and @name='s']")
                )
            )
            Select(filter).select_by_visible_text("Newest")

            # story_items = driver.find_elements(By.XPATH,"//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")
            story_items = WebDriverWait(driver, 20).until(
                EC.visibility_of_all_elements_located(
                    (
                        By.XPATH,
                        "//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']",
                    )
                )
            )

            for index, story in enumerate(story_items):
                try:
                    story_content = story.find_element(
                        By.XPATH,
                        "./div[@class='PagePromo']/div[@class='PagePromo-content']",
                    )

                    story_title = story_content.find_element(
                        By.XPATH,
                        "./bsp-custom-headline[@custom-headline='div']/div[@class='PagePromo-title']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']",
                    ).text

                    story_description = story_content.find_element(
                        By.XPATH,
                        "./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']",
                    ).text

                    story_timestamp = story_content.find_element(
                        By.XPATH,
                        "./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp",
                    ).get_attribute("data-timestamp")
                    timestamp = datetime.utcfromtimestamp(float(story_timestamp) / 1000)

                    # story_img_url = story.find_element(
                    #     By.XPATH,
                    #     "./div[@class='PagePromo']/div[@class='PagePromo-media']/a/picture/img[@class='Image']",
                    # ).get_attribute("src")

                    # download_img_driver = self.connect_driver(child_driver=True, url=story_img_url)
                    # img_to_write = download_img_driver.find_element(
                    #             By.TAG_NAME, "body"
                    #         ).screenshot_as_png
                    # with open("image_name.jpg", "wb") as file:
                    #     file.write(
                    #         img_to_write
                    #     )
                    # download_img_driver.close()

                    stories[index] = NewsStory(
                        title=story_title,
                        content=story_description,
                        date_created=timestamp,
                    )
                except StaleElementReferenceException:
                    return None

        finally:
            driver.close()

        return stories


def main():
    news_scraper = NewsScraper(web_driver='Firefox')
    driver = news_scraper.connect_driver()
    stories = news_scraper.find_story_elements(driver=driver)

    if stories is None:
        print("No stories found - re-running web scraping activity")
        # driver.close() # Close current open connection
        driver = news_scraper.connect_driver()
        stories = news_scraper.find_story_elements(driver=driver)
    else:
         for story in stories.values():
            print(story.title)

if __name__=="__main__":
    main()