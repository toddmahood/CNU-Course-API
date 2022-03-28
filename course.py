import ratemyprofessor

school = ratemyprofessor.get_school_by_name("Christopher Newport University")

class Course():
    def __init__(self):
        """
        process html here
        """
        self.crn
        self.course
        self.section
        self.title
        self.hours
        self.area_of_llc
        self.type
        self.days
        self.time
        self.location	
        self.instructor	
        self.seats_available
        self.status
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
            
