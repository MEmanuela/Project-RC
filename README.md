# Server DHCP

DHCP (Dynamic Host Configuration Protocol) este un protocol care atribuie in mod dinamic(automat) adrese IP si alte informatii de configurare ale clientului (masca de retea, gateway implicit si servere DNS).

## Cum functioneaza un DHCP

![DHCP diagram](/diagram.png)

**Discover** - clientul trimite un mesaj pentru a localiza un server DHCP in retea

**Offer** - serverul DHCP trimite o oferta clientului in care i se ofera o adresa IP unica

**Request** - clientul trimite o cerere serverului DHCP cu un raspuns, in care ii „cere” serverului sa ii „imprumute” adresa IP

**Acknowledgment** - serverul transmite clientului pachetul de date solicitat

**Negative Acknowledgment** - serverul il trimite daca adresa IP nu este disponibila sau daca adresa nu mai este valida. In cazul acesta, clientul trebuie sa restarteze procesul de „inchiriere”.

In final, serverul DHCP marcheaza adresa IP alocata ca fiind ocupata si in uz de catre dispozitivul care a solicitat-o, acesta putand acum sa comunice cu celelalte dispozitive din retea.

## Lease Time

Deoarece numarul de adrese IP dintr-un server DHCP este limitat, DHCP aloca adrese IP doar pentru o perioada limitata de timp - durata de atribuire (lease time).

Aceasta durata de atribuire variaza in functie de situatie:
- pentru dispozitivele cu cablu, o durata de atribuire de 8 zile este o perioada tipica 

- pentru dispozitivele wireless este recomandata o perioada de atriburire mai mica de 24 de ore

**Lease Renew** - mesaj trimis serverului pentru extinderea duratei de atribuire. 
Se trimite atunci cand T = LT/2;

**Lease Rebinding** - mesaj trimis serverului pentru extinderea duratei de atribuire, in cazul in care mesajul de Lease Renew nu a fost receptionat. 
Se trimite atunci cand T = 7/8 LT;

## Alte mesaje DHCP

**DHCP DECLINE** - mesaj trimis de client catre serverul DHCP in care refuza oferta adresei IP

**DHCP RELEASE** - mesajul este utilizat in mod obisnuit atunci cand clientul  „renunta” si elibereaza adresa IP

**DHCP INFORM** - mesaj trimis serverului DHCP cu scopul de a alfa mai multe detalii (ex: DHCP INFORM poate fi trimis pentru a localiza alt server DHCP in retea)

## Schema unei aplicatii 

![App Diagram](/RC-APP.png)