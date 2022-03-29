from cnu_schedule import *

if __name__ == "__main__":
    schedule = CNUSchedule("Fall 2022")
    for course in schedule:
        if course.crn == '9298':
            print(course)

