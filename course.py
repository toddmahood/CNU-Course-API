import ratemyprofessor

# Get our school object upon import so that we don't have to load it every time a professor rating is queried.
# Check out RateMyProfessorAPI @ https://github.com/Nobelz/RateMyProfessorAPI
school = ratemyprofessor.get_school_by_name("Christopher Newport University")

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
        self.name = cols[1]
        self.section = cols[2]
        self.title = cols[3]
        self.hours = int(cols[4])
        self.area_of_llc = cols[5]
        self.course_type = cols[6]
        self.days = cols[7]
        self.time = cols[8]
        self.location = cols[9]
        self.instructor	= cols[10]
        self.seats_available = int(cols[11])
        self.status = cols[12]
            
    def get_professor_rating(self):
        """
        Returns list of tuples containing professor rating statistics from ratemyprofessor.com
        """
        # List approach was taken because there could be multiple professors listed. 
        ratings = []
        for instructor in self.instructor.split(" and "):
            professor = ratemyprofessor.get_professor_by_school_and_name(school, self.instructor)
            if self.instructor != "Staff, CNU" and professor is not None:
                if professor.would_take_again is not None:
                    would_take_again = str(round(professor.would_take_again, 1)) + '%'
                else:
                    would_take_again = "N/A"
                ratings.append((instructor, professor.rating, professor.difficulty, professor.num_ratings, would_take_again))
        return ratings

    def __str__(self):
        return f"CRN: {self.crn}, Course: {self.name}, Section: {self.section}, Title: {self.title}, Hours: {self.hours}, Area of LLC: {self.area_of_llc}, Type: {self.course_type}, Days: {self.days}, Time: {self.time}, Location: {self.location}, Instructor: {self.instructor}, Seats Available: {self.seats_available}, Status: {self.status}"

    def __eq__(self, other):
        """
        Pending implementation.
        """
        return False
            
