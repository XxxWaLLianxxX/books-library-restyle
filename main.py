import requests
import os


folder = 'books'
url = "http://tululu.org/txt.php"
os.makedirs(folder, exist_ok=True)

for id in range(1, 11):
    response = requests.get(url, params={"id":id}, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 302:
        with open(f"{folder}/id{id}.txt", "w") as book:
            book.write(response.text)
    else:
        continue
