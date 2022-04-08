from cnu_schedule import *
import time

if __name__ == "__main__":
    # start = time.time()
    schedule = CNUSchedule("Fall 2022", discipline="Computer Science")
    print(len(schedule.courses))
    for course in schedule.courses:
        # if course.crn == '9298':
        print(course)
        # ratings = course.get_professor_ratings()
        # print(f"Professor(s) Rating Stats: {ratings}")
        # end = time.time()
        # time_elapsed = end - start
        # print(f"Parsed and found class in {time_elapsed} seconds.")
    csv_reader_obj = schedule.get_csv()
    # Print("CSV object returned and saved.")
    schedule.update()
    print("Updated.")
    for course in schedule.courses:
        print(course)
    
