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
		chrome_options.add_argument("--disable-setuid-sandbox")
		chrome_options.add_argument("--use-fake-ui-for-media-stream")
		# Initialize the Chrome webdriver
		print(f"LOADING: Opening Chrome, This may take a while.")
		# Patch to fix a bug in uc
		executable_path = "/usr/local/bin/chromedriver"
		driver = uc.Chrome(options=chrome_options, driver_executable_path=executable_path)
		
		return driver
		
	


class ZoomBot(object):
	def __init__(self, driver , bot_name, meeting_url, stop_incoming_video):
		self.driver = driver
		self.bot_name = bot_name
		self.meeting_url = meeting_url
		self.stop_incoming_video = stop_incoming_video
		self.participants = []
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

	def log_participants(self, get_attempts=0):
		"""Log participants' names"""
		try:
			self.driver.find_elements(By.XPATH, "//span[text()='Participants']")[0].click()

			users = self.driver.find_elements(By.CLASS_NAME, "participants-item__name-section")
			for user in users[1:]:
				tempText = re.findall(r"^<span .*\">(.*)<\/span.*\">(.*)<\/span>", user.get_attribute("innerHTML").strip())
				uName = tempText[0][0] + tempText[0][1]
				if not uName in self.participants:
					self.participants.append(uName)
			print(f"Searched for meeting participants: {self.participants}")
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Did not find meeting participants')
			else:
				print(f"An ERROR OCCURED: While Trying To get Zoom Meeting participants, Retrying {get_attempts}.")
				return self.log_participants(get_attempts)
			
	def get_current_speaker(self, get_attempts=0):
		try:
			active_speaker_container = self.driver.find_element(By.CLASS_NAME, 'speaker-active-container__wrap')
			video_frame = active_speaker_container.find_element(By.CLASS_NAME, 'speaker-active-container__video-frame')
			try:
				current_speaker_name = video_frame.find_element(By.CLASS_NAME, 'video-avatar__avatar-name').text
			except:
				current_speaker_name = video_frame.find_element(By.CLASS_NAME, 'video-avatar__avatar-img').get_attribute('alt')
			if not current_speaker_name in self.participants:
				self.log_participants()
			return current_speaker_name
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Did not find the current speaker in the meeting')
				return None
			else:
				print(f"An ERROR OCCURED: While Trying To get the current speaker in the Zoom Meeting, Retrying {get_attempts}.")
				return self.get_current_speaker(get_attempts)

	


class GoogleMeetBot(object):
	def __init__(self, driver, meeting_url, bot_name):
		self.driver = driver
		self.meeting_url = meeting_url
		self.bot_name = bot_name
		self.participant_number = 0
		self.participants = []
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
	
	def log_participants(self, get_attempts=0):
		"""Log participants' names"""
		try:
			participant_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-self-name='You']")
			for element in participant_elements:
				# Find the actual participant name within the element
				name_element = element.find_element(By.CLASS_NAME, 'dwSJ2e')
				self.participants.append(name_element.text)
			print(f"Searched for meeting participants: {self.participants}")
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Did not find meeting participants')
			else:
				print(f"An ERROR OCCURED: While Trying To get Google Meeting participants, Retrying {get_attempts}.")
				return self.log_participants(get_attempts)
	
	def get_current_speaker(self, get_attempts=0):
		"""Get participants' names"""
		try:
			if self.participant_number != len(self.participants):
				participant_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-self-name='You']")
				for element in participant_elements:
					# Find the actual participant name within the element
					name_element = element.find_element(By.CLASS_NAME, 'dwSJ2e')
					if not name_element.text in self.participants:
						self.participants.append(name_element.text)
				print(f"Searched for meeting participants: {self.participants}")
				return str(self.participants)
			else:
				return ""
		except Exception as e:
			# retry initialize 5 times
			if get_attempts >= 5:
				print(e)
				print('Did not find meeting participants')
			else:
				print(f"An ERROR OCCURED: While Trying To get Google Meet participants, Retrying {get_attempts}.")
				return self.get_current_speaker(get_attempts)
	
	

	
	




class MicrosoftTeamsBot(object):
    def __init__(self, driver, meeting_url, bot_name):
        self.driver = driver
        self.meeting_url = meeting_url
        self.bot_name = bot_name
        self.participants = []

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

    def log_participants(self, get_attempts=0):
        pass
    def get_current_speaker(self, get_attempts=0):
        return ""















