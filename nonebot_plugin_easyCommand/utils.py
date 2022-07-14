

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment
import re
import json
from os.path import dirname,exists
path=dirname(__file__) +'/reply.json'

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

def readReplyTextJson():
    if not exists(path):
        with open(path,'w',encoding='utf-8') as fp:
            json.dump({},fp,ensure_ascii=False)
    with open(path,'r',encoding='utf-8') as fp:
        replyTextJson = json.loads(fp.read())
    return replyTextJson

def addCommand(plaintext,inText,replyTextKeyList:list,creatorId=-1):
    replyKey='reply'
    creatorIdKey="creatorId"
    #输入
    if inText!='':
        replyTextJson=readReplyTextJson()
        inText=inText[:400]
        replyTextJson[plaintext]={replyKey:inText,creatorIdKey:creatorId}
        with open(path,'w',encoding='utf-8') as fp:
            json.dump(replyTextJson,fp,ensure_ascii=False)
        replyTextKeyList.append(plaintext)
        return '{}:\n{}'.format(plaintext,replyTextJson[plaintext][replyKey])
    return '怪'


def matchText(plaintext:str,creatorId=-1):
    replyTextJson=readReplyTextJson()
    #输出
    replyText=''
    replyKey='reply'
    creatorIdKey="creatorId"
    if replyTextJson.get(plaintext)==None:
        for replyKey in replyTextJson.keys():
            if plaintext in replyKey and len(plaintext)*2>=len(replyKey) and len(plaintext)>=3:
                plaintext=replyKey
                break
    if replyTextJson.get(plaintext)==None:
        return replyText
    
    replyText=replyTextJson[plaintext][replyKey]
    urlList=re.findall('\[CQ:image,file=.+?,url=(http.+?)]',replyText)
    if len(urlList)!=0:
        return MessageSegment.image(urlList[0])
    faceList=re.findall('\[CQ:face,id=([\d]{1,4})]',replyText)
    if len(faceList)!=0:
        return MessageSegment.face(faceList[0])
    # if '[CQ:image,' in replyText:
    #     urlList=re.findall('(http.+?)]',replyText)
    #     if len(urlList)!=0:
    #         return MessageSegment.image(urlList[0])
    # if '[CQ:face,id=' in replyText:
    #     faceList=re.findall('[CQ:face,id=([\d]{1,4})]',replyText)
    #     if len(faceList)!=0:
    #         return MessageSegment.face(faceList[0])
    # return '{}:\n{}'.format(plaintext,replyText)
    return '{}'.format(replyText)