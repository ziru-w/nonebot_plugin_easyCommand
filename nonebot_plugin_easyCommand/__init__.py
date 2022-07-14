import json
from nonebot.adapters.onebot.v11 import Bot,MessageEvent, GroupMessageEvent,PrivateMessageEvent,MessageSegment
from nonebot import  on_regex, on_command, logger,get_driver
from .utils import getCommandStartList,parseDifferentCommandStart,path,matchText,addCommand


with open(path,'r',encoding='utf-8') as fp:
    replyTextJson = json.loads(fp.read())

replyTextKeyList =list(replyTextJson.keys())
commandStartList=getCommandStartList()
superList=list(get_driver().config.superusers)
# 默认不开放群无起始符命令，且不记录，为管理员游戏做
addLiaotian = on_command('添加命令',aliases={"删除命令","查看命令","允许命令","结束命令"}, block=True)
@addLiaotian.handle()
async def _(bot: Bot, event: MessageEvent):
    # answer=chat_by_Turing(plaintext)
    plaintext=str(event.get_message()).strip()
    op=plaintext
    plaintext=parseDifferentCommandStart(plaintext)[5:].strip()
    uid=event.get_user_id()
    if '删除' in op[:3]:
        with open(path,'r',encoding='utf-8') as fp:
            replyTextJson = json.loads(fp.read())
        if plaintext in replyTextKeyList and int(uid)==replyTextJson[plaintext]['creatorId']:
            del replyTextJson[plaintext]
            with open(path,'w',encoding='utf-8') as fp:
                json.dump(replyTextJson,fp,ensure_ascii=False)
            await addLiaotian.send('已删除'+plaintext)
        return
    if '查看' in op[:3] and uid in superList:
        # with open(path,'r',encoding='utf-8') as fp:
        #     replyTextJson = json.loads(fp.read())
        await addLiaotian.send('列表\n{}'.format(replyTextKeyList)[:400])
        return
    if '允许' in op[:3] and uid in superList:
        if isinstance(event,GroupMessageEvent) and event.group_id not in allowGroupList:
            existKey=(event.group_id in allowGroupList)
            if not existKey:
                allowGroupList.append(event.group_id)
                await addLiaotian.send('允许{}'.format(not existKey))
            else:
                await addLiaotian.send('早已允许{}'.format(existKey))
        return
    if '结束' in op[:3] and event.get_user_id() in superList:
        if isinstance(event,GroupMessageEvent):
            existKey=(event.group_id in allowGroupList)
            if existKey:
                allowGroupList.remove(event.group_id)
                await addLiaotian.send('结束{}'.format(existKey))
            else:
                await addLiaotian.send('早已结束{}'.format(not existKey))
        return
    try:
        # if plaintext=='':
        #     await addLiaotian.send('按格式好好输入')
        #     return
        command,reply=plaintext.split()
        
        print(command,reply)
        replyText=addCommand(command,reply,replyTextKeyList,event.user_id)
        
        await addLiaotian.send(replyText)
        # await easyCommand.send(chat_by_Turing(plaintext))
    except Exception as res:
        print(res)
        await addLiaotian.send('按格式好好输入{}'.format(res))


allowGroupList=[]
# GroupMessageEvent,PrivateMessageEvent
# 群聊@、白名单 /且全部匹配 匹配回复，私聊不加起始符匹配回复或加且全部匹配，默认起始符长度都是1,其他都不认
easyCommand = on_regex('.{1,100}', block=True, priority=99)
@easyCommand.handle()
async def _(bot: Bot, event: MessageEvent):
    # answer=chat_by_Turing(plaintext)
    plaintext=event.get_plaintext().strip()
    try:
        if isinstance(event,GroupMessageEvent):
            gid=event.group_id
            if event.to_me==True or gid in allowGroupList:
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
        print(plaintext)
        replyText=matchText(plaintext)
        if replyText=='':
            logger.info('匹配结果空')
            return

        await easyCommand.send(replyText)
        # await easyCommand.send(chat_by_Turing(plaintext))
    except Exception as res:
        print(res)





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
