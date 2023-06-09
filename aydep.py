import time
import requests
from os import getenv
from time import sleep
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

username = getenv("USERNAME")
password = getenv("PASS")
ntfLvl = getenv("NOTIFIER_LEVEL")

token = ""

def auth():
    #region Step One
    loginHeaders={
        'Connection':'keep-alive',
        'sec-ch-ua':'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site':'none',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-User':'?1',
        'Sec-Fetch-Dest':'document',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9'
    }

    req = requests.get('https://aydep.ahievran.edu.tr/', headers=loginHeaders)
    newCookies= req.history[0].headers["Set-Cookie"][0:-8]
    print("newCookie: ",newCookies)   


    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    loginHeaders["Cookie"]=newCookies
    req1 = requests.get('https://aydep.ahievran.edu.tr/system/login', headers=loginHeaders, allow_redirects=False)
    
    token= req1.text.split("name=\"_token\" value=\"")[1].split("\"")[0]
    print("token: ",token)

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    authHeaders={
        'Connection':'keep-alive',
        'Cache-Control':'max-age=0',
        'sec-ch-ua':'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'Upgrade-Insecure-Requests':'1',
        'Origin':'https://aydep.ahievran.edu.tr',
        'Content-Type':'application/x-www-form-urlencoded',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-User':'?1',
        'Sec-Fetch-Dest':'document',
        'Referer':'https://aydep.ahievran.edu.tr/system/login',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9'
    }

    authHeaders["Cookie"]=newCookies

    authCredentials ={
        'username': f'{username}',
        'password': f'{password}',
        'login': '',
        '_token': f'{token}'
    }

    req2 = requests.post('https://aydep.ahievran.edu.tr/system/auth',headers=authHeaders, data=authCredentials,allow_redirects=False)
    
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    instutionHeaders={
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-User':'?1',
    'Sec-Fetch-Dest':'document',
    'sec-ch-ua':'"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile':'?0',
    'sec-ch-ua-platform':'"Windows"',
    'Referer':'https://aydep.ahievran.edu.tr/system/login',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en-US,en;q=0.9'
    }

    instutionHeaders["Cookie"]=f"{newCookies}; XSRF-TOKEN={token};"

    req3 = requests.get('https://aydep.ahievran.edu.tr/system/institutions',headers=instutionHeaders)


    #Changing Cookie
    authUri = req3.history[0].headers['Location']
    newCookie = req3.history[1].cookies.get_dict()
    return newCookie


    #endregion

def run():

    round = 0
    lstLenTable = 0
    lenTable = 0

    while True:
        try:
            cookie = auth()

            sessionId= cookie.get('PHPSESSID')
            sessionToken = cookie.get('XSRF-TOKEN')

            ntfHeaders = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57",
                "Cookie": f"PHPSESSID={sessionId}; XSRF-TOKEN={sessionToken};",
                "Connection": "keep-alive"
            }

            ntfHeaders2 = {
                "Content-Type": "application/json"
            }

            while True:
                req = requests.get('https://aydep.ahievran.edu.tr/n/home', headers=ntfHeaders)

                html = req.content
                soup = BeautifulSoup(html, 'html.parser')

                table = soup.find('table', {'class': 'table table-bordered senkronlarim'})
                tableLines = table.find_all('tr')

                lastLine = tableLines[-1]

                lessonName = lastLine.contents[1].contents[0]
                lessonDateAndTime = lastLine.contents[5].contents[0]
                ntfMsgContent = f"{lessonName} {lessonDateAndTime}"

                lenTable = tableLines.__len__()
                print(f"Table Length : {lenTable}")
                print(f"Last Table Length : {lstLenTable}")
                if lenTable != lstLenTable:

                    lstLenTable = lenTable
                    if round != 0:

                        notifyshHeaders = {
                            "tags":"loudspeaker",
                            "title": "Yaklasan Ders".encode('utf-8'),
                            "message": f"{ntfMsgContent}".encode('utf-8'),
                            "attachment_name": "favicon.ico",
                            "attachment_type": "image/x-icon",
                            "attachment_url": "https://tq.tahakara.dev/favicon.ico",
                            "click": "googlechrome://navigate?url=https://tq.tahakara.dev/aydep",
                            "priority": f"{ntfLvl}"
                        }

                        notif = requests.post('https://ntfy.sh/aydep', headers=notifyshHeaders)#me
                        print("\n\nNotification Sent\n\n")
                        sleep(30)

                
                print(f"\nRound : {round} Time:", time.time(),"\n")
                sleep(30)
                round += 1

        except Exception as e:
            print(e,"\n\n\nCookies Expired\n\n\n")

        

if __name__ == '__main__':
    run()


