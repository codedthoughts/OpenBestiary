import tkinter
from tkinter import ttk, messagebox
import json
from functools import partial
import json
import dataclasses
import os

scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
bgui = None
bdict = {}
currently_selected = ""

class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)
		
def getConfig(parent="", key="", *, filename="config"):
	with open(filename+".json") as f:
		data = json.load(f)
		
		if parent == "" and key == "":
			return data
		else:
			try:
				if key == "":
					return data[parent]
				else:
					return data[parent][key]
			except:
				return "NO_CONFIG_KEY"

def setConfig(parent:str, key:str, value, *, filename="config", logging=False):
	if logging:
		AddLog(f"{parent} : {key} : {value}")
	data = getConfig()
	try:
		data[parent][key] = value
	except:
		data[parent] = {}
		data[parent][key] = value
	with open(filename+'.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def dumpConfig(data, filename="config"):
	with open(filename+'.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def touchConfig(parent:str, key:str, default, *, filename="config"):
	with open(filename+".json") as f:
		data = json.load(f)
		try:
			return data[parent][key]
		except:
			setConfig(parent, key, default)
			return default

def load_game(game):
	print(game.get())
	try:
		data = getConfig(filename=game.get())
		print(data)
		for item in data:
			if item.startswith("_"): #Meta data keys
				messagebox.showinfo(message=f"Author: {data[item]['author']}\nGame: {data[item]['game']}")
			else:
				bgui.modules.insert(0, item)
		bgui.cur_game = game.get()
		
	except FileNotFoundError:
		print("FILE NOT FOUND")
		
def load_game_from_list(game_list, sw):
	try:
		index = int(game_list.curselection()[0])
	except IndexError:
		return
	
	game = game_list.get(index)
	print(game)
	try:
		data = getConfig(filename=game)
		print(data)
		bgui.abut.config(state="normal")
		bgui.rbut.config(state="normal")
		bgui.ebut.config(state="normal")
		bgui.dbut.config(state="normal")
		if len(data) > 1:
			bgui.fbut.config(state="normal")
		else:
			bgui.fbut.config(state="disable")
		messagebox.showinfo(message=f"Author: {data['_META']['author']}\nGame: {data['_META']['game']}")	
		
		for item in data:
			if not item.startswith("_"): #Meta data keys
				bgui.modules.insert(0, item)
		bgui.cur_game = game
		sw.destroy()
		
	except FileNotFoundError:
		print("FILE NOT FOUND")

def add_mob(mob=False):
	print(mob)
	mobdata = {}
	if mob:
		data = getConfig(filename=bgui.cur_game)
		mobdata = data[bgui.currently_selected]
		
	w = tkinter.Tk()
	w.title("Mob Create")
	entries_names = []
	entries_value = []
	name_label = tkinter.Label(w, text="Name", width=8)
	name_label.grid(column=0, row=0)
	name_entry = tkinter.Entry(w)
	name_entry.grid(column=1, row=0)
	if mob:
		name_entry.insert(0, bgui.currently_selected)
	
	for key in mobdata:
		le = tkinter.Entry(w)
		le.grid(column=0, row=len(entries_names)+1)
		le.insert(0, key)
		lv = tkinter.Entry(w)
		lv.grid(column=1, row=len(entries_value)+1)
		lv.insert(0, mobdata[key])
		entries_names.append(le)
		entries_value.append(lv)
		
	pl = partial(add_editor_line, entries_names, entries_value, w)
	plus_lines = tkinter.Button(w, text="+", command=pl)
	plus_lines.grid(column=2, row=0)
	ml = partial(minus_editor_line, entries_names, entries_value)
	minus_lines = tkinter.Button(w, text="-", command=ml)
	minus_lines.grid(column=3, row=0)
	sv = partial(save_editor_mob, name_entry, entries_names, entries_value)
	save_edit = tkinter.Button(w, text="SAVE", command=sv)
	save_edit.grid(column=4, row=0)
	
	
def delete_mob():
	if not tkinter.messagebox.askokcancel(message=f"Delete {bgui.currently_selected} from {bgui.cur_game}?"):
		return
	mobdata = {}
	data = getConfig(filename=bgui.cur_game)
	del data[bgui.currently_selected]
	dumpConfig(data, filename=bgui.cur_game)
	reload_mobs()
	
def save_editor_mob(name, en, ev):
	data = {}
	name = name.get()
	for item in range(0, len(en)):
		data[en[item].get()] = ev[item].get()
	print(data)
	#if len(data) == 0:
	#	messagebox.showerror(message="No entries added.")
		
	b = getConfig(filename=bgui.cur_game)
	b[name] = data
	dumpConfig(b, filename=bgui.cur_game)
	reload_mobs()
	
def add_editor_line(en, ev, window):
	le = tkinter.Entry(window, width=8)
	le.grid(column=0, row=len(en)+1)
	lv = tkinter.Entry(window)
	lv.grid(column=1, row=len(ev)+1)
	en.append(le)
	ev.append(lv)
	
def minus_editor_line(en, ev):
	en[len(en)-1].destroy()
	en.pop()
	ev[len(ev)-1].destroy()
	ev.pop()
	
def load_mob():
	data = getConfig(filename=bgui.cur_game)
	print(data[bgui.currently_selected])
	w = tkinter.Tk()
	
	mobs = tkinter.Listbox(w, height=15)
	mobs.grid(rowspan=6, columnspan=4)
	mobsc = tkinter.Scrollbar(w)
	mobsc.grid(column=4, row=0, rowspan=6, sticky="ns")
	mobsc.config(command=mobs.yview)
	mobs.config(yscrollcommand=mobsc.set)	

	mob = data[bgui.currently_selected]
	w.title(bgui.currently_selected)
	for item in mob:	
		mobs.insert(1, f"{item}: {mob[item]}")
	mobs.insert(0, bgui.currently_selected)	

def reload_mobs():
	game = bgui.cur_game
	print(game)
	try:
		data = getConfig(filename=game)
		print(data)
		bgui.abut.config(state="normal")
		if len(data) > 1:
			bgui.fbut.config(state="normal")
		else:
			bgui.fbut.config(state="disable")
		bgui.modules.delete(0, 'end')	
		for item in data:
			if item != "_META":
				bgui.modules.insert(0, item)
		bgui.cur_game = game
		
	except FileNotFoundError:
		print("FILE NOT FOUND")
		
def onselect(evt):
	w = evt.widget
	try:
		index = int(w.curselection()[0])
	except IndexError:
		return
	# value = w.get(index)
	bgui.currently_selected = w.get(index)
	print(bgui.currently_selected)

def about():
	print("None")

def find_game():
	w = tkinter.Tk()
	ls = tkinter.Listbox(w)
	ls.pack()
	for file in os.listdir(scriptdir):
		filename = os.fsdecode(file)
		if filename.endswith('json'):
			ls.insert('end', filename.split(".")[0])
	srch = partial(load_game_from_list, ls, w)
	b = tkinter.Button(w, text="Load", command=srch)
	b.pack()	
	
class bestiary:
	def __init__(self):
		self.cur_game = ""
		self.currently_selected = ""
		self.mob_label = None
		
		self.mainwin = tkinter.Tk()
		self.mainwin.title("Bestiary")
		self.modules = tkinter.Listbox(self.mainwin, height=15)
		self.modules.grid(rowspan=6, columnspan=4)
		self.modules_scroll = tkinter.Scrollbar(self.mainwin)
		self.modules_scroll.grid(column=4, row=0, rowspan=6, sticky="ns")
		self.modules_scroll.config(command=self.modules.yview)
		self.modules.config(yscrollcommand=self.modules_scroll.set)	
		self.modules.bind('<<ListboxSelect>>', onselect)
		
		self.fbut = tkinter.Button(self.mainwin, text="Get Info", command=load_mob, state='disabled', width=7)
		self.fbut.grid(row=0, column=5, sticky="ns")
		self.abut = tkinter.Button(self.mainwin, text="Add Mob", command=add_mob, state='disabled', width=7)
		self.abut.grid(row=1, column=5, sticky="ns")
		self.rbut = tkinter.Button(self.mainwin, text="Reload", command=reload_mobs, state='disabled', width=7)
		self.rbut.grid(row=2, column=5, sticky="ns")
		edit_mob = partial(add_mob, True)
		self.ebut = tkinter.Button(self.mainwin, text="Edit Mob", command=edit_mob, state='disabled', width=7)
		self.ebut.grid(row=3, column=5, sticky="ns")
		self.dbut = tkinter.Button(self.mainwin, text="Delete Mob", command=delete_mob, state='disabled', width=7)
		self.dbut.grid(row=4, column=5, sticky="ns")
		
		self.menu = tkinter.Menu(self.mainwin)
		self.mainwin.config(menu=self.menu)
		self.filemenu = tkinter.Menu(self.mainwin)
		self.menu.add_cascade(label="Bestiary", menu=self.filemenu)
		self.filemenu.add_command(label="About", command=about)
		self.filemenu.add_command(label="Find Game", command=find_game)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", command=self.mainwin.destroy)
		#load_game("test")
		
def begin():
	global bgui
	bgui = bestiary()	
	bgui.mainwin.mainloop()
	
if __name__ == "__main__":	
	begin()
	print("Closing.")
