from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from config import *
import pickle
import pandas as pd
import numpy as np


def get_element(driver, by, value):
    element = WebDriverWait(driver=driver, timeout=10).until(
        EC.presence_of_element_located((by, value))
    )
    return element


def get_all_elements(driver, by, value):
    elements = WebDriverWait(driver=driver, timeout=10).until(
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
    try:

        academic = get_element(driver, By.XPATH, "//span[@title='Academic']")
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
    with open("CPI.pkl", 'wb') as file:
        pickle.dump(MAIN_DICT, file)


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


def cpi():
    with open("CPI.pkl", "rb") as file:
        data = pickle.load(file)
    course_data = pd.DataFrame(data["courses"]).replace("", np.nan).dropna()
    CREDITS = np.sum(course_data["Credits"])
    POINTS = 0
    # print(course_data.to_string())
    for group, frame in course_data.groupby("Semester"):
        credits = frame["Credits"]
        grades = frame["Grade"].apply(get_grade)
        points = credits * grades
        POINTS += np.sum(points)
        print(f"Semester-{group} GPA: {np.sum(points / np.sum(credits))}")

    print(f"\nCumulative GPA: {POINTS / CREDITS}")
    print(f"Total Credits done: {CREDITS}\n")

    for group, frame in course_data.groupby("Course Type"):
        print(f"{group}: {np.sum(frame['Credits'])}")


def initialize():
    driver = webdriver.Chrome(executable_path=Driver_Path)
    actions = ActionChains(driver)
    login(driver, email, password)
    homepage(driver, actions)
    courses_page(driver)


if __name__ == '__main__':
    # initialize()
    time.sleep(1)
    cpi()
