# -*- coding: utf-8 -*-


import sys
import re
import json
import gzip

import traceback
import random

import pandas as pd
from flask import Flask, request, jsonify
import logging


from urllib import parse

logging.basicConfig(level=logging.DEBUG)


""" Load data """

path = 'mdm_s.json.gz'
i = 0
df_dict = {}
search_full = ""


jgz = gzip.open(path, 'rb')
for line in jgz:
    d = json.loads(line)
    
    if not (len(d['imageURLHighRes']) and len(d['title'])): continue
    if re.search(r'[<>]',d['title']): continue
    d['brand'] = d['brand'] if not re.search(r'[<>]',d['brand']) else ""
    # if d['rank']:
    #     if isinstance(d['rank'], list): d['rank'] = d['rank'][0]
    #     d['rankn'] = int(re.subn(r'\D','',d['rank'])[0])
    # else:
    #     d['rankn'] = float('inf')
    # for k in ['category', 'tech1', 'fit',  'tech2',  'similar_item', 'date']:
    #     del d[k]
    search_full+=parse.unquote(d['title'])+"|"+parse.unquote(d['brand'])+"<"+d['asin']+">"
    if len(d['asin']) != 10:print(d['asin'])


    #for col in d.keys():
      #d[col] = d[col] if len(d[col]) else None # make it 'Null' if empty list or empty string
    #d['details'] = [ i[0]+" "+i[1] for i in d['details'].items()] if 'details' in d and d['details'] else None
    
    #if d['rankn']<float('inf'): i+=1
    #if d['asin'] in df_dict:
        #i+=1
        #if json.dumps(d) != json.dumps(df_dict[d['asin']]): print("not match")
    df_dict[d['asin']] = d

# with gzip.open('mdm_s.json.gz', 'wb') as outf :
#     for i in sorted(df_dict.values(),key=lambda k: k['rankn']):
#         outf.write(bytes(json.dumps(i)+'\n','UTF-8'))
        
#print(i)        


print(path,len(df_dict))
print(len(search_full))




def wrap_response(asins):
    return [ dict(
            asin = asin,
            title = parse.unquote(df_dict[asin]['title']),
            img_url = df_dict[asin]['imageURLHighRes'][0],
            brand = parse.unquote(df_dict[asin]['brand']) if not re.search(r'[<>]',df_dict[asin]['brand']) else "",
        ) for asin in asins]


""" Random """

        
def get_rand_items(num):

    asins = random.choices(list(df_dict.keys()),k=num)
    #print(asins)

    return wrap_response(asins)


#print(get_rand_items(5))

#sys.exit()

""" search """

def search_keyword(word,num):
    asins = []
    
    point = search_full.find(word)
    while point > -1:
        #print(point)
        #print(search_full[point:point+62])
        asin_point = search_full.find("<",point-1)
        asin = search_full[asin_point+1:asin_point+11]
        #print(asin)
        asins.append(asin)
        
        if len(asins)>=num: break
        point = search_full.find(word,asin_point+12)
        
    return wrap_response(asins)
    
# print(search_keyword("D",5))
# print(search_keyword("Anglophile",5))
# print(search_keyword("B01CC3N2CA",5))
# sys.exit()



app = Flask(__name__)

@app.route("/random", methods=['GET']) 
def api_rand():
    
        try:
            args = request.args
            app.logger.info('Processing default request')
            print(args,file=sys.stdout)
            sys.stdout.flush()
            
            num = int(args.get('num','5'))
            return jsonify(get_rand_items(num if num>0 else 5))


        except:

            return jsonify({'args': str(args), 'trace': traceback.format_exc()})


@app.route("/recommend", methods=['GET']) 
def api_recom():
    
        try:
            args = request.args
            if 'asin' not in args:
                return jsonify({'error':'you need to specify an asin for recommend'})
            
            num = int(args.get('num','5'))
            return jsonify(get_rand_items(num if num>0 else 5)) # random recommend for now, will be replaced with real recommender


        except:

            return jsonify({'args': str(args), 'trace': traceback.format_exc()})


@app.route("/search", methods=['GET']) 
def api_search():
    
        try:
            args = request.args
            if 'keyword' not in args:
                return jsonify({'error':'you need to specify an keyword for search'})
            
            num = int(args.get('num','5'))
            return jsonify(search_keyword(args['keyword'],num if num>0 else 5))


        except:

            return jsonify({'args': str(args), 'trace': traceback.format_exc()})

if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 8888 # If you don't provide any port the port will be set to 12345
    
    app.run(port=port, debug=True)
