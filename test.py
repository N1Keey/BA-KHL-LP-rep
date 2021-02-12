import database as db
from pprint import pprint

krankheiten=db.Krankheit.getall2dict()
pprint(krankheiten)