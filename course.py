import ratemyprofessor

school = ratemyprofessor.get_school_by_name("Christopher Newport University")

class Course():
    def __init__(self, row):
        """
        Store the class attributes, derived from html table row.
        """
        if len(row.find_all('td')) >= 1:
            cols = row.find_all('td')
            #0-12 cols
            cols = [col.text.strip() for index, col in enumerate(cols) if index != 5]
            # print(cols)
            self.crn = cols[0]
            self.course_name = cols[1]
            self.section = cols[2]
            self.title = cols[3]
            self.hours = cols[4]
            self.area_of_llc = cols[5]
            self.course_type = cols[6]
            self.days = cols[7]
            self.time = cols[8]
            self.location = cols[9]
            self.instructor	= cols[10]
            self.seats_available = cols[11]
            self.status = cols[12]
        
    def get_professor_rating(self):
        professor = ratemyprofessor.get_professor_by_school_and_name(school, self.instructor)
        if self.instructor != "Staff, CNU" and professor is not None:
            self.instructor_rating = professor.rating
            self.instructor_difficulty = professor.difficulty
            self.instructor_num_ratings = professor.num_ratings
            if professor.would_take_again is not None:
                self.instructor_would_take_again = round(professor.would_take_again, 1) + '%'
            else:
                self.instructor_would_take_again = "N/A"
        else:
            self.instructor_rating = None
            self.instructor_difficulty = None
            self.instructor_num_ratings = None
            self.instructor_would_take_again = "N/A"

    def __str__(self):
        return f"CRN: {self.crn}, Course: {self.course_name}, Section: {self.section}, Title: {self.title}, Hours: {self.hours}, Area of LLC: {self.area_of_llc}, Type: {self.course_type}, Days: {self.days}, Time: {self.time}, Location: {self.location}, Instructor: {self.instructor}, Seats Available: {self.seats_available}, Status: {self.status}"
            
