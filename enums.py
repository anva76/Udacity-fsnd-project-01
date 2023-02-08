import enum


class SelectEnum(enum.Enum):
    @classmethod
    def choices(cls):
        return [
            (c.value, c.value)
            for c in cls
        ]

    @classmethod
    def choices_first_blank(cls):
        return [
            ('', ''),
            *cls.choices()
        ]

    @classmethod
    def validation_list(cls):
        return [
            c.value
            for c in cls
        ]


class Genres(SelectEnum):
    Alternative         = 'Alternative'
    Blues               = 'Blues'
    Classical           = 'Classical'
    Country             = 'Country'
    Electronic          = 'Electronic'
    Folk                = 'Folk'
    Funk                = 'Funk'
    HipHop              = 'Hip-Hop'
    HeavyMetal          = 'Heavy Metal'
    Instrumental        = 'Instrumental'
    Jazz                = 'Jazz'
    MusicalTheatre      = 'Musical Theatre'
    Pop                 = 'Pop'
    Punk                = 'Punk'
    RnB                 = 'R&B'
    Reggae              = 'Reggae'
    RockNRoll           = 'Rock n Roll'
    Soul                = 'Soul'
    Other               = 'Other'


class States(SelectEnum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'
