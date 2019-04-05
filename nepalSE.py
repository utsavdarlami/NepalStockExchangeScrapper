import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import os
from dateutil import rrule, parser
from time import sleep
from datetime import date,datetime
import os

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
            sleep(2)
            real_date = date_input.date()
            main_url="http://www.nepalstock.com/main/todays_price/index/?startDate="+str(real_date)+"&stock-symbol="+self.stock_symbol+"&_limit=500"
            user_agent  =UserAgent()
            headers  = {'user-agent':user_agent.Chrome}
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
    