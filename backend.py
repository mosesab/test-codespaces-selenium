"""
Python 3.12.4
"""
import sys
import csv
import re
import traceback
from time import sleep, strftime, localtime
#from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

class Browser(object):
	def initialize_browser(self):
		# Initialize chrome_options
		chrome_options = uc.ChromeOptions()
		chrome_options.add_argument("--disable-search-engine-choice-screen")
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument("--disable-setuid-sandbox")
		chrome_options.add_argument("--use-fake-ui-for-media-stream")
		# Initialize the Chrome webdriver
		print(f"LOADING: Opening Chrome, This may take a while.")
		# Patch to fix a bug in uc
		executable_path = "/usr/local/bin/chromedriver"
		browser_path = "/usr/local/bin/chrome"
		driver = uc.Chrome(options=chrome_options, driver_executable_path=executable_path, browser_executable_path=browser_path, patcher_force_close=True)
		return driver
		
	


class ZoomBot(object):
	def __init__(self, driver , bot_name, meeting_url, stop_incoming_video):
		self.driver = driver
		self.bot_name = bot_name
		self.meeting_url = meeting_url
		self.stop_incoming_video = stop_incoming_video
		self.participants = []
		self.js_code =""
	def join_meeting(self, join_attempts=0):
		join_attempts += 1
		try:
			self.driver.get(self.meeting_url)
			print(f"LOADING: {self.meeting_url} - {join_attempts} attempts")
			try:
				launch_meeting_css_selector = 'div.mbTuDeF1[role="button"][tabindex="0"]'
				element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, launch_meeting_css_selector)))
				self.driver.find_elements(By.CSS_SELECTOR, launch_meeting_css_selector).click()
				print("clicked launch meeting Element.")
			except TimeoutException:
				pass
			except Exception as e:
				print(e)
			try:
				join_from_browser_css_selector = 'div.mbTuDeF1[role="button"][tabindex="0"]'
				element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, join_from_browser_css_selector)))
				self.driver.find_elements(By.CSS_SELECTOR, launch_meeting_css_selector).click()
				print("clicked join from browser Element.")
			except TimeoutException:
				pass
			except Exception as e:
				print(e)
			try:
				element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox-border")))
				print("HELP HELP HELP - I Encountered a Recaptcha Element.")
				sleep(12)
			except TimeoutException:
				pass
			except Exception as e:
				print(e)
			try:
				name_box_xpath = "//*[@id='input-for-name']"
				WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.XPATH, name_box_xpath))
			except TimeoutException:
				name_box_xpath = "//*[@id='inputname']"
				WebDriverWait(self.driver, 5).until, EC.presence_of_element_located((By.XPATH, name_box_xpath))	
			print(f"Joining Zoom Meeting - {join_attempts} attempts")
			name_box = self.driver.find_element(By.XPATH, name_box_xpath)
			name_box.clear()  # Clear any previous text in the search box
			name_box.send_keys(self.bot_name)
			join_button_xpath = "//button[contains(text(), 'Join')]"
			WebDriverWait(self.driver, 30).until, EC.element_to_be_clickable((By.XPATH, join_button_xpath))
			join_button = self.driver.find_element(By.XPATH, join_button_xpath)
			join_button.click()
		except Exception as e:
			# retry initialize 5 times
			if join_attempts >= 5:
				print(e)
				self.driver.close()
				raise
			else:
				print(f"An ERROR OCCURED: While Trying To Join Zoom Meeting, Retrying {join_attempts}.")
				print("This may be because the meeting has not yet started or has already ended.")
				return self.join_meeting(join_attempts)

	def is_meeting_ongoing(self, get_attempts=0):
		"""Check if meeting is ongoing and Log new participants' names"""
		get_attempts+=1
		try:
			try:
			    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,  "//span[text()='Participants']")))
			    self.driver.find_elements(By.XPATH, "//span[text()='Participants']")[0].click()
			except:
			    pass
			users = self.driver.find_elements(By.CLASS_NAME, "participants-item__name-section")
			if len(users[1:]) < 2 :
			    print("Participants are less than 2, so meeting has ended. Hurray, Hurray.")
			    return False
			for user in users[1:]:
				tempText = re.findall(r"^<span .*\">(.*)<\/span.*\">(.*)<\/span>", user.get_attribute("innerHTML").strip())
				uName = tempText[0][0] + tempText[0][1]
				if not uName in self.participants:
					self.participants.append(uName)
					print(f"New meeting participant found: {uName}")
			return True
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Did not find meeting participants')
				return None
			else:
				print(f"An ERROR OCCURED: While Trying To get Zoom Meeting participants, Retrying {get_attempts}.")
				return self.is_meeting_ongoing(get_attempts)





class GoogleMeetBot(object):
	def __init__(self, driver, meeting_url, bot_name):
		self.driver = driver
		self.meeting_url = meeting_url
		self.bot_name = bot_name
		self.participant_number = 0
		self.participants = []
		self.js_code =""
		self.google_username="pythonrobot007@gmail.com"
		self.google_password="python&007"
	def login(self, login_attempts=0): 
		login_attempts += 1
		url = 'https://accounts.google.com/'
		try:
			# google login page
			self.driver.get(url)
			# Finding username textbox and logging the username
			WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.ID, 'identifierId')).send_keys(self.google_username)
			WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.ID, 'identifierNext')).click()		
			# Finding password textbox and logging the password
			WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.NAME, 'password')).send_keys(self.google_password)
			WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.ID, 'passwordNext')).click()
			print("Logging Into Google")
			# HERE - WebDriverWait for login to complete successfully
		except:
			# retry initialize 5 times
			if login_attempts >= 5:
				print(traceback.format_exc())
				self.driver.close()
				raise
			else:
				print(f"An ERROR OCCURED: While Trying To Login to Google Account, Retrying {login_attempts}.")
				print("This may be because of 2-Factor Authentication.")
				return self.login(login_attempts)
				
	def join_meeting(self, join_attempts=0):
		join_attempts += 1
		try:
			self.driver.get(self.meeting_url)
			try:
				# Wait until the element is visible and clickable
				continue_button_xpath = "//span[contains(text(), 'Continue without microphone')]"
				continue_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, continue_button_xpath)))
				# Click the element
				continue_button.click()
			except:
				pass
			print(f"LOADING: {self.meeting_url} - {join_attempts} attempts")
			# Wait until the input field is visible
			name_input_xpath = "//input[@placeholder='Your name']"
			name_input = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, name_input_xpath)))
			name_input.send_keys(self.bot_name)
			ask_to_join_button_xpath = "//span[contains(text(), 'Ask to join')]/ancestor::button"
			# Wait until the "Ask to join" button is clickable
			ask_to_join_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, ask_to_join_button_xpath)))
			ask_to_join_button.click()
			print(f"Joining the Google Meet Meeting")
			# HERE - wait for join meeting page to open
			#WebDriverWait(self.driver, 30).until, EC.presence_of_element_located((By.XPATH, name_box_xpath))
		except:
			# retry initialize 5 times
			if join_attempts >= 5:
				print(traceback.format_exc())
				self.driver.close()
				raise
			else:
				print(f"An ERROR OCCURED: While Trying To Join Google Meet Meeting, Retrying {join_attempts}.")
				print("This may be because the meeting has not yet started or has already ended.")
				return self.join_meeting(join_attempts)
				
	def is_meeting_ongoing(self, get_attempts=0):
		get_attempts+=1
		"""Check if meeting is ongoing and Log new participants' names"""
		try:
			WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-self-name='You']")))
			participant_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-self-name='You']")
			if len(participant_elements) < 2 :
			    print("Participants are less than 2, so meeting has ended. Hurray, Hurray.")
			    return False
			for element in participant_elements:
				# Find the actual participant name within the element
				name_element = element.find_element(By.CLASS_NAME, 'dwSJ2e')
				uName = name_element.text
				if not uName in self.participants:
				    self.participants.append(uName)
				    print(f"New meeting participant found: {uName}")
			return True
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Error: is_meeting_ongoing: Did not find meeting participants')
				return None
			else:
				print(f"An ERROR OCCURED: While Trying To log Google Meeting participants, Retrying {get_attempts}.")
				return self.is_meeting_ongoing(get_attempts)
	
	
	

	
	




class MicrosoftTeamsBot(object):
    def __init__(self, driver, meeting_url, bot_name):
        self.driver = driver
        self.meeting_url = meeting_url
        self.bot_name = bot_name
        self.participants = []
        self.js_code =""
        self.microsoft_username="pythonrobot007@gmail.com"
        self.microsoft_password="python&007"
    def login(self, login_attempts=0): 
        login_attempts += 1
        try:
            # go to microsoft page
            self.driver.get(self.meeting_url)
            # wait for page to load
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
            if("login.microsoftonline.com" in self.driver.current_url):
                # Finding username textbox and logging the username
                emailField = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'i0116')))
                emailField.click()
                emailField.send_keys(self.microsoft_username)
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'idSIButton9'))).click() #Next button
                # Wait for the password page to load and input password
                passwordField = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'i0118')))
                passwordField.click()
                passwordField.send_keys(self.microsoft_password)
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'idSIButton9'))).click()
                # Handle stay signed in prompt
                WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, 'idSIButton9'))).click() #remember login
                print("Logging Into microsoft")
        except:
            # retry initialize 5 times
            if login_attempts >= 5:
                print(traceback.format_exc())
                self.driver.close()
                raise
            else:
                print(f"An ERROR OCCURED: While Trying To Login To Microsoft Account, Retrying {login_attempts}.")
                print("This may be because of 2-Factor Authentication.")
                return self.login(login_attempts)

    def join_meeting(self, join_attempts=0):
        join_attempts += 1
        try:
            self.driver.get(self.meeting_url)
            try:
                continue_button_xpath = "//button[@aria-label='Join meeting from this browser']"
                continue_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, continue_button_xpath)))
                continue_button.click()
            except:
                pass
            try:
                continue_button_xpath_2 = "//button[@aria-label='Join meeting from this browser']"
                continue_button_2 = WebDriverWait(self.driver, 120).until(EC.element_to_be_clickable((By.XPATH, continue_button_xpath_2)))
                continue_button_2.click()
            except:
                pass
            allow_to_join_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue without audio or video')]")))
            allow_to_join_button.click()
            try:
                join_button_xpath = "//button[contains(text(), 'Join meeting')]"
                join_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, join_button_xpath)))
                join_button.click()
            except:
                pass
            print(f"LOADING: {self.meeting_url} - {join_attempts} attempts")
            try: # sometimes there can be two join buttons
                join_button_2 = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, join_button_xpath)))
                join_button_2.click()
            except:
                pass
            # Wait until the input field is visible
            name_input_xpath = "//input[@placeholder='Type your name']"
            name_input = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, name_input_xpath)))
            name_input.send_keys(self.bot_name)
		# Wait until the "join now" button is clickable
            join_now_button_id = "prejoin-join-button"
            join_now_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, join_now_button_id)))
            join_now_button.click()
            print(f"Joining the Microsoft Teams Meeting")
        except:
            # retry initialize 5 times
            if join_attempts >= 5:
                print(traceback.format_exc())
                self.driver.close()
                raise
            else:
                print(f"An ERROR OCCURED: While Trying To Join Microsoft Teams Meeting, Retrying {join_attempts}.")
                print("This may be because the meeting has not yet started or has already ended.")
                return self.join_meeting(join_attempts)

    def is_meeting_ongoing(self, get_attempts=0):
        print("INFO: On Microsoft Teams, by default Selenium Bot uses JavaScript code to check if meeting has ended.")
        return None













