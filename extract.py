import calendar
import json
import requests
from dateutil.parser import *
from dateutil.relativedelta import * 
from datetime import *

url = "http://localhost:5005/model/parse"


# response = json.loads(raw_response.text)
response_query_destination = "Where do you wanna go?"
response_query_departure = "Where will you board the flight from?"
response_query_t1 = "What's the preferred time for departure?"
response_query_t2 = "what's the preferred time for return flight?"
response_query_onward_date = "please enter first flight date"
response_query_return_date = "please enter return flight date"
destination_flag = 0
departure_flag = 0
festive_dates = {"diwali": datetime.strptime("2022-10-24", "%Y-%m-%d"), "holi": datetime.strptime("2022-03-19", "%Y-%m-%d"), "christmas": datetime.strptime("2022-12-25", "%Y-%m-%d"), "valentine's day": datetime.strptime("2022-02-14", "%Y-%m-%d")}
time_slots = {"early morning": "00:00 - 06:00", "morning": "06:00 - 12:00", "afternoon": "12:00 - 06:00", "noon": "11:00 - 13:00", "eve": "18:00 - 24:00", "evening": "18:00 - 24:00", "night": "20:00 - 24:00"}
calendar_surplus = {"sunday": calendar.SUNDAY, "monday": calendar.MONDAY, "tuesday": calendar.TUESDAY, "wednesday": calendar.WEDNESDAY, "thursday": calendar.THURSDAY, "friday": calendar.FRIDAY, "saturday": calendar.SATURDAY}
today = date.today()
flag_add = 1

with open("text.txt", "w") as file:
    while True:
        lang = input("continue?")
        if lang =='y':
            text = input("enter text")
            payload = {
                "text": text,
                "message_id": "1234-abde-4321"
                }
            day_one = ""
            day_two = ""
            destination = ""
            departure = ""
            weekday_one = ""
            weekday_two = ""
            t1 = ""
            t2 = ""
            relation= ""
            festival= ""
            personalevent = ""
            dates = []
            buffer = []
            date_order = []
            times = {}
            info = {}
            entity_list = []
            raw_response = requests.post(url, json=payload)

            info = raw_response.json()
            # print(info)

            entity_list = info["entities"]
            message = info["text"]
            buffer = message.split(" ")
            # Parses all the literal dates 
            try:
            
                for i in range(0, len(buffer)):
                
                    if buffer[i][0].isnumeric():
                        dates.append(parse(buffer[i] + " " + buffer[i+1], fuzzy=True))
                        date_order.append(buffer[i])
                dates.sort()
            except ParserError:
                pass


            if info["intent"]["name"] == "returnsearch":

                onward = response_query_onward_date
                return_mess = response_query_return_date
                try:
                    for i in entity_list:
                        if i.get("role") == "t2":
                            t2 = i["value"]
                        if i.get("role") == "t1":
                            t1 = i["value"]
                        if i.get("role") == "weekday_one":
                            weekday_one = i["value"]
                        if i.get("role") == "weekday_two":
                            weekday_two = i["value"]
                        if i.get("role") == "destination":
                            destination = i["value"]
                        if i.get("role") == "departure":
                            departure = i["value"]
                        if i.get("entity") == "festivals":
                            festival = i["value"]
                        if i.get("role") == "add":
                            flag_add = 1
                        if i.get("role") == "sub":
                            flag_add = -1
                except ValueError:
                    pass
                # checks - departure and destination
                if len(departure) == 0:
                    from_mess = response_query_departure
                else:
                    from_mess = departure[0].upper() + departure[1:].lower()

                if len(destination) == 0:
                    to_mess = response_query_destination
                else:
                    to_mess = destination[0].upper() + destination[1:].lower()

                # checks - time onward and return 

                if len(t1)>0:
                    onward_departure_time = time_slots[t1.lower()]
                else:
                    onward_departure_time = "please enter onward departure time"

                if len(t2)>0:
                    return_departure_time = time_slots[t2.lower()]
                else:
                    return_departure_time = "please enter Return departure time"
                
                if len(festival)!=0 and len(dates) == 0:
                    if len(weekday_one) + len(weekday_two) == 0:
                        if len(destination)>0 and len(departure)>0:
                            if buffer.index(festival) > buffer.index(destination) and buffer.index(festival) < buffer.index(departure):
                                onward = datetime.strftime(festive_dates[festival.lower()], "%d-%m-%Y")
                                return_mess = response_query_return_date
                            else:
                                onward = response_query_onward_date
                                return_mess = datetime.strftime(festive_dates[festival.lower()], "%d-%m-%Y")
                    elif len(weekday_one) > 0 and len(weekday_two) > 0:
                        if abs(buffer.index(festival) - buffer.index(weekday_one)) < abs(buffer.index(festival) - buffer.index(weekday_two)):
                            onward = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                            return_mess = datetime.strftime((festive_dates[festival.lower()] + relativedelta(weekday=calendar_surplus[weekday_one.lower()])) + relativedelta(weekday = calendar_surplus[weekday_two.lower()]), "%d-%m-%Y")
                        else:
                            onward = datetime.strftime(today + relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                            return_mess = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_two.lower()]), "%d-%m-%Y")

                    elif len(weekday_one)>0 and len(weekday_two)==0:
                        if abs(buffer.index(festival) - buffer.index(weekday_one))>4:
                            onward = datetime.strftime(today + relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                            return_mess = datetime.strftime(festive_dates[festival.lower()], "%d-%m-%Y")
                        else:
                            onward = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                            return_mess = response_query_return_date
                    
                    elif len(weekday_one)==0 and len(weekday_two)>0:
                        if abs(buffer.index(festival) - buffer.index(weekday_two))>4:
                            onward = datetime.strftime(festive_dates[festival.lower()], "%d-%m-%Y")
                            return_mess = datetime.strftime(festive_dates[festival.lower()] + relativedelta(weekday=calendar_surplus[weekday_two.lower()]), "%d-%m-%Y")
                        else:
                            onward = response_query_onward_date
                            return_mess = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")

                elif len(festival)!=0 and len(dates) == 1:
                    if len(weekday_one)>0 :
                        onward = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                        return_mess = datetime.strftime(dates[0], "%d-%m-%Y")
                    elif len(weekday_two)>0:
                        onward = datetime.strftime(dates[0], "%d-%m-%Y")
                        return_mess = datetime.strftime(festive_dates[festival.lower()] + flag_add*relativedelta(weekday=calendar_surplus[weekday_two.lower()]), "%d-%m-%Y")
                            # two cases left festival + date and week cross (festival + date)
                

                elif len(dates) == 2 and len(festival)==0:
                    # needs retraining for secondary relative date and secondary festival
                    if len(weekday_one)>0 and len(weekday_two)==0:
                        onward = datetime.strftime(dates[0] + flag_add*relativedelta(weekday=calendar_surplus[weekday_one.lower()]),  "%d-%m-%Y")
                        return_mess = datetime.strftime(dates[1], "%d-%m-%Y")
                    elif len(weekday_one)==0 and len(weekday_two)>0:
                        onward = datetime.strftime(dates[0], "%d-%m-%Y")
                        return_mess = datetime.strftime(dates[1] + flag_add*relativedelta(weekday=calendar_surplus[weekday_two.lower()]), "%d-%m-%Y")
                    elif len(weekday_one)==0 and len(weekday_two)==0:
                        onward = datetime.strftime(dates[0], "%d-%m-%Y")
                        return_mess = datetime.strftime(dates[1], "%d-%m-%Y")


                structured_response = {"From": from_mess,
                    "To": to_mess,
                    "Onward": onward,
                    "Return": return_mess,
                    "Onward Departure Time": onward_departure_time,
                    "Return Departure Time": return_departure_time}

            # one way search
            if info["intent"]["name"] == "onewaysearch":
                onward_departure_time = "please enter preferred flight time"
                return_departure_time = "blank"
                return_mess = "blank"

                for i in entity_list:
                    if i.get("entity") == "time":
                        t1 = i["value"]
                    if i.get("entity") == "weekday":
                        weekday_one = i["value"]
                    if i.get("role") == "destination":
                        destination = i["value"]
                    if i.get("role") == "departure":
                        departure = i["value"]
                    if i.get("entity") == "festivals":
                        festival = i["value"]
                    if i.get("role") == "add":
                        flag_add = 1
                    if i.get("role") == "sub":
                        flag_add = -1
                
                 # checks - departure and destination
                if len(departure) == 0:
                    from_mess = response_query_departure
                else:
                    from_mess = departure[0].upper() + departure[1:].lower()

                if len(destination) == 0:
                    to_mess = response_query_destination
                else:
                    to_mess = destination[0].upper() + destination[1:].lower()
                
                if len(t1)>0:
                    onward_departure_time = time_slots[t1.lower()]


                if len(dates)>0:
                    onward = datetime.strftime(dates[0], "%d-%m-%Y")
                elif len(weekday_one)>0 and len(festival)==0:
                    onward = datetime.strftime(today + relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                elif len(weekday_one)>0 and len(festival)>0:
                    onward = datetime.strftime(festive_dates[festival.lower()] + relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")
                elif len(weekday_one) == 0 and len(dates) == 0 and len(festival)>0:
                    onward = datetime.strftime(festive_dates[festival.lower()] + relativedelta(weekday=calendar_surplus[weekday_one.lower()]), "%d-%m-%Y")



                structured_response = {"From": from_mess,
                    "To": to_mess,
                    "Onward": onward, 
                    "Return": return_mess,
                    "Onward Departure Time": onward_departure_time,
                    "Return Departure Time": return_departure_time}




            file.write(message + "---")
            file.write(str(structured_response) + "\n")
        else:
            break
    

file.close()



