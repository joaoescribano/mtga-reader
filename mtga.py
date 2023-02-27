import glob
import os
import io
import sqlite3
import UnityPy
import cv2
import numpy as np

class mtga_reader:
	mtga_root_dir = None
	mtga_data_dir = None
	mtga_assets_dir = None
	mtga_raw_dir = None
	lang = None
	connections = {}
	enums = {}

	def __init__(self, mtga_root_dir, lang='enUS'):
		self.lang = lang
		self.mtga_root_dir = mtga_root_dir
		self.mtga_data_dir = f'{self.mtga_root_dir}MTGA_Data/'
		self.mtga_assets_dir = f'{self.mtga_data_dir}Downloads/AssetBundle/'
		self.mtga_raw_dir = f'{self.mtga_data_dir}Downloads/Raw/'
		self.get_databases()
		self.get_enums()

	def dict_factory(self, cursor, row):
	    d = {}
	    for idx, col in enumerate(cursor.description):
	        d[col[0]] = row[idx]
	    return d

	def get_databases(self):
		try:
			dbs = ['ArtCropDatabase','CardDatabase','ClientLocalization','altArtCredits','altFlavorTexts','altPrintings','credits','metadatatags']
			for db in dbs:
				self.connections[db] = sqlite3.connect(max(glob.glob(f"{self.mtga_raw_dir}Raw_{db}_*.mtga"), key=os.path.getctime))
				self.connections[db].row_factory = self.dict_factory
			return True
		except:
			self.connections = {}
			return False

	def close(self):
		for db in self.connections:
			self.connections[db].close()
		return True

	def get_enums(self):
		cursor = self.connections['CardDatabase'].cursor()
		cursor.execute('Select "Type" FROM Enums GROUP BY "Type"')

		for linha in cursor.fetchall():
			self.enums[linha['Type']] = {}

		for enum_type in self.enums:
			cursor.execute(f'Select Value, LocId  FROM Enums WHERE "Type" = "{enum_type}"')
			for linha in cursor.fetchall():
				self.enums[enum_type][linha['Value']] = self.get_card_translation_id(linha['LocId'])

		print(self.enums)

	def get_card_translation_id(self, text_id):
		try:
			cursor = self.connections['CardDatabase'].cursor()
			cursor.execute(f'select {self.lang} from Localizations WHERE LocId = {text_id}')
			ret = []
			for linha in cursor.fetchall():
				ret.append(linha)
			return ret[0][self.lang] if ret else None
		except:
			return text_id

	def get_card_abilities(self, ability_id):
		try:
			cursor = self.connections['CardDatabase'].cursor()
			cursor.execute(f'select * from Abilities WHERE Id = {ability_id}')
			ret = []
			for linha in cursor.fetchall():
				linha['TextId'] = self.get_card_translation_id(linha['TextId'])

				ret.append(linha)
			return ret[0] if ret else None
		except:
			return ability_id

	def get_card_by_id(self, card_id, get_art=True):
		card = None
		cursor = self.connections['CardDatabase'].cursor()
		cursor.execute(f'SELECT * FROM Cards WHERE GrpId = {card_id} LIMIT 1')
		ret = []
		for linha in cursor.fetchall():
			tmp = {}
			for key,val in linha.items():
				if 'TextId' in key or 'TitleId' in key:
					tmp[key.replace("Id", "").lower()] = val if val == None else self.get_card_translation_id(val)
				elif 'AbilityIds' in key:
					tmp[key.replace("Id", "").lower()] = val if val == None else self.get_card_abilities(val)
				elif 'ArtId' in key:
					tmp['art'] = val if (val == None or not get_art) else self.get_card_art_by_id(val)
				else:
					tmp[key] = val
			ret.append(tmp)
		return ret[0] if ret else None

	def get_card_by_name(self, card_name, limit=None, get_art=True):
		card = None
		cursor = self.connections['CardDatabase'].cursor()
		cursor.execute(f'SELECT GrpId FROM Cards WHERE TitleId = (select LocId from Localizations WHERE {self.lang} like "{card_name}")' + (f' LIMIT {limit}' if limit else ''))
		ret = []
		for linha in cursor.fetchall():
			ret.append(self.get_card_by_id(linha['GrpId'], get_art))
		return ret

	def find_card_art_file(self, card_id):
		ret = {
			'image': None,
			'util': None
		}

		for file_name in glob.glob(f"{self.mtga_assets_dir}{str(card_id).zfill(6)}*.mtga"):
			env = UnityPy.load(file_name)

			for path,obj in env.container.items():
				# Checa por sprites e texturas2D
				if obj.type.name in ["Texture2D", "Sprite"]:
					data = obj.read()
					img_byte_arr = io.BytesIO()
					data.image.save(img_byte_arr, format='PNG')

					image = np.asarray(bytearray(img_byte_arr.getvalue()), dtype="uint8")
					image = cv2.imdecode(image, cv2.IMREAD_COLOR)

					if 'Util' in path:
						ret['util'] = image
					if f'{card_id}_AIF.':
						ret['image'] = image
					else:
						tmp = path.split(".")[0].split("_")[-1]
						ret[tmp] = image
		return ret

	def get_card_art_by_id(self, card_id):
		tmp = self.find_card_art_file(card_id)
		return tmp