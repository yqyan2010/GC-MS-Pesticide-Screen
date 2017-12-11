from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import date
from openpyxl import load_workbook
import time

""" Login First """
#login_url="http://environmental.puritylabsinc.com:8080/Purity/login_form"
#input_lst=soup.find_all("input") # Login token is saved in one "input" tag
#for i in range(0,len(input_lst)):
 #   if input_lst[i].has_attr("name")==True and input_lst[i]["name"]=="_authenticator":
        #token=input_lst[i]["value"]
  #  else:
   #     pass

""" Get Sample ID List"""
print(r'Only Works for Kirkman Samples with "DS-" IDs')
time.sleep(2)
sp_count=int(input('How many GC samples are you running?\n'))
sp_url_list=[]
sp_id_list=[]
sp_id=""
logic='no'
while logic.lower()== 'no':
    for i in range(0,sp_count):
        sp_id=str(input('Please Enter Sample ID: '))## Sample ID
        sp_id=sp_id.upper()
        sp_id_list.append(sp_id)
        sp_url="http://environmental.puritylabsinc.com:8080/Purity/clients/client-116/"+sp_id
        sp_url_list.append(sp_url)
    time.sleep(1)
    print('\nGC Samples:')
    print(sp_id_list)
    time.sleep(2)
    logic=str(input('\nDoes the above list contain all samples you want to run?\nYes or No\n'))

""" Get GC Method """
md=str(input("GC Method File Is EXP_:"))

""" Access Sample Web """
login_info={"__ac_name":"YYan","__ac_password":"Purity#1!"}
data=parse.urlencode(login_info)
asciidata=data.encode('ascii')
opener=request.build_opener()

""" //Function// """
""" Fn to get today date """
today=date.today().__str__()
yr_lg=today[0:4]
yr=today[2:4]
mon=today[5:7]
day=today[8:]

""" Fn to Get One Sample Info From Given URL (Name, Lot, BuB, Recieved Date) """
def Get_Sample_Info(url): ## We supply url link, function parses sp info
    res=opener.open(url,asciidata)
    soup=BeautifulSoup(res.read(),'html.parser')
    ## Get name, lot number, best used by
    sp_info=soup.find_all(name='input',attrs={'id':'ClientSampleID'})[0]['value']
    sp_info=sp_info.split()
    sp_lot=""
    sp_bub=""
    sp_name=""
    for item in sp_info:
        if item.lower().startswith('lot#'):
            sp_lot=item[4:] ## Lot Number
        elif item.lower().startswith('bub:'):
            sp_bub=item[4:] ## Sample best used by
        else:
            sp_name=sp_name+item+" " ## Sample name
        sp_name=sp_name.rstrip()
        ## Get received date
        sp_rec=soup.tr.contents[-2].span.string
        sp_rec=sp_rec.split()[0]
    return sp_name,sp_lot,sp_bub,sp_rec

""" Get A List of Sample Info """
sp_name_list=[]
sp_lot_list=[]
sp_bub_list=[]
sp_rec_list=[]
for url in sp_url_list:
    sp_name,sp_lot,sp_bub,sp_rec=Get_Sample_Info(url) # Run built in function
    sp_name_list.append(sp_name)
    sp_lot_list.append(sp_lot)
    sp_bub_list.append(sp_bub)
    sp_rec_list.append(sp_rec)

""" Build Sample Info data frame
    and write to .xlsx file """
df_sp=pd.DataFrame(data=None,index=sp_id_list)
df_sp["Name"]=sp_name_list
df_sp["Lot Number"]=sp_lot_list
df_sp["BuB"]=sp_bub_list
df_sp["Received Date"]=sp_rec_list

path=r"C:\Users\yyan\Documents\Data\Pesticide\Sequence_log.xlsx"
book=load_workbook(path)
writer=pd.ExcelWriter(path,engine='openpyxl')
writer.book=book
df_sp.to_excel(writer,sheet_name='Sheet2',na_rep="")

writer.save()

""" Create GC Sequence Data Frame """
## Start block of sequence ##
type_list=["QC","Calibration","QC","QC","Blank"]
vial_list=[1,4,5,6,1]
sample_list=["DCM","ICV","MB","LCS","DCM"]
dfile_list=["DCM_01","ICV_"+yr+mon+day,"MB_"+yr+mon+day,"LCS_"+yr+mon+day,"DCM_02"]
## Append Samle Block Sequence ##:
for i in range(0,len(sp_id_list)):
    type_list.append("Sample")
    vial_list.append(i+7)
    sample_list.append(sp_name_list[i])
    dfile_list.append(sp_id_list[i])
    type_list.append('Blank')
    vial_list.append(2)
    sample_list.append("rinse EtAc")
    dfile_list.append("EtAc_"+str(i+1))
## End Block of Sequence ##
type_list+=["Calibration","Blank","Blank"]
vial_list+=[4,2,1]
sample_list+=["CCV","rinse EtAc","DCM"]
dfile_list+=["CCV_"+yr+mon+day,"EtAc_"+str(i+2),"DCM_03"]

method_list=["EXP_"+md]*len(sample_list)
com_list=sample_list

df_seq=pd.DataFrame(data=None)
df_seq["Type"]=type_list
df_seq["Vial"]=vial_list
df_seq["Sample"]=sample_list
df_seq["Method"]=method_list
df_seq["DataFile"]=dfile_list
df_seq["Comment"]=com_list

""" Write GC Sequence to CSV File """
df_seq.to_csv("GC_sequence.csv",sep=',',na_rep='',index=False)

""" End of scripts """
