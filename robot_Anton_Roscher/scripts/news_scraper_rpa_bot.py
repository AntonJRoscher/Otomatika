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
    word_count:int
    title_has_money:bool

class IO():
    def __init__(self) -> None:
        pass
    def write_excel(self, filename:str, Data:NewsStory, sheet_name:str):
        """ This function is responasble for writing the data to the excel file 
            filename: the name of the file to write to
            Data: the data to write to the file
            sheet_name: the name of the sheet to write to
        """
        try:
            workbook = xls.open('news_searches.xlsx')
        except FileNotFoundError:
            workbook  = xls.Workbook()

        worksheet  = workbook.create_sheet(sheet_name)
        worksheet.append(['Title','Story_Content','Date_Created','Image_Filename','word_count','title_has_money'])

        for row_num, news_story_data in enumerate(Data.values(), start=1):
            worksheet.append([news_story_data.title, news_story_data.content, news_story_data.date_created, news_story_data.img_filename, news_story_data.word_count, news_story_data.title_has_money])
            
        workbook.save('news_searches.xlsx')
        workbook.close()

class NewsScraper():
    def __init__(self) -> None:
        self.webdriver = Selenium()
        self.EXPECTED_CONDITION_WAIT_TIME = 5
        self.WAIT_TIME = 10
        # self.io = IO()

    def connect_driver(self, url:str="https://apnews.com/"):
        """ This function connects to the requested url parameter provided 
        url: The URL of the site to connect to, to recieve news articles"""

        driver = self.webdriver
        driver.open_available_browser(url)
        return driver

    def check_element_exists(self, driver, xpath:str, is_img:bool=False):
        """ This function checks whether or not an element exists before trying access it via its XPATH
        driver: web driver used to access element 
        xpath: the xpath of the element to check for"""

        try:
            if not is_img:
                length = len(driver.find_element("xpath",xpath).text)
            else:
                length = len(driver.find_element("xpath",xpath).get_attribute('outerHTML'))    
            if length >0:
                return True
            else:
                return False
        except Exception as e:
            logging.error(traceback.format_exc())
            return False
    
    def check_story_month(self, story_date:datetime, period_of_news:int):
        """ This function takes in the datetime of the story/article and compares it to the datetime range allowed/requested 
        to receive news for. 
        story_date: The datetime of the story/article
        period_of_news: The number of months to receive news for"""

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
 
    def write_image(self, img_driver, img_name, base_write_path:str) -> None:
        """ This functino writes the saved image from each article to a folder
            img_driver: the web driver used to access the image
            img_name: the name of the image
            base_write_path: the base path to write the image to
        """


        write_path = os.path.join(os.getcwd(),base_write_path)

        if not os.path.exists(write_path):
            os.mkdir(write_path)

        file_dir = write_path+'/'+img_name

        img_driver.capture_page_screenshot(filename=file_dir)

    def generate_filename(self, story_title:str):
        """ A function to generate the fiename of the image based on the title of the article. 
        story_title: the title of the article"""

        filename = story_title.replace(",","").replace(".","").replace(" ", "_")
        return filename+".png"

    def count_words(self, text:str):
        """ A function to count the number of words in a string """
        return len(text.split())

    def title_contains_money(self, text:str):
        """ I do know this is inefficient as it runs in O(n^2) time. However, 
        I choose to utilise the solution I understand, rather than regex as regex expressions aren't my strongest suit.   
        
        This function checks if there are money identifiers present in the title of the article 
        text: the title of the article
        """
        money_symbols = ["$", "€", "£"]
        for symbol in money_symbols:
            if symbol in text:
                return True
            return False


    def find_story_elements(self, driver , search_phrase:str, months_to_receive_news:int):
        """ This function is the main driver of the bot. 
        It takes in the web driver, the search phrase and the number of months to receive news for and finds the elements to interact with 
        to pull down the data for each article/story. It stores the information in a Data class structure and writes the image to the filesystem
        and article data into an excel file. 

        driver: the web driver used to access the page
        search_phrase: the search phrase used to find the articles/stories
        months_to_receive_news: the number of months to receive news for"""

        stories = {}
        try:
            # THIS WILL DELETE THE POP-UP ELEMENT BY ID. I, HOWEVER, DID NOT RECEIVE THIS POP-UP IN CONSISTENTLY. ONLY WHEN THROTTLING INTERNET SPEED TO BE SLOWER
            # IHAVE TEHEREFORE LEFT THE DELETION CODE IN - COMMENTED OUT 

            # delete_pop_up_node = """
            # element = document.getElementById("bx-group-2475153-9sIfbYI-h2");
            # element.remove();
            # """
            # driver.execute_script(delete_pop_up_node)

            search_button = driver.find_element("class:SearchOverlay-search-button")
            search_button.click()

            searchbox = driver.find_element(
                        "class:SearchOverlay-search-input"
                    )
            
            searchbox.send_keys(f"{search_phrase}")

            searchbox_button_submit = driver.find_element(
                        "//button[@class='SearchOverlay-search-submit' and @type='submit']"
                    )
            searchbox_button_submit.click()
            # # TODO - ENCAPSULATE THIS INTO A SEARCH FUNCTION

            filter = driver.find_element(
                "//select[@class='Select-input' and @name='s']")
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
                        comparison_timestamp = datetime(1990,1,1)

                    if not self.check_story_month(comparison_timestamp,period_of_news=months_to_receive_news):
                        print('Maximum timedelta reached for months requested')
                        return (2,stories)


                    filename = self.generate_filename(story_title=story_title)

                    if self.check_element_exists(driver=story, xpath= "./div/div/a/picture", is_img=True):
                        story_img_url = story.find_element("xpath",
                            "./div/div/a/picture/img"
                        ).get_attribute("src")

                        print(story_img_url)

                        driver.open_available_browser(story_img_url)
                        # driver.get(story_img_url)

                        self.write_image(driver,filename,"images/")

                        driver.close_window()
                        # driver.switch_to.window(driver.window_handles[0]) # Switch To First Window
                    # else:
                        # pass
                    else:
                        pass
                    
                    if (len(story_description) and len(story_title)) > 0:
                        word_count = self.count_words(story_title) + self.count_words(story_description) 
                    else: 
                        word_count = 0

                    if (len(story_title)) > 0:
                        title_contains_money = self.title_contains_money(story_title)
                    else:
                        title_contains_money = False


                    stories[index] = NewsStory(
                        title=story_title,
                        content=story_description,
                        date_created=timestamp,
                        img_filename=filename+".png",
                        word_count= word_count,
                        title_has_money= title_contains_money

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
    # Can use a loop to iterate through all items if there are more search terms that need to be added to the work item file 

    searchphrase = script_params_wi.get_work_item_variable("SEARCH_ITEM")
    months_to_receive_news = script_params_wi.get_work_item_variable("TIME_PERIOD")

    news_scraper = NewsScraper()
    driver = news_scraper.connect_driver()
    return_val,stories = news_scraper.find_story_elements(driver=driver, search_phrase=searchphrase,months_to_receive_news=months_to_receive_news)

    if return_val is None:
        print("Error Encountered during run \n Exiting...")
    elif return_val == 1:
        print("No stories found - re-running web scraping activity")
        driver.close_all_browsers()
        main()
    elif return_val == 2:
        print("Maximum stories reached for months requested \n Saving \n Exiting...")
        _io.write_excel("news_stories.xlsx",stories,sheet_name=searchphrase)
        sys.exit(0)
    else:
        _io.write_excel("news_stories.xlsx",stories,sheet_name=searchphrase)

if __name__=="__main__":
    main()