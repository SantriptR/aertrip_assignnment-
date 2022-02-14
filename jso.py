import requests
import json

url = "http://localhost:5005/model/parse"

# san = {"Rover": "San"}
# dic = {"san":  "Nastik"}

# print(dic[(san["Rover"]).lower()])



with open("text.txt", "w") as file:
    while True:
        lang = input("continue?")
        if lang =='y':
            text = input("enter text")
            payload = {
            "text": text,
            "message_id": "1234-abde-4321"
            }

            raw_response = requests.post(url, json=payload)
            trial = raw_response.json()
            print(len(trial["entities"]))
            file.write("\n"+str(trial))
        else:
            break

file.close()
