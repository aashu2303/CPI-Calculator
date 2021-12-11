import json

credits = []
points = []
types = {}


def get_grade(char):
    if char == "A+" or char == "A":
        return 10
    elif char == "A-":
        return 9
    elif char == "B":
        return 8
    elif char == "B-":
        return 7
    elif char == "C":
        return 6
    elif char == "C-":
        return 5
    elif char == "D":
        return 4
    elif char == "FR" or char == "F" or char == "FS":
        return 0
    else:
        return None


with open("CPI.json", "r") as file:
    data = json.load(file)["courses"]
    for course in data:
        sem = course['semester']
    total_p = 0
    total_cre = 0

    for i in range(1, sem + 1):
        p = 0
        cre = 0
        for course in data:
            if course['semester'] == i and get_grade(course['grade']) is not None:
                cre += course['credits']
                total_cre += course["credits"]
                p += course['credits'] * get_grade(course['grade'])
                total_p += course['credits'] * get_grade(course['grade'])
        points.append(p)
        credits.append(cre)
        if cre != 0:
            print(f"Your Semester {i} CGPA is {points[i - 1] / credits[i - 1]}")
        else:
            print(f"Your haven't done any credits in Semester {i} or the courses aren't graded yet")

    print(f"\nYour Overall CGPA till now is {total_p / total_cre}", end="\n\n")

    for course in data:
        if course['type'] not in types.keys():
            types[course['type']] = 0

        types[course['type']] += course['credits']
    print("This is the list of credits done in each type of course")
    for key, value in types.items():
        print(f"{key} : {value} credits")
