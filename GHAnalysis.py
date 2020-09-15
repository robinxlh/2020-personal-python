import json
import os
import argparse
import linecache
import gc
import multiprocessing
class Data:
    def __init__(self, dict_address: int = None, reload: int = 0):
        self.done=1
        self.done1=0
        if reload  == 1:
            self.__4Events4PerP = {}  # 关联人与事件数
            self.__4Events4PerR = {}  # 关联项目与事件数
            self.__4Events4PerPPerR = {}  # 关联人与项目与事件数
            self.__init(dict_address)
            with open('1.json', 'w', encoding='utf-8') as f:  # 初始化
                json.dump(self.__4Events4PerP, f)  # 写入
            with open('2.json', 'w', encoding='utf-8') as f:
                json.dump(self.__4Events4PerR, f)
            with open('3.json', 'w', encoding='utf-8') as f:
                json.dump(self.__4Events4PerPPerR, f)
        if dict_address is None and not os.path.exists('1.json') and not os.path.exists('2.json') and not os.path.exists('3.json'):     #要查却没文件
            raise RuntimeError('error: init failed')
        x = open('1.json', 'r', encoding='utf-8').read()    #打开
        self.__4Events4PerP = json.loads(x)     #解码json数据
        x = open('2.json', 'r', encoding='utf-8').read()
        self.__4Events4PerR = json.loads(x)
        x = open('3.json', 'r', encoding='utf-8').read()
        self.__4Events4PerPPerR = json.loads(x)

    def __init(self, dict_address: str):
        i=0
        pool = multiprocessing.Pool(processes=4)
        for root, dic, files in os.walk(dict_address):
            for f in files:
                pool.apply_async(self.fly, args=(f,dict_address,))
                # print(self.__4Events4PerP,'1')
        pool.close()
        pool.join()

    def fly(self,f,dict_address):
        self.done1+=1
        if f[-5:] == '.json':
            json_list = []  # 读入
            x = open(dict_address + '\\' + f,
                     'r', encoding='utf-8').read()
            str_list = [_x for _x in x.split('\n') if len(_x) > 0]
            # str_list = [_x for _x in x.split('\n') if len(_x) > 0]
            for i, _str in enumerate(str_list):  # 序号，每列字符
                try:
                    json_list.append(json.loads(_str))
                except:  # 注意
                    pass
            print(self.done1,i)
            i += 1
            self.solve(json_list)
            del x, str_list, json_list
            gc.collect()
            # print(x)
    def solve(self,json_list):
        records = self.__listOfNestedDict2ListOfDict(json_list)   #带所有字典的列表
        for i in records:
            if not self.__4Events4PerP.get(i['actor__login'], 0):    #字典中若不存在这个人
                self.__4Events4PerP.update({i['actor__login']: {}})     #加入这个人
                self.__4Events4PerPPerR.update({i['actor__login']: {}})     #加入
            self.__4Events4PerP[i['actor__login']][i['type']
                                         ] = self.__4Events4PerP[i['actor__login']].get(i['type'], 0)+1     #这项事件数加一
            if not self.__4Events4PerR.get(i['repo__name'], 0):     #若字典中没有这个项目
                self.__4Events4PerR.update({i['repo__name']: {}})       #创建
            self.__4Events4PerR[i['repo__name']][i['type']
                                       ] = self.__4Events4PerR[i['repo__name']].get(i['type'], 0)+1     #这个项目此次事件加一
            if not self.__4Events4PerPPerR[i['actor__login']].get(i['repo__name'], 0):      #若这个人字典中没有这个项目
                self.__4Events4PerPPerR[i['actor__login']].update({i['repo__name']: {}})    #创建
            self.__4Events4PerPPerR[i['actor__login']][i['repo__name']][i['type']
                                                          ] = self.__4Events4PerPPerR[i['actor__login']][i['repo__name']].get(i['type'], 0)+1  #人的项目的事件数加一

        # if self.done==1:
        #     with open('1.json', 'w', encoding='utf-8') as f:  # 初始化
        #         json.dump(self.__4Events4PerP, f)  # 写入
        #     with open('2.json', 'w', encoding='utf-8') as f:
        #         json.dump(self.__4Events4PerR, f)
        #     with open('3.json', 'w', encoding='utf-8') as f:
        #         json.dump(self.__4Events4PerPPerR, f)
        # else:
        #     with open('1.json', 'a', encoding='utf-8') as f:        #初始化
        #         json.dump(self.__4Events4PerP,f)        #写入
        #     with open('2.json', 'a', encoding='utf-8') as f:
        #         json.dump(self.__4Events4PerR,f)
        #     with open('3.json', 'a', encoding='utf-8') as f:
        #         json.dump(self.__4Events4PerPPerR,f)

    def __parseDict(self, d: dict, prefix: str):
        _d = {}
        # for k in d.keys():          #键
        #     if str(type(d[k]))[-6:-2] == 'dict':    #如果值是字典
        #         _d.update(self.__parseDict(d[k], k))    #迭代
        #     else:
        #         _k = f'{prefix}__{k}' if prefix != '' else k    #把字典里的字典整到外面
        #         _d[_k] = d[k]
        for k in d.keys():          #键
            if str(type(d[k]))[-6:-2] == 'dict':
                list=[]
                list1=[]
                list.append(d[k])
                list1.append(k)
                while list:
                    d2=list[0]
                    prefix=list1[0]
                    del list[0],list1[0]
                    for k1 in d2.keys():
                        if str(type(d2[k1]))[-6:-2] == 'dict':
                            list.append(d2[k1])
                            list1.append(k1)
                        else:
                            _k = f'{prefix}__{k1}' if prefix != '' else k1  # 把字典里的字典整到外面
                            _d[_k] = d2[k1]
            else:
                _k = f'{prefix}__{k}' if prefix != '' else k  # 把字典里的字典整到外面
                _d[_k] = d[k]

        return _d

    def __listOfNestedDict2ListOfDict(self, a: list):
        records = []
        for d in a:         #d:一条项目
            _d = self.__parseDict(d, '')
            records.append(_d)  #字典放入列表，列表存有所有项目

        return records

    def getEventsUsers(self, username: str, event: str) -> int:         #事件一
        if not self.__4Events4PerP.get(username,0):         #找不到人
            return 0
        else:
            return self.__4Events4PerP[username].get(event,0)

    def getEventsRepos(self, reponame: str, event: str) -> int:         #事件二
        if not self.__4Events4PerR.get(reponame,0):         #找不到项目
            return 0
        else:
            return self.__4Events4PerR[reponame].get(event,0)

    def getEventsUsersAndRepos(self, username: str, reponame: str, event: str) -> int:      #事件三
        if not self.__4Events4PerP.get(username,0):     #找不到人
            return 0
        elif not self.__4Events4PerPPerR[username].get(reponame,0):     #找不到项目
            return 0
        else:
            return self.__4Events4PerPPerR[username][reponame].get(event,0)


class Run:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.data = None
        self.argInit()
        print(self.analyse())

    def argInit(self):
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def analyse(self):
        if self.parser.parse_args().init:
            self.data = Data(self.parser.parse_args().init, 1)
            return 0
        else:
            if self.data is None:
                self.data = Data()      #创建变量
            if self.parser.parse_args().event:      #必有事件
                if self.parser.parse_args().user:       #事件一或三
                    if self.parser.parse_args().repo:       #事件三
                        res = self.data.getEventsUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo, self.parser.parse_args().event)
                    else:                                   #事件一
                        res = self.data.getEventsUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:         #事件二
                    res = self.data.getEventsRepos(
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:                                       #格式错误
                    raise RuntimeError('error: argument -l or -c are required')
            else:
                raise RuntimeError('error: argument -e is required')
        return res


if __name__ == '__main__':
    a = Run()