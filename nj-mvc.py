# based on https://github.com/AbhilashMuthyala/python-njmvc-appoinment
# last updated 12/31/2021

import urllib.request
import re
from bs4 import BeautifulSoup
import datetime as dt
import os
import time

# see https://github.com/tangbao/NJ-MVC-Appointment-Helper/blob/master/location_list.md
dmv_codes = ['270', '274', '282']
dmv_names = ['Camden', 'South Plainfield', 'North Bergen']
# inclusive
desired_date = [dt.date(2022, 1, 3), dt.date(2022, 1, 6)]
desired_time = [dt.time(10, 0), dt.time(18, 0)]
t_sleep = 4
# this is for non-cdl knowledge test
url_base = 'https://telegov.njportal.com/njmvc/AppointmentWizard/19/'

# PLEASE REVIEW THE VARIABLES ABOVE

# just for debugging
# desired_date = [dt.date(2022, 1, 3), dt.date(2023, 1, 6)]
# dmv_codes = ['267', '270', '282']
# dmv_names = ['Bakers Basin', 'Camden', 'North Bergen']

n_dmv = len(dmv_codes)
assert len(dmv_names) == n_dmv

while True:
    for i_dmv in range(n_dmv):
        try:
            url = url_base + dmv_codes[i_dmv]
            response = urllib.request.urlopen(url)
            page_html = response.read()
            soup = BeautifulSoup(page_html, 'lxml')

            if soup.find('div', attrs={'class': 'alert-danger'}) is not None:
                current_time = '[{:02d}:{:02d}:{:02d}]'.format(
                    time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
                print('     ' + current_time + ' No slot available at ' + dmv_names[i_dmv])
            else:
                date_string = soup.find('div', attrs={'class': 'col-md-8'}).find('label',
                                        attrs={'class': 'control-label'}).text
                date_string = re.sub('Time of Appointment for ', '', date_string)
                date_string = re.sub(': ', '', date_string)
                assert(isinstance(date_string, str))

                time_string = []
                for foo in soup.find('div', attrs={'class': 'col-md-8'}).findAll('div',
                                     attrs={'class': 'col availableTimeslot'}):
                    time_string += re.findall(r'\d{1,2}:\d{2}? [A|P]M', foo.text)
                assert(all(isinstance(foo, str) for foo in time_string))

                date_time = [dt.datetime.strptime(date_string + ', ' + foo, '%B %d, %Y, %I:%M %p')
                             for foo in time_string]
                for foo in date_time:
                    desired = (desired_date[0] <= foo.date() <= desired_date[1]) * (desired_time[0]
                               <= foo.time() <= desired_time[1])
                    marker = ' *** ' if desired else '     '
                    current_time = '[{:02d}:{:02d}:{:02d}]'.format(
                        time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
                    print(marker + current_time + ' Slot available at ' + dmv_names[i_dmv] + ', ' +
                          str(foo) + marker)
                    if desired:
                        os.system('say "' + dmv_names[i_dmv] + ', ' + foo.strftime('%b %d, %-I:%M')
                                  + '"')
        except:
            current_time = '[{:02d}:{:02d}:{:02d}]'.format(
                    time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
            print('     ' + current_time + ' Error raised during the latest attempt')
        finally:
            time.sleep(t_sleep)
