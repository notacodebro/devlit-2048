#!/opt/homebrew/bin/python3
import pyfiglet
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
    material = open('.config', 'r')
except FileNotFoundError:
    print('!!!configuration file missing, create it please!!!!')
    exit(0)
material =  base64.b64decode(material.read()).decode("utf-8").strip()
HEADERS = {'Content-Type' : 'application/json', 'Authorization' : f'Bearer {material}'}

def fig(text, style='mini', color="HEADER"):
    text = pyfiglet.figlet_format(text, font=style)
    print(f'{getattr(bcolors, color)}{text}{bcolors.ENDC}')


def gather_test_results(testid):
    url = f'{BASE_URL}/v7/test-results/{testid}/http-server'
    result = requests.get(url, headers=HEADERS, verify=False)
    result = json.loads(result.text)
    return(result)

def internet_insights():
    provider_data = {
        "window" : "1d",
        "providerName": ["Century Link", "Microsoft", "NTT", "Cogent", "Tata"]
    }
    url = f'{BASE_URL}/v7/internet-insights/outages/filter'
    result = requests.post(url, headers=HEADERS, json=provider_data, verify=False)
    result = json.loads(result.text)

def pre_change():
    _current_test_ids = ['4805920', '4805922', '4805928'] # These ID's need to be added prior to execution 
    print(f'{bcolors.WARNING}Pre-Change Module{bcolors.ENDC}') 
    internet_insights()
    for items in _current_test_ids:
        result = gather_test_results(items)
        printer(result)

    
def post_change():
    _instant_test_ids = ['7195415', '7195422', '7195425']
    print(f'{bcolors.WARNING}Post-Change Module{bcolors.ENDC}') 
    print('*'*64)
    print('Execututing Instant Tests: ', end="", flush=True )
    for items in _instant_test_ids:
        url = f'{BASE_URL}/v7/tests/{items}/run'
        requests.post(url, headers=HEADERS, verify=False) 
    print(f'{bcolors.OKGREEN} Complete{bcolors.ENDC}')
    print('Gathering results(takes ~20 seconds): ', end="", flush=True )
    time.sleep(25)
    print(f'{bcolors.OKGREEN} Complete{bcolors.ENDC}')
    time.sleep(5)
    for items in _instant_test_ids:
        result = gather_test_results(items)
        printer(result)

def printer(result):
    error_count = 0
    print('*'*64)
    print(f'Test Name: {result["test"]["testName"]}')
    print(f'{bcolors.OKCYAN}Test Target: {result["test"]["url"]}{bcolors.ENDC}')
    print('*'*64)
    print('Results')
    print(f'Test Date: {result["results"][0]["date"]}')
    #print(result)
    for items in result['results']:
        print(f'Test Agent: {items["agent"]["agentName"]}')
        print(f'Test Errors: {bcolors.OKGREEN if items["errorType"] == "None" else bcolors.FAIL}{items["errorType"]}{bcolors.ENDC}')
        print(f'Response Code: {bcolors.OKGREEN if items["responseCode"] == 200 else bcolors.FAIL}{items["responseCode"]}{bcolors.ENDC}')
        print(f'Total Connect Time: {items["connectTime"]}')
        print('*'*32)
        if items["responseCode"] != 200: error_count = error_count + 1
    print('*'*64)
    if error_count >= 1:
        fig('Site Health is Compromised', "standard", "FAIL")
    print('*'*64)
    x = input('Hit enter to continue')
           
def parser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('-pre', help='pre-validation module', required=False, action='store_true')  
    _parser.add_argument('-post', help='post-validation module', required=False,action='store_true') 
    args = _parser.parse_args() 
    return args 

def main():
    os.system('clear')
    fig(".  :  l  : .  :  l  :  .\nChange Validation Tool")
    args = parser()
    if args.pre:
        pre_change()
    if args.post:
        post_change()   
main()
