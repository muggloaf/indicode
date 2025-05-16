"""
Transliteration utility for converting text between languages
Based on character mapping and phonetic rules
"""
import re

# Hindi Unicode range: 0900-097F
HINDI_CHARS = {
    # Independent vowels (स्वर)
    'अ': 'a',    'आ': 'aa',   'इ': 'i',    'ई': 'ee',   'उ': 'u',
    'ऊ': 'oo',   'ए': 'e',    'ऐ': 'ai',   'ओ': 'o',    'औ': 'au',
    'अं': 'an',  'अः': 'ah',
    
    # Consonant-Vowel combinations (व्यंजन + मात्रा)
    # क-row (ka)
    'क': 'ka',    'का': 'kaa',  'कि': 'ki',  'की': 'kee',  'कु': 'ku',
    'कू': 'koo',  'के': 'ke',   'कै': 'kai',  'को': 'ko',   'कौ': 'kau',
    'कं': 'kan',  'कः': 'kah',
    
    # ख-row (kha)
    'ख': 'kha',   'खा': 'khaa', 'खि': 'khi', 'खी': 'khee', 'खु': 'khu',
    'खू': 'khoo', 'खे': 'khe',  'खै': 'khai', 'खो': 'kho',  'खौ': 'khau',
    'खं': 'khan', 'खः': 'khah',
    
    # ग-row (ga)
    'ग': 'ga',    'गा': 'gaa',  'गि': 'gi',  'गी': 'gee',  'गु': 'gu',
    'गू': 'goo',  'गे': 'ge',   'गै': 'gai',  'गो': 'go',   'गौ': 'gau',
    'गं': 'gan',  'गः': 'gah',
    
    # घ-row (gha)
    'घ': 'gha',   'घा': 'ghaa', 'घि': 'ghi', 'घी': 'ghee', 'घु': 'ghu',
    'घू': 'ghoo', 'घे': 'ghe',  'घै': 'ghai', 'घो': 'gho',  'घौ': 'ghau',
    'घं': 'ghan', 'घः': 'ghah',
    
    # ङ-row (nga)
    'ङ': 'nga',   'ङा': 'ngaa', 'ङि': 'ngi', 'ङी': 'ngee', 'ङु': 'ngu',
    'ङू': 'ngoo', 'ङे': 'nge',  'ङै': 'ngai', 'ङो': 'ngo',  'ङौ': 'ngau',
    'ङं': 'ngan', 'ङः': 'ngah',
    
    # च-row (cha)
    'च': 'cha',   'चा': 'chaa', 'चि': 'chi', 'ची': 'chee', 'चु': 'chu',
    'चू': 'choo', 'चे': 'che',  'चै': 'chai', 'चो': 'cho',  'चौ': 'chau',
    'चं': 'chan', 'चः': 'chah',
    
    # छ-row (chha)
    'छ': 'chha',  'छा': 'chhaa', 'छि': 'chhi', 'छी': 'chhee', 'छु': 'chhu',
    'छू': 'chhoo', 'छे': 'chhe',  'छै': 'chhai', 'छो': 'chho',  'छौ': 'chhau',
    'छं': 'chhan', 'छः': 'chhah',
    
    # ज-row (ja)
    'ज': 'ja',    'जा': 'jaa',  'जि': 'ji',  'जी': 'jee',  'जु': 'ju',
    'जू': 'joo',  'जे': 'je',   'जै': 'jai',  'जो': 'jo',   'जौ': 'jau',
    'जं': 'jan',  'जः': 'jah',
    
    # झ-row (jha)
    'झ': 'jha',   'झा': 'jhaa', 'झि': 'jhi', 'झी': 'jhee', 'झु': 'jhu',
    'झू': 'jhoo', 'झे': 'jhe',  'झै': 'jhai', 'झो': 'jho',  'झौ': 'jhau',
    'झं': 'jhan', 'झः': 'jhah',
    
    # ञ-row (nya)
    'ञ': 'nya',   'ञा': 'nyaa', 'ञि': 'nyi', 'ञी': 'nyee', 'ञु': 'nyu',
    'ञू': 'nyoo', 'ञे': 'nye',  'ञै': 'nyai', 'ञो': 'nyo',  'ञौ': 'nyau',
    'ञं': 'nyan', 'ञः': 'nyah',
    
    # ट-row (ta - retroflex)
    'ट': 'ta',    'टा': 'taa',  'टि': 'ti',  'टी': 'tee',  'टु': 'tu',
    'टू': 'too',  'टे': 'te',   'टै': 'tai',  'टो': 'to',   'टौ': 'tau',
    'टं': 'tan',  'टः': 'tah',
    
    # ठ-row (tha - retroflex)
    'ठ': 'tha',   'ठा': 'thaa', 'ठि': 'thi', 'ठी': 'thee', 'ठु': 'thu',
    'ठू': 'thoo', 'ठे': 'the',  'ठै': 'thai', 'ठो': 'tho',  'ठौ': 'thau',
    'ठं': 'than', 'ठः': 'thah',
    
    # ड-row (da - retroflex)
    'ड': 'da',    'डा': 'daa',  'डि': 'di',  'डी': 'dee',  'डु': 'du',
    'डू': 'doo',  'डे': 'de',   'डै': 'dai',  'डो': 'do',   'डौ': 'dau',
    'डं': 'dan',  'डः': 'dah',
    
    # ढ-row (dha - retroflex)
    'ढ': 'dha',   'ढा': 'dhaa', 'ढि': 'dhi', 'ढी': 'dhee', 'ढु': 'dhu',
    'ढू': 'dhoo', 'ढे': 'dhe',  'ढै': 'dhai', 'ढो': 'dho',  'ढौ': 'dhau',
    'ढं': 'dhan', 'ढः': 'dhah',
    
    # ण-row (na - retroflex)
    'ण': 'na',    'णा': 'naa',  'णि': 'ni',  'णी': 'nee',  'णु': 'nu',
    'णू': 'noo',  'णे': 'ne',   'णै': 'nai',  'णो': 'no',   'णौ': 'nau',
    'णं': 'nan',  'णः': 'nah',
    
    # त-row (ta - dental)
    'त': 'ta',    'ता': 'taa',  'ति': 'ti',  'ती': 'tee',  'तु': 'tu',
    'तू': 'too',  'ते': 'te',   'तै': 'tai',  'तो': 'to',   'तौ': 'tau',
    'तं': 'tan',  'तः': 'tah',
    
    # थ-row (tha - dental)
    'थ': 'tha',   'था': 'thaa', 'थि': 'thi', 'थी': 'thee', 'थु': 'thu',
    'थू': 'thoo', 'थे': 'the',  'थै': 'thai', 'थो': 'tho',  'थौ': 'thau',
    'थं': 'than', 'थः': 'thah',
    
    # द-row (da - dental)
    'द': 'da',    'दा': 'daa',  'दि': 'di',  'दी': 'dee',  'दु': 'du',
    'दू': 'doo',  'दे': 'de',   'दै': 'dai',  'दो': 'do',   'दौ': 'dau',
    'दं': 'dan',  'दः': 'dah',
    
    # ध-row (dha - dental)
    'ध': 'dha',   'धा': 'dhaa', 'धि': 'dhi', 'धी': 'dhee', 'धु': 'dhu',
    'धू': 'dhoo', 'धे': 'dhe',  'धै': 'dhai', 'धो': 'dho',  'धौ': 'dhau',
    'धं': 'dhan', 'धः': 'dhah',
    
    # न-row (na - dental)
    'न': 'na',    'ना': 'naa',  'नि': 'ni',  'नी': 'nee',  'नु': 'nu',
    'नू': 'noo',  'ने': 'ne',   'नै': 'nai',  'नो': 'no',   'नौ': 'nau',
    'नं': 'nan',  'नः': 'nah',
    
    # प-row (pa)
    'प': 'pa',    'पा': 'paa',  'पि': 'pi',  'पी': 'pee',  'पु': 'pu',
    'पू': 'poo',  'पे': 'pe',   'पै': 'pai',  'पो': 'po',   'पौ': 'pau',
    'पं': 'pan',  'पः': 'pah',
    
    # फ-row (pha)
    'फ': 'pha',   'फा': 'phaa', 'फि': 'phi', 'फी': 'phee', 'फु': 'phu',
    'फू': 'phoo', 'फे': 'phe',  'फै': 'phai', 'फो': 'pho',  'फौ': 'phau',
    'फं': 'phan', 'फः': 'phah',
    
    # ब-row (ba)
    'ब': 'ba',    'बा': 'baa',  'बि': 'bi',  'बी': 'bee',  'बु': 'bu',
    'बू': 'boo',  'बे': 'be',   'बै': 'bai',  'बो': 'bo',   'बौ': 'bau',
    'बं': 'ban',  'बः': 'bah',
    
    # भ-row (bha)
    'भ': 'bha',   'भा': 'bhaa', 'भि': 'bhi', 'भी': 'bhee', 'भु': 'bhu',
    'भू': 'bhoo', 'भे': 'bhe',  'भै': 'bhai', 'भो': 'bho',  'भौ': 'bhau',
    'भं': 'bhan', 'भः': 'bhah',
    
    # म-row (ma)
    'म': 'ma',    'मा': 'maa',  'मि': 'mi',  'मी': 'mee',  'मु': 'mu',
    'मू': 'moo',  'मे': 'me',   'मै': 'mai',  'मो': 'mo',   'मौ': 'mau',
    'मं': 'man',  'मः': 'mah',
    
    # य-row (ya)
    'य': 'ya',    'या': 'yaa',  'यि': 'yi',  'यी': 'yee',  'यु': 'yu',
    'यू': 'yoo',  'ये': 'ye',   'यै': 'yai',  'यो': 'yo',   'यौ': 'yau',
    'यं': 'yan',  'यः': 'yah',
    
    # र-row (ra)
    'र': 'ra',    'रा': 'raa',  'रि': 'ri',  'री': 'ree',  'रु': 'ru',
    'रू': 'roo',  'रे': 're',   'रै': 'rai',  'रो': 'ro',   'रौ': 'rau',
    'रं': 'ran',  'रः': 'rah',
    
    # ल-row (la)
    'ल': 'la',    'ला': 'laa',  'लि': 'li',  'ली': 'lee',  'लु': 'lu',
    'लू': 'loo',  'ले': 'le',   'लै': 'lai',  'लो': 'lo',   'लौ': 'lau',
    'लं': 'lan',  'लः': 'lah',
    
    # व-row (va/wa)
    'व': 'va',    'वा': 'vaa',  'वि': 'vi',  'वी': 'vee',  'वु': 'vu',
    'वू': 'voo',  'वे': 've',   'वै': 'vai',  'वो': 'vo',   'वौ': 'vau',
    'वं': 'van',  'वः': 'vah',
    
    # श-row (sha - palatal)
    'श': 'sha',   'शा': 'shaa', 'शि': 'shi', 'शी': 'shee', 'शु': 'shu',
    'शू': 'shoo', 'शे': 'she',  'शै': 'shai', 'शो': 'sho',  'शौ': 'shau',
    'शं': 'shan', 'शः': 'shah',
    
    # ष-row (sha - retroflex)
    'ष': 'sha',   'षा': 'shaa', 'षि': 'shi', 'षी': 'shee', 'षु': 'shu',
    'षू': 'shoo', 'षे': 'she',  'षै': 'shai', 'षो': 'sho',  'षौ': 'shau',
    'षं': 'shan', 'षः': 'shah',
    
    # स-row (sa)
    'स': 'sa',    'सा': 'saa',  'सि': 'si',  'सी': 'see',  'सु': 'su',
    'सू': 'soo',  'से': 'se',   'सै': 'sai',  'सो': 'so',   'सौ': 'sau',
    'सं': 'san',  'सः': 'sah',
    
    # ह-row (ha)
    'ह': 'ha',    'हा': 'haa',  'हि': 'hi',  'ही': 'hee',  'हु': 'hu',
    'हू': 'hoo',  'हे': 'he',   'है': 'hai',  'हो': 'ho',   'हौ': 'hau',
    'हं': 'han',  'हः': 'hah',
    
    # क्ष-row (ksha)
    'क्ष': 'ksha',  'क्षा': 'kshaa', 'क्षि': 'kshi', 'क्षी': 'kshee', 'क्षु': 'kshu',
    'क्षू': 'kshoo', 'क्षे': 'kshe',  'क्षै': 'kshai', 'क्षो': 'ksho',  'क्षौ': 'kshau',
    'क्षं': 'kshan', 'क्षः': 'kshah',
    
    # त्र-row (tra)
    'त्र': 'tra',  'त्रा': 'traa', 'त्रि': 'tri', 'त्री': 'tree', 'त्रु': 'tru',
    'त्रू': 'troo', 'त्रे': 'tre',  'त्रै': 'trai', 'त्रो': 'tro',  'त्रौ': 'trau',
    'त्रं': 'tran', 'त्रः': 'trah',
    
    # ज्ञ-row (gya)
    'ज्ञ': 'gya',  'ज्ञा': 'gyaa', 'ज्ञि': 'gyi', 'ज्ञी': 'gyee', 'ज्ञु': 'gyu',
    'ज्ञू': 'gyoo', 'ज्ञे': 'gye',  'ज्ञै': 'gyai', 'ज्ञो': 'gyo',  'ज्ञौ': 'gyau',
    'ज्ञं': 'gyan', 'ज्ञः': 'gyah',
    
    # Additional common conjuncts
    # त्व-row (tva)
    'त्व': 'tva',  'त्वा': 'tvaa', 'त्वि': 'tvi', 'त्वी': 'tvee', 'त्वु': 'tvu',
    'त्वू': 'tvoo', 'त्वे': 'tve',  'त्वै': 'tvai', 'त्वो': 'tvo',  'त्वौ': 'tvau',
    'त्वं': 'tvan', 'त्वः': 'tvah',
    
    # त्म-row (tma)
    'त्म': 'tma',  'त्मा': 'tmaa', 'त्मि': 'tmi', 'त्मी': 'tmee', 'त्मु': 'tmu',
    'त्मू': 'tmoo', 'त्मे': 'tme',  'त्मै': 'tmai', 'त्मो': 'tmo',  'त्मौ': 'tmau',
    'त्मं': 'tman', 'त्मः': 'tmah',
    
    # प्र-row (pra)
    'प्र': 'pra',  'प्रा': 'praa', 'प्रि': 'pri', 'प्री': 'pree', 'प्रु': 'pru',
    'प्रू': 'proo', 'प्रे': 'pre',  'प्रै': 'prai', 'प्रो': 'pro',  'प्रौ': 'prau',
    'प्रं': 'pran', 'प्रः': 'prah',
    
    # स्व-row (sva)
    'स्व': 'sva',  'स्वा': 'svaa', 'स्वि': 'svi', 'स्वी': 'svee', 'स्वु': 'svu',
    'स्वू': 'svoo', 'स्वे': 'sve',  'स्वै': 'svai', 'स्वो': 'svo',  'स्वौ': 'svau',
    'स्वं': 'svan', 'स्वः': 'svah',
    
    # स्त्र-row (stra)
    'स्त्र': 'stra',  'स्त्रा': 'straa', 'स्त्रि': 'stri', 'स्त्री': 'stree', 'स्त्रु': 'stru',
    'स्त्रू': 'stroo', 'स्त्रे': 'stre',  'स्त्रै': 'strai', 'स्त्रो': 'stro',  'स्त्रौ': 'strau',
    'स्त्रं': 'stran', 'स्त्रः': 'strah',
    
    # न्त्र-row (ntra)
    'न्त्र': 'ntra',  'न्त्रा': 'ntraa', 'न्त्रि': 'ntri', 'न्त्री': 'ntree', 'न्त्रु': 'ntru',
    'न्त्रू': 'ntroo', 'न्त्रे': 'ntre',  'न्त्रै': 'ntrai', 'न्त्रो': 'ntro',  'न्त्रौ': 'ntrau',
    'न्त्रं': 'ntran', 'न्त्रः': 'ntrah',
    
    # श्र-row (shra)
    'श्र': 'shra',  'श्रा': 'shraa', 'श्रि': 'shri', 'श्री': 'shree', 'श्रु': 'shru',
    'श्रू': 'shroo', 'श्रे': 'shre',  'श्रै': 'shrai', 'श्रो': 'shro',  'श्रौ': 'shrau',
    'श्रं': 'shran', 'श्रः': 'shrah',
    
    # द्र-row (dra)
    'द्र': 'dra',  'द्रा': 'draa', 'द्रि': 'dri', 'द्री': 'dree', 'द्रु': 'dru',
    'द्रू': 'droo', 'द्रे': 'dre',  'द्रै': 'drai', 'द्रो': 'dro',  'द्रौ': 'drau',
    'द्रं': 'dran', 'द्रः': 'drah',
    
    # क्र-row (kra)
    'क्र': 'kra',  'क्रा': 'kraa', 'क्रि': 'kri', 'क्री': 'kree', 'क्रु': 'kru',
    'क्रू': 'kroo', 'क्रे': 'kre',  'क्रै': 'krai', 'क्रो': 'kro',  'क्रौ': 'krau',
    'क्रं': 'kran', 'क्रः': 'krah',
    
    # ग्र-row (gra)
    'ग्र': 'gra',  'ग्रा': 'graa', 'ग्रि': 'gri', 'ग्री': 'gree', 'ग्रु': 'gru',
    'ग्रू': 'groo', 'ग्रे': 'gre',  'ग्रै': 'grai', 'ग्रो': 'gro',  'ग्रौ': 'grau',
    'ग्रं': 'gran', 'ग्रः': 'grah',
    
    # द्व-row (dva)
    'द्व': 'dva',  'द्वा': 'dvaa', 'द्वि': 'dvi', 'द्वी': 'dvee', 'द्वु': 'dvu',
    'द्वू': 'dvoo', 'द्वे': 'dve',  'द्वै': 'dvai', 'द्वो': 'dvo',  'द्वौ': 'dvau',
    'द्वं': 'dvan', 'द्वः': 'dvah',
    
    # द्य-row (dya)
    'द्य': 'dya',  'द्या': 'dyaa', 'द्यि': 'dyi', 'द्यी': 'dyee', 'द्यु': 'dyu',
    'द्यू': 'dyoo', 'द्ये': 'dye',  'द्यै': 'dyai', 'द्यो': 'dyo',  'द्यौ': 'dyau',
    'द्यं': 'dyan', 'द्यः': 'dyah',
    
    # न्य-row (nya)
    'न्य': 'nya',  'न्या': 'nyaa', 'न्यि': 'nyi', 'न्यी': 'nyee', 'न्यु': 'nyu',
    'न्यू': 'nyoo', 'न्ये': 'nye',  'न्यै': 'nyai', 'न्यो': 'nyo',  'न्यौ': 'nyau',
    'न्यं': 'nyan', 'न्यः': 'nyah',
    
    # Special consonants and modifiers
    '्': '',      # virama/halant (vowel suppressor)
    'ं': 'n',     # anusvara (nasal sound)
    'ः': 'h',     # visarga (aspiration)
    'ँ': 'n',     # chandrabindu (nasalization)
    
    # Nukta-modified consonants (for Urdu/Persian/Arabic sounds)
    'क़': 'qa',   'क़ा': 'qaa',  'क़ि': 'qi',  'क़ी': 'qee',  'क़ु': 'qu',
    'क़ू': 'qoo',  'क़े': 'qe',   'क़ै': 'qai',  'क़ो': 'qo',   'क़ौ': 'qau',
    'क़ं': 'qan',  'क़ः': 'qah',
    
    'ख़': 'kha',  'ख़ा': 'khaa', 'ख़ि': 'khi', 'ख़ी': 'khee', 'ख़ु': 'khu',
    'ख़ू': 'khoo', 'ख़े': 'khe',  'ख़ै': 'khai', 'ख़ो': 'kho',  'ख़ौ': 'khau',
    'ख़ं': 'khan', 'ख़ः': 'khah',
    
    'ग़': 'gha',  'ग़ा': 'ghaa', 'ग़ि': 'ghi', 'ग़ी': 'ghee', 'ग़ु': 'ghu',
    'ग़ू': 'ghoo', 'ग़े': 'ghe',  'ग़ै': 'ghai', 'ग़ो': 'gho',  'ग़ौ': 'ghau',
    'ग़ं': 'ghan', 'ग़ः': 'ghah',
    
    'ज़': 'za',   'ज़ा': 'zaa',  'ज़ि': 'zi',  'ज़ी': 'zee',  'ज़ु': 'zu',
    'ज़ू': 'zoo',  'ज़े': 'ze',   'ज़ै': 'zai',  'ज़ो': 'zo',   'ज़ौ': 'zau',
    'ज़ं': 'zan',  'ज़ः': 'zah',
    
    'फ़': 'fa',   'फ़ा': 'faa',  'फ़ि': 'fi',  'फ़ी': 'fee',  'फ़ु': 'fu',
    'फ़ू': 'foo',  'फ़े': 'fe',   'फ़ै': 'fai',  'फ़ो': 'fo',   'फ़ौ': 'fau',
    'फ़ं': 'fan',  'फ़ः': 'fah',
    
    'ड़': 'da',   'ड़ा': 'daa',  'ड़ि': 'di',  'ड़ी': 'dee',  'ड़ु': 'du',
    'ड़ू': 'doo',  'ड़े': 'de',   'ड़ै': 'dai',  'ड़ो': 'do',   'ड़ौ': 'dau',
    'ड़ं': 'dan',  'ड़ः': 'dah',
    
    'ढ़': 'rha',  'ढ़ा': 'rhaa', 'ढ़ि': 'rhi', 'ढ़ी': 'rhee', 'ढ़ु': 'rhu',
    'ढ़ू': 'rhoo', 'ढ़े': 'rhe',  'ढ़ै': 'rhai', 'ढ़ो': 'rho',  'ढ़ौ': 'rhau',
    'ढ़ं': 'rhan', 'ढ़ः': 'rhah',
    
    # Additional vowels for loanwords
    'ऑ': 'o',    'ऑं': 'on',  # short o (as in coffee)
    'ॉ': 'o',     # matra form of ऑ
    'ऍ': 'e',    'ऍं': 'en',  # short e (as in met) 
    'ॅ': 'e',     # matra form of ऍ
    'ऋ': 'ri',   'ऋं': 'rin', # vocalic r
    'ृ': 'ri',    # matra form of ऋ
    'ॡ': 'lri',   # vocalic l
    
    # Additional special symbols
    'ॐ': 'om',    # Om symbol
    '॰': '.',     # Abbreviation sign
    '₹': 'Rs',    # Rupee symbol
    'ऽ': '\'',     # Avagraha (vowel elision)
    '़': '',      # Nukta (dot below modifier for Urdu sounds)
    
    # More conjuncts commonly found in texts
    # ह्न-row (hna)
    'ह्न': 'hna',  'ह्ना': 'hnaa', 'ह्नि': 'hni', 'ह्नी': 'hnee', 'ह्नु': 'hnu',
    'ह्नू': 'hnoo', 'ह्ने': 'hne',  'ह्नै': 'hnai', 'ह्नो': 'hno',  'ह्नौ': 'hnau',
    
    # ह्म-row (hma)
    'ह्म': 'hma',  'ह्मा': 'hmaa', 'ह्मि': 'hmi', 'ह्मी': 'hmee', 'ह्मु': 'hmu',
    'ह्मू': 'hmoo', 'ह्मे': 'hme',  'ह्मै': 'hmai', 'ह्मो': 'hmo',  'ह्मौ': 'hmau',
    
    # ह्य-row (hya)
    'ह्य': 'hya',  'ह्या': 'hyaa', 'ह्यि': 'hyi', 'ह्यी': 'hyee', 'ह्यु': 'hyu',
    'ह्यू': 'hyoo', 'ह्ये': 'hye',  'ह्यै': 'hyai', 'ह्यो': 'hyo',  'ह्यौ': 'hyau',
    
    # ह्र-row (hra)
    'ह्र': 'hra',  'ह्रा': 'hraa', 'ह्रि': 'hri', 'ह्री': 'hree', 'ह्रु': 'hru',
    'ह्रू': 'hroo', 'ह्रे': 'hre',  'ह्रै': 'hrai', 'ह्रो': 'hro',  'ह्रौ': 'hrau',
    
    # ह्ल-row (hla)
    'ह्ल': 'hla',  'ह्ला': 'hlaa', 'ह्लि': 'hli', 'ह्ली': 'hlee', 'ह्लु': 'hlu',
    'ह्लू': 'hloo', 'ह्ले': 'hle',  'ह्लै': 'hlai', 'ह्लो': 'hlo',  'ह्लौ': 'hlau',
    
    # ह्व-row (hva)
    'ह्व': 'hva',  'ह्वा': 'hvaa', 'ह्वि': 'hvi', 'ह्वी': 'hvee', 'ह्वु': 'hvu',
    'ह्वू': 'hvoo', 'ह्वे': 'hve',  'ह्वै': 'hvai', 'ह्वो': 'hvo',  'ह्वौ': 'hvau',
    
    # श्च-row (shcha)
    'श्च': 'shcha',  'श्चा': 'shchaa', 'श्चि': 'shchi', 'श्ची': 'shchee', 'श्चु': 'shchu',
    'श्चू': 'shchoo', 'श्चे': 'shche',  'श्चै': 'shchai', 'श्चो': 'shcho',  'श्चौ': 'shchau',
    
    # ल्ल-row (lla)
    'ल्ल': 'lla',  'ल्ला': 'llaa', 'ल्लि': 'lli', 'ल्ली': 'llee', 'ल्लु': 'llu',
    'ल्लू': 'lloo', 'ल्ले': 'lle',  'ल्लै': 'llai', 'ल्लो': 'llo',  'ल्लौ': 'llau',
    
    # त्न-row (tna)
    'त्न': 'tna',  'त्ना': 'tnaa', 'त्नि': 'tni', 'त्नी': 'tnee', 'त्नु': 'tnu',
    'त्नू': 'tnoo', 'त्ने': 'tne',  'त्नै': 'tnai', 'त्नो': 'tno',  'त्नौ': 'tnau',
    
    # स्न-row (sna)
    'स्न': 'sna',  'स्ना': 'snaa', 'स्नि': 'sni', 'स्नी': 'snee', 'स्नु': 'snu',
    'स्नू': 'snoo', 'स्ने': 'sne',  'स्नै': 'snai', 'स्नो': 'sno',  'स्नौ': 'snau',
    
    # भ्र-row (bhra)
    'भ्र': 'bhra',  'भ्रा': 'bhraa', 'भ्रि': 'bhri', 'भ्री': 'bhree', 'भ्रु': 'bhru',
    'भ्रू': 'bhroo', 'भ्रे': 'bhre',  'भ्रै': 'bhrai', 'भ्रो': 'bhro',  'भ्रौ': 'bhrau',
    
    # स्म-row (sma)
    'स्म': 'sma',  'स्मा': 'smaa', 'स्मि': 'smi', 'स्मी': 'smee', 'स्मु': 'smu',
    'स्मू': 'smoo', 'स्मे': 'sme',  'स्मै': 'smai', 'स्मो': 'smo',  'स्मौ': 'smau',
    
    # Numerals
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
    
    # Punctuation & Special Characters
    '।': '.', '॥': '.',
    
    # Matras (Vowel diacritics/signs) alone - for composition
    'ा': 'aa',   'ि': 'i',    'ी': 'ee',   'ु': 'u',    'ू': 'oo',
    'े': 'e',    'ै': 'ai',   'ो': 'o',    'ौ': 'au',
    
    # Half-consonant forms (with virama/halant)
    'क्': 'k',   'ख्': 'kh',   'ग्': 'g',    'घ्': 'gh',   'ङ्': 'ng',
    'च्': 'ch',  'छ्': 'chh',  'ज्': 'j',    'झ्': 'jh',   'ञ्': 'ny',
    'ट्': 't',   'ठ्': 'th',   'ड्': 'd',    'ढ्': 'dh',   'ण्': 'n',
    'त्': 't',   'थ्': 'th',   'द्': 'd',    'ध्': 'dh',   'न्': 'n',
    'प्': 'p',   'फ्': 'ph',   'ब्': 'b',    'भ्': 'bh',   'म्': 'm',
    'य्': 'y',   'र्': 'r',    'ल्': 'l',    'व्': 'v',    'श्': 'sh',
    'ष्': 'sh',  'स्': 's',    'ह्': 'h',
    
    # Nukta-modified half-consonants 
    'क़्': 'q',  'ख़्': 'kh',  'ग़्': 'gh',   'ज़्': 'z',    'फ़्': 'f',
    'ड़्': 'r',  'ढ़्': 'rh',
    
    # Special half-conjuncts
    'क्ष्': 'ksh',  'त्र्': 'tr',  'ज्ञ्': 'gy',
    
    # Special sequences for common half-letter combinations
    'न्न': 'nn', 'त्त': 'tt', 'त्त्': 'tt', 'द्द': 'dd', 'द्ध': 'ddh',
    'ड्ड': 'dd', 'ट्ट': 'tt', 'ट्ठ': 'tth', 'क्क': 'kk', 'ल्ल': 'll',
    'च्च': 'cch', 'ज्ज': 'jj', 'प्प': 'pp', 'श्श': 'shsh', 'स्स': 'ss',
    
    # Common half-form combinations
    'क्त': 'kt', 'क्य': 'ky', 'क्ल': 'kl', 'ग्य': 'gy', 'ग्ल': 'gl',
    'घ्य': 'ghy', 'घ्र': 'ghr', 'च्य': 'chy', 'ज्य': 'jy', 'ज्व': 'jv',
    'ट्य': 'ty', 'ट्र': 'tr', 'ठ्य': 'thy', 'ड्य': 'dy', 'ढ्य': 'dhy',
    'त्य': 'ty', 'त्र': 'tr', 'थ्य': 'thy', 'द्ध': 'ddh', 'द्भ': 'dbh',
    'न्त': 'nt', 'न्द': 'nd', 'न्ध': 'ndh', 'न्न': 'nn', 'प्य': 'py',
    'प्र': 'pr', 'प्ल': 'pl', 'ब्य': 'by', 'ब्र': 'br', 'भ्य': 'bhy',
    'म्य': 'my', 'व्य': 'vy', 'श्य': 'shy', 'श्र': 'shr', 'श्ल': 'shl',
    'स्त': 'st', 'स्थ': 'sth', 'स्प': 'sp', 'स्फ': 'sph', 'स्य': 'sy',
    'स्र': 'sr', 'स्व': 'sv', 'ह्न': 'hn', 'ह्म': 'hm', 'ह्य': 'hy',
    'ह्र': 'hr', 'ह्ल': 'hl', 'ह्व': 'hv',
    
    # Three-consonant combinations
    'क्त्र': 'ktr', 'न्त्र': 'ntr', 'स्त्र': 'str', 'ष्ट्र': 'shtr',
    'श्च': 'shch',
    
    # Less common combinations
    'दृ': 'dri', 'ध्र': 'dhr', 'ट्र': 'tr', 'द्र': 'dr', 'क्र': 'kr',
    'छ्र': 'chhr', 'ट्र': 'tr', 'ड्र': 'dr', 'ढ्र': 'dhr', 'फ्र': 'phr',
    'स्क': 'sk', 'स्ख': 'skh', 'स्त्र': 'str', 'ष्ट': 'sht', 'ष्ठ': 'shth',
}

# Marathi Unicode range: 0900-097F (shares with Hindi) and some specific chars
MARATHI_CHARS = {
    # Specific Marathi characters
    'ळ': 'la', 'ऴ': 'la',
    # The rest are same as Hindi
    **HINDI_CHARS
}

def preprocess_text(text):
    """
    Preprocess text for transliteration
    """
    # Replace zero-width spaces and other invisible characters
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def postprocess_text(text):
    """
    Postprocess the transliterated text to make it more readable and 
    fix the word-ending consonant issue. Also handles schwa deletion patterns.
    """
    # Fix double spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Extended consonant pattern for more accurate handling
    consonant_sounds = (
        r'kh|gh|ch|chh|jh|ny|th|dh|ph|bh|sh|ng|tr|gy|hr|hn|hm|hl|hv|hy|ll|'
        r'sn|sm|tn|bhr|ktr|ntr|str|shch|shtr|ksh|ddh|dbh|ndh|nn|sth|sph|'
        r'[kgcjtdnpbmyrlvshzfq]'
    )
    
    # Replace consonant+a at word boundaries with just the consonant
    # This pattern looks for consonant sounds followed by 'a' at word boundaries
    consonant_pattern = f'({consonant_sounds})a\\b'
    text = re.sub(consonant_pattern, r'\1', text)
    
    # Handle common schwa deletion in Hindi (selective)
    # Pattern: CaCa -> Ca (e.g., "namaste" instead of "namasta")
    text = re.sub(f'({consonant_sounds})a({consonant_sounds})a\\b', r'\1a\2', text)
    
    # Fix common compound pattern: CaCCa -> CaCaC (e.g., "dharma" instead of "dharama")
    text = re.sub(f'({consonant_sounds})a({consonant_sounds})({consonant_sounds})a\\b', r'\1a\2\3', text)
    
    # Fix repeating consonant clusters (handle gemination)
    geminate_pattern = r'([kgcjtdnpbmyrlvsh])a\1'
    text = re.sub(geminate_pattern, r'\1\1', text)
    
    # Handle specific common words that need schwa deletion
    common_words = {
        'namaskara': 'namaskar',
        'dhanyavaada': 'dhanyavaad',
        'shukriya': 'shukriya',
        'namaste': 'namaste'
    }
    
    for original, replacement in common_words.items():
        text = re.sub(r'\b' + original + r'\b', replacement, text)
    
    # Capitalize proper sentences
    text = re.sub(r'(^|[.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
    
    return text.strip()

def transliterate_text(text, char_map, consonants_no_a_map=None):  # Make the third param optional
    """
    Generic transliteration function using a simpler approach that prioritizes
    direct character mappings and handles word-ending consonants in post-processing
    
    Args:
        text: Input text
        char_map: Character mapping dictionary
        consonants_no_a_map: Not used in this implementation - word endings handled in postprocessing
        
    Returns:
        Transliterated text
    """
    try:
        text = preprocess_text(text)
        result = []
        
        i = 0
        while i < len(text):
            # Try to match longest sequences first (up to 5 chars, then descending)
            matched = False
            
            # Try 5, 4, 3, 2, then 1 character sequences
            # Increased to support longer consonant clusters and half-forms
            for seq_len in range(min(5, len(text) - i), 0, -1):
                sequence = text[i:i+seq_len]
                if sequence in char_map:
                    result.append(char_map[sequence])
                    i += seq_len
                    matched = True
                    break
            
            if not matched:
                # Check for virama/halant + consonant combinations for half-forms
                if i+1 < len(text) and text[i+1] == '्':
                    # Look ahead for virama + consonant combinations that may not be in the map
                    j = i + 2
                    next_vowel = j
                    # Find the next vowel or end of string
                    while next_vowel < len(text) and not is_vowel_or_matra(text[next_vowel]):
                        next_vowel += 1
                    
                    # If a multi-character consonant cluster is found
                    if j < next_vowel:
                        # Handle the consonant without the inherent 'a' vowel
                        if text[i] in char_map:
                            # Get the transliteration and remove trailing 'a' if present
                            cons_trans = char_map[text[i]]
                            if cons_trans.endswith('a'):
                                cons_trans = cons_trans[:-1]
                            result.append(cons_trans)
                            i = j  # Skip the virama
                            matched = True
                
                if not matched:
                    # Just append the character as is if no mapping exists
                    result.append(text[i])
                    i += 1
        
        # Join the result and apply post-processing
        transliterated = ''.join(result)
        return postprocess_text(transliterated)
    
    except Exception as e:
        print(f"Transliteration error: {str(e)}")
        if 'i' in locals() and i < len(text):
            print(f"Error occurred at character index {i}: '{text[i]}' (Unicode: {ord(text[i])})")
        if 'result' in locals():
            transliterated = ''.join(result)
            return postprocess_text(transliterated)
        return ""

def is_vowel_or_matra(char):
    """Helper function to check if a character is a vowel or vowel matra"""
    # Vowel range in Devanagari
    if '\u0904' <= char <= '\u0914':  # Independent vowels
        return True
    # Matra range
    if '\u093A' <= char <= '\u094F':  # Dependent vowel signs
        return True
    return False

def hindi2english(text):
    """
    Transliterate Hindi text to English
    
    Args:
        text: Input Hindi text string
    
    Returns:
        Transliterated English text
    """
    if not text:
        return ""
    
    result = transliterate_text(text, HINDI_CHARS)
    if result is None:
        raise ValueError("Failed to transliterate Hindi text")
    return result

def marathi2english(text):
    """
    Transliterate Marathi text to English
    
    Args:
        text: Input Marathi text string
    
    Returns:
        Transliterated English text
    """
    if not text:
        return ""
    
    result = transliterate_text(text, MARATHI_CHARS)
    if result is None:
        raise ValueError("Failed to transliterate Marathi text")
    return result
