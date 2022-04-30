theme = 'blue'
scrollWidth = 20
labelHeight = 25
buttonHeight = 40
padding = 10
red = '#ffaa88'
purple = '#ee99ff'
blue = '#88aaff'
yellow = '#ffff88'
colors = [
	blue,
	yellow,
	purple,
	red
]
states = [
	'Final',
	'No Tx Needed',
	'In Progress',
	'Untranslated'
]
bg = '#6699cc'
textFont = ("Bahnschrift Condensed", 16, 'bold')
labelFont = ("Courier New", 12, 'bold')

namedTypes = [
	'CLAS',
	'FACT',
	'HDPT',
	'EYES',
	'RACE',
	'MGEF',
	'ENCH',
	'SPEL',
	'SCRL',
	'ACTI',
	'TACT',
	'ARMO',
	'BOOK',
	'CONT',
	'DOOR',
	'INGR',
	'LIGH',
	'MISC',
	'TREE',
	'FLOR',
	'FURN',
	'WEAP',
	'AMMO',
	'NPC_',
	'KEYM',
	'ALCH',
	'PROJ',
	'HAZD',
	'SLGM',
	'REFR',
	'CELL',
	'WRLD',
	'DIAL',
	'QUST',
	'LSCR',
	'WATR',
	'EXPL',
	'PERK',
	'AVIF',
	'LCTN',
	'MESG',
	'WOOP',
	'SHOU',
	'SCEN'
]

namedExcl = [
	'HDPT',
	'EYES',
	'ENCH',
	'TACT',
	'CONT',
	'DOOR',
	'INGR',
	'LIGH',
	'MISC',
	'TREE',
	'FURN',
	'AMMO',
	'KEYM',
	'ALCH',
	'PROJ',
	'HAZD',
	'SLGM',
	'REFR',
	'CELL',
	'WRLD',
	'WATR',
	'EXPL',
	'LCTN',
	'WOOP'
]

descTypes = [
	'CLAS',
	'RACE',
	'MGEF',
	'SPEL',
	'SCRL',
	'ACTI',
	'ARMO',
	'FLOR',
	'WEAP',
	'NPC_',
	'LSCR',
	'PERK',
	'AVIF',
	'SHOU'
]


class Settings:
	def __init__(self):
		self.enc0 = 'utf-8'
		self.enc1 = 'utf-8'
		self.mode = 'r'
		self.write = 's'
		self.file = None
		self.target = None
		self.dict = dict()
		self.util = {
			'EDID': {},
			'KYWD': {},
			'GLOB': {},
			'VMAD': {},
			'AVIF': {},
			'D>I': {},
			'I>D': {},
			'D<I': {},
			'I<D': {},
			'Q>D': {},
			'Q>S': {},
			'S>D': {}
		}
		self.rec = ''
		self.fid = ''
		self.esp = ''
		self.srcLang = 'ru'
		self.tgtLang = 'en'
		# self.mast = dict()
		self.tree = None
		self.table = None
		self.prog = None
