import tkinter
from tkinter import ttk, messagebox
import json
from functools import partial
import json
import dataclasses
import os
import contextlib

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
	with open(scriptdir+filename+".json") as f:
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
	data = getConfig(filename=filename)
	try:
		data[parent][key] = value
	except:
		data[parent] = {}
		data[parent][key] = value
	with open(scriptdir+filename+'.json', "w") as s:
		json.dump(data, s, indent=4)

def dumpConfig(data, filename="config"):
	with open(scriptdir+filename+'.json', "w") as s:
		json.dump(data, s, indent=4)

def touchConfig(parent:str, key:str, default, *, filename="config"):
	with open(scriptdir+filename+".json") as f:
		data = json.load(f)
		try:
			return data[parent][key]
		except:
			setConfig(parent, key, default, filename=filename)
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
	bgui.modules.delete(0, 'end')
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
			
		s = ""
		for item in data['_META']:
			if data['_META'][item] != "":
				s += f"{item.capitalize()}: {data['_META'][item]}\n"
		messagebox.showinfo(message=s)	
		
		for item in data:
			if not item.startswith("_"): #Meta data keys
				bgui.modules.insert('end', item)
		bgui.cur_game = game
		sw.destroy()
		
	except FileNotFoundError:
		print("FILE NOT FOUND")

def add_mob(mob=False):
	print(mob)
	data = {}
	mobdata = {}
	w = tkinter.Tk()
	if mob:
		data = getConfig(filename=bgui.cur_game)
		mobdata = data[bgui.currently_selected]
		w.title(f"Mob Edit")
	else:
		w.title(f"Mob Create")

	entries_names = []
	entries_value = []
	name_label = tkinter.Label(w, text="Name", width=12)
	name_label.grid(column=0, row=0)
	name_entry = tkinter.Entry(w)
	name_entry.grid(column=1, row=0)
	
	if mob:
		name_entry.insert(0, bgui.currently_selected)
	
	for key in mobdata:
		le = tkinter.Entry(w, width=12)
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
	le = tkinter.Entry(window, width=12)
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
	frame = tkinter.Frame(w)
	frame.grid()
	mobs = tkinter.Listbox(frame, height=20, width=40)
	mobs.grid(rowspan=6, columnspan=4, sticky="nsew")
	mobsc = tkinter.Scrollbar(frame)
	mobsc.grid(column=4, row=0, rowspan=6, sticky="ns")
	mobsc.config(command=mobs.yview)
	mobs.config(yscrollcommand=mobsc.set)	

	mob = data[bgui.currently_selected]
	w.title(bgui.currently_selected)
	for item in mob:	
		mobs.insert('end', f"{item}: {mob[item]}")
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
				bgui.modules.insert('end', item)
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

def edit_game(new_game=False):
	w = tkinter.Tk()
	w.title("Game Editor")
	print(bgui.cur_game)
	if not new_game:
		if bgui.cur_game == "":
			messagebox.showerror(message="No game open.")
			w.destroy()
			return
		w.title(f"Game Editor ({bgui.cur_game})")
		data = getConfig(filename=bgui.cur_game)
		
	name_label = tkinter.Label(w, text="Name:")
	name_label.grid(row=0, column=0)
	name_entry = tkinter.Entry(w)
	name_entry.grid(row=0, column=1)
	author_label = tkinter.Label(w, text="Author: ")
	author_label.grid(row=1, column=0)
	author_entry = tkinter.Entry(w)
	author_entry.grid(row=1, column=1)
	contact_label = tkinter.Label(w, text="Contact: ")
	contact_label.grid(row=2, column=0)
	contact_entry = tkinter.Entry(w)
	contact_entry.grid(row=2, column=1)
	platforms_label = tkinter.Label(w, text="Platforms: ")
	platforms_label.grid(row=3, column=0)
	platforms_entry = tkinter.Entry(w)
	platforms_entry.grid(row=3, column=1)
	dev_label = tkinter.Label(w, text="Developer: ")
	dev_label.grid(row=4, column=0)
	dev_entry = tkinter.Entry(w)
	dev_entry.grid(row=4, column=1)
	notes_label = tkinter.Label(w, text="Notes: ")
	notes_label.grid(row=5, column=0)
	notes_entry = tkinter.Entry(w)
	notes_entry.grid(row=5, column=1)
	
	filename_entry = tkinter.Entry(w)
	filename_entry.grid(row=0, column=3)
	if not new_game:
		with contextlib.suppress(KeyError):
			filename_entry.insert(0, bgui.cur_game)
			name_entry.insert(0, data['_META']['game'])
			author_entry.insert(0, data['_META']['author'])
			contact_entry.insert(0, data['_META']['contact'])
			platforms_entry.insert(0, data['_META']['platform'])
			dev_entry.insert(0, data['_META']['developers'])
			notes_entry.insert(0, data['_META']['notes'])
		
	save_game = partial(save_game_meta, filename_entry, name_entry, author_entry, contact_entry, platforms_entry, notes_entry, dev_entry, new_game)
	save_button = tkinter.Button(w, text="SAVE ->", command=save_game).grid(row=0, column=2)

def save_game_meta(filename, name, author, contact, platform, notes, devs, new_game):
	if filename.get() == "":
		messagebox.showerror(message="Filename is empty.")
	data = {}
	data['game'] = name.get()
	data['author'] = author.get()
	data['contact'] = contact.get()
	data['platform'] = platform.get()
	data['devs'] = devs.get()
	data['notes'] = notes.get()
	
	if not new_game:
		g = getConfig(filename=bgui.cur_game)
		g['_META'] = data
		dumpConfig(g, filename=bgui.cur_game)
	else:
		open(scriptdir+filename.get()+".json", 'w+').close()
		with open(scriptdir+filename.get()+".json", 'w+') as f:
			f.write("{}")
		g = getConfig(filename=filename.get())
		g['_META'] = data
		dumpConfig(g, filename=filename.get())	
		
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
		self.filemenu.add_command(label="Load Game", command=find_game)
		self.filemenu.add_command(label="Edit Game", command=edit_game)
		edit_game_load = partial(edit_game, True)
		self.filemenu.add_command(label="New Game", command=edit_game_load)
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
