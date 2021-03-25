
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import pandas as pd
import numpy as np
import yaml
import logging
import warnings
warnings.filterwarnings('ignore')

import os



def same_as_data(userinput,usrname, email, mobile, useradd):
    
    userinput = userinput.lower()
    usrname = usrname.lower()
    email = email.lower()
    userAdd = useradd.lower()
    
    userinput = userinput.replace(userAdd,"")
    userinput = userinput.replace(usrname,"")
    userinput = userinput.replace(email, "")
    userinput = userinput.replace(mobile,"")

    item_list1=[]
    item_list2=[]
        
    # re_str = userinput[0]
    # add_str = re.findall('(.*\w\s)\d',re_str)[0]
    
    # indx = re_str.find(add_str)+len(add_str)
    # add = re_str[indx:]
    # userinput[0] = add_str
   
    user_list = re.split(r'\s*[,\t\n]\s*', userinput)
    while("" in user_list): 
        user_list.remove("") 
    
    for i in range(len(user_list)):

        if user_list[i].strip()[0].isdigit()==True:
            item_list2.append(user_list[i])
        
        else:
            item_list1.append(user_list[i])
    return item_list1, item_list2 

def check(item_lst1, item_lst2):
    name_list=[]
    quant_list1=[]
    unit_list1=[]
    for element in item_lst1:
        try:
            value=re.findall('(\d.*)$',element)[0]
            index=element.find(value) #Get the index of digit
            name=element[:index]
            name_list.append(name) #appending name in list
            quant_unit=value
            value=re.findall(r'\d*[\d\,\.\/]',quant_unit)[0] #(.*\d)Last digit eg:500gm
            ind=quant_unit.find(value)+len(value)
            quant_list1.append(quant_unit[:ind])
            unit_list1.append(quant_unit[ind:])
        except:
            name_list.append(element)
            quant_list1.append('Not Provided')
            unit_list1.append('Not Provided')

    item2=[]
    for element in item_lst2:
        while(True):
            try:
                new_string=re.findall('(.*\w\s+)\d',element)[0] #check digit in the last of data after text and stop it
            except:
                item2.append(element)
                break
            index=element.find(new_string) + len(new_string) 
            item2.append(element[index:])
            element=new_string 

    # lst1=[]
    # item_name=[]

    units_al = ['G','L','M','GMS','GM','KGS','KG','PCS','PC','PINCH','GRAMS','GRAM','METERS','METER','MTRS','MTR','PONDS','BUNCHES','BEGS','BEG','PINCHES','PINCH', \
          'FEET','FOOT','UNITS','UNIT','POND','PKTS','PKT','PACKS','PACK','PIECES','PIECE','PECES','PECE','LTRS','LTR','BAGS','BAG','BUNCH','MOLA','CM','LT','ML','FT']
    units_all = [i.lower() for i in units_al]
    item2 = [j.lower() for j in item2]

    item_name=[]
    quant_list2 = []
    unit_list2 = []
    for element in item2:
        data=re.findall(r'\d*[\d\,\.\/]', element)[0]
        quant_list2.append(data)
        indes = element.find(data)+len(data)
        quant_units = element[indes:]
        qq = quant_units.strip()
        qq = qq.split(' ')
        item_ = []
        if len(qq)==1:
            item_name.append(qq[0])
            unit_list2.append(" ")
        else:
            if qq[0] in units_all:
                unit_list2.append(qq[0])
                a =" ".join(qq[1:])
                item_name.append(a)
            else:
                unit_list2.append(" ")
                b = " ".join(qq[0:])
                item_name.append(b)



    total_name=name_list+item_name
    total_quant=quant_list1+quant_list2
    total_unit=unit_list1+unit_list2
    return (total_name, total_quant, total_unit)


def create_df(a,b,c):
    df = pd.DataFrame(zip(a, b,c),columns =['ProductName', 'Quantity','Unit of measure'])
    df['ProductName'] = df['ProductName'].str.replace('[#,@,&,' ',-]', '')
    df['ProductName'] = df['ProductName'].str.strip()
    df['Quantity'] = df['Quantity'].str.strip()
    df['Unit of measure'] = df['Unit of measure'].str.strip()
    df['Order Number'] = np.random.randint(11111, 99999)
    df['User Name'] = ''
    df['Email ID']=''
    df['Mobile No']=''
    df['User Address']=''
    
    x=[]
    for i in range(1,len(df)+1):
        x.append(str(i).zfill(2))

    df['Order Line Number']=x 
    df['Error'] = ""
    return df

def enterUserInfo(df,usrname, email, mobile, useradd):
    if usrname or email or mobile:
        df.loc[0,['User Name']] = usrname
        df.loc[0,['Email ID']]=email
        df.loc[0,['Mobile No']]=mobile
    if useradd:
        df.loc[0,['User Address']]=useradd
    else:
        df.loc[0,['Error']] = 'Address not found'
    return df




def open_yml_file():
    
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #r'/workchat/grocery/data/nlulookups.yml'
    #print(dir_path)
    with open('/home/devendra/Music/grocery-main/data/nlulookups.yml') as file:
        try:
            yml_data=yaml.load(file)
        except yaml.YAMLError as exc:
            print('yml file not found')
        return yml_data
    
    
def get_product_data():
    data=open_yml_file()
    for i,k in enumerate(data['nlu']):
        if k['lookup']=='Item':
            lookup_item = re.sub('[^a-zA-Z0-9\n\.]', ' ', k['examples']).lower()
            
        elif k['lookup']=='UnitofMeasure':
            lookup_item_uom = re.sub('[^a-zA-Z0-9\n\.]', ' ', k['examples']).lower()
    lookup_items = lookup_item.split('\n')
    lookup_item_uoms = lookup_item_uom.split('\n')
    return lookup_items


def product_check(data):
    lookupItem = get_product_data()
    df=data
    prodname = df['ProductName'].str.lower()
    uom = df['Unit of measure'].str.lower()
    
    try:
        flag=0
        for i in (prodname):
            x=False
            flag+=1
            for j in range(len(lookupItem)):
            
                if i.strip()==lookupItem[j].strip():
                    x=True
                    break
            if x:
                df["Error"].iloc[flag-1]=df["Error"].iloc[flag-1]+''  
            else:
                df['Error'].iloc[flag-1]=df["Error"].iloc[flag-1]+',Product Not found'
    except:
        print('DataFrame Empty')
    return 0



def authorize_GoogleSheet():
    # Authorize google sheet
    try:
        scope=['https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/feeds']
        credsfile = '/home/devendra/Music/grocery-main/actions/anydesk_6.1.0-1_amd64.deb/chatsheetsapi-e10d830e42a5.json'
        cred=ServiceAccountCredentials.from_json_keyfile_name(credsfile, scope)
        gc=gspread.authorize(cred)
    except:
        logging.exception("Authrization not perform well")
    
    # Excess google sheet
    try:
        sh = gc.open('OrderManagement')  
        # worksheet = sh.get_worksheet(2)
        wks=sh.worksheet("Orders")
        # print(wks)
    except:
        print('Did not find Google Sheet')
    
    return wks


def insert_data_in_sheet(data):
    wks = authorize_GoogleSheet()
    df=data
    l=len(wks.col_values(1))
    # print(l)
    if l==0:
        head = ['Order Number','Order Line Number','User Name','Mobile No','ProductName','Quantity','Unit of measure','User Address','Email ID','Error']
        wks.insert_row(head, 1)
        l=l+1

    l=l+1
    for indx in range(df.shape[0]):
        c=df.iloc[indx]
        new_data=[str(c['Order Number']),c['Order Line Number'],c['User Name'],c['Mobile No'],c['ProductName'],c['Quantity'],c['Unit of measure'],c['User Address'],c['Email ID'],c['Error']]
        
        wks.insert_row(new_data, indx+l)
    return df['Order Number'][0]




def processorder(user_input,Username,EmailId,MobileNo,UserAddress):
    data, usrname, email, mobile, useradd = user_input, Username, EmailId, MobileNo, UserAddress
    x,y = same_as_data(data,usrname, email, mobile, useradd)
    a,b,c = check(x,y)
    df = create_df(a,b,c)
    df2 = enterUserInfo(df,usrname, email, mobile, useradd)
    product_check(df2)
    orderNum = insert_data_in_sheet(df2)
    # insert_data_in_UserSheet(usrname, email, mobile, useradd)
    
    return orderNum

user_input = input("input")
aa = input("name")
bb = input("email")
cc = input("mob")
dd = input("add")
processorder(user_input,aa,bb,cc,dd)

