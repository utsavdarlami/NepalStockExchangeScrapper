import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import random
from dateutil import rrule, parser
from time import sleep
from datetime import date,datetime
import os


user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

titles=["S.N.","Traded Companies","No. Of Transaction","Max Price","Min Price","Closing Price","Traded Shares","Amount","Previous Closing","Difference Rs."]

class NepalStockScrap(object):
    
    datelist=[] 

    def __init__(self,from_date,to_date,stock_symbol=''):
        self.from_date = str(from_date)
        self.to_date = str(to_date)
        self.datelist = list(rrule.rrule(rrule.DAILY,dtstart=parser.parse(self.from_date),until=parser.parse(self.to_date)))
        self.stock_symbol = stock_symbol
        self.stock_data = self.get_csv_data()

    def get_csv(self):
        dfx = self.stock_data
        filename = "NepSE_"+str(self.from_date)+"_"+str(self.to_date)+"_"+str(self.stock_symbol)+".csv"
        dfx.to_csv(filename)

    def get_excel(self):
        dfx = self.stock_data
        filename = "NepSE_"+str(self.from_date)+"_"+str(self.to_date)+"_"+str(self.stock_symbol)+".xlsx"
        dfx.to_excel(filename)
    
    def get_json(self):
        pass
    
    def get_database(self):
        pass
    
    def get_csv_data(self):
        final_df = pd.DataFrame()
        print("......SCRAPPING DATA......")
        for date_input in self.datelist:
            sleep(1)
            real_date = date_input.date()
            main_url="http://www.nepalstock.com/main/todays_price/index/?startDate="+str(real_date)+"&stock-symbol="+self.stock_symbol+"&_limit=500"
            user_agent  =UserAgent()
            headers  = {'user-agent':random.choice(user_agent_list)}
            response = requests.get(main_url,headers,timeout=5)
            # sleep(2)
            page_source = response.content
            response.connection.close()

            main_soup = BeautifulSoup(page_source,'html.parser')
            table =  (main_soup.find('table',attrs={'class':'table table-condensed table-hover'}))

            tr_tags=(table.find_all('tr'))

            first_data = tr_tags[2].find('td')

            instant1_df = pd.DataFrame()
            aDic={}

            if(first_data.text)=="No Data Available!":
                print("\n No Data Available! For Date :" + str(real_date))
                aDic['Date']=real_date
                for t in titles:
                    aDic[t]=None
                    instant1_df = pd.DataFrame([aDic],columns=aDic.keys())
            else:
                for tr in tr_tags[2:-4]:
                    td_tags = tr.find_all('td')
                    aDic['Date']=real_date
                    for index,(t,td) in  enumerate(zip(titles,td_tags)):
                        aDic[t]=td.text.split('\n')[0]
                    df = pd.DataFrame([aDic],columns=aDic.keys())
                    instant1_df=pd.concat([instant1_df,df],ignore_index=True,axis=0,sort=False)
            final_df=pd.concat([final_df,instant1_df],ignore_index=True,axis=0,sort=False)
            final_df=final_df.drop('S.N.',1)
            sleep(2)
        return final_df

if __name__ == '__main__':  
    
    now_dt=datetime.now()
    date_now= now_dt.date()
    print("")
    stock_symbol=input("     * Stock-Symbol : ")
    from_date = input("     * From Date(yyyy-mm-dd) (leave empty for current date): (yyyy-mm-dd) =>")
    
    if from_date=='':
        from_date=str(date_now)
    
    to_date = input("     * To Date(yyyy-mm-dd) (leave empty for current date): (yyyy-mm-dd) => ")
    
    if to_date=='':
        to_date=str(date_now)

    print("")
    stockObj = NepalStockScrap(from_date,to_date,stock_symbol)
    q=False
    
    while q==False:
        print("")
        print("     1.Get CSV ::")
        print("     2.Get Excel ::")
        print("     3.Quit :: ")
        print("")

        choice = input("------>Option : ")
        print("")

        if choice=='1':
            stockObj.get_csv()
            pass
        elif choice=='2':
            stockObj.get_excel()
            pass
        elif choice=='3':
            print("")
            print("     Good Day with Scrapping...")
            print("")
            q=True
        else:
            print("")
            print("No Such Option..")
            print("")
    
