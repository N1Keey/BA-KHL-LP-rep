import math

krankheiten=15
ursachen=88
symptome=113
komplikationen=40
diagnostiken=58
therapien=127
elementzahlgesamt=ursachen+symptome+komplikationen+diagnostiken+therapien
elemente4frage3=84

fragenPkrankheit=fragearten*fragen
def fragenanzahlberechner(umstand):
    fakultät=1
    for _ in range(umstand):
        if umstand!=0:
            fakultät=fakultät*umstand
            umstand-=1
        else:
            print('bla')
    return fakultät

fak_urs=fragenanzahlberechner(ursachen)
fak_sym=fragenanzahlberechner(symptome)
fak_komp=fragenanzahlberechner(komplikationen)
fak_dia=fragenanzahlberechner(diagnostiken)
fak_the=fragenanzahlberechner(therapien)

fak_elem_gesamt=fak_urs+fak_sym+fak_komp+fak_dia+fak_the

fak_mitkh=fak_elem_gesamt*krankheiten
fak_2fragearten=fak_mitkh*2

fak_frageart3=fragenanzahlberechner(elemente4frage3)

fak_gesamt_allefa=fak_frageart3+fak_2fragearten
def großezahlklein(großezahl):
    n=0
    while großezahl >=10:
        großezahl=großezahl/10
        n+=1
    text='%s*10^%s=%s'%(großezahl,n,großezahl*10**n)
    return text
print(fak_gesamt_allefa)
print(großezahlklein(fak_gesamt_allefa))

print(großezahlklein(fak_mitkh))