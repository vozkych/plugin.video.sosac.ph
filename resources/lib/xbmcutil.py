# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2011 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import os
import re
import sys
import urllib
import urllib.request
import urllib.parse
import traceback
import http.cookiejar
import time
import socket
import xbmcgui
import xbmcplugin
import xbmc
import xbmcvfs
import xbmcaddon
from html.entities import name2codepoint as n2cp
import json
from . import util
from . import utmain

UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'

sys.path.append(os.path.join(os.path.dirname(__file__), 'usage'))

__scriptid__ = 'plugin.video.sosac.ph'
__addon__ = xbmcaddon.Addon(__scriptid__)
__lang__ = __addon__.getLocalizedString


##
# initializes urllib cookie handler


def init_urllib():
    cj = http.cookiejar.LWPCookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)


def request(url, headers=None):
    if headers is None:
        headers = {}
    debug('request: %s' % url)
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    data = response.read()
    response.close()
    debug('len(data) %s' % len(data))
    return data.decode("utf-8")


def post(url, data):
    postdata = urllib.parse.urlencode(data)
    req = urllib.request.Request(url, postdata)
    req.add_header('User-Agent', UA)
    response = urllib.request.urlopen(req)
    data = response.read()
    response.close()
    return data


def icon(name):
    return 'https://github.com/lzoubek/xbmc-doplnky/raw/dharma/icons/' + name


def substr(data, start, end):
    i1 = data.find(start)
    i2 = data.find(end, i1)
    return data[i1:i2]


def add_dir(name, params, logo='', infoLabels={}, menuItems={}):
    name = decode_html(name)
    if not 'title' in infoLabels:
        infoLabels['title'] = ''
    if logo == None:
        logo = ''
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': 'DefaultFolder.png', 'thumb': logo})
    try:
        liz.setInfo(type='Video', infoLabels=infoLabels)
    except:
        traceback.print_exc()
    items = []
    for mi in menuItems.keys():
        action = menuItems[mi]
        if not type(action) == type({}):
            items.append((mi, action))
        else:
            if 'action-type' in action:
                action_type = action['action-type']
                del action['action-type']
                if action_type == 'list':
                    items.append((mi, 'Container.Update(%s)' % _create_plugin_url(action)))
                elif action_type == 'play':
                    items.append((mi, 'PlayMedia(%s)' % _create_plugin_url(action)))
                else:
                    items.append((mi, 'RunPlugin(%s)' % _create_plugin_url(action)))
            else:
                items.append((mi, 'RunPlugin(%s)' % _create_plugin_url(action)))
    if len(items) > 0:
        liz.addContextMenuItems(items)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=_create_plugin_url(params),
                                       listitem=liz, isFolder=True)


def add_local_dir(name, url, logo='', infoLabels={}, menuItems={}):
    name = decode_html(name)
    infoLabels['Title'] = name
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': 'DefaultFolder.png', 'thumb': logo})
    liz.setInfo(type='Video', infoLabels=infoLabels)
    items = []
    for mi in menuItems.keys():
        items.append((mi, 'RunPlugin(%s)' % _create_plugin_url(menuItems[mi])))
    if len(items) > 0:
        liz.addContextMenuItems(items)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz,
                                       isFolder=True)


def add_video(name, params={}, logo='', infoLabels={}, menuItems={}):
    name = decode_html(name)
    if not 'Title' in infoLabels:
        infoLabels['Title'] = name
    url = _create_plugin_url(params)
    li = xbmcgui.ListItem(name, path=url)
    li.setArt({'icon': 'DefaultVideo.png', 'thumb': logo})
    li.setInfo(type='Video', infoLabels=infoLabels)
    # remove WARNING: XFILE::CFileFactory::CreateLoader - unsupported
    # protocol(plugin) in plugin://....
    li.addStreamInfo('video', {})
    li.setProperty('IsPlayable', 'true')
    items = [(xbmc.getLocalizedString(13347), 'Action(Queue)')]
    for mi in menuItems.keys():
        action = menuItems[mi]
        if not type(action) == type({}):
            items.append((mi, action))
        else:
            if 'action-type' in action:
                action_type = action['action-type']
                del action['action-type']
                if action_type == 'list':
                    items.append((mi, 'Container.Update(%s)' % _create_plugin_url(action)))
                elif action_type == 'play':
                    items.append((mi, 'PlayMedia(%s)' % _create_plugin_url(action)))
                else:
                    items.append((mi, 'RunPlugin(%s)' % _create_plugin_url(action)))
            else:
                items.append((mi, 'RunPlugin(%s)' % _create_plugin_url(action)))

    if len(items) > 0:
        li.addContextMenuItems(items)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li,
                                       isFolder=False)


def _create_plugin_url(params, plugin=sys.argv[0]):
    url = []
    for key in params.keys():
        value = decode_html(params[key])
        # --value = value.encode('ascii','ignore')
        value = value.encode('utf-8')
        url.append(key + '=' + value.hex() + '&')
    return plugin + '?' + ''.join(url)


def reportUsage(addonid, action):
    host = 'xbmc-doplnky.googlecode.com'
    tc = 'UA-3971432-4'
    try:
        utmain.main({'id': addonid, 'host': host, 'tc': tc, 'action': action})
    except:
        pass


def init_usage_reporting(addonid):
    utmain.main({'do': 'reg', 'id': addonid})


def compat_path(path):
    if not sys.platform.startswith('win'):
        if isinstance(path, str):
            return path.encode('utf-8')

    return path


def download_subtitles(url, headers=None, name=None, path=None):
    if url == None or url == '':
        raise RuntimeError("Can't download undefined subtitles")

    util.info("Downloading subtitles from '%s'" % url)
    # define vfs and device paths to download folder
    virt_path = ('special://temp/%s' % __scriptid__) if (path == None or path == '') else path
    real_path = xbmcvfs.translatePath(virt_path)
    # make the device path existing
    real_path_compat = compat_path(real_path) # is it needed?
    if not os.path.exists(real_path_compat):
        os.makedirs(real_path_compat)
    # compute the subtitle filename
    filename = ('xbmc_subs%s.srt' % int(time.time())) if (name == None or name == '') else ('%s.srt' % name)
    # append filename to vfs and device paths
    virt_path = xbmcvfs.makeLegalFilename(xbmcvfs.validatePath('%s/%s' % (virt_path,filename)))
    real_path = xbmcvfs.makeLegalFilename(os.path.join(real_path, filename))
    # download and write the subtitle file
    try:
        subtitles = request(url, headers)
        util.info("Storing subtitles to '%s'" % real_path)
        fo = open(compat_path(real_path), 'w', encoding='utf-8')
        fo.write(subtitles)
        fo.flush()
        os.fsync(fo.fileno())
        fo.close()
    except:
        traceback.print_exc()
        util.error("Failed to download subtitles from '%s' or store them to '%s'!" % (url,real_path))
        return None,None

    return virt_path,real_path


def set_subtitles(listItem, url, headers=None):
    if not (url == None or url == ''):
        virt_path,real_path = download_subtitles(url, headers)
        if (virt_path == None):
            return
        util.info("Setting subtitles from '%s' to playable item" % url)
        listItem.setSubtitles([virt_path])


def load_subtitles(url, headers=None):
    if not (url == None or url == ''):
        virt_path,real_path = download_subtitles(url, headers)
        if (virt_path == None):
            return
        player = xbmc.Player()
        count = 0
        max_count = 99
        while not player.isPlaying() and count < max_count:
            count += 1
            xbmc.sleep(200)
            if count > max_count - 2:
                util.warn("Cannot load subtitles, player timed out")
                return
        util.info("Loading subtitles from '%s' to player" % url)
        player.setSubtitles(virt_path)


def _substitute_entity(match):
    ent = match.group(3)
    if match.group(1) == '#':
        # decoding by number
        if match.group(2) == '':
            # number is in decimal
            return chr(int(ent))
        elif match.group(2) == 'x':
            # number is in hex
            return chr(int('0x' + ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp:
                return chr(cp)
            else:
                return match.group()


def decode_html(data):
    try:
        if not type(data) == str:
            data = str(data, 'utf-8', errors='ignore')
        entity_re = re.compile(r'&(#?)(x?)(\w+);')
        return entity_re.subn(_substitute_entity, data)[0]
    except:
        traceback.print_exc()
        return data


def debug(text):
    xbmc.log(str([text]), xbmc.LOGDEBUG)


def info(text):
    xbmc.log(str([text]))


def error(text):
    xbmc.log(str([text]), xbmc.LOGERROR)


def search_remove(cache, search):
    data = cache.get('search')
    if data == None or data == '':
        data = []
    else:
        data = eval(data)
    data.remove(search)
    cache.set('search', repr(data))


def search_replace(cache, search, replacement):
    data = cache.get('search')
    if data == None or data == '':
        data = []
    else:
        data = eval(data)
    index = data.index(search)
    if index > -1:
        data[index] = replacement
        cache.set('search', repr(data))


def search_add(cache, search, maximum):
    data = cache.get('search')
    if data == None or data == '':
        data = []
    else:
        data = eval(data)
    if search in data:
        data.remove(search)
    data.insert(0, search)
    remove = len(data) - maximum
    if remove > 0:
        for i in range(remove):
            data.pop()
    cache.set('search', repr(data))


def search_list(cache):
    data = cache.get('search')
    if data == None or data == '':
        data = []
    else:
        data = eval(data)
    return data


# obsolete functions ..


def get_searches(addon, server):
    local = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    c_local = compat_path(local)
    if not os.path.exists(c_local):
        os.makedirs(c_local)
    c_local = compat_path(os.path.join(local, server))
    if not os.path.exists(c_local):
        return []
    f = open(c_local, 'r')
    data = f.read()
    searches = json.loads(str(data.decode('utf-8', 'ignore')))
    f.close()
    return searches


def add_search(addon, server, search, maximum):
    searches = []
    local = xbmcvfs.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    c_local = compat_path(local)
    if not os.path.exists(c_local):
        os.makedirs(c_local)
    c_local = compat_path(os.path.join(local, server))
    if os.path.exists(c_local):
        f = open(c_local, 'r')
        data = f.read()
        searches = json.loads(str(data.decode('utf-8', 'ignore')))
        f.close()
    if search in searches:
        searches.remove(search)
    searches.insert(0, search)
    remove = len(searches) - maximum
    if remove > 0:
        for i in range(remove):
            searches.pop()
    f = open(c_local, 'w')
    f.write(json.dumps(searches, ensure_ascii=True))
    f.close()


def delete_search_history(addon, server):
    local = xbmcvfs.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    c_local = compat_path(local)
    if not os.path.exists(c_local):
        return
    c_local = compat_path(os.path.join(local, server))
    if os.path.exists(c_local):
        os.remove(c_local)


def remove_search(addon, server, search):
    local = xbmcvfs.translatePath(addon.getAddonInfo('profile')).decode('utf-8')
    c_local = compat_path(local)
    if not os.path.exists(c_local):
        return
    c_local = compat_path(os.path.join(local, server))
    if os.path.exists(c_local):
        f = open(c_local, 'r')
        data = f.read()
        searches = json.loads(str(data.decode('utf-8', 'ignore')))
        f.close()
        searches.remove(search)
        f = open(c_local, 'w')
        f.write(json.dumps(searches, ensure_ascii=True))
        f.close()


# obsolete funcionts END


def download(addon, filename, url, local, notifyFinishDialog=True, headers={}):
    try:
        util.info('Downloading %s to %s' % (url, local))
    except:
        util.info('Downloading ' + url)
    local = xbmcvfs.makeLegalFilename(local)
    try:
        filename = util.replace_diacritic(util.decode_html(filename))
    except:
        filename = 'Video soubor'
    icon = os.path.join(addon.getAddonInfo('path'), 'icon.png')
    notifyEnabled = addon.getSetting('download-notify') == 'true'
    notifyEvery = addon.getSetting('download-notify-every')
    notifyPercent = 1
    if int(notifyEvery) == 0:
        notifyPercent = 10
    if int(notifyEvery) == 1:
        notifyPercent = 5

    def encode(string):
        return u' '.join(string).encode('utf-8')

    def notify(title, message, time=10000):
        try:
            xbmcgui.Dialog().notification(encode(title), encode(message), time=time, icon=icon,
                                          sound=False)
        except:
            traceback.print_exc()
            error('unable to show notification')

    def callback(percent, speed, est, filename):
        if percent == 0 and speed == 0:
            notify(xbmc.getLocalizedString(13413), filename)
            return
        if notifyEnabled:
            if percent > 0 and percent % notifyPercent == 0:
                esTime = '%ss' % est
                if est > 60:
                    esTime = '%sm' % int(est / 60)
                message = xbmc.getLocalizedString(24042).format(percent) + ' - {0} KB/s {1}'.format(speed, esTime)
                notify(message, filename)

    downloader = Downloader(callback)
    result = downloader.download(url, local, filename, headers)
    try:
        if result == True:
            if xbmc.Player().isPlaying():
                notify(xbmc.getLocalizedString(20177), filename)
            else:
                if notifyFinishDialog:
                    xbmcgui.Dialog().ok(xbmc.getLocalizedString(20177), filename)
                else:
                    notify(xbmc.getLocalizedString(20177), filename)
        else:
            notify(xbmc.getLocalizedString(257), filename)
            xbmcgui.Dialog().ok(filename, xbmc.getLocalizedString(257) + ' : ' + result)
    except:
        traceback.print_exc()


class Downloader(object):

    def __init__(self, callback=None):
        self.init_time = time.time()
        self.callback = callback
        self.gran = 50
        self.percent = -1

    def download(self, remote, local, filename=None, headers={}):
        class MyURLopener(urllib.request.FancyURLopener):
            def http_error_default(self, url, fp, errcode, errmsg, headers):
                self.error_msg = 'Download failed, error : ' + str(errcode)

        if not filename:
            filename = os.path.basename(local)
        self.filename = filename
        if self.callback:
            self.callback(0, 0, 0, filename)
        socket.setdefaulttimeout(60)
        opener = MyURLopener()
        for header in headers:
            opener.addheader(header, headers[header])
        try:
            opener.retrieve(remote, local, reporthook=self.dlProgress)
            if hasattr(opener, 'error_msg'):
                return opener.error_msg
            return True
        except socket.error:
            errno, errstr = sys.exc_info()[:2]
            if errno == socket.timeout:
                return 'Download failed, connection timeout'
        except:
            traceback.print_exc()
            errno, errstr = sys.exc_info()[:2]
            return str(errstr)

    def dlProgress(self, count, blockSize, totalSize):
        if count % self.gran == 0 and not count == 0:
            percent = int(count * blockSize * 100 / totalSize)
            newTime = time.time()
            diff = newTime - self.init_time
            self.init_time = newTime
            if diff <= 0:
                diff = 1
            speed = int(((1 / diff) * blockSize * self.gran) / 1024)
            est = int((totalSize - int(count * blockSize)) / 1024 / speed)
            if self.callback and not self.percent == percent:
                self.callback(percent, speed, est, self.filename)
            self.percent = percent


_diacritic_replace = {u'\u00f3': 'o',
                      u'\u0213': '-',
                      u'\u00e1': 'a',
                      u'\u010d': 'c',
                      u'\u010c': 'C',
                      u'\u010f': 'd',
                      u'\u010e': 'D',
                      u'\u00e9': 'e',
                      u'\u011b': 'e',
                      u'\u00ed': 'i',
                      u'\u0148': 'n',
                      u'\u0159': 'r',
                      u'\u0161': 's',
                      u'\u0165': 't',
                      u'\u016f': 'u',
                      u'\u00fd': 'y',
                      u'\u017e': 'z'
                      }


def replace_diacritic(string):
    ret = []
    for char in string:
        if char in _diacritic_replace:
            ret.append(_diacritic_replace[char])
        else:
            ret.append(char)
    return ''.join(ret)
