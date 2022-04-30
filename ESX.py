import struct
import zlib
import os


def uint(chunk):											# Unsigned int value
	return int.from_bytes(chunk, byteorder="little", signed=False)


def uint8(chunk, index=0):
	return uint(chunk[index:index+1])


def uint16(chunk, index=0):
	return uint(chunk[index:index+2])


def uint32(chunk, index=0):
	return uint(chunk[index:index+4])


def uint64(chunk, index=0):
	return uint(chunk[index:index+8])


def _int16(strlen):											# Used to convert new string lengths back into esp format
	return strlen.to_bytes(length=2, byteorder='little', signed=False)


def _int32(strlen):											# Used to size modified Record data back into esp format
	return strlen.to_bytes(length=4, byteorder='little', signed=False)


def sint(chunk):											# Signed int value
	return int.from_bytes(chunk, byteorder="little", signed=True)


def float32(chunk, index=0):								# 32-bit float value
	return struct.unpack('<f', chunk[index:index+4])[0]		# Python returns the struct.unpack call as a tuple containing the float value and a blank entry, so we have to return [0]


def formID(chunk, index=0):
	fid = ["00", "00", "00", "00"]
	for x in range(4):
		b = hex(uint(chunk[index+x:index+x+1]))
		if len(b) == 3:
			fid[3-x] = "0" + b[2:]
		else:
			fid[3-x] = b[2:]

	string = ""
	for x in range(4):
		string += fid[x]
	return string


def strLen(chunk, index=0):								# Gets the prefixed uint16 that defines the size of the string
	return uint(chunk[index:index+2])


def zstring(chunk, index=0, enc0='utf-8', enc1='cp1252'):				# zstrings are null-terminated with a prefixed uint16 defining the length of the str (including the 0x00)
	size = strLen(chunk, index)
	if size == 1:
		return ""
	try:
		return chunk[index+2:index+1+size].decode(enc0)
	except Exception:
		try:
			return chunk[index+2:index+1+size].decode(enc1)
		except Exception:
			return f"0x{chunk[index+2:index+2+size].hex()}"


def _zstring(string, enc0='utf-8'):
	zstr = string.encode(enc0)
	size = len(zstr) + 1
	arr = bytearray()
	arr.extend(_int16(size))
	arr.extend(zstr)
	arr.append(0x00)
	return arr


# Available encodings are:
# cp1250
# cp1251
# cp1252
# cp1253
# cp1254
# cp1255
# cp1256
# utf-8


def wstring(chunk, index=0, enc0='utf-8', enc1='cp1252'):				# wstrings are not null-terminated, retaining the uint16 defining the str length
	size = strLen(chunk, index)
	if size == 0:
		return ""
	try:
		return chunk[index+2:index+2+size].decode(enc0)
	except Exception:
		try:
			return chunk[index+2:index+2+size].decode(enc1)
		except Exception:
			return f"0x{chunk[index+2:index+2+size].hex()}"


def _wstring(string, enc0='utf-8'):
	wstr = string.encode(enc0)
	size = len(wstr)
	arr = bytearray()
	arr.extend(_int16(size))
	arr.extend(wstr)
	return arr


def checkType(chunk, index=0):
	return chunk[index:index+4].decode('utf-8')


def test(chunk, test, index=0):
	try:
		return chunk[index:index+4].decode('utf-8') == test
	except Exception:
		return False


def getBytes(string):
	return bytearray(string.encode())


def find(chunk, term):
	asBytes = getBytes(term)
	return chunk.find(asBytes)


# Groups of Records should appear in the file, if present, in the following order:
# GMST		Game Setting
# KYWD		Keyword
# LCRT		Location Reference Type
# AACT		Action
# TXST		Texture Set
# GLOB		Global value
# CLAS		Class
# FACT		Faction
# HDPT		Head Part
# EYES		Eyes
# RACE		Race
# SOUN		Sound
# ASPC		Acoustic Space
# MGEF		Magic Effect
# LTEX		Land Texture
# ENCH		Enchantment
# SPEL		Spell
# SCRL		Scroll
# ACTI		Activator
# TACT		Talking Activator
# ARMO		Armor
# BOOK		Book
# NOTE		Fallout holotape object
# CONT		Container
# DOOR		Door
# INGR		Ingredient
# LIGH		Light
# MISC		Miscellaneous item
# APPA		Apparatus (only found in Oblivion/Morrowind files?)
# STAT		Static (architecture mesh)
# MSTT		Moveable Static (switch-activated walls, etc)
# GRAS		Grass
# TREE		Tree
# FLOR		Flora (harvest-able plants/animals)
# FURN		Furniture
# WEAP		Weapon
# AMMO		Ammo
# NPC_		NPC
# LVLN		Leveled NPC
# KEYM		Key
# ALCH		Alchemy (food, drink, potions)
# IDLM		Idle Marker
# COBJ		Contructible Object (recipes)
# PROJ		Projectile
# HAZD		Hazard (traps)
# SLGM		Soul Gem
# LVLI		Leveled Item
# WTHR		Weather
# CLMT		Climate
# SPGD		Shader Particle Geometry
# RFCT		Visual Effect
# REGN		Region
# NAVI		Navigation
# CELL		Cell (interior space)
#  ACHR	Actor Reference (places a copy of an NPC)
#  REFR	Object Reference (places of copy of any other place-able Record)
#  NAVM	Nav Mesh
#  PGRE	Placed Grenade (has projectile)
#  PHZD	Placed Hazard (no projecile)
# WRLD		Worldspace (exterior space)
#  LAND	Landscape
# DIAL		Dialog Topic (player dialog)
#  INFO	Dialog topics/responses
# QUST		Quest
# IDLE		Idle Animation
# PACK		AI Package
# CSTY		Combat Style
# LSCR		Load Screen
# LVSP		Leveled Spell
# ANIO		Animated Object
# WATR		Water Type
# EFSH		Effect Shader
# EXPL		Explosion
# DEBR		Debris
# IMGS		Image Space
# IMAD		Image Space Modifier
# FLST		Form List (non-leveled list)
# PERK		Perk
# BPTD		Body Part
# ADDN		Addon Node
# AVIF		Actor Values/Perk Tree Graphics
# CAMS		Camera Shot
# CPTH		Camera Path
# VTYP		Voice Type
# MATT		Material Type
# IPCT		Impact Data
# IPDS		Impact Data Set
# ARMA		Armor Addon (male/female clothing parts)
# ECZN		Encounter Zone
# LCTN		Location
# MESG		Message
# DOBJ		Default Object Manager
# LGTM		Lighting Template
# MUSC		Music Type
# FSTP		Footstep
# FSTS		Footstep Set
# SMBN		Story Manager Branch Node
# SMQN		Story Manager Quest Node
# SMEN		Story Manager Event Node
# DLBR		Dialog Branch
# MUST		Music Track
# DLVW		Dialog View
# WOOP		Word Of Power
# SHOU		Shout
# EQUP		Equip Slot
# RELA		Relationship
# SCEN		Scene
# ASTP		Association Type
# OTFT		Outfit
# ARTO		Art Object
# MATO		Material Object
# MOVT		Movement Type
# SNDR		Sound Reference
# DUAL		Dual Cast Data
# SNCT		Sound Category
# SOPM		Sound Output Model
# COLL		Collision Layer
# CLFM		Color
# REVB		Reverb Parameters


class Record:

	def __init__(self, settings, chunk):
		self.type = chunk[0:4].decode('utf-8')  # Type (DIAL, INFO, WEAP, etc)
		self.size = uint32(chunk, 4)  # Size of data, not including 24-byte header
		self.flags = uint32(chunk, 8)  # Flags - should not be changed
		self.formID = formID(chunk, 12)  # FormID
		self.version2 = uint16(chunk, 20)  # Internal version number: SE files should have the value 0x2c00, LE files 0x2b00

		if settings.mode == 'r':
			if settings.rec not in settings.dict:
				settings.dict[settings.rec] = dict()
		else:
			self.header = chunk
			if settings.write == 'r':
				settings.target.write(chunk)


class NamedRecord(Record):						# Handles Record types that have an EDID and FULL field

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		self.bytes = settings.file.read(self.size)

		self.compressed = False
		if self.flags & 0x00040000:  # Some types of Records may have the Data block compressed
			zipSize = uint32(self.bytes)  # When the occurs, the first 4 bytes specify the size of the uncompressed data
			expanded = zlib.decompress(self.bytes[4:], bufsize=zipSize)  # The remainder of the block is compressed with zlib
			self.bytes = expanded
			self.compressed = True
		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "EDID") + 4
			self.EDID = ""
			if offset > 3:
				self.EDID = zstring(chunk, offset)

			self.FULL = ""
			if settings.rec != 'SCEN':
				offset = find(chunk, "FULL") + 4
				if offset > 3:
					self.FULL = zstring(chunk, offset, settings.enc0, settings.enc1)
				settings.dict[settings.rec][self.formID] = {'EDID': self.EDID, 'FULL': {'old': self.FULL, 'gt': "", 'new': ""}, 'status': 'Untranslated'}
			else:
				settings.dict['SCEN'][self.formID] = {'EDID': self.EDID, 'status': 'Untranslated'}

			if self.EDID.strip() != "":
				settings.util['EDID'][self.EDID] = self.formID
			if settings.rec == 'QUST' or settings.rec == 'SCEN':
				return
			if settings.rec == 'MESG' or self.FULL.strip() != "":
				if settings.rec == 'REFR' and not settings.tree.exists('REFR'):
					settings.tree.insert('', 'end', 'REFR', text="REFR - CELL Object References", tags=('type', 'REFR', 'Untranslated'))
				settings.tree.insert(settings.rec, 'end', self.formID, text=f"{self.formID}{' - ' if self.EDID != '' else ''}{self.EDID}", tags=(self.formID, settings.rec, 'Untranslated'))
				if not settings.rec == 'MESG':
					settings.table.insert('', 'end', self.formID, values=(self.formID, settings.rec, self.EDID, self.FULL, "", 'Untranslated'), tags=(self.formID, settings.rec, 'Untranslated'))
		else:
			self.fullStart = -1
			self.fullEnd = -1
			offset = find(chunk, 'FULL') + 4
			if offset > 3:
				self.fullStart = offset
				self.fullEnd = offset + strLen(chunk, offset) + 2

			if settings.write == 'n':
				if self.formID not in settings.dict[self.type] or settings.rec == 'SCEN':
					outBytes = self.bytes
				else:
					record = settings.dict[self.type][self.formID]
					outBytes = bytearray()
					if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
						outBytes = self.bytes
					else:
						i = 0
						while i < len(self.bytes):
							if i == self.fullStart:
								txt = record['FULL']['new']
								outBytes.extend(_zstring(txt, settings.enc0))
								i = self.fullEnd
								continue
							outBytes.append(self.bytes[i])
							i += 1

				if self.compressed:
					zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
					zipSize = len(outBytes)
					outBytes = bytearray()
					outBytes.extend(_int32(zipSize))
					outBytes.extend(zipped)

				header = bytearray()
				header.extend(self.header[0:4])
				header.extend(_int32(len(outBytes)))
				header.extend(self.header[8:24])
				settings.target.write(header)
				settings.target.write(outBytes)


class DescRecord(NamedRecord):						# Handles Record types that have an EDID, FULL, and DESC

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			self.DESC = ""
			offset = find(chunk, "DESC") + 4
			if offset > 3:
				self.DESC = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict[settings.rec][self.formID]['DESC'] = {'old': self.DESC, 'gt': "", 'new': ""}
			if not settings.tree.exists(self.formID) and self.DESC.strip() != "":
				settings.tree.insert(settings.rec, 'end', self.formID, text=f"{self.formID}{' - ' if self.EDID != '' else ''}{self.EDID}", tags=(self.formID, settings.rec, 'Untranslated'))
			if settings.rec == 'MESG':
				settings.table.insert('', 'end', self.formID, values=(self.formID, settings.rec, self.EDID, self.DESC, "", 'Untranslated'), tags=(self.formID, settings.rec, 'Untranslated'))
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'DESC') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			if settings.write == 'd':
				if self.formID not in settings.dict[self.type]:
					outBytes = self.bytes
				else:
					record = settings.dict[self.type][self.formID]
					outBytes = bytearray()
					full = True
					desc = True
					if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
						full = False
					if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
						desc = False
					if not full and not desc:
						outBytes = self.bytes
					else:
						i = 0
						while i < len(self.bytes):
							if full and i == self.fullStart:
								txt = record['FULL']['new']
								outBytes.extend(_zstring(txt, settings.enc0))
								i = self.fullEnd
								continue
							if desc and i == self.descStart:
								txt = record['DESC']['new']
								outBytes.extend(_zstring(txt, settings.enc0))
								i = self.descEnd
								continue
							outBytes.append(self.bytes[i])
							i += 1

				if self.compressed:
					zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
					zipSize = len(outBytes)
					outBytes = bytearray()
					outBytes.extend(_int32(zipSize))
					outBytes.extend(zipped)

				header = bytearray()
				header.extend(self.header[0:4])
				header.extend(_int32(len(outBytes)))
				header.extend(self.header[8:24])
				settings.target.write(header)
				settings.target.write(outBytes)


class TES4(Record):									# File header, only Record type not found as part of a GRUP

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		if settings.mode == 'w':
			self.header = chunk
		chunk = settings.file.read(self.size)

		if settings.mode == 'r':
			offset = find(chunk, "CNAM") + 4
			self.CNAM = ""
			if offset > 3:
				self.CNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			offset = find(chunk, "SNAM") + 4
			self.SNAM = ""
			if offset > 3:
				self.SNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			self.masters = []						# Parse master files
			offset = 0
			while offset < self.size:				# There are an arbitrary number of masters, so we iterate until we run out
				index = find(chunk[offset:], "MAST") + 4
				if index > 3:
					offset += index
					self.masters.append(zstring(chunk, offset))
				else:
					break

			settings.dict['TES4'] = {self.formID: {'EDID': "Header", 'AUTH': {'old': self.CNAM, 'gt': "", 'new': ""}, 'DESC': {'old': self.SNAM, 'gt': "", 'new': ""}, 'status': 'Untranslated'}}
			settings.tree.insert('', 'end', self.formID, text='Header', tags=(self.formID, 'TES4', 'Untranslated'))
			settings.table.insert('', 'end', self.formID, values=(self.formID, 'TES4', "Header", self.CNAM, "", 'Untranslated'), tags=(self.formID, 'TES4', 'Untranslated'))
			# TODO Parse masters?
		else:
			self.authStart = -1
			self.authEnd = -1
			offset = find(chunk, 'CNAM') + 4
			if offset > 3:
				self.authStart = offset
				self.authEnd = offset + strLen(chunk, offset) + 2

			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'DESC') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['TES4']['00000000']
			outBytes = bytearray()
			auth = True
			desc = True
			if self.authStart < 0 or record['status'] == "No Tx Needed" or record['AUTH']['new'].strip() == "":
				auth = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not auth and not desc:
				outBytes = chunk
			else:
				i = 0
				while i < len(chunk):
					if auth and i == self.authStart:
						txt = record['AUTH']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.authEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(chunk[i])
					i += 1

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class KYWD(Record):							# Keyword

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = settings.file.read(self.size)

		if settings.mode == 'r':
			self.EDID = zstring(chunk, 4)

			settings.util['KYWD'][self.formID] = {'EDID': self.EDID}
		else:
			settings.target.write(chunk)


class GLOB(Record):							# Global value/variable

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = settings.file.read(self.size)

		if settings.mode == 'r':
			self.EDID = zstring(chunk, 4)
			self.value = 0.0
			offset = find(chunk, "FLTV") + 6
			if offset > 3:
				self.value = float32(chunk, offset)

			settings.util['GLOB'][self.formID] = {'EDID': self.EDID, 'value': self.value}
		else:
			settings.target.write(chunk)


class CLAS(DescRecord):						# Class

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class FACT(NamedRecord):					# Faction

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			self.ranks = dict()					# Parse rank data
			offset = 0
			while offset < self.size:			# There are an arbitrary number of ranks, so we iterate until we can't find one
				index = find(chunk[offset:], "RNAM") + 6
				if index > 5:
					offset += index
					rank = uint32(chunk, offset)
					offset += 4

					mnam = ""
					mStart = -1
					mEnd = -1
					if test(chunk, 'MNAM', offset):
						offset += 4
						mStart = offset
						mnam = zstring(chunk, offset, settings.enc0, settings.enc1)
						offset += strLen(chunk, offset) + 2
						mEnd = offset

					fnam = ""
					fStart = -1
					fEnd = -1
					if test(chunk, 'FNAM', offset):
						offset += 4
						fStart = offset
						fnam = zstring(chunk, offset, settings.enc0, settings.enc1)
						offset += strLen(chunk, offset) + 2
						fEnd = offset
					self.ranks[str(rank)] = {'MNAM': {'old': mnam, 'gt': "", 'new': "", 'start': mStart, 'end': mEnd}, 'FNAM': {'old': fnam, 'gt': "", 'new': "", 'start': fStart, 'end': fEnd}, 'status': "Untranslated"}
					if not settings.tree.exists(self.formID):
						settings.tree.insert(settings.rec, 'end', self.formID, text=f"{self.formID}{' - ' if self.EDID != '' else ''}{self.EDID}", tags=(self.formID, 'FACT', 'Untranslated'))
					if not settings.table.exists(self.formID):
						settings.table.insert('', 'end', self.formID, values=(self.formID, settings.rec, self.EDID, self.FULL, "", 'Untranslated'), tags=(self.formID, 'FACT', 'Untranslated'))
				else:
					break

			settings.dict['FACT'][self.formID]['RANK'] = self.ranks
		else:
			record = settings.dict['FACT'][self.formID]
			outBytes = bytearray()
			full = True
			ranks = False
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			for rank in record['RANK']:
				mnam = record['RANK'][rank]['MNAM']
				fnam = record['RANK'][rank]['FNAM']
				status = record['RANK'][rank]['status']
				check = True
				if (mnam['start'] < 0 and fnam['start'] < 0) or status == "No Tx Needed" or (mnam['new'].strip() == "" and fnam['new'].strip() == ""):
					check = False
				if check:
					ranks = True
			if not full and not ranks:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if ranks:
						for rank in record['RANK']:
							mnam = record['RANK'][rank]['MNAM']
							fnam = record['RANK'][rank]['FNAM']
							status = record['RANK'][rank]['status']
							if status == "In Progress" or status == "Final":
								if i == mnam['start'] and mnam['new'].strip() != "":
									outBytes.extend(_zstring(mnam['new'], settings.enc0))
									i = mnam['end']
									continue
								if i == fnam['start'] and fnam['new'].strip() != "":
									outBytes.extend(_zstring(fnam['new'], settings.enc0))
									i = fnam['end']
									continue
					if i >= len(self.bytes):
						break
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class HDPT(NamedRecord):					# Head Part

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class EYES(NamedRecord):					# Eyes

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class RACE(DescRecord):						# Race

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class MGEF(NamedRecord):					# Magic Effect

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "DNAM") + 4
			self.DNAM = ""
			if offset > 3:
				self.DNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['MGEF'][self.formID]['DESC'] = {'old': self.DNAM, 'gt': "", 'new': ""}
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'DNAM') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['MGEF'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not full and not desc:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class ENCH(NamedRecord):					# Enchantment

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class SPEL(DescRecord):						# Spell

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class SCRL(DescRecord):						# Scroll

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class ACTI(NamedRecord):					# Activator

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "RNAM") + 4
			self.RNAM = ""
			if offset > 3:
				self.RNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['ACTI'][self.formID]['DESC'] = {'old': self.RNAM, 'gt': "", 'new': ""}
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'RNAM') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['ACTI'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not full and not desc:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class TACT(NamedRecord):					# Talking Activator

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class ARMO(DescRecord):						# Armor

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class BOOK(DescRecord):						# Book/letter/etc

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "CNAM") + 4
			self.CNAM = ""
			if offset > 3:
				self.CNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['BOOK'][self.formID]['TEXT'] = {'old': self.CNAM, 'gt': "", 'new': ""}
		else:
			self.textStart = -1
			self.textEnd = -1
			offset = find(chunk, 'CNAM') + 4
			if offset > 3:
				self.textStart = offset
				self.textEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict[self.type][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			text = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if self.textStart < 0 or record['status'] == "No Tx Needed" or record['TEXT']['new'].strip() == "":
				text = False
			if not full and not desc and not text:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					if text and i == self.textStart:
						txt = record['TEXT']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.textEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class CONT(NamedRecord):					# Container

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class DOOR(NamedRecord):					# Door

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class INGR(NamedRecord):					# Ingredient

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class LIGH(NamedRecord):					# Light

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class MISC(NamedRecord):					# Miscellaneous item

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class TREE(NamedRecord):					# Tree

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class FLOR(NamedRecord):					# Flora (harvest-able plants/animals)

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "RNAM") + 4
			self.RNAM = ""
			if offset > 3:
				self.RNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['FLOR'][self.formID]['DESC'] = {'old': self.RNAM, 'gt': "", 'new': ""}
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'RNAM') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['FLOR'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not full and not desc:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class FURN(NamedRecord):					# Furniture

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class WEAP(DescRecord):						# Weapon

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class AMMO(NamedRecord):					# Ammo

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class NPC_(NamedRecord):					# NPC

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "SHRT") + 4
			self.SHRT = ""
			if offset > 3:
				self.SHRT = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['NPC_'][self.formID]['DESC'] = {'old': self.SHRT, 'gt': "", 'new': ""}
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'SHRT') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['NPC_'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not full and not desc:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class KEYM(NamedRecord):					# Key

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class ALCH(NamedRecord):					# Alchemy (food, drink, potions)

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class PROJ(NamedRecord):					# Projectile

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class HAZD(NamedRecord):					# Hazard (traps)

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class SLGM(NamedRecord):					# Soul Gem

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class REFR(NamedRecord):					# Object Reference (places of copy of any other place-able Record)

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class CELL(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = settings.file.read(24)					# At the end of each CELL record, there may be GRUP headers specifying the size of some subgroups containing all of the references in the CELL

		settings.fid = self.formID
		if find(chunk, "GRUP") == 0:
			Group(settings, chunk)


class WRLD(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class Object:

	def __init__(self, settings, chunk, offset, byteOrder, primitive):
		self.content = None
		if primitive == 1:
			if byteOrder == 1:
				fid = formID(chunk, offset)
				alias = uint16(chunk, offset+4)
				self.content = (alias, fid)
			else:
				alias = uint16(chunk, offset+2)
				fid = formID(chunk, offset+4)
				self.content = (alias, fid)
			self.size = 8
		elif primitive == 2:
			self.start = offset
			self.content = wstring(chunk, offset, settings.enc0, settings.enc1)
			self.size = strLen(chunk, offset) + 2
			self.end = offset + self.size
		elif primitive == 3:
			self.content = uint32(chunk, offset)
			self.size = 4
		elif primitive == 4:
			self.content = float32(chunk, offset)
			self.size = 4
		else:
			self.content = uint8(chunk, offset)
			self.size = 1


class Property:

	def __init__(self, settings, chunk, offset, byteOrder):
		self.name = wstring(chunk, offset, 'utf-8')
		self.size = strLen(chunk, offset) + 2

		self.primitive = uint8(chunk, offset + self.size)
		self.size += 1

		self.status = uint8(chunk, offset + self.size)
		self.size += 1

		self.objects = dict()
		if self.primitive > 5:
			objCount = uint32(chunk, offset + self.size)
			self.size += 4
			for o in range(objCount):
				obj = Object(settings, chunk, offset + self.size, byteOrder, self.primitive - 10)
				self.size += obj.size
				self.objects[str(o)] = obj
		else:
			obj = Object(settings, chunk, offset + self.size, byteOrder, self.primitive)
			self.size += obj.size
			self.objects['0'] = obj


class Script:

	def __init__(self, settings, chunk, offset, byteOrder):
		self.name = wstring(chunk, offset, 'utf-8')
		self.size = strLen(chunk, offset) + 2

		self.status = uint8(chunk, offset + self.size)
		self.size += 1

		self.propCount = uint16(chunk, offset + self.size)
		self.size += 2

		self.properties = dict()
		for p in range(self.propCount):
			prop = Property(settings, chunk, offset + self.size, byteOrder)
			self.size += prop.size
			self.properties[str(p)] = prop


class Frag:

	def __init__(self, settings, chunk, offset):
		self.size = 1		# 1 byte of ?

		self.scriptName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2

		self.fragName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2


class QuestFrag:

	def __init__(self, settings, chunk, offset):
		self.stage = uint16(chunk, offset)
		self.size = 2

		self.size += 2		# 2 bytes of 0x0000
		self.log = uint32(chunk, offset + self.size)
		self.size += 4

		self.size += 1		# 1 byte of 0x01
		self.scriptName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2

		self.fragName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2


class QuestAlias:

	def __init__(self, settings, chunk, offset, byteOrder):
		self.object = Object(settings, chunk, offset, byteOrder, 1)
		self.size = self.object.size

		self.size += 4		# 4 bytes of garbage
		self.scriptCount = uint16(chunk, offset + self.size)
		self.size += 2

		self.scripts = dict()
		for s in range(self.scriptCount):
			scpt = Script(settings, chunk, self.size, byteOrder)
			self.size += scpt.size
			self.scripts[str(s)] = scpt


class PhaseFrag:

	def __init__(self, settings, chunk, offset):
		self.size = 1		# 1 byte of ?

		self.index = uint32(chunk, offset + self.size)
		self.size += 4

		self.size += 1		# 1 byte of ?
		self.scriptName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2

		self.fragName = wstring(chunk, offset + self.size)
		self.size += strLen(chunk, offset + self.size) + 2


class VMAD:

	def __init__(self, settings, chunk, recType):
		self.version = uint16(chunk, 0)
		self.size = 2

		self.format = uint16(chunk, 2)
		self.size += 2

		self.scriptCount = uint16(chunk, 4)
		self.size += 2

		self.scripts = dict()
		for s in range(self.scriptCount):
			scpt = Script(settings, chunk, self.size, self.format)
			self.size += scpt.size
			self.scripts[str(s)] = scpt

		self.frags = dict()
		self.aliases = dict()
		self.phases = dict()

		if recType == "QUST":
			for scpt in self.scripts:
				for prop in self.scripts[scpt].properties:
					name = self.scripts[scpt].properties[prop].name
					typ = self.scripts[scpt].properties[prop].primitive
					if typ == 2 or typ == 12:
						for obj in self.scripts[scpt].properties[prop].objects:
							string = self.scripts[scpt].properties[prop].objects[obj].content
							start = self.scripts[scpt].properties[prop].objects[obj].start
							end = self.scripts[scpt].properties[prop].objects[obj].end
							if name not in settings.dict['QUST'][settings.fid]['Prop']:
								settings.dict['QUST'][settings.fid]['Prop'][name] = {}
							settings.dict['QUST'][settings.fid]['Prop'][name][obj] = {'old': string, 'gt': "", 'new': "", 'status': "Untranslated", 'start': start, 'end': end}

			self.size += 1
			self.fragCount = uint16(chunk, self.size)
			self.size += 2

			self.fileName = wstring(chunk, self.size)
			self.size += strLen(chunk, self.size) + 2

			for f in range(self.fragCount):
				frag = QuestFrag(settings, chunk, self.size)
				self.size += frag.size
				self.frags[str(f)] = frag

			self.aliasCount = uint16(chunk, self.size)

		elif recType == "INFO":
			self.size += 1

			self.flags = uint8(chunk, self.size)
			self.hasBegin = self.flags & 0x01
			self.hasEnd = min(self.flags & 0x02, 1)
			self.flagsCount = self.hasBegin + self.hasEnd
			self.size += 1

			self.fileName = wstring(chunk, self.size)
			self.size += strLen(chunk, self.size) + 2

			for f in range(self.flagsCount):
				frag = Frag(settings, chunk, self.size)
				self.size += frag.size
				self.frags[str(f)] = frag
		elif recType == "SCEN":
			self.size += 1

			self.flags = uint8(chunk, self.size)
			self.hasBegin = self.flags & 0x01
			self.hasEnd = min(self.flags & 0x02, 1)
			self.flagsCount = self.hasBegin + self.hasEnd
			self.size += 1

			self.fileName = wstring(chunk, self.size)
			self.size += strLen(chunk, self.size) + 2

			for f in range(self.flagsCount):
				frag = Frag(settings, chunk, self.size)
				self.size += frag.size
				self.frags[str(f)] = frag

			self.phaseCount = uint16(chunk, self.size)
			self.size += 2

			for p in range(self.phaseCount):
				phase = PhaseFrag(settings, chunk, self.size)
				self.size += phase.size
				self.phases[str(phase.index)] = phase


class INFO(Record):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = settings.file.read(self.size)

		if settings.mode == 'r':
			offset = find(chunk, "EDID") + 4
			self.EDID = ""
			if offset > 3:
				self.EDID = zstring(chunk, offset)							# Editor ID (optional)

			self.VMAD = None
			offset = find(chunk, "VMAD") + 4
			if offset > 3:
				vmadSize = uint16(chunk, offset)
				self.VMAD = VMAD(settings, chunk[offset + 2:offset + 2 + vmadSize], "INFO")

			self.TCLT = dict()
			index = find(chunk[offset:], "TCLT") + 6
			dCount = 0
			while index > 5:
				offset += index
				fid = formID(chunk, offset)
				self.TCLT[str(dCount)] = fid
				index = find(chunk[offset:], "TCLT") + 6

			self.NAM1 = dict()
			index = find(chunk[offset:], "TRDT") + 6
			while index > 5:
				offset += index
				offset += 12
				infoNum = uint8(chunk, offset)
				offset += 16
				start = offset
				infoStr = zstring(chunk, offset, settings.enc0, settings.enc1)
				end = offset + strLen(chunk, offset) + 2
				self.NAM1[str(infoNum)] = {'old': infoStr, 'gt': "", 'new': "", 'status': "Untranslated", 'start': start, 'end': end}
				index = find(chunk[offset:], "TRDT") + 6

			offset = find(chunk, "RNAM") + 4
			self.RNAM = ""
			rStart = -1
			rEnd = -1
			if offset > 3:
				rStart = offset
				self.RNAM = zstring(chunk, offset, settings.enc0, settings.enc1)
				rEnd = offset + strLen(chunk, offset) + 2

			if self.formID not in settings.util['I>D']:
				settings.util['I>D'][self.formID] = []
			for i in self.TCLT:
				settings.util['I>D'][self.formID].append(self.TCLT[i])				# Add DIAL responses to list of DIAL records referenced by this INFO (by INFO ID)
				if i not in settings.util['D<I']:
					settings.util['D<I'][i] = []
				settings.util['D<I'][i].append(self.formID)							# Add formID to list of DIAL records referenced by this INFO (by DIAL ID)

			if self.formID not in settings.util['I<D']:
				settings.util['I<D'][self.formID] = []
			settings.util['I<D'][self.formID].append(settings.fid)					# Add referencing DIAL ID to list of DIAL records referencing this INFO (by INFO ID)

			if settings.fid not in settings.util['D>I']:
				settings.util['D>I'][settings.fid] = []
			settings.util['D>I'][settings.fid].append(self.formID)					# Add formID to list of INFO records referenced by referencing DIAL (by DIAL ID)

			settings.dict['INFO'][self.formID] = {'EDID': self.EDID, 'NAM1': self.NAM1, 'RNAM': {'old': self.RNAM, 'gt': "", 'new': "", 'start': rStart, 'end': rEnd}, 'status': 'Untranslated'}
			if settings.tree.exists(settings.fid):
				text = f"{self.formID}{' - ' if self.EDID.strip() != '' else ''}{self.EDID}"
				settings.tree.insert(settings.fid, 'end', self.formID, text=text, tags=(self.formID, 'INFO', "Untranslated"))
			# TODO Conditions, Scripts
		else:
			record = settings.dict['INFO'][self.formID]
			outBytes = bytearray()
			rnam = True
			nams = False
			if record['RNAM']['start'] < 0 or record['status'] == "No Tx Needed" or record['RNAM']['new'].strip() == "":
				rnam = False
			for num in record['NAM1']:
				nam = record['NAM1'][num]
				cnd = True
				if nam['start'] < 0 or nam['status'] == "No Tx Needed" or nam['new'].strip() == "":
					cnd = False
				if cnd:
					nams = True
			if not rnam and not nams:
				outBytes = chunk
			else:
				i = 0
				while i < len(chunk):
					if rnam and i == record['RNAM']['start']:
						txt = record['RNAM']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = record['RNAM']['end']
						continue
					if nams:
						for num in record['NAM1']:
							nam = record['NAM1'][num]
							if nam['status'] == "In Progress" or nam['status'] == "Final":
								if i == nam['start'] and nam['new'].strip() != "":
									outBytes.extend(_zstring(nam['new'], settings.enc0))
									i = nam['end']
									continue
					if i >= len(chunk):
						break
					outBytes.append(chunk[i])
					i += 1

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class DIAL(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		offset = find(chunk, "QNAM") + 6
		self.QNAM = ""
		if offset > 5:
			self.QNAM = formID(chunk, offset)

		if settings.mode == 'r':
			if self.QNAM not in settings.util['Q>D']:
				settings.util['Q>D'][self.QNAM] = []
			settings.util['Q>D'][self.QNAM].append(self.formID)

		offset = find(chunk, "TIFC") + 6
		self.TIFC = ""
		if offset > 5:
			self.TIFC = uint32(chunk, offset)
			if self.TIFC > 0:
				settings.fid = self.formID
				chunk = settings.file.read(24)
				Group(settings, chunk)


class QuestLog:

	def __init__(self, settings, chunk, offset):
		self.size = offset
		offset += 4
		offset += 2

		self.flags = uint8(chunk, offset)
		offset += 1

		while test(chunk, 'CTDA', offset):
			offset += 4
			cndSize = uint16(chunk, offset)
			offset += cndSize
			#TODO Conditions

		self.log = None
		if test(chunk, 'CNAM', offset):
			offset += 4
			self.start = offset
			self.log = zstring(chunk, offset, settings.enc0, settings.enc1)
			offset += strLen(chunk, offset) + 2
			self.end = offset

		self.size = offset - self.size


class QuestStage:

	def __init__(self, settings, chunk, offset):
		offset += 4

		self.size = uint16(chunk, offset)
		offset += 2

		self.index = uint16(chunk, offset)
		offset += 2

		offset += 1
		offset += 1

		self.logCount = 0
		self.logs = {}
		while not test(chunk, 'ANAM', offset) and not test(chunk, 'INDX', offset) and not test(chunk, 'QOBJ', offset):
			if test(chunk, 'QSDT', offset):
				log = QuestLog(settings, chunk, offset)
				if log.log:
					self.logs[str(self.logCount)] = {'old': log.log, 'gt': "", 'new': "", 'status': "Untranslated", 'start': log.start, 'end': log.end}
					self.logCount += 1
					offset += log.size
			offset += 1


class QuestObj:

	def __init__(self, settings, chunk, offset):
		offset += 4
		offset += 2

		self.index = uint16(chunk, offset)
		offset += 2

		offset += 4
		offset += 2
		self.flags = uint32(chunk, offset)
		offset += 4

		offset += 4
		self.start = offset
		self.obj = zstring(chunk, offset, settings.enc0, settings.enc1)
		self.end = offset + strLen(chunk, offset) + 2


class QUST(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			settings.dict['QUST'][self.formID]['Prop'] = {}
			settings.dict['QUST'][self.formID]['Stage'] = {}
			settings.dict['QUST'][self.formID]['Obj'] = {}
			settings.fid = self.formID

			self.VMAD = None
			offset = find(chunk, "VMAD") + 4
			if offset > 3:
				vmadSize = uint16(chunk, offset)
				self.VMAD = VMAD(settings, chunk[offset+2:offset+2+vmadSize], "QUST")

			add = False
			while offset < len(chunk):
				offset += 1
				if test(chunk, 'INDX', offset):
					stage = QuestStage(settings, chunk, offset)
					if stage.logCount > 0:
						settings.dict['QUST'][self.formID]['Stage'][str(stage.index)] = stage.logs
						add = True
				if test(chunk, 'QOBJ', offset):
					obj = QuestObj(settings, chunk, offset)
					settings.dict['QUST'][self.formID]['Obj'][str(obj.index)] = {'old': obj.obj, 'gt': "", 'new': "", 'status': "Untranslated", 'start': obj.start, 'end': obj.end}
					add = True
			if self.FULL.strip() != "":
				add = True
			if settings.dict['QUST'][self.formID]['Prop']:
				add = True
			if add:
				settings.tree.insert(settings.rec, 'end', self.formID, text=f"{self.formID} - {self.EDID}", tags=(self.formID, settings.rec, 'Untranslated'))
				settings.table.insert('', 'end', self.formID, values=(self.formID, settings.rec, self.EDID, self.FULL, "", 'Untranslated'), tags=(self.formID, settings.rec, 'Untranslated'))
		else:
			vStart = -1
			offset = find(chunk, "VMAD") + 4
			if offset > 5:
				vStart = offset						# We have to track the byte position after the VMAD chars so that we can update the VMAD size later
				offset += 2							# We need an offset that is after the two bytes that store the VMAD size to correct the placement of our property wstrings
			vEnd = find(chunk, 'FULL')
			if vEnd < 0:
				vEnd = find(chunk, 'DNAM')

			record = settings.dict['QUST'][self.formID]
			outBytes = bytearray()
			full = True
			props = False
			stages = False
			objs = False
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			for name in record['Prop']:
				for num in record['Prop'][name]:
					prop = record['Prop'][name][num]
					cnd = True
					if prop['start'] < 0 or prop['status'] == "No Tx Needed" or prop['new'].strip() == "":
						cnd = False
					if cnd:
						props = True
			for stg in record['Stage']:
				for num in record['Stage'][stg]:
					stage = record['Stage'][stg][num]
					cnd = True
					if stage['start'] < 0 or stage['status'] == "No Tx Needed" or stage['new'].strip() == "":
						cnd = False
					if cnd:
						stages = True
			for num in record['Obj']:
				obj = record['Obj'][num]
				cnd = True
				if obj['start'] < 0 or obj['status'] == "No Tx Needed" or obj['new'].strip() == "":
					cnd = False
				if cnd:
					objs = True

			if not full and not props and not stages and not objs:
				outBytes = self.bytes
			else:
				i = 0
				vPos = 0
				while i < len(self.bytes):
					if i == vStart:
						vPos = len(outBytes)						# In order to correctly modify the VMAD size, we have to capture the position of the first size byte in the output array
					if i == vEnd:
						pos = len(outBytes)							# Once we reach the end of the VMAD data in the source file, we again store the current output array size
						vSize = pos - vPos							# The difference of the two position samplings tells us the new VMAD size
						outBytes[vPos:vPos+2] = _int16(vSize - 2)   # Over-write the size bytes with the new size
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if props:
						for name in record['Prop']:
							for num in record['Prop'][name]:
								prop = record['Prop'][name][num]
								if prop['status'] == "In Progress" or prop['status'] == "Final":
									if i == prop['start'] + offset and prop['new'].strip() != "":		# Due to how the VMAD data is parsed, we have to offset the property start position like this
										outBytes.extend(_wstring(prop['new'], settings.enc0))			# Script string properties are wstrings, not zstrings like everything else
										i = prop['end'] + offset										# Have to offset the property end position for the same reason
										continue
					if stages:
						for stg in record['Stage']:
							for num in record['Stage'][stg]:
								stage = record['Stage'][stg][num]
								if stage['status'] == "In Progress" or stage['status'] == "Final":
									if i == stage['start'] and stage['new'].strip() != "":
										outBytes.extend(_zstring(stage['new'], settings.enc0))
										i = stage['end']
										continue
					if objs:
						for num in record['Obj']:
							obj = record['Obj'][num]
							if obj['status'] == "In Progress" or obj['status'] == "Final":
								if i == obj['start'] and obj['new'].strip() != "":
									outBytes.extend(_zstring(obj['new'], settings.enc0))
									i = obj['end']
									continue
					if i >= len(self.bytes):
						break
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class LSCR(DescRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class WATR(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class EXPL(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class PERK(DescRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class AVIF(DescRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class LCTN(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class MESG(DescRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			self.options = dict()
			opCount = 0
			offset = 0
			while offset < self.size:  # There are an arbitrary number of options, so we iterate until we run out
				index = find(chunk[offset:], "ITXT") + 4
				if index > 3:
					oStart = offset + index
					option = zstring(chunk[offset:], index, settings.enc0, settings.enc1)
					oEnd = offset + index + strLen(chunk[offset:], index) + 2
					offset += index
					self.options[str(opCount)] = {'old': option, 'gt': "", 'new': "", 'status': "Untranslated", 'start': oStart, 'end': oEnd}
					opCount += 1
				else:
					break

			settings.dict['MESG'][self.formID]['ITXT'] = self.options
		else:
			record = settings.dict['MESG'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			opts = False
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			for idx in record['ITXT']:
				itxt = record['ITXT'][idx]
				if type(itxt) is dict:
					break
				opt = True
				if itxt['start'] < 0 or itxt['status'] == "No Tx Needed" or itxt['new'].strip() == "":
					opt = False
				if opt:
					opts = True
			if not full and not desc and not opts:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					if opts:
						for idx in record['ITXT']:
							itxt = record['ITXT'][idx]
							if itxt['status'] == "In Progress" or itxt['status'] == "Final":
								if i == itxt['start'] and itxt['new'].strip() != "":
									outBytes.extend(_zstring(itxt['new'], settings.enc0))
									i = itxt['end']
									continue
					if i >= len(self.bytes):
						break
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class WOOP(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			offset = find(chunk, "TNAM") + 4
			self.TNAM = ""
			if offset > 3:
				self.TNAM = zstring(chunk, offset, settings.enc0, settings.enc1)

			settings.dict['WOOP'][self.formID]['DESC'] = {'old': self.TNAM, 'gt': "", 'new': ""}
		else:
			self.descStart = -1
			self.descEnd = -1
			offset = find(chunk, 'TNAM') + 4
			if offset > 3:
				self.descStart = offset
				self.descEnd = offset + strLen(chunk, offset) + 2

			record = settings.dict['WOOP'][self.formID]
			outBytes = bytearray()
			full = True
			desc = True
			if self.fullStart < 0 or record['status'] == "No Tx Needed" or record['FULL']['new'].strip() == "":
				full = False
			if self.descStart < 0 or record['status'] == "No Tx Needed" or record['DESC']['new'].strip() == "":
				desc = False
			if not full and not desc:
				outBytes = self.bytes
			else:
				i = 0
				while i < len(self.bytes):
					if full and i == self.fullStart:
						txt = record['FULL']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.fullEnd
						continue
					if desc and i == self.descStart:
						txt = record['DESC']['new']
						outBytes.extend(_zstring(txt, settings.enc0))
						i = self.descEnd
						continue
					outBytes.append(self.bytes[i])
					i += 1

			if self.compressed:
				zipped = zlib.compress(outBytes, level=zlib.Z_BEST_COMPRESSION)
				zipSize = len(outBytes)
				outBytes = bytearray()
				outBytes.extend(_int32(zipSize))
				outBytes.extend(zipped)

			header = bytearray()
			header.extend(self.header[0:4])
			header.extend(_int32(len(outBytes)))
			header.extend(self.header[8:24])
			settings.target.write(header)
			settings.target.write(outBytes)


class SHOU(DescRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)


class Phase:

	def __init__(self, settings, chunk, offset):
		self.size = offset
		offset += 10
		self.desc = zstring(chunk, offset, settings.enc0, settings.enc1)
		offset += strLen(chunk, offset) + 2

		self.startCond = None
		if checkType(chunk, offset) == "CTDA":
			self.startCond = None		# CTDA(chunk, offset)
		offset += find(chunk[offset:], "NEXT") + 6
		self.endCond = None
		if checkType(chunk, offset) == "CTDA":
			self.endCond = None		# CTDA(chunk, offset)

		offset += find(chunk[offset:], "HNAM") + 6
		self.size = offset - self.size
		# TODO Conditions


class Actor:

	def __init__(self, settings, chunk, offset):
		self.size = offset
		offset += 6
		self.alias = uint32(chunk, offset)
		offset += 4

		if checkType(chunk, offset) == "LNAM":
			offset += 6
			self.flags = uint32(chunk, offset)
			offset += 4

		if checkType(chunk, offset) == "DNAM":
			offset += 6
			self.behaviors = uint32(chunk, offset)
			offset += 4
			# 0x01	Death Pause
			# 0x02	Death End
			# 0x04	Combat Pause
			# 0x08	Combat End
			# 0x16	Dialogue Pause
			# 0x32	Dialogue End
			# 0x64	OBS_COM Pause
			# 0x128	OBS_COM End

		self.size = offset - self.size


class Action:

	def __init__(self, settings, chunk, offset):
		self.size = offset
		offset += 6
		self.type = uint16(chunk, offset)
		offset += 2
		# 0 = Dialog
		# 1 = Package
		# 2 = Timer

		offset += 4
		self.desc = zstring(chunk, offset, settings.enc0, settings.enc1)
		offset += strLen(chunk, offset) + 2

		offset += 6
		self.actorIdx = uint32(chunk, offset)
		offset += 4

		offset += 6
		self.index = uint32(chunk, offset)
		offset += 4

		if checkType(chunk, offset) == "FNAM":
			offset += 6
			self.flags = uint32(chunk, offset)
			offset += 4

		offset += 6
		self.startP = uint32(chunk, offset)
		offset += 4

		offset += 6
		self.endP = uint32(chunk, offset)
		offset += 4

		self.dial = None
		self.pack = None
		self.time = None
		if checkType(chunk, offset) == "DATA":
			offset += 6
			self.dial = formID(chunk, offset)
			if self.dial in settings.dict['DIAL'] and self.dial in settings.util['D>I']:
				if settings.fid not in settings.util['S>D']:
					settings.util['S>D'][settings.fid] = {str(self.index): []}
				if str(self.index) not in settings.util['S>D'][settings.fid]:
					settings.util['S>D'][settings.fid][str(self.index)] = []
				settings.util['S>D'][settings.fid][str(self.index)].append(self.dial)

				infoCount = 0
				for info in settings.util['D>I'][self.dial]:
					settings.tree.insert(settings.fid, 'end', info, text=info, tags=(info, 'INFO', "Untranslated"))
					infoCount += 1
			offset += 4
		if checkType(chunk, offset) == "PNAM":
			offset += 6
			self.pack = formID(chunk, offset)
			offset += 4
		if checkType(chunk, offset) == "SNAM":
			offset += 6
			self.time = float32(chunk, offset)
			offset += 4

		offset += find(chunk[offset:], "ANAM") + 6
		self.size = offset - self.size


class SCEN(NamedRecord):

	def __init__(self, settings, chunk):
		super().__init__(settings, chunk)

		chunk = self.bytes

		if settings.mode == 'r':
			if self.formID not in settings.dict['SCEN']:
				settings.dict['SCEN'][self.formID] = {'EDID': self.EDID, 'status': 'Untranslated'}
			settings.fid = self.formID

			settings.tree.insert('SCEN', 'end', self.formID, text=f"{self.formID} - {self.EDID}", tags=(self.formID, settings.rec, 'Untranslated'))
			settings.table.insert('', 'end', self.formID, values=(self.formID, 'SCEN', self.EDID, "", "", 'Untranslated'), tags=(self.formID, 'SCEN', 'Untranslated'))

			self.VMAD = None
			offset = find(chunk, "VMAD") + 4
			if offset > 3:
				vmadSize = uint16(chunk, offset)
				self.VMAD = VMAD(settings, chunk[offset + 2:offset + 2 + vmadSize], "SCEN")

			offset = find(chunk, "FNAM") + 6
			self.flags = uint32(chunk, offset)
			offset += 4

			self.phases = dict()
			pCount = 0
			self.actors = dict()
			cCount = 0
			self.actions = dict()
			aCount = 0
			while checkType(chunk, offset) != "PNAM":
				if checkType(chunk, offset) == "HNAM":
					phase = Phase(settings, chunk, offset)
					self.phases[str(pCount)] = phase
					pCount += 1
					offset += phase.size
				if checkType(chunk, offset) == "ALID":
					actor = Actor(settings, chunk, offset)
					self.actors[str(cCount)] = actor
					cCount += 1
					offset += actor.size
				if checkType(chunk, offset) == "ANAM":
					settings.fid = self.formID
					action = Action(settings, chunk, offset)
					self.actions[str(aCount)] = action
					aCount += 1
					offset += action.size

			offset = find(chunk, "PNAM") + 6
			self.QUST = formID(chunk, offset)
			offset += 4

			offset += 6
			self.maxAction = uint32(chunk, offset)
			offset += 4

			'''offset += 6
			offset += 4
			offset += 4
			offset += 4
			offset += 4

			self.condition = None
			if len(chunk) > offset:
				if checkType(chunk, offset) == "CTDA":
					self.condition = None		# CTDA(chunk, offset)'''
					# TODO Conditions
			if self.QUST not in settings.util['Q>S']:
				settings.util['Q>S'][self.QUST] = {'SCEN': []}
			settings.util['Q>S'][self.QUST]['SCEN'].append(self.formID)


types = {
	'CLAS': 'Classes',
	'FACT': 'Factions',
	'HDPT': 'Head Parts',
	'EYES': 'Eyes',
	'RACE': 'Races',
	'MGEF': 'Magic Effects',
	'ENCH': 'Enchantments',
	'SPEL': 'Spells',
	'SCRL': 'Scrolls',
	'ACTI': 'Activators',
	'TACT': 'Talking Activators',
	'ARMO': 'Armor',
	'BOOK': 'Books and Notes',
	'CONT': 'Containers',
	'DOOR': 'Doors',
	'INGR': 'Ingredients',
	'LIGH': 'Lights',
	'MISC': 'Misc Objects',
	'TREE': 'Trees',
	'FLOR': 'Harvestable Flora',
	'FURN': 'Furniture',
	'WEAP': 'Weapons',
	'AMMO': 'Ammo',
	'NPC_': 'NPCs',
	'KEYM': 'Keys',
	'ALCH': 'Potions',
	'PROJ': 'Projectiles',
	'HAZD': 'Hazards',
	'SLGM': 'Soulgems',
	'CELL': 'Interior Cells',
	'REFR': 'Cell Object References',
	'WRLD': 'Worldspaces',
	'DIAL': 'Player Dialog',
	'QUST': 'Quests',
	'LSCR': 'Loading Screens',
	'WATR': 'Water',
	'EXPL': 'Explosions',
	'PERK': 'Perks',
	'AVIF': 'Actor Values',
	'LCTN': 'Locations',
	'MESG': 'Messages',
	'WOOP': 'Words of Power',
	'SHOU': 'Shouts',
	'SCEN': 'Scenes'
}


class Group:

	def __init__(self, settings, chunk):
		if settings.mode == "w":
			self.startPos = settings.target.tell()
			settings.target.write(chunk)
		self.grup = checkType(chunk, 0)			# Should always be "GRUP"
		self.size = uint32(chunk, 4)		# Size of the whole group, including 24 bytes of header
		self.lastByte = settings.file.tell() + self.size - 24
		# The current file pointer is after this header, so we take the pointer value - 24 bytes + the GRUP size and that will be the final byte of the GRUP block
		self.type = uint32(chunk, 12)
		if self.type == 0:
			self.label = checkType(chunk, 8)

			settings.prog.set_text(f"Parsing {self.label} Records...")
			settings.rec = self.label
			if not settings.tree.exists(self.label) and self.label in types:
				settings.tree.insert('', 'end', self.label, text=f"{self.label} - {types[self.label]}", tags=('type',  self.label, 'Untranslated'))
		elif self.type == 1:
			self.label = "WRLD Children"
		elif self.type == 2:
			self.label = "Int CELL Block"
		elif self.type == 3:
			self.label = "Int CELL Sub-Block"
		elif self.type == 4:
			self.label = "Ext CELL Block"
		elif self.type == 5:
			self.label = "Ext CELL Sub-Block"
		elif self.type == 6:
			self.label = "CELL Children"
		elif self.type == 7:
			self.label = "Topic Children"
		elif self.type == 8:
			self.label = "CELL Pers Children"
		elif self.type == 9:
			self.label = "CELL Temp Children"
		else:
			self.label = "ERROR"

		self.recList = []
		while settings.file.tell() < self.lastByte:
			chunk = settings.file.read(24)
			settings.prog.set(settings.file.tell())
			if test(chunk, 'GRUP'):
				Group(settings, chunk)
				continue
			if self.label == "KYWD":
				settings.write = 'r'
				rec = KYWD(settings, chunk)
			elif self.label == "GLOB":
				settings.write = 'r'
				rec = GLOB(settings, chunk)
			elif self.label == "CLAS":
				settings.write = 'd'
				rec = CLAS(settings, chunk)
			elif self.label == "FACT":
				settings.write = 's'
				rec = FACT(settings, chunk)
			elif self.label == "HDPT":
				settings.write = 'n'
				rec = HDPT(settings, chunk)
			elif self.label == "EYES":
				settings.write = 'n'
				rec = EYES(settings, chunk)
			elif self.label == "RACE":
				settings.write = 'd'
				rec = RACE(settings, chunk)
			elif self.label == "MGEF":
				settings.write = 's'
				rec = MGEF(settings, chunk)
			elif self.label == "ENCH":
				settings.write = 'n'
				rec = ENCH(settings, chunk)
			elif self.label == "SPEL":
				settings.write = 'd'
				rec = SPEL(settings, chunk)
			elif self.label == "SCRL":
				settings.write = 'd'
				rec = SCRL(settings, chunk)
			elif self.label == "ACTI":
				settings.write = 's'
				rec = ACTI(settings, chunk)
			elif self.label == "TACT":
				settings.write = 'n'
				rec = TACT(settings, chunk)
			elif self.label == "ARMO":
				settings.write = 'd'
				rec = ARMO(settings, chunk)
			elif self.label == "BOOK":
				settings.write = 's'
				rec = BOOK(settings, chunk)
			elif self.label == "CONT":
				settings.write = 'n'
				rec = CONT(settings, chunk)
			elif self.label == "DOOR":
				settings.write = 'n'
				rec = DOOR(settings, chunk)
			elif self.label == "INGR":
				settings.write = 'n'
				rec = INGR(settings, chunk)
			elif self.label == "LIGH":
				settings.write = 'n'
				rec = LIGH(settings, chunk)
			elif self.label == "MISC":
				settings.write = 'n'
				rec = MISC(settings, chunk)
			elif self.label == "TREE":
				settings.write = 'n'
				rec = TREE(settings, chunk)
			elif self.label == "FLOR":
				settings.write = 's'
				rec = FLOR(settings, chunk)
			elif self.label == "FURN":
				settings.write = 'n'
				rec = FURN(settings, chunk)
			elif self.label == "WEAP":
				settings.write = 'd'
				rec = WEAP(settings, chunk)
			elif self.label == "AMMO":
				settings.write = 'n'
				rec = AMMO(settings, chunk)
			elif self.label == "NPC_":
				settings.write = 's'
				rec = NPC_(settings, chunk)
			elif self.label == "KEYM":
				settings.write = 'n'
				rec = KEYM(settings, chunk)
			elif self.label == "ALCH":
				settings.write = 'n'
				rec = ALCH(settings, chunk)
			elif self.label == "PROJ":
				settings.write = 'n'
				rec = PROJ(settings, chunk)
			elif self.label == "HAZD":
				settings.write = 'n'
				rec = HAZD(settings, chunk)
			elif self.label == "SLGM":
				settings.write = 'n'
				rec = SLGM(settings, chunk)
			elif 'CELL' in self.label and 'Block' in self.label and checkType(chunk) == 'CELL':			# The actual CELL records are only found within the Sub-block groups
				settings.rec = 'CELL'
				settings.write = 'n'
				rec = CELL(settings, chunk)
			elif 'CELL' in self.label and 'Children' in self.label and checkType(chunk) == 'REFR':
				settings.rec = 'REFR'
				settings.write = 'n'
				rec = REFR(settings, chunk)
			elif "WRLD" in self.label:
				settings.rec = 'WRLD'
				settings.write = 'n'
				rec = WRLD(settings, chunk)
			elif self.label == "DIAL":
				settings.rec = 'DIAL'
				settings.write = 'n'
				rec = DIAL(settings, chunk)
			elif self.label == "INFO" or 'Topic' in self.label:
				settings.rec = 'INFO'
				settings.write = 's'
				rec = INFO(settings, chunk)
			elif self.label == "QUST":
				settings.write = 's'
				rec = QUST(settings, chunk)
			elif self.label == "LSCR":
				settings.write = 'd'
				rec = LSCR(settings, chunk)
			elif self.label == "WATR":
				settings.write = 'n'
				rec = WATR(settings, chunk)
			elif self.label == "EXPL":
				settings.write = 'n'
				rec = EXPL(settings, chunk)
			elif self.label == "PERK":
				settings.write = 'd'
				rec = PERK(settings, chunk)
			elif self.label == "AVIF":
				settings.write = 'd'
				rec = AVIF(settings, chunk)
			elif self.label == "LCTN":
				settings.write = 'n'
				rec = LCTN(settings, chunk)
			elif self.label == "MESG":
				settings.write = 's'
				rec = MESG(settings, chunk)
			elif self.label == "WOOP":
				settings.write = 's'
				rec = WOOP(settings, chunk)
			elif self.label == "SHOU":
				settings.write = 'd'
				rec = SHOU(settings, chunk)
			elif self.label == "SCEN":
				settings.write = 'n'
				rec = SCEN(settings, chunk)
			else:
				settings.write = 'r'
				rec = Record(settings, chunk)
				dat = settings.file.read(rec.size)
				if settings.mode == 'w':
					settings.target.write(dat)
			if rec:
				self.recList.append(rec)

		if settings.mode == "w":
			self.endPos = settings.target.tell()
			size = self.endPos - self.startPos
			settings.target.seek(self.startPos + 4, os.SEEK_SET)
			settings.target.write(_int32(size))
			settings.target.seek(0, os.SEEK_END)
