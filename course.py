import ratemyprofessor

# Get our school object upon import so that we don't have to load it every time a professor rating is queried.
# Check out RateMyProfessorAPI @ https://github.com/Nobelz/RateMyProfessorAPI
school = ratemyprofessor.get_school_by_name("Christopher Newport University")

class Meeting():
    def __init__(self, days, time, location):
        """
        Store meeting attributes.
        """
        # Stores -1 for start and end time if there is none provided.
        self.days = [day for day in days]
        if time == "":
            self.start_time = -1
            self.end_time = -1
        else:
            self.start_time = int(time.split("-")[0])
            self.end_time = int(time.split("-")[1])
        self.location = location

    def __str__(self):
        return f"Days: {self.days}, Start Time: {self.start_time}, End Time: {self.end_time}, Location: {self.location}"

class Course():
    def __init__(self, row):
        """
        Store the course attributes, derived from html table row.
        """
        # 0-13 cols, but we exclude col 5 because it is always blank.
        cols = row.find_all('td')
        # get relevant column text and strip whitespace.
        cols = [col.text.strip() for index, col in enumerate(cols) if index != 5]
        # This assigns column data to course attributes. Doesn't currently do anything for columns with no value will simply assign empty string.
        self.crn = int(cols[0])
        self.course = cols[1]
        self.section = cols[2]
        self.title = cols[3]
        # self.hours = int(cols[4])
        hours = cols[4].split("-")
        if len(hours) > 1:
            self.min_hours = int(hours[0]) # min hours
            self.max_hours = int(hours[1]) # max hours
        else:
            self.min_hours = int(hours[0])
            self.max_hours = int(hours[0])
        self.area_llc = cols[5].split(" ") # List of interests
        self.type = cols[6] 

        # Not sure if this will work every time.
        self.meeting = []
        day_lines = cols[7].split(" and ") 
        time_lines = cols[8].split(" and ")
        location_lines = cols[9].split(" and ") # I am assuming that every time there are locations listed on two lines there will be multiple start, end, and times.
        for index, location in enumerate(location_lines):
            self.meeting.append(Meeting(day_lines[index], time_lines[index], location))
        self.instructors = cols[10].split(" and ")
        self.seats_still_available = int(cols[11]) 
        self.open = (cols[12] == "Open") 
        
    def get_professor_ratings(self):
        """
        Returns list of tuples containing professor rating statistics from ratemyprofessor.com
        """
        # List approach was taken because there could be multiple professors listed. 
        ratings = []
        for instructor in self.instructors:
            professor = ratemyprofessor.get_professor_by_school_and_name(school, instructor)
            if instructor != "Staff, CNU" and professor is not None:
                if professor.would_take_again is not None:
                    would_take_again = str(round(professor.would_take_again, 1)) + '%'
                else:
                    would_take_again = "N/A"
                ratings.append((instructor, professor.rating, professor.difficulty, professor.num_ratings, would_take_again))
        return ratings

    def __str__(self):
        return f"CRN: {self.crn}, Course: {self.course}, Section: {self.section}, Title: {self.title}, Minimum Hours: {self.min_hours}, Maximum Hours: {self.max_hours}, Area(s) of LLC: {self.area_llc}, Type: {self.type}, Meeting Information: {[str(meeting) for meeting in self.meeting]}, Instructor(s): {self.instructors}, Seats Available: {self.seats_still_available}, Open: {self.open}"

    def __eq__(self, other):
        """
        Pending implementation.
        """
        return False
            
