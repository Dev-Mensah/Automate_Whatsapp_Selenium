from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os

filePath = r"<<Path To file>>"
chromePath = "<<Chrome Path>>"
srcFolder = r"<<src Folder>>"
logFilePath = r"<<LogFile Path>>"


class Whatsapp:
    def __init__(self):
        self.driver = webdriver.Chrome(chromePath)

    'logs into whatsapp and wait until user has scanned qr code'
    def login(self):
        self.driver.get('https://web.whatsapp.com/')
        wait = WebDriverWait(self.driver, 0)
        while True:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "._2vDPL")))
                break
            except:
                pass
        print("** logged in **")
        time.sleep(3)

    # read a list of chatNames from the srcFolder
    # and search for the chatNames one after the other
    def search_chat(self):
        while True:
            with open(srcFolder, 'r') as f:
                paths = f.readlines()
            for path in paths:
                file_path = f"{filePath}\{path.strip()}.txt"
                search_box = self.driver.find_element('xpath', '//div[@contenteditable="true"][@data-tab="3"]')
                #clear fails sometimes when search box is already empty
                search_box.send_keys(path.strip())
                search_box.clear()
                search_box.send_keys(path.strip())
                search_box.send_keys(Keys.RETURN)
                wait = WebDriverWait(self.driver, 0)
                while True:
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "._5kRIK")))
                        break
                    except:
                        pass
                #check if that chat file has been created already in  <<filePath>>
                # keep scrolling to top for three minutes if file doesnt exist
                if os.path.isfile(file_path):
                    if os.path.getsize(file_path) > 0:
                        pass
                    else:
                        os.remove(file_path)
                else:
                    start_time = time.time()
                    end_time = start_time + (1 * 60)  # 1 minute in seconds
                    while time.time() < end_time:
                        self.driver.execute_script("arguments[0].scrollTo(0, 0);", self.driver.find_element(By.CSS_SELECTOR, "._5kRIK"))
                    time.sleep(5)      

                print (path.strip())
                print("** Chat Found **")
                time.sleep(5)
                self.print_messages(path.strip())

    def get_date_from_string(self, txtstr, formatstr):
        date_time_obj = datetime.strptime(txtstr, formatstr)
        return date_time_obj
       

    def read_last_date_from_file(self, file_path):
        with open(file_path, 'r') as file:
            last_line = file.readlines()[-1].strip().split("message time: ")[1]
            last_line_time = last_line.split(" message date: ")[0]
            last_line_date = last_line.split(" message date: ")[1]
            lastLine_dateTime = f"{last_line_time},{last_line_date}"
            return lastLine_dateTime 
        
    def format_last_date_from_file(self, file_path):
        last_date_str = self.read_last_date_from_file(file_path)
        format_string = "%I:%M %p, %d/%m/%Y"
        file_date_time = self.get_date_from_string(last_date_str, format_string)
        return file_date_time
    
    # write logs to a logfile int <<logFilePath>> every time a successful message is retrieved
    def write_to_log(self, count, chatName):
        today = datetime.today()
        with open(logFilePath, 'a') as logFile:
                logFile.write(f"{count} messages retrieved from {chatName} on {today} \n")
                time.sleep(2)

           
    # write messages to the file created
    def print_messages(self, file__Path):
        file_path = f"{filePath}\{file__Path}.txt"
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) > 0:
                # read last line from file if size > 0
                file_date_time = self.format_last_date_from_file(file_path)
                dateTimeStr = self.read_last_date_from_file(file_path)
                # find all messages in chat with date and time greater than last date in file
                messages = self.driver.find_elements(By.XPATH, f'//div[contains(@data-pre-plain-text, "{dateTimeStr}")]/following::div[contains(@class, "ItfyB _3nbHh")]')
                msgCount = len(messages)
                self.write_to_log(msgCount, file__Path)

                with open(file_path, 'a') as f:
                    for every_message in messages:
                        try:
                            message_sender = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split("]")[0]
                            message_date_time = message_sender.split("[")[1]
                            format_string = '%I:%M %p, %d/%m/%Y'
                            msg_date_time = self.get_date_from_string(message_date_time, format_string)

                            if (msg_date_time > file_date_time):
                                try:
                                    message_type = every_message.find_element(By.CSS_SELECTOR, ".HLjg0").get_attribute("data-testid")
                                    f.write(f"\nmessage Type: {message_type} \n")
                                    initial_sender = every_message.find_element('xpath', ".//div[@class='yKTUI _1JeGx']//span[1]").text
                                    f.write(f"Initial Sender: {initial_sender} \n")
                                    initial_message = every_message.find_element(By.CSS_SELECTOR, ".quoted-mention._11JPr").text
                                    f.write(f"initial message: {initial_message} \n")
                                except:
                                    ""
                                try:
                                    read_more = every_message.find_element(By.CSS_SELECTOR, ".o0rubyzf.le5p0ye3.ajgl1lbb.l7jjieqr.read-more-button")
                                    read_more.click()
                                except:
                                    ""
                                try:
                                    message_sender = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split("]")[1]
                                    f.write(f"\nmessage sender: {message_sender} \n")
                                    print(f"message sender: {message_sender} ")

                                    message_text = every_message.find_element(By.CSS_SELECTOR, "._11JPr.selectable-text.copyable-text").text
                                    f.write(f"message body: {message_text} \n")
                                    print(f"message body: {message_text} ")

                                    msg_time = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split(",")[0]
                                    message_time = msg_time.split("[")[1]
                                    f.write(f"message time: {message_time} ")
                                    print(f"message time: {message_time} ")

                                    msg_date = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split(",")[1]
                                    message_date = msg_date.split("]")[0]
                                    f.write(f"message date: {message_date} \n")
                                    print(f"message date: {message_date} ")
                                    f.flush()
                                    print("\n")
                                except:
                                    "error"
                            else:
                                print("There are no new messages to print")
                        except:
                            ""
            # if file exists but empty delete it
            else:
                os.remove(file_path)
        # create files which do not exist
        else:
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".ItfyB._3nbHh")
            with open(file_path, 'a') as f:
                for every_message in messages:
                    try:
                        message_type = every_message.find_element(By.CSS_SELECTOR, ".HLjg0").get_attribute("data-testid")
                        f.write(f"\nmessage Type: {message_type} \n")
                        initial_sender = every_message.find_element('xpath', ".//div[@class='yKTUI _1JeGx']//span[1]").text
                        f.write(f"Initial Sender: {initial_sender} \n")
                        initial_message = every_message.find_element(By.CSS_SELECTOR, ".quoted-mention._11JPr").text
                        f.write(f"initial message: {initial_message} \n")
                    except:
                        ""
                    try:
                        read_more = every_message.find_element(By.CSS_SELECTOR, ".o0rubyzf.le5p0ye3.ajgl1lbb.l7jjieqr.read-more-button")
                        read_more.click()
                    except:
                        ""
                    try:
                        message_sender = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split("]")[1]
                        f.write(f"\nmessage sender: {message_sender} \n")
                        print(f"message sender: {message_sender} ")

                        message_text = every_message.find_element(By.CSS_SELECTOR, "._11JPr.selectable-text.copyable-text").text
                        f.write(f"message body: {message_text} \n")
                        print(f"message body: {message_text} ")

                        msg_time = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split(",")[0]
                        message_time = msg_time.split("[")[1]
                        f.write(f"message time: {message_time} ")
                        print(f"message time: {message_time} ")

                        msg_date = every_message.find_element(By.CSS_SELECTOR, ".copyable-text").get_attribute("data-pre-plain-text").split(",")[1]
                        message_date = msg_date.split("]")[0]
                        f.write(f"message date: {message_date} \n")
                        print(f"message date: {message_date} ")

                        f.flush()
                        print("\n")
                    except:
                        "error"

            msgCount = len(messages)
            self.write_to_log(msgCount, file__Path)
            

    def run(self):
        self.login()
        self.search_chat()
Whatsapp().run()