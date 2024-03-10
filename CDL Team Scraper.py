#Devin Cooke
#Used this for WebDriver Wait: https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html
#https://www.selenium.dev/documentation/webdriver/waits/
#Scraping results from each match in the Call of Duty League, 171 page loads, dynamically scrapes match results this should work even after they are updated too.
#(Realistically I do not think that the site has been majorly changed over the past 2 years other than data input)
#Used WebDriver Wait to improve speed 
#For each match result this program scrapes the data: (Event Played, Team1, Team2, Team1 Total Score, Team2 Total Score, Date, Map Results)
#Map Results for each map: (Team1 Score, Team2 Score, Map, Mode, Winner)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import time

class CDL_team_results:
    #Init
    def __init__(self, base_url="https://callofdutyleague.com/en-us/schedule?utm_source=cdlweb&utm_medium=navigationbar&utm_campaign=general"):
        self.driver = webdriver.Firefox()
        self.base_url = base_url
        self.matches_data = []
        self.page_loads = 0

    #Checks if row contains an ad by searching for the link
    def is_ad_element(self, element):
        ad_anchor = element.find_elements(By.CSS_SELECTOR, 'a[href="https://pickem.callofdutyleague.com"]')
        return len(ad_anchor) > 0

    #Scrapes both team names, team scores, date played, and adds scores to determine total rounds played.
    #Find (map/mode, both team score, winner) per game (multiple games per match)
    #team{x}_tot: how many games that team won
    def scrape_match(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.matchup-headerstyles__TeamLongName-sc-11r2gmu-15:nth-child(3)')))
        team1 = self.driver.find_element(By.CSS_SELECTOR, 'span.matchup-headerstyles__TeamLongName-sc-11r2gmu-15:nth-child(3)').text
        team1_tot = int(self.driver.find_element(By.CSS_SELECTOR, '.matchup-headerstyles__LeftScore-sc-11r2gmu-9').text)
        team2 = self.driver.find_element(By.CSS_SELECTOR, 'span.matchup-headerstyles__TeamLongName-sc-11r2gmu-15:nth-child(2)').text
        team2_tot = int(self.driver.find_element(By.CSS_SELECTOR, '.matchup-headerstyles__RightScore-sc-11r2gmu-10').text)
        date = self.driver.find_element(By.CSS_SELECTOR, '.rendercdl-match-detailstyles__VideoStreamDate-sc-1i9oyql-7').text
        tot_rnd = int(team2_tot) + int(team1_tot)
        maps_details = []
        for map_index in range(1, tot_rnd + 1):
            map_xpath_base = f'/html/body/div[2]/div/div/div[3]/div[3]/section/div[2]/div[{map_index}]'
            map_name = self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[3]/div[1]/span[2]').text
            mode_name = self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[3]/div[1]/span[1]').text
            try:
                map_score1 = int(self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[2]/div/span').text)
            except: 
                try:
                    map_score1 = int(self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[2]/div/span[2]').text)
                except ValueError:
                    map_score1 = 0
            try:
                map_score2 = int(self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[4]/div/span').text)
            except: 
                try:
                    map_score2 = int(self.driver.find_element(By.XPATH, f'{map_xpath_base}/div/div[2]/div[4]/div/span[2]').text)
                except ValueError:
                    map_score2 = 0

        #format = 'LAN' if event % 2 == 0 else 'ONLINE' #Format Text
            map_winner = team1 if map_score1 > map_score2 else team2
                

            maps_details.append({
                'map_name': map_name,
                'mode_name': mode_name,
                'map_winner': map_winner,
                'team1_score': map_score1,
                'team2_score': map_score2
            })


        match_data = {
            'team1': team1,
            'team1_score': team1_tot,
            'team2': team2,
            'team2_score': team2_tot,
            'total_rounds': tot_rnd,
            'date': date,
            'maps': maps_details
        }
        return match_data

    #Searches the row element for the results link (an ad moves it) 
    def find_results(self, event, match, length_of_section_class):
        row_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'div.css-ufg8u0:nth-child({event}) > div:nth-child({match})')
            )
        )
        #If ad then the match link is in a different place
        if self.is_ad_element(row_element):
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'div.css-ufg8u0:nth-child({event}) > div:nth-child({match}) > div:nth-child(2) > div:nth-child(3) > a:nth-child(1) > div:nth-child(1) > p:nth-child(2)')
                )
            ).click()
            self.page_loads += 2
            #self.scrape_match(event_data)
        else:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'div.css-ufg8u0:nth-child({event}) > div:nth-child({match}) > div:nth-child(1) > div:nth-child(3) > a:nth-child(1) > div:nth-child(1) > p:nth-child(2)')
                )
            ).click()
            self.page_loads += 2

        match_data = self.scrape_match()
        self.driver.back()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#completed_matches"))).click()
            #tournament_data.append(self.scrape_match(driver))
        print(f'Scraped match: ({match - 2}/{length_of_section_class - 2})')
        return match_data

    #Finds tournament details and calls find_results for each row in the event
    def scrape_event(self, event):
        major = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f'div.css-ufg8u0:nth-child({event}) > div:nth-child(1)')#Major Text
            )
        ).text
        #Finds format (Online/LAN)
        format = 'LAN' if event % 2 == 0 else 'ONLINE' #Format Text
        tournament = f'{major} {format}'
        print(f'Scraping {tournament}...')

        #Finds amount of matches in tournament
        elements = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'div.css-ufg8u0:nth-child({event}) > div')))
        length_of_section_class = len(elements)
        tournament_data = {
            'tournament': tournament,
            'matches': []
        }
        print(f'MATCHES PLAYED: {length_of_section_class - 2}')
        #Find the link to the results for each match in the event
        for match in range(3, length_of_section_class + 1): #Actual loop (Each match)
        #for match in range(3, 4): #For testing purposes
            match_data = self.find_results(event, match, length_of_section_class)
            tournament_data['matches'].append(match_data)


        self.matches_data.append(tournament_data)

    #Scrape each event
    def scrape_all_events(self, file_name):
        self.driver.get(self.base_url)
        self.page_loads += 1
        time.sleep(3)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-close-btn-container > button"))).click() #Close cookie bar
        time.sleep(5)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#completed_matches"))).click() #Click completed matches button

        events = len(WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-ufg8u0')))) #Finds length of event list
        for event in range(1, events + 1):  # Use a smaller range for testing
        #for event in range(1, 2): # Testing
            self.scrape_event(event)

        print(f'Page Loads: {self.page_loads}')
        self.driver.close()

        #Writes to json
        try:
            with open(file_name, 'w') as file:
                json.dump(self.matches_data, file, indent=4)
            print(f'Data has been written to {file_name}')
        except Exception as e:
            print(f"Error writing to file: {e}")

if __name__ == "__main__":
    scraper = CDL_team_results()
    scraper.scrape_all_events(file_name='matches_data.json')