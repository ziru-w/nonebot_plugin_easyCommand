import json
from os.path import dirname
from nonebot.adapters.onebot.v11 import Bot,MessageEvent, GroupMessageEvent,PrivateMessageEvent,MessageSegment
from nonebot import  on_regex, on_command, logger,get_driver,get_bot
from .utils import getCommandStartList,parseTimeData,path,matchText,addCommand,readReplyTextJson,parseText,getTime,writeFile,getExist,parseMsg
import nonebot_plugin_apscheduler
# 根据配置的参数，注册定时任务,每天发送

from nonebot.params import Arg, CommandArg
from nonebot.adapters import Message

scheduler=nonebot_plugin_apscheduler.scheduler
commandStartList=getCommandStartList()
superList=list(get_driver().config.superusers)
# content={
#     superList[0]:{
#         "测试":{
#             'time':['0','9','0'],
#             'content':'测试',
#             'type':'private',
#             'id':int(superList[0]),
#             "jobId":getTime()
#         }
#     }
# }
content={}
schedulerInfoPath=dirname(__file__)+'/schedulerInfo.json'
schedulerInfo=readReplyTextJson(schedulerInfoPath,content)
print(content)
async def sendEveryday(content,sendID,type):
    message=parseText(content)
    if type=='group':
        await get_bot().send_group_msg(group_id=sendID, message=message)
    elif type=='private':
        await get_bot().send_private_msg(user_id=sendID, message=message)
    return

for infos in schedulerInfo.values():
    for infosTitle in infos.keys():
        info=infos[infosTitle]
        time=info['time']
        scheduler.add_job(sendEveryday, "cron", hour=time[0], minute=time[1],second=time[2],args=[info['content'],info['id'],info['type']],id=info['jobId'])


reScheduler=on_command("注册定时",aliases={"删除定时"},block=True)
@reScheduler.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text()
    commandText=getExist('',text,argsText)
    if "注册定时" in commandText:
        time,title,content=str(args).strip().split(maxsplit=2)
        if schedulerInfo.get(event.get_user_id())==None:
            schedulerInfo[event.get_user_id()]={}
        tempInfo=schedulerInfo[event.get_user_id()].get(title)
        if tempInfo!=None:
            await reScheduler.send('请先删除定时任务{}:{}'.format(title,tempInfo))
            return
        time=time.split('.')
        isSuper=event.get_user_id() in superList
        errorData=parseTimeData(time,isSuper)
        if errorData!=-1:
            await reScheduler.send('{}中，第{}个数据{}非法，或过于危险，注册失败'.format(time,errorData,time[errorData]))
            return
        timeNum=len(time)
        if timeNum<3:
            time=time+['0','0','0'][:3-timeNum]
        print(time)
        if isinstance(event,GroupMessageEvent):
            msgType='group'
            tempInfo={'time':time,'content':content,'type':msgType,'id':event.group_id,'jobId':getTime()}
        else:
            msgType='private'
            tempInfo={'time':time,'content':content,'type':msgType,'id':event.user_id,'jobId':getTime()}

        schedulerInfo[event.get_user_id()][title]=tempInfo
        scheduler.add_job(sendEveryday, "cron", hour=time[0], minute=time[1],args=[tempInfo['content'],tempInfo['id'],tempInfo['type']],id=tempInfo['jobId'])
        writeFile(schedulerInfoPath,schedulerInfo)
        await reScheduler.send('已注册:\n{}'.format(tempInfo))
    else:
        title=str(args).strip()
        if schedulerInfo.get(event.get_user_id())==None or schedulerInfo[event.get_user_id()].get(title)==None:
            await reScheduler.send('不存在哦')
            return
        tempInfo=schedulerInfo[event.get_user_id()][title]
        scheduler.remove_job(tempInfo['jobId'])
        del schedulerInfo[event.get_user_id()][title]
        writeFile(schedulerInfoPath,schedulerInfo)
        await reScheduler.send('已删除:\n{}'.format(tempInfo))

replyTextJson = readReplyTextJson()

replyTextKeyList =list(replyTextJson.keys())
cqList=[]
# 默认不开放群无起始符命令，且不记录，为管理员游戏做
addLiaotian = on_command('添加命令',aliases={"删除命令","查看命令","允许命令","结束命令","获取CQ"}, block=True)
@addLiaotian.handle()
async def _(bot: Bot, event: MessageEvent,args: Message = CommandArg()):
    # answer=chat_by_Turing(plaintext)
    text=event.get_plaintext().strip()
    argsText=args.extract_plain_text()
    commandText=getExist('',text,argsText)
    argsText=str(args).strip()
    if isinstance(event,GroupMessageEvent):
        id=event.group_id
    elif isinstance(event,PrivateMessageEvent):
        id=event.user_id
    else:
        return
    uid=event.get_user_id()
    if '获取CQ' in commandText:
        if event.user_id not in cqList:
            cqList.append(event.user_id)
            await addLiaotian.send('授权成功')
        else:
            cqList.remove(event.user_id)
            await addLiaotian.send('已取消授权')
        return
    if '删除' in commandText:
        with open(path,'r',encoding='utf-8') as fp:
            replyTextJson = json.loads(fp.read())
        if argsText=='#+-*/真的啦已经确认过啦' and uid==superList[0]:
            with open(path,'w',encoding='utf-8') as fp:
                json.dump({},fp,ensure_ascii=False)
            await addLiaotian.send('已删除'+argsText)
            return
        if argsText in replyTextKeyList and int(uid)==replyTextJson[argsText]['creatorId']:
            del replyTextJson[argsText]
            with open(path,'w',encoding='utf-8') as fp:
                json.dump(replyTextJson,fp,ensure_ascii=False)
            await addLiaotian.send('已删除'+argsText)
        return
    if '查看' in commandText:
        # with open(path,'r',encoding='utf-8') as fp:
        #     replyTextJson = json.loads(fp.read())
        if '全' in argsText and uid in superList:
            await addLiaotian.send('正在绘制图片，请稍等。。。')
            msg=await parseMsg(commandText,'列表:\n{}'.format(replyTextKeyList).replace("', '",'\t'),isText=0)
            await addLiaotian.finish(msg)
        else:
            with open(path,'r',encoding='utf-8') as fp:
                replyTextJson = json.loads(fp.read())
            commandList=[]
            for title in replyTextJson.keys():
                if replyTextJson[title]['creatorId']==int(uid):
                    commandList.append(title)
            msg=await parseMsg(commandText,'列表:\n{}'.format(commandList).replace("', '",'\t'),isText=1)
            await addLiaotian.finish(msg)
        return
    if '允许' in commandText and uid in superList:
        existKey=(id in allowGroupList)
        if not existKey:
            allowGroupList.append(id)
            await addLiaotian.send('允许{}'.format(not existKey))
        else:
            await addLiaotian.send('早已允许{}'.format(existKey))
        return
    if '结束' in commandText and event.get_user_id() in superList:
        existKey=(id in allowGroupList)
        if existKey:
            allowGroupList.remove(id)
            await addLiaotian.send('结束{}'.format(existKey))
        else:
            await addLiaotian.send('早已结束{}'.format(not existKey))
        return
    if '添加' in commandText:
        try:
            # if plaintext=='':
            #     await addLiaotian.send('按格式好好输入')
            #     return
            command,reply=argsText.split(maxsplit=1)
            print(command,reply)
            replyText=addCommand(command,reply,replyTextKeyList,event.user_id)
            await addLiaotian.send(replyText)
            # await easyCommand.send(chat_by_Turing(plaintext))
        except Exception as res:
            print(res)
            await addLiaotian.send('按格式好好输入{}'.format(res))
        return



allowGroupList=[]
# GroupMessageEvent,PrivateMessageEvent
# 群聊@、白名单 /且全部匹配 匹配回复，私聊不加起始符匹配回复或加且全部匹配，默认起始符长度都是1,其他都不认
easyCommand = on_regex('.{1,100}', block=True, priority=99)
@easyCommand.handle()
async def _(bot: Bot, event: MessageEvent):
    # answer=chat_by_Turing(plaintext)
    plaintext=str(event.get_message()).strip()
    print(plaintext)
    if plaintext=='':
        return
    if event.user_id in cqList:
        if '[CQ:' in plaintext:
            await easyCommand.send('CQ如下:\n{}'.format(plaintext))
        else:
            await easyCommand.send('非CQ如下:\n{}'.format(plaintext))
        cqList.remove(event.user_id)
        return
    # try:
    if isinstance(event,GroupMessageEvent):
        gid=event.group_id
        uid=event.user_id
        if event.to_me==True or gid in allowGroupList or uid in allowGroupList:
            plaintext=plaintext.strip()
        elif plaintext[0] in commandStartList:
            plaintext=plaintext[1:]
            if plaintext not in replyTextKeyList:
                return
        else:
            return
    elif isinstance(event,PrivateMessageEvent):
        if plaintext[0] in commandStartList:
            plaintext=plaintext[1:]
            if plaintext not in replyTextKeyList:
                return
    print(plaintext,1)
    
    replyText=matchText(plaintext)
    if replyText=='':
        logger.info('匹配结果空')
        return
    
    await easyCommand.send(replyText)
        # await easyCommand.send(chat_by_Turing(plaintext))
    # except Exception as res:
    #     print(res)


 


## 直接匹配回复,起始符默认1
# easyCommand = on_command('你好', aliases=replyTextKeySet,block=True, priority=100)
# @easyCommand.handle()
# async def _(bot: Bot, event: MessageEvent):
#     plaintext=event.get_plaintext().strip()[1:]
#     try:
#         replyText=matchText(plaintext)
#         if replyText=='':
#             print('匹配结果空')
#             return
#         await easyCommand.send(replyText)
#         # await easyCommand.send(chat_by_Turing(plaintext))
#     except Exception as res:
#         print(res)
