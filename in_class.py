from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
#import undetected_chromedriver as uc
import time
#from webdriver_manager.microsoft import EdgeChromiumDriverManager

#driver = webdriver.Edge(executable_path=r'C:\Users\dc116\Documents\edgedriver_win64')
#driver = uc.Chrome()
driver = webdriver.Firefox()
driver.get("https://www.rottentomatoes.com/")
time.sleep(5)
textbox = driver.find_element(By.XPATH, '/html/body/div[3]/rt-header/search-algolia/search-algolia-controls/input')
textbox.clear()
textbox.send_keys("Spiderman")
textbox.send_keys(Keys.RETURN)

for x in range(1, 7):
    time.sleep(5)
    driver.find_element(By.XPATH, f'/html/body/div[3]/main/div/div/section[1]/div/search-page-result[1]/ul/search-page-media-row[{x}]/a[2]').click()
    time.sleep(5)
    print(driver.find_element(By.XPATH, '/html/body/div[3]/main/div[1]/section/div[2]/section[1]/div[1]/score-board-deprecated/h1').text)
    #print(driver.find_element(By.XPATH, '//*[@id="rating"]').text)
    print(driver.find_element(By.XPATH, '/html/body/div[3]/main/div/section/div[2]/section[1]/div[1]/score-board-deprecated/p').text)
    time.sleep(3)
    driver.back()