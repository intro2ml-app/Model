import PyPDF2
import os
import json


start_page = 2  # Page A (0-indexed, so page 2 is the third page)
end_page = 6    # Page B (inclusive)

# Lấy mục lục
with open('decuongmonhoc.pdf', 'rb') as file:
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfReader(file)
    
    # Extract text from pages in the specified range
    text = ""
    for page_num in range(start_page - 1, end_page):  # Adjust for 0-indexing
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

courses = text.split("\n")
i = 0
end = -1
handle_courses = []
for course in courses:
    if course == "" or course == " " or "MỤC LỤC" in course or len(course) < 20:
        continue
    course = course.strip()
    if course[1] == " ":
        course = course[2:]
    # print(course)
    course_id = course[:11]
    course_id = course_id.replace(" ", "").replace("–", "")

    course_name = course.split(" – ")[1]
    course_name = course_name.strip()
    course_name = course_name.replace(".", "")
    course_name = course_name.split(" ")[:-1]
    course_name = " ".join(course_name)
    course_name = course_name.strip()

    course_start_page = int(course.split(" ")[-1])
    new_course = {
        "course_id": course_id,
        "course_name": course_name,
        "course_start_page": course_start_page,
        "course_end_page": None
    }
    handle_courses.append(new_course)

for i in range(len(handle_courses) - 1):
    handle_courses[i]["course_end_page"] = handle_courses[i + 1]["course_start_page"] - 1

handle_courses[-1]["course_end_page"] = 306

for course in handle_courses:
    print(course)

with open('decuongmonhoc.pdf', 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    for courses in handle_courses:
        text = ""
        start_page = courses["course_start_page"]
        end_page = courses["course_end_page"]
        text = ""
        for page_num in range(start_page - 1, end_page):  # Adjust for 0-indexing
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

        # text = text.encode('utf-8', 'ignore').decode('utf-8')
        index = text.find("ĐỀ CƯƠNG TÓM T ẮT")  
        if index != -1:
            text = text[index:]      
            text = text.replace("ĐỀ CƯƠNG TÓM T ẮT", "ĐỀ CƯƠNG TÓM TẮT")

        courses["content"] = text

folder = "Decuongmonhoc/"
# save those those into json 
for course in handle_courses:
    file_name= course["course_id"] + ".json"
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(course, file, ensure_ascii=False,  indent=4)