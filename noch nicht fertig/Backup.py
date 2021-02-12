# def fragen_typ1_build(krankheiten4use):
#     def dicts_prepare(krankheiten4use):
#         krankheitenfragendicts=[]
#         for krankheit in krankheiten4use:
#             krankheitenfragendict={'Krankheit':krankheit,'Umstand':{'Ursachen':[],'Symptome':[],
#             'Komplikationen':[], 'Diagnostiken':[], 'Therapien':[]}}
#             krankheitenfragendicts.append(krankheitenfragendict)
#         return krankheitenfragendicts
#     def dicts_fill(prepared_dicts):
#         for krankheit in krankheitendicts4fragen:
#             for umstand in krankheit.get('Umstand'):
#                 if krankheit.get('Umstand').get(umstand)==[]: #Wenn Frage neu gebildet und nicht aktualisiert wird
#                     krankheit.get('Umstand')[umstand]={'Frage':'','Antworten':{'Right':[],'Wrong':[]}}
#                     if umstand=='Ursachen':
#                         umstandRights=Ursache.getAll_fromKrankheit(Ursache,krankheit.get('Krankheit'), True)
#                         umstandAll=Ursache.getAll(Ursache)
#                     elif umstand=='Symptome':
#                         umstandRights=Symptom.getAll_fromKrankheit(Symptom,krankheit.get('Krankheit'), True)
#                         umstandAll=Symptom.getAll(Symptom)
#                     elif umstand=='Komplikationen':
#                         umstandRights=Komplikation.getAll_fromKrankheit(Komplikation,krankheit.get('Krankheit'), True)
#                         umstandAll=Komplikation.getAll(Komplikation)
#                     elif umstand=='Diagnostiken':
#                         umstandRights=Diagnostik.getAll_fromKrankheit(Diagnostik,krankheit.get('Krankheit'), True)
#                         umstandAll=Diagnostik.getAll(Diagnostik)
#                     elif umstand=='Therapien':
#                         umstandRights=Therapie.getAll_fromKrankheit(Therapie,krankheit.get('Krankheit'), True)
#                         umstandAll=Therapie.getAll(Therapie)
#                     for element in umstandRights:
#                         krankheit.get('Umstand')[umstand]['Antworten']['Right'].append(element)
#                         if element in umstandAll:
#                             umstandAll.remove(element)
#                     for element in umstandAll:
#                         krankheit.get('Umstand')[umstand]['Antworten']['Wrong'].append(element)
#         return krankheitendicts4fragen
#     def fragentext_build(krankheit, umstand):
#         if umstand == 'Ursachen':
#             frage='Welche %s hat ein/e %s?'
#         elif umstand == 'Symptome':
#             frage='Welche %s treten bei einer/m %s auf?'
#         elif umstand == 'Komplikationen':
#             frage='Welche %s können bei einer/m %s auftreten?'
#         elif umstand == 'Diagnostiken':
#             frage='Welche %s nutzt man bei einer/m %s?'
#         elif umstand == 'Therapien':
#             frage='Welche %s nutzt man bei einer/m %s?'
#         frage=frage%(umstand,krankheit)
#         return frage
#     def dicts_sortAns(filled_dicts):
#         answercount=6 #legt anzahl antworten fest
#         for krankheit in data4fragenDicts:
#             for umstand in krankheit.get('Umstand'):
#                 fragenDict={}
#                 if 'Right' in krankheit.get('Umstand').get(umstand).get('Antworten'):
#                     rightAnsAll=krankheit.get('Umstand').get(umstand).get('Antworten').get('Right')
#                     rightAns=[]
#                     rnd=random.randint(1,answercount-1)
#                     if answercount > len(rightAnsAll):
#                         rnd=random.randint(1,len(rightAnsAll))
#                     while len(rightAns) < rnd:
#                         rightAn=rightAnsAll[random.randint(0,len(rightAnsAll)-1)]
#                         if rightAn not in rightAns:
#                             rightAns.append(rightAn)
#                             fragenDict[rightAn]='right'
#                 if 'Wrong' in krankheit.get('Umstand').get(umstand).get('Antworten'):
#                     wrongAnsAll=krankheit.get(umstand).get('Antworten').get('Wrong')
#                     wrongAns=[]
#                     while len(wrongAns) < answercount-rnd:
#                         wrongAn=wrongAnsAll[random.randint(0,len(wrongAnsAll)-1)]
#                         if wrongAn not in wrongAns:
#                             wrongAns.append(wrongAn)      
#                             fragenDict[wrongAn]='wrong' 
#                 if 'Right' in krankheit.get('Umstand').get(umstand).get('Antworten') or 'Wrong' in krankheit.get('Umstand').get(umstand).get('Antworten'):
#                     keys=list(fragenDict.items())
#                     random.shuffle(keys)
#                     fragenDict=dict(keys)
#                     krankheit.get('Umstand')[umstand]['Antworten']=fragenDict
#                     krankheit.get('Umstand')[umstand]['Frage']=fragen_buildFrage4dict_Fragenart1(krankheit.get('Krankheit'), umstand)
#         return sorted
#     def build_from_scratch(krankheiten4use):
        # prepared_dicts=dicts_prepare(krankheiten4use)
        # filled_dicts=dicts_fill(prepared_dicts)
        # sorted_dicts=dicts_sortAns(filled_dicts)
        # return sorted_dicts