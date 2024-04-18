# https://thoughtfulautomation.notion.site/RPA-Challenge-Fresh-news-2-0-37e2db5f88cb48d5ab1c972973226eb4

# Selenium Imports
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.support.ui import Select


# Time Based Imports
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# Type Imports
from dataclasses import dataclass

# Logging Import
import logging
import traceback

# Filesystem Import
import os 
import sys
import openpyxl as xls 

# Robocorp Import
from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems
# from RPA.Robocorp.WorkItems import WorkItems



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
        try:
            workbook = xls.open('news_searches.xlsx')
        except FileNotFoundError:
            workbook  = xls.Workbook()

        worksheet  = workbook.create_sheet(sheet_name)
        worksheet.append(['Title','Story_Content','Date_Created','Image_Filename'])

        for row_num, news_story_data in enumerate(Data.values(), start=1):
            worksheet.append([news_story_data.title, news_story_data.content, news_story_data.date_created, news_story_data.img_filename])
            
        workbook.save('news_searches.xlsx')
        workbook.close()

class NewsScraper():
    def __init__(self) -> None:
        self.webdriver = Selenium()
        self.EXPECTED_CONDITION_WAIT_TIME = 5
        self.WAIT_TIME = 10
        # self.io = IO()

    def type_driver(self):
        driver = Selenium().brow

        return driver

    def connect_driver(self, url:str="https://apnews.com/"):
        driver = self.webdriver
        driver.open_available_browser(url)
        return driver

    def check_element_exists(self, driver, xpath:str):
        try:
            if len(driver.find_element("xpath",xpath).text)>0:
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def check_story_month(self, story_date:datetime, period_of_news:int):
        today = datetime.today()
        if ((period_of_news != 0) and (period_of_news !=1)):
            if today.month == 12:
                last_date = datetime(today.year, today.month, 31)
            else:
                last_date = datetime(today.year, today.month - 1, 1) + timedelta(days=1) # get last months end date + 1 day 
            if story_date >= last_date:
                return True
            else:
                return False
        else: 
            end_range = today - relativedelta(months=period_of_news) 
            last_date = datetime(end_range.year, end_range.month-1, 1) + timedelta(days=1) # get last months end date + 1 day
            if story_date >= last_date :
                return True
            else:
                return False
 
    def write_image(self, img_driver, img_name, base_write_path:str, search_phrase:str) -> None:
        img_to_write = img_driver.find_element("xpath","//img"
                            ).screenshot_as_png
        write_path = os.path.join(os.getcwd(),base_write_path+search_phrase)
        print(write_path)

        if not os.path.exists(write_path):
            os.mkdir(write_path)

        file_dir = write_path+'/'+img_name
        with open(file_dir, "wb") as file:
                file.write(
                img_to_write
            )

    def generate_filename(self, story_title:str):
        filename = story_title.replace(",","").replace(".","").replace(" ", "_")
        return filename+".png"

    def find_story_elements(self, driver , search_phrase:str, months_to_receive_news:int):
        stories = {}
        try:
            # THIS WILL DELETE THE POP-UP ELEMENT BY ID. I, HOWEVER, DID NOT RECEIVE THIS POP-UP IN CONSISTENTLY. ONLY WHEN THROTTLING INTERNET SPEED TO BE SLOWER
            # IHAVE TEHEREFORE LEFT THE DELETION CODE IN - COMMENTED OUT 

            # delete_pop_up_node = """
            # element = document.getElementById("bx-group-2475153-9sIfbYI-h2");
            # element.remove();
            # """
            # driver.execute_script(delete_pop_up_node)

            search_button = driver.find_element("//button[@class='SearchOverlay-search-button']")
            search_button.click()

            searchbox = driver.find_element(
                        "//input[@name='q' and @class='SearchOverlay-search-input']"
                    )
            
            searchbox.send_keys(f"{search_phrase}")

            searchbox_button_submit = driver.find_element(
                        "//button[@class='SearchOverlay-search-submit' and @type='submit']"
                    )
            searchbox_button_submit.click()
            # # TODO - ENCAPSULATE THIS INTO A SEARCH FUNCTION

            filter = driver.find_element("//select[@class='Select-input' and @name='s']")
            filter.click()
            Select(filter).select_by_visible_text("Newest")
            

            story_items = driver.find_elements(
                        "//body[@class='Page-body']/div[@class='SearchResultsPage-content']/bsp-search-results-module[@class='SearchResultsModule']/form[@class='SearchResultsModule-form']/div[@class='SearchResultsModule-ajax']/div[@class='SearchResultsModule-ajaxContent']/bsp-search-filters[@class='SearchResultsModule-filters']/div[@class='SearchResultsModule-wrapper']/main[@class='SearchResultsModule-main']/div[@class='SearchResultsModule-results']/bsp-list-loadmore[@class='PageListStandardD']/div[@class='PageList-items']/div[@class='PageList-items-item']"
                    )

            for index, story in enumerate(story_items):
                # TEST IF WE ARE AT THE LAST ELEMENT OF THE STORIES PRESENT IN PAGE 
                try:
                    # print(story.get_attribute('innerHTML'))
                    if self.check_element_exists(driver=story, xpath="./div[@class='PagePromo']/div[@class='PagePromo-content']"):   
                        story_content = story.find_element("xpath",
                            "./div[@class='PagePromo']/div[@class='PagePromo-content']"
                        )
                    else: 
                        print('No stories found during enumeration')
                        return (1,None) # Break program flow - no stories 

                    if self.check_element_exists(driver=story_content,xpath="./bsp-custom-headline[@custom-headline='div']/div[@class='PagePromo-title']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']"):
                        story_title = story_content.find_element("xpath",
                            "./bsp-custom-headline[@custom-headline='div']/div[@class='PagePromo-title']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']"
                        ).text
                    else:
                        story_title = ""

                    if self.check_element_exists(driver=story_content, xpath="./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']"):
                        story_description = story_content.find_element("xpath",
                            "./div[@class='PagePromo-description']/a[@class='Link ']/span[@class='PagePromoContentIcons-text']"
                        ).text
                    else: 
                        story_description = ""
                        
                    if self.check_element_exists(driver=story_content,xpath="./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp"):
                        story_timestamp = story_content.find_element("xpath",
                            "./div[@class='PagePromo-byline']/div[@class='PagePromo-date']/bsp-timestamp"
                        ).get_attribute("data-timestamp")

                        comparison_timestamp = datetime.utcfromtimestamp(float(story_timestamp) / 1000)
                        timestamp = comparison_timestamp.strftime("%Y-%m-%d %H:%M:%S")

                    else:
                        timestamp = ""

                    if not self.check_story_month(comparison_timestamp,period_of_news=months_to_receive_news):
                        print('Maximum timedelta reached for months requested')
                        return (2,stories)


                    filename = self.generate_filename(story_title=story_title)

                    if self.check_element_exists(driver=story, xpath="./div[@class='PagePromo']/div[@class='PagePromo-media']/a[@class='Link']/picture/img[@class='Image']"):
                        story_img_url = story.find_element("xpath",
                            "./div[@class='PagePromo']/div[@class='PagePromo-media']/a[@class='Link']/picture/img[@class='Image']"
                        ).get_attribute("src")

                        driver.switch_to.new_window('window')
                        driver.get(story_img_url)

                        self.write_image(driver,filename,"images/",search_phrase=search_phrase)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0]) # Switch To First Window
                    else:
                        pass


                    stories[index] = NewsStory(
                        title=story_title,
                        content=story_description,
                        date_created=timestamp,
                        img_filename=filename+".png",
                    )
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return (None,None)

        finally:
            # driver.close()
            pass

        return (0,stories)



@task
def main():
    _io = IO() 
    # searchphrase = _io.input_text('Enter News Phrase to Search')
    # months_to_receive_news = int(_io.input_text('Enter Months to Receive News'))

    script_params_wi = WorkItems()
    script_params_wi.get_input_work_item()

    searchphrase = script_params_wi.get_work_item_variable("SEARCH_ITEM")
    months_to_receive_news = script_params_wi.get_work_item_variable("TIME_PERIOD")

    news_scraper = NewsScraper()
    driver = news_scraper.connect_driver()
    return_val,stories = news_scraper.find_story_elements(driver=driver, search_phrase=searchphrase,months_to_receive_news=months_to_receive_news)

    if return_val is None:
        print("Error Encountered during run \n Exiting...")
    elif return_val == 1:
        print("No stories found - re-running web scraping activity")
        main()
    elif return_val == 2:
        print("Maximum stories reached for months requested \n Saving \n Exiting...")
        _io.write_excel("news_stories.xlsx",stories,sheet_name=searchphrase)
        sys.exit(0)
    else:
        _io.write_excel("news_stories.xlsx",stories,sheet_name=searchphrase)

if __name__=="__main__":
    main()