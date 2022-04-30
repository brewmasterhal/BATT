from tkinter import *
import tkinter as tk
from tkinter.ttk import *
from ttkthemes import ThemedTk
from googletrans import Translator

from Const import *


def update_tree(tree):
	for record in tree.get_children(''):
		if record == '00000000':
			continue
		if len(tree.get_children(record)) == 0:
			continue
		rTags = tree.item(record, 'tags')
		status = 0
		for item in tree.get_children(record):
			tags = tree.item(item, 'tags')
			stat = states.index(tags[2])
			status = max(status, stat)
		rTags = (rTags[0], rTags[1], states[status])
		tree.item(record, tags=rTags)


class ScrollText(Frame):

	def __init__(self, parent, width, text="", editable=True):
		Frame.__init__(self, parent)

		self.text = Text(self, wrap=WORD, font=textFont)
		self.text.insert('1.0', text)
		if not editable:
			self.text['state'] = DISABLED
		self.text.place(relx=0, rely=0, width=width-scrollWidth, relheight=1)

		yscroll = Scrollbar(self, orient=VERTICAL, command=self.text.yview)
		yscroll.place(x=width-scrollWidth, rely=0, width=scrollWidth, relheight=1)
		self.text.configure(yscrollcommand=yscroll.set)


class EditBlock(Frame):

	def __init__(self, parent, settings, field, label, width, height, scroll=False):
		Frame.__init__(self, parent)

		if scroll:
			limit = 1950
		else:
			limit = 248
		y = 0

		old = field['old'].strip()
		gt = field['gt'].strip()
		new = field['new'].strip()

		self.labLabel = Label(self, text=label, font=("Helvetica", 16, 'bold'))
		self.labLabel.place(relx=0.1, y=y, relwidth=0.9, height=labelHeight)
		y += 35

		self.oldLabel = Label(self, text="Original", anchor=CENTER, font=labelFont)
		self.oldLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.oldLim = Label(self, text=f"{len(old)}/{limit}", anchor=CENTER, font=labelFont)
		self.oldLim.place(relx=0, y=y+30, relwidth=0.09, height=labelHeight)

		self.gtButton = tk.Button(self, text="Translate", font=labelFont)
		self.gtButton.place(relx=0, y=y+60, relwidth=0.09, height=buttonHeight)

		if scroll:
			self.oldScroll = ScrollText(self, width, old, False)
			self.oldText = self.oldScroll.text
			self.oldScroll.place(relx=0.1, y=y, relwidth=0.89, height=height)
		else:
			self.oldText = Text(self, wrap=WORD, font=textFont)
			self.oldText.insert('1.0', old)
			self.oldText['state'] = DISABLED
			self.oldText.place(relx=0.1, y=y, relwidth=0.89, height=height)
		y += height + padding

		self.gtLabel = Label(self, text="Google", anchor=CENTER, font=labelFont)
		self.gtLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.gtLim = Label(self, text=f"{len(gt)}/{limit}", anchor=CENTER, font=labelFont)
		self.gtLim.place(relx=0, y=y+30, relwidth=0.09, height=labelHeight)

		self.copyButton = tk.Button(self, text="Copy", font=labelFont)
		self.copyButton.place(relx=0, y=y+60, relwidth=0.09, height=buttonHeight)

		if scroll:
			self.gtScroll = ScrollText(self, width, gt, False)
			self.gtText = self.gtScroll.text
			self.gtScroll.place(relx=0.1, y=y, relwidth=0.89, height=height)
		else:
			self.gtText = Text(self, wrap=WORD, font=textFont)
			self.gtText.insert('1.0', gt)
			self.gtText['state'] = DISABLED
			self.gtText.place(relx=0.1, y=y, relwidth=0.89, height=height)
		y += height + padding

		self.newLabel = Label(self, text="Translated", anchor=CENTER, font=labelFont)
		self.newLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.newLim = Label(self, text=f"{len(new)}/{limit}", anchor=CENTER, font=labelFont)
		self.newLim.place(relx=0, y=y+30, relwidth=0.09, height=labelHeight)

		self.tagButton = tk.Button(self, text="Tag", font=labelFont)
		self.tagButton.place(relx=0, y=y+60, relwidth=0.09, height=buttonHeight)

		if scroll:
			self.newScroll = ScrollText(self, width, new, True)
			self.newText = self.newScroll.text
			self.newScroll.place(relx=0.1, y=y, relwidth=0.89, height=height)
		else:
			self.newText = Text(self, wrap=WORD, font=textFont)
			self.newText.insert('1.0', new)
			self.newText.place(relx=0.1, y=y, relwidth=0.89, height=height)
		y += height + padding

		def update_limit(text, label, char):
			count = len(text.get('1.0', END) + char)
			label.configure(text=f"{count}/{limit}")
			if count > limit:
				label.configure(foreground='red3')
			else:
				label.configure(foreground='green')

		def tag_text():
			text = self.newText.get('1.0', END)
			if text.startswith("$"):
				return
			text = f"${settings.fid}$ "
			self.newText.insert('1.0', text)
			update_limit(self.newText, self.newLim, '')

		def copy_gt():
			self.newText.delete('1.0', END)
			self.newText.insert('1.0', self.gtText.get('1.0', END).strip())
			update_limit(self.newText, self.newLim, '')

		def text_changed(event):
			update_limit(self.newText, self.newLim, event.char)

		def get_gt():
			translator = Translator()
			tx = translator.translate(old, src=settings.srcLang, dest=settings.tgtLang)
			self.gtText['state'] = NORMAL
			self.gtText.delete('1.0', END)
			self.gtText.insert('1.0', tx.text.strip())
			update_limit(self.gtText, self.gtLim, '')
			self.gtText['state'] = DISABLED

		update_limit(self.oldText, self.oldLim, '')
		update_limit(self.gtText, self.gtLim, '')
		update_limit(self.newText, self.newLim, '')
		if not scroll:
			self.newText.bind("<Return>", lambda e: 'break')
		self.newText.bind("<Key>", text_changed)
		self.gtButton.configure(command=get_gt)
		self.copyButton.configure(command=copy_gt)
		self.tagButton.configure(command=tag_text)


def sort_column(table, col, reverse):
	items = [(table.set(k, col), k) for k in table.get_children('')]				# Create a list of all table elements and sort it by the chosen column value
	items.sort(reverse=reverse)

	for index, (val, k) in enumerate(items):										# Shift each row into its new position
		table.move(k, '', index)

	table.heading(col, command=lambda: sort_column(table, col, not reverse))		# Replace the existing lambda with one having the inverse sort direction


class Tes4Editor(ThemedTk):
	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")

		formID = '00000000'
		record = settings.dict['TES4'][formID]

		self.typeLabel = Label(self, text="Type: TES4", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.authBlock = EditBlock(self, settings, record['AUTH'], "Author", width/2, height/8)
		self.authBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width/2 + padding

		self.descBlock = EditBlock(self, settings, record['DESC'], "Description", width/2, height/4, True)
		self.descBlock.place(x=x, y=y, width=width / 2 - padding, height=height - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'TES4', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['TES4'][formID]['AUTH']['gt'] = self.authBlock.gtText.get('1.0', END).strip()
			settings.dict['TES4'][formID]['AUTH']['new'] = self.authBlock.newText.get('1.0', END).strip()

			settings.dict['TES4'][formID]['DESC']['gt'] = self.descBlock.gtText.get('1.0', END).strip()
			settings.dict['TES4'][formID]['DESC']['new'] = self.descBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.authBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['TES4'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class NamedEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]

		self.typeLabel = Label(self, text=f"Type: {settings.rec}", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {settings.fid}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Name", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (settings.fid, settings.rec, self.var.get())
			settings.tree.item(settings.fid, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict[settings.rec][settings.fid]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict[settings.rec][settings.fid]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(settings.fid, 'values')
			settings.table.item(settings.fid, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict[settings.rec][settings.fid]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class DescEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]

		self.typeLabel = Label(self, text=f"Type: {settings.rec}", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {settings.fid}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Name", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		label = "Description"
		if settings.rec == 'ACTI':
			label = "Activate Verb"
		if settings.rec == 'FLOR':
			label = "Harvest Verb"
		if settings.rec == 'NPC_':
			label = "Short Name"
		self.descBlock = EditBlock(self, settings, record['DESC'], label, width/2, height/8)
		self.descBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (settings.fid, settings.rec, self.var.get())
			settings.tree.item(settings.fid, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict[settings.rec][settings.fid]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict[settings.rec][settings.fid]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			settings.dict[settings.rec][settings.fid]['DESC']['gt'] = self.descBlock.gtText.get('1.0', END).strip()
			settings.dict[settings.rec][settings.fid]['DESC']['new'] = self.descBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(settings.fid, 'values')
			settings.table.item(settings.fid, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict[settings.rec][settings.fid]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class BookEditor(DescEditor):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		self.typeLabel = Label(self, text="Type: BOOK", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Name", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.descBlock = EditBlock(self, settings, record['DESC'], "Text", width / 2, height / 4, True)
		self.descBlock.place(x=x, y=y, width=width / 2 - padding, height=height - padding)
		x, y = 0, height / 2

		self.textBlock = EditBlock(self, settings, record['TEXT'], "Description", width / 2, height / 8)
		self.textBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'BOOK', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['BOOK'][formID]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['BOOK'][formID]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			settings.dict['BOOK'][formID]['TEXT']['gt'] = self.textBlock.gtText.get('1.0', END).strip()
			settings.dict['BOOK'][formID]['TEXT']['new'] = self.textBlock.newText.get('1.0', END).strip()

			settings.dict['BOOK'][formID]['DESC']['gt'] = self.descBlock.gtText.get('1.0', END).strip()
			settings.dict['BOOK'][formID]['DESC']['new'] = self.descBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['BOOK'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class RankEditor(ThemedTk):

	def __init__(self, settings, table, rank):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['FACT'][settings.fid]['RANK'][rank]

		self.typeLabel = Label(self, text=f"Faction Rank", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Rank: {rank}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.mnamBlock = EditBlock(self, settings, record['MNAM'], "Male Title", width/2, height/8)
		self.mnamBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.fnamBlock = EditBlock(self, settings, record['FNAM'], "Female Title", width / 2, height / 8)
		self.fnamBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			values = table.item(rank, 'values')
			tags = (rank, self.var.get())
			table.item(rank, values=(values[0], self.mnamBlock.newText.get('1.0', END), self.fnamBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['FACT'][settings.fid]['RANK'][rank]['status'] = self.var.get()

			# Update dict entries
			settings.dict['FACT'][settings.fid]['RANK'][rank]['MNAM']['gt'] = self.mnamBlock.gtText.get('1.0', END).strip()
			settings.dict['FACT'][settings.fid]['RANK'][rank]['MNAM']['new'] = self.mnamBlock.newText.get('1.0', END).strip()

			settings.dict['FACT'][settings.fid]['RANK'][rank]['FNAM']['gt'] = self.fnamBlock.gtText.get('1.0', END).strip()
			settings.dict['FACT'][settings.fid]['RANK'][rank]['FNAM']['new'] = self.fnamBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class FactEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		self.typeLabel = Label(self, text="Type: FACT", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Name", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.rankLabel = Label(self, text="Ranks", font=("Helvetica", 16, 'bold'))
		self.rankLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'mnam', 'fnam')
		rankTable = Treeview(self, columns=columns, show='headings')
		rankTable.heading('fid', text='Rank', command=lambda: sort_column(rankTable, 'fid', False))
		rankTable.column('fid', minwidth=50, width=50, stretch=NO, anchor=CENTER)
		rankTable.heading('mnam', text='Male', command=lambda: sort_column(rankTable, 'mnam', False))
		rankTable.column('mnam', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		rankTable.heading('fnam', text='Female', command=lambda: sort_column(rankTable, 'fnam', False))
		rankTable.column('fnam', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		rankTable.bind('<Double-1>', lambda e: 'break')
		rankTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=rankTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		rankTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			rankTable.tag_configure(states[i], background=colors[i])

		for rank in settings.dict['FACT'][formID]['RANK']:
			mnam = settings.dict['FACT'][formID]['RANK'][rank]['MNAM']['new']
			fnam = settings.dict['FACT'][formID]['RANK'][rank]['FNAM']['new']
			status = settings.dict['FACT'][formID]['RANK'][rank]['status']
			rankTable.insert('', 'end', rank, values=(rank, mnam, fnam), tags=(rank, status))

		def table_edit(event):
			item = rankTable.identify('item', event.x, event.y)
			tags = rankTable.item(item, 'tags')
			rank = tags[0]
			settings.fid = formID
			editor = RankEditor(settings, rankTable, rank)
			self.wait_window(editor)

		for item in rankTable.get_children(''):
			tags = rankTable.item(item, 'tags')
			rankTable.tag_bind(tags[0], '<Double-1>', table_edit)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'FACT', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['FACT'][formID]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['FACT'][formID]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['FACT'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class ItxtEditor(ThemedTk):

	def __init__(self, settings, table, index):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['MESG'][settings.fid]['ITXT'][index]

		self.typeLabel = Label(self, text=f"Messagebox Option", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Index: {index}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record, "Text", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			values = table.item(index, 'values')
			tags = (index, self.var.get())
			table.item(index, values=(values[0], values[1], self.fullBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['MESG'][settings.fid]['ITXT'][index]['status'] = self.var.get()

			# Update dict entries
			settings.dict['MESG'][settings.fid]['ITXT'][index]['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['MESG'][settings.fid]['ITXT'][index]['new'] = self.fullBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class MesgEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		self.typeLabel = Label(self, text="Type: MESG", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Category Name", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.txtLabel = Label(self, text="Options", font=("Helvetica", 16, 'bold'))
		self.txtLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		txtTable = Treeview(self, columns=columns, show='headings')
		txtTable.heading('fid', text='Option', command=lambda: sort_column(txtTable, 'fid', False))
		txtTable.column('fid', minwidth=50, width=50, stretch=NO, anchor=CENTER)
		txtTable.heading('old', text='Original', command=lambda: sort_column(txtTable, 'old', False))
		txtTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		txtTable.heading('new', text='Translation', command=lambda: sort_column(txtTable, 'new', False))
		txtTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		txtTable.bind('<Double-1>', lambda e: 'break')
		txtTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=txtTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		txtTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			txtTable.tag_configure(states[i], background=colors[i])

		for opt in settings.dict['MESG'][formID]['ITXT']:
			old = settings.dict['MESG'][formID]['ITXT'][opt]['old']
			new = settings.dict['MESG'][formID]['ITXT'][opt]['new']
			status = settings.dict['MESG'][formID]['ITXT'][opt]['status']
			txtTable.insert('', 'end', opt, values=(opt, old, new), tags=(opt, status))

		def table_edit(event):
			item = txtTable.identify('item', event.x, event.y)
			tags = txtTable.item(item, 'tags')
			index = tags[0]
			settings.fid = formID
			editor = ItxtEditor(settings, txtTable, index)
			self.wait_window(editor)

		for item in txtTable.get_children(''):
			tags = txtTable.item(item, 'tags')
			txtTable.tag_bind(tags[0], '<Double-1>', table_edit)

		x, y = 0, height / 2

		self.descBlock = EditBlock(self, settings, record['DESC'], "Message Text", width/2, height/8)
		self.descBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'MESG', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['MESG'][formID]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['MESG'][formID]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			settings.dict['MESG'][formID]['DESC']['gt'] = self.descBlock.gtText.get('1.0', END).strip()
			settings.dict['MESG'][formID]['DESC']['new'] = self.descBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['MESG'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class DialEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		self.typeLabel = Label(self, text="Type: DIAL", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record['FULL'], "Player Dialog", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.infoLabel = Label(self, text="NPC Responses", font=("Helvetica", 16, 'bold'))
		self.infoLabel.place(x=x+padding, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		infoTable = Treeview(self, columns=columns, show='headings')
		infoTable.heading('fid', text='Index', command=lambda: sort_column(infoTable, 'fid', False))
		infoTable.column('fid', minwidth=70, width=70, stretch=NO, anchor=CENTER)
		infoTable.heading('old', text='Original', command=lambda: sort_column(infoTable, 'old', False))
		infoTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		infoTable.heading('new', text='Translation', command=lambda: sort_column(infoTable, 'new', False))
		infoTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		infoTable.bind('<Double-1>', lambda e: 'break')
		infoTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=infoTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		infoTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			infoTable.tag_configure(states[i], background=colors[i])

		if formID in settings.util['D>I'] and len(settings.util['D>I'][formID]) > 0:
			for info in settings.util['D>I'][formID]:
				if settings.dict['INFO'][info]['NAM1']:
					idx = list(settings.dict['INFO'][info]['NAM1'])[0]
					old = settings.dict['INFO'][info]['NAM1'][idx]['old']
					new = settings.dict['INFO'][info]['NAM1'][idx]['new']
					status = settings.dict['INFO'][info]['status']
					infoTable.insert('', 'end', info, values=(info, old, new), tags=(info, 'INFO', status))

		def table_edit(event):
			item = infoTable.identify('item', event.x, event.y)
			tags = infoTable.item(item, 'tags')
			settings.fid = tags[0]  # FormID
			settings.rec = tags[1]  # Record type
			settings.mode = tags[2]  # Translation status
			editor = InfoEditor(settings)
			self.wait_window(editor)

			index = list(settings.dict['INFO'][tags[0]]['NAM1'])[0]
			old = settings.dict['INFO'][tags[0]]['NAM1'][index]['old']
			new = settings.dict['INFO'][tags[0]]['NAM1'][index]['new']
			status = settings.dict['INFO'][tags[0]]['status']
			infoTable.item(tags[0], values=(tags[0], old, new), tags=(tags[0], 'INFO', status))

		for item in infoTable.get_children(''):
			tags = infoTable.item(item, 'tags')
			infoTable.tag_bind(tags[0], '<Double-1>', table_edit)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'DIAL', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['DIAL'][formID]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['DIAL'][formID]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['DIAL'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class NamEditor(ThemedTk):

	def __init__(self, settings, table, index):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['INFO'][settings.fid]['NAM1'][index]

		self.typeLabel = Label(self, text=f"NPC Dialog", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Index: {index}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record, "Text", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			values = table.item(index, 'values')
			tags = (index, self.var.get())
			table.item(index, values=(values[0], values[1], self.fullBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['INFO'][settings.fid]['NAM1'][index]['status'] = self.var.get()

			# Update dict entries
			settings.dict['INFO'][settings.fid]['NAM1'][index]['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['INFO'][settings.fid]['NAM1'][index]['new'] = self.fullBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class InfoEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['INFO'][settings.fid]
		formID = settings.fid

		self.typeLabel = Label(self, text="Type: INFO", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(self, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(self, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.rnamBlock = EditBlock(self, settings, record['RNAM'], "Player Dialog", width/2, height/8)
		self.rnamBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.dialLabel = Label(self, text="Player Responses", font=("Helvetica", 16, 'bold'))
		self.dialLabel.place(x=x+padding, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		dialTable = Treeview(self, columns=columns, show='headings')
		dialTable.heading('fid', text='Index', command=lambda: sort_column(dialTable, 'fid', False))
		dialTable.column('fid', minwidth=70, width=70, stretch=NO, anchor=CENTER)
		dialTable.heading('old', text='Original', command=lambda: sort_column(dialTable, 'old', False))
		dialTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.heading('new', text='Translation', command=lambda: sort_column(dialTable, 'new', False))
		dialTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.bind('<Double-1>', lambda e: 'break')
		dialTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=dialTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		dialTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			dialTable.tag_configure(states[i], background=colors[i])

		if formID in settings.util['I>D'] and len(settings.util['I>D'][formID]) > 0:
			for dial in settings.util['I>D'][formID]:
				old = settings.dict['DIAL'][dial]['FULL']['old']
				new = settings.dict['DIAL'][dial]['FULL']['new']
				status = settings.dict['DIAL'][dial]['status']
				dialTable.insert('', 'end', dial, values=(dial, old, new), tags=(dial, 'DIAL', status))

		def dialTable_edit(event):
			item = dialTable.identify('item', event.x, event.y)
			tags = dialTable.item(item, 'tags')
			settings.fid = tags[0]  # FormID
			settings.rec = tags[1]  # Record type
			settings.mode = tags[2]  # Translation status
			editor = DialEditor(settings)
			self.wait_window(editor)

			old = settings.dict['DIAL'][tags[0]]['old']
			new = settings.dict['DIAL'][tags[0]]['new']
			status = settings.dict['DIAL'][tags[0]]['status']
			dialTable.item(tags[0], values=(tags[0], old, new), tags=(tags[0], 'DIAL', status))

		for item in dialTable.get_children(''):
			tags = dialTable.item(item, 'tags')
			dialTable.tag_bind(tags[0], '<Double-1>', dialTable_edit)

		x, y = 0, height / 2

		self.namLabel = Label(self, text="NPC Dialogs", font=("Helvetica", 16, 'bold'))
		self.namLabel.place(x=padding, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		namTable = Treeview(self, columns=columns, show='headings')
		namTable.heading('fid', text='Index', command=lambda: sort_column(namTable, 'fid', False))
		namTable.column('fid', minwidth=50, width=50, stretch=NO, anchor=CENTER)
		namTable.heading('old', text='Original', command=lambda: sort_column(namTable, 'old', False))
		namTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		namTable.heading('new', text='Translation', command=lambda: sort_column(namTable, 'new', False))
		namTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		namTable.bind('<Double-1>', lambda e: 'break')
		namTable.place(x=padding, y=y, width=width / 2 - padding * 2 - scrollWidth, height=height / 3 - padding * 2 - labelHeight)
		tabScroll = Scrollbar(self, orient=VERTICAL, command=namTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=height / 3 - padding * 2 - labelHeight)
		namTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			namTable.tag_configure(states[i], background=colors[i])

		for nam in settings.dict['INFO'][formID]['NAM1']:
			old = settings.dict['INFO'][formID]['NAM1'][nam]['old']
			new = settings.dict['INFO'][formID]['NAM1'][nam]['new']
			status = settings.dict['INFO'][formID]['NAM1'][nam]['status']
			namTable.insert('', 'end', nam, values=(nam, old, new), tags=(nam, status))

		def namTable_edit(event):
			item = namTable.identify('item', event.x, event.y)
			tags = namTable.item(item, 'tags')
			index = tags[0]
			settings.fid = formID
			editor = NamEditor(settings, namTable, index)
			self.wait_window(editor)

		for item in namTable.get_children(''):
			tags = namTable.item(item, 'tags')
			namTable.tag_bind(tags[0], '<Double-1>', namTable_edit)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update dict entries
			settings.dict['INFO'][formID]['RNAM']['gt'] = self.rnamBlock.gtText.get('1.0', END).strip()
			settings.dict['INFO'][formID]['RNAM']['new'] = self.rnamBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class PropEditor(ThemedTk):

	def __init__(self, settings, table, name, index):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['QUST'][settings.fid]['Prop'][name][index]

		self.typeLabel = Label(self, text=f"Quest Script String Property", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Name: {name}${index}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record, "String", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			pid = f"{name}${index}"
			values = table.item(pid, 'values')
			tags = (name, index, self.var.get())
			table.item(pid, values=(values[0], values[1], self.fullBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['QUST'][settings.fid]['Prop'][name][index]['status'] = self.var.get()

			# Update dict entries
			settings.dict['QUST'][settings.fid]['Prop'][name][index]['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['QUST'][settings.fid]['Prop'][name][index]['new'] = self.fullBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class StageEditor(ThemedTk):

	def __init__(self, settings, table, stage, index):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['QUST'][settings.fid]['Stage'][stage][index]

		self.typeLabel = Label(self, text=f"Quest Journal Entry", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Stage: {stage}${index}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record, "Text", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			sid = f"{stage}${index}"
			values = table.item(sid, 'values')
			tags = (stage, index, self.var.get())
			table.item(sid, values=(values[0], values[1], self.fullBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['QUST'][settings.fid]['Stage'][stage][index]['status'] = self.var.get()

			# Update dict entries
			settings.dict['QUST'][settings.fid]['Stage'][stage][index]['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['QUST'][settings.fid]['Stage'][stage][index]['new'] = self.fullBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class ObjEditor(ThemedTk):

	def __init__(self, settings, table, obj):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict['QUST'][settings.fid]['Obj'][obj]

		self.typeLabel = Label(self, text=f"Type: Quest Objective", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.49, height=labelHeight)

		self.edidLabel = Label(self, text=f"Objective: {obj}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.5, y=y, relwidth=0.49, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(self, settings, record, "Text", width/2, height/8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)

		self.botFrame = Frame(self)
		self.botFrame.place(relx=0.5, y=height - 130 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, record['status'], *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update table
			values = table.item(obj, 'values')
			tags = (obj, self.var.get())
			table.item(obj, values=(values[0], self.fullBlock.newText.get('1.0', END)), tags=tags)
			settings.dict['QUST'][settings.fid]['Obj'][obj]['status'] = self.var.get()

			# Update dict entries
			settings.dict['QUST'][settings.fid]['Obj'][obj]['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['QUST'][settings.fid]['Obj'][obj]['new'] = self.fullBlock.newText.get('1.0', END).strip()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)


class QustEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		tabs = Notebook(self)
		tabs.place(relx=0, rely=0, relwidth=1, relheight=1)

		tab1 = Frame(tabs)
		tab1.place(relx=0, rely=0, relwidth=1, relheight=1)
		tabs.add(tab1, text="Properties")
		tabs.select(tab1)

		self.typeLabel = Label(tab1, text="Type: QUST", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(tab1, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(tab1, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.fullBlock = EditBlock(tab1, settings, record['FULL'], "Name", width / 2, height / 8)
		self.fullBlock.place(x=x, y=y, width=width / 2 - padding, height=height / 2 - padding)
		x = width / 2 + padding

		self.propLabel = Label(tab1, text="Script String Properties", font=("Helvetica", 16, 'bold'))
		self.propLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		propTable = Treeview(tab1, columns=columns, show='headings')
		propTable.heading('fid', text='Index', command=lambda: sort_column(propTable, 'fid', False))
		propTable.column('fid', minwidth=150, width=150, stretch=NO, anchor=CENTER)
		propTable.heading('old', text='Original', command=lambda: sort_column(propTable, 'old', False))
		propTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		propTable.heading('new', text='Translation', command=lambda: sort_column(propTable, 'new', False))
		propTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		propTable.bind('<Double-1>', lambda e: 'break')
		propTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(tab1, orient=VERTICAL, command=propTable.yview)
		tabScroll.place(x=x + width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		propTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			propTable.tag_configure(states[i], background=colors[i])

		for prop in settings.dict['QUST'][formID]['Prop']:
			for index in settings.dict['QUST'][formID]['Prop'][prop]:
				old = settings.dict['QUST'][formID]['Prop'][prop][index]['old']
				new = settings.dict['QUST'][formID]['Prop'][prop][index]['new']
				status = settings.dict['QUST'][formID]['Prop'][prop][index]['status']
				pid = f"{prop}${index}"
				propTable.insert('', 'end', pid, values=(pid, old, new), tags=(prop, index, status))

		def propTable_edit(event):
			item = propTable.identify('item', event.x, event.y)
			tags = propTable.item(item, 'tags')
			name = tags[0]
			index = tags[1]
			settings.fid = formID
			editor = PropEditor(settings, propTable, name, index)
			self.wait_window(editor)
		for item in propTable.get_children(''):
			tags = propTable.item(item, 'tags')
			propTable.tag_bind(tags[0], '<Double-1>', propTable_edit)

		self.botFrame = Frame(tab1)
		self.botFrame.place(relx=0.5, y=height - 160 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'QUST', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update dict entries
			settings.dict['QUST'][formID]['FULL']['gt'] = self.fullBlock.gtText.get('1.0', END).strip()
			settings.dict['QUST'][formID]['FULL']['new'] = self.fullBlock.newText.get('1.0', END).strip()

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['QUST'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)

		tab2 = Frame(tabs)
		tab2.place(relx=0, rely=0, relwidth=1, relheight=1)
		tabs.add(tab2, text="Stages")
		x, y = padding, padding

		self.stageLabel = Label(tab2, text="Stages", font=("Helvetica", 16, 'bold'))
		self.stageLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		stageTable = Treeview(tab2, columns=columns, show='headings')
		stageTable.heading('fid', text='Index', command=lambda: sort_column(stageTable, 'fid', False))
		stageTable.column('fid', minwidth=50, width=50, stretch=NO, anchor=CENTER)
		stageTable.heading('old', text='Original', command=lambda: sort_column(stageTable, 'old', False))
		stageTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		stageTable.heading('new', text='Translation', command=lambda: sort_column(stageTable, 'new', False))
		stageTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		stageTable.bind('<Double-1>', lambda e: 'break')
		stageTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(tab2, orient=VERTICAL, command=stageTable.yview)
		tabScroll.place(x=width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		stageTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			stageTable.tag_configure(states[i], background=colors[i])

		for stage in settings.dict['QUST'][formID]['Stage']:
			for index in settings.dict['QUST'][formID]['Stage'][stage]:
				old = settings.dict['QUST'][formID]['Stage'][stage][index]['old']
				new = settings.dict['QUST'][formID]['Stage'][stage][index]['new']
				status = settings.dict['QUST'][formID]['Stage'][stage][index]['status']
				sid = f"{stage}${index}"
				stageTable.insert('', 'end', sid, values=(sid, old, new), tags=(stage, index, status))

		def stageTable_edit(event):
			item = stageTable.identify('item', event.x, event.y)
			tags = stageTable.item(item, 'tags')
			stage = tags[0]
			index = tags[1]
			settings.fid = formID
			editor = StageEditor(settings, stageTable, stage, index)
			self.wait_window(editor)
		for item in stageTable.get_children(''):
			tags = stageTable.item(item, 'tags')
			stageTable.tag_bind(tags[0], '<Double-1>', stageTable_edit)

		x, y = width / 2 + padding, padding

		self.objLabel = Label(tab2, text="Objectives", font=("Helvetica", 16, 'bold'))
		self.objLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		objTable = Treeview(tab2, columns=columns, show='headings')
		objTable.heading('fid', text='Index', command=lambda: sort_column(objTable, 'fid', False))
		objTable.column('fid', minwidth=50, width=50, stretch=NO, anchor=CENTER)
		objTable.heading('old', text='Original', command=lambda: sort_column(objTable, 'old', False))
		objTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		objTable.heading('new', text='Translation', command=lambda: sort_column(objTable, 'new', False))
		objTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		objTable.bind('<Double-1>', lambda e: 'break')
		objTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(tab2, orient=VERTICAL, command=objTable.yview)
		tabScroll.place(x=width - padding - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		objTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			objTable.tag_configure(states[i], background=colors[i])

		for obj in settings.dict['QUST'][formID]['Obj']:
			old = settings.dict['QUST'][formID]['Obj'][obj]['old']
			new = settings.dict['QUST'][formID]['Obj'][obj]['new']
			status = settings.dict['QUST'][formID]['Obj'][obj]['status']
			objTable.insert('', 'end', obj, values=(obj, old, new), tags=(obj, status))

		def objTable_edit(event):
			item = objTable.identify('item', event.x, event.y)
			tags = objTable.item(item, 'tags')
			obj = tags[0]
			settings.fid = formID
			editor = ObjEditor(settings, objTable, obj)
			self.wait_window(editor)
		for item in objTable.get_children(''):
			tags = objTable.item(item, 'tags')
			objTable.tag_bind(tags[0], '<Double-1>', objTable_edit)

		tab3 = Frame(tabs)
		tab3.place(relx=0, rely=0, relwidth=1, relheight=1)
		tabs.add(tab3, text="Dialogs")
		x, y = padding, padding

		self.dialLabel = Label(tab3, text="Dialogs", font=("Helvetica", 16, 'bold'))
		self.dialLabel.place(x=x, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		dialTable = Treeview(tab3, columns=columns, show='headings')
		dialTable.heading('fid', text='Index', command=lambda: sort_column(dialTable, 'fid', False))
		dialTable.column('fid', minwidth=70, width=70, stretch=NO, anchor=CENTER)
		dialTable.heading('old', text='Original', command=lambda: sort_column(dialTable, 'old', False))
		dialTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.heading('new', text='Translation', command=lambda: sort_column(dialTable, 'new', False))
		dialTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.bind('<Double-1>', lambda e: 'break')
		dialTable.place(x=x, y=y, width=width / 2 - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(tab3, orient=VERTICAL, command=dialTable.yview)
		tabScroll.place(x=width / 2 - padding * 2 - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		dialTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			dialTable.tag_configure(states[i], background=colors[i])

		if formID in settings.util['Q>D']:
			for dial in settings.util['Q>D'][formID]:
				old = settings.dict['DIAL'][dial]['FULL']['old']
				new = settings.dict['DIAL'][dial]['FULL']['new']
				status = settings.dict['DIAL'][dial]['status']
				dialTable.insert('', 'end', dial, values=(dial, old, new), tags=(dial, 'DIAL', status))

		def dialTable_edit(event):
			item = dialTable.identify('item', event.x, event.y)
			tags = dialTable.item(item, 'tags')
			settings.fid = tags[0]  # FormID
			settings.rec = tags[1]  # Record type
			settings.mode = tags[2]  # Translation status
			editor = DialEditor(settings)
			self.wait_window(editor)
		for item in dialTable.get_children(''):
			tags = dialTable.item(item, 'tags')
			dialTable.tag_bind(tags[0], '<Double-1>', dialTable_edit)


class ScenEditor(ThemedTk):

	def __init__(self, settings):
		ThemedTk.__init__(self)
		self.get_themes()
		self.set_theme(theme)
		self.configure(background=bg)
		self.option_add("*tearOff", FALSE)
		self.title("TES Parser v0.1")
		x, y, width, height = 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()
		self.geometry("%dx%d+0+0" % (width, height))
		self.state("zoomed")
		self.width, self.height = width, height

		record = settings.dict[settings.rec][settings.fid]
		formID = settings.fid

		tabs = Notebook(self)
		tabs.place(relx=0, rely=0, relwidth=1, relheight=1)

		tab1 = Frame(tabs)
		tab1.place(relx=0, rely=0, relwidth=1, relheight=1)
		tabs.add(tab1, text="Properties")
		tabs.select(tab1)

		self.typeLabel = Label(tab1, text="Type: SCEN", font=labelFont, anchor=CENTER)
		self.typeLabel.place(relx=0, y=y, relwidth=0.09, height=labelHeight)

		self.fidLabel = Label(tab1, text=f"FormID: {formID}", font=labelFont, anchor=CENTER)
		self.fidLabel.place(relx=0.1, y=y, relwidth=0.09, height=labelHeight)

		edid = ""
		if 'EDID' in record:
			edid = record['EDID']
		self.edidLabel = Label(tab1, text=f"EDID: {edid}", font=labelFont, anchor=CENTER)
		self.edidLabel.place(relx=0.2, y=y, relwidth=0.79, height=labelHeight)
		y += 35

		self.dialLabel = Label(tab1, text="Dialogs", font=("Helvetica", 16, 'bold'))
		self.dialLabel.place(x=padding, y=y, width=width / 2 - padding, height=labelHeight)
		y += labelHeight + padding

		columns = ('fid', 'old', 'new')
		dialTable = Treeview(tab1, columns=columns, show='headings')
		dialTable.heading('fid', text='Index', command=lambda: sort_column(dialTable, 'fid', False))
		dialTable.column('fid', minwidth=70, width=70, stretch=NO, anchor=CENTER)
		dialTable.heading('old', text='Original', command=lambda: sort_column(dialTable, 'old', False))
		dialTable.column('old', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.heading('new', text='Translation', command=lambda: sort_column(dialTable, 'new', False))
		dialTable.column('new', minwidth=50, width=50, stretch=YES, anchor=CENTER)
		dialTable.bind('<Double-1>', lambda e: 'break')
		dialTable.place(x=padding, y=y, width=width - padding * 2 - scrollWidth, height=3 * height / 4)
		tabScroll = Scrollbar(tab1, orient=VERTICAL, command=dialTable.yview)
		tabScroll.place(x=width - padding - scrollWidth, y=y, width=scrollWidth, height=3 * height / 4)
		dialTable.configure(yscrollcommand=tabScroll.set)
		for i in range(len(states)):
			dialTable.tag_configure(states[i], background=colors[i])

		if formID in settings.util['S>D']:
			for index in settings.util['S>D'][formID]:
				for dial in settings.util['S>D'][formID][index]:
					for info in settings.util['D>I'][dial]:
						if settings.dict['INFO'][info]['NAM1']:
							idx = list(settings.dict['INFO'][info]['NAM1'])[0]
							old = settings.dict['INFO'][info]['NAM1'][idx]['old']
							new = settings.dict['INFO'][info]['NAM1'][idx]['new']
							status = settings.dict['INFO'][info]['status']
							dialTable.insert('', 'end', info, values=(info, old, new), tags=(info, 'INFO', status))

		def dialTable_edit(event):
			item = dialTable.identify('item', event.x, event.y)
			tags = dialTable.item(item, 'tags')
			settings.fid = tags[0]  # FormID
			settings.rec = tags[1]  # Record type
			settings.mode = tags[2]  # Translation status
			editor = InfoEditor(settings)
			self.wait_window(editor)

			index = list(settings.dict['INFO'][tags[0]]['NAM1'])[0]
			old = settings.dict['INFO'][tags[0]]['NAM1'][index]['old']
			new = settings.dict['INFO'][tags[0]]['NAM1'][index]['new']
			status = settings.dict['INFO'][tags[0]]['status']
			dialTable.item(tags[0], values=(tags[0], old, new), tags=(tags[0], 'INFO', status))
		for item in dialTable.get_children(''):
			tags = dialTable.item(item, 'tags')
			dialTable.tag_bind(tags[0], '<Double-1>', dialTable_edit)

		self.botFrame = Frame(tab1)
		self.botFrame.place(relx=0.5, y=height - 160 - padding, width=width / 2 - padding, height=75)

		w = width / 8
		x = 0
		self.statLabel = Label(self.botFrame, text="Translation Status", font=labelFont, anchor=E)
		self.statLabel.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		self.var = StringVar(self)
		self.statMenu = OptionMenu(self.botFrame, self.var, settings.mode, *states)
		self.var.set(settings.mode)
		self.statMenu.place(x=x, y=15, width=max(w / 2, 150), height=40)
		x += w

		def cancel_button():
			self.destroy()
		self.cancelBtn = tk.Button(self.botFrame, text="Cancel", font=("Helvetica", 24), command=cancel_button)
		self.cancelBtn.place(x=x, y=0, width=w - padding, relheight=1)
		x += w

		def save_button():
			# Update tree items
			tags = (formID, 'SCEN', self.var.get())
			settings.tree.item(formID, tags=tags)
			update_tree(settings.tree)

			# Update table items
			values = settings.table.item(formID, 'values')
			settings.table.item(formID, values=(values[0], values[1], values[2], values[3], self.fullBlock.newText.get('1.0', END), self.var.get()), tags=tags)
			settings.dict['SCEN'][formID]['status'] = self.var.get()

			self.destroy()
		self.saveBtn = tk.Button(self.botFrame, text="Save", font=("Helvetica", 24), command=save_button)
		self.saveBtn.place(x=x, y=0, width=w - padding, relheight=1)
