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

# Logging Import
import logging
import traceback

# Filesystem Import
import os 
# import xlsxwriter as xls
import openpyxl as xls 


@dataclass
class NewsStory:
    title:str
    content:str
    date_created:datetime
    img_filename:str

class IO():
    def __init__(self) -> None:
        pass

    def input_text(self, label:str):
        return input(f"{label}: ")
    def write_excel(self, filename:str, Data:NewsStory, sheet_name:str):

        workbook  = xls.Workbook()
        worksheet  = workbook.create_sheet()
        worksheet.append(['Title','Story_Content','Date_Created','Image_Filename'])

        for row_num, news_story_data in enumerate(Data.values(), start=1):
            worksheet.append([news_story_data.title, news_story_data.content, news_story_data.date_created, news_story_data.img_filename])
            
        workbook.save('news_searches.xlsx')

class NewsScraper():
    def __init__(self, web_driver='Firefox') -> None:
        self.web_driver_type = web_driver
        self.webdriver = self.type_driver(web_driver=web_driver)
        self.EXPECTED_CONDITION_WAIT_TIME = 5
        self.WAIT_TIME = 10
        # self.io = IO()

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

    def check_element_exists(self, driver:webdriver, xpath:str = "./div[@class='PagePromo']/div[@class='PagePromo-media']/a[@class='Link']/picture/img[@class='Image']"):
        try:
            if len(driver.find_elements(By.XPATH,xpath))>0:
                return True
            else:
                return False
        except StaleElementReferenceException:
            return False

    def write_image(self, img_driver:webdriver, img_name, base_write_path:str) -> None:
        img_to_write = img_driver.find_element(
                                By.XPATH,"//img"
                            ).screenshot_as_png
        write_path = os.path.join(os.getcwd(),base_write_path)

        if not os.path.exists(write_path):
            os.mkdir(write_path)

        with open(write_path+img_name, "wb") as file:
                file.write(
                img_to_write
            )

    def generate_filename(self, story_title:str):
        filename = story_title.replace(",","").replace(".","").replace(" ", "_")
        return filename+".png"

    def find_story_elements(self, driver: webdriver, search_phrase:str):
        stories = {}
        try:
            # TODO - HANDLE POP-UP IF PRESENT

            search_button = WebDriverWait(driver, self.EXPECTED_CONDITION_WAIT_TIME,poll_frequency=.2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='SearchOverlay-search-button']")
                )
            )
            search_button.click()

            searchbox = WebDriverWait(driver, self.EXPECTED_CONDITION_WAIT_TIME,poll_frequency=.2).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//input[@name='q' and @class='SearchOverlay-search-input']",
                    )
                )
            )
            
            searchbox.send_keys(f"{search_phrase}")

            searchbox_button_submit = WebDriverWait(driver, self.EXPECTED_CONDITION_WAIT_TIME,poll_frequency=.2).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@class='SearchOverlay-search-submit' and @type='submit']",
                    )
                )
            )
            searchbox_button_submit.click()
            # TODO - ENCAPSULATE THIS INTO A SEARCH FUNCTION

            filter = WebDriverWait(driver, self.EXPECTED_CONDITION_WAIT_TIME,poll_frequency=.2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//select[@class='Select-input' and @name='s']")
                )
            )
            Select(filter).select_by_visible_text("Newest")

            # driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

            # story_items = driver.find_elements(By.XPATH,"//main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']")
            story_items = WebDriverWait(driver, self.EXPECTED_CONDITION_WAIT_TIME).until(
                EC.presence_of_all_elements_located(
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

                    try:
                        story_description = story_content.find_element(
                            By.XPATH,
                            "./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']",
                        ).text
                    except StaleElementReferenceException:
                        story_description = story_content.find_element(
                            By.XPATH,
                            "./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']",
                        ).text

                    story_timestamp = story_content.find_element(
                        By.XPATH,
                        "./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp",
                    ).get_attribute("data-timestamp")
                    timestamp = datetime.utcfromtimestamp(float(story_timestamp) / 1000)


                    img_present = self.check_element_exists(driver=story)
                    filename = self.generate_filename(story_title=story_title)

                    if img_present:
                        story_img_url = story.find_element(
                            By.XPATH,
                            "./div[@class='PagePromo']/div[@class='PagePromo-media']/a[@class='Link']/picture/img[@class='Image']",
                        ).get_attribute("src")

                        driver.switch_to.new_window('window')
                        driver.get(story_img_url)

                        self.write_image(driver,filename,"images/")

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0]) # Switch To First Window
                    else:
                        pass


                    stories[index] = NewsStory(
                        title=story_title,
                        content=story_description,
                        date_created=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        img_filename=filename+".png",
                    )
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return None

        finally:
            driver.close()

        return stories

def main():
    _io = IO() 
    searchphrase = _io.input_text('Enter News Phrase to Search')
    news_scraper = NewsScraper(web_driver='Firefox')
    driver = news_scraper.connect_driver()
    stories = news_scraper.find_story_elements(driver=driver, search_phrase=searchphrase)

    if stories is None:
        print("No stories found - re-running web scraping activity")
        main()
    else:
        _io.write_excel("news_stories.xlsx",stories,sheet_name=searchphrase)

if __name__=="__main__":
    main()