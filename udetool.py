# fmt: off
import collections
import unidecode
import time
import sys
import shutil
import re
import pdb
import os.path
import os
import logging
import locale
import json
import chromedriver_autoinstaller
import art 
import argparse
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Firefox
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from os.path import abspath
from inspect import getmembers
from datetime import datetime, timedelta


def configure_firefox_driver_profile(dn, profile_folder_path):
    options = Options()
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.update_preferences()
    desired = DesiredCapabilities.FIREFOX
    service = Service(os.path.join(dn, "geckodriver-v0.30.0-win64.exe"))
    firefox = webdriver.Firefox(desired_capabilities=desired, service=service)
    return firefox


def configure_firefox_driver_no_profile(dn):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--private')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('referer=https://www.google.com/')
    options.add_argument('--disable-extensions')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-blink-featuresi=AutomationControlled')
    options.add_argument('--disable-blink-features')
    options.set_preference('excludeSwitches', 'enable-automation')
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("browser.privatebrowsing.autostart", True)
    service = Service(os.path.join(dn, "geckodriver-v0.30.0-win64.exe"))
    firefox = webdriver.Firefox(options=options, service=service)
    firefox.get('about:home')
    firefox.maximize_window()
    return firefox


def configure_chrome_driver_no_profile(dn):
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("ignore-certificate-errors")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("disable-infobars")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome = webdriver.Chrome(options=options, executable_path="ChromeDriver 98.0.4758.80.exe")
    return chrome


def uncollapse_exams(driver):
    try:
        elements = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.udi.udi-chevron-up')))
        while len(elements) > 0:    
            element = elements[0]    
            action = webdriver.ActionChains(driver)    
            action.move_to_element(element)    
            action.perform()    
            element.click()    
            elements = driver.find_elements(By.CSS_SELECTOR, 'span.udi.udi-chevron-up')
    except:
        print("An exception occurred")


def login_into_udemy(driver, email, password):
    driver.get("https://www.udemy.com")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.main-content-wrapper > div.ud-app-loader.ud-component--header-v6--header.udlite-header.ud-app-loaded > div.udlite-text-sm.header--header--3sK1h.header--flex-middle--2Xqjv > div:nth-child(8) > a > span'))).click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#email--1'))).send_keys(email)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id_password'))).send_keys(password)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#submit-id-submit'))).click()

def show_intro():
    banner = art.text2art("UDETOOL")
    print(banner)
    print("Starting...\n")


def show_intro():
    print("Opciones:\n")
    print("1. Preparar examen (ordenar, mostrar distribución y mostrar reactivos sin explicación.)")
    print("2. Transferir examen de una cuenta a otra.")
    print("2. Transferir examen de un conjunto de exámenes a otro.")
    print("3. Duplicar examen dentro de un mismo conjunto de exámenes.")



def prepare_exam(driver,):
dn = os.getcwd()
print("Opening selenium...")
chrome = configure_chrome_driver_no_profile(dn)
email = input("Input your udemy email:")
password = input("Input your udemy password:")
login_into_udemy(chrome, email, password)

exam_url = input("Input exam content url:") # Example https://www.udemy.com/instructor/course/4444014/manage/practice-tests   
chrome.get(exam_url)

# Remove Chat from pages
try:
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#webWidget')))
    driver.execute_script(""" var element = arguments[0]; element.parentNode.removeChild(element); """, element)
    print('Chat element deleted')
except:
    print('Chat element not found')

try:
    uncollapse_exams(driver)
except:
    print('Contents already colapsed')

 

exam_index = 0
exam_sections = chrome.find_elements(By.CSS_SELECTOR, "li[id*='practice-test']")
print("Number of elements detected {}".format(len(exam_sections)))

questions = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li > div')
print("Number of questions detected {} in exam {}".format(len(questions), str(exam_index)))


# Order questiosn to his category
print("Introduce las materias o categorías en el orden deseado:")
topics_order = {}
for i in range(9):    
    topic_info = []
    topic_info.append(input("Nombre de {} :".format(str(i))).upper())
    topic_info.append(int(input("Num de reactivos:")))
    topics_order[i] = topic_info

# execute order
#for question_index in range(0,len(questions)-1): 
for question_index in range(0,10): 
    exam_sections = chrome.find_elements(By.CSS_SELECTOR, "li[id*='practice-test']")
    questions = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li > div')
    # Open sender question    
    pencil_buttons = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li')
    pencil_button = pencil_buttons[question_index].find_element(By.CSS_SELECTOR, 'span.udi.udi-pencil')
    chrome.execute_script("arguments[0].click();", pencil_button)
    # Check topic
    topic_radios = WebDriverWait(chrome, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form > div:nth-child(4) > div > label > input[type=radio]")))
    knowledge_areas = chrome.find_elements(By.CSS_SELECTOR,"#knowledge-area")
    print("Number of topics {}".format(len(topic_radios)-1))
    current_topic = ""
    for index in range(len(topic_radios)):
        if topic_radios[index].is_selected() and knowledge_areas[index].get_attribute('value'):
            current_topic = knowledge_areas[index].get_attribute('value')
    print("Categoría actual: {}".format(current_topic))
    # Close question
    chrome.find_element_by_tag_name('html').send_keys(Keys.HOME) #Scrolls up to the top of the page   
    sender_close_question_button = chrome.find_element(By.CSS_SELECTOR,"button[data-purpose^='content-tab-close']")
    action = webdriver.ActionChains(chrome)
    action.move_to_element(sender_close_question_button)
    action.perform()
    sender_close_question_button.click()
    # Verrify if index question in correct range
    topics_order_values = topics_order.values()
    inferior_limit = 0
    superior_limit = 0
    correct_inferior_limit = 0
    correct_superior_limit = 0
    for element in topics_order_values:   
        superior_limit = inferior_limit + int(element[1])-1
        print("{}: {} ".format(element[0],element[1]))
        print("Limite inferior {}".format(inferior_limit))
        print("Limite superior {}".format(superior_limit))    
        if current_topic.upper() == element[0].upper():
            print("Etiquetado con categoria {}".format(element[0]))
            correct_inferior_limit = inferior_limit
            correct_superior_limit = superior_limit
            if question_index >= inferior_limit and question_index <= superior_limit:
                print("Esta en el rango correcto")
            else:
                print("No está en el rango correcto")
                # if is no in te correct category have to move to its inferior num  
                print("Moviendo {} a {}".format(str(question_index+1),str(correct_inferior_limit+1)))
                source_question_dragable = chrome.find_element(By.CSS_SELECTOR,"ul > li:nth-child("+str(question_index+1)+") > div > div:nth-child(5) > div > span.udi.udi-bars")
                target_question_dragable = chrome.find_element(By.CSS_SELECTOR,"ul > li:nth-child("+str(correct_inferior_limit+1)+") > div")
                ActionChains(chrome).drag_and_drop(source_question_dragable, target_question_dragable).perform()  
        inferior_limit = superior_limit + 1
    

question_index = 1   
correct_inferior_limit = 10





# Print ranges topics
inferior_limit = 0
superior_limit = 0
for element in topics_order_values:   
        superior_limit = inferior_limit + int(element[1])-1
        print("{}: {}".format(element[0],element[1]))
        print("Limite inferior {}".format(inferior_limit))
        print("Limite superior {}".format(superior_limit)) 
        inferior_limit = superior_limit + 1    

exam_knowledge_areas = []
questions_no_explain = []
for question_index in range(0,len(questions)-1): 
    # Open sender question    
    pencil_buttons = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li')
    pencil_button = pencil_buttons[question_index].find_element(By.CSS_SELECTOR, 'span.udi.udi-pencil')
    driver.execute_script("arguments[0].click();", pencil_button)
    # Check topic
    topic_radios = WebDriverWait(chrome, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form > div:nth-child(4) > div > label > input[type=radio]")))
    knowledge_areas = chrome.find_elements_by_css_selector("#knowledge-area")
    print("Number of topics {}".format(len(topic_radios)))
    for index in range(len(topic_radios)):
        if topic_radios[index].is_selected() and knowledge_areas[index].get_attribute('value'):
            exam_knowledge_areas.append(knowledge_areas[index].get_attribute('value'))
    # Check explanaition If is empty only have one
    question_explainantion = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form > div:nth-child(3) > div > div.rt-editor.rt-editor--wysiwyg-mode > div")))
    if len(question_explainantion.find_elements(By.TAG_NAME,'p')) == 1:
        questions_no_explain.append(question_index)
    # Close question
    chrome.find_element_by_tag_name('html').send_keys(Keys.HOME) #Scrolls up to the top of the page   
    sender_close_question_button = chrome.find_element(By.CSS_SELECTOR,"button[data-purpose^='content-tab-close']")
    action = webdriver.ActionChains(chrome)
    action.move_to_element(sender_close_question_button)
    action.perform()
    sender_close_question_button.click()
# Pritn results
counter=collections.Counter(exam_knowledge_areas)
for line in counter:
    print("{}:\t{}".format(line,str(counter[line])))   

def show_exam_distribution(driver):
    exam_url = input("Input exam content url:")    
    get_exam_distribution(driver,exam_url)



# REce ie exams URL and an recdier URL exames copy one name examen in other name
def transfer_all_exams_pack(user1, password1, content1, user2, password2, content2):
    # Open and configure drivers
    dn = os.getcwd()
    chrome1 = configure_chrome_driver_no_profile(dn) # Sender
    chrome2 = configure_chrome_driver_no_profile(dn) # Receiver
    login_into_udemy(chrome1, user1, password1)
    login_into_udemy(chrome2, user2, password2)
    chrome1.get(content1)
    chrome2.get(content2)
    
    # Remove Chat from pages
    try:
        element = WebDriverWait(chrome1, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#webWidget')))
        chrome1.execute_script(""" var element = arguments[0]; element.parentNode.removeChild(element); """, element)
    except:
        print('Chat menu not')
    finally:
        print("No chat")
    
    try:
        element = WebDriverWait(chrome2, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#webWidget')))
        chrome2.execute_script(""" var element = arguments[0]; element.parentNode.removeChild(element); """,element) 
    except:
        print('Chat menu not')
    finally:
        print("No chat")
    
    # If collapsed
    try:
        uncollapse_exams(chrome1)
    except:
        print('Already colapsed')
    
    try:
        uncollapse_exams(chrome2)
    except:
        print('Already colapsed')
    
    # In receiver if exams number are note zero notice
    exam_sections_edit_buttons = chrome2.find_elements(By.CSS_SELECTOR, "span.udi.udi-pencil")
    if len(exam_sections_edit_buttons) > 0:
        print("There is exams in receiver, delete it or create new item to receive all the exams!")
        #exit()
    
    # For each exam
    quiz_edit_buttons = chrome1.find_elements(By.CSS_SELECTOR,"button[data-purpose^='quiz-edit-btn']")
    exam_index = 1
    
    # Click exam edit button    
    current_exam_section_edit_button = quiz_edit_buttons[exam_index]
    action = webdriver.ActionChains(chrome1)
    action.move_to_element(current_exam_section_edit_button).perform()
    current_exam_section_edit_button.click()
    
    # Get all information of examn properties
    current_exam_title = chrome1.find_element(
        By.CSS_SELECTOR, "#title").get_attribute('value')
    current_exam_description = chrome1.find_element(
        By.CSS_SELECTOR, 'div > div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > form > div.df.db-sm > div.fx.mt20.ml15.mr15 > div:nth-child(2) > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
    current_exam_description_html = "'" + \
        current_exam_description.get_attribute('outerHTML')+"'"
    current_exam_duration = chrome1.find_element(
        By.CSS_SELECTOR, "#duration").get_attribute('value')
    current_exam_approving_grade_ = chrome1.find_element(
        By.CSS_SELECTOR, "#pass-percent").get_attribute('value')
    cancel_button = WebDriverWait(chrome1, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'div > div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > form > div.df.db-sm > div.fx.mt20.ml15.mr15 > div.text-right > button.btn.btn-sm.btn-tertiary')))
    chrome1.execute_script("arguments[0].click();", cancel_button)
    
    # Add new exam receiver
    add_item_button = chrome2.find_element(
        By.CSS_SELECTOR, '#chapter0 > div > div > div > button')
    action = webdriver.ActionChains(chrome2)
    action.move_to_element(add_item_button)
    action.perform()
    add_item_button.click()
    add_exam_button = chrome2.find_element(
        By.CSS_SELECTOR, '#chapter0 > div > div > div:nth-child(2) > div > div > button > span')
    action = webdriver.ActionChains(chrome2)
    action.move_to_element(add_exam_button)
    action.perform()
    add_exam_button.click()
    
    # Put the information
    receiver_exam_title = chrome2.find_element(By.CSS_SELECTOR, "#title")
    receiver_exam_title.send_keys(current_exam_title)
    receiver_exam_description = chrome2.find_element(
        By.CSS_SELECTOR, 'form > div.df.db-sm > div.fx.mt20.ml15.mr15 > div:nth-child(2) > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
    chrome2.execute_script(
        "arguments[0].innerHTML =" + current_exam_description_html, receiver_exam_description)
    receiver_exam_duration = chrome2.find_element(By.CSS_SELECTOR, "#duration")
    receiver_exam_duration.send_keys(current_exam_duration)
    receiver_exam_approving_grade_ = chrome2.find_element(
        By.CSS_SELECTOR, "#pass-percent")
    receiver_exam_approving_grade_.send_keys(current_exam_approving_grade_)
    save_button = WebDriverWait(chrome2, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'div > div > div:nth-child(2) > div > form > div.df.db-sm > div.fx.mt20.ml15.mr15 > div.text-right > button.ml5.btn.btn-sm.btn-secondary')))
    chrome2.execute_script("arguments[0].click();", save_button) 
    
    
    
    exam_sections = chrome1.find_elements(By.CSS_SELECTOR, "li[id*='practice-test']")
    questions = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li > div')
    
    # Open the exam sender
    chrome1.execute_script("arguments[0].click();", WebDriverWait(chrome1, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.udi.udi-chevron-down')))[exam_index])
    
    # For each question
    sender_question_index = 0
    for k in range(0,len(questions)-1): 
        # Open sender question    
        pencil_buttons = exam_sections[exam_index].find_elements(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--edit-content--HLXOq > div > div.quiz-editor--assessment-list--AusWI > ul > li')
        pencil_button = pencil_buttons[sender_question_index].find_element(By.CSS_SELECTOR, 'span.udi.udi-pencil')
        chrome1.execute_script("arguments[0].click();", pencil_button)
        
        # Open de receiver exam and ready for the questions new question
        if exam_index > 0:
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.fx > div > div:nth-child(2) > button')))[0])
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li:nth-child(1) > a > div > small')))[0])
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.content-type-selector--option__icon--305N_.content-type-selector--option__icon--before--3d1xd.udi.udi-file-text-o')))[0])
        else: 
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.fx > div > div:nth-child(2) > button')))[0])
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li:nth-child(1) > a > div > small')))[0])
            chrome2.execute_script("arguments[0].click();", WebDriverWait(chrome2, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.content-type-selector--option__icon--305N_.content-type-selector--option__icon--before--3d1xd.udi.udi-file-text-o')))[0])
        
        # Select editor sender and copy content 
        WebDriverWait(chrome1, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq')))
        sender_editor_items = WebDriverWait(chrome1, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq')))[exam_index]
        WebDriverWait(sender_editor_items, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.rt-editor.rt-editor--wysiwyg-mode > div')))
        sender_editor_item = sender_editor_items.find_element(By.CSS_SELECTOR, 'div.rt-editor.rt-editor--wysiwyg-mode > div')
        htmlelement= chrome2.find_element_by_tag_name('html')
        htmlelement.send_keys(Keys.HOME) #Scrolls up to the top of the page
        action = webdriver.ActionChains(chrome1)
        action.move_to_element(sender_editor_item).perform()
        sender_editor_item.click()
        action = webdriver.ActionChains(chrome1).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        action = webdriver.ActionChains(chrome1).key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL).perform()
        
        # Select editor receiver 
        WebDriverWait(chrome2, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-purpose^='wysiwyg-mode']")))
        receiver_editor_item = WebDriverWait(chrome2, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-purpose^='wysiwyg-mode']")))[exam_index]
        htmlelement= chrome2.find_element_by_tag_name('html')
        htmlelement.send_keys(Keys.HOME) #Scrolls up to the top of the page
        action = webdriver.ActionChains(chrome2)
        action.move_to_element(receiver_editor_item).perform()
        receiver_editor_item.click()
        action = webdriver.ActionChains(chrome2).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        
        # Transfer items
        sender_answer1 = chrome1.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(2) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        receiver_answer1 = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(2) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        sender_answer1_html = "'"+sender_answer1.get_attribute('outerHTML')+"'"
        chrome2.execute_script("arguments[0].innerHTML =" + sender_answer1_html, receiver_answer1)
        sender_answer2 = chrome1.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(3) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        receiver_answer2 = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(3) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        sender_answer2_html = "'"+sender_answer2.get_attribute('outerHTML')+"'"
        chrome2.execute_script("arguments[0].innerHTML =" + sender_answer2_html, receiver_answer2)
        sender_answer3 = chrome1.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(4) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        receiver_answer3 = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(4) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        sender_answer3_html = "'"+sender_answer3.get_attribute('outerHTML')+"'"
        chrome2.execute_script("arguments[0].innerHTML =" + sender_answer3_html, receiver_answer3)
        
        # Add answer space for 4 answers in receiver
        receiver_answer3 = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(4) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        action = webdriver.ActionChains(chrome2)
        action.move_to_element(receiver_answer3)
        action.perform()
        receiver_answer3.click()
        
        # Transfer fourth answer
        sender_answer4 = chrome1.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(5) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        receiver_answer4 = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(5) > div.fx > div > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        sender_answer4_html = "'"+sender_answer4.get_attribute('outerHTML')+"'"
        chrome2.execute_script("arguments[0].innerHTML =" + sender_answer4_html, receiver_answer4)
        
        # Transfer explaination
        sender_explaination = chrome1.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(3) > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        receiver_explaination = chrome2.find_element(By.CSS_SELECTOR, 'div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(3) > div > div.rt-editor.rt-editor--wysiwyg-mode > div')
        sender_explaination_html = "'"+sender_explaination.get_attribute('outerHTML')+"'"    
        chrome2.execute_script("arguments[0].innerHTML =" + sender_explaination_html, receiver_explaination)
        
        # Select correct answer radio button
        answer_radio_input1 = chrome1.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(2) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > input[type=radio]")
        answer_radio1 = chrome2.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(2) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > span")
        if answer_radio_input1.is_selected():
            chrome2.execute_script("arguments[0].click();", answer_radio1)
        
        answer_radio_input2 = chrome1.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(3) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > input[type=radio]")
        answer_radio2 = chrome2.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(3) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > span")
        if answer_radio_input2.is_selected():
            chrome2.execute_script("arguments[0].click();", answer_radio2)
        
        answer_radio_input3 = chrome1.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(4) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > input[type=radio]")
        answer_radio3 = chrome2.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(4) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > span")
        if answer_radio_input3.is_selected():
            chrome2.execute_script("arguments[0].click();", answer_radio3)
        
        answer_radio_input4 = chrome1.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(5) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > input[type=radio]")
        answer_radio4 = chrome2.find_element_by_css_selector("div.quiz-editor--quiz-editor--2RKDC.default-item-editor--item-editor--3GhNq > div.default-item-editor--add-content--1wZ-X > div > div.pl10.pr10.pb10 > div > form > div:nth-child(2) > div:nth-child(5) > div.multiple-choice-assessment-editor--answer-option__toggle-wrapper--ffwMX > label > span")
        if answer_radio_input4.is_selected():
            chrome2.execute_script("arguments[0].click();", answer_radio4)
        
        # Get the number of areas in receiver if doesnt have same insert suposeed empty exp s9 first 0  and 11 empty 
        sender_area_inputs = chrome1.find_elements(By.CSS_SELECTOR, "#knowledge-area")
        receiver_area_inputs = chrome2.find_elements(By.CSS_SELECTOR, "#knowledge-area")
        
        # Add areas if necesary
        if len(sender_area_inputs) > len(receiver_area_inputs):
            for i in range(1,len(sender_area_inputs)-1):
                print(i)
                sender_area_text = "'"+sender_area_inputs[i].get_attribute('value')+"'"
                # Fill the new area in receiver
                receiver_area_inputs = chrome2.find_elements(By.CSS_SELECTOR, "#knowledge-area")
                receiver_area_input = chrome2.find_elements(By.CSS_SELECTOR, "#knowledge-area")[len(receiver_area_inputs)-1]
                receiver_area_input.clear()
                receiver_area_input.send_keys(sender_area_text.replace("'",""))
                add_area_button = chrome2.find_element(By.CSS_SELECTOR,"form > div:nth-child(4) > span > span > button")
                htmlelement= chrome2.find_element_by_tag_name('html')
                htmlelement.send_keys(Keys.DOWN) #Scrolls up to the top of the page 
                action = webdriver.ActionChains(chrome2)
                action.move_to_element(add_area_button).perform()
                add_area_button.click()        
        
        # Select radio button area with span not radio
        selected = 1
        sender_area_inputs = chrome1.find_elements(By.CSS_SELECTOR, "form > div:nth-child(4) > div > label > input[type=radio]")
        for i in range(1,len(sender_area_inputs)):
            if  sender_area_inputs[i].is_selected():
                selected = i
                print("{} index is selected".format(i))
        
        receiver_area_radios = chrome2.find_elements(By.CSS_SELECTOR, "form > div:nth-child(4) > div > label > span")
        action = webdriver.ActionChains(chrome2)
        action.move_to_element(receiver_area_radios[selected])
        action.perform()
        receiver_area_radios[selected].click()
        
        # Save the exam
        htmlelement= chrome2.find_element_by_tag_name('html')
        htmlelement.send_keys(Keys.HOME) #Scrolls up to the top of the page  
        save_exam_button = chrome2.find_element(By.CSS_SELECTOR,"form > div.text-right > button")
        action = webdriver.ActionChains(chrome2)
        action.move_to_element(save_exam_button)
        action.perform()
        save_exam_button.click()
        
        # Close sender question 
        htmlelement.send_keys(Keys.HOME) #Scrolls up to the top of the page   
        sender_close_question_button = chrome1.find_element(By.CSS_SELECTOR,"button[data-purpose^='content-tab-close']")
        action = webdriver.ActionChains(chrome1)
        action.move_to_element(sender_close_question_button)
        action.perform()
        sender_close_question_button.click()
        
        # Next question
        sender_question_index = sender_question_index +1
        time.sleep(3)
    
    # Close current exams to prepare next ones
    htmlelement= chrome2.find_element_by_tag_name('html')
    htmlelement.send_keys(Keys.HOME) #Scrolls up to the top of the page 
    
    # Close sender exam
    sender_close_exam_button = chrome1.find_element(By.CSS_SELECTOR,"button[data-purpose^='quiz-collapse-btn']")
    action = webdriver.ActionChains(chrome1)
    action.move_to_element(sender_close_exam_button)
    action.perform()
    sender_close_exam_button.click()
    
    # Close receiver exam
    receiver_close_exam_button = chrome2.find_element(By.CSS_SELECTOR,"button[data-purpose^='quiz-collapse-btn']")
    action = webdriver.ActionChains(chrome2)
    action.move_to_element(receiver_close_exam_button)
    action.perform()
    receiver_close_exam_button.click()
    exam_index = exam_index +1
    

def main():
    # Open and configure drivers
    show_intro()
    show_menu()
    selection = input()



dn = os.getcwd()
chrome = configure_chrome_driver_no_profile(dn)




email = input("Input your udemy email:")
password = input("Input your udemy password:")
login_into_udemy(chrome, email, password)
show_exam_distribution(chrome)
    

if __name__ == "__main__":
    main()
