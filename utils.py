import json
import os

# data = ({
#             'content': content,
#             'date': date,
#             'source': url,
#             'title': title
#         })
def saveJson(data, folder="HandledData/Blog/"):
    # folder = "HandledData/Blog/"
    if data['title'] == "":
        print("No title found, skipping this data")
        return
    filename = data['title'] + ".json"
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def checkJsonExisted(data, folder="HandledData/Blog/"):
    # folder = "HandledData/Blog/"
    if data['title'] == "":
        print("No title found, skipping this data")
        return None
    filename = data['title'] + ".json"
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        print("File already exists, skipping this data")
        return True
    return False

def find_txt_files(folder_path):
    txt_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    return txt_files
