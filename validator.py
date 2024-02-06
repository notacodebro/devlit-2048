#!/usr/bin/python3
import requests
import json 
import argparse
import base64
import urllib3
import os 
import time
from bcolors import bcolors 

urllib3.disable_warnings()
BASE_URL = 'https://api.thousandeyes.com'

try:
    material = open('config', 'r')
except FileNotFoundError:
    print('!!!configuration file missing, create it please!!!!')
    exit(0)
material =  base64.b64decode(material.read()).decode("utf-8")
HEADERS = {'Content-Type' : 'application/json', 'Authorization' : f'Bearer {material}'}

def current_test_results(testid):
    url = f'{BASE_URL}/v7/test-results/{testid}/network'
    result = requests.get(url, headers=HEADERS, verify=False)
    result = json.loads(result.text)
    return(result)
    #print(json.dumps(result, indent=2))
def internet_insights():
    provider_data = {
        "window" : "1d",
        "providerName": ["Century Link", "Microsoft", "NTT", "Cogent", "Tata"]
    }
    url = f'{BASE_URL}/v7/internet-insights/outages/filter'
    result = requests.post(url, headers=HEADERS, json=provider_data, verify=False)
    result = json.loads(result.text)

def parser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-pre', help='pre-validation module', required=False, action='store_true')  
    _parser.add_argument('-post', help='post-validation module', required=False,action='store_true') 
    args = _parser.parse_args() 
    return args 

def pre_change():
    _current_test_ids = []
    print('Pre Change Validation Module') 
    internet_insights()
    for testid in _current_test_ids:
        result = current_test_results(testid)
        print('*'*64)
        print(f'Test Name: {result["test"]["testName"]}')
        print(f'Test Target: {result["results"][0]["serverIp"]}')
        print('*'*64)
        print('Results')
        print(f'Test Date: {result["results"][0]["date"]}')
        for items in result['results']:
            print(f'Test Agent: {items["agent"]["agentName"]}')
            if items['loss'] == 0.0:
                print(f'{bcolors.OKGREEN}Test Loss: {items["loss"]}{bcolors.ENDC}')
                tloss = 0
            if items['loss'] >=1:
                print(f'{bcolors.WARNING}Test Loss: {items["loss"]}{bcolors.ENDC}')
                tloss = 1
            if items['loss'] >=40:
                print(f'{bcolors.FAIL}Test Loss: {items["loss"]}{bcolors.ENDC}')
                tloss = 2
        x = input('press enter for more results')
    if tloss < 1:
        print(f'{bcolors.OKCYAN}All tests clear! You can proceed with change{bcolors.ENDC}')
    elif tloss == 1:
        print(f'{bcolors.FAIL}One or more tests has exhibited issues. Please Investigate{bcolors.ENDC}')
    post_change()
    
def post_change():
    _instant_test_ids = []
    print('Post Change Validation Module') 
    print('*'*64)
    print('Execututing Instant Tests...')
    for items in _instant_test_ids:
        url = f'{BASE_URL}/v7/tests/{items}/run'
        result = requests.post(url, headers=HEADERS, verify=False)
    print('Gathering results... This takes about 15-20 seconds')
    time.sleep(30) 
    for items in _instant_test_ids:
        print('*'*64)
        rurl = f'{BASE_URL}/v7/test-results/{items}/http-server'
        result = requests.get(rurl, headers=HEADERS, verify=False)
        result = json.loads(result.text)
        for items in result["results"]:
            print(f'Test Target: {result["test"]["url"]}')
            print(f'Test Agent: {items["agent"]["agentName"]}')
            print(f'Test Date: {items["date"]}')
            if items['errorType'] == 'HTTP':
                print(f'{bcolors.FAIL}Test Errors: {items["errorType"]}{bcolors.ENDC}')
            else:
                print(f'{bcolors.OKGREEN}Test Errors: {items["errorType"]}{bcolors.ENDC}')
        x = input('hit the enter key to see more results')
def main():
    os.system('clear')
    args = parser()
    if args.pre:
        pre_change()
    if args.post:
        post_change()   
main()
