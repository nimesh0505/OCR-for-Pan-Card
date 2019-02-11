import cv2
import pytesseract
import nltk
import re
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pymongo import MongoClient


def filterOut(d_list):
  empty_free = d_list
  empty_free = list(filter(str.strip,empty_free))
  a=[y.strip('~!@#$%^&*()=+ "|') for y in empty_free]
  empty_free = a
  return empty_free

def storeDB(j_details):
  myclient = MongoClient("mongodb://127.0.0.1:27017")
  db = myclient.pan_cardDB
  if(db.panDetails.count()==0):
    db.panDetails.insert_one(dict(j_details))
  else:
    db.panDetails.update({"pan-number":j_details["pan-number"]},{"$set":{"name":j_details["name"],"fathers-name":j_details["fathers-name"],"DOB":j_details["DOB"]},},upsert=True)  



def fetchDetail(d_tuple):
  panD = dict()
  global flag
  flag = 0
  d_list = np.array(d_tuple)
  for i in range(len(d_list)):
    #CHECKING THE FIRST CONDITION
    if(len(d_list)!=i):
      if(d_list[i][0].find("numb" or "num" or "account")!=-1):

        flag+=1
        if((d_list[i+1][1]=='NN' or d_list[i+1][1]=='VBD') and len(d_list[i+1][0])==10):
          #pan number will be added first
          panD['pan-number'] = str(d_list[i+1][0]).upper()
          flag+=1
        #CHECKING THE SECOND CONDITION     
      if(d_list[i][0].find("income" or "tax" or "department" or "gov" or "india" or "incometaxdepartment" or "income tax department")!=-1):
        flag+=1
        if(d_list[i+1][1]==('NN' or 'NNP' or 'NNPS')):
          flag+=1
          panD['name'] = str(d_list[i+1][0]).upper()
          if((d_list[i+2][0])!=None and d_list[i+3][0]!=None):
              flag+=1
              panD['fathers-name']=str(d_list[i+2][0]).upper()
              if(d_list[i+3][1]=='CD'):
                flag+=1
                panD['DOB']=str(d_list[i+3][0])
  if(flag==6):
    storeDB(panD)
    return ("----Data sucessfully stored in the Database----")

  else:
    plt.axis("off")
    plt.title("SampleImage")
    plt.show(plt.imshow(cv2.cvtColor(cv2.imread('5.jpg'),cv2.COLOR_BGR2RGB)))
    return ("---Data could  not be stored ,Unclear scanned doc can be a reason")



def extractUnorganisedText(im):
  text = pytesseract.image_to_string(im,config='--oem 1 --psm 3')
  store_text = text.lower()
  lis=store_text.split('\n')
  return store_text,lis    


print("-----The Image of size of Doc should be 500x350 and the scanned doc should be in jpg format-----")

#path of image
imPath = "2.jpg"
im = cv2.imread(imPath,cv2.COLOR_BGR2GRAY)
size = im.shape
height = size[0]
width = size[1]


if((height>=300) and (width>=500)):
  try:
    text,text_list=extractUnorganisedText(im_one)
    temp_list = filterOut(text_list)
    finalOCR = nltk.pos_tag(temp_list)
    result= fetchDetail(finalOCR)
    print(result)
  except(Exception):
    print("Error in doc,Unclear scanned doc can be a reason!")  
else:
  print("Size is Low !")  

