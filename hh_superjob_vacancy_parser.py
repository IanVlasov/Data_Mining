from bs4 import BeautifulSoup
import requests
import time
import pymongo
from random import randint
import re


class VacancyParser:

    def __init__(self):
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 " \
                          "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 "
        self.hh_base_url = 'https://spb.hh.ru'
        self.sj_base_url = 'https://www.superjob.ru'
        self.vacancies_db = []

    def search_vacancy(self):
        vacancy_to_search = input('Введите название интересующей вакансии: ')
        self.hh_search(vacancy_to_search)
        self.sj_search(vacancy_to_search)

    def hh_search(self, vacancy):
        next_url = '/search/vacancy'
        params = {'st': 'searchVacancy', 'text': vacancy}
        while next_url:
            hh_response = requests.get(f'{self.hh_base_url}{next_url}', params=params,
                                       headers={'User-Agent': self.USER_AGENT})
            if hh_response.status_code == 200:
                soup = BeautifulSoup(hh_response.text, 'lxml')
                vacancies_on_page = soup.find_all('div',
                                                  attrs={'class': "vacancy-serp-item__row "
                                                                  "vacancy-serp-item__row_header"})
                for vacancy in vacancies_on_page:
                    self.vacancies_db.append(self.get_vacancy_record_hh(vacancy))

                try:
                    next_url = soup.find('a', attrs={'class': 'bloko-button HH-Pager-Controls-Next '
                                                              'HH-Pager-Control'}).attrs['href']
                    params = {}
                except AttributeError:
                    break

                time.sleep(randint(1, 5))
                print('Идем дальше')

            else:
                print('Нас забанили!')
                break

    def get_vacancy_record_hh(self, vacancy):
        name = vacancy.find('div', attrs={'class': 'vacancy-serp-item__info'}).text
        salary_str = vacancy.find('div', attrs={'class': 'vacancy-serp-item__sidebar'}).text
        min_salary, max_salary = self.salary_converter_hh(salary_str)
        link = f"{self.hh_base_url}{vacancy.find('a').attrs['href']}"
        source = 'HeadHunter'
        vacancy_record = {'Title': name,
                          'Min salary': min_salary,
                          'Max salary': max_salary,
                          'Link': link,
                          'Source': source}
        return vacancy_record

    def sj_search(self, vacancy):
        next_url = '/vacancy/search/'
        params = {'keywords': vacancy}
        while next_url:
            sj_response = requests.get(f'{self.sj_base_url}{next_url}', params=params,
                                       headers={'User-Agent': self.USER_AGENT})
            if sj_response.status_code == 200:
                soup = BeautifulSoup(sj_response.text, 'lxml')
                vacancies_on_page = soup.find_all('div',
                                                  attrs={'class': '_3zucV _2GPIV i6-sc _3VcZr'})
                for vacancy in vacancies_on_page:
                    self.vacancies_db.append(self.get_vacancy_record_sj(vacancy))

                try:
                    next_url = soup.find('a', attrs={'class': 'icMQ_ _1_Cht _3ze9n '
                                                              'f-test-button-dalshe f-test-link-dalshe'}).attrs['href']
                    params = {}
                except AttributeError:
                    break

                time.sleep(randint(1, 5))
                print('Идем дальше')

            else:
                print('Нас забанили!')
                break

    def get_vacancy_record_sj(self, vacancy):
        name = vacancy.find('a', {'class': re.compile(r'icMQ_.*_2JivQ.*')}).text
        salary_str = vacancy.find('span', attrs={'class': '_3mfro _2Wp8I f-test-text-company-item-salary '
                                                         'PlM3e _2JVkc _2VHxz'}).text
        min_salary, max_salary = self.salary_converter_sj(salary_str)
        link = f"{self.sj_base_url}{vacancy.find('a', {'class': re.compile(r'icMQ_.*_2JivQ.*')}).attrs['href']}"
        source = 'SuperJob'
        vacancy_record = {'Title': name,
                          'Min salary': min_salary,
                          'Max salary': max_salary,
                          'Link': link,
                          'Source': source}
        return vacancy_record

    @staticmethod
    def salary_converter_hh(salary_str):
        if not salary_str:
            min_salary = None
            max_salary = None
            return min_salary, max_salary

        salary_str = salary_str.replace(u'\xa0', u'')

        if salary_str.find('от') != -1:
            min_salary = int(salary_str[salary_str.find(' '): salary_str.rfind(' ')])
            max_salary = None
            return min_salary, max_salary

        elif salary_str.find('до') != -1:
            min_salary = None
            max_salary = int(salary_str[salary_str.find(' '): salary_str.rfind(' ')])
            return min_salary, max_salary

        else:
            salary_str = salary_str.split('-')
            min_salary = int(salary_str[0])
            max_salary = int(salary_str[1][:salary_str[1].rfind(' ')])
            return min_salary, max_salary

    @staticmethod
    def salary_converter_sj(salary_str):
        if not salary_str or salary_str == 'По договорённости':
            min_salary = None
            max_salary = None
            return min_salary, max_salary

        salary_str = salary_str.replace(u'\xa0', u' ')

        if salary_str.find('от') != -1:
            min_salary = int(salary_str[salary_str.find(' '): salary_str.rfind(' ')].replace(' ', ''))
            max_salary = None
            return min_salary, max_salary

        elif salary_str.find('до') != -1:
            min_salary = None
            max_salary = int(salary_str[salary_str.find(' '): salary_str.rfind(' ')].replace(' ', ''))
            return min_salary, max_salary

        else:
            salary_str = salary_str.split('—')
            if len(salary_str) == 1:
                min_salary = int(salary_str[0][salary_str[0].find(' '): salary_str[0].rfind(' ')].replace(' ', ''))
                max_salary = int(salary_str[0][salary_str[0].find(' '): salary_str[0].rfind(' ')].replace(' ', ''))
            else:
                min_salary = int(salary_str[0].replace(' ', ''))
                max_salary = int(salary_str[1][:salary_str[1].rfind(' ')].replace(' ', ''))
            return min_salary, max_salary


if __name__ == '__main__':
    test = VacancyParser()
    test.search_vacancy()

    mongo_url = 'mongodb://localhost:27017'
    client = pymongo.MongoClient('localhost', 27017)
    database = client.hh_sj_parser
    collection = database.hh_sj_vacancies

    for vacancy_ in test.vacancies_db:
        collection.insert_one(vacancy_)

