import os
import threading
import codecs
from tkinter import *
import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import font
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
from datetime import datetime
import time
import json
import xmltodict
import jellyfish

from Const import *
from ESX import *
from Editors import *


class ModFrame(Frame):
	def __init__(self, parent, width):
		Frame.__init__(self, parent)
		self.root = parent

		self.settings = Settings()
		self.settings.enc0 = 'utf-8'
		self.settings.enc1 = 'cp1251'
		self.settings.mode = 'r'
		self.settings.dict = {'TES4': '00000000'}

		tree = Treeview(self)
		tree.bind('<Double-1>', lambda e: 'break')
		tree.place(relx=0, rely=0.02, width=0.2*width-scrollWidth, relheight=0.98)
		treeScroll = Scrollbar(self, orient=VERTICAL, command=tree.yview)
		treeScroll.place(x=0.2*width-scrollWidth, rely=0.02, width=scrollWidth, relheight=0.98)
		tree.configure(yscrollcommand=treeScroll.set)
		for i in range(len(states)):
			tree.tag_configure(states[i], background=colors[i])

		def tree_walk(item, state):
			tree.item(item, open=state)
			for child in tree.get_children(item):
				tree_walk(child, state)

		def open_all():
			tree_walk('', True)

		def close_all():
			tree_walk('', False)

		openButton = tk.Button(self, text="Expand All", font=labelFont, command=open_all)
		openButton.place(x=5, y=3, width=(0.2*width-scrollWidth)/2-7, relheight=0.03)

		closeButton = tk.Button(self, text="Collapse All", font=labelFont, command=close_all)
		closeButton.place(x=(0.2*width-scrollWidth)/2+2, y=3, width=(0.2*width-scrollWidth)/2-7, relheight=0.03)

		def sort_column(table, col, reverse):
			items = [(table.set(k, col), k) for k in table.get_children('')]				# Create a list of all table elements and sort it by the chosen column value
			items.sort(reverse=reverse)

			for index, (val, k) in enumerate(items):										# Shift each row into its new position
				table.move(k, '', index)

			table.heading(col, command=lambda: sort_column(table, col, not reverse))		# Replace the existing lambda with one having the inverse sort direction

		columns = ('fid', 'type', 'edid', 'old', 'new', 'status')
		table = Treeview(self, columns=columns, show='headings')
		table.heading('fid', text='FormID', command=lambda: sort_column(table, 'fid', False))
		table.column('fid', minwidth=100, width=100, stretch=NO, anchor=CENTER)
		table.heading('type', text='Type', command=lambda: sort_column(table, 'type', False))
		table.column('type', minwidth=75, width=75, stretch=NO, anchor=CENTER)
		table.heading('edid', text='EDID', anchor=W, command=lambda: sort_column(table, 'edid', False))
		table.column('edid', minwidth=75, width=200, stretch=YES, anchor=W)
		table.heading('old', text='Original', anchor=W, command=lambda: sort_column(table, 'old', False))
		table.column('old', minwidth=75, width=500, stretch=YES, anchor=W)
		table.heading('new', text='Translation', anchor=W, command=lambda: sort_column(table, 'new', False))
		table.column('new', minwidth=75, width=500, stretch=YES, anchor=W)
		table.heading('status', text='Status', command=lambda: sort_column(table, 'status', False))
		table.column('status', minwidth=130, width=130, stretch=NO, anchor=CENTER)
		table.bind('<Double-1>', lambda e: 'break')
		table.place(relx=0.2, rely=0, width=0.8*width-scrollWidth, relheight=1)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=table.yview)
		tabScroll.place(x=width-scrollWidth, rely=0, width=scrollWidth, relheight=1)
		table.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			table.tag_configure(states[i], background=colors[i])

		self.settings.tree = tree
		self.settings.table = table
		# self.mods = dict()

	def load_mod(self):

		# self.tree.insert('', 'end', settings.esp, text=settings.esp)
		settings = self.settings
		tree = settings.tree
		table = settings.table

		settings.prog.set_text("Parsing TES4 Header...")

		chunk = settings.file.read(24)
		if checkType(chunk) == "TES4":
			TES4(settings, chunk)
		else:
			print("Invalid Mod File!")
			settings.prog.complete()
			self.destroy()
			return

		chunk = settings.file.read(24)
		while chunk:
			Group(settings, chunk)
			chunk = settings.file.read(24)

		emptyTypes = []
		for record in settings.dict:
			if settings.dict[record] == {}:
				emptyTypes.append(record)
		for record in emptyTypes:
			del settings.dict[record]

		settings.prog.set_text("Cleaning Up...")

		def tree_edit(event):
			item = tree.identify('item', event.x, event.y)
			tags = tree.item(item, 'tags')
			settings.fid = tags[0]				# FormID
			settings.rec = tags[1]				# Record type
			settings.mode = tags[2]				# Translation status
			if settings.rec == 'TES4':
				editor = Tes4Editor(settings)
			elif settings.rec == 'FACT':
				editor = FactEditor(settings)
			elif settings.rec == 'BOOK':
				editor = BookEditor(settings)
			elif settings.rec == 'MESG':
				editor = MesgEditor(settings)
			elif settings.rec == 'DIAL':
				editor = DialEditor(settings)
			elif settings.rec == 'INFO':
				editor = InfoEditor(settings)
			elif settings.rec == 'QUST':
				editor = QustEditor(settings)
			elif settings.rec == 'SCEN':
				editor = ScenEditor(settings)
			elif settings.rec in descTypes:
				editor = DescEditor(settings)
			else:
				editor = NamedEditor(settings)
			self.wait_window(editor)
		for record in tree.get_children(''):
			if record == '00000000':
				tree.tag_bind('00000000', '<Double-1>', tree_edit)
				continue
			if len(tree.get_children(record)) == 0:
				tree.item(record, tags=('', record, 'No Tx Needed'))
				continue
			for item in tree.get_children(record):
				if item:
					tags = tree.item(item, 'tags')
					tree.tag_bind(tags[0], '<Double-1>', tree_edit)
				for subItem in tree.get_children(item):
					if subItem:
						tags = tree.item(subItem, 'tags')
						tree.tag_bind(tags[0], '<Double-1>', tree_edit)

		def table_edit(event):
			item = table.identify('item', event.x, event.y)
			tags = table.item(item, 'tags')
			settings.fid = tags[0]				# FormID
			settings.rec = tags[1]				# Record type
			settings.mode = tags[2]				# Translation status
			if settings.rec == 'TES4':
				editor = Tes4Editor(settings)
			elif settings.rec == 'FACT':
				editor = FactEditor(settings)
			elif settings.rec == 'BOOK':
				editor = BookEditor(settings)
			elif settings.rec == 'MESG':
				editor = MesgEditor(settings)
			elif settings.rec == 'DIAL':
				editor = DialEditor(settings)
			elif settings.rec == 'INFO':
				editor = InfoEditor(settings)
			elif settings.rec == 'QUST':
				editor = QustEditor(settings)
			elif settings.rec == 'SCEN':
				editor = ScenEditor(settings)
			elif settings.rec in descTypes:
				editor = DescEditor(settings)
			else:
				editor = NamedEditor(settings)
			self.wait_window(editor)
		for item in table.get_children(''):
			tags = table.item(item, 'tags')
			table.tag_bind(tags[0], '<Double-1>', table_edit)

		# self.mods[settings.esp] = settings.dict
		# self.mods = settings.dict
		settings.prog.complete()


class OpenModDialog(Toplevel):
	def __init__(self, parent):
		Toplevel.__init__(self, parent)

		self.root = parent
		self.option_add("*tearOff", FALSE)
		self.resizable(FALSE, FALSE)
		width, height = parent.winfo_screenwidth(), parent.winfo_screenheight()
		w = width / 2
		h = height / 2
		x = (width - w) / 2
		y = (height - h) / 2
		self.geometry("%dx%d+%d+%d" % (w, h, x, y))
		self.overrideredirect(True)

		inLabel = Label(self, text="Target Mod File")
		inLabel.place(relx=0, rely=0, relwidth=0.2, relheight=0.1, anchor=NW)

		inEntry = Label(self, text="No Mod File Selected")
		inEntry.place(relx=0.2, rely=0, relwidth=0.7, relheight=0.1, anchor=NW)

		def open_button():
			modFile = filedialog.askopenfilename(title="Open Mod File", filetypes=[("", ".esp .esm .esl")])
			if modFile:
				inEntry.text = modFile

		inButton = Button(self, text="...", command=open_button)
		inButton.place(relx=0.9, rely=0, relwidth=0.1, relheight=0.1, anchor=NW)

		#inList = Listbox()
		#inList.place()

		outLabel = Label(self, text="Default Output File")
		outLabel.place(relx=0, rely=0.3, relwidth=0.2, relheight=0.1, anchor=NW)

		outEntry = Label(self, text="No Output File Selected")
		outEntry.place(relx=0.2, rely=0.3, relwidth=0.7, relheight=0.1, anchor=NW)

		def save_button():
			saveFile = filedialog.asksaveasfilename(title="Save Mod File", filetypes=[("", ".esp .esm .esl")])
			if saveFile:
				outEntry.text = saveFile

		outButton = Button(self, text="...", command=save_button)
		outButton.place(relx=0.9, rely=0.3, relwidth=0.1, relheight=0.1, anchor=NW)

		#outList = Listbox()
		#outList.place()

		#impEntry = Entry()
		#impEntry.place()

		#impButton = Button()
		#impButton.place()

		#parent.open_file(modFile)


class ProgressFrame(Frame):
	def __init__(self, parent, maximum, text):
		Frame.__init__(self, parent)
		self.text = text
		self.label = Label(self, anchor=CENTER)
		self.label.place(relx=0, rely=0, relwidth=1, relheight=0.3)
		self.timer = Label(self, anchor=CENTER)
		self.timer.place(relx=0, rely=0.3, relwidth=1, relheight=0.4)
		self.startTime = datetime.now()
		mode = 'determinate' if maximum > 0 else 'indeterminate'
		self.progressBar = Progressbar(self, orient=HORIZONTAL, mode=mode)
		self.set_max(maximum)
		self.progressBar.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)
		self.set_text(self.text)

	def set_text(self, text):
		val = self.progressBar['value']
		mval = self.progressBar['maximum']
		self.text = text
		if mval > 0:
			self.label['text'] = f"{text}: ({val}/{mval})"
			curTime = datetime.now()
			diffTime = curTime - self.startTime
			self.timer['text'] = f"{str(diffTime.seconds // 60).zfill(2)}:{str(diffTime.seconds % 60).zfill(2)}"
		else:
			self.label['text'] = text

	def set_max(self, maximum):
		self.progressBar['maximum'] = maximum
		self.progressBar['value'] = 0
		self.set_text(self.text)

	def set(self, value):
		self.progressBar['value'] = value
		self.set_text(self.text)

	def increment(self, count=1):
		val = self.progressBar['value']
		self.progressBar['value'] = val + count
		self.set_text(self.text)

	def complete(self, text):
		self.set_max(1)
		self.progressBar['value'] = 1
		self.label['text'] = text


class ProgressDialog(Toplevel):
	def __init__(self, parent, width, height, maximum, text):
		Toplevel.__init__(self, parent)
		self.option_add('*tearOff', FALSE)
		self.resizable(FALSE, FALSE)
		w = width / 3
		h = height / 6
		x = (width-w)/2
		y = (height-h)/2
		self.geometry("%dx%d+%d+%d" % (w, h, x, y))
		self.overrideredirect(True)
		self.progress = ProgressFrame(self, maximum, text)
		self.progress.place(relx=0.02, rely=0.04, relwidth=0.96, relheight=0.9, anchor=NW)

	def set_max(self, maximum):
		self.progress.set_max(maximum)

	def set_text(self, text):
		self.progress.set_text(text)

	def set(self, value):
		self.progress.set(value)

	def increment(self, count=1):
		self.progress.increment(count)

	def complete(self):
		self.destroy()


class UI(ThemedTk):
	def __init__(self):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.option_add("*tearOff", FALSE)
		self.title("Bethesda Analysis and Translation Toolkit v0.1")
		width, height = self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.default_font = font.nametofont("TkDefaultFont")
		self.default_font.configure(family="Courier New", size=12)

		menubar = Menu(self)
		self['menu'] = menubar

		menu_file = Menu(menubar)
		menubar.add_cascade(menu=menu_file, label='File')

		self.tabs = Notebook(self)
		self.tabs.place(relx=0, rely=0, relwidth=1, relheight=1, anchor=NW)

		def open_mod():
			#OpenModDialog(self)
			modFile = filedialog.askopenfilename(title="Open Mod File", filetypes=[("", ".esp .esm .esl")])
			if modFile:
				with open(modFile, "rb") as file:
					file.seek(0, os.SEEK_END)
					fileSize = file.tell()
					file.seek(0, os.SEEK_SET)

					def open_mod(tab):
						tab.load_mod()

					tab = ModFrame(self.tabs, width)
					tab.place(relx=0, rely=0, relwidth=1, relheight=1, anchor=NW)
					self.tabs.add(tab, text=os.path.split(modFile)[1])
					self.tabs.select(tab)

					progress = ProgressDialog(tab, tab.winfo_width(), tab.winfo_height(), fileSize, "Opening Mod File")

					tab.settings.file = file
					tab.settings.esp = os.path.basename(file.name)
					tab.settings.prog = progress

					thread = threading.Thread(target=open_mod, args=(tab,))
					thread.setDaemon(True)
					thread.start()
					progress.grab_set()
					self.wait_window(progress)
		menu_file.add_command(label="Open Mod File", command=open_mod)

		def close_mod():
			if self.tabs.index('current') == "":
				return
			self.tabs.forget(self.tabs.index('current'))
		menu_file.add_command(label="Close Mod File", command=close_mod)

		def close_app():
			self.destroy()
		menu_file.add_command(label='Close Program', command=close_app)

		menu_import = Menu(menubar)
		menubar.add_cascade(menu=menu_import, label='Import')

		def parse_dict(settings):
			tree = settings.tree
			table = settings.table
			settings.prog.set_max(len(settings.dict))
			settings.prog.set(0)
			recordCount = 0
			for record in settings.dict:
				recordCount += len(settings.dict[record])
			settings.prog.set_max(recordCount)
			for record in settings.dict:
				settings.prog.set_text(f"Updating {record} Strings...")
				for formID in settings.dict[record]:
					# if 'status' not in settings.dict[record][formID]:
					# 	tags = (formID, record, 'Untranslated')
					# else:
					tags = (formID, record, settings.dict[record][formID]['status'])
					if tree.exists(formID):
						tree.item(formID, tags=tags)
					if table.exists(formID):
						edid = ""
						old = ""
						new = ""
						if 'EDID' in settings.dict[record][formID]:
							edid = settings.dict[record][formID]['EDID']
						if 'FULL' in settings.dict[record][formID]:
							old = settings.dict[record][formID]['FULL']['old']
							new = settings.dict[record][formID]['FULL']['new']
						if record == 'TES4':
							edid = "Header"
							old = settings.dict[record][formID]['AUTH']['old']
							new = settings.dict[record][formID]['AUTH']['new']
						if record == 'MESG':
							old = settings.dict[record][formID]['DESC']['old']
							new = settings.dict[record][formID]['DESC']['new']
						table.item(formID, values=(formID, record, edid, old, new, settings.dict[record][formID]['status']), tags=tags)
					settings.prog.increment()
			update_tree(tree)

		def import_dict():
			mod = self.tabs.nametowidget(self.tabs.select())
			if not mod or not mod.settings:
				return

			jsonFile = filedialog.askopenfilename(title="Import JSON File", filetypes=[("", ".json")])
			if jsonFile:
				progress = ProgressDialog(self, width, height, 1, "Reading JSON File...")

				def parse_json(jsonFile):
					with open(jsonFile, 'r', encoding='utf8') as file:
						mod.settings.dict = json.loads(file.read())
					mod.settings.prog = progress
					parse_dict(mod.settings)
					progress.complete()
				thread = threading.Thread(target=parse_json, args=(jsonFile,))
				thread.setDaemon(True)
				thread.start()
				progress.grab_set()
				self.wait_window(progress)

		menu_import.add_command(label="Import Translation from JSON", command=import_dict)

		def import_xtrans():
			mod = self.tabs.nametowidget(self.tabs.select())
			if not mod or not mod.settings:
				return

			xmlFile = filedialog.askopenfilename(title="Import xTranslator XML File", filetypes=[("", ".xml")])
			if xmlFile:
				progress = ProgressDialog(self, width, height, 1, "Reading XML File...")

				def parse_xml(xmlFile):
					with codecs.open(xmlFile, 'r', 'utf8') as file:
						xmlContents = file.read()
						xT = xmltodict.parse(xmlContents)
						progress.set_max(len(xT['SSTXMLRessources']['Content']['String']))
						progress.set(0)
						progress.set_text('Parsing XML Strings...')
						conversion = {
							'TES4': {'CNAM': 'AUTH', 'SNAM': 'DESC'},
							'MGEF': {'DNAM': 'DESC'},
							'ACTI': {'RNAM': 'DESC'},
							'BOOK': {'CNAM': 'TEXT'},
							'FLOR': {'RNAM': 'DESC'},
							'NPC_': {'SHRT': 'DESC'},
							'WOOP': {'TNAM': 'DESC'}
						}
						for entry in xT['SSTXMLRessources']['Content']['String']:
							partial = 'Final'
							if '@Partial' in entry:
								partial = entry['@Partial']
								if partial == '1':
									partial = 'In Progress'
								if partial == '2':
									partial = 'No Tx Needed'
							edid = entry['EDID']
							rec = entry['REC']
							index = None
							if '@id' in rec:
								index = entry['REC']['@id']
							if '#text' in rec:
								rec = entry['REC']['#text']
							field = rec[5:]
							rec = rec[:4]
							if rec not in mod.settings.dict:
								continue
							old = entry['Source']
							new = entry['Dest']
							if edid.startswith('['):
								edid = edid[1:].lower()
							if edid.endswith(']'):
								edid = edid[:-1].lower()
							if edid not in mod.settings.dict[rec]:							# xTranslator stores objects by EDID and not FormID unless EDID = ""
								fid = None
								if edid in mod.settings.util['EDID']:								# We store an EDID -> FormID dict within settings.util that we can reference
									fid = mod.settings.util['EDID'][edid]
								else:
									for i in mod.settings.dict[rec]:
										if mod.settings.dict[rec][i]['EDID'] == edid:				# If that doesn't work, we can search the dict for the EDID to get the corresponding FormID
											fid = i
											break
								if not fid:															# If we make it through the whole list of rec types and can't find the EDID, then it doesn't exist
									continue
							else:
								fid = edid

							def update_field(fid, field):
								if index:
									i = index
									if rec == 'FACT':
										mod.settings.dict['FACT'][fid]['RANK'][i][field]['old'] = old
										mod.settings.dict['FACT'][fid]['RANK'][i][field]['new'] = new
										mod.settings.dict['FACT'][fid]['RANK'][i]['status'] = partial
									if rec == 'QUST':
										if field == 'CNAM':
											s, i, m = '0', '0', 999
											for stage in mod.settings.dict['QUST'][fid]['Stage']:
												for idx in mod.settings.dict['QUST'][fid]['Stage'][stage]:
													o = mod.settings.dict['QUST'][fid]['Stage'][stage][idx]['old']
													d = jellyfish.levenshtein_distance(old, o)
													if d < m:
														s, i, m = stage, idx, d
											mod.settings.dict['QUST'][fid]['Stage'][s][i]['old'] = old
											mod.settings.dict['QUST'][fid]['Stage'][s][i]['new'] = new
											mod.settings.dict['QUST'][fid]['Stage'][s][i]['status'] = partial
										if field == 'NNAM':
											i, m = '0', 999
											for idx in mod.settings.dict['QUST'][fid]['Obj']:
												o = mod.settings.dict['QUST'][fid]['Obj'][idx]['old']
												d = jellyfish.levenshtein_distance(old, o)
												if d < m:
													i, m = idx, d
											mod.settings.dict['QUST'][fid]['Obj'][i]['old'] = old
											mod.settings.dict['QUST'][fid]['Obj'][i]['new'] = new
											mod.settings.dict['QUST'][fid]['Obj'][i]['status'] = partial
									if rec == 'MESG':
										mod.settings.dict['MESG'][fid]['ITXT'][i]['old'] = old
										mod.settings.dict['MESG'][fid]['ITXT'][i]['new'] = new
										mod.settings.dict['MESG'][fid]['ITXT'][i]['status'] = partial
									if rec == 'INFO':
										i, m = '0', 999
										for idx in mod.settings.dict['INFO'][fid]['NAM1']:
											o = mod.settings.dict['INFO'][fid]['NAM1'][idx]['old']
											d = jellyfish.levenshtein_distance(old, o)
											if d < m:
												i, m = idx, d
										mod.settings.dict['INFO'][fid]['NAM1'][i]['old'] = old
										mod.settings.dict['INFO'][fid]['NAM1'][i]['new'] = new
										mod.settings.dict['INFO'][fid]['NAM1'][i]['status'] = partial
									return
								if rec == 'INFO' and field == 'NAM1':
									i = list(mod.settings.dict['INFO'][fid]['NAM1'])[0]
									mod.settings.dict['INFO'][fid]['NAM1'][i]['old'] = old
									mod.settings.dict['INFO'][fid]['NAM1'][i]['new'] = new
									mod.settings.dict['INFO'][fid]['NAM1'][i]['status'] = partial
									return
								if rec == 'QUST':
									if field == 'CNAM':
										s = list(mod.settings.dict['QUST'][fid]['Stage'])[0]
										i = list(mod.settings.dict['QUST'][fid]['Stage'][s])[0]
										mod.settings.dict['QUST'][fid]['Stage'][s][i]['old'] = old
										mod.settings.dict['QUST'][fid]['Stage'][s][i]['new'] = new
										mod.settings.dict['QUST'][fid]['Stage'][s][i]['status'] = partial
									if field == 'NNAM':
										i = list(mod.settings.dict['QUST'][fid]['Obj'])[0]
										mod.settings.dict['QUST'][fid]['Obj'][i]['old'] = old
										mod.settings.dict['QUST'][fid]['Obj'][i]['new'] = new
										mod.settings.dict['QUST'][fid]['Obj'][i]['status'] = partial
									return
								if rec in conversion and field in conversion[rec]:
									field = conversion[rec][field]
								mod.settings.dict[rec][fid][field]['old'] = old
								mod.settings.dict[rec][fid][field]['new'] = new
							update_field(fid, field)
							mod.settings.dict[rec][fid]['status'] = partial
							progress.increment()
					mod.settings.prog = progress
					parse_dict(mod.settings)
					progress.complete()
				thread = threading.Thread(target=parse_xml, args=(xmlFile,))
				thread.setDaemon(True)
				thread.start()
				progress.grab_set()
				self.wait_window(progress)
		menu_import.add_command(label="Import Translation from xTranslator XML", command=import_xtrans)

		menu_export = Menu(menubar)
		menubar.add_cascade(menu=menu_export, label='Export')

		def export_dict():
			mod = self.tabs.nametowidget(self.tabs.select())
			if not mod or not mod.settings:
				return

			jsonFile = filedialog.asksaveasfilename(title="Save JSON File", defaultextension='.json', filetypes=[("", ".json")])
			if jsonFile:
				progress = ProgressDialog(self, width, height, 0, "Writing JSON File...")

				def write_json(jsonFile):
					if not jsonFile.endswith('.json'):
						jsonFile += '.json'
					with open(jsonFile, 'w', encoding='utf8') as file:
						json.dump(mod.settings.dict, file, ensure_ascii=False)
						progress.complete()
				thread = threading.Thread(target=write_json, args=(jsonFile,))
				thread.setDaemon(True)
				thread.start()
				progress.grab_set()
				self.wait_window(progress)

		menu_export.add_command(label='Export Translation to JSON', command=export_dict)

		def export_esp():
			mod = self.tabs.nametowidget(self.tabs.select())
			if not mod or not mod.settings:
				return

			ext = os.path.splitext(mod.settings.file.name)[1]
			outFile = filedialog.asksaveasfilename(title="Save Mod File", defaultextension=ext, filetypes=[("", f"{ext}")])
			if outFile:
				with open(mod.settings.file.name, "rb") as inFile:
					with open(outFile, "w") as file:
						file.write("data")
					with open(outFile, "r+b") as file:
						inFile.seek(0, os.SEEK_END)
						fileSize = inFile.tell()
						inFile.seek(0, os.SEEK_SET)

						progress = ProgressDialog(self, width, height, fileSize, "Writing Mod File")

						file.truncate(0)
						mod.settings.file = inFile
						mod.settings.target = file
						mod.settings.prog = progress
						mod.settings.mode = 'w'
						mod.settings.write = 's'

						def write_mod():
							settings = mod.settings
							settings.prog.set_text("Parsing TES4 Header...")

							chunk = settings.file.read(24)
							if checkType(chunk) == "TES4":
								TES4(settings, chunk)
							else:
								print("Invalid Mod File!")
								settings.prog.complete()
								return

							chunk = settings.file.read(24)
							while chunk:
								Group(settings, chunk)
								chunk = settings.file.read(24)

							settings.prog.complete()

						thread = threading.Thread(target=write_mod, args=())
						thread.setDaemon(True)
						thread.start()
						progress.grab_set()
						self.wait_window(progress)

		menu_export.add_command(label='Export Translated Mod', command=export_esp)

		self.mainloop()


UI()
