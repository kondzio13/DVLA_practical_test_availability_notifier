from selenium import webdriver
import os
import time
import requests
from datetime import date


def telegram_bot_sendtext(bot_message, bot_token, bot_chatID):

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


class DvlaChecker:

    def __init__(self, test_type, licence_number, postcode, centre_name, driver_path, lag, bot_token, bot_chatID, date):
        
        self.test_type = test_type
        self.licence_number = licence_number
        self.postcode = postcode
        self.centre_name = centre_name

        self.driver_path = driver_path
        self.lag = lag

        self.bot_token = bot_token
        self.bot_chatID = bot_chatID

        self.dates_free = '12345'
        self.date = date
        self.dates_free = ''
        self.times_checked = 0
        
        self.book_URL = 'https://driverpracticaltest.dvsa.gov.uk/application'

        while True:
            try:
                self.driver.close()
                self.times_checked += 1
            except:
                try:
                    self.driver = webdriver.Chrome(self.driver_path)
                    self.startBooking()
                    self.inputDetails()
                    time.sleep(60.0 * self.lag)
                except:
                    print('Failed to check free sessions')
                time.sleep(60.0 * self.lag)
    
    def startBooking(self):
        self.driver.get(self.book_URL)

    def inputDetails(self):
        time.sleep(1.0)
        self.driver.find_elements_by_id(self.test_type)[0].click()
        time.sleep(1.0)
        self.driver.find_elements_by_id('driving-licence')[0].send_keys(self.licence_number)
        self.driver.find_elements_by_id('special-needs-none')[0].click()
        time.sleep(1.0)
        self.driver.find_elements_by_id('driving-licence-submit')[0].click()
        time.sleep(1.0)
        self.driver.find_elements_by_id('test-choice-calendar')[0].send_keys(self.date)
        time.sleep(1.0)
        self.driver.find_elements_by_id('driving-licence-submit')[0].click()
        time.sleep(1.0)
        self.driver.find_elements_by_id('test-centres-input')[0].send_keys(self.postcode)
        time.sleep(1.0)
        self.driver.find_elements_by_id('test-centres-submit')[0].click()
        time.sleep(1.0)
        self.driver.find_elements_by_id(self.centre_name)[0].click()
        time.sleep(1.0)
        first_3_date_elements = self.driver.find_elements_by_class_name('BookingCalendar-date--bookable')[:3]
        dates_free = ''
        for element in first_3_date_elements:
            text = element.get_attribute('innerHTML')
            index_hr = text.find('href')
            date = text[index_hr+17:index_hr+22]
            date = date[-2:] + '/' + date[:2]
            if len(dates_free) != 0:
                dates_free = dates_free + ', ' + date
            else:
                dates_free = date

        if self.dates_free[:5] != dates_free[:5]:
            notification = ('Alert: ' + dates_free)
            response = telegram_bot_sendtext(notification, self.bot_token, self.bot_chatID)
            self.dates_free = dates_free
            print('Notification \'' + notification + '\' requested to be sent after check ' + str(self.times_checked) + ' with response:')
            print(response)
        else:
            print('No notification sent after check ' + str(self.times_checked))
        

if __name__ == '__main__':

    test_type = 'test-type-car'     # Enter the type of test to be monitored
    licence_number = ''             # Enter your driving licence number
    postcode = ''                   # Enter your postcode
    centre_num = 'centre-name-xxx'  # Enter center number to be monitored

    driver_path = 'chromedriver' # Path to chromedriver to be used
    check_every = 1                 # Specifies number of minutes between start of next check

    bot_token = '1136006997:AAFhgzyqymSs59z1DV7jf1j2dmiCM51CH7s' # Telegram bot token
    bot_chatID = '1297686015'                                    # Telegram bot chatID

    today = date.today()
    today = today.strftime("%d/%m/%Y")
    day = str(int(today[:2]) + 1)
    if len(day) == 1:
        day = '0' + day
    date = day + today[2:6] + today[-2:]

    dvla = DvlaChecker(test_type, licence_number, postcode, centre_num, driver_path, check_every, bot_token, bot_chatID, date)
