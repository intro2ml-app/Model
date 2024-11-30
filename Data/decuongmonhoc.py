import PyPDF2

start_page = 2  # Page A (0-indexed, so page 2 is the third page)
end_page = 6    # Page B (inclusive)

# Open the PDF file
with open('decuongmonhoc.pdf', 'rb') as file:
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfReader(file)
    
    # Extract text from pages in the specified range
    text = ""
    for page_num in range(start_page - 1, end_page):  # Adjust for 0-indexing
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

# Print the extracted text
courses = text.split("\n")
print(courses)
for course in courses:
    course_id = None
    course_name = None
    course_start_page = None