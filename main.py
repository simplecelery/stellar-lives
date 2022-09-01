import time
import StellarPlayer
import math
from . import json5
import json
import os
import sys
import bs4
import urllib3
import requests
import threading
import time
from shutil import copyfile
import base64

pbc = ["薦","成人电影","麻豆传媒","果冻传媒","乃","抽插","直播","觀","极品","女神","無碼","奸","有碼","无码","3p","女上位","变态","魅惑","女友","少妇","有码","性感","先生","潮吹","潮喷","喷潮","愛","親","澤","婦","幹","絕","對","痴女","免费看","97yj.xyz","番号","宅男","色情","人妖","在线播放","干炮","小姐姐","無","衝撃","撃","狂い","機","橋","堕","電","會所","乳","推特","尻","屁股","奶大","爽","大胸","射","私拍","淫","大乱交","拷問","開発","性爱","高潮","薬","斗鱼","韓國","學","射","操","逼","性生活","肏","實","錄","天美传媒","加勒比","里番","未亡人","tokyo","援交","重口","骚","尤物","全裸","幼女","歐美","蘿莉","流出","泄密","裸贷","啪啪","約","天海翼","國","產","創","風呂","無修正","大尺度","超人氣","写真","小电影","探花","sexy","kin8teng","撸管","金8天國","多p","生殖","丝语","诱惑","彼女","魔穗","素人","绿帽","福利","人妻","刘玥","june","乱伦","妻","无套","罩杯","主播","樂","露脸","奶子","屌","丝袜","车震","萝莉","自慰","自拍","丝袜","美腿","国语对白","调教","誘惑","視頻","熟女","桜","会所"]
'''
sourceurls = ["https://raw-gh.gcdn.mirr.one/520tv/TVbox/main/ts.json",
"https://raw.githubusercontents.com/520tv/TVbox/main/ts.json"
]
'''
sourceurls = [
"https://gitea.com/Yoursmile/TVBox/raw/branch/main/XC.json",
"https://box.okeybox.top/tv/0xth.json",
"https://box.okeybox.top/tv/plunju.json",
"https://cdn.jsdelivr.net/gh/520tv/mao@main/tvbox.json",
"https://raw.githubusercontents.com/520tv/mao/main/tvbox.json",
"https://cdn.jsdelivr.net/gh/Cyril0563/lanjing_live@main/hd/live_plus.json",
"https://raw.githubusercontents.com/Cyril0563/lanjing_live/main/hd/live_plus.json",
"https://cdn.jsdelivr.net/gh/Cyril0563/lanjing_live@main/hn/live_plus.json",
"https://raw.githubusercontents.com/Cyril0563/lanjing_live/main/hn/live_plus.json",
"https://cdn.jsdelivr.net/gh/Cyril0563/lanjing_live@main/hk/live_plus.json",
"https://raw.githubusercontents.com/Cyril0563/lanjing_live/main/hk/live_plus.json"]


def getRedirect(redirect):
    idx = redirect.find("ext=")
    if idx > 0:
        ext = redirect[idx + 4:]
        reurl = str(base64.b64decode(ext),'UTF-8')
        return reurl
    else:
        return None

def getRedirectLives(redirecturl):
    if redirecturl.find("https://raw.githubusercontents.com") >= 0:
        redirecturl = redirecturl.replace("https://raw.githubusercontents.com","https://raw-gh.gcdn.mirr.one")
    r = requests.get(redirecturl,timeout = 5,verify=False,)
    r.encoding = 'utf-8'
    if r.status_code != 200:
        return
    lines = r.text.split("\n")
    groupname = ""
    allLives = []
    channels = []
    for line in lines:
        if line.find(",") < 0:
            continue
        detail = line.split(",")
        if detail[1].strip() == "#genre#":
            if groupname != "":
                if len(channels) > 0:
                    allLives.append({"group":groupname,"channels":channels})
            groupname = detail[0].strip()
            channels = []
            continue
        channelname = detail[0].strip()
        strchannels = detail[1].split("#")
        index = 0
        urls = []
        for url in strchannels:
            i = 0
            find = False
            channelsnum = len(channels)
            for i in range(channelsnum):
                if channels[i]["name"] == channelname:
                    channels[i]["urls"].append(url.strip())
                    find = True
                    break
            if find == False:
                urls.append(url.strip())
        if len(urls) > 0:
            channels.append({"name":channelname,"urls":urls})
    allLives.append({"group":groupname,"channels":channels})
    print(allLives)
    return allLives

def parserLives(jsonlives):
    redirects = []
    tv = []
    for live in jsonlives:
        alllives = []
        for channel in live["channels"]:
            allurls = []
            index = 0
            for url in channel["urls"]:
                if url.find("proxy://") >= 0:
                    redirects.append(url)
                else:
                    allurls.append(url)
            if len(allurls) > 0:
                alllives.append({"name":channel["name"],"urls":allurls})
        if len(alllives) > 0:
            tv.append({"group":live["group"],"channels":alllives})
    for redirect in redirects:
        redirecturl = getRedirect(redirect)
        print(redirecturl)
        rlives = getRedirectLives(redirecturl)
        for rlive in rlives:
            tv.append(rlive)
    return tv
    
def parserSites(sitelives):
    allzyz = []
    for item in sitelives:
        if item['type'] == 0 or item['type'] == 1:
            if 'playUrl' in item:
                plauurlstr = item['playUrl']
                if len(plauurlstr) > 0:
                    continue
            keyval = item['key']
            if len(keyval) == 1:
                continue
            if keyval.find('*') == 0:
                continue
            playurl = item['api']
            if playurl.find('?') > 0:
                item['api'] = playurl.split("?")[0]
            allzyz.append(item)
    return allzyz

def getSourceJson(outfile):
    urllib3.disable_warnings()
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    for url in sourceurls:
        try:
            r = requests.get(url,timeout = 5,headers = header,verify=False) 
            result = r.status_code
            if result == 200:
                jsonstr = r.text
                jsonstr = jsonstr.replace('##','//')
                fileJson = json5.loads(jsonstr)
                livejson = parserLives(fileJson["lives"])
                sitejson = parserSites(fileJson['sites'])
                parserjson = fileJson['parses']
                if livejson and sitejson and parserjson:
                    savejson = {}
                    savejson["lives"] = livejson
                    savejson["sites"] = sitejson
                    savejson["parses"] = parserjson
                    with open(outfile, 'w',encoding='utf-8') as f:
                        json.dump(savejson, f,sort_keys=True, indent=4, separators=(',', ':'), ensure_ascii=False)
                print(url)
                return livejson,sitejson,parserjson
        except:
            continue
    return None,None,None

def checkpbc(word):
    for t in pbc:
        if word.find(t) >= 0:
            return True
    return False

class CheckZYZThread(threading.Thread):
    def __init__(self, zyz):
        threading.Thread.__init__(self)
        self.zyz = zyz
        self.result = None
        
    def run(self):
        try:
            down_url = self.zyz['api']
            r = requests.get(down_url,timeout = 1,verify=False) 
            result = r.status_code
            if result == 200:
                self.result = self.zyz

        except Exception as r:
           self.zyz = None
        
    def get_result(self):
        return self.result

class livesplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.configjson = ''
        self.tv = []
        self.zyz = []
        self.actzyz = 0
        self.jx = []
        self.cur_page = ''
        self.max_page = ''
        self.nextpg = ''
        self.previouspg = ''
        self.firstpg = ''
        self.lastpg = ''
        self.pg = ''
        self.wd = ''
        self.ids = ''
        self.tid = ''
        self.parserres = []
        self.mediaclass = []
        self.medias = []
        self.actTVChannels = []
        self.actTVXL = []
        self.allmovidesdata = {}
        self.allxlsdata = {}
        self.allzyzparserdata = {}
        self.stopjx = True
        self.zyzThread = None
        self.parserThread = None
        self.stopzyz = True
        self.li = []
        self.pli = []
        self.allSearchMedias = []
    
    def start(self):
        super().start()
        
        self.configjson = 'tv.json'
        jsonpath = self.player.dataDirectory + os.path.sep + 'tv.json'
        jsontv,jsonzyz,jsonjx = getSourceJson(jsonpath)

        self.loadSourceFile(self.configjson,jsontv,jsonzyz,jsonjx)
    
    def loadTV(self,tvjson,jsontv):
        if jsontv:
            self.tv = jsontv
        else:
            self.tv = tvjson
        if len(self.tv) > 0:
            self.actTVChannels = self.tv[0]['channels']
        self.actTVXL = []
        index = 0
        for xl in self.actTVChannels[0]['urls']:
            index = index + 1
            xlname = '线路' + str(index)
            self.actTVXL.append({'xlname':xlname,'xlurl':xl})
    
    def getPageInfoJson(self,jsondata):
        self.pageindex = jsondata['page']
        self.pagenumbers = jsondata['pagecount']
        self.nextpg = '&pg=' + str(int(self.pageindex) + 1)
        if self.pageindex == 1:
            self.previouspg = '&pg=1'
        else:
            self.previouspg = '&pg=' + str(int(self.pageindex) - 1)
        self.firstpg = '&pg=1'
        self.lastpg = '&pg=' + str(self.pagenumbers)
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'  
        self.player.updateControlValue('影视资源','cur_page',self.cur_page)
        self.player.updateControlValue('影视资源','max_page',self.max_page)
    
    def getPageInfoXML(self,bs):
        self.nextpg = ''
        self.previouspg = ''
        self.firstpg = ''
        self.lastpg = ''
        selector = bs.select('rss > list')
        self.pagenumbers = 0
        self.pageindex = 0
        if selector:
            self.pageindex = int(selector[0].get('page'))
            self.pagenumbers = int(selector[0].get('pagecount'))
            if self.pageindex < self.pagenumbers:
                self.nextpg = '&pg=' + str(int(self.pageindex) + 1)
            else:
                self.nextpg = '&pg=' + str(self.pagenumbers)
            if self.pageindex == 1:
                self.previouspg = '&pg=1'
            else:
                self.previouspg = '&pg=' + str(int(self.pageindex) - 1)
            self.firstpg = '&pg=1'
            self.lastpg = '&pg=' + str(self.pagenumbers)
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.max_page = '共' + str(self.pagenumbers) + '页'
        self.player.updateControlValue('影视资源','cur_page',self.cur_page)
        self.player.updateControlValue('影视资源','max_page',self.max_page)
    
    def loadZYZ(self,zyzjson,jsonzyz):
        '''
        self.zyz = zyzjson
        if jsonzyz:
            self.zyz = jsonzyz
        '''
        li = []
        zyzdata = zyzjson
        if jsonzyz:
            zyzdata = jsonzyz
        for item in zyzdata:
            if item['type'] == 0 or item['type'] == 1:
                if 'playUrl' in item:
                    plauurlstr = item['playUrl']
                    if len(plauurlstr) > 0:
                        continue
                keyval = item['key']
                if len(keyval) == 1:
                    continue
                if keyval.find('*') == 0:
                    continue
                playurl = item['api']
                if playurl.find('?') > 0:
                    item['api'] = playurl.split("?")[0]
                t = CheckZYZThread(item)
                li.append(t)
                t.start()
        self.zyz = []
        for t in li:
            t.join()
            reszyz = t.get_result()
            if reszyz:
                self.zyz.append(reszyz)
        #'''
        self.actzyz = 0
        if len(self.zyz) > 0:
            n = 0
            for item in self.zyz:
                apiurl = item['api'] 
                apitype = item['type']
                url = apiurl + '?ac=list'
                self.getMediaClass(url,apitype)
                if len(self.mediaclass) > 0:
                    self.getMediaList()
                    self.actzyz = n
                    return
                n = n + 1

    def getMediaClass(self,url,apitype):
        try:
            res = requests.get(url,timeout = 5,verify=False)
            if res.status_code == 200:
                if apitype == 1:
                    jsondata = json.loads(res.text, strict = False)
                    if jsondata:
                        self.mediaclass = jsondata['class']
                        self.getPageInfoJson(jsondata)
                else:
                    bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                    selector = bs.select('rss > class >ty')
                    if selector:
                        for item in selector:
                            t_id = int(item.get('id'))
                            t_name = item.string
                            self.mediaclass.append({'type_id':t_id,'type_name':t_name})
                        self.getPageInfoXML(bs)
        except:
            self.mediaclass = []

    def getMediaList(self):
        self.medias = []
        apiurl = self.zyz[self.actzyz]['api']
        apitype = self.zyz[self.actzyz]['type']
        url = apiurl + '?ac=videolist'
        if self.wd != '':
            self.tid = ''
            url = url + '&wd=' +self.wd
        if self.tid != '':
            url = url + self.tid
        if self.pg != '':
            url = url + self.pg
        try:
            res = requests.get(url,timeout = 5,verify=False)
            if res.status_code == 200:
                if apitype == 1:
                    jsondata = json.loads(res.text, strict = False)
                    if jsondata:
                        jsonlist = jsondata['list']
                        for item in jsonlist:
                            self.medias.append({'ids':item['vod_id'],'title':item['vod_name'],'picture':item['vod_pic'],'api':apiurl,'apitype':apitype})
                        self.getPageInfoJson(jsondata)
                else:
                    bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                    selector = bs.select('rss > list > video')
                    if selector:
                        for item in selector:
                            nameinfo = item.select('name')
                            picinfo = item.select('pic')
                            idsinfo = item.select('id')
                            if nameinfo and picinfo and idsinfo:
                                name = nameinfo[0].string
                                pic = picinfo[0].string
                                ids = int(idsinfo[0].string)
                                self.medias.append({'ids':ids,'title':name,'picture':pic,'api':apiurl,'apitype':apitype})
                    self.getPageInfoXML(bs)
            else:
                self.medias = []
        except:
            self.medias = []
        
    def loadParser(self,jxjson,jsonjx):
        jxdata = jxjson
        if jsonjx:
            jxdata = jsonjx
        self.jx = []
        for item in jxjson:
            if 'type' in item:
                if item['type'] == 1:
                    self.jx.append({'jxname':item['name'],'jxurl':item['url']})
    
    def loadSourceFile(self,file,jsontv,jsonzyz,jsonjx):
        file = open(file, "r",encoding = "UTF-8")
        jsonstr = file.read()
        jsonstr = jsonstr.replace('##','//')
        fileJson = json5.loads(jsonstr)
        self.loadTV(fileJson["lives"],jsontv)
        self.loadZYZ(fileJson['sites'],jsonzyz)
        self.loadParser(fileJson['parses'],jsonjx)
        file.close()    
    
    def show(self):
        if hasattr(self.player, 'createTab'):
            self.showJX()
            self.showZYZ()
            self.showTV()
        else:
            self.player.showText('播放器版本过低，不支持此插件,请升级播放器')
            #self.player.showNotify('错误', '播放器版本过低，不支持此插件,请升级播放器')
    
    def showTV(self):
        controls = self.makeTVModal()
        self.player.createTab('电视直播','电视直播', controls)
        
    def showZYZ(self):
        controls = self.makeZYZModal()
        self.cur_page = '第0页'
        self.max_page = '共0页'
        self.player.createTab('影视资源','影视资源', controls)
    
    def showJX(self):
        controls = self.makeJXModal()
        self.player.createTab('网页解析','网页解析', controls)
    
    def makeJXModal(self):
        parser_layout =[
            {'type':'link','name':'title','textColor':'#556B2F','fontSize':15,'@click':'on_parserurl_click'},
            {'type':'space','height':5}
        ]
        controls = [
            {'type':'space','height':5},
            {
                'group':[
                    {'type':'space','width':5},
                    {'type':'edit','name':'parser_edit','label':'网址','width':0.7},
                    {'type':'button','name':'解析','@click':'onParser','width':80},
                    {'type':'space','width':5},
                    {'type':'button','name':'停止解析','@click':'onStopParser','width':80},
                ],
                'height':40
            },
            {'type':'label','name':'jxsm','value':'解析功能来自网络多个源，取得的播放地址如不能正常播放请切换解析结果','height':30},
            {'type':'grid','name':'parsergrid','itemlayout':parser_layout,'value':self.parserres,'separator':True,'itemheight':80,'itemwidth':120,'width':1.0},
        ]
        return controls
    
    def makeTVModal(self):
        gropu_layout=[
            {'type':'link','name':'group','textColor':'#ff7f00','fontSize':15,'hAlign':'center','vAlign':'center','@click':'on_tvgroup_click'}
        ]
        channel_layout=[
            {'type':'link','name':'name','textColor':'#556B2F','fontSize':15,'hAlign':'center','vAlign':'center','@click':'on_tvchannel_click'}
        ]
        xl_layout=[
            {'type':'link','name':'xlname','textColor':'#008000','fontSize':15,'hAlign':'center','vAlign':'center','@click':'on_tvxl_click'}
        ]
        controls = [
            {
                'group': [
                    {'type':'grid','name':'tvgroupgrid','itemlayout':gropu_layout,'value':self.tv,'separator':True,'itemheight':40,'itemwidth':120,'width':200},
                    {
                        'group': [
                            {'type':'label','name':'电视台列表','height':30},
                            {'type':'grid','name':'tvchannelgrid','itemlayout':channel_layout,'value':self.actTVChannels,'separator':True,'itemheight':40,'itemwidth':120},
                        ],
                        'dir':'vertical',
                        'width':200
                    },
                    {
                        'group': [
                            {'type':'label','name':'线路列表','height':30},
                            {'type':'grid','name':'tvxlgrid','itemlayout':xl_layout,'value':self.actTVXL,'separator':True,'itemheight':40,'itemwidth':120}
                        ],
                        'dir':'vertical'
                    }
                ]
            }
        ]
        return controls            
        
    def makeZYZModal(self):
        zyz_layout=[
            {'type':'link','name':'name','textColor':'#ff7f00','fontSize':15,'hAlign':'center','vAlign':'center','@click':'on_zyz_click'}
        ]
        mediaclass_layout = [
            {'type':'link','name':'type_name','textColor':'#556B2F','fontSize':15,'hAlign':'center','vAlign':'center','@click':'on_zyzsecmenu_click'}
        ]
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_mediagrid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':15,'height':0.15, '@click':'on_mediagrid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {
                'group':[
                    {'type':'space','width':5},
                    {'type':'edit','name':'search_edit','label':'关键字','width':0.6,'height':35},
                    {'type':'button','name':'搜索当前站','@click':'onSearchActZYZ','width':80},
                    {'type':'space','width':15},
                    {'type':'button','name':'搜索所有站','@click':'onSearchAllZYZ','width':80},
                ],
                'height':40
            },
            {
                'group': [
                    {'type':'grid','name':'zygrid','itemlayout':zyz_layout,'value':self.zyz,'itemheight':30,'itemwidth':120,'width':150},
                    {'type':'grid','name':'mediaclassgrid','itemlayout':mediaclass_layout,'value':self.mediaclass,'itemheight':30,'itemwidth':120,'width':150},
                    {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':240,'itemwidth':150}
                ]
            },
            {
                'group':[
                    {'type':'space','width':5},
                    {'type':'label','name':'cur_page','value':self.cur_page},
                    {'type':'link','name':'首页','@click':'onClickFirstPage'},
                    {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                    {'type':'link','name':'下一页','@click':'onClickNextPage'},
                    {'type':'link','name':'末页','@click':'onClickLastPage'},
                    {'type':'label','name':'max_page','value':self.max_page},
                    {'type':'space','width':5}
                ],
                'height':50
            }
        ]
        return controls
      
    def onSearchActZYZ(self, *args):
        keyval = self.player.getControlValue('影视资源','search_edit').strip()
        if checkpbc(keyval):
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            return
        if 'searchable' in self.zyz[self.actzyz] and self.zyz[self.actzyz]['searchable'] == 0:
            self.player.toast('影视资源','本站不支持搜索')
            return
        zyzs = []
        zyzs.append({'api':self.zyz[self.actzyz]['api'],'type':self.zyz[self.actzyz]['type'],'pg':1})
        if self.zyzThread and self.zyzThread.is_alive():
            self.stopzyz = True
            self.zyzThread.join()
            self.zyzThread = None
        newthread = threading.Thread(target=self._zyzSearchThread,args=(zyzs,keyval))
        self.zyzThread = newthread
        self.zyzThread.start()
    
    def onSearchAllZYZ(self, *args):
        keyval = self.player.getControlValue('影视资源','search_edit').strip()
        if checkpbc(keyval):
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            return
        zyzs = []
        for item in self.zyz:
            if 'searchable' in item and item['searchable'] == 0:
                continue
            zyzs.append({'api':item['api'],'type':item['type'],'pg':1})
        if self.zyzThread and self.zyzThread.is_alive():
            self.stopzyz = True
            self.zyzThread.join()
            self.zyzThread = None
        newthread = threading.Thread(target=self._zyzSearchThread,args=(zyzs,keyval))
        self.zyzThread = newthread
        self.zyzThread.start()
    
    def _zyzSearchThread(self,zyzs,key):
        for t in self.li:
            t.join()
        self.li = []
        self.player.updateControlValue('影视资源','cur_page','')
        self.player.updateControlValue('影视资源','max_page','')
        self.stopzyz = False
        self.medias = []
        self.allSearchMedias = []
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        for node in zyzs:
            self.newSearchNode(node,key)
        for t in self.li:
            t.join()
    
    def newSearchNode(self,node,key):
        t = threading.Thread(target=self._zyzSearchNoneThread,args=(node,key))
        self.li.append(t)
        t.start()
        
    def _zyzSearchNoneThread(self,node,key):
        zyzapiurl = node['api']
        zyzapitype = node['type']
        if self.stopzyz:
            return
        url = zyzapiurl + '?ac=videolist&wd=' + key + '&pg=' + str(node['pg'])
        try:
            res = requests.get(url,timeout = 5,verify=False)
            if res.status_code == 200:
                if zyzapitype == 1:
                    jsondata = json.loads(res.text, strict = False)
                    if jsondata:
                        pageindex = int(jsondata['page'])
                        pagenumbers = int(jsondata['pagecount'])
                        if pageindex < pagenumbers and pagenumbers < 5:
                            self.newSearchNode({'api':zyzapiurl,'type':zyzapitype,'pg':pageindex + 1},key)
                        if pagenumbers >= 5:
                            return
                        jsonlist = jsondata['list']
                        for item in jsonlist:
                            if self.stopzyz == False:
                                self.allSearchMedias.append({'ids':item['vod_id'],'title':item['vod_name'],'picture':item['vod_pic'],'api':zyzapiurl,'apitype':zyzapitype})
                else:
                    bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                    selector = bs.select('rss > list')
                    pagenumbers = 0
                    pageindex = 0
                    if selector:
                        pageindex = int(selector[0].get('page'))
                        pagenumbers = int(selector[0].get('pagecount'))
                    if pageindex < pagenumbers and pagenumbers < 5:
                        self.newSearchNode({'api':zyzapiurl,'type':zyzapitype,'pg':pageindex + 1},key)
                    if pagenumbers >= 5:
                        return
                    selector = bs.select('rss > list > video')
                    if selector:
                        for item in selector:
                            nameinfo = item.select('name')
                            picinfo = item.select('pic')
                            idsinfo = item.select('id')
                            if nameinfo and picinfo and idsinfo:
                                name = nameinfo[0].string
                                pic = picinfo[0].string
                                ids = int(idsinfo[0].string)
                                if self.stopzyz == False:
                                    self.allSearchMedias.append({'ids':ids,'title':name,'picture':pic,'api':zyzapiurl,'apitype':zyzapitype})
            else:
                return
        except:
            return
        if self.stopzyz == False:
            if len(self.medias) < 20:
                num = 20
                if num > len(self.allSearchMedias):
                    num = len(self.allSearchMedias)
                for i in range(len(self.medias),num):
                    self.pageindex = 1
                    self.medias.append(self.allSearchMedias[i]);
                    self.cur_page = '第1页'
                    self.player.updateControlValue('影视资源','cur_page',self.cur_page)
            self.pagenumbers = len(self.allSearchMedias) // 20
            if self.pagenumbers * 20 < len(self.allSearchMedias):
                self.pagenumbers = self.pagenumbers + 1
            self.max_page = '共' + str(self.pagenumbers) + '页'
            self.player.updateControlValue('影视资源','max_page',self.max_page)
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
      
    def on_zyz_click(self, page, listControl, item, itemControl):
        self.stopzyz = True
        self.allSearchMedias = []
        self.loading('影视资源')
        self.pg = ''
        self.wd = ''
        self.tid = ''
        self.mediaclass = []
        self.medias = []
        self.player.updateControlValue('影视资源','mediaclassgrid',self.mediaclass)
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        self.actzyz = item
        print('item:' + str(self.actzyz))
        apiurl = self.zyz[self.actzyz]['api'] 
        print(self.zyz[self.actzyz])
        apitype = self.zyz[self.actzyz]['type']
        url = apiurl + '?ac=list'
        self.getMediaClass(url,apitype)
        if len(self.mediaclass) > 0:
            self.getMediaList()
        self.player.updateControlValue('影视资源','mediaclassgrid',self.mediaclass)
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        self.loading('影视资源',True)
        
    def on_zyzsecmenu_click(self, page, listControl, item, itemControl):
        self.stopzyz = True
        for t in self.li:
            if t:
                t.join()
        self.li = []
        if self.zyzThread != None and self.zyzThread.is_alive():
            self.zyzThread.join()
            self.zyzThread = None
        self.allSearchMedias = []
        self.loading('影视资源')
        self.medias = []
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        typeid = self.mediaclass[item]['type_id']
        self.wd = ''
        self.pg = ''
        self.tid = '&t=' + str(typeid)
        self.getMediaList()
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        self.loading('影视资源',True)

    def on_mediagrid_click(self, page, listControl, item, itemControl):
        apiurl = self.medias[item]['api'] 
        apitype = self.medias[item]['apitype']
        videoid = self.medias[item]['ids']
        url = apiurl + '?ac=videolist&ids=' + str(videoid)
        self.onGetMediaPage(url,apitype)
        
    def onGetMediaPage(self,url,apitype):
        print(url)
        try:
            res = requests.get(url,timeout = 5,verify=False)
            if res.status_code == 200:
                if apitype == 1:
                    jsondata = json.loads(res.text, strict = False)
                    if jsondata:
                        medialist = jsondata['list']
                        if len(medialist) > 0:
                            info = medialist[0]
                            playfrom = info["vod_play_from"]
                            playnote = '$$$'
                            playfromlist = playfrom.split(playnote)
                            playurl = info["vod_play_url"]
                            hasm3u8 = playurl.find('m3u8') >= 0
                            playurllist = playurl.split(playnote)
                            sourcelen = len(playfromlist)
                            sourcelist = []
                            for i in range(sourcelen):
                                urllist = [] 
                                urlstr = playurllist[i]
                                jjlist = urlstr.split('#')
                                n = 0
                                for jj in jjlist:
                                    n = n + 1
                                    if jj.strip() != '':
                                        jjinfo = jj.split('$')
                                        js = ''
                                        jsdz = ''
                                        if len(jjinfo) == 1:
                                            js = '第' + str(n) + '集'
                                            jsdz = jjinfo[0]
                                        elif len(jjinfo) == 2:
                                            js = jjinfo[0]
                                            jsdz = jjinfo[1]
                                        #if jsdz.find('.m3u8') > 0 or jsdz.find('.mp4') > 0:
                                        urllist.append({'title':js,'url':jsdz})
                                if len(urllist) > 0:
                                    sourcelist.append({'flag':playfromlist[i],'medias':urllist})
                            if len(sourcelist) > 0:
                                mediainfo = {'medianame':info['vod_name'],'pic':info['vod_pic'],'actor':'演员:' + info['vod_actor'].strip(),'content':'简介:' + info['vod_content'].strip(),'source':sourcelist}
                                self.createMediaFrame(mediainfo)
                                return
                            else:
                                self.player.toast('main','无法获取视频信息')
                else:
                    bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                    selector = bs.select('rss > list > video')
                    if len(selector) > 0:
                        info = selector[0]
                        nameinfo = info.select('name')[0]
                        name = nameinfo.text
                        picinfo = info.select('pic')[0]
                        pic = picinfo.text
                        actorinfo = info.select('actor')[0]
                        actor = '演员:' + actorinfo.text.strip()
                        desinfo = info.select('des')[0]
                        des = '简介:' + desinfo.text.strip()
                        dds = info.select('dl > dd')
                        hasm3u8 = False
                        for dd in dds:
                            ddflag = dd.get('flag')
                            if ddflag.find('m3u8') >= 0:
                                hasm3u8 = True
                                break
                        sourcelist = []
                        for dd in dds:
                            ddflag = dd.get('flag')
                            ddinfo = dd.text
                            m3u8list = []
                            if ddflag.find('m3u8') < 0 and hasm3u8:
                                continue
                            urllist = ddinfo.split('#')
                            n = 1
                            for source in urllist:
                                urlinfo = source.split('$')
                                if len(urlinfo) == 1:
                                    m3u8list.append({'title':'第' + str(n) + '集','url':ddinfo})
                                else:
                                    m3u8list.append({'title':urlinfo[0],'url':urlinfo[1]})
                                n = n + 1
                            sourcelist.append({'flag':ddflag,'medias':m3u8list})
                        mediainfo = {'medianame':name,'pic':pic,'actor':actor,'content':des,'source':sourcelist}
                        self.createMediaFrame(mediainfo)
                        return
        except:
            self.player and self.player.toast('main','请求失败')
        self.player and self.player.toast('main','无法获取视频信息')
        return
        
    def createMediaFrame(self,mediainfo):
        if len(mediainfo['source']) == 0:
            self.player.toast('main','该视频没有可播放的视频源')
            return
        actmovies = []
        actparserurl = []
        if len(mediainfo['source']) > 0:
            actmovies = mediainfo['source'][0]['medias']
        medianame = mediainfo['medianame']
        self.allmovidesdata[medianame] = {'allmovies':mediainfo['source'],'actmovies':actmovies,'actparserurl':actparserurl,'parserstop':True,'parserthread':None}
        xl_list_layout = {'type':'link','name':'flag','fontSize':15,'textColor':'#ff0000','width':0.6,'@click':'on_xl_click'}
        movie_list_layout = {'type':'link','name':'title','fontSize':15,'@click':'on_movieurl_click'}
        parserurl_list_layout = {'type':'link','name':'title','fontSize':15,'textColor':'#006400','@click':'on_zyzparserurl_click'}
        controls = [
            {'type':'space','height':5},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':mediainfo['pic'],'width':0.25},
                    {'group':[
                            {'type':'label','name':'medianame','textColor':'#ff7f00','fontSize':15,'value':mediainfo['medianame'],'height':40},
                            {'type':'label','name':'actor','textColor':'#555500','value':mediainfo['actor'],'height':0.3},
                            {'type':'label','name':'info','textColor':'#005555','value':mediainfo['content'],'height':0.7}
                        ],
                        'dir':'vertical',
                        'width':0.75
                    }
                ],
                'width':1.0,
                'height':250
            },
            {'type':'label','name':'线路','height':30},
            {'group':
                {'type':'grid','name':'xllist','itemlayout':xl_list_layout,'value':mediainfo['source'],'separator':True,'itemheight':30,'itemwidth':120},
                'height':40
            },
            {'type':'space','height':5},
            {'group':
                {'type':'grid','name':'movielist','itemlayout':movie_list_layout,'value':actmovies,'separator':True,'itemheight':30,'itemwidth':120},
                'height':160
            },
            {'type':'label','name':'jxdz','value':'','height':30},
            {'group':
                {'type':'grid','name':'parserurllist','itemlayout':parserurl_list_layout,'value':actparserurl,'separator':True,'itemheight':30,'itemwidth':120},
                'height':70
            }
        ]
        result,control = self.doModal(mediainfo['medianame'],750,600,'',controls)

    def on_xl_click(self, page, listControl, item, itemControl):
        self.player.updateControlValue(page,'movielist',[])
        if len(self.allmovidesdata[page]['allmovies']) > item:
            self.allmovidesdata[page]['actmovies'] = self.allmovidesdata[page]['allmovies'][item]['medias']
        self.player.updateControlValue(page,'movielist',self.allmovidesdata[page]['actmovies'])
        self.player.updateControlValue(page,'parserurllist',[])
        self.player.updateControlValue(page,'jxdz','')
        
    def on_movieurl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['actmovies']) > item:
            playurl = self.allmovidesdata[page]['actmovies'][item]['url']
            playname = page + ' ' + self.allmovidesdata[page]['actmovies'][item]['title']
            if playurl.find('.m3u8') > 0 or playurl.find('.mp4') > 0:
                playlist = []
                for xl in self.allmovidesdata[page]['allmovies']:
                    if len(xl['medias']) > item:
                        playlist.append({'url':xl['medias'][item]['url']})
                try:
                    self.player.playMultiUrls(playlist,playname)
                except:
                    self.player.play(playurl, caption=playname)
            else:
                self.player and self.player.toast(page,'该线路需要解析播放，请点击解析地址播放')
                self.parserurl(playurl,page,item)
        
    def on_zyzparserurl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['actparserurl']) > item:
            playurl = self.allmovidesdata[page]['actparserurl'][item]['playurl']
            n = self.allmovidesdata[page]['actparserurl'][item]['index']
            playname = page + ' ' + self.allmovidesdata[page]['actmovies'][n]['title']
            playlist = []
            playlist.append({'url':self.allmovidesdata[page]['actparserurl'][item]['playurl']})
            n = 0
            for n in range(len(self.allmovidesdata[page]['actparserurl'])):
                if n != item:
                    playlist.append({'url':self.allmovidesdata[page]['actparserurl'][n]['playurl']})
            try:
                self.player.playMultiUrls(playlist,playname)
            except:
                self.player.play(playurl, caption=playname)
        
    def parserurl(self,url,page,n):
        if self.allmovidesdata[page]['parserthread'] and self.allmovidesdata[page]['parserthread'].is_alive():
            self.allmovidesdata[page]['parserstop'] = True
            self.allmovidesdata[page]['parserthread'].join()
        newthread = threading.Thread(target=self._parserUrlThread,args=(page,url,n))
        self.allmovidesdata[page]['parserthread'] = newthread
        self.allmovidesdata[page]['parserthread'].start()
        
    def _parserUrlThread(self,page,url,n):
        for t in self.pli:
            t.join()
        self.pli = []
        self.allmovidesdata[page]['parserstop'] = False
        self.allmovidesdata[page]['actparserurl'] = []
        self.player.updateControlValue(page,'parserurllist',self.allmovidesdata[page]['actparserurl'])
        self.player.updateControlValue(page,'jxdz','解析地址')
        for item in self.jx:
            t = threading.Thread(target=self._parserNodeThread,args=(item,page,url,n))
            t.start()
            self.pli.append(t)
        for t in self.pli:
            t.join()
        if len(self.allmovidesdata[page]['actparserurl']) == 0:
            self.player and self.player.toast(page,'无法获取视频解析地址或资源已下架，请切换线路')
            return
        return
        
    def _parserNodeThread(self,item,page,url,n):
        if self.allmovidesdata[page]['parserstop']:
            return
        parserurl = item['jxurl'] + url
        try:
            res = requests.get(parserurl,timeout = 5,verify=False)
            if res.status_code == 200:
                jsondata = json.loads(res.text, strict = False)
                if jsondata:
                    if jsondata['code'] == 200 and jsondata['success'] == 1:
                        if jsondata['url'] != url:
                            self.allmovidesdata[page]['actparserurl'].append({'jxname':item['jxname'],'playurl':jsondata['url'],'title':jsondata['type'],'index':n})
                            if self.player.isModalExist(page) and self.allmovidesdata[page]['parserstop'] == False:
                                self.player.updateControlValue(page,'parserurllist',self.allmovidesdata[page]['actparserurl'])
                        return
        except:
            return

        
    def reloadTVXL(self,n):
        self.actTVXL = []
        index = 0
        for xl in self.actTVChannels[n]['urls']:
            index = index + 1
            xlname = '线路' + str(index)
            self.actTVXL.append({'xlname':xlname,'xlurl':xl})
        
    def on_tvgroup_click(self, page, listControl, item, itemControl):
        self.actTVChannels = []
        self.actTVXL = []
        self.player.updateControlValue('电视直播','tvchannelgrid',self.actTVChannels)
        self.player.updateControlValue('电视直播','tvxlgrid',self.actTVXL)
        self.actTVChannels = self.tv[item]['channels']
        self.reloadTVXL(0)
        self.player.updateControlValue('电视直播','tvchannelgrid',self.actTVChannels)
        self.player.updateControlValue('电视直播','tvxlgrid',self.actTVXL)
        
    def on_tvchannel_click(self, page, listControl, item, itemControl):
        self.actTVXL = []
        self.player.updateControlValue('电视直播','tvxlgrid',self.actTVXL)
        self.reloadTVXL(item)
        self.player.updateControlValue('电视直播','tvxlgrid',self.actTVXL)
        playlist = []
        for item in self.actTVXL:
            playlist.append({'url':item['xlurl']})
        try:
            self.player.playMultiUrls(playlist,page)
        except:
            if len(self.actTVXL) == 1:
                url = self.actTVXL[0]['xlurl']
                xlname = page + self.actTVXL[0]['xlname']
                self.player.play(url, caption=xlname)
    
    def on_tvxl_click(self, page, listControl, item, itemControl):
        url = self.actTVXL[item]['xlurl']
        xlname = page + self.actTVXL[item]['xlname']
        self.player.play(url, caption=xlname)
        
    def updateSearch(self,index):
        print(index)
        if index < 1:
            return
        self.medias = []
        self.player.updateControlValue('影视资源','mediagrid',self.medias)
        self.pageindex = index
        self.cur_page = '第' + str(self.pageindex) + '页'
        self.player.updateControlValue('影视资源','cur_page',self.cur_page)
        if len(self.allSearchMedias) >= 20 * (index - 1):
            idxend = 20 * index
            idxstart = idxend - 20
            if idxend > len(self.allSearchMedias):
                idxend = len(self.allSearchMedias)
            for i in range(idxstart,idxend):
                self.medias.append(self.allSearchMedias[i])
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
    
    def onClickFirstPage(self, *args):
        if len(self.allSearchMedias) == 0:
            if self.firstpg == '':
                return
            self.pg = self.firstpg
            self.loading('影视资源')
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.getMediaList()
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.loading('影视资源',True)
        else:
            self.updateSearch(1)
        
    def onClickFormerPage(self, *args):
        if len(self.allSearchMedias) == 0:
            if self.previouspg == '':
                return
            self.pg = self.previouspg
            self.loading('影视资源')
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.getMediaList()
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.loading('影视资源',True)
        else:
            self.updateSearch(self.pageindex - 1)
    
    def onClickNextPage(self, *args):
        if len(self.allSearchMedias) == 0:
            if self.nextpg == '':
                return
            self.pg = self.nextpg
            self.loading('影视资源')
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.getMediaList()
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.loading('影视资源',True)
        else:
            self.updateSearch(self.pageindex + 1)
        
    def onClickLastPage(self, *args):
        if len(self.allSearchMedias) == 0:
            if self.lastpg == '':
                return
            self.pg = self.lastpg
            self.loading('影视资源')
            self.medias = []
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.getMediaList()
            self.player.updateControlValue('影视资源','mediagrid',self.medias)
            self.loading('影视资源',True)
        else:
            self.updateSearch(self.pagenumbers)
        
    def onParser(self, *args):
        newthread = threading.Thread(target=self._parserThread)
        newthread.start()
        return
    
    def _jxurlThread(self,item,parser_word):
        if self.stopjx:
            return
        url = item['jxurl'] + parser_word
        try:
            res = requests.get(url,timeout = 5,verify=False)
            if res.status_code == 200:
                jsondata = json.loads(res.text, strict = False)
                if jsondata:
                    if jsondata['code'] == 200 and jsondata['success'] == 1 and jsondata['url'] != "":
                        self.parserres.append({'jxname':item['jxname'],'playurl':jsondata['url'],'title':jsondata['type']})
                        self.player.updateControlValue('网页解析','parsergrid',self.parserres)
                        return
        except:
            return
    
    def _parserThread(self):
        parser_word = self.player.getControlValue('网页解析','parser_edit').strip()
        self.parserres  = []
        self.player.updateControlValue('网页解析','parsergrid',self.parserres)
        self.stopjx = False
        jxli = []
        for item in self.jx:
            t = threading.Thread(target=self._jxurlThread,args=[item,parser_word,])
            t.start()
            jxli.append(t)
        for t in jxli:
            t.join()
        self.player.toast('网页解析','解析完成')
        return
    
    def on_parserurl_click(self, page, listControl, item, itemControl):
        if item >= len(self.parserres):
            return
        playlist = []
        for it in self.parserres:
            playlist.append({'url':it['playurl']})
        try:
            self.player.playMultiUrls(playlist)
        except:
            url = self.parserres[item]['playurl']
            self.player.play(url)

    def onStopParser(self, *args):
        self.stopjx = True
        
    def loading(self, page, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation(page, stop=stopLoading)
    
    def stop(self):
        self.stopjx = True
        self.stopzyz = True
        for key,value in self.allmovidesdata.items():
            self.allmovidesdata[key]['parserstop']  = True
        return super().stop()
            
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = livesplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()