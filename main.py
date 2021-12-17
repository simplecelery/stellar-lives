import time
import StellarPlayer
import math
import json
import os
import sys
import requests
from shutil import copyfile

class livesplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.configjson = ''
        self.source = []
        self.allmovidesdata = {}
        self.allxlsdata = {}
    
    def start(self):
        super().start()
        self.configjson = 'tv.json'
        jsonpath = self.player.dataDirectory + '\\tv.json'
        if os.path.exists(jsonpath) == False:
            localpath = os.path.split(os.path.realpath(__file__))[0] + '\\tv.json'
            print(localpath)
            if os.path.exists(localpath):
                try:
                    copyfile(localpath,jsonpath)
                except IOError as e:
                    print("Unable to copy file. %s" % e)
                except:
                    print("Unexpected error:", sys.exc_info())
        down_url = "https://cdn.jsdelivr.net/gh/nomoodhalashao/my-movie@main/tv.json"
        try:
            r = requests.get(down_url,timeout = 5,verify=False) 
            result = r.status_code
            if result == 200:
                with open(self.configjson,'wb') as f:
                    f.write(r.content)
        except Exception as r:
            print('get remote source.json error %s' %r)
        self.loadSourceFile(self.configjson)

    def loadSourceFile(self,file):
        file = open(file, "rb")
        fileJson = json.loads(file.read())
        self.source = fileJson["lives"]
        print(self.source)
        file.close()    
    
    def show(self):
        if hasattr(self.player, 'createTab'):
            for item in self.source:
                controls = self.makeGroupLayout(item)
                self.allmovidesdata[item['group']] = item['channels']
                if not self.player.isModalExist(item['group']):
                    self.player.createTab(item['group'],item['group'], controls)
        else:
            self.player.showText('播放器版本过低，不支持此插件')
            #self.player.showNotify('错误', '播放器版本过低，不支持此插件,请升级播放器')
    
    def makeGroupLayout(self,group):
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'space', 'width':5},
                        {'type':'link','name':'name','textColor':'#ff7f00','fontSize':15,'hAlign':'center','@click':'on_grid_click'},
                        {'type':'space', 'width':5},
                    ]
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {'type':'label','height':15,'name':group['group'],'height':30},
            {'type':'space','height':5},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':group['channels'],'separator':True,'itemheight':40,'itemwidth':180},
            {'type':'space','height':15}
        ]
        return controls
            
        
    def on_grid_click(self, page, listControl, item, itemControl):
        mediainfo = self.allmovidesdata[page][item]
        print(mediainfo)
        if len(mediainfo['urls']) > 1:
            self.createMediaFrame(mediainfo)
        else:
            tvurl = mediainfo['urls'][0]
            self.player.play(tvurl, caption=mediainfo['name'])
        
    def createMediaFrame(self,mediainfo):
        medianame = mediainfo['name']
        urlindex = []
        urllen = len(mediainfo['urls'])
        urllist = []
        for num in range(0,urllen):
            indexname = '线路' + str(num + 1)
            urllist.append({'title':indexname})
        self.allxlsdata[medianame] = mediainfo['urls']
        print(self.allxlsdata)
        xl_layout = [
            [
                {
                    'group': [
                        {'type':'space', 'width':5},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':15,'hAlign':'center','@click':'onXLClick'},
                        {'type':'space', 'width':5},
                    ]
                }
            ]
        ]
        controls = [
            {'type':'space','height':15},
            {'type':'grid','name':'xlgrid','itemlayout':xl_layout,'value':urllist,'separator':True,'itemheight':40,'itemwidth':80},
            {'type':'space','height':15}
        ]
        if not self.player.isModalExist(mediainfo['name']):
            self.player.createTab(medianame,medianame, controls)   
            #result,control = self.doModal(mediainfo['name'],680,400,'',controls)

    def onXLClick(self, page, listControl, item, itemControl):
        url = self.allxlsdata[page][item]
        xlname = page + ' 线路' + str(item + 1) 
        self.player.play(url, caption=xlname)
    
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = livesplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()