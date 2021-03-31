
import os
import yaml
import gspread
import warnings
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
warnings.filterwarnings('ignore')

def open_yml_file():
    with open(r'/workchat/grocery/data/google_sheets_config.yml') as file:
        try:
            Config_yml_file = yaml.load(file)
        except:
            print('yml file not found')
        return Config_yml_file

def authorize_google_sheet(yml_data):
 
    sheet_name = yml_data['sheet_ID']
    tab_name = yml_data['tab_name']

    # Authorize google sheet
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('/workchat/grocery/actions/gsheets/chatsheetsapi-e10d830e42a5.json', scope)
        client = gspread.authorize(creds)
    except:
        print("Google sheet Authrization not perform well")

    # Excess google sheet

    
    try:
        sheet = client.open(sheet_name)
        wks=[]
        for i in range(len(tab_name)):
            workshit = sheet.worksheet(tab_name[i])
            wks.append(workshit)
        
    except:
        print('Sheet didn"t find')
   
    return wks


def config_to_df(yml_data, wks):
    d=[]
    for i in range(len(wks)):
        data = pd.DataFrame(wks[i].get_all_records())
        d.append(data)
    df = pd.concat(d, axis=1)
    df.fillna('', inplace=True)

    lst = []
    for i, k in enumerate(yml_data):
        if i > 2:
            lst.append(yml_data[k]['lookup'])
    
    head1 = []
    for i in lst:
        if i in list(df):
            head1.append(i)
            
    sort_df = df.sort_values(by = head1)
    return sort_df


def to_nlulookup(sort_df, yml_data):
    
    line1 = "version: \"2.0\""
    line2 = ""
    line3 = "nlu:"
    line4 = ""


    
    with open(os.getcwd() + '/workchat/grocery/data/nlulookups.yml','w') as out:
        out.write('{}\n{}\n{}\n{}\n'.format(line1,line2,line3,line4))


    for i, k in enumerate(yml_data):
        if i > 1:
        
            line5 = "- lookup: " + k
            line6 = "  examples: |"
            line8 = "    - "
            temp_1 = 0
        

            for j in sorted(sort_df[yml_data[k]['lookup']].str.lower().unique()):
                temp_1 += 1
                if temp_1 == len(sort_df[yml_data[k]['lookup']].unique().tolist()): 
                  
                    if len(str(j).strip()) == 0 or isinstance(j, int or float):
                        line5 = ""
                        line6 = ""
                        line8 = ""

                    else:                    
                        line8 = line8 + str(j).strip() + '\n'
                else:
                    if temp_1>1:
                        line8 = line8 + str(j).strip() + "\n    - "
                

            with open(os.getcwd() + '/workchat/grocery/data/nlulookups.yml','a') as out:
                out.write('{}\n{}\n{}\n'.format(line5,line6,line8))
    return 0

def generate_lookup_file():
    yml_data=open_yml_file()
    worksheet = authorize_google_sheet(yml_data)
    df = config_to_df(yml_data, worksheet)
    df = df.astype(str)
    to_nlulookup(df, yml_data)
    temp = 'Successfully generated'
    return temp

generate_lookup_file()

