#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit, argv
from os  import path, getenv

from random     import choice
from urllib     import quote
from urllib2    import urlopen
from win32gui   import MessageBox
from webbrowser import open_new
from socket     import setdefaulttimeout

from wx.lib.hyperlink import HyperLinkCtrl

import wx
import time
import hashlib
import _winreg
import win32process, win32api, win32con

import log
import quotes

log = log.Log()

if __name__ == "__main__":
    log._debug_ = True

inlineimages = True
if inlineimages:
    from images import images

from main import _version_, _threaded_

wxID_IPHONE_AUTO = 1110
wxID_IPHONE_MANUAL = 1111

wxID_IPHONE = 1010
wxID_IPOD = 1009
wxID_DISABLE = 1000
wxID_PAUSE = 1001
wxID_LASTFMHOME = 1002
wxID_LASTFMUSER = 1003
wxID_LASTFMAPP = 1004
wxID_PREFS = 1005
wxID_STATS = 1006
wxID_EXIT = 1007
wxID_TIMER = 1008
wxID_STATSTIMER = 1009

wxID_USERNAME = 2000
wxID_PASSWORD = 2001
wxID_IPODSUPPORT = 2002
wxID_IPODMULTIPLE = 2003
#wxID_XMLFILE = 2004
#wxID_XMLBUTTON = 2005
wxID_LOGINRUN = 2006
wxID_IPODMANUAL = 2007
wxID_DONATE = 2008

wxID_SONGSSUB = 3001
wxID_SONGSQUE = 3002
wxID_SUBATTEM = 3003
wxID_SUCCSUBS = 3004
wxID_PLAYING = 3005
wxID_LASTSUB = 3006
wxID_ITUNES = 3007
wxID_OPENLOG = 3008
wxID_PLAYTRK = 3009
wxID_PLAYART = 3010
wxID_LASTART = 3011
wxID_LASTTRK = 3012
wxID_PROFILE = 3013

PREFS_WIDTH = 350
PREFS_HEIGHT = 400
STATS_WIDTH = 300
STATS_HEIGHT = 330
LOGIN_RUN = False


class DummyClass:
    def __init__(self):
        #s
        self.lastserverresponse = []
        self.lastrawserverresponse = "OK"
        self.lastsubmitted = {}
        self.playingsong = {'artist':"Locanda Delle Fate", 'name':unicode("Forse Le Lucciole Non Si Amano Pi","utf-8")}
        self.songssubmitted = 1
        self.songsqueued = 2
        self.submissionattempts = 3
        self.successfullsubmissions = 4
        self.pausesubmissions = False
        self.disablesubmissions = False

        #main
        self.updateonunmount = False
        self.ipodmounted = False

        #main
        self.prefs = {'username': "dave",
                      'password': "",
                      'passlength': 8,
                      'ipodsupport': False,
                      'ipodmultiple': False,
                      'xmlfile': "",
                      'ipodmanual': False}

        #itunes
        self.connected = True

    #s
    def submissionstate(self,mode,bool):
        if mode == "disable":
            if not bool and self.disablesubmissions:
                self.disablesubmissions = False
            elif bool:
                self.disablesubmissions = True
        else:
            if not bool and self.pausesubmissions:
                self.pausesubmissions = False
            elif bool:
                self.pausesubmissions = True

    #main
    def ready(self):
        return True
    def core(self):
        pass
    def drivecheck(self):
        pass
    def ipodcheck(self):
        pass

    #itunes
    def pumpevents(self):
        pass
    def cleanup(self):
        pass

    #f
    def _pickle(self,name,data):
        print "Saving new prefs: "+repr(main.prefs)


class DummyException(Exception):
    pass

class PrefsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "iSproggler Preferences", (-1,-1), wx.Size(PREFS_WIDTH,PREFS_HEIGHT))

        if inlineimages:
            #bitmap = wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(imagesdict['lastfm.png'])))
            lastfm_bitmap = images("lastfm.png")
            donate_bitmap = images("donate.gif")
        else:
            lastfm_image = wx.Image(path.join(path.abspath(path.dirname(argv[0])),"data\\lastfm.png"), wx.BITMAP_TYPE_PNG)
            lastfm_bitmap = wx.BitmapFromImage(lastfm_image)
            donate_image = wx.Image(path.join(path.abspath(path.dirname(argv[0])),"data\\donate.gif"), wxBITMAP_TYPE_GIF)
            donate_bitmap = wx.BitmapFromImage(donate_image)

        #wx.StaticBitmap(self, -1, bitmap, wx.DLG_PNT(self,70,30))
        #wx.StaticText(self, -1, "iSproggler Version %s" % _version_, wx.DLG_PNT(self,80,80))
        self.box = wx.BoxSizer(wx.VERTICAL)
        #self.box.Add((30, 30), 0)
        #self.box.Add(wx.StaticBitmap(self, -1, lastfm_bitmap), 0, wx.ALIGN_CENTER)
        #self.box.Add((15, 15), 0)

        self.box.Add((15, 15), 0)
        self.box.Add(wx.StaticBitmap(self, -1, lastfm_bitmap), 0, wx.ALIGN_CENTER)
        self.box.Add((10, 10), 0)
        self.box.Add(wx.StaticText(self, -1, "iSproggler Version %s" % _version_), 0, wx.ALIGN_CENTER)
        self.box.Add((25, 25), 0)

        self.paypal = wx.StaticBitmap(self, wxID_DONATE, donate_bitmap)
        self.paypal.Bind(wx.EVT_LEFT_DOWN, self.Donate)
        self.box.Add(self.paypal, 0, wx.ALIGN_CENTER)
        #self.SetSizer(self.box)

        wx.StaticText(self, -1, "Username:", wx.DLG_PNT(self,7,116))
        self.username = wx.TextCtrl(self, wxID_USERNAME, "", wx.DLG_PNT(self,50,114))
        self.username.SetValue(main.prefs['username'])
        wx.StaticText(self, -1, "Password:", wx.DLG_PNT(self,7,133))
        self.password = wx.TextCtrl(self, wxID_PASSWORD, "", wx.DLG_PNT(self,50,131), wx.DefaultSize, wx.TE_PASSWORD)
        if main.prefs['password'] != "":
            self.password.SetValue("*" * int(main.prefs['passlength']))

        self.ipodsupport = wx.CheckBox(self, wxID_IPODSUPPORT, "Enable iPod Support", wx.DLG_PNT(self,7,151))
        self.ipodmultiple = wx.CheckBox(self, wxID_IPODMULTIPLE, "Enable Multiple iPod Plays", wx.DLG_PNT(self,100,151))
        self.ipodmanual = wx.CheckBox(self, wxID_IPODMANUAL, "Only Check Manually Updated iPods", wx.DLG_PNT(self,100,166))

        #wx.StaticText(self, -1, "iTunes Library XML File:", wx.DLG_PNT(self,7,167))
        #self.xmlfile = wx.TextCtrl(self, wxID_XMLFILE, "", wx.DLG_PNT(self,7,180),wx.DLG_SZE(self,174,-1),wx.TE_READONLY)
        self.xmlfile = ""
        #if main.prefs['ipodsupport']:
        #    self.xmlfile.SetValue(str(main.prefs['xmlfile']))
        #self.xmlbutton = wx.Button(self, wxID_XMLBUTTON, "Choose", wx.DLG_PNT(self,185,180),(60,20))

        self.loginrun = wx.CheckBox(self, wxID_LOGINRUN, "Run When Windows Starts", wx.DLG_PNT(self,7,186))

        #wx.Button(self, wx.ID_CANCEL, "Cancel", wx.DLG_PNT(self,120,213))
        #okbutton = wx.Button(self, wx.ID_OK, "OK", wx.DLG_PNT(self,175,213)).SetDefault()
        #wx.Button(self, wx.ID_CANCEL, "Cancel", wx.Point(179,346))
        #okbutton = wx.Button(self, wx.ID_OK, "OK", wx.Point(261,346)).SetDefault()
        #self.vbuttonbox = wx.BoxSizer(wx.VERTICAL)
        self.hbuttonbox = wx.BoxSizer(wx.HORIZONTAL)
        #self.box.Add((0,235),0,wx.GROW)
        self.box.Add((-1,-1), -1, wx.GROW|wx.ALL)
        cancelbutton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.hbuttonbox.Add(cancelbutton)
        self.hbuttonbox.Add((7, 7))
        okbutton = wx.Button(self, wx.ID_OK, "OK")
        self.hbuttonbox.Add(okbutton)
        self.hbuttonbox.Add((7, 7))
        #self.vbuttonbox.Add(self.hbuttonbox, 0, wx.ALIGN_RIGHT)
        #self.vbuttonbox.Add((7, 7), 0)
        self.box.Add(self.hbuttonbox, 0, wx.ALIGN_RIGHT)
        self.box.Add((7, 7))
        #self.SetSizer(self.vbuttonbox)
        self.SetSizer(self.box)

        #self.ipodmultiple.Disable()
        if main.prefs['ipodsupport']:
            self.xmlfile = main.prefs['xmlfile']
            self.ipodsupport.SetValue(True)
        else:
            self.ipodmanual.Disable()
            self.ipodmultiple.Disable()
            #self.ipodmanual.Disable()

        if main.prefs['ipodmultiple']:
            self.ipodmultiple.SetValue(True)
        if main.prefs['ipodmanual']:
            self.ipodmanual.SetValue(True)

        self.loginrun.SetValue(self.LoginRun())
        okbutton.SetDefault()

        wx.EVT_CHECKBOX(self, wxID_IPODSUPPORT, self.iPodSupport)
        wx.EVT_CHECKBOX(self, wxID_IPODMULTIPLE, self.iPodMultiple)
        wx.EVT_CHECKBOX(self, wxID_IPODMANUAL, self.iPodManual)

        #wx.EVT_LEFT_DOWN(self, wxID_DONATE, self.Donate)
        #self.Bind(wx.EVT_LEFT_DOWN, wxID_DONATE, self.Donate)

    def Donate(self, event):
        try:
            open_new("https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=david%2enicolson%40gmail%2ecom&item_name=iSproggler%20Donation&no_shipping=0&no_note=1&tax=0&currency_code=USD&lc=AU&bn=PP%2dDonationsBF&charset=UTF%2d8")
        except:
            pass

    def iPodSupport(self, event):
        if self.ipodsupport.GetValue():
            try:
                #reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
                #key = _winreg.OpenKey(reg, r"Software\Apple Computer, Inc.\iTunes", 0, _winreg.KEY_READ)
                #folder = _winreg.QueryValueEx(key, "Win2KMyMusicFolder")[0]
                #log.verb("Win2KMyMusicFolder folder: %s" % folder)
                #mydocs = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_PERSONAL)
                try:
                    reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
                    key = _winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders", 0, _winreg.KEY_READ)
                    mymusic = _winreg.QueryValueEx(key, "My Music")[0]
                    log.verb("My Music folder: %s" % mymusic)
                except:
                    mymusic = path.join(getenv("USERPROFILE"),"My Documents","My Music")
                xmlfile = path.join(path.join(mymusic,"iTunes"),"iTunes Music Library.xml")

                if s.lastsong == {}:
                    s.lastsong = {'album': "",
                                  'name': "",
                                  'artist': "",
                                  'mbid': None,
                                  'location': "",
                                  'duration': 0,
                                  'position': 0,
                                  'playcount': 0,
                                  'id': 0,
                                  'time': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()+10))}
                    f._writehistory(s.lastsong)
                MessageBox(0,"iPod support is now enabled.\n\nSongs played after %s UTC on an iPod will now be submitted when the iPod is synced.\n\nIf the iPod is automatically updated, the process automatic. If disk use is enabled, eject the iPod after it has synced.\n\nIf \"Manually manage music [and videos]\" is checked in the iPod settings, select the \"Update iPod\" iSproggler menu item when the iPod is plugged in. If there is not a Smart Playlist on the iPod, create a one titled \"Recently Played\" with the condition: Last Played in the last 2 weeks." % s.lastsong['time'],"iSproggler",1)
                log.verb("iPod support enabled")
                log.verb("iPod-played songs played after %s UTC will be submitted" % s.lastsong['time'])

                if path.exists(xmlfile):
                    log.verb("Found XML file: %s" % xmlfile)
                    self.xmlfile = xmlfile
                    self.ipodmultiple.Enable()
                    self.ipodmanual.Enable()
                else:
                    log.verb("Did not find XML file: %s" % xmlfile)
                    MessageBox(0,"The iTunes Music Library.xml file is used to determine iPod-played songs, it was not found in the default location: %s\n\nIf iTunes is installed, please locate this file." % xmlfile,"iSproggler",1)
                    raise DummyException
            except DummyException:
                self.XMLDialog()

            #self.xmlfile.Enable()
            #self.xmlbutton.Enable()
        else:
            #self.ipodmultiple.SetValue(False)
            #self.ipodmanual.SetValue(False)
            self.ipodmultiple.Disable()
            self.ipodmanual.Disable()

    def XMLDialog(self):
        defaultpath = path.join(getenv("USERPROFILE"),"My Documents")
        #xmldlg = wx.FileDialog(self, "Choose your XML file...", defaultpath, "", "iTunes Music Library.xml", wx.OPEN)
        xmldlg = wx.FileDialog(self, "Choose your XML file...", defaultpath, "", "*.xml", wx.OPEN)
        if xmldlg.ShowModal() == wx.ID_OK:
            self.xmlfile = xmldlg.GetPath()
            log.verb("Manually found XML file: %s" % self.xmlfile)
            self.ipodmultiple.Enable()
            self.ipodmanual.Enable()
        else:
            self.ipodsupport.SetValue(False)
            #for some reason Disable() doesn't work here
            self.ipodmultiple.Disable()
            #self.ipodmultiple.SetValue(False)
            self.ipodmanual.Disable()
            #self.ipodmanual.SetValue(False)

        xmldlg.Destroy()

    def iPodMultiple(self, event):
        if self.ipodmultiple.GetValue():
            if self.ipodmanual.GetValue():
                self.ipodmanual.SetValue(False)

    def iPodManual(self, event):
        if self.ipodmanual.GetValue():
            if self.ipodmultiple.GetValue():
                self.ipodmultiple.SetValue(False)

    def LoginRun(self):
        try:
            reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
            key = _winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, _winreg.KEY_READ)
            val = _winreg.QueryValueEx(key, "iSproggler")[0]
            if val[1:-1] == argv[0]:
                globals()['LOGIN_RUN'] = True
                return True
        except:
            globals()['LOGIN_RUN'] = False
        return False

class StatsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "iSproggler Statistics", (-1,-1), wx.Size(STATS_WIDTH,STATS_HEIGHT))

        wx.StaticText(self, -1, "Songs Submitted:", wx.DLG_PNT(self,7,5))
        self.songssubmitted = wx.StaticText(self, wxID_SONGSSUB, "0", wx.DLG_PNT(self,175,5))
        wx.StaticText(self, -1, "Songs Queued for Submission:", wx.DLG_PNT(self,7,15))
        self.songsqueued = wx.StaticText(self, wxID_SONGSQUE, "0", wx.DLG_PNT(self,175,15))
        wx.StaticText(self, -1, "Submission Attempts:", wx.DLG_PNT(self,7,25))
        self.submissionattempts = wx.StaticText(self, wxID_SUBATTEM, "0", wx.DLG_PNT(self,175,25))
        wx.StaticText(self, -1, "Successful Submissions:", wx.DLG_PNT(self,7,35))
        self.successfullsubmissions = wx.StaticText(self, wxID_SUCCSUBS, "0", wx.DLG_PNT(self,175,35))

        wx.StaticText(self, -1, "Last Submitted Song:", wx.DLG_PNT(self,7,55))
        wx.StaticText(self, -1, "Playing Song:", wx.DLG_PNT(self,7,90))
        wx.StaticText(self, -1, "iTunes Status:", wx.DLG_PNT(self,7,127))
        self.itunesstatus = wx.StaticText(self, wxID_ITUNES, "", wx.DLG_PNT(self,95,127))
        wx.StaticText(self, -1, "Last Server Response:", wx.DLG_PNT(self,7,137))
        self.lastresponse = wx.StaticText(self, wxID_ITUNES, "", wx.DLG_PNT(self,95,137))

        self.lnkNowPlayingTrack = HyperLinkCtrl(self, wxID_PLAYTRK, '', wx.Point(10,163), URL='')
        self.lnkNowPlayingArtist = HyperLinkCtrl(self, wxID_PLAYART, '', wx.Point(10,177), URL='')

        self.lnkLastPlayedTrack = HyperLinkCtrl(self, wxID_LASTTRK, '', wx.Point(10,105), URL='')
        self.lnkLastPlayedArtist = HyperLinkCtrl(self, wxID_LASTART, '', wx.Point(10,119), URL='')

        self.lnkProfile = HyperLinkCtrl(self, wxID_PROFILE, 'Profile', wx.Point(10,246),
                                        URL='http://last.fm/user/%s' % main.prefs['username'])

        self.lnkProfile.SetColours(visited=wx.Colour(0, 0, 255))
        self.lnkNowPlayingTrack.SetColours(visited=wx.Colour(0, 0, 255))
        self.lnkLastPlayedTrack.SetColours(visited=wx.Colour(0, 0, 255))
        self.lnkNowPlayingArtist.SetColours(visited=wx.Colour(0, 0, 255))
        self.lnkLastPlayedArtist.SetColours(visited=wx.Colour(0, 0, 255))

        #openlogbutton = wx.Button(self, wxID_OPENLOG, "Open Log")

        #self.hbuttonbox_openlog = wx.BoxSizer(wx.HORIZONTAL)
        #self.hbuttonbox_openlog.Add(openlogbutton)
        #self.hbuttonbox_openlog.Add((7, 7))
        #self.hbuttonbox.Add((-1,-1),-1, wxEXPAND|wx.ALL)
        #self.hbuttonbox.Add(okbutton, 0, wx.ALIGN_RIGHT)
        #self.hbuttonbox.Add((7, 7))

        #self.gridsizer = wxGridSizer(2,0,0)
        #self.gridsizer.AddMany([openlogbutton,okbutton])

        #self.box.Add(self.hbuttonbox_openlog, 0, wx.ALIGN_RIGHT)
        #self.box.Add((7, 7))

        wx.Button(self, wx.ID_OK, "OK", wx.DLG_PNT(self,140,168))
        wx.Button(self, wxID_OPENLOG, "Open Log", wx.DLG_PNT(self,7,168))

        self.SetValues()

        wx.EVT_BUTTON(self, wxID_OPENLOG, self.OpenLog)

        self.timer = wx.Timer(self, wxID_STATSTIMER)
        wx.EVT_TIMER(self, wxID_STATSTIMER, self.OnTimer)
        self.timer.Start(1000)

        self.first = True


    def OpenLog(self, event):
        filepath = path.join(getenv("APPDATA"),"iSproggler\\iSproggler.log")
        #Windows and Notepad couldn't open the temp files, Firefox could though
        #try:
        #    import tempfile
        #    logfile = open(logpath,"rb").read()
        #    logfile = logfile.replace("\n","\r\n")
        #    templog = tempfile.NamedTemporaryFile("wb+")
        #    templog.write(logfile)
        #    filepath = templog.name
        #except:
        #    filepath = logpath
        try:
            #TODO: open in a \n editor like anything but NotePad, find cause of Exception
            open_new(filepath)
        except:
            pass

    def OnTimer(self, event):
        self.SetValues()
        if self.first:
            self.CheckVersion()

    def _sum_version(self,version_str):
        base = 1
        version = 0
        pieces = version_str.split(".")[::-1]
        for piece in pieces:
            version += int(piece) * base
            base *= 10
        return version

    def CheckVersion(self):
        self.first = False

        #try:
            #setdefaulttimeout(12)
            #null, newversion, versiontext = urlopen("").readlines()
            #newversion = newversion[:-1]
            #versiontext = versiontext[:-1]
            #if self._sum_version(newversion) > self._sum_version(_version_):
            #    wx.StaticText(self, -1, "New Version: "+newversion+versiontext, wx.DLG_PNT(self,7,155))
            #log.debug(newversion+versiontext)
        #except Exception, err:
            #log.warning("Version checking error: [%s:%s]" % (Exception,err))

    def SetValues(self):
        self.songssubmitted.SetLabel(str(s.songssubmitted))
        self.songsqueued.SetLabel(str(s.songsqueued))
        self.submissionattempts.SetLabel(str(s.submissionattempts))
        self.successfullsubmissions.SetLabel(str(s.successfullsubmissions))

        if s.lastsubmitted != {}:
            self.lnkLastPlayedTrack.SetURL("http://last.fm/music/%s/_/%s" % (quote(s.lastsubmitted['artist'].encode('utf-8').replace('/','%2F')),
                                                                             quote(s.lastsubmitted['name'].encode('utf-8').replace('/','%2F'))))
            try:
                self.lnkLastPlayedTrack.SetLabel(s.lastsubmitted['name'])
            except:
                self.lnkLastPlayedTrack.SetLabel('track contains non-displayable characters')
            self.lnkLastPlayedArtist.SetURL("http://last.fm/music/%s" % (quote(s.lastsubmitted['artist'].encode('utf-8').replace('/','%2F'))))
            try:
                self.lnkLastPlayedArtist.SetLabel(s.lastsubmitted['artist'])
            except:
                self.lnkLastPlayedArtist.SetLabel('artist contains non-displayable characters')

        playingsong = s.playingsong

        if playingsong != None:
            self.lnkNowPlayingTrack.SetURL("http://last.fm/music/%s/_/%s" % (quote(playingsong['artist'].encode('utf-8').replace('/','%2F')),
                                                                             quote(playingsong['name'].encode('utf-8').replace('/','%2F'))))
            self.lnkNowPlayingArtist.SetURL("http://last.fm/music/%s" % (quote(playingsong['artist'].encode('utf-8').replace('/','%2F'))))
            try:
                self.lnkNowPlayingTrack.SetLabel(playingsong['name'])
            except:
                self.lnkNowPlayingTrack.SetLabel('track contains non-displayable characters')

            try:
                self.lnkNowPlayingArtist.SetLabel(playingsong['artist'])
            except:
                self.lnkNowPlayingArtist.SetLabel('artist contains non-displayable characters')

        else:
            self.lnkNowPlayingTrack.SetURL('')
            self.lnkNowPlayingTrack.SetLabel('')
            self.lnkNowPlayingArtist.SetURL('')
            self.lnkNowPlayingArtist.SetLabel('')

        try:
            if itunes.Events.suspended:
                itunesstatus = "Busy"
            elif itunes.Events.playing:
                itunesstatus = "Playing"
            elif itunes.Events.stopped:
                itunesstatus = "Stopped"
            elif itunes.Events.quit:
                itunesstatus = "Quitting"
            else:
                itunesstatus = ""
        except:
            itunesstatus = ""

        self.itunesstatus.SetLabel(itunesstatus)
        self.lastresponse.SetLabel(s.lastrawserverresponse)


class TaskBarApp(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (1,1), style=wx.FRAME_NO_TASKBAR)

        self.iconstatus = 0
        #self.pathtoself = path.split(argv[0])[0]
        self.pathtoself = path.abspath(path.dirname(argv[0]))
        self.ipodmenuenabled = False

        self.statsdlgshown = False
        self.prefsdlgshown = False

        self.changesuccessicon = False
        self.lastsubtime = -1

        self.submissions_manually_disabled = False
        self.quotes = True

        if wx.Platform == "__WXMSW__":
            self.tbi = wx.TaskBarIcon()
            if inlineimages:
                icon = images("normal.ico")
            else:
                icon = wx.Icon(path.join(self.pathtoself,"data\\normal.ico"), wx.BITMAP_TYPE_ICO)
            self.tbi.SetIcon(icon, "iSproggler")
            self.tbi.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRight)
            self.tbi.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDouble)

        self.menu = wx.Menu()
        #if main.prefs['ipodsupport']:
        self.submenu = wx.Menu()
        self.submenu.Append(wxID_IPHONE_AUTO,"&Automatic")
        self.submenu.Append(wxID_IPHONE_MANUAL,"&Manual")
        self.menu.AppendMenu(-1,"Update iP&hone/iPod Touch",self.submenu)
        self.menu.Append(wxID_IPOD, "&Update iPod"," Update iPod")
        self.menu.AppendSeparator()
        self.ipodmenuenabled = True
        self.menu.Append(wxID_DISABLE, "&Disable Submissions"," Disable Submissions")
        self.menu.Append(wxID_PAUSE, "Pause Su&bmissions"," Pause Submissions")
        self.menu.AppendSeparator()
        self.menu.Append(wxID_LASTFMHOME, "&Last.fm Homepage"," Go to Last.fm Homepage")
        self.menu.Append(wxID_LASTFMUSER, "Last.fm User &Page"," Go to Last.fm User Page")
        self.menu.Append(wxID_LASTFMAPP, "Last.fm &iSproggler Page"," Go to Last.fm iSproggler Page")
        self.menu.AppendSeparator()
        self.menu.Append(wxID_STATS, "&Statistics"," Show Statistics")
        self.menu.Append(wxID_PREFS, "Pre&ferences..."," Show Preferences...")
        self.menu.Append(wxID_EXIT, "E&xit"," Quit iSproggler")

        #wx.EVT_MENU(self, wxID_DISABLE, self.OnDisableSubmissions)
        #wx.EVT_MENU(self, wxID_PAUSE, self.OnPauseSubmissions)
        #wx.EVT_MENU(self, wxID_LASTFMHOME, self.OnLastfmHomepage)
        #wx.EVT_MENU(self, wxID_LASTFMUSER, self.OnLastfmUserPage)
        #wx.EVT_MENU(self, wxID_STATS, self.OnStatistics)
        #wx.EVT_MENU(self, wxID_PREFS, self.OnPreferences)
        #wx.EVT_MENU(self, wxID_EXIT, self.OnExit)

        if wx.Platform != "__WXMSW__":
            self.tbi = self

        #if main.prefs['ipodsupport']:
        self.tbi.Bind(wx.EVT_MENU, self.OnUpdateiPhoneAuto, id=wxID_IPHONE_AUTO)
        self.tbi.Bind(wx.EVT_MENU, self.OnUpdateiPhoneManual, id=wxID_IPHONE_MANUAL)
        self.tbi.Bind(wx.EVT_MENU, self.OnUpdateiPod, id=wxID_IPOD)
        self.tbi.Bind(wx.EVT_MENU, self.OnDisableSubmissions, id=wxID_DISABLE)
        self.tbi.Bind(wx.EVT_MENU, self.OnPauseSubmissions, id=wxID_PAUSE)
        self.tbi.Bind(wx.EVT_MENU, self.OnLastfmHomepage, id=wxID_LASTFMHOME)
        self.tbi.Bind(wx.EVT_MENU, self.OnLastfmUserPage, id=wxID_LASTFMUSER)
        self.tbi.Bind(wx.EVT_MENU, self.OnLastfmAppPage, id=wxID_LASTFMAPP)
        self.tbi.Bind(wx.EVT_MENU, self.OnStatistics, id=wxID_STATS)
        self.tbi.Bind(wx.EVT_MENU, self.OnPreferences, id=wxID_PREFS)
        self.tbi.Bind(wx.EVT_MENU, self.OnExit, id=wxID_EXIT)

        if not main.ready():
            log.verb("Preferences need to be set")
            self.OnPreferences(-1)

        if wx.Platform != "__WXMSW__":
            wx.Frame.__init__(self,NULL, -1, "iSproggler")
            self.Show(True)
            menubar = wx.MenuBar()
            menubar.Append(self.menu, "iSproggler")
            self.SetMenuBar(menubar)

        self.timer = wx.Timer(self, wxID_TIMER)
        #wx.EVT_TIMER(self, wxID_TIMER, self.OnTimer)
        self.Bind(wx.EVT_TIMER, self.OnTimer, id=wxID_TIMER)
        self.timer.Start(1000)
        self.coretimer = 10
        self.SetWindowSize()

        if main.prefs['ipodsupport']:
            if not main.ipodmounted:
                try:
                    self.menu.Enable(wxID_IPOD,False)
                    self.ipodmenuenabled = False
                except:
                    log.warning("Exception raised when disabling the Update iPod menu")
        else:
            try:
                self.menu.Enable(wxID_IPOD,False)
                log.verb("Disabling \"Update iPod\" menu item as iPod is support is not enabled")
                self.ipodmenuenabled = False
            except:
                log.warning("Exception raised when disabling the Update iPod menu")

        if s.pausesubmissions:
            self.menu.SetLabel(wxID_PAUSE, "Resume Submissions")
            self.SetBlueIcon("Submissions Paused")
            self.menu.Enable(wxID_DISABLE,False)
            log.verb("Paused submission state restored")
        elif s.disablesubmissions:
            self.menu.SetLabel(wxID_DISABLE, "Enable Submissions")
            self.SetBlueIcon("Submissions Disabled")
            self.menu.Enable(wxID_PAUSE,False)
            log.verb("Disabled submission state restored")

    def SetWindowSize(self):
        try:
            reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
            key = _winreg.OpenKey(reg, r"Control Panel\Desktop\WindowMetrics", _winreg.KEY_READ)
            dpi = _winreg.QueryValueEx(key, "AppliedDPI")[0]
        except:
            dpi = 96

        try:
            ratio = int(dpi) / 96.0
            if ratio != 1:
                globals()['PREFS_WIDTH'] = int(ratio * PREFS_WIDTH)
                globals()['PREFS_HEIGHT'] = int(ratio * PREFS_HEIGHT)
                globals()['STATS_WIDTH'] = int(ratio * STATS_WIDTH)
                globals()['STATS_HEIGHT'] = int(ratio * STATS_HEIGHT)
                log.verb("Adjusting dialog sizes to ratio %f (%d,%d,%d,%d)" % (ratio,PREFS_WIDTH,PREFS_HEIGHT,STATS_WIDTH,STATS_HEIGHT))
        except ValueError:
            log.warning("Bad DPI value read from registry")

    def _lastfm_running(self):
        processes = win32process.EnumProcesses()
        for pid in processes:
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            except:
                continue
            try:
                exe = win32process.GetModuleFileNameEx(handle, 0)
                if path.split(exe)[1].lower() == "lastfm.exe":
                    return True
            except:
                pass
        return False

    def _enable_submissions(self,message):
        log.verb(message)
        self.menu.SetLabel(wxID_DISABLE, "Disable Submissions")
        self.SetRedIcon(self.SetIconQuote())
        self.menu.Enable(wxID_PAUSE,True)
        s.submissionstate("disable",False)

    def _disable_submissions(self,message):
        log.verb(message)
        self.menu.SetLabel(wxID_DISABLE, "Enable Submissions")
        self.SetBlueIcon("Submissions Disabled")
        self.menu.Enable(wxID_PAUSE,False)
        s.submissionstate("disable",True)

    def LastFMCheck(self):
        if self.submissions_manually_disabled:
            return
        if not self._lastfm_running():
            if s.disablesubmissions:
                self._enable_submissions("Enabling submissions as the Last.fm software is not running")

            return
        try:
            reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
            key = _winreg.OpenKey(reg, r"Software\Last.fm\Client\Users", _winreg.KEY_READ)
            user = _winreg.QueryValueEx(key, "CurrentUser")[0]
            key = _winreg.OpenKey(reg, r"Software\Last.fm\Client\Users\%s" % user, _winreg.KEY_READ)
            enable = _winreg.QueryValueEx(key, "LogToProfile")[0]

            if enable == 1:
                if s.disablesubmissions:
                    return
                self._disable_submissions("Disabling submissions as the Last.fm software is enabled")
            else:
                if not s.disablesubmissions:
                    return
                self._enable_submissions("Enabling submissions as the Last.fm software is disabled")
        except:
            pass

    def OnTaskBarRight(self, event):
        self.tbi.PopupMenu(self.menu)

    #def OnTaskBarLeftDouble(self, event):
    #    self.IconQuote()

    def OnTaskBarLeftDouble(self, event):
        if self.quotes:
            self.quotes = False
            log.verb("Task bar quotes disabled")
        else:
            self.quotes = True
            log.verb("Task bar quotes enabled")

    def OnUpdateiPhoneManual(self, event):
        log.verb("OnUpdateiPhoneManual")
        if s.ipodmanual():
            main.updateonunmount = False
        else:
            if s.manualipoderror == "":
                log.info("No manualipoderror set")
                MessageBox(0,"An error occurred manually checking for iPod songs, see the log for more information"+".\n\nPlease try again.","iSproggler",1)
            else:
                log.warning(s.manualipoderror)
                MessageBox(0,s.manualipoderror+".\n\nPlease try again.","iSproggler",1)

    def OnUpdateiPhoneAuto(self, event):
        log.verb("OnUpdateiPhoneAuto")
        if main.prefs['ipodmultiple']:
          main.prefs['ipodmultiple'] = False
          f._pickle("iSproggler Prefs.pkl",main.prefs)
          log.verb("Multiple plays disabled as it is not compatible with iPhone and iPod touch");
        s.checkipodsongs()

    def OnUpdateiPod(self, event):
        if s.ipodmanual():
            main.updateonunmount = False
            try:
                self.menu.Enable(wxID_IPOD,False)
                log.verb("Disabling \"Update iPod\" menu item as iPod songs have been found")
                self.ipodmenuenabled = False
            except:
                log.warning("Exception raised when disabling the Update iPod menu")
        else:
            if s.manualipoderror == "":
                log.info("No manualipoderror set")
                MessageBox(0,"An error occurred manually checking for iPod songs, see the log for more information"+".\n\nPlease try again.","iSproggler",1)
            else:
                log.warning(s.manualipoderror)
                MessageBox(0,s.manualipoderror+".\n\nPlease try again.","iSproggler",1)
                s.manualipoderror = ""

    def OnDisableSubmissions(self, event):
        if s.disablesubmissions:
            #print "Enable Submissions"
            self.menu.SetLabel(wxID_DISABLE, "Disable Submissions")
            self.SetRedIcon(self.SetIconQuote())
            self.menu.Enable(wxID_PAUSE,True)
            s.submissionstate("disable",False)
            self.submissions_manually_disabled = False
        else:
            #print "Disable Submissions"
            self.menu.SetLabel(wxID_DISABLE, "Enable Submissions")
            self.SetBlueIcon("Submissions Disabled")
            self.menu.Enable(wxID_PAUSE,False)
            s.submissionstate("disable",True)
            self.submissions_manually_disabled = True

    def OnPauseSubmissions(self, event):
        if s.pausesubmissions:
            #print "Resume Submissions"
            self.menu.SetLabel(wxID_PAUSE, "Pause Submissions")
            self.SetRedIcon(self.SetIconQuote())
            self.menu.Enable(wxID_DISABLE,True)
            s.submissionstate("pause",False)
        else:
            #print "Pause Submissions"
            self.menu.SetLabel(wxID_PAUSE, "Resume Submissions")
            self.SetBlueIcon("Submissions Paused")
            self.menu.Enable(wxID_DISABLE,False)
            s.submissionstate("pause",True)

    def OnLastfmHomepage(self, event):
        #print "Menu: Last.fm Homepage"
        try:
            open_new("http://www.last.fm/")
        except:
            MessageBox(0,"Failed to open address http://www.last.fm/ in browser.","iSproggler",1)

    def OnLastfmUserPage(self, event):
        #print "Menu: Last.fm User Page"
        try:
            open_new("http://www.last.fm/user/%s/" % main.prefs['username'])
        except:
            MessageBox(0,"Failed to open address http://www.last.fm/user/%s/ in browser." % main.prefs['username'],"iSproggler",1)

    def OnLastfmAppPage(self, event):
        #print "Menu: Last.fm App Page"
        try:
            open_new("http://www.last.fm/group/iSproggler+Users")
        except:
            MessageBox(0,"Failed to open address http://www.last.fm/group/iSproggler+Users in browser.","iSproggler",1)

    def OnPreferences(self, event):
        #global prefs
        #print "Menu: Preferences..."
        if not self.prefsdlgshown:
            prefsdlg = PrefsDialog(self)
            self.prefsdlgshown = True
            if prefsdlg.ShowModal() == wx.ID_OK:
                newprefs = {}
                newprefs['username'] = prefsdlg.username.GetValue()
                if prefsdlg.password.GetValue() != "*" * int(main.prefs['passlength']):
                    password = prefsdlg.password.GetValue()
                    newprefs['passlength'] = len(password)
                    if type(password) == type(u""):
                        password = password.encode("utf-8")
                    newprefs['password'] = hashlib.md5(password).hexdigest()
                if prefsdlg.ipodsupport.GetValue():
                    newprefs['ipodsupport'] = prefsdlg.ipodsupport.GetValue()
                    newprefs['ipodmultiple'] = prefsdlg.ipodmultiple.GetValue()
                    newprefs['xmlfile'] = prefsdlg.xmlfile
                    newprefs['ipodmanual'] = prefsdlg.ipodmanual.GetValue()
                    #if not path.isfile(newprefs['xmlfile']):
                    if newprefs['xmlfile'] == "":
                        newprefs['ipodsupport'] = False
                else:
                    newprefs['ipodsupport'] = prefsdlg.ipodsupport.GetValue()

                for pref in main.prefs:
                    try:
                        newprefs[pref]
                    except:
                        newprefs[pref] = main.prefs[pref]
                if newprefs != main.prefs:
                    main.prefs = newprefs
                    f._pickle("iSproggler Prefs.pkl",main.prefs)
                    log.verb("Destroying prefs dialog, saving preferences")
                else:
                    log.verb("Destroying prefs dialog, preferences unchanged")
            else:
                log.verb("Destroying prefs dialog, ID_CANCEL received")

            if prefsdlg.loginrun.GetValue():
                if not globals()['LOGIN_RUN']:
                    log.verb("Writing registry to run at login")
                    try:
                        reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
                        key = _winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, _winreg.KEY_SET_VALUE)
                        _winreg.SetValueEx(key, "iSproggler", 0, _winreg.REG_SZ, r'"%s"' % argv[0])
                        log.verb("Registry writing successful")
                    except:
                        pass
            else:
                if globals()['LOGIN_RUN']:
                    log.verb("Writing registry to not run at login")
                    try:
                        reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
                        key = _winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, _winreg.KEY_SET_VALUE)
                        _winreg.DeleteValue(key, "iSproggler")
                        log.verb("Registry writing successful")
                    except:
                        pass

            try:
                self.prefsdlgshown = False
                prefsdlg.Destroy()
            except:
                pass

    def OnStatistics(self, event):
        #print "Menu: Statistics"
        if not self.statsdlgshown:
            statsdlg = StatsDialog(self)
            self.statsdlgshown = True
            statsdlg.ShowModal()
            try:
                self.statsdlgshown = False
                statsdlg.Destroy()
            except:
                pass

    def OnTimer(self, event):
        itunes.pumpevents()
        if main.prefs['ipodsupport']:
            main.ipodcheck()
            if main.ipodmounted and not self.ipodmenuenabled:
                try:
                    self.menu.Enable(wxID_IPOD,True)
                    log.verb("Enabling \"Update iPod\" menu item as an iPod volume has mounted")
                    self.ipodmenuenabled = True
                except:
                    log.warning("Exception raised when enabling the Update iPod menu")
            if not main.ipodmounted and self.ipodmenuenabled:
                try:
                    self.menu.Enable(wxID_IPOD,False)
                    log.verb("Disabling \"Update iPod\" menu item as iPod volume has unmounted")
                    self.ipodmenuenabled = False
                except:
                    log.warning("Exception raised when disabling the Update iPod menu")
        if self.coretimer % 2 == 0:
            if self.changesuccessicon:
                self.SetRedIcon(self.SetIconQuote())
                self.changesuccessicon = False
        if self.coretimer == 10:
            self.LastFMCheck()
            if not _threaded_:
                if main.ready():
                    main.core()
            self.coretimer = 0
            #if last response is a failed one
            if not s.lastserverresponse[0]:
                self.SetBlueIcon(s.lastserverresponse[1])
            else:
                #if submissions are not paused or disabled
                if not s.disablesubmissions and not s.pausesubmissions:
                    #if last server response is OK
                    if s.lastserverresponse[0]:
                        #only set green if new server response
                        if self.lastsubtime != s.lastserverresponse[2] and s.lastserverresponse[2] != 0:
                            #set green icon on successful submission
                            self.SetGreenIcon(s.lastserverresponse[1])
                            self.changesuccessicon = True
                            self.lastsubtime = s.lastserverresponse[2]
                        else:
                            self.SetRedIcon(self.SetIconQuote())
                            self.IconQuote()
        self.coretimer += 1

    def OnExit(self, event):
        #print "Menu: Exit"
        try:
            self.tbi.Destroy()
        except:
            pass
        if itunes.connected:
            itunes.cleanup()
        log.verb("Exiting...")
        exit()

    def SetIconQuote(self):
        if self.quotes and s.lastsubmitted != {}:
            try:
              return ("\"%s\" by %s" % (s.lastsubmitted['name'],s.lastsubmitted['artist'])).encode('utf-8')
            except:
              return choice(quotes.quotes)
        else:
            return choice(quotes.quotes)

    def IconQuote(self):
        if self.iconstatus != 1:
            if inlineimages:
                icon = images("normal.ico")
            else:
                icon = wxIcon(path.join(self.pathtoself,"data\\normal.ico"), wx.BITMAP_TYPE_ICO)
            #icon = wxEmptyIcon()
            #icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(imagesdict['normal.ico']))))
            if wx.Platform == "__WXMSW__":
              try:
                self.tbi.SetIcon(icon, self.SetIconQuote())
              except:
                self.tbi.SetIcon(icon, choice(quotes.quotes))

    def SetRedIcon(self,slogan):
        if self.iconstatus != 0:
            if inlineimages:
                icon = images("normal.ico")
            else:
                icon = wxIcon(path.join(self.pathtoself,"data\\normal.ico"), wx.BITMAP_TYPE_ICO)
            #icon = wxEmptyIcon()
            #icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(imagesdict['normal.ico']))))
            if wx.Platform == "__WXMSW__":
              try:
                self.tbi.SetIcon(icon, slogan)
              except:
                self.tbi.SetIcon(icon, choice(quotes.quotes))
            self.iconstatus = 0

    def SetGreenIcon(self,message):
        if self.iconstatus != 2:
            if inlineimages:
                icon = images("green.ico")
            else:
                icon = wxIcon(path.join(self.pathtoself,"data\\green.ico"), wx.BITMAP_TYPE_ICO)
            #icon = wxEmptyIcon()
            #icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(imagesdict['normal.ico']))))
            if wx.Platform == "__WXMSW__":
              try:
                self.tbi.SetIcon(icon, message)
              except:
                self.tbi.SetIcon(icon, choice(quotes.quotes))
            self.iconstatus = 2

    def SetBlueIcon(self,error):
        if self.iconstatus != 1:
            if inlineimages:
                icon = images("error.ico")
            else:
                icon = wxIcon(path.join(self.pathtoself,"data\\error.ico"), wx.BITMAP_TYPE_ICO)
            #icon = wxEmptyIcon()
            #icon.CopyFromBitmap(wx.BitmapFromImage(wx.ImageFromStream(cStringIO.StringIO(imagesdict['error.ico']))))
            if wx.Platform == "__WXMSW__":
              try:
                self.tbi.SetIcon(icon, error)
              except:
                self.tbi.SetIcon(icon, choice(quotes.quotes))
            self.iconstatus = 1


class MyApp(wx.App):
    def OnInit(self):
        frame = TaskBarApp(None, -1, "iSproggler")
        frame.Center(wx.BOTH)
        frame.Show(False)
        return True


if __name__ == '__main__':
    main = DummyClass()
    itunes = DummyClass()
    s = DummyClass()
    f = DummyClass()
    s.lastserverresponse.append(False)
    s.lastserverresponse.append("Debug")
    app = MyApp(0)
    app.MainLoop()