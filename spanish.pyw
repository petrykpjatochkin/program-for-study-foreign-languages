#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
from gi.repository import Gtk, Gdk, GObject     # for gui
import os                                       # for files
import urllib2                                  # for google tranlate
from time import time                           # for logs
from random import randrange                    # for random
from random import shuffle                      # for sort by random
from pygame import mixer                        # for sond

data = []
main_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
settings = {"ico_file_name":        main_dir + "spain.png",
            "dict_dir":             main_dir + "dicts",
            "sonds_dir":            main_dir + "sonds",
            "mp3dict_dir":          main_dir + "mp3dicts",
            "dict_file_name":       main_dir + "/dicts/English.dict",
            "silence_file_name":    "silence-1sec.mp3",
            "silence_duration":     0,                      # in seconds
            "extension":            "dict",
            "langs":                ["es", "en"],
            "win_pos":              [0, 0],
            "revers_lang":          False,
            "play_status":          False
}

langs = {"es":  "spanish",
        "en":   "english",
        "ru":   "russian"
}


class MainWin:
    def destroy(self, widget, data=None):
        self.log("destroy signal occurred")
        os.remove("lock")
        Gtk.main_quit()

    def reverse_lange(self, widget):
        global settings
        settings["revers_lang"] = not settings["revers_lang"]
        self.b_lang1.handler_block(self.handle_lang1_id)
        self.b_lang2.handler_block(self.handle_lang2_id)
        if widget == self.b_lang1:
            self.b_lang2.set_active(not self.b_lang2.get_active())
        elif widget == self.b_lang2:
            self.b_lang1.set_active(not self.b_lang1.get_active())
        else:
            self.b_lang1.set_active(not self.b_lang1.get_active())
            self.b_lang2.set_active(not self.b_lang2.get_active())
        self.b_lang1.handler_unblock(self.handle_lang1_id)
        self.b_lang2.handler_unblock(self.handle_lang2_id)
        self.log("reverse lange")

    def sort(self, widget, need_show):
        global data
        if widget.get_active() == 0:
            data.sort(key=lambda d: d[2])
        elif widget.get_active() == 1:
            data.sort(key=lambda d: d[0].lower())
        elif widget.get_active() == 2:
            data.sort(key=lambda d: d[0].lower(), reverse=True)
        elif widget.get_active() == 3:
            data.sort(key=lambda d: d[1].lower())
        elif widget.get_active() == 4:
            data.sort(key=lambda d: d[1].lower(), reverse=True)
        elif widget.get_active() == 5:
            data.sort(key=lambda d: d[2].count("1"))
        elif widget.get_active() == 6:
            data.sort(key=lambda d: d[2].count("1"), reverse=True)
        elif widget.get_active() == 7:
            shuffle(data)
        if need_show:
            self.show(False, False)
        self.log("sorted by " + widget.get_active_text())

    def icon_click(self, widget, e):
        if e.button == 1:
            if self.win1.get_visible():
                settings["win_pos"] = self.win1.get_position()
                self.win1.hide()
                self.log("hide window")
            else:
                self.win1.show()
                self.win1.move(settings["win_pos"][0], settings["win_pos"][1])
                self.log("show window")
        elif e.button == 2:
            self.b_play.set_active(not settings["play_status"])
        elif e.button == 3:
            self.menu.popup(None, None, None, None, e.button, e.time)

    def icon_scroll(self, widget, e):
        if str(e.direction) == '<enum GDK_SCROLL_UP of type GdkScrollDirection>':
            mixer.music.set_volume(mixer.music.get_volume() + .05)
        elif str(e.direction) == '<enum GDK_SCROLL_DOWN of type GdkScrollDirection>':
            mixer.music.set_volume(mixer.music.get_volume() - .05)
        self.log("volume: " + str(mixer.music.get_volume()))

    def read_dict(self):
        global data, settings
        data = []

        data_file = open(settings["dict_file_name"], 'r')
        text = data_file.read().split('\n')[0:-1]
        for i in range(1, len(text)):
            data.extend([text[i].split('||') + [True]])
        data_file.close()
        settings["langs"] = [text[0].split('||')[0], text[0].split('||')[1]]

        try:
            for dirname in [settings["dict_dir"], settings["sonds_dir"], settings["mp3dict_dir"],
                            settings["sonds_dir"] + '/' + settings["langs"][0], settings["sonds_dir"] + '/'+settings["langs"][1],
                            settings["sonds_dir"] + '/' + settings["langs"][0] + '/temp', settings["sonds_dir"] + '/' + settings["langs"][1]+'/temp']:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                    self.log("Create folder: " + dirname)
        except Exception, e:
            self.log(str(e))
        if not os.path.exists(settings["dict_file_name"]):
            with open(settings["dict_file_name"], 'a') as data_file:
                data_file.write(settings["langs"][0] + '||' + settings["langs"][1] + '||' + str(time()) + '\n')

        self.b_lang1.set_label(settings["langs"][0])
        self.b_lang2.set_label(settings["langs"][1])
        self.entry1.set_placeholder_text(langs[settings["langs"][0]])
        self.entry2.set_placeholder_text(langs[settings["langs"][1]])

    def open_dict(self, widget, new):
        global settings
        if settings["play_status"]:
            self.b_play.set_active(False)
        self.entry1.set_text("")
        self.entry2.set_text("")
        if new:
            act = Gtk.FileChooserAction.SAVE
            label = "New dict"
            button = Gtk.STOCK_SAVE
        else:
            act = Gtk.FileChooserAction.OPEN
            label = "Open dict"
            button = Gtk.STOCK_OPEN
        dialog=Gtk.FileChooserDialog(title=label, action=act,
                                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    button, Gtk.ResponseType.OK))
        dialog.set_current_folder(settings["dict_dir"])

        filter_dict = Gtk.FileFilter()
        filter_dict.set_name(label)
        filter_dict.add_mime_type(settings["extension"] + "/dat")
        filter_dict.add_pattern("*." + settings["extension"])
        dialog.add_filter(filter_dict)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            settings["dict_file_name"] = dialog.get_filenames()[0]
            if not settings["dict_file_name"].endswith("." + settings["extension"]):
                settings["dict_file_name"] += "." + settings["extension"]
            self.log("Open " + settings["dict_file_name"])
        elif response == Gtk.ResponseType.CANCEL:
            self.log("Closed, no files selected")

        dialog.destroy()
        self.show(True, False)

    def show(self, newshow, filt):
        global data
        self.b = []
        j = 0
        for b in self.table:
            self.table.remove(b)
        self.table.resize(1, 2)
        if newshow:
            self.read_dict()
            self.sort(self.c_sort, False)
        elif not filt:
            for i in range(len(data)):
                data[i][-1] = True
        else:
            s = filt.get_text().lower()
            for i in range(len(data)):
                if data[i][0].lower().find((' ' + s)) != -1 or data[i][1].lower().find(' '+s) != -1 or data[i][0].lower().find(s) == 0 or data[i][1].lower().find(s) == 0:
                    data[i][-1] = True
                else:
                    data[i][-1] = False

        for i in range(len(data)):
            if data[i][-1]:
                self.b.append([Gtk.Button(data[i][0]), Gtk.Button(data[i][1])])

                self.b[j][0].connect("clicked", self.say, data[i][0], settings["langs"][0], True, False, True)
                self.b[j][1].connect("clicked", self.say, data[i][1], settings["langs"][1], True, False, True)

                self.table.attach(self.b[j][0], 0, 1, j, j + 1)
                self.table.attach(self.b[j][1], 1, 2, j, j + 1)
                j += 1

        self.win1.set_title(settings["dict_file_name"].split('/')[-1].split('.')[0] + ' (' + str(len(data)) + ' words)')
        self.win1.show_all()

    def entry_key(self, widget, e):
        if e.keyval == 65293 or e.keyval == 65421:
            self.say(widget, widget.get_text(), settings["langs"][int(Gtk.Buildable.get_name(widget)[-1]) - 1], False, True, True)
            for i in range(len(data)):
                data[i][-1] = True
            self.show(False, False)
        elif e.keyval == 65307:
            widget.set_text('')

    def entry_change(self, widget):
        self.show(False, widget)

    def say(self, widget, *data):
        words, lan, clipboard, temp, show = data
        if show:
            self.log(words)
            os.system('notify-send "' + words + '"')
        file_name = self.google_voice(words, lan, temp)

        mixer.music.load(file_name)
        if clipboard:
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(words, -1)
        mixer.music.play()
        return True

    def google_voice(self, words, lan, temp):
        if temp:
            file_name = settings["sonds_dir"] + '/' + lan + '/temp/' + words + '.mp3'
        else:
            file_name = settings["sonds_dir"] + '/' + lan + '/' + words + '.mp3'
        if not os.path.exists(file_name):
            url = "http://translate.google.com/translate_tts?tl=" + lan + "&q=" + words.replace(" ", "+")
            request = urllib2.Request(url)
            headers = {"Host": "translate.google.com",
                        "Referer": "http://www.gstatic.com/translate/sound_player2.swf",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19"}
            request.add_header('User-agent', headers)
            opener = urllib2.build_opener()

            f = open(file_name, "wb")
            f.write(opener.open(request).read())
            f.close()
            self.log("Create file: " + words + '.mp3')
        return file_name

    def add_word(self, widget):
        global data
        data.append([self.entry1.get_text(), self.entry2.get_text(), True])

        with open(settings["dict_file_name"], 'a') as data_file:
            data_file.write(self.entry1.get_text() + '||' + self.entry2.get_text() + '||0000000000||' + str(time()) + '\n')

        self.log("add new words: " + self.entry1.get_text() + " = " + self.entry2.get_text())
        self.entry1.set_text('')
        self.entry2.set_text('')
        self.show(False, False)

    def make_mp3dict(self, widget):
        silence_file = open(settings["sonds_dir"] + "/" + settings["silence_file_name"], 'rb').read()
        if settings["revers_lang"]:
            mp3_file = open(settings["mp3dict_dir"] + "/" + settings["dict_file_name"].split('/')[-1].split('.')[0] + "-" + settings["langs"][1] + "-" + settings["langs"][0] + ".mp3", 'wb')
        else:
            mp3_file = open(settings["mp3dict_dir"] + "/" + settings["dict_file_name"].split('/')[-1].split('.')[0] + "-" + settings["langs"][0] + "-" + settings["langs"][1] + ".mp3", 'wb')
        for words in data:
            for i in range(2):
                if settings["revers_lang"]:
                    i = int(not i)
                mp3_file.write(silence_file * settings["silence_duration"])
                mp3_file.write(open(self.google_voice(words[i], settings["langs"][i], False), 'rb').read())
        self.log("Create file: " + mp3_file.name)
        mp3_file.close()

    def play(self, widget):
        global settings, timer_id, num_song
        if settings["play_status"]:
            GObject.source_remove(timer_id)
            self.b_play.set_image(self.i_play)
            for b in self.table:
                b.get_style_context().remove_class("act")
            self.log("stop play")
        else:
            num_song = -1
            timer_id = GObject.timeout_add(4 * 1000, self.learn)
            self.b_play.set_image(self.i_stop)
            self.log("start play")
        settings["play_status"] = not settings["play_status"]

    def learn(self):
        global num_song
        if settings["revers_lang"]:
            lan1, lan2 = 1, 0
        else:
            lan1, lan2 = 0, 1
        for b in self.table:
            b.get_style_context().remove_class("act")
        if num_song == -1:
            num_song = randrange(len(data))
            self.say(None, data[num_song][lan1], settings["langs"][lan1], False, False, True)
            self.b[num_song][lan1].get_style_context().add_class("act")
        else:
            self.say(None, data[num_song][lan2], settings["langs"][lan2], False, False, True)
            self.b[num_song][lan2].get_style_context().add_class("act")
            num_song = -1
        return True

    def test(self, widget, e):
        global ans
        if not e:
            if self.win2.get_visible():
                self.win2.hide()
            else:
                self.win2.show_all()
                ans = None
        else:
            self.b_test.set_active(not self.b_test.get_active)
        return True

    def types(self, widget):
        try:
            try:
                entry = self.win1.get_focus_child().get_focus_child()
                pos = entry.get_position()
            except Exception:
                entry = self.win2.get_focus_child().get_focus_child().get_focus_child()
                pos = entry.get_position()
            entry.set_text(entry.get_text() + widget.get_label())
            entry.set_position(pos + 1)
        except Exception,e:
            self.log(str(e))

#test2------------------------------------------------------------------#
    def data_to_file(self):
        os.remove(settings["dict_file_name"])
        with open(settings["dict_file_name"], 'a') as data_file:
            data_file.write(settings["langs"][0] + '||' + settings["langs"][1] + '||' + str(time()) + '\n')
            for d in data:
                data_file.write('||'.join(d[:-1]) + '\n')

    def test12_start(self, widget):
        global ans
        self.e11.set_text("")
        self.l12.set_text("")
        self.l13.set_text("")
        try:
            self.e11.get_style_context().remove_class("ok")
        except Exception:
            pass
        try:
            self.e11.get_style_context().remove_class("error")
        except Exception:
            pass
        self.b11.set_label(self.b11.get_label().split("/")[0] + "/" + str(int(self.b11.get_label().split("/")[1])+1))
        ans = randrange(len(data)) + 1
        self.say(None, data[ans - 1][int(settings["revers_lang"])], settings["langs"][settings["revers_lang"]], False, False, False)
        self.l14.set_text(str(data[ans - 1][2].count("1")) + "0%")

    def test12(self, widget, e):
        global ans, data
        if Gtk.Buildable.get_name(widget) == "e11" and (e.keyval == 65293 or e.keyval == 65421) and not ans:
            self.test12_start(None)
            return False
        elif Gtk.Buildable.get_name(widget) == "e11" and (e.keyval==65293 or e.keyval == 65421) and ans and len(self.e11.get_text()) == 0:
            self.say(None, data[ans - 1][int(settings["revers_lang"])], settings["langs"][settings["revers_lang"]], False, False, False)
            return False
        elif len(self.e11.get_text()) == 0 or not ans or (Gtk.Buildable.get_name(widget) == "e11" and not (e.keyval==65293 or e.keyval==65421)):
            return False
        elif self.e11.get_text().lower() == data[ans - 1][settings["revers_lang"]].lower() :
            self.b11.set_label(str(int(self.b11.get_label().split("/")[0]) + 1) + "/" + self.b11.get_label().split("/")[1])
            data[ans - 1][2] = data[ans - 1][2][1:] + "1"
            self.e11.get_style_context().add_class("ok")
            self.log("OK")
        else:
            data[ans - 1][2] = data[ans - 1][2][1:] + "0"
            self.e11.get_style_context().add_class("error")
            self.log("Eror")
        self.l12.set_text(data[ans - 1][int(settings["revers_lang"])])
        self.l13.set_text(data[ans - 1][int(not settings["revers_lang"])])
        self.l14.set_text(str(data[ans - 1][2].count("1")) + "0%")
        self.say(None, data[ans - 1][int(not settings["revers_lang"])], settings["langs"][not settings["revers_lang"]], False, False, False)
        ans = None
        self.data_to_file()
        return True

    def test12_restart(self, widget):
        self.b11.set_label("0/0")
        self.e11.set_text("")
        self.l12.set_text("")
        self.l13.set_text("")
        self.l14.set_text("")
        try:
            self.e11.get_style_context().remove_class("ok")
        except Exception:
            pass
        try:
            self.e11.get_style_context().remove_class("error")
        except Exception:
            pass
        ans = None
#test2------------------------------------------------------------------#

    def test22_start(self, widget):
        global ans
        self.e21.set_text("")
        self.l22.set_text("")
        self.l23.set_text("")
        try:
            self.e21.get_style_context().remove_class("ok")
        except Exception:
            pass
        try:
            self.e21.get_style_context().remove_class("error")
        except Exception:
            pass
        self.b21.set_label(self.b21.get_label().split("/")[0] + "/" + str(int(self.b21.get_label().split("/")[1])+1))
        ans = randrange(len(data)) + 1
        self.say(None, data[ans - 1][settings["revers_lang"]], settings["langs"][settings["revers_lang"]], False, False, False)
        self.l24.set_text(str(data[ans - 1][2].count("1")) + "0%")

    def test22(self, widget, e):
        global ans, data
        if Gtk.Buildable.get_name(widget) == "e21" and (e.keyval == 65293 or e.keyval == 65421) and not ans:
            self.test22_start(None)
            return False
        elif Gtk.Buildable.get_name(widget) == "e21" and (e.keyval == 65293 or e.keyval == 65421) and ans and len(self.e21.get_text()) == 0:
            self.say(None, data[ans - 1][not settings["revers_lang"]], settings["langs"][not settings["revers_lang"]], False, False, False)
            return False
        elif len(self.e21.get_text()) == 0 or not ans or (Gtk.Buildable.get_name(widget) == "e21" and not (e.keyval == 65293 or e.keyval==65421)):
            return False
        elif self.e21.get_text().lower() == data[ans - 1][not settings["revers_lang"]].lower() :
            self.b21.set_label(str(int(self.b21.get_label().split("/")[0]) + 1) + "/"+self.b21.get_label().split("/")[1])
            data[ans - 1][2] = data[ans - 1][2][1:] + "1"
            self.e21.get_style_context().add_class("ok")
            self.log("OK")
        else:
            data[ans - 1][2] = data[ans - 1][2][1:] + "0"
            self.e21.get_style_context().add_class("error")
            self.log("Eror")
        self.l22.set_text(data[ans - 1][not settings["revers_lang"]])
        self.l23.set_text(data[ans - 1][settings["revers_lang"]])
        self.l24.set_text(str(data[ans - 1][2].count("1")) + "0%")
        self.say(None, data[ans - 1][not settings["revers_lang"]], settings["langs"][not settings["revers_lang"]], False, False, False)
        ans = None
        self.data_to_file()
        return True

    def test22_restart(self, widget):
        self.b21.set_label("0/0")
        self.e21.set_text("")
        self.l22.set_text("")
        self.l23.set_text("")
        self.l24.set_text("")
        try:
            self.e21.get_style_context().remove_class("ok")
        except Exception:
            pass
        try:
            self.e21.get_style_context().remove_class("error")
        except Exception:
            pass
        ans = None
#test3------------------------------------------------------------------#

    def test32_start(self, widget):
        global ans
        self.l32.set_text("")
        self.b31.set_label(self.b31.get_label().split("/")[0] + "/" + str(int(self.b31.get_label().split("/")[1])+1))
        ans = randrange(len(data)) + 1
        self.say(None, data[ans - 1][settings["revers_lang"]], settings["langs"][settings["revers_lang"]], False, False, False)
        self.l24.set_text(str(data[ans - 1][2].count("1")) + "0%")
#-----------------------------------------------------------------------#

    def log(self, mesege):
        print "{0:.3f}".format(time() - start_time), ":", mesege

    def __init__(self):
        global start_time
        start_time = time()
        self.log("Program starts")
        mixer.init(16000)

        try:
            os.open("lock", os.O_CREAT | os.O_EXCL)
        except Exception, e:
            if raw_input("{0:.3f}".format(time() - start_time) + " : it seems program is already works, do you still want run this program? ('no' for exit)?\n") == "no":
                exit(0)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("spanish.glade")

        self.win1 = self.builder.get_object("Spanish")
        self.win2 = self.builder.get_object("Test")
#-----------------------------------------------------------------------#
        self.b_add = self.builder.get_object("b_add")
        self.b_play = self.builder.get_object("b_play")
        self.b_set = self.builder.get_object("b_set")
        self.b_open = self.builder.get_object("b_open")
        self.b_new = self.builder.get_object("b_new")
        self.b_test = self.builder.get_object("b_test")
        self.b_lang1 = self.builder.get_object("b_lang1")
        self.b_lang2 = self.builder.get_object("b_lang2")
        self.entry1 = self.builder.get_object("entry1")
        self.entry2 = self.builder.get_object("entry2")
        self.c_sort = self.builder.get_object("c_sort")
        self.scrolled_window = self.builder.get_object("scrolledwindow1")
        self.i_play = self.builder.get_object("i_play")
        self.i_stop = self.builder.get_object("i_stop")
#-----------------------------------------------------------------------#
        self.e11 = self.builder.get_object("e11")
        self.b11 = self.builder.get_object("b11")
        self.b12 = self.builder.get_object("b12")
        self.b13 = self.builder.get_object("b13")
        self.l11 = self.builder.get_object("l11")
        self.l12 = self.builder.get_object("l12")
        self.l13 = self.builder.get_object("l13")
        self.l14 = self.builder.get_object("l14")
#-----------------------------------------------------------------------#
        self.e21 = self.builder.get_object("e21")
        self.b21 = self.builder.get_object("b21")
        self.b22 = self.builder.get_object("b22")
        self.b23 = self.builder.get_object("b23")
        self.l21 = self.builder.get_object("l21")
        self.l22 = self.builder.get_object("l22")
        self.l23 = self.builder.get_object("l23")
        self.l24 = self.builder.get_object("l24")
#-----------------------------------------------------------------------#
        self.l32 = self.builder.get_object("l32")
        self.b31 = self.builder.get_object("b31")
        self.b32 = self.builder.get_object("b32")
        self.b33 = self.builder.get_object("b33")
        self.b34 = self.builder.get_object("b34")
#-----------------------------------------------------------------------#
        self.l42 = self.builder.get_object("l42")
        self.e41 = self.builder.get_object("e41")
        self.b41 = self.builder.get_object("b41")
#-----------------------------------------------------------------------#

        self.b_lang1.set_name("b_lang1")
        self.b_lang2.set_name("b_lang2")
        self.c_sort.append_text("Time")
        self.c_sort.append_text("A-Z (lang1)")
        self.c_sort.append_text("Z-A (lang1)")
        self.c_sort.append_text("A-Z (lang2)")
        self.c_sort.append_text("Z-A (lang2)")
        self.c_sort.append_text("by know low-well")
        self.c_sort.append_text("by know well-low")
        self.c_sort.append_text("Randome")
        self.c_sort.set_active(0)

#-----------------------------------------------------------------------#
        self.win1.connect("destroy", self.destroy)
        self.win2.connect("delete_event", self.test)
        self.b_add.connect("clicked", self.add_word)
        self.b_play.connect("clicked", self.play)
        self.b_set.connect("clicked", lambda w: self.menu.popup(None, None, None, None, 0, 0))
        self.b_open.connect("clicked", self.open_dict, False)
        self.b_new.connect("clicked", self.open_dict, True)
        self.b_test.connect("clicked", self.test, False)
        self.c_sort.connect("changed", self.sort, True)
        self.handle_lang1_id = self.b_lang1.connect("clicked", self.reverse_lange)
        self.handle_lang2_id = self.b_lang2.connect("clicked", self.reverse_lange)
        self.entry1.connect("key-press-event", self.entry_key)
        self.entry1.connect("changed", self.entry_change)
        self.entry2.connect("key-press-event", self.entry_key)
        self.entry2.connect("changed", self.entry_change)
#-----------------------------------------------------------------------#
        self.e11.connect("key-press-event", self.test12)
        self.b11.connect("clicked", self.test12_restart)
        self.b12.connect("clicked", self.test12_start)
        self.b13.connect("clicked", self.test12, None)
#-----------------------------------------------------------------------#
        self.e21.connect("key-press-event", self.test22)
        self.b22.connect("clicked", self.test22_start)
        self.b23.connect("clicked", self.test22, None)
        self.b21.connect("clicked", self.test22_restart)
#-----------------------------------------------------------------------#

        self.table = Gtk.Table(1, 2, False)
        self.table.set_row_spacings(3)
        self.table.set_col_spacings(3)
        self.scrolled_window.add_with_viewport(self.table)

        self.read_dict()

        try:
            self.win1.set_icon_from_file(settings["ico_file_name"])
        except Exception, e:
            self.log("no ico file\n\t" + str(e))

        try:
            cssProvider = Gtk.CssProvider()
            cssProvider.load_from_path('style.css')
            screen = Gdk.Screen.get_default()
            styleContext = Gtk.StyleContext()
            styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        except Exception, e:
            self.log("no css file\n\t " + str(e))

        self.statusicon = Gtk.StatusIcon()
        self.statusicon.set_from_file(settings["ico_file_name"])
        self.statusicon.connect("button-press-event", self.icon_click)
        self.statusicon.connect("scroll-event", self.icon_scroll)

        self.menu = Gtk.Menu()
        self.li1 = Gtk.MenuItem("Play/Stop")
        self.li2 = Gtk.MenuItem("Open dict")
        self.li3 = Gtk.MenuItem("New dict")
        self.li4 = Gtk.MenuItem("Additional keys")
        self.li4s = [
                    Gtk.MenuItem("á"),
                    Gtk.MenuItem("é"),
                    Gtk.MenuItem("í"),
                    Gtk.MenuItem("ó"),
                    Gtk.MenuItem("ú"),
                    Gtk.MenuItem("ü"),
                    Gtk.MenuItem("ñ"),
                    Gtk.MenuItem("¿"),
                    Gtk.MenuItem("¡")
        ]
        self.li5 = Gtk.MenuItem("Options")
        self.li51 = Gtk.MenuItem("Make mp3dict")
        self.li52 = Gtk.MenuItem("Change lang")
        self.li6 = Gtk.MenuItem("Quit")
        self.li1.connect("activate", lambda w: self.b_play.set_active(not settings["play_status"]))
        self.li2.connect("activate", self.open_dict, False)
        self.li3.connect("activate", self.open_dict, True)
        for l in self.li4s:
            l.connect("activate", self.types)
        self.li51.connect("activate", self.make_mp3dict)
        self.li52.connect("activate", self.reverse_lange)
        self.li6.connect("activate", self.destroy)

        self.menu.append(self.li1)
        self.menu.append(self.li2)
        self.menu.append(self.li3)
        self.menu.append(self.li4)
        self.smenu_keys = Gtk.Menu()
        self.li4.set_submenu(self.smenu_keys)
        for l in self.li4s:
            self.smenu_keys.append(l)
        self.menu.append(self.li5)
        self.smenu_opt = Gtk.Menu()
        self.li5.set_submenu(self.smenu_opt)
        self.smenu_opt.append(self.li51)
        self.smenu_opt.append(self.li52)
        self.menu.append(self.li6)
        self.menu.show_all()

        self.show(True, True)
        self.win1.show_all()

    def main(self):
        Gtk.main()

if __name__ == "__main__":
    MainWin().main()
