import database as db

krankheitendicts=db.Krankheit.getall2dict()
for krankheit in krankheitendicts:
    for umstand in krankheit.get('Umstände'):
        for element in krankheit.get('Umstände').get(umstand):
            print(element)