import os
import sys
import logging
import threading
import time
import queue  # For thread-safe communication between threads
import subprocess
import soundfile as sf
import shlex
import boto3
import schedule
import traceback 
import csv
import json
import numpy as np
import sys
from urllib.parse import urlparse
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from backend import Browser, ZoomBot, GoogleMeetBot, MicrosoftTeamsBot
from javascript_code import JS_GoogleMeetBot, JS_MicrosoftTeamsBot, JS_ZoomBot

logging.basicConfig() 
logging.getLogger().setLevel(logging.INFO) 
valid_audio_extensions = ['.mp3', '.wav', '.flac', '.ogg'] # List of valid audio file extensions
driver = None

####### ----   REGION - S3 and Code Execution ----   ####### 


def send_recording_to_S3(recording_file_path, retry_attempts=0):
    retry_attempts+=1
    # Upload the recording file to the S3 bucket
    try:
        if not os.path.exists(recording_file_path):
            print(f"Warning: send_recording_to_S3: Path: {recording_file_path} does not exist")
            return None
        user_id = os.getenv("USER_ID")
        meeting_id = os.getenv("MEETING_ID") 
        time_stamp = str(time.strftime("%Y-%m-%d-%H-%M-%S"))
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        object_name = f"{user_id}+{meeting_id}+{time_stamp}"
        bucket_name = os.getenv("AWS_BUCKET_NAME")
        # Rename the file
        file_name, extension = os.path.splitext(recording_file_path)
        object_name = object_name + extension
        # Initialize S3 client
        if (len(aws_access_key_id) > 1) or (len(aws_secret_access_key) > 1):
            boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        else:
            s3_client = boto3.client('s3')
            
        if object_name is None:
            object_name = file_name + str(time_stamp)

        response = s3_client.upload_file(
            recording_file_path, 
            bucket_name, 
            object_name            
        )
        print(f"File {file_name} uploaded successfully to {bucket_name}/{object_name}")
        return response
    except FileNotFoundError:
        traceback.print_exc()
        print("send_recording_to_S3: Error, The file was not found")
        return None
    except NoCredentialsError:
        traceback.print_exc()
        print("send_recording_to_S3: Error, Credentials not available")
        return None
    except PartialCredentialsError:
        traceback.print_exc()
        print("send_recording_to_S3: Error, Incomplete credentials provided")
        return None
    except Exception as e:
        # retry initialize 5 times
        if retry_attempts >= 5:
            traceback.print_exc()
            print(f"send_recording_to_S3: Error uploading file: {e}")
            return None
        else:
            print(f"An ERROR OCCURED: While Trying To send_recording_to_S3, Retrying {retry_attempts}.")
            return send_recording_to_S3(recording_file_path, retry_attempts)


def stop_code_execution(driver=None):
    try:
        if driver != None:
            driver.close()
    except:
        traceback.print_exc()
        pass
    recording_file_path = os.path.join(os.getcwd(), f"recording.wav")
    send_recording_to_S3(recording_file_path)
    # Print a message before stopping execution
    print("Stopping all code execution and terminating the process.")
    # Flush stdout and stderr
    sys.stdout.flush()
    sys.stderr.flush()
    # terminates the code abruptly, Docker releases the associated resources like memory.
    os._exit(0)
    # sys.exit("Main program exiting.")
    # sys.exit() is more graceful than os._exit() , but it needs to be called on each thread


####### ----   REGION - Selenium - Automatically Join Meetings   ----   ####### 

# all URLs passed to the WebDriver must explicitly include the scheme (http:// or https://)
# Web browsers address bar can automatically append the scheme but the WebDriver requires a complete URL
def ensure_url_scheme(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url

def start_zoom_bot(start_audio_record_event, meeting_url, bot_name):
    stop_incoming_video = False
    # Initialize Classes and web driver
    browser = Browser()
    global driver
    driver = browser.initialize_browser()
    # convert the Zoom meeting_url so it opens with zoom website client. 
    base_url, query_string = meeting_url.split('?') # Split the meeting_url 
    # Replace '/j/' with '/wc/' in the base_url and append '/join'
    if '/j/' in base_url or '/wc/' in base_url:
        new_base_url = base_url.replace('/j/', '/wc/') + '/join'
        meeting_url = new_base_url + '?' + query_string # combine back the meeting_url
    else:
        print("zoom meeting link is wrong: Failed to process the zoom meeting link.")
        driver.quit()
        return
    # Calling the automation methods
    meeting_url = ensure_url_scheme(meeting_url)
    zoom_bot = ZoomBot(driver , bot_name, meeting_url, stop_incoming_video)
    zoom_bot.join_meeting()
    start_audio_record_event.set() # Set the audio record event
    # Run the javascript code, has an implict infinite loop
    javascript_object = JS_ZoomBot()
    driver.execute_script(javascript_object.js_code) # Continously Execute the JavaScript code


def start_meet_bot(start_audio_record_event, meeting_url, bot_name):
    # Initialize Classes and web driver
    browser = Browser()
    global driver
    driver = browser.initialize_browser()
    meeting_url = ensure_url_scheme(meeting_url)
    meet_bot = GoogleMeetBot(driver, meeting_url, bot_name)
    # Calling the automation methods
    meet_bot.join_meeting()
    start_audio_record_event.set() # Set the audio record event
    # Run the javascript code, has an implict infinite loop
    javascript_object = JS_GoogleMeetBot()
    driver.execute_script(javascript_object.js_code) # Continously Execute the JavaScript code


def start_teams_bot(start_audio_record_event, meeting_url, bot_name):
    # Initialize Classes and web driver
    browser = Browser()
    global driver
    driver = browser.initialize_browser()
    meeting_url = ensure_url_scheme(meeting_url)
    team_bot = MicrosoftTeamsBot(driver, meeting_url, bot_name)
    # Calling the automation methods
    team_bot.join_meeting()
    start_audio_record_event.set() # Set the audio record event
    # Run the javascript code, has an implict infinite loop
    javascript_object = JS_MicrosoftTeamsBot()
    driver.execute_script(javascript_object.js_code) # Continously Execute the JavaScript code


def start_bot(start_audio_record_event, retry_attempts=0):
    retry_attempts += 1
    try:
        bot_name = os.getenv("BOT_NAME")
        meeting_url = os.getenv("MEETING_LINK")
        # Parse url
        parsed_url = urlparse(meeting_url) # break the url into its components
        if ('zoom.us' in parsed_url.netloc) or ('zoom.us/j/' in meeting_url):
            start_zoom_bot(start_audio_record_event, meeting_url, bot_name)
        elif 'meet.google.com' in meeting_url:
            start_meet_bot(start_audio_record_event, meeting_url, bot_name)
        elif 'teams.microsoft.com' in meeting_url:
            start_teams_bot(start_audio_record_event, meeting_url, bot_name)
        else:
            print("This is an invalid link, Check again!, it's not a Zoom, Google Meet or Microsoft Teams link.")
            stop_code_execution(driver)
        # Flush stdout and stderr
        sys.stdout.flush()
        sys.stderr.flush()
        print("start_bot finished successfully")
    except Exception as e:
        # retry initialize 5 times
        if retry_attempts >= 5:
            print(f"CRITICAL: An ERROR OCCURED: at start_bot: {e}")
            traceback.print_exc()
            stop_code_execution(driver)
        else:
            print(f"An ERROR OCCURED: at start_bot, Retrying {retry_attempts}.")
            return start_bot(start_audio_record_event, retry_attempts)


####### ----   REGION - Meeting MetaData Handling  ----   #######

def get_meta_data(attempts=0):
        """ Execute Javascript code to Retrieve the current meta_data from localStorage"""
        attempts += 1
        meta_data = None
        try:
            if driver is None:
                return None
            meta_data = driver.execute_script("return localStorage.getItem('audioData');")
            # time,allAttendees,activeMike,changeInVoice,currentAudioChunk
            if meta_data is None:
                if attempts >= 5: # retry 5 times
                    print("Warning: Failed To Get Javascript 'audioData' used by metadata")
                    return None
                else:
                    return get_meta_data(attempts)
            meta_data = json.loads(meta_data) # Convert JSON string to Python list
            print(f"meta_data: type: {type(meta_data)} len: {len(meta_data)}")
            return meta_data
        except Exception as e:
            if attempts >= 5: # retry 5 times
                print(f"Error: While Trying To Get Javascript 'audioData' used by metadata: {e}")
                return None
            else:
                return get_meta_data(attempts)

def write_metadata_to_csv(meta_data):
    csv_file_path = "metadata.csv"
    print(f"meta_data: {meta_data}")
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)     
        # Write headers if the file is empty
        if os.stat(csv_file_path).st_size == 0:
            writer.writerow(['start', 'end', 'meta_data'])
        start_time = meta_data[0]
        end_time = meta_data[1]
        writer.writerow([start_time, end_time, meta_data[2]])



####### ----   REGION - Audio Recording and Writing  ----   #######


def record_audio(audio_queue, start_audio_record_event, retry_attempts=0):
    retry_attempts += 1
    try:
        print("starting virtual audio devices")
        # find audio source for specified browser
        subprocess.check_output(
            "sudo rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse", shell=True
        )
        subprocess.check_output(
            "sudo pulseaudio -D --verbose --exit-idle-time=-1 --system --disallow-exit  >> /dev/null 2>&1",
            shell=True,
        )
        subprocess.check_output(
            'sudo pactl load-module module-null-sink sink_name=DummyOutput sink_properties=device.description="Virtual_Dummy_Output"',
            shell=True,
        )
        subprocess.check_output(
            'sudo pactl load-module module-null-sink sink_name=MicOutput sink_properties=device.description="Virtual_Microphone_Output"',
            shell=True,
        )
        subprocess.check_output(
            "sudo pactl set-default-source MicOutput.monitor", shell=True
        )
        subprocess.check_output("sudo pactl set-default-sink MicOutput", shell=True)
        subprocess.check_output(
            "sudo pactl load-module module-virtual-source source_name=VirtualMic",
            shell=True,
        )
        print(f"Starting Audio Recording From Virtual Speakers as a way to listen to the meeting")
        chunk_sec = 5  # Duration of each recorded chunk in seconds
        record_command = f"ffmpeg -y -f pulse -i default -t {chunk_sec} -c:a pcm_s16le -ar 44100 -ac 2 -"
        args = shlex.split(record_command)
        start_audio_record_event.wait() # Wait until the event is set
        while True:
            # Execute ffmpeg command
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                audio_queue.put(chunk)
                print(f"chunk: len:{len(chunk)} type:{len(chunk)}")  # Debugging line
            process.wait() # Wait for the process to terminate
    except Exception as e:
        # retry initialize 5 times
        if retry_attempts >= 5:
            print(f"CRITICAL: An ERROR OCCURED: While Trying To record audio: {e}")
            traceback.print_exc()
            stop_code_execution(driver)
        else:
            print(f"An ERROR OCCURED: While Trying To record audio, Retrying {retry_attempts}.")
            return record_audio(audio_queue, start_audio_record_event, retry_attempts)
        

def write_audio_periodically(audio_queue, file_use_permission_queue, start_audio_record_event, retry_attempts=0):
    retry_attempts += 1
    try:
        stop_after_time = os.getenv("CODE_EXECUTION_TIME_LIMIT")
        stop_after_time = int(stop_after_time)
        speaker_sample_rate = 41000
        recording_file_path = os.path.join(os.getcwd(), f"recording.wav")
        write_interval = 10
        start_audio_record_event.wait() # Wait until the event is set
        # Regardless of outcome, after time_limit in hours, stop all code execution.
        schedule.every(stop_after_time).hours.do(stop_code_execution, driver)
        start_time = time.time()
        while True:
            time.sleep(write_interval)
            # Flush stdout and stderr
            sys.stdout.flush()
            sys.stderr.flush()
            data_list = []
            schedule.run_pending()
            while not audio_queue.empty():
                data_list.append(audio_queue.get())
            if data_list:
                all_data = np.concatenate(data_list, axis=0)
            else:
                continue
            while True:
                if file_use_permission_queue.empty():
                    file_use_permission_queue.put(True)
                    break
            try:
                meta_data = get_meta_data()
                if meta_data is None:
                    meta_data = "'Empty'"
                else:
                    # [time,allAttendees,activeMike,changeInVoice,currentAudioChunk]
                    meta_data = f"'Speakers:{meta_data[3]},ActiveMic:{meta_data[2]},AllParticipants:{meta_data[1]}'"
                end_time = time.time()
                write_metadata_to_csv([start_time, end_time, meta_data])
                start_time = end_time
                try:
                    meeting_is_ongoing = driver.execute_script("return localStorage.getItem('audioLooping');")
                    if meeting_is_ongoing is False:
                        print("Hurray, the Meeting has ended.")
                        stop_code_execution(driver) # allows all threads to end
                except:
                    pass
                if os.path.exists(recording_file_path):
                    with sf.SoundFile(recording_file_path, mode='r+',) as file:
                        file.seek(0, sf.SEEK_END)
                        file.write(all_data[:, 0])
                else:
                    sf.write(file=recording_file_path, data=all_data[:, 0], samplerate=speaker_sample_rate)
            except FileNotFoundError:
                try:
                    sf.write(file=recording_file_path, data=all_data[:, 0], samplerate=speaker_sample_rate)
                except Exception as e:
                    traceback.print_exc()
                    print(f"WARNING: Couldn't write audio to file after FileNotFoundError: {e}")
            except Exception as e:
                traceback.print_exc()
                print(f"WARNING: Couldn't write audio to file: {e}")
            file_use_permission_queue.get() #empty the queue
    except Exception as e:
        # retry initialize 5 times
        if retry_attempts >= 5:
            print(f"CRITICAL: An ERROR OCCURED: While Trying To write audio to file: {e}")
            traceback.print_exc()
            stop_code_execution(driver)
        else:
            print(f"An ERROR OCCURED: While Trying To write audio to file, Retrying {retry_attempts}.")
            return write_audio_periodically(audio_queue, file_use_permission_queue, start_audio_record_event, retry_attempts)


if __name__ == '__main__':
    # Create the memory safe variables for audio recording and processing
    audio_queue = queue.Queue()
    file_use_permission_queue = queue.Queue()
    start_audio_record_event = threading.Event()

    # Start audio recording in a separate thread
    record_thread = threading.Thread(target=record_audio, args=(audio_queue, start_audio_record_event))
    record_thread.daemon = True
    record_thread.start()

    # Start periodic writing in a separate thread
    writing_thread = threading.Thread(target=write_audio_periodically, args=(audio_queue, file_use_permission_queue, start_audio_record_event))
    writing_thread.daemon = True
    writing_thread.start()
    
    # Start selenium in main thread
    selenium_thread = threading.Thread(target=start_bot, args=(start_audio_record_event, 0))
    selenium_thread.daemon = True
    selenium_thread.start()

    while True:
        # Get a list of currently alive threads
        threads = threading.enumerate()
        num_threads = len(threads) - 1  # Exclude the main thread
        # Print the number of active threads (excluding the main thread)
        print(f"Number of active threads (excluding main): {num_threads}")
        if num_threads < 1:
            print("Threads ended, Ending the main thread")
            break
        time.sleep(10)  # Check every 10 seconds
