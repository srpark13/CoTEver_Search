from html.parser import HTMLParser
from xml.dom.expatbuilder import parseString
from googleapiclient.discovery import build #google-api-python-client 
import requests
import json
import re
from readability import Document
import os
url = 'https://www.google.com/search?q='
google_search_api = "AIzaSyAB5Jaqdh98MZ8aMv9bBxdMynMhJGRBfGQ"
google_engine_id = "74f117132b62c4715"
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

def search(q)->json:
    sub_questions = q['explanation']
    res={}
    res['questions'] = []
    qst_res={}
    qst_res['question sentence']=[]
    qst_res['question sentence']=q['question']
    res['questions'].append(qst_res)
    tmp_res = {}
    tmp_res['subquestions'] = []
    for i in sub_questions:
        sub_qst={}
        sub_qst['subquestion sentence']=sub_questions[str(i)]['sub_question']
        tmp_res['subquestions'].append(sub_qst)
        tmptmp_res = {}
        tmptmp_res[str(i)] = []
        search_result = google_search(sub_questions[str(i)]['sub_question'], google_search_api, google_engine_id)
        items = search_result['items']
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

        for k in range(0,5):
            tmptmptmp_res = {}
            tmptmptmp_res['url'] = url[k]
            tmptmptmp_res['title'] = title[k]
            tmptmptmp_res['content'] = content[k]
            tmptmp_res[str(i)].append(tmptmptmp_res)
        tmp_res['subquestions'].append(tmptmp_res)

    res['questions'].append(tmp_res)

    
    json_file = json.dumps(res,ensure_ascii=False, indent=4)
    return json_file
