import requests
import urllib.parse
from bs4 import BeautifulSoup
import time
import csv

# Define headers for our requests.
headers = {
    'Host': 'navigator.cnu.edu',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9'
}


class CNUCourseAPI:

    def __init__(self, semester, after2014=True):
        """
        Get the current course schedule to be used in subsequent methods
        :param after2014: (boolean) Specifies whether the course was before or after 2014, defaults to True
        :param semester: (str) Specifies the semester to get schedule for. Can pass arguments like "fall 2022", "spring 2021", "2021 fall", ect.
        :raise: ValueError
        :return: None
        """

        '''
        Semester parameter seems to follow pattern {end_year}{term}
        End year: 
            2021-(2022)
            2022-(2023)
        Term parameters: 
            00 - Fall
            10 - Spring
            20 - May 
            31 - First summer term 
            32 - Second summer term
        '''

        year = None
        term = None

        if "fall" in semester.lower():
            term = "00"
        elif "spring" in semester.lower():
            term = "10"
        elif "may" in semester.lower():
            term = "20"
        elif "summer term 1" in semester.lower():
            term = "31"
        elif "summer term 2" in semester.lower():
            term = "32"

        # hacky way to get the first 4 consequtive digits in string
        for index, character in enumerate(semester.lower()):
            if (index + 3) <= semester.length():
                if character.isdigit() and semester[index + 1].isdigit() and semester[index + 2].isdigit() and semester[index + 3].isdigit():
                    year = semester[index:index+3]
                    break
        
        if year == None or term == None:
            raise ValueError("Invalid semester argument, please try again. Examples of valid ")

        semesterlist = f"{year}{term}" 

        if after2014:
            startyearlist = "2"
        else:
            startyearlist = "1"

        
        # Create our requests session, makes it easier to carry over cookies to next request.
        session = requests.Session()

        # Generates our cookies and provides viewstate and eventvalidation parameters for next request.
        response = session.get('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers)

        # Find post fields and parse them
        soup = BeautifulSoup(response.content, 'html.parser')
        viewstate = urllib.parse.quote(soup.find(id="__VIEWSTATE")["value"], safe='')
        viewstate_generator = urllib.parse.quote(soup.find(id="__VIEWSTATEGENERATOR")["value"], safe='')
        event_validation = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")["value"], safe='')

        

        interestlist2 = "Any" # Liberal Learning Core, Honors Program or Writing Intensive Course selection
        # disciplineslistbox = "All+Courses" # Subject selection (not required)

        headers = {
            'Host': 'navigator.cnu.edu',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://navigator.cnu.edu',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://navigator.cnu.edu/StudentScheduleofClasses/',
            'accept-language': 'en-US,en;q=0.9'
        }

        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={startyearlist}&semesterlist={semesterlist}&Interestlist2={interestlist2}&CourseNumTextbox=&Button1=Search'
        response = session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        # Stop here if you just want schedule html
        print("Successfully grabbed schedule html.")



    def search():
        return None
    
    def get_csv():