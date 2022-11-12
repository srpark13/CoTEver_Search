from html.parser import HTMLParser
from imghdr import what
from xml.dom.expatbuilder import parseString
from googleapiclient.discovery import build #google-api-python-client 
import requests
from bs4 import BeautifulSoup as bs
import json
import re
from readability import Document
import numpy as np
import pandas as pd
import os
url = 'https://www.google.com/search?q='
google_search_api = ""
google_engine_id = ""
header = { 
'User-Agent' : ('Mozilla/5.0 (Windows NT 10.0;Win64; x64)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98\
Safari/537.36'), 
} 

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

def html_parser(rough_html):
  parse_re = re.compile('<([^>]+)>|\t|\n|\r|\([^)]*\)|\[[^)]*\]')
  parsed_content = re.sub(parse_re, '', rough_html)
  return parsed_content

with open("examples.json","r",encoding="utf-8") as f:
    q = json.load(f)
questions = q['output']
res={}
res['questions'] = []
qst_res={}
qst_res['question sentence']=[]
for i in range (0, len(questions)):
    sub_questions = questions[i].split("\n")
    sub_questions = sub_questions[0:-1][0::2]

    for j in range(0,len(sub_questions)):
        sub_questions[j] = sub_questions[j].split(' : ',1)[1]
        
    qst_res['question sentence']=sub_questions[-1]
    res['questions'].append(qst_res)

    tmp_res = {}
    tmp_res['subquestions'] = []

    for j in range(0,len(sub_questions)-1):
        sub_qst={}
        sub_qst['subquestion sentence']=[]
        sub_qst['subquestion sentence']=sub_questions[j]
        tmp_res['subquestions'].append(sub_qst)
        tmptmp_res = {}
        tmptmp_res[str(j)] = []

        search_result = google_search(sub_questions[j], google_search_api, google_engine_id)

        with open("resp.json", 'w',encoding="utf-8") as f:
            json.dump(search_result, f, ensure_ascii=False, indent=4)

        with open("resp.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data['items']
        title = []
        url = []
        content = []

        for k in items:
            title.append(k['title'])
            url.append(k['link'])
            
        for k in range(0,5):
            response = requests.get(url[k], headers = header)
            doc = response.text
            docu = Document(doc)
            docu = docu.summary()
            docu = html_parser(docu)
            content.append(docu)

        title = title[0:5]
        url = url[0:5]

        for t in range(0,5):
            tmptmptmp_res = {}
            tmptmptmp_res['url'] = url[t]
            tmptmptmp_res['title'] = title[t]
            tmptmptmp_res['content'] = content[t]
            tmptmp_res[str(j)].append(tmptmptmp_res)
        tmp_res['subquestions'].append(tmptmp_res)

    res['questions'].append(tmp_res)

    
json_file = json.dumps(res,ensure_ascii=False, indent=4)
with open(os.path.join('./', 'result.json'),'w',encoding="utf-8") as f:
    f.write(json_file)
