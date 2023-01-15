

from datetime import datetime,timedelta
from time import sleep,time
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
import re
import json
from os.path import dirname,exists
from nonebot_plugin_txt2img import Txt2Img

path=dirname(__file__) +'/reply.json'
cdTime=2

def getTime():
    sleep(0.00001)
    content=time()
    content=str(content)
    return content

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

def addCommand(plaintext,inText,replyTextJson,creatorId=-1):
    replyKey='reply'
    creatorIdKey="creatorId"
    datetimeKey='datetime'
    #输入
    if inText!='':
        plaintext=plaintext[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
        inText=inText[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
        plaintext=parseImage(plaintext)
        replyTextJson[plaintext]={replyKey:inText,creatorIdKey:creatorId,datetimeKey:str(datetime.now() - timedelta(minutes=10))}
        return '{}:\n{}'.format(plaintext,replyTextJson[plaintext][replyKey])
    return '怪'


def parseImage(text):
    urlList=re.findall('\[CQ:image,file=.+?,url=(http.+?)]',text)
    if len(urlList)!=0:
        for url in urlList:
            text=text.replace(url,'')
    return text
def cd(reply):
    if  reply!=None:
        print(reply['datetime'])
        old=datetime.strptime(reply['datetime'],"%Y-%m-%d %H:%M:%S.%f")
        now=datetime.now()
        if (now-old).seconds<cdTime:
            return 'cd冷却中'
        else:
            reply['datetime']=str(now)
            return ''
    return ''
replyTextJson=readReplyTextJson()
def matchText(plaintext:str,replyTextJson,keyLen=3):
    # print(replyTextJson)
    # replyTextJson=readReplyTextJson()
    
    print(replyTextJson.get(plaintext))
    #输出
    # print(plaintext,'amp;')
    plaintext=plaintext[:400].replace('amp;','').replace('&#91;','[').replace('&#93;',']')
    # print(plaintext)
    replyText=''
    creatorIdKey="creatorId"
    # print(replyTextJson.get(plaintext))
    # print(plaintext,62)
    plaintext=parseImage(plaintext)
    if replyTextJson.get(plaintext)==None:
        for replyKey in replyTextJson.keys():
            if plaintext in replyKey and len(plaintext)*2>=len(replyKey) and len(plaintext)>=keyLen:#键长>=3，且占比>=比较键长1/2
                plaintext=replyKey
                break
    if cd(replyTextJson.get(plaintext))=='cd冷却中':
        return 'cd冷却中'
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



def parseText(replyText:str,maxImage=10):#免得图像太多，费流量
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
    commandText=wholeMessageText[::-1].replace(argsText[::-1],'',1)[::-1].strip()
    if plainCommandtext=='':
        return commandText
    else:
        return plainCommandtext in commandText



def parseTimeArea(inputTime,timeType):
    if timeType=='h':
        if inputTime>24 or inputTime<0:
            return False
    else:
        if inputTime>59 or inputTime<0:
            return False
    return True

def parseNum(inputTime:str,timeType:str,cornType):
    '1,*/2,0-59,*'
    if timeType==0:
        timeType='h'
    else:
        timeType='noH'
    if cornType==0:
        inputTime=int(inputTime)
        if not parseTimeArea(inputTime,timeType):
            return False
        return str(inputTime)
    elif cornType==1:
        inputTime=int(inputTime[2:])
        if inputTime<1:
            return False
        return '*/{}'.format(inputTime)
    elif cornType==2:
        inputTime=inputTime.split('-')
        temp=''
        for index,tempi in enumerate(inputTime):
            if not parseTimeArea(inputTime[index],timeType):
                return False
            temp=temp+inputTime[index]+'-'
        return temp[:-1]
    return inputTime


def parseTimeData(time:list,isSuper:False):
    pattern=["^[0-9]{1,2}$", "^[*][/][0-9]{1,2}$","^[0-9]{1,2}-[0-9]{1,2}$","^[*]$"]
    print(time)
    errorData=-1
    for i,inputTime in enumerate(time):
        for cornType,patterni in enumerate(pattern):
            select=re.match(patterni,inputTime)
            if select:
                isCorrect=parseNum(inputTime,i,cornType)
                if not isCorrect:
                    errorData=i
                    return errorData #收束数据超限
                time[i]=isCorrect
                break # 真，结束循环
            if (cornType==0 and not isSuper) or cornType+1==len(pattern): # 成功即break,故至此者非第一个匹配非超管F或最后一轮仍未break，判错
                errorData=i
                return errorData #收束未匹配
    return errorData # 全成功


async def parseMsg(commandText,resMsg,font_size = 32,isText=1):
    if len(resMsg)<=300 and isText==1:
       return resMsg
    else:
        title = commandText
        img = Txt2Img(font_size)
        pic = img.save(title, resMsg)
        return MessageSegment.image(pic)


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
