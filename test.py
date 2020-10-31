import database as db

# beschreibung=db.krankheit_getschema('Arteriosklerose','Beschreibung')
# print(beschreibung) 
ursachen=db.krankheit_getSchemacontent('ursachen','Arteriosklerose')
print(ursachen)