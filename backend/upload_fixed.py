from pinecone import Pinecone
import os
from dotenv import load_dotenv
import json

load_dotenv()

#load the pinecone stuff
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "penn-scheduler-py" #index(database) we are uploading to
dense_index = pc.Index(index_name) 

#getting the scraped data and loaoding it from the json.
with open('/Users/zikangjiang/learning_coding/penn_courses_data.json', 'r') as file:
    scraped_data = json.load(file)

# making it into a more manageable size for testing at first. 
course_data = scraped_data.get('courses')
sample_data = course_data[0:]

#variables needed to upload properly
upload_size = 90
i=0; # tracks # of upload cycles
stop_all = False; #makes sure we can break out of not just the for loop but the while loop as well.
iteration = 0;

#goes until entire dataset has been uploaded to Pinecone
while(True):
    upload_data = []
    for l in range(upload_size): #iterations through sets of 50 datapoints to upload. 
        iteration = i*upload_size + l #counts how many datapoints have been uploaded.
        data = sample_data[iteration]
        #structures data in the needed format
        data.update({"id":f"course{iteration}"})
        data['chunk_text'] = data.pop('course_name')
        upload_data.append(data)

        #upload the data
        if iteration == (len(sample_data)-1): #if all data has been uploaded. remembered to do this cuz got the out of bounds error.
            stop_all = True
            break;
    
    dense_index.upsert_records("penn", upload_data)
    print(f'uploaded for the {iteration}th time')
    
    if stop_all: #breaks out the while as well. 
        break;
    i+=1;

