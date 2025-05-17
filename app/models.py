from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')) 
    owner_id = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")

#class User(Base):
#    __tablename__ = "users"
#
#    id = Column(Integer, primary_key=True, nullable=False)
#    email = Column(String, nullable=False, unique=True)
#    password = Column(String, nullable=False)
#    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)



class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, nullable=False)
    ime_korisnika = Column(String, nullable=False)
    prezime_korisnika = Column(String,nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    datum_kreiranja_naloga = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Firma(Base):
    __tablename__ = "firma"

    id_firme = Column(Integer, primary_key=True, nullable=False)
    sifra = Column(String, nullable=False)
    naziv = Column(String, nullable=False)
    mesto = Column(String, nullable=False)
    adresa = Column(String, nullable=False)
    pib = Column(Integer, nullable=False)
    maticni_broj = Column(Integer, nullable=False)


class UserFirma(Base):
    __tablename__ = "userFirma"

    id_user_firma = Column(Integer, primary_key=True, nullable=False)
    datum_kreiranja = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    id_user_fk = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_firme_fk = Column(Integer, ForeignKey("firma.id_firme", ondelete="CASCADE"), nullable=False)

    user = relationship("User")
    firma = relationship("Firma")


class Kupac(Base):
    __tablename__ = "kupac"

    id_kupac = Column(Integer, primary_key=True, nullable=False)
    sifra = Column(String, nullable=False)
    naziv = Column(String, nullable=False)
    mesto = Column(String, nullable=False)
    adresa = Column(String, nullable=False)
    pib = Column(Integer, nullable=False)
    maticni_broj = Column(Integer, nullable=False)
    kontatkt = Column(String, nullable=False)  
    id_firme_fk = Column(Integer, ForeignKey("firma.id_firme", ondelete="CASCADE"), nullable=False)
    
    firma = relationship("Firma")


class Roba(Base):
    __tablename__ = "roba"

    id_robe = Column(Integer, primary_key=True, nullable=False)
    barcod = Column(String, nullable=False)
    naziv = Column(String, nullable=False)
    jedinica_mere = Column(String, nullable=False)
    cena_robe = Column(Integer, nullable=False)
    stopa_PDVa = Column(Integer, nullable=False)
    iznos_pdv_robe = Column(Integer, nullable=True)
    iznos_robe_sa_pdv = Column(Integer, nullable=True)
    valuta = Column(String, nullable=True)
    id_firme_fk = Column(Integer, ForeignKey("firma.id_firme", ondelete="CASCADE"), nullable=False)
    
    firma = relationship("Firma")


class Usluga(Base):
    __tablename__ = "usluga"

    id_usluge = Column(Integer, primary_key=True, nullable=False)
    sifra = Column(String, nullable=False)
    opis = Column(String, nullable=False)
    jedinica_mere = Column(String, nullable=False)
    cena_usluge = Column(Integer, nullable=False)
    stopa_PDVa = Column(Integer, nullable=False)
    iznos_pdv_usluge = Column(Integer, nullable=True)
    iznos_usluge_sa_pdv = Column(Integer, nullable=True)
    valuta = Column(String, nullable=True)
    id_firme_fk = Column(Integer, ForeignKey("firma.id_firme", ondelete="CASCADE"), nullable=False)
    
    firma = relationship("Firma")


class Racun(Base):
    __tablename__ = "racun"

    id_racuna = Column(Integer, primary_key=True, nullable=False)
    broj_racuna = Column(String, nullable=False)
    #status_fakture = Column(String, nullable=False)
    status_racuna = Column(String, nullable=True)
    tip_izdatog_racuna = Column(String, nullable=True)
    datum_izdavanja = Column(TIMESTAMP(timezone=True), nullable=True)
    datum_valute = Column(TIMESTAMP(timezone=True), nullable=True )
    datum_prometa = Column(TIMESTAMP(timezone=True), nullable=True)
    ukupna_osnovica = Column(Integer, nullable=True)
    ukupna_pdv = Column(Integer, nullable=True)
    ukupna_iznos = Column(Integer, nullable=True)
    valuta = Column(String, nullable=True)
    nacin_placanja = Column(String, nullable=True)
    broj_racuna_za_uplatu = Column(String, nullable=True)
    obaveznik_pdv = Column(String, nullable=True)
    
    ukupna_osnovica_20 = Column(Integer, nullable=True)
    ukupna_osnovica_10 = Column(Integer, nullable=True)
    ukupna_osnovica_0 = Column(Integer, nullable=True)
    ukupna_pdv_20 = Column(Integer, nullable=True)
    ukupna_pdv_10 = Column(Integer, nullable=True)
    ukupna_iznos_20 = Column(Integer, nullable=True)
    ukupna_iznos_10 = Column(Integer, nullable=True)

    napomena_na_fakturi = Column(String, nullable=True)
    poziv_na_broj = Column(String, nullable=True)

    mesto_isporuke = Column(String, nullable=True)
    nacin_transporta = Column(String, nullable=True)
    datum_isporuke = Column(TIMESTAMP(timezone=True), nullable=True)
  
    vrednost_avansa_20 = Column(Integer, nullable=True)
    vrednost_avansa_10 = Column(Integer, nullable=True)
    vrednost_avansa_0 = Column(Integer, nullable=True)

    id_firme_fk = Column(Integer, ForeignKey("firma.id_firme", ondelete="CASCADE"), nullable=False)
    id_kupac_fk = Column(Integer, ForeignKey("kupac.id_kupac", ondelete="CASCADE"), nullable=False)
    id_istorije_racuna_fk = Column(Integer, ForeignKey("racun.id_racuna", ondelete="CASCADE"), nullable=True)
    id_predracuna = Column(Integer, ForeignKey("racun.id_racuna", ondelete="CASCADE"), nullable=True)
    id_korisnik_kreirao_fk = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=True)

    firma = relationship("Firma")
    kupac = relationship("Kupac")
    user = relationship("User")

class RobaRacun(Base):
    __tablename__ = "robaRacun"

    id_roba_racun = Column(Integer, primary_key=True, nullable=False)
    kolicina = Column(Integer, nullable=False)
    osnovica_pdv_robe = Column(Integer, nullable=True)
    stopa_PDVa = Column(Integer, nullable=True)
    iznos_pdv_robe = Column(Integer, nullable=True)
    ukupna_cena_robe = Column(Integer, nullable=True)
    datum_kreiranja = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
   
    id_robe_fk = Column(Integer, ForeignKey("roba.id_robe", ondelete="CASCADE"), nullable=False)
    id_racuna_fk = Column(Integer, ForeignKey("racun.id_racuna", ondelete="CASCADE"), nullable=False)


    roba = relationship("Roba")
    racun = relationship("Racun")


class UslugaRacun(Base):
    __tablename__ = "uslugaRacun"

    id_usluga_racun = Column(Integer, primary_key=True, nullable=False)
    kolicina = Column(Integer, nullable=False)
    osnovica_pdv_usluge = Column(Integer, nullable=True)
    stopa_PDVa = Column(Integer, nullable=True)
    iznos_pdv_usluge = Column(Integer, nullable=True)
    ukupna_cena_usluge = Column(Integer, nullable=True)
    datum_kreiranja = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    id_usluge_fk = Column(Integer, ForeignKey("usluga.id_usluge", ondelete="CASCADE"), nullable=False)
    id_racuna_fk = Column(Integer, ForeignKey("racun.id_racuna", ondelete="CASCADE"), nullable=False)

    usluga = relationship("Usluga")
    racun = relationship("Racun")


class UserRacun(Base):
    __tablename__ = "userRacun"

    id_user_racun = Column(Integer, primary_key=True, nullable=False)
    datum_kreiranja_racuna = Column(TIMESTAMP(timezone=True), nullable=True)
    datum_izmene_racuna = Column(TIMESTAMP(timezone=True), nullable=True )
    datum_izdavanja_racuna = Column(TIMESTAMP(timezone=True), nullable=True)
    Tip_izdatog_racuna =  Column(String, nullable=False)
    id_user_fk = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_racuna_fk = Column(Integer, ForeignKey("racun.id_racuna", ondelete="CASCADE"), nullable=False)

    user = relationship("User")
    racun = relationship("Racun")

