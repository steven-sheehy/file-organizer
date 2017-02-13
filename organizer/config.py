# -*- coding: utf-8 -*-

from normalize.literal import *
from normalize.substitution import *

skippedFiles = set(['cover.jpg', 'metadata.opf', '.DS_Store'])
deleteFiles = set(['__MACOSX', '.DS_Store', '*.website', '*.url', '*.part', '*sample*'])
# rename "Featurettes" to "Extras"
manga  = Literals("7z", "rar", "zip")
dir = Literals("")

abbreviations = Literals("Ave", "Bros", "Dr", "Jr", "Mr", "Mrs", "Ms", "Rev", "St", "vs")
acronyms = Literals("AKA", "C2C", "DC", "LLC", "OVA", "TV", "UFO", "UK", "USA")
foreign = Literals("al", "chan", "de", "du", "et", "ga", "kun", "ni", "-san", "und", "wa", "wo")
groups = Literals("CHD", "d'argh", "DCP", "DTG", "FTG", "HP", "JYK", "LGC", "LOL", "n0m1", "PSA", "QCF", "RARBG", "RMTeam", "UTR", "YSTeam")
metadata = Literals("480p", "720p", "1080p", "1CH", "2CH", "6CH", "7CH", "AAC", "AC3", "azw3", "BluRay", "CD", "DL", "DTS", "DVD", "DVDRip", "epub", "FLAC", "HDTV", "HEVC", "mobi", "MKV", "MP3", "pdf", "x264", "x265", "Xvid")
miscellaneous = Literals("C-3PO", "com", "iZombie", "LEGO")
numerals = Literals("II", "III", "IV", "V", "VI", "VII", "VIII", "IX")
literals = Literals(acronyms, foreign, groups, metadata, miscellaneous, numerals)
possessives = Literals("Bob", "Marvel", "DC", "Childhood", "there", "Attenborough", "who")
small = Literals('a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'via', 'vs', 'vs\.')
removed = Literals('?', '*', 'www.RapidMovieZ.com', '(request)', '[request]', '[ed]')

preSubstitutions = [
  Substitution(r'%s' % removed.pattern, r''),
  Substitution(r'\. ?\. ?\.', r'…'),
  Substitution(r'((?<=^\w)|(?<!\.\w))\.(?=[ \)\]])', r'␃'),
  Substitution(r'(?<=\d)\.(?=\d\b)', r'␃'),
  Substitution(r'\.', r' '),
  Substitution(r'␃', r'.'),
  Substitution(r'(:|꞉|~|–)', ' - '),                         # Replace colon and colon similars
  Substitution(r'(?<=[^\s])(\[|\()', r' \1'),                # Rambo(1988) -> Rambo (1988)
  Substitution(r'(\]|\))(?=[^\s,])', r'\1 '),                # [1988]Rambo -> [1988] Rambo
  Substitution(r'(?<=\w)[-_]\s', ' - '),                     # Foo- Bar -> Foo - Bar
  Substitution(r'\s[_-](?=\w)', ' - '),                      # Foo -Bar -> Foo - Bar
  Substitution(r'^([\[\(].*?[\]\)]) ?(.*)', r'\2 \1'),       # [HorribleSubs] Naruto 1.mkv -> Naruto 1 [HorribleSubs].mkv
  Substitution(r'\b(%s)(?=s\s+\w)' % possessives.pattern, r"\1'"), # marvels -> Marvel's
  Substitution(r'\bDD(\d)\b', r'DD \1'),                     # DD5.1 -> DD 5.1
  Substitution(r'\bAAC(\d)\b', r'AAC \1'),                   # AAC1.0 -> AAC 1.0
  Substitution(r'\b[hx][ \.]?(26[45])\b', r'x\1'),           # H.265 -> x265
  Substitution(r'\b(%s)-' % metadata.pattern, r'\1 '),       # HEVC-RARBG -> HEVC RARBG
  Substitution(r'\bweb[- \.]?dl\b', r'Web-DL'),
  Substitution(r'\bweb[- \.]?rip\b', r'WebRip'),
  Substitution(r'\bB(D|R)(Rip)?\b', r'BluRay'),
  Substitution(r'\bx[ \.]files', r'X-Files'),
  Substitution(r'"', "'"),
  Substitution(r'[<>\|\\_]', ' '),
  Substitution(r'\s+', ' ')
]

postSubstitutions = [
  Substitution(r'(- )?\bs?(\d\d)[\. ]?(e|x|ep)[\. ]?(\d\d)\b( -)?', r'S\2E\4'),     # s01e04 -> S01E04
  Substitution(r'(- )?\bs?(\d)[\. ]?[e|x|ep][\. ]?(\d\d)\b( -)?', r'S0\2E\3'),      # s01e04 -> S01E04
  Substitution(r'\b(\d)of\d\b', r'S01E0\1'),                                        # 4of6 -> S01E04
  Substitution(r'(^|(?<= ))(?:[a-z]( |$)){2,}', lambda m: m.group(0).upper().replace(' ', '.') + ' '),  # A D -> A.D.
  Substitution(r'((?<=[a-z]\.){2,}) ?([a-z])$', r'\2.'),                              # U.S A.mkv -> U.S.A..mkv
  Substitution(r'(?<=\b\d) (?=\d\b)', '.'),                                         # 5 1 -> 5.1
  Substitution(r'\b(%s) ' % abbreviations.pattern, r'\1. '),                        # Dr -> Dr.
  Substitution(r'\b(%s)\b' % literals.pattern, literals.convert),                   # [rmteam] -> [RMTeam]
  Substitution(r'\s+(\]|\))', r'\1'),                        # [1998 ] -> [1988]
  Substitution(r'(\[|\()\s+', r'\1'),                        # [ 1998] -> [1988]
  Substitution(r'\bV(ol(ume|\.)? ?)?(\d+)\b', r'v\3', manga),                       # Vol. 01 -> v01
  Substitution(r'\bV(\d+)(\b|(?=c\d+))', r'v\1'),                                              # V01 -> v01
  Substitution(r'\bC(h(apters?|\.)?)? ?(\d+)\b', r'c\3', manga),                    # Chapters 001 -> c001
  Substitution(r'\bC(\d+)\b', r'c\1'),                                              # C001 -> c001
  Substitution(r'\[[a-f0-9]{8}\]', lambda m: m.group(0).upper()),                   # [Eb6cb498] -> [EB6CB498]
  Substitution(r'(?<=[,\]\)\d] )(%s)' % small.pattern, lambda m: m.group(1).capitalize())   # Simpsons, the (2015) the -> Simpsons, The (2015) The
]

