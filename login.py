from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from config import *
import json


def get_element(driver, by, value):
    element = WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((by, value))
    )
    return element


def get_all_elements(driver, by, value):
    elements = WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_all_elements_located((by, value))
    )
    return elements


# Fun begins;)

def login(driver, email, password):
    site = "https://aims.iith.ac.in/aims/login/loginHome"
    driver.get(site)
    try:
        email_inp = get_element(driver=driver, by=By.ID, value="uid")
        password_inp = get_element(driver=driver, by=By.ID, value="pswrd")

        email_inp.send_keys(email)
        password_inp.send_keys(password)

        captcha_image = get_element(driver=driver, by=By.ID, value="appCaptchaLoginImg")
        captcha = captcha_image.get_attribute("src")[-5:]

        captcha_field = get_element(driver=driver, by=By.ID, value="captcha")
        captcha_field.send_keys(captcha)

        submit = get_element(driver=driver, by=By.NAME, value="signIn")
        submit.click()
        time.sleep(10)
    except:
        driver.quit()


def homepage(driver, actions):
    # site = "https://aims.iith.ac.in/aims/login/home"
    # driver.get(site)
    try:

        academic = get_element(driver, By.XPATH, "//span[@title='Academic']")
        # print(academic.get_attribute("title"))
        actions.click(on_element=academic)

        view_courses = get_element(driver, By.XPATH, "//span[@title='View My Courses']")
        actions.move_to_element(to_element=view_courses).click(on_element=view_courses)
        actions.perform()
    except:
        driver.quit()


def courses_page(driver):
    course_elements = get_all_elements(driver, by=By.CLASS_NAME, value=r'tab_body_bg')

    MAIN_DICT = {
        "courses": []
    }
    num_semesters = 0
    for elem in course_elements:
        class_name = elem.get_attribute("class")
        num_classes = len(class_name.split(" "))

        if num_classes > 3:
            num_semesters += 1

    for elem in course_elements:
        lis = elem.find_elements(By.XPATH, value=".//*")
        course_dict = {}
        if len(elem.get_attribute("class").split(" ")) > 3:
            num_semesters -= 1
            continue
        course_dict["Course Code"] = lis[0].text.strip()
        course_dict["Course Name"] = lis[1].text.strip()
        course_dict["Semester"] = num_semesters + 1
        course_dict["Credits"] = float(lis[2].text.strip())
        course_dict["Registration Type"] = lis[3].text.strip()
        course_dict["Course Type"] = lis[4].text.strip()
        course_dict["Segment"] = lis[5].text.strip()
        course_dict["Instructor Name"] = lis[6].text.strip()
        course_dict["Grade"] = lis[7].text.strip()
        course_dict["Feedback Status"] = lis[-1].get_attribute("title")

        MAIN_DICT["courses"].append(course_dict)
    driver.quit()
    with open("CPI.json", "w+") as file:
        json.dump(MAIN_DICT, file)


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


def cpi_calculator():
    credits = []
    points = []
    types = {}
    with open("CPI.json", "r") as file:
        data = json.load(file)["courses"]
        sem = data[0]["Semester"]
        total_p = 0
        total_cre = 0

        for i in range(sem, 0, -1):
            p = 0
            cre = 0
            for course in data:
                if course['Semester'] == i and get_grade(course['Grade']) is not None:
                    cre += course['Credits']
                    total_cre += course["Credits"]
                    p += course['Credits'] * get_grade(course['Grade'])
                    total_p += course['Credits'] * get_grade(course['Grade'])
            points.append(p)
            credits.append(cre)
            if cre != 0:
                print(f"Your Semester {i} CGPA is {points[sem - i] / credits[sem - i]}")
            else:
                print(f"Your haven't done any credits in Semester {i} or the courses aren't graded yet")

        print(f"\nYour Overall CGPA till now is {total_p / total_cre}", end="\n\n")

        for course in data:
            if course['Course Type'] not in types.keys():
                types[course['Course Type']] = 0

            if get_grade(course['Grade']) is not None:
                types[course['Course Type']] += course['Credits']
        print("This is the list of credits done in each type of course")
        for key, value in types.items():
            print(f"{key} : {value} credits")


def initialize():
    driver = webdriver.Chrome(Driver_Path)
    driver.set_window_size(1280, 1080)
    actions = ActionChains(driver)
    login(driver, email, password)
    homepage(driver, actions)
    courses_page(driver)


if __name__ == '__main__':
    # initialize()
    time.sleep(1)
    cpi_calculator()
