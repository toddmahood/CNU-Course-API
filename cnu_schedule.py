import requests
import urllib.parse
import cchardet
import lxml
import time
import csv
import os
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
    def get_dynamic_params(self, response):
        """
        Gets dynamic POST parameters from a requests response object.
        """
        # Find POST fields and parse them.
        soup = BeautifulSoup(response.content, 'lxml', from_encoding="utf8")
        viewstate = urllib.parse.quote(soup.find(id="__VIEWSTATE")["value"], safe='')
        viewstate_generator = urllib.parse.quote(soup.find(id="__VIEWSTATEGENERATOR")["value"], safe='')
        event_validation = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")["value"], safe='')
        return viewstate, viewstate_generator, event_validation

    def __init__(self, semester, interest="Any", discipline="All Courses", course_num="", after2014=True):
        """
        Get the current course schedule to be used in subsequent methods.
        Note you cannot pass in both interest and discipline or course number at the same time, you must pick one or the other and sort.
        :param after2014: (bool) Specifies whether the schedule is before or after 2014, defaults to True
        :param semester: (str) Specifies the semester to get schedule for. Can pass arguments like "fall 2022", "sPrIng 2021", "2021 fall", ect.
        :param interest: (str) Specifies Liberal Learning Core, Honors Program or Writing Intensive Course selection.
        :param discipline: (str - Case sensitive) Specifies the subject to look up and return.
        :param course_num: (str or int) Specifies the course number to lookup and return.
        :raise: ValueError - ValueError is raised if incorrect parameters are passed in.
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

        # start = time.time()
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
                        year = semester[index:index+4]
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

        headers.update(post_headers) # Add POST headers to existing header dictionary.

        # This intermediary request is not necessary for querying classes in the default term. However, once you try to request classes of a specific subject for a non default semester this request becomes necessary.
        data = f'__EVENTTARGET=semesterlist&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={startyearlist}&semesterlist={semesterlist}&Interestlist2=Any&CourseNumTextbox='
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        if response.status_code == 500:
            raise ValueError("Bad Request, make sure the provided semester exists. If it does, check to see if the POST payload is incorrect or headers have changed.")
        
        soup = BeautifulSoup(response.content, 'lxml', from_encoding="utf8")

        # Don't use dynamic parameter method because we need additional items from this request and there is no point in creating two identical BeautifulSoup objects.
        viewstate = urllib.parse.quote(soup.find(id="__VIEWSTATE")["value"], safe='')
        viewstate_generator = urllib.parse.quote(soup.find(id="__VIEWSTATEGENERATOR")["value"], safe='')
        event_validation = urllib.parse.quote(soup.find(id="__EVENTVALIDATION")["value"], safe='')

        interest_options = soup.find(id="Interestlist2").find_all('option')
        discipline_options = soup.find(id="DisciplinesListBox").find_all('option')
        interest_list = [option.get("value") for option in interest_options]
        discipline_list = [option.get("value") for option in discipline_options]

        # Sanity checks / some input data validation
        if interest != "Any" and (discipline != "All Courses" or course_num != ""):
            raise ValueError(f"Cannot pass interest and discipline or course_num arguments at the same time.")

        if interest.strip().upper() not in interest_list and interest != "Any":
            raise ValueError(f"Invalid interest argument, please try again. Examples of valid arguments include: {interest_list}")

        if discipline not in discipline_list:
            raise ValueError(f"Invalid discipline argument, please try again. Examples of valid arguments include: {discipline_list}")

        if course_num != "":
            try:
                course_num = int(course_num)
                course_num = str(course_num)
            except ValueError as e:
                raise ValueError(f"Invalid course_num argument, please try again. Examples of valid arguments include: 201, 150, 327, 214")

        if interest != "Any":
            interestlist2 = interest.strip().upper() 
            disciplineslistbox = ""
        else:
            interestlist2 = interest
            disciplineslistbox = "&DisciplinesListBox=" + discipline.strip().replace(" ", "+") 
        
        
        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={startyearlist}&semesterlist={semesterlist}&Interestlist2={interestlist2}{disciplineslistbox}&CourseNumTextbox={course_num}&Button1=Search'
        # print(data)

        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        if response.status_code == 500:
            raise ValueError("Bad Request, make sure the provided semester exists. If it does, check to see if the POST payload is incorrect or headers have changed.")
        
        # Remove POST headers from headers dictionary.
        for key in post_headers:
            headers.pop(key)
        
        self.__startyearlist = startyearlist
        self.__semesterlist = semesterlist
        self.__interestlist2 = interestlist2
        self.__disciplineslistbox = disciplineslistbox
        self.__query_course_num = course_num
        self.__schedule_response = response

        # end = time.time()
        # time_elapsed = end - start
        # print(f"Got HTML schedule in {time_elapsed} seconds.")
        self.courses = []
        # start = time.time()
        if "No Results Found. Please search again." not in response.text:
            schedule_soup = BeautifulSoup(response.content, 'lxml', from_encoding="utf8")
            # end = time.time()
            # time_elapsed = end - start
            # print(f"Created BeautifulSoup object in {time_elapsed} seconds.")
            rows = schedule_soup.find("table").find_all("tr") # Get all rows in html table
            for row in rows:
                # Ensure we are only passing valid rows to our Course constructor.
                if len(row.find_all('td')) >= 1:
                    # A little pre-processing to remove the linebreaks and replace them with " and ".
                    for linebreak in row.find_all("br"):
                        linebreak.replace_with(" and ")
                    self.courses.append(Course(row))
        
    def search(self):
        """
        Pending implementation?
        """
        return None
    
    def update(self):
        """
        Update schedule. Will assume the search parameters passed into constructor. Could potentially make this a Course method.
        """
        # Reload schedule starting from original search page, this is because cookies/session may expire before we want to update course schedule.
        response = self.session.get('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers)
        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(response)

        headers.update(post_headers)
        
        data = f'__EVENTTARGET=semesterlist&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={self.__startyearlist}&semesterlist={self.__semesterlist}&Interestlist2=Any&CourseNumTextbox='
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(response)

        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&startyearlist={self.__startyearlist}&semesterlist={self.__semesterlist}&Interestlist2={self.__interestlist2}{self.__disciplineslistbox}&CourseNumTextbox={self.__query_course_num}&Button1=Search'
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/', headers=headers, data=data)
        self.schedule_response = response

        for key in post_headers:
            headers.pop(key)

        self.courses = []
        if "No Results Found. Please search again." not in response.text:
            schedule_soup = BeautifulSoup(response.content, 'lxml', from_encoding="utf8")
            rows = schedule_soup.find("table").find_all("tr")
            for row in rows:
                if len(row.find_all('td')) >= 1:
                    for linebreak in row.find_all("br"):
                        linebreak.replace_with(" and ")
                    self.courses.append(Course(row))
    
    def get_csv(self, file_directory=""):
        """
        Returns csv.reader object with schedule data and saves csv to the file_directory passed in.
        """

        viewstate, viewstate_generator, event_validation = self.get_dynamic_params(self.__schedule_response)
        data = f'__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&__VIEWSTATEGENERATOR={viewstate_generator}&__EVENTVALIDATION={event_validation}&Button1=+Export+to+Excel+%28CSV%29'

        headers.update(post_headers)
        
        response = self.session.post('https://navigator.cnu.edu/StudentScheduleofClasses/socresults.aspx', headers=headers, data=data)
        with open(os.path.join(file_directory, "schedule.csv"), "wb") as file:
            for chunk in response:
                file.write(chunk)
            csv_reader = csv.reader(file)

        return csv_reader