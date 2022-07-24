

from datetime import datetime
from time import sleep,time
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
import re
import json
from os.path import dirname,exists
path=dirname(__file__) +'/reply.json'


def getTime():
    sleep(0.001)
    content=time()
    content=str(content)
    return content

def getCommandStartList(n='')->list:
    command_start=list(get_driver().config.command_start)
    if len(command_start)==0:
        command_start=['']
    else:
        if n!='':
            command_start=command_start[:n]
    return command_start
    
def parseDifferentCommandStart(text):
    lenght=len(getCommandStartList()[0])
    if lenght==0:
        text='/'+text
    else:
        text='/'+text[lenght:]
    return text

def readReplyTextJson(path=path,content={}):
    if not exists(path):
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(content,fp,ensure_ascii=False)
    with open(path,'r',encoding='utf-8') as fp:
        replyTextJson = json.loads(fp.read())
    return replyTextJson
def writeFile(path,content):
    with open(path,'w',encoding='utf-8') as fp:
        json.dump(content,fp,ensure_ascii=False)

def addCommand(plaintext,inText,replyTextKeyList:list,creatorId=-1):
    replyKey='reply'
    creatorIdKey="creatorId"
    datetimeKey='datetime'
    #输入
    if inText!='':
        replyTextJson=readReplyTextJson()
        plaintext=plaintext[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
        inText=inText[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
        replyTextJson[plaintext]={replyKey:inText,creatorIdKey:creatorId,datetimeKey:str(datetime.now())}
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(replyTextJson,fp,ensure_ascii=False)
        replyTextKeyList.append(plaintext)
        return '{}:\n{}'.format(plaintext,replyTextJson[plaintext][replyKey])
    return '怪'


def matchText(plaintext:str,creatorId=-1):
    replyTextJson=readReplyTextJson()
    #输出
    # print(plaintext,'amp;')
    plaintext=plaintext[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
    # print(plaintext)
    replyText=''
    creatorIdKey="creatorId"
    
    # print(replyTextJson.get(plaintext))
    # print(plaintext,62)
    if replyTextJson.get(plaintext)==None:
        for replyKey in replyTextJson.keys():
            if plaintext in replyKey and len(plaintext)*2>=len(replyKey) and len(plaintext)>=3:
                plaintext=replyKey
                break
    
    if replyTextJson.get(plaintext)==None:
        return replyText
    replyText=replyTextJson[plaintext]['reply']
        
    return parseText(replyText)
    # if '[CQ:image,' in replyText:
    #     urlList=re.findall('(http.+?)]',replyText)
    #     if len(urlList)!=0:
    #         return MessageSegment.image(urlList[0])
    # if '[CQ:face,id=' in replyText:
    #     faceList=re.findall('[CQ:face,id=([\d]{1,4})]',replyText)
    #     if len(faceList)!=0:
    #         return MessageSegment.face(faceList[0])
    # return '{}:\n{}'.format(plaintext,replyText)



def parseText(replyText:str):
    maxImage=10
    msg=''
    print(time())
    if '[CQ:' not in replyText:
        pass
    else:
        urlList=re.findall('\[CQ:image,file=.+?,url=(http.+?)]',replyText)
        if len(urlList)!=0:
            cqList=re.findall('\[CQ:image,file=.+?,url=http.+?]',replyText)[:maxImage]
            for i,temp in enumerate(cqList):
                temp=replyText.split(temp,maxsplit=1) 
                msg+=temp[0]+MessageSegment.image(urlList[i])
                print(msg)
                replyText=temp[1]
            msg+=replyText
            print(time())
            return msg
        faceList=re.findall('\[CQ:face,id=([\d]{1,4})]',replyText)
        if len(faceList)!=0:
            cqList=re.findall('\[CQ:face,id=[\d]{1,4}]',replyText)[:maxImage]
            replyText=replyText
            for i,temp in enumerate(cqList):
                temp=replyText.split(temp,maxsplit=1) 
                msg+=temp[0]+MessageSegment.face(faceList[i])
                replyText=temp[1]
            msg+=replyText
            return msg
        forwardList=re.findall('\[CQ:forward,id=(.{30,100})]',replyText)
        if len(forwardList)!=0:
            cqList=re.findall('\[CQ:forward,id=.{30,100}]',replyText)[:maxImage]
            replyText=replyText
            for i,temp in enumerate(cqList):
                temp=replyText.split(temp,maxsplit=1) 
                msg+=temp[0]+MessageSegment.forward(forwardList[i])
                replyText=temp[1]
            msg+=replyText
            return msg
    return msg+replyText

def getExist(plainCommandtext:str,wholeMessageText:str,argsText:str):
    commandText=wholeMessageText.replace(argsText,'').strip()
    if plainCommandtext=='':
        return commandText
    else:
        return plainCommandtext in commandText


def parseTimeArea(x,i):
    if i=='h':
        if x>24 or x<0:
            return False
    else:
        if x>59 or x<0:
            return False
    return True

def parseNum(x:str,i:str,op):
    '1,*/2,0-59,*'
    if i==0:
        i='h'
    else:
        i='noH'
    if op==0:
        x=int(x)
        if not parseTimeArea(x,i):
            return False
        return str(x)
    elif op==1:
        x=int(x[2:])
        if x<1:
            return False
        return '*/{}'.format(x)
    elif op==2:
        x=x.split('-')
        temp=''
        for index,tempi in enumerate(x):
            if not parseTimeArea(x[index],i):
                return False
            temp=temp+x[index]+'-'
        return temp[:-1]
    return x


def parseTimeData(time:list,isSuper:False):
    pattern=["^[0-9]{1,2}$", "^[*][/][0-9]{1,2}$","^[0-9]{1,2}-[0-9]{1,2}$","^[*]$"]
    print(time)
    errorData=-1
    for i,x in enumerate(time):
        for op,patterni in enumerate(pattern):
            select=re.match(patterni,x)
            if select:
                isCorrect=parseNum(x,i,op)
                if not isCorrect:
                    errorData=i
                    return errorData #收束数据超限
                time[i]=isCorrect
                break # 真，结束循环
            if (op==0 and not isSuper) or op+1==len(pattern): # 成功即break,故至此者非第一个匹配非超管F或最后一轮仍未break，判错
                errorData=i
                return errorData #收束未匹配
    return errorData # 全成功

# def parseTimeData(time:list,isSuper:False):
#     # patternH="^[0-9]$|^[1][0-9]|^[2][0-4]$" 
#     # pattern="^[0-9]$|^[1-5][0-9]$" 
#     # pattern1 = "^[*][/][1-9]$"

#     # pattern="^[0-9]{1,2}$" 
#     # pattern1 = "^[*][/][0-9]{1,2}$"
#     # # pattern2H="^[0-9]|^[1][0-9]|^[2][0-4]-[0-9]$"
#     # pattern2="^[0-9]{1,2}-[0-9]{1,2}$"
#     # pattern3="^[*]$"
#     pattern=["^[0-9]{1,2}$", "^[*][/][0-9]{1,2}$","^[0-9]{1,2}-[0-9]{1,2}$","^[*]$"]
#     print(time)
#     errorData=-1
#     for i,x in enumerate(time):
#         for op,patterni in enumerate(pattern):
#             if op>0 and not isSuper:
#                 break
#             select=re.match(patterni,x)
#             if select:
#                 op=0#'范围正确'
#                 if not parseNum(x,i,op):
#                     errorData=i
#                     break
#                 continue

#         if isSuper:
#             select=re.match(pattern1,x)
#             if select:
#                 op=1#'范围正确'
#                 if not parseNum(x,i,op):
#                     errorData=i
#                     break
#                 continue
#             select=re.match(pattern2,x)
#             if select:
#                 op=2#'范围正确'
#                 if not parseNum(x,i,op):
#                     errorData=i
#                     break
#                 continue
#             select=re.match(pattern3,x)
#             if select:
#                 op=3#'范围正确'
#                 if not parseNum(x,i,op):
#                     errorData=i
#                     break
#                 continue   
#         #收束所有错误
#         errorData=i
#     return errorData
