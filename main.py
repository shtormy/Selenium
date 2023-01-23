from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time
import getpass


my_user = getpass.getpass('Введите логин: ')
my_password = getpass.getpass('Введите пароль: ')

# Запускаем драйвер
s = Service('./chromedriver.exe')
chromeOptions = Options()
chromeOptions.add_argument('start_maximized')
driver = webdriver.Chrome(service=s, options=chromeOptions)
driver.get('https://account.mail.ru/login')
driver.implicitly_wait(25)

# Вводим логин
login = driver.find_element(By.NAME, 'username')
login.send_keys(my_user)

driver.find_element(By.XPATH, '//button[@data-test-id="next-button"]').click()

# Вводим пароль
psw = driver.find_element(By.NAME, 'password')
psw.send_keys(my_password)

driver.find_element(By.XPATH, '//button[@data-test-id="submit-button"]').click()

time.sleep(5)

# Заходим в папку Спам
spam_folder = driver.find_element(By.XPATH, '//a[@data-folder-link-id="950"]').get_attribute('href')
driver.get(spam_folder)

# Собираем ссылки
letters_spam = driver.find_element(By.CLASS_NAME, "letter-list__react")

letters_urls = set()
last_len = 0

while True:
    letters = letters_spam.find_elements(By.XPATH, '//div[@class="layout__content-column"]//a[@data-id]')
    letters_urls.update(letter.get_attribute("href") for letter in letters)
    if last_len == len(letters_urls):
        break

    last_len = len(letters_urls)

    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()
    time.sleep(1)

# Собираем данные
result_items = []

for _url in letters_urls:

    item = {}

    driver.get(_url)

    item["url"] = _url
    item["title"] = driver.find_element(By.XPATH, "//h2[contains(@class, 'thread-subject')]").text
    container = driver.find_element(By.XPATH, "//div[contains(@class, 'thread thread_fluid thread_rounded thread_compressed thread_direction-next')]")

    item["from"] = container.find_element(By.XPATH, "//span[@class = 'letter-contact letter-contact_pony-mode']").text
    item["date"] = container.find_element(By.XPATH, ".//div[@class='letter__date']").text
    item["body"] = container.find_element(By.XPATH, "//div[@class = 'letter-body']").text

    result_items.append(item)

driver.close()

# Записываем в БД
client = MongoClient('127.0.0.1', 27017)
db = client['emails_db']
emails_db = db.emails

for item in result_items:
    emails_db.update_one({'link': item['url']}, {'$set': item}, upsert=True)







# spam_links = []
# for i in driver.find_elements(By.XPATH, '//div[@class="layout__content-column"]//a[@data-uidl-id]'):
#     x = i.get_attribute('href')
#     spam_links.append(x)
# print(len(spam_links))

# actions = ActionChains(driver)
# actions.scroll_to_element(spam_links[-1])
# actions.perform()
# print()


# for links in len(spam_links):
#     driver.find_element(By.__init__(links)).click()

#     from_whom = letter.find_elements(By.XPATH, '//div[@class="letter__author"]/span').text
#     data_get = letter.find_elements(By.XPATH, '//div[@class="letter__date"]').text
#     top_letter = letter.find_elements(By.XPATH, '//span[@class="ll-sj__normal"]').text
#     text_letter = letter.find_elements(By.XPATH, '//span[@class="ll-sp__normal"]').text

