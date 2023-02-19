import streamlit as st
import pandas as pd
import math
import requests
from datetime import datetime
from datetime import time
from time import sleep
import pytz

st.set_page_config(
        page_title = "Dashboard",
        layout = "wide"  
)

with st.sidebar:
    startDate = st.date_input("Start Date", value = datetime.now(pytz.timezone('US/Pacific')))
    startHour = st.number_input("Start Hour", min_value = 0, max_value = 24, value = 0, step = 1)
    startMin = st.number_input("Start Minute", min_value = 0, max_value = 59, value = 0, step = 1) 
    live = st.checkbox("Update End Date Live")
    if not live:
        endDate = st.date_input("End Date") 
        endHour = st.number_input("End Hour", min_value = 0, max_value = 23, value = 23, step = 1)
        endMin = st.number_input("End Minute", min_value = 0, max_value = 59, value = 59, step = 1)
    boxValue = st.number_input("Boxing Value", min_value = 1, value = 1, step = 1)
    boxUnit = st.selectbox("Boxing Unit", ["Days", "Hours", "Minutes", "Seconds"], index=1)
    trim = st.checkbox("Trim ends")
    
title = st.empty()

boxSize = boxValue
if boxUnit != "Seconds":
    boxSize *= 60
    if boxUnit != "Minutes":
        boxSize *= 60
        if boxUnit != "Hours":
            boxSize *= 24

chart = st.empty()

while True:
    startDateTimestamp = datetime.combine(startDate, time(startHour, startMin, 0)).timestamp()
    if live:
        endDateTimestamp = datetime.now().timestamp()
        endDateTime_localized = datetime.now(pytz.timezone('US/Pacific'))
    else:
        endDateTimestamp = datetime.combine(endDate, time(endHour, endMin, 0)).timestamp()
        endDateTime_localized = datetime.combine(endDate, time(endHour, endMin, 0))

    if startDateTimestamp >= endDateTimestamp:
        title.write("Start date must be before end date")
        break
    
    url = "https://odozkue0n6.execute-api.us-west-2.amazonaws.com/Stage/getLogs"
    body = {"startTime":startDateTimestamp, "endTime": endDateTimestamp}
    response = requests.post(url, json = body)

    if response.status_code == 200:
        df = pd.json_normalize(response.json(), record_path=['logs'])
    else:
        continue

    boxes = math.ceil((endDateTimestamp - startDateTimestamp)/boxSize)
    if boxUnit == "Days":
        box_date_strings = [datetime.fromtimestamp(startDateTimestamp + boxSize * box).strftime("%m/%d/%Y") for box in range(boxes)]
        startDateTimeString = datetime.fromtimestamp(startDateTimestamp).strftime("%m/%d/%Y")
        endDateTimeString = endDateTime_localized.strftime("%m/%d/%Y")
    if boxUnit == "Hours":
        box_date_strings = [datetime.fromtimestamp(startDateTimestamp + boxSize * box).strftime("%H:%M") for box in range(boxes)]
        startDateTimeString = datetime.fromtimestamp(startDateTimestamp).strftime("%m/%d/%Y, %H:%M")
        endDateTimeString = endDateTime_localized.strftime("%m/%d/%Y, %H:%M")
    if boxUnit == "Minutes":
        box_date_strings = [datetime.fromtimestamp(startDateTimestamp + boxSize * box).strftime("%H:%M") for box in range(boxes)]
        startDateTimeString = datetime.fromtimestamp(startDateTimestamp).strftime("%m/%d/%Y, %H:%M")
        endDateTimeString = endDateTime_localized.strftime("%m/%d/%Y, %H:%M")
    if boxUnit == "Seconds":
        box_date_strings = [datetime.fromtimestamp(startDateTimestamp + boxSize * box).strftime("%H:%M:%S") for box in range(boxes)]
        startDateTimeString = datetime.fromtimestamp(startDateTimestamp).strftime("%m/%d/%Y, %H:%M:%S")
        endDateTimeString = endDateTime_localized.strftime("%m/%d/%Y, %H:%M:%S")
    box_values = [0 for _ in range(boxes)]

    if df.size > 0:
        for index, log in df.iterrows():
            box = math.floor((log['timeCreated'] - startDateTimestamp)/boxSize)
            box_values[box] += 1


        if trim and box_values:
            for value in box_values:
                if value == 0:
                    box_values = box_values[1:]
                    box_date_strings = box_date_strings[1:]
                else:
                    break
            for value in box_values[::-1]:
                if value == 0:
                    box_values = box_values[:-1]
                    box_date_strings = box_date_strings[:-1]
                else:
                    break

        if boxUnit == "Days":
            d = {'Dates': box_date_strings, 'Conversations': box_values}
        else:
            d = {'Times': box_date_strings, 'Conversations': box_values}

        histo_df = pd.DataFrame(data=d)

        title.write("Total Conversations From " + startDateTimeString + " To " + endDateTimeString)
        if boxUnit == "Days":
            chart.bar_chart(data=histo_df, x='Dates', y='Conversations')
        else:
            chart.bar_chart(data=histo_df, x='Times', y='Conversations')
    
    else:
        title.write("No Data From " + startDateTimeString + " To " + endDateTimeString)
    
    sleep(1)