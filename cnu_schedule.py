import requests
import urllib.parse
import os
import time
import csv
from bs4 import BeautifulSoup
from course import Course


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

post_headers = {
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'referer': 'https://navigator.cnu.edu/StudentScheduleofClasses/'
}


class CNUSchedule:

    def get_dynamic_params(self, html):
        '''
        '''
        # Find post fields and parse them
        soup = BeautifulSoup(html.content, 'html.parser')
        viewstate = urllib.parse.quote(soup.find(id="__VIEWSTATE")["value"], safe='')
        viewstate_generator = urllib.parse.quote(soup.find(id="__VIEWSTATEGENERATOR")["value"], safe='')
        event_validation = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")["value"], safe='')
        return viewstate, viewstate_generator, event_validation

    def __init__(self, semester, after2014=True):
        """
        Get the current course schedule to be used in subsequent methods
        :param after2014: (bool) Specifies whether the schedule is before or after 2014, defaults to True
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

        # hacky way to get the first 4 consecutive digits in string
        for index, character in enumerate(semester.lower()):
            if (index + 3) <= (len(semester) - 1):
                if character.isdigit() and semester[index + 1].isdigit() and semester[index + 2].isdigit() and semester[index + 3].isdigit():
                    if term == "00":
                        year = str(int(semester[index:index + 4]) + 1) 
                    else:
                        year = semester[index:index+3]
                    break
        
        if year == None or term == None:
            raise ValueError("Invalid semester argument, please try again. Examples of valid arguments include: 'fall 2020', '2020 spring', 'summer term 1 2018', 'may 2020', 'summer term 2 2019'")

        semesterlist = f"{year}{term}" 

        if type(after2014) != bool:
            raise ValueError("Invalid after2014 argument, must be of type bool.")

        if after2014:
            startyearlist = "2"
        else:
            startyearlist = "1"

        # Create our requests session, makes it easier to carry over cookies to next request.
        self.session = requests.Session()

        # Generates our cookies and provides viewstate and eventvalidation parameters for next request.
        response = self.session.get('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers)

        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(response)

        # Can possibly add these in init header
        interestlist2 = "Any" # Liberal Learning Core, Honors Program or Writing Intensive Course selection
        disciplineslistbox = "All+Courses" # Subject selection (not required)
        headers.update(post_headers)
        
        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={startyearlist}&semesterlist={semesterlist}&Interestlist2={interestlist2}&CourseNumTextbox=&Button1=Search'
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        if response.status_code == 500:
            raise ValueError("Bad Request, make sure the provided semester exists. If it does, check to see if the POST payload or headers have changed.")

        for key in post_headers:
            headers.pop(key)
        
        self.interestlist2 = interestlist2
        self.disciplineslistbox = disciplineslistbox
        self.semesterlist = semesterlist
        self.startyearlist = startyearlist
        self.schedule_html = BeautifulSoup(response.content, 'html.parser')
        self.courses = []
        rows = self.schedule_html.find("table").find_all("tr")
        for row in rows:
            # A little pre processing to remove the linebreaks and replace them with and.
            for linebreak in row.find_all("br"):
                linebreak.replace_with(" and ")
            self.courses.append(Course(row))
        

    def search(self, crn=None, course_name=None, ):
        return None
    
    def update(self):
        response = self.session.get('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers)

        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(response.content)

        headers.update(post_headers)
        
        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={self.startyearlist}&semesterlist={self.semesterlist}&Interestlist2={self.interestlist2}&CourseNumTextbox=&Button1=Search'
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        
        for key in post_headers:
            headers.pop(key)
    
        self.schedule_html = BeautifulSoup(response.content, 'html.parser')
        

    def get_csv(self, file_directory=""):
        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(str(self.schedule_html))
        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&Button1=+Export+to+Excel+%28CSV%29'

        headers.update(post_headers)
        
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/socresults.aspx', headers=headers, data=data)
        with open(os.path.join(file_directory, "schedule.csv"), "wb") as file:
            for chunk in response:
                file.write(chunk)

        csv_reader = csv.reader(file)
        return csv_reader