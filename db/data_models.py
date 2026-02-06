import json

class Company:
    mbs: str
    ime: str
    oib: str | None
    djelatnost_sifra: str | None
    djelatnost_naziv: str | None
    zupanija: str | None
    adresa: str | None
    naselje: str | None
    email_adrese: list[str] | None
    telefonski_brojevi: list[str] | None
    ostalo: dict | None
    gfi_count: int | None
    status: int | None
    naznaka_imena: str | None
    pravni_oblik: str | None

    def __init__(self, **kwargs):
        self.mbs = kwargs.get('mbs')
        self.ime = kwargs.get('ime')
        self.oib = kwargs.get('oib')
        self.djelatnost_sifra = kwargs.get('djelatnost_sifra')
        self.djelatnost_naziv = kwargs.get('djelatnost_naziv')
        self.zupanija = kwargs.get('zupanija')
        self.adresa = kwargs.get('adresa')
        self.naselje = kwargs.get('naselje')
        self.email_adrese = kwargs.get('email_adrese')
        self.telefonski_brojevi = kwargs.get('telefonski_brojevi')
        self.ostalo = kwargs.get('ostalo')
        self.gfi_count = kwargs.get('gfi_count')
        self.status = kwargs.get('status', 0)
        self.naznaka_imena = kwargs.get('naznaka_imena')
        self.pravni_oblik = kwargs.get('pravni_oblik')

    # to json
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> dict:
        return {
            "mbs": self.mbs,
            "ime": self.ime,
            "oib": self.oib,
            "djelatnost_sifra": self.djelatnost_sifra,
            "djelatnost_naziv": self.djelatnost_naziv,
            "zupanija": self.zupanija,
            "adresa": self.adresa,
            "naselje": self.naselje,
            "email_adrese": self.email_adrese,
            "telefonski_brojevi": self.telefonski_brojevi,
            "ostalo": self.ostalo,
            "gfi_count": self.gfi_count,
            "status": self.status,
            "naznaka_imena": self.naznaka_imena,
            "pravni_oblik": self.pravni_oblik,
        }

    def inject_from_sudreg_object(self, details: dict):
        self.oib = details.get('oib')
        self.djelatnost_sifra = details.get('pretezita_djelatnost', {}).get('sifra', '')
        self.djelatnost_naziv = details.get('pretezita_djelatnost', {}).get('puni_naziv', '')
        self.zupanija = details.get('sjediste', {}).get('naziv_zupanije', '')
        self.adresa = details.get('sjediste', {}).get('ulica', '') + ' ' + str(details.get('sjediste', {}).get('kucni_broj', ''))
        self.naselje = details.get('sjediste', {}).get('naziv_naselja', '')
        self.email_adrese = ', '.join([e['adresa'] for e in details.get('email_adrese', [])])
        self.gfi_count = len(details.get('gfi', []))
        self.status = details.get('status', 0)
        self.naznaka_imena = details.get('tvrtka', {}).get('naznaka_imena', '')
        self.pravni_oblik = details.get('pravni_oblik', {}).get('vrsta_pravnog_oblika').get('kratica', '')

    def update_with_values(self, c: "Company"):
        if self.mbs != c.mbs:
            raise ValueError("Companies must have the same MBS")

        self.oib = c.oib if c.oib else self.oib
        self.djelatnost_sifra = c.djelatnost_sifra if c.djelatnost_sifra else self.djelatnost_sifra
        self.djelatnost_naziv = c.djelatnost_naziv if c.djelatnost_naziv else self.djelatnost_naziv
        self.zupanija = c.zupanija if c.zupanija else self.zupanija
        self.adresa = c.adresa if c.adresa else self.adresa
        self.naselje = c.naselje if c.naselje else self.naselje
        self.email_adrese = c.email_adrese if c.email_adrese else self.email_adrese
        self.telefonski_brojevi = c.telefonski_brojevi if c.telefonski_brojevi else self.telefonski_brojevi
        self.ostalo = c.ostalo if c.ostalo else self.ostalo
        self.gfi_count = c.gfi_count if c.gfi_count else self.gfi_count
        self.status = c.status if c.status else self.status
        self.naznaka_imena = c.naznaka_imena if c.naznaka_imena else self.naznaka_imena
        self.pravni_oblik = c.pravni_oblik if c.pravni_oblik else self.pravni_oblik