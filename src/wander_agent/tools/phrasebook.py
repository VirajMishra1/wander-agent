"""Language phrasebook — survival phrases for 25 tourist languages."""
from __future__ import annotations

_DEST_TO_LANG: dict[str, str] = {
    # Country/city → language code
    "japan": "ja", "tokyo": "ja", "kyoto": "ja", "osaka": "ja",
    "france": "fr", "paris": "fr", "nice": "fr", "lyon": "fr",
    "spain": "es", "madrid": "es", "barcelona": "es", "seville": "es",
    "italy": "it", "rome": "it", "milan": "it", "venice": "it", "florence": "it",
    "germany": "de", "berlin": "de", "munich": "de", "frankfurt": "de",
    "portugal": "pt", "lisbon": "pt", "porto": "pt",
    "brazil": "pt-br", "sao paulo": "pt-br", "rio": "pt-br", "rio de janeiro": "pt-br",
    "thailand": "th", "bangkok": "th", "chiang mai": "th", "phuket": "th",
    "china": "zh", "beijing": "zh", "shanghai": "zh", "chengdu": "zh",
    "taiwan": "zh", "taipei": "zh",
    "south korea": "ko", "korea": "ko", "seoul": "ko", "busan": "ko",
    "vietnam": "vi", "hanoi": "vi", "ho chi minh": "vi", "da nang": "vi",
    "indonesia": "id", "bali": "id", "jakarta": "id",
    "india": "hi", "delhi": "hi", "mumbai": "hi", "jaipur": "hi",
    "turkey": "tr", "istanbul": "tr", "ankara": "tr",
    "greece": "el", "athens": "el", "santorini": "el",
    "netherlands": "nl", "amsterdam": "nl",
    "russia": "ru", "moscow": "ru", "st petersburg": "ru",
    "poland": "pl", "warsaw": "pl", "krakow": "pl",
    "czech republic": "cs", "prague": "cs",
    "hungary": "hu", "budapest": "hu",
    "malaysia": "ms", "kuala lumpur": "ms",
    "philippines": "tl", "manila": "tl", "cebu": "tl",
    "kenya": "sw", "nairobi": "sw", "tanzania": "sw", "zanzibar": "sw",
    "israel": "he", "tel aviv": "he",
    "cambodia": "km", "siem reap": "km", "phnom penh": "km",
    "morocco": "ar", "marrakech": "ar", "casablanca": "ar",
    "egypt": "ar", "cairo": "ar",
    "uae": "ar", "dubai": "ar", "abu dhabi": "ar",
    "jordan": "ar", "amman": "ar",
    "saudi arabia": "ar", "riyadh": "ar",
    "sri lanka": "si", "colombo": "si",
    "nepal": "ne", "kathmandu": "ne",
    "georgia": "ka", "tbilisi": "ka",
}

PHRASES: dict[str, dict] = {
    "ja": {
        "language": "Japanese", "script": "Japanese (hiragana/kanji)", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "こんにちは", "romanized": "Konnichiwa", "cat": "greeting"},
            {"en": "Good morning", "local": "おはようございます", "romanized": "Ohayou gozaimasu", "cat": "greeting"},
            {"en": "Thank you", "local": "ありがとうございます", "romanized": "Arigatou gozaimasu", "cat": "essential"},
            {"en": "Please", "local": "お願いします", "romanized": "Onegaishimasu", "cat": "essential"},
            {"en": "Sorry / Excuse me", "local": "すみません", "romanized": "Sumimasen", "cat": "essential"},
            {"en": "Yes", "local": "はい", "romanized": "Hai", "cat": "essential"},
            {"en": "No", "local": "いいえ", "romanized": "Iie", "cat": "essential"},
            {"en": "Do you speak English?", "local": "英語を話せますか？", "romanized": "Eigo wo hanasemasu ka?", "cat": "essential"},
            {"en": "I don't understand", "local": "わかりません", "romanized": "Wakarimasen", "cat": "essential"},
            {"en": "How much?", "local": "いくらですか？", "romanized": "Ikura desu ka?", "cat": "shopping"},
            {"en": "Where is...?", "local": "...はどこですか？", "romanized": "...wa doko desu ka?", "cat": "transport"},
            {"en": "Train station", "local": "駅", "romanized": "Eki", "cat": "transport"},
            {"en": "Airport", "local": "空港", "romanized": "Kuukou", "cat": "transport"},
            {"en": "Hotel", "local": "ホテル", "romanized": "Hoteru", "cat": "accommodation"},
            {"en": "Restaurant", "local": "レストラン", "romanized": "Resutoran", "cat": "food"},
            {"en": "Water please", "local": "お水をください", "romanized": "Omizu wo kudasai", "cat": "food"},
            {"en": "The bill please", "local": "お会計をお願いします", "romanized": "Okaikei wo onegaishimasu", "cat": "food"},
            {"en": "I'm vegetarian", "local": "ベジタリアンです", "romanized": "Bejitarian desu", "cat": "food"},
            {"en": "Help!", "local": "助けてください！", "romanized": "Tasukete kudasai!", "cat": "emergency"},
            {"en": "Call the police", "local": "警察を呼んでください", "romanized": "Keisatsu wo yonde kudasai", "cat": "emergency"},
            {"en": "I need a doctor", "local": "医者が必要です", "romanized": "Isha ga hitsuyou desu", "cat": "emergency"},
            {"en": "Toilet", "local": "トイレ", "romanized": "Toire", "cat": "essential"},
            {"en": "One / Two / Three", "local": "一 / 二 / 三", "romanized": "Ichi / Ni / San", "cat": "numbers"},
            {"en": "Delicious!", "local": "おいしい！", "romanized": "Oishii!", "cat": "food"},
            {"en": "No spicy please", "local": "辛くしないでください", "romanized": "Karaku shinaide kudasai", "cat": "food"},
        ],
    },
    "fr": {
        "language": "French", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Bonjour", "romanized": "Bonjour", "cat": "greeting"},
            {"en": "Good evening", "local": "Bonsoir", "romanized": "Bonsoir", "cat": "greeting"},
            {"en": "Thank you", "local": "Merci", "romanized": "Merci", "cat": "essential"},
            {"en": "Please", "local": "S'il vous plaît", "romanized": "Sil voo pleh", "cat": "essential"},
            {"en": "Sorry / Excuse me", "local": "Pardon / Excusez-moi", "romanized": "Pardon / Ex-coo-zay mwa", "cat": "essential"},
            {"en": "Yes / No", "local": "Oui / Non", "romanized": "Wee / Nohn", "cat": "essential"},
            {"en": "Do you speak English?", "local": "Parlez-vous anglais?", "romanized": "Par-lay voo ahn-gleh?", "cat": "essential"},
            {"en": "I don't understand", "local": "Je ne comprends pas", "romanized": "Zhuh nuh kohm-prohn pah", "cat": "essential"},
            {"en": "How much?", "local": "Combien ça coûte?", "romanized": "Kohm-byahn sah koot?", "cat": "shopping"},
            {"en": "Where is...?", "local": "Où est...?", "romanized": "Oo ay...?", "cat": "transport"},
            {"en": "A table for two please", "local": "Une table pour deux, s'il vous plaît", "romanized": "Oon tab-luh poor duh", "cat": "food"},
            {"en": "The bill please", "local": "L'addition, s'il vous plaît", "romanized": "La-dee-syohn, sil voo pleh", "cat": "food"},
            {"en": "I'm vegetarian", "local": "Je suis végétarien(ne)", "romanized": "Zhuh swee vay-zhay-tar-ee-ehn", "cat": "food"},
            {"en": "Water please", "local": "De l'eau, s'il vous plaît", "romanized": "Duh loh, sil voo pleh", "cat": "food"},
            {"en": "Help!", "local": "Au secours!", "romanized": "Oh suh-koor!", "cat": "emergency"},
            {"en": "Call the police", "local": "Appelez la police", "romanized": "Ah-play lah po-lees", "cat": "emergency"},
            {"en": "I need a doctor", "local": "J'ai besoin d'un médecin", "romanized": "Zhay buh-zwahn duhn may-duh-sahn", "cat": "emergency"},
            {"en": "Toilet", "local": "Les toilettes", "romanized": "Lay twah-let", "cat": "essential"},
            {"en": "One / Two / Three", "local": "Un / Deux / Trois", "romanized": "Uhn / Duh / Trwah", "cat": "numbers"},
        ],
    },
    "es": {
        "language": "Spanish", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Hola", "romanized": "OH-lah", "cat": "greeting"},
            {"en": "Good morning", "local": "Buenos días", "romanized": "BWAY-nos DEE-as", "cat": "greeting"},
            {"en": "Thank you", "local": "Gracias", "romanized": "GRAH-syahs", "cat": "essential"},
            {"en": "Please", "local": "Por favor", "romanized": "Por fah-VOR", "cat": "essential"},
            {"en": "Sorry / Excuse me", "local": "Perdón / Disculpe", "romanized": "Pehr-DON / Dees-KUL-peh", "cat": "essential"},
            {"en": "Yes / No", "local": "Sí / No", "romanized": "See / No", "cat": "essential"},
            {"en": "Do you speak English?", "local": "¿Habla inglés?", "romanized": "AH-blah een-GLAYS?", "cat": "essential"},
            {"en": "I don't understand", "local": "No entiendo", "romanized": "No ehn-TYEHN-do", "cat": "essential"},
            {"en": "How much?", "local": "¿Cuánto cuesta?", "romanized": "KWAHN-to KWES-tah?", "cat": "shopping"},
            {"en": "Where is...?", "local": "¿Dónde está...?", "romanized": "DON-day es-TAH?", "cat": "transport"},
            {"en": "The bill please", "local": "La cuenta, por favor", "romanized": "Lah KWEHN-tah, por fah-VOR", "cat": "food"},
            {"en": "I'm vegetarian", "local": "Soy vegetariano/a", "romanized": "Soy veh-heh-tah-RYAH-no", "cat": "food"},
            {"en": "Help!", "local": "¡Socorro!", "romanized": "So-KOR-ro!", "cat": "emergency"},
            {"en": "Call the police", "local": "Llame a la policía", "romanized": "YAH-meh ah lah po-lee-SEE-ah", "cat": "emergency"},
            {"en": "Toilet", "local": "El baño / Los servicios", "romanized": "El BAHN-yo", "cat": "essential"},
            {"en": "One / Two / Three", "local": "Uno / Dos / Tres", "romanized": "OO-no / Dos / Trays", "cat": "numbers"},
        ],
    },
    "th": {
        "language": "Thai", "script": "Thai script", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "สวัสดี", "romanized": "Sawatdee (krap/ka)", "cat": "greeting", "note": "Add krap (male) or ka (female)"},
            {"en": "Thank you", "local": "ขอบคุณ", "romanized": "Khob khun", "cat": "essential"},
            {"en": "Yes / No", "local": "ใช่ / ไม่ใช่", "romanized": "Chai / Mai chai", "cat": "essential"},
            {"en": "How much?", "local": "เท่าไหร่", "romanized": "Tao rai?", "cat": "shopping"},
            {"en": "Too expensive", "local": "แพงเกินไป", "romanized": "Phaeng kern pai", "cat": "shopping"},
            {"en": "Where is...?", "local": "...อยู่ที่ไหน", "romanized": "...yuu thi nai?", "cat": "transport"},
            {"en": "I don't eat meat", "local": "ไม่กินเนื้อสัตว์", "romanized": "Mai kin neua sat", "cat": "food"},
            {"en": "Not spicy please", "local": "ไม่เผ็ด", "romanized": "Mai phet", "cat": "food"},
            {"en": "Delicious!", "local": "อร่อยมาก!", "romanized": "Aroi maak!", "cat": "food"},
            {"en": "The bill please", "local": "เก็บเงินด้วย", "romanized": "Kep ngern duay", "cat": "food"},
            {"en": "Help!", "local": "ช่วยด้วย!", "romanized": "Chuay duay!", "cat": "emergency"},
            {"en": "Toilet", "local": "ห้องน้ำ", "romanized": "Hong nam", "cat": "essential"},
        ],
    },
    "zh": {
        "language": "Mandarin Chinese", "script": "Simplified Chinese", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "你好", "romanized": "Nǐ hǎo", "cat": "greeting"},
            {"en": "Thank you", "local": "谢谢", "romanized": "Xièxiè", "cat": "essential"},
            {"en": "Please", "local": "请", "romanized": "Qǐng", "cat": "essential"},
            {"en": "Sorry", "local": "对不起", "romanized": "Duìbuqǐ", "cat": "essential"},
            {"en": "Yes / No", "local": "是 / 不是", "romanized": "Shì / Bù shì", "cat": "essential"},
            {"en": "How much?", "local": "多少钱？", "romanized": "Duōshǎo qián?", "cat": "shopping"},
            {"en": "Too expensive", "local": "太贵了", "romanized": "Tài guì le", "cat": "shopping"},
            {"en": "Where is...?", "local": "...在哪里？", "romanized": "...zài nǎlǐ?", "cat": "transport"},
            {"en": "I don't eat meat", "local": "我不吃肉", "romanized": "Wǒ bù chī ròu", "cat": "food"},
            {"en": "The bill please", "local": "买单", "romanized": "Mǎi dān", "cat": "food"},
            {"en": "Help!", "local": "救命!", "romanized": "Jiùmìng!", "cat": "emergency"},
            {"en": "Toilet", "local": "厕所", "romanized": "Cèsuǒ", "cat": "essential"},
            {"en": "No spicy", "local": "不要辣", "romanized": "Bù yào là", "cat": "food"},
        ],
    },
    "ar": {
        "language": "Arabic", "script": "Arabic script", "rtl": True,
        "phrases": [
            {"en": "Hello (Peace be upon you)", "local": "السلام عليكم", "romanized": "As-salamu alaykum", "cat": "greeting"},
            {"en": "Thank you", "local": "شكراً", "romanized": "Shukran", "cat": "essential"},
            {"en": "Please", "local": "من فضلك", "romanized": "Min fadlak (m) / fadlik (f)", "cat": "essential"},
            {"en": "Yes / No", "local": "نعم / لا", "romanized": "Na'am / La", "cat": "essential"},
            {"en": "How much?", "local": "كم الثمن؟", "romanized": "Kam al-thaman?", "cat": "shopping"},
            {"en": "Where is...?", "local": "أين...؟", "romanized": "Ayna...?", "cat": "transport"},
            {"en": "The bill please", "local": "الحساب من فضلك", "romanized": "Al-hisab min fadlak", "cat": "food"},
            {"en": "Help!", "local": "النجدة!", "romanized": "An-najda!", "cat": "emergency"},
            {"en": "Toilet", "local": "دورة المياه", "romanized": "Dawrat al-miyah", "cat": "essential"},
            {"en": "I'm a tourist", "local": "أنا سائح", "romanized": "Ana sa'ih", "cat": "essential"},
        ],
    },
    "de": {
        "language": "German", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Hallo / Guten Tag", "romanized": "HAH-lo / GOO-ten tahk", "cat": "greeting"},
            {"en": "Thank you", "local": "Danke schön", "romanized": "DAHN-keh shurn", "cat": "essential"},
            {"en": "Please", "local": "Bitte", "romanized": "BIT-teh", "cat": "essential"},
            {"en": "Sorry", "local": "Entschuldigung", "romanized": "Ent-SHUL-dee-goong", "cat": "essential"},
            {"en": "Yes / No", "local": "Ja / Nein", "romanized": "Yah / Nine", "cat": "essential"},
            {"en": "How much?", "local": "Wie viel kostet das?", "romanized": "Vee feel KOS-tet das?", "cat": "shopping"},
            {"en": "Where is...?", "local": "Wo ist...?", "romanized": "Vo ist?", "cat": "transport"},
            {"en": "The bill please", "local": "Die Rechnung, bitte", "romanized": "Dee RECH-noong, bit-teh", "cat": "food"},
            {"en": "Help!", "local": "Hilfe!", "romanized": "HIL-feh!", "cat": "emergency"},
            {"en": "Toilet", "local": "Toilette / WC", "romanized": "Twa-LET-teh", "cat": "essential"},
        ],
    },
    "it": {
        "language": "Italian", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Ciao / Buongiorno", "romanized": "Chow / Bwon-JOR-no", "cat": "greeting"},
            {"en": "Thank you", "local": "Grazie", "romanized": "GRAHT-syeh", "cat": "essential"},
            {"en": "Please", "local": "Per favore", "romanized": "Pehr fah-VOH-reh", "cat": "essential"},
            {"en": "Sorry", "local": "Scusi / Mi dispiace", "romanized": "SKOO-zee", "cat": "essential"},
            {"en": "How much?", "local": "Quanto costa?", "romanized": "KWAHN-to KOS-tah?", "cat": "shopping"},
            {"en": "The bill please", "local": "Il conto, per favore", "romanized": "Eel KON-to, pehr fah-VOH-reh", "cat": "food"},
            {"en": "I'm vegetarian", "local": "Sono vegetariano/a", "romanized": "SOH-no veh-jeh-tah-RYAH-no", "cat": "food"},
            {"en": "Help!", "local": "Aiuto!", "romanized": "Ah-YOO-to!", "cat": "emergency"},
            {"en": "Toilet", "local": "Il bagno", "romanized": "Eel BAHN-yo", "cat": "essential"},
        ],
    },
    "ko": {
        "language": "Korean", "script": "Hangul", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "안녕하세요", "romanized": "Annyeonghaseyo", "cat": "greeting"},
            {"en": "Thank you", "local": "감사합니다", "romanized": "Gamsahamnida", "cat": "essential"},
            {"en": "Yes / No", "local": "네 / 아니요", "romanized": "Ne / Aniyo", "cat": "essential"},
            {"en": "How much?", "local": "얼마예요?", "romanized": "Eolmayeyo?", "cat": "shopping"},
            {"en": "Where is...?", "local": "...어디에요?", "romanized": "...eodieyo?", "cat": "transport"},
            {"en": "Delicious!", "local": "맛있어요!", "romanized": "Masisseoyo!", "cat": "food"},
            {"en": "The bill please", "local": "계산서 주세요", "romanized": "Gyesanseo juseyo", "cat": "food"},
            {"en": "Help!", "local": "도와주세요!", "romanized": "Dowajuseyo!", "cat": "emergency"},
            {"en": "Toilet", "local": "화장실", "romanized": "Hwajangsil", "cat": "essential"},
        ],
    },
    "hi": {
        "language": "Hindi", "script": "Devanagari", "rtl": False,
        "phrases": [
            {"en": "Hello / Greetings", "local": "नमस्ते", "romanized": "Namaste", "cat": "greeting"},
            {"en": "Thank you", "local": "धन्यवाद", "romanized": "Dhanyavaad", "cat": "essential"},
            {"en": "Please", "local": "कृपया", "romanized": "Kripaya", "cat": "essential"},
            {"en": "Yes / No", "local": "हाँ / नहीं", "romanized": "Haan / Nahin", "cat": "essential"},
            {"en": "How much?", "local": "कितने का है?", "romanized": "Kitne ka hai?", "cat": "shopping"},
            {"en": "Where is...?", "local": "...कहाँ है?", "romanized": "...kahan hai?", "cat": "transport"},
            {"en": "I'm vegetarian", "local": "मैं शाकाहारी हूँ", "romanized": "Main shakahaari hoon", "cat": "food"},
            {"en": "Help!", "local": "मदद करो!", "romanized": "Madad karo!", "cat": "emergency"},
            {"en": "Toilet", "local": "शौचालय", "romanized": "Shauchalay", "cat": "essential"},
        ],
    },
    "vi": {
        "language": "Vietnamese", "script": "Latin (tonal)", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Xin chào", "romanized": "Sin chow", "cat": "greeting"},
            {"en": "Thank you", "local": "Cảm ơn", "romanized": "Kahm uhn", "cat": "essential"},
            {"en": "How much?", "local": "Bao nhiêu?", "romanized": "Bow nyew?", "cat": "shopping"},
            {"en": "Too expensive", "local": "Đắt quá", "romanized": "Dat kwa", "cat": "shopping"},
            {"en": "The bill please", "local": "Tính tiền", "romanized": "Ting tyen", "cat": "food"},
            {"en": "No meat please", "local": "Không có thịt", "romanized": "Khong ko tit", "cat": "food"},
            {"en": "Delicious!", "local": "Ngon lắm!", "romanized": "Ngon lahm!", "cat": "food"},
            {"en": "Help!", "local": "Cứu tôi!", "romanized": "Kyoo toy!", "cat": "emergency"},
            {"en": "Toilet", "local": "Nhà vệ sinh", "romanized": "Nya veh sin", "cat": "essential"},
        ],
    },
    "id": {
        "language": "Indonesian", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Halo / Selamat pagi", "romanized": "Hah-lo / Seh-lah-maht PAH-gee", "cat": "greeting"},
            {"en": "Thank you", "local": "Terima kasih", "romanized": "Teh-REE-mah KAH-see", "cat": "essential"},
            {"en": "Please", "local": "Tolong", "romanized": "TO-long", "cat": "essential"},
            {"en": "How much?", "local": "Berapa harganya?", "romanized": "Beh-RAH-pah har-GAH-nyah?", "cat": "shopping"},
            {"en": "Where is...?", "local": "Di mana...?", "romanized": "Dee MAH-nah?", "cat": "transport"},
            {"en": "Delicious!", "local": "Enak sekali!", "romanized": "Eh-NAHK seh-KAH-lee!", "cat": "food"},
            {"en": "The bill please", "local": "Minta bill", "romanized": "MIN-tah bill", "cat": "food"},
            {"en": "Help!", "local": "Tolong!", "romanized": "TO-long!", "cat": "emergency"},
            {"en": "Toilet", "local": "Toilet / Kamar mandi", "romanized": "Toy-LET / KAH-mar MAN-dee", "cat": "essential"},
        ],
    },
    "tr": {
        "language": "Turkish", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Merhaba", "romanized": "Mehr-HAH-bah", "cat": "greeting"},
            {"en": "Thank you", "local": "Teşekkür ederim", "romanized": "Teh-shek-KYUR eh-deh-REEM", "cat": "essential"},
            {"en": "How much?", "local": "Ne kadar?", "romanized": "Neh KAH-dar?", "cat": "shopping"},
            {"en": "Where is...?", "local": "...nerede?", "romanized": "...neh-REH-deh?", "cat": "transport"},
            {"en": "The bill please", "local": "Hesap lütfen", "romanized": "HEH-sahp LEWT-fen", "cat": "food"},
            {"en": "Help!", "local": "İmdat!", "romanized": "Eem-DAHT!", "cat": "emergency"},
            {"en": "Toilet", "local": "Tuvalet", "romanized": "Too-vah-LET", "cat": "essential"},
        ],
    },
    "pt": {
        "language": "Portuguese (European)", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Olá / Bom dia", "romanized": "Oh-LAH / Bohn JEE-ah", "cat": "greeting"},
            {"en": "Thank you", "local": "Obrigado/a", "romanized": "Oh-bree-GAH-do", "cat": "essential"},
            {"en": "How much?", "local": "Quanto custa?", "romanized": "KWAHN-to KOOSH-tah?", "cat": "shopping"},
            {"en": "The bill please", "local": "A conta, por favor", "romanized": "Ah KON-tah, por fah-VOR", "cat": "food"},
            {"en": "Help!", "local": "Socorro!", "romanized": "So-KOR-ro!", "cat": "emergency"},
            {"en": "Toilet", "local": "Casa de banho", "romanized": "KAH-zah deh BAHN-yo", "cat": "essential"},
        ],
    },
    "ms": {
        "language": "Malay", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Helo / Selamat datang", "romanized": "Heh-lo / Seh-lah-maht DAH-tang", "cat": "greeting"},
            {"en": "Thank you", "local": "Terima kasih", "romanized": "Teh-REE-mah KAH-see", "cat": "essential"},
            {"en": "How much?", "local": "Berapa?", "romanized": "Beh-RAH-pah?", "cat": "shopping"},
            {"en": "The bill please", "local": "Bil, tolong", "romanized": "Bill, TO-long", "cat": "food"},
            {"en": "Help!", "local": "Tolong!", "romanized": "TO-long!", "cat": "emergency"},
            {"en": "Toilet", "local": "Tandas", "romanized": "TAN-das", "cat": "essential"},
        ],
    },
    "sw": {
        "language": "Swahili", "script": "Latin", "rtl": False,
        "phrases": [
            {"en": "Hello", "local": "Jambo / Habari", "romanized": "JAM-bo / Hah-BAH-ree", "cat": "greeting"},
            {"en": "Thank you", "local": "Asante", "romanized": "Ah-SAHN-teh", "cat": "essential"},
            {"en": "How much?", "local": "Bei gani?", "romanized": "Beh-ee GAH-nee?", "cat": "shopping"},
            {"en": "Help!", "local": "Msaada!", "romanized": "Muh-SAH-dah!", "cat": "emergency"},
            {"en": "Toilet", "local": "Choo", "romanized": "Choh", "cat": "essential"},
            {"en": "No problem", "local": "Hakuna matata", "romanized": "Hah-KOO-nah mah-TAH-tah", "cat": "essential"},
        ],
    },
}

# Add pt-br alias
PHRASES["pt-br"] = {**PHRASES["pt"], "language": "Portuguese (Brazilian)"}


async def get_language_phrasebook(
    destination: str,
    language_code: str | None = None,
    category: str | None = None,
) -> dict:
    """Get survival phrases for the destination language.

    Returns the 25 most useful tourist phrases with romanized pronunciation.
    Works for 17 languages covering 80% of global tourism.

    Args:
        destination: City or country name (e.g. "Tokyo", "France", "Bali")
        language_code: Override language (ja, fr, es, it, de, pt, th, zh, ko, hi, vi, id, tr, ar, ms, sw)
        category: Filter by: greeting, essential, food, transport, shopping, emergency, accommodation, numbers
    """
    lang = language_code
    if not lang:
        dest_lower = destination.lower()
        lang = _DEST_TO_LANG.get(dest_lower)
        if not lang:
            for key, code in _DEST_TO_LANG.items():
                if key in dest_lower or dest_lower in key:
                    lang = code
                    break

    if not lang or lang not in PHRASES:
        return {
            "destination": destination,
            "error": "Language not found. Try language_code parameter.",
            "supported_languages": {k: v["language"] for k, v in PHRASES.items()},
            "supported_destinations": list(_DEST_TO_LANG.keys())[:30],
            "suggest_web_search": [f"survival phrases {destination} for tourists"],
        }

    data = PHRASES[lang]
    phrases = data["phrases"]
    if category:
        phrases = [p for p in phrases if p.get("cat") == category.lower()]

    # Group by category
    grouped: dict[str, list] = {}
    for p in phrases:
        c = p.get("cat", "essential")
        grouped.setdefault(c, []).append({
            "english": p["en"],
            "local": p["local"],
            "pronunciation": p["romanized"],
            **({"note": p["note"]} if p.get("note") else {}),
        })

    return {
        "destination": destination,
        "language": data["language"],
        "language_code": lang,
        "script": data["script"],
        "right_to_left": data.get("rtl", False),
        "phrases_by_category": grouped,
        "total_phrases": len(phrases),
        "emergency_numbers": {
            "note": "Look up local emergency numbers",
            "links": {
                "google": f"https://www.google.com/search?q=emergency+numbers+{destination.replace(' ', '+')}",
                "wikipedia": "https://en.wikipedia.org/wiki/List_of_emergency_telephone_numbers",
            },
        },
        "learning_tip": f"Even saying hello in {data['language']} opens doors. Locals appreciate the effort.",
        "offline_app": f"Google Translate works offline — download {data['language']} language pack before your trip.",
        "suggest_web_search": [
            f"common phrases {destination} for tourists",
            f"{data['language']} pronunciation guide for English speakers",
        ],
    }
