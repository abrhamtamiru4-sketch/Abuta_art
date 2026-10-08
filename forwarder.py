import re, json, copy, asyncio, logging, time, sys, random, os, sqlite3, hashlib, io
from datetime import datetime, timedelta
from collections import defaultdict
from telethon import TelegramClient, events, functions, types, utils
from telethon.errors import (
    FloodWaitError, ReactionsTooManyError, ChatAdminRequiredError,
    MessageNotModifiedError, MessageIdInvalidError, PeerIdInvalidError,
    SlowModeWaitError, UserBannedInChannelError, ChannelPrivateError,
    ChatWriteForbiddenError, MediaCaptionTooLongError, FilePartMissingError,
    UserDeactivatedBanError, AuthKeyUnregisteredError,
)

# ╔══════════════════════════════════════════════════════════════╗
# ║     888 SPORT FORWARDER v7 — EXTREME EDITION               ║
# ║     Prepared by Abuta                                      ║
# ╚══════════════════════════════════════════════════════════════╝

VERSION = "7.0.0"
BUILD   = "2025-EXTREME"

api_id   = 37817947
api_hash = "dfef5c793eae6286dd44a93ebf0c79e5"
phone    = "+251925244562"

PIPELINES = [
    ([-1001764387820, -1001113308505], [-1004331053652]),
    ([-1001915363651],                 [-1004427584149]),
]

# ── CORE FLAGS ────────────────────────────────────────────────
REACTIONS_ENABLED   = True
FORWARD_EDITS       = True
DELETE_ON_DELETE    = True
PIN_SYNC            = True
SILENT_FORWARD      = True
BACKFILL_ON_START   = False
BACKFILL_LIMIT      = 50
AUTO_RECONNECT      = True
DEDUP_WINDOW_SECS   = 60

RATE_LIMIT          = 0.8
REACTION_DEBOUNCE   = 3
FLOOD_BACKOFF_EXTRA = 2

MAX_CAPTION_CHARS   = 1024
MAX_MESSAGE_CHARS   = 4096
MAX_SEND_RETRIES    = 4
TRUNCATE_SUFFIX     = " …"

INCLUDE_KEYWORDS    = []
EXCLUDE_KEYWORDS    = []
MEDIA_FILTER        = []
REPLACEMENTS        = {}
TRANSLATION_TABLE   = {}
TRANSLATE_PREMIUM   = True

# ── BRAND ─────────────────────────────────────────────────────
BRAND_NAME    = "888 Sport"
BRAND_FOOTER  = f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n💎 {BRAND_NAME}  |  Stay Inspired ✨"

HEADER_STYLES = [
    f"╔══════════════════════╗\n║  🔥  {BRAND_NAME.upper()}  🔥  ║\n╚══════════════════════╝",
    f"┌──────────────────────────┐\n│  ✨  {BRAND_NAME}  ✨  │\n└──────────────────────────┘",
    f"▓▓▒▒░░ {BRAND_NAME.upper()} ░░▒▒▓▓",
    "⚡️⚡️  8 8 8  S P O R T  ⚡️⚡️",
    f"🏆━━━━ {BRAND_NAME.upper()} ━━━━🏆",
    f"『 {BRAND_NAME} 』✦ Official",
    f"◈━━━━◈ {BRAND_NAME.upper()} ◈━━━━◈",
    f"🎯 ═══ {BRAND_NAME.upper()} ═══ 🎯",
    f"⚽ {BRAND_NAME} — Live Sports Hub ⚽",
]

_msg_arm = {}

# ── BOOST ─────────────────────────────────────────────────────
BOOST_ENABLED    = True
BOOST_SESSIONS   = ["boost1","boost2","boost3","boost4","boost5"]
BOOST_BATCH      = 5
BOOST_DELAY      = 5
BOOST_DELAY_PER  = 2.0
FILL_REACTIONS   = ["🔥","👍","❤️","🎉","😮","🏆","⚡️","💪","👏","😍","🙌"]

BOOST_TRY_REACTION      = True
BOOST_TRY_COMMENT       = True
BOOST_TRY_VIEW          = True
BOOST_TRY_FORWARD       = True
BOOST_TRY_VOTE          = True
BOOST_TRY_CHANNEL_BOOST = True

# ── IMAGE SENDER ───────────────────────────────────────────────
# When the source has no media but you want to attach a default image,
# place any .jpg/.png file here. Leave empty ("") to disable.
DEFAULT_IMAGE_PATH = ""   # e.g. "assets/logo.jpg"

# If True, attach DEFAULT_IMAGE_PATH to text-only messages
ATTACH_DEFAULT_IMAGE = False

# ── NEW: CAPTION FONT STYLE ───────────────────────────────────
# Choices: "bold", "italic", "mono", "normal"
TEXT_FONT_STYLE = "bold"

# ── NEW: TIME DISPLAY ─────────────────────────────────────────
# Time is shown in small format: "· 14:35" rather than full date+time
TIME_COMPACT = True      # True = "· HH:MM", False = full date+time

# ── NEW: AUTO IMAGE CAPTION ───────────────────────────────────
# Replaces "[unnamed]" / empty alt text in media messages
AUTO_CAPTION_TEMPLATE = "📸 {brand} — Sports Update"

# ── NEW: SMART SCHEDULER ──────────────────────────────────────
SMART_SCHEDULE_ENABLED = True
SMART_SCHEDULE_TARGETS = []   # fill with target IDs or leave [] for all
SMART_SCHEDULE_SLOTS   = {    # hour → message template
    7:  "☀️ *Morning Kick-off!*\nStart your day with the best sports coverage.\n\n💎 {brand}",
    10: "📊 *Mid-Morning Update*\nCheck today's fixtures & predictions.\n\n🏆 {brand}",
    13: "⚽ *Lunch Break Scores!*\nLatest results — don't miss a goal!\n\n🔥 {brand}",
    16: "🕓 *Afternoon Sports Flash!*\nLive now — tune in!\n\n⚡️ {brand}",
    19: "🌆 *Evening Highlights*\nBest moments of the day.\n\n💎 {brand}",
    22: "🌙 *Night Wrap-Up*\nFull results, top scorers & more.\n\n🏅 {brand}",
}

# ── NEW: LINK PREVIEW CONTROL ─────────────────────────────────
LINK_PREVIEW_ENABLED = False   # set True to show Telegram link previews

# ── NEW: MEDIA FALLBACK CAPTION ───────────────────────────────
# Caption shown when a forwarded media has no text at all
MEDIA_NO_CAPTION_TEXT = "📢 Latest update from {brand}"

# ── NEW: MESSAGE COUNTER ──────────────────────────────────────
MSG_COUNTER_ENABLED = True
_msg_counter = 0

# ── NEW: DUPLICATE MEDIA HASH WINDOW ─────────────────────────
DEDUP_MEDIA_ENABLED  = True
_media_hashes        = {}
MEDIA_DEDUP_WINDOW   = 3600   # seconds

# ── NEW: AUTO THREAD REPLY ────────────────────────────────────
AUTO_THREAD_REPLY_ENABLED = False
AUTO_THREAD_REPLY_MSGS    = [
    "🔥 What do you think? Drop your reaction below!",
    "⚽ Stay tuned for more updates!",
    "💎 Share with your friends!",
    "🏆 Follow us for live scores!",
]
AUTO_THREAD_DELAY = 5   # seconds after message send

# ── NEW: CONTENT ANALYTICS ────────────────────────────────────
ANALYTICS_ENABLED    = True
ANALYTICS_FILE       = "analytics.csv"
ANALYTICS_FIELDS     = ["ts","src_chat","msg_id","targets","has_media","text_len","hashtags"]

# ── NEW: HEARTBEAT ────────────────────────────────────────────
HEARTBEAT_ENABLED    = True
HEARTBEAT_INTERVAL   = 1800   # 30 min
HEARTBEAT_LOG_ONLY   = True   # False = also send to Saved Messages

# ── NEW: MESSAGE ENRICHMENT ───────────────────────────────────
ENRICH_ENABLED          = True
ENRICH_LIVE_SCORES      = True    # detect "live","score","vs" and add 🔴 LIVE tag
ENRICH_MATCH_EMOJI      = True    # add sport-specific emoji based on keywords
ENRICH_SPORT_MAP        = {
    "football":  "⚽", "soccer": "⚽", "goal": "⚽",
    "basketball":"🏀", "nba":    "🏀",
    "tennis":    "🎾", "wimbledon":"🎾",
    "boxing":    "🥊", "mma":    "🥊", "ufc":"🥊",
    "cricket":   "🏏",
    "rugby":     "🏉",
    "golf":      "⛳",
    "formula":   "🏎️", "f1":"🏎️",
    "baseball":  "⚾",
    "hockey":    "🏒", "nhl":"🏒",
    "cycling":   "🚴",
    "athletics": "🏃",
}

# ── MOD ENGINE ────────────────────────────────────────────────
MOD_ENABLED          = True
MOD_WELCOME          = True
MOD_WELCOME_TARGETS  = []
MOD_WELCOME_MSGS     = [
    "👋 Welcome to {name}! 🏆 Stay tuned for the latest sports updates.",
    "🔥 Hey {name}! Great to have you here. Enjoy the content! ⚡️",
    "⚽ Welcome {name}! You just joined the best sports channel. 🎉",
    "🏅 {name} just joined! Welcome aboard. 💎",
    "🎯 Welcome {name}! Prepare for live scores, highlights & more. 🔥",
]
MOD_SCHEDULER        = True
MOD_SCHEDULE_TARGETS = []
MOD_SCHEDULE_HOURS   = [8, 12, 18, 21]
MOD_SCHEDULE_MSGS    = [
    "📢 *Don't miss today's top sports highlights!*\n🔔 Share with friends & grow our community!\n\n🏆 {brand} — Stay Inspired ✨",
    "⚡️ *Live scores. Real-time updates. Pure sport.*\n📲 Invite your friends to join us!\n\n💎 {brand}",
    "🔥 *The best sports channel on Telegram!*\n👥 Help us grow — share this channel!\n\n🏅 {brand} — Stay Inspired ✨",
    "🌍 *Sports fans unite!*\n📣 Forward this channel to every fan you know!\n\n⚽ {brand}",
    "🎯 *Goals. Highlights. Analysis.*\n🚀 Share & invite — let's grow together!\n\n🏆 {brand} — Stay Inspired ✨",
]
MOD_SHOUTOUT         = False
MOD_SHOUTOUT_TARGETS = []
MOD_SHOUTOUT_CHANNELS= []
MOD_SHOUTOUT_INTERVAL= 86400
MOD_MILESTONE        = True
MOD_MILESTONE_TARGETS= []
MOD_MILESTONES       = [100,500,1000,5000,10000,50000,100000]
MOD_MILESTONE_MSGS   = [
    "🎉 *We just hit {count} members!*\nThank you all for joining {brand}!\n🔥 Keep sharing — more milestones ahead! 🏆",
    "🏅 *{count} strong!* The {brand} community keeps growing. You're all legends! 💪",
]
MOD_AUTO_PIN         = False
MOD_AUTO_PIN_TARGETS = []
MOD_ANTISPAM         = True
MOD_ANTISPAM_TARGETS = []
MOD_MAX_MSG_PER_MIN  = 5
MOD_MUTE_DURATION    = 300
MOD_DAILY_DIGEST     = True
MOD_DIGEST_TARGETS   = []
MOD_DIGEST_HOUR      = 23

# ── GROWTH SYSTEMS ────────────────────────────────────────────
GROWTH_HASHTAGS      = True
GROWTH_HASHTAG_POOL  = [
    "#football","#soccer","#sports","#goals","#highlights",
    "#UEFA","#FIFA","#PremierLeague","#LaLiga","#SerieA",
    "#sport","#betting","#888sport","#live","#score",
    "#championsleague","#epl","#bundesliga","#ligue1","#mls",
]
GROWTH_HASHTAG_COUNT = 5
GROWTH_FINGERPRINT   = True
GROWTH_TRACKER       = True
GROWTH_TRACKER_FILE  = "growth.csv"
GROWTH_TRACKER_INTERVAL = 3600
GROWTH_PEAK_HOURS    = True
GROWTH_PEAK_WINDOW   = [7,8,9,12,13,17,18,19,20,21,22]
GROWTH_REPOST_VIRAL  = False
GROWTH_VIRAL_THRESH  = 50
GROWTH_VIRAL_INTERVAL= 43200
GROWTH_BULK_FORWARD  = False
GROWTH_BULK_LIMIT    = 20
GROWTH_BULK_DELAY    = 10
GROWTH_LANG_TAG      = True
GROWTH_LANG          = "EN"
GROWTH_NOTIFY_ADMIN  = False
GROWTH_ADMIN_ID      = 0

# ── EXTREME SYSTEMS ───────────────────────────────────────────
HOT_CONFIG_FILE      = "hotconfig.json"
WATCHDOG_TIMEOUT     = 3600
MEDIA_CACHE_MAX      = 30

# ══════════════════════════════════════════════════════════════
ALL_SOURCES = list({s for srcs, _ in PIPELINES for s in srcs})
ALL_TARGETS = list({t for _, tgts in PIPELINES for t in tgts})

def targets_for(chat_id):
    for srcs, tgts in PIPELINES:
        if chat_id in srcs: return tgts
    return []

# ── LOGGING ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.FileHandler("forwarder.log", encoding="utf-8"),
              logging.StreamHandler(sys.stdout)])
log = logging.getLogger("forwarder")
for _n in ("telethon.network","telethon.client.updates","telethon.extensions.messagepacker"):
    logging.getLogger(_n).setLevel(logging.WARNING)

client = TelegramClient("session", api_id, api_hash, receive_updates=True)

# ── STATE ─────────────────────────────────────────────────────
BOOST_ACCOUNTS   = {}
DEAD_BOOSTERS    = set()
BOOST_METHOD     = {}
LINKED_GROUP     = {}
DEAD_TARGETS     = set()
REACTION_CAPABLE = {}
STATS            = defaultdict(int)
STATS_START      = datetime.now()
_seen_times      = {}
_last_activity   = [time.monotonic()]
_paused          = False

try:
    with open("mapping.json", encoding="utf-8") as f: MAPPING = json.load(f)
except (FileNotFoundError, json.JSONDecodeError): MAPPING = {}

def save_mapping():
    with open("mapping.json", "w", encoding="utf-8") as f:
        json.dump(MAPPING, f, ensure_ascii=False)

def key(c, m): return f"{c}:{m}"

def already_seen(k):
    if k in _seen_times and time.time() - _seen_times[k] < DEDUP_WINDOW_SECS: return True
    return k in MAPPING

def mark_seen(k):
    _seen_times[k] = time.time()
    _last_activity[0] = time.monotonic()

def touch(): _last_activity[0] = time.monotonic()

# ── NEW: FONT STYLE HELPERS ───────────────────────────────────
_BOLD_MAP = {
    'a':'𝗮','b':'𝗯','c':'𝗰','d':'𝗱','e':'𝗲','f':'𝗳','g':'𝗴','h':'𝗵',
    'i':'𝗶','j':'𝗷','k':'𝗸','l':'𝗹','m':'𝗺','n':'𝗻','o':'𝗼','p':'𝗽',
    'q':'𝗾','r':'𝗿','s':'𝘀','t':'𝘁','u':'𝘂','v':'𝘃','w':'𝘄','x':'𝘅',
    'y':'𝘆','z':'𝘇',
    'A':'𝗔','B':'𝗕','C':'𝗖','D':'𝗗','E':'𝗘','F':'𝗙','G':'𝗚','H':'𝗛',
    'I':'𝗜','J':'𝗝','K':'𝗞','L':'𝗟','M':'𝗠','N':'𝗡','O':'𝗢','P':'𝗣',
    'Q':'𝗤','R':'𝗥','S':'𝗦','T':'𝗧','U':'𝗨','V':'𝗩','W':'𝗪','X':'𝗫',
    'Y':'𝗬','Z':'𝗭',
    '0':'𝟬','1':'𝟭','2':'𝟮','3':'𝟯','4':'𝟰','5':'𝟱','6':'𝟲','7':'𝟳',
    '8':'𝟴','9':'𝟵',
}
_ITALIC_MAP = {
    'a':'𝘢','b':'𝘣','c':'𝘤','d':'𝘥','e':'𝘦','f':'𝘧','g':'𝘨','h':'𝘩',
    'i':'𝘪','j':'𝘫','k':'𝘬','l':'𝘭','m':'𝘮','n':'𝘯','o':'𝘰','p':'𝘱',
    'q':'𝘲','r':'𝘳','s':'𝘴','t':'𝘵','u':'𝘶','v':'𝘷','w':'𝘸','x':'𝘹',
    'y':'𝘺','z':'𝘻',
    'A':'𝘈','B':'𝘉','C':'𝘊','D':'𝘋','E':'𝘌','F':'𝘍','G':'𝘎','H':'𝘏',
    'I':'𝘐','J':'𝘑','K':'𝘊','L':'𝘓','M':'𝘔','N':'𝘕','O':'𝘖','P':'𝘗',
    'Q':'𝘘','R':'𝘙','S':'𝘚','T':'𝘛','U':'𝘜','V':'𝘝','W':'𝘞','X':'𝘟',
    'Y':'𝘠','Z':'𝘡',
}
_MONO_MAP = {
    'a':'𝚊','b':'𝚋','c':'𝚌','d':'𝚍','e':'𝚎','f':'𝚏','g':'𝚐','h':'𝚑',
    'i':'𝚒','j':'𝚓','k':'𝚔','l':'𝚕','m':'𝚖','n':'𝚗','o':'𝚘','p':'𝚙',
    'q':'𝚚','r':'𝚛','s':'𝚜','t':'𝚝','u':'𝚞','v':'𝚟','w':'𝚠','x':'𝚡',
    'y':'𝚢','z':'𝚣',
    'A':'𝙰','B':'𝙱','C':'𝙲','D':'𝙳','E':'𝙴','F':'𝙵','G':'𝙶','H':'𝙷',
    'I':'𝙸','J':'𝙹','K':'𝙺','L':'𝙻','M':'𝙼','N':'𝙽','O':'𝙾','P':'𝙿',
    'Q':'𝚀','R':'𝚁','S':'𝚂','T':'𝚃','U':'𝚄','V':'𝚅','W':'𝚆','X':'𝚇',
    'Y':'𝚈','Z':'𝚉',
}

def apply_font_style(text, style=None):
    """Convert body text to Unicode font style for Telegram display."""
    s = style or TEXT_FONT_STYLE
    if s == "normal" or not text: return text
    mapping = {"bold": _BOLD_MAP, "italic": _ITALIC_MAP, "mono": _MONO_MAP}.get(s, {})
    if not mapping: return text
    return "".join(mapping.get(ch, ch) for ch in text)

def format_time():
    """Return compact or full timestamp string."""
    now = datetime.now()
    if TIME_COMPACT:
        return f"· {now.strftime('%H:%M')}"
    return now.strftime("%d %b %Y · %H:%M")

# ── NEW: CONTENT ENRICHMENT ───────────────────────────────────
def enrich_text(text):
    if not text or not ENRICH_ENABLED: return text
    tl = text.lower()
    # live score detection
    if ENRICH_LIVE_SCORES and any(k in tl for k in ["live","score","vs","ft ","ht ","min)"]):
        if not text.startswith("🔴"):
            text = "🔴 LIVE  " + text
    # sport emoji injection
    if ENRICH_MATCH_EMOJI:
        for kw, em in ENRICH_SPORT_MAP.items():
            if kw in tl and not text.startswith(em):
                text = em + " " + text
                break
    return text

# ── NEW: MEDIA DEDUP ──────────────────────────────────────────
def is_media_duplicate(msg):
    if not DEDUP_MEDIA_ENABLED: return False
    doc = getattr(msg.media, "document", None) or getattr(msg.media, "photo", None)
    raw_id = getattr(doc, "id", None) or getattr(doc, "access_hash", None)
    if not raw_id: return False
    h = hashlib.md5(str(raw_id).encode()).hexdigest()
    now = time.time()
    if h in _media_hashes and now - _media_hashes[h] < MEDIA_DEDUP_WINDOW:
        return True
    _media_hashes[h] = now
    # prune old
    expired = [k for k,v in _media_hashes.items() if now-v > MEDIA_DEDUP_WINDOW]
    for k in expired: del _media_hashes[k]
    return False

# ── NEW: ANALYTICS ────────────────────────────────────────────
def log_analytics(src_chat, msg_id, targets, has_media, text_len, hashtag_count):
    if not ANALYTICS_ENABLED: return
    try:
        with open(ANALYTICS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()},{src_chat},{msg_id},"
                    f"{len(targets)},{int(has_media)},{text_len},{hashtag_count}\n")
    except Exception: pass

# ── ADAPTIVE LIMITER ──────────────────────────────────────────
class AdaptiveLimiter:
    def __init__(self, base):
        self.base = base
        self.interval = defaultdict(lambda: base)
        self.locks = defaultdict(asyncio.Lock)
        self.next_ok = defaultdict(float)

    async def gate(self, tgt):
        async with self.locks[tgt]:
            wait = self.next_ok[tgt] - time.monotonic()
            if wait > 0: await asyncio.sleep(wait)
            self.next_ok[tgt] = time.monotonic() + self.interval[tgt]

    def flood_hit(self, tgt, seconds):
        self.interval[tgt] = min(30.0, max(self.interval[tgt], seconds / 10.0) * 1.5)
        log.info(f"🧠 Limiter learned: {tgt} → {self.interval[tgt]:.1f}s/req")

    def calm(self, tgt):
        self.interval[tgt] = max(self.base, self.interval[tgt] * 0.9)

limiter = AdaptiveLimiter(RATE_LIMIT)

# ── HEADER BANDIT ─────────────────────────────────────────────
class Bandit:
    def __init__(self, n, eps=0.15):
        self.n, self.eps = n, eps
        self.pulls, self.reward = [0]*n, [0.0]*n
    def choose(self):
        if random.random() < self.eps or sum(self.pulls) < 14:
            return random.randrange(self.n)
        return max(range(self.n), key=lambda i: self.reward[i]/max(1,self.pulls[i]))
    def update(self, arm, r):
        self.pulls[arm] += 1; self.reward[arm] += r
    def snapshot(self):
        return {i: {"pulls": self.pulls[i],
                    "avg_rx": round(self.reward[i]/max(1,self.pulls[i]),2)}
                for i in range(self.n)}

BANDIT = Bandit(len(HEADER_STYLES))
try:
    _b = json.load(open("bandit.json"))
    BANDIT.pulls, BANDIT.reward = _b["pulls"], _b["reward"]
    log.info("🎯 Bandit state loaded")
except Exception: pass

def persist_bandit():
    with open("bandit.json", "w") as f:
        json.dump({"pulls": BANDIT.pulls, "reward": BANDIT.reward}, f)

# ── DLQ ───────────────────────────────────────────────────────
DLQ = sqlite3.connect("dlq.db", check_same_thread=False)
DLQ.execute("""CREATE TABLE IF NOT EXISTS failed(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_chat INTEGER, src_id INTEGER, tgt INTEGER,
    kind TEXT, tries INTEGER DEFAULT 0, next_try REAL, ts REAL)""")
DLQ.commit()

def dlq_add(msg, tgt, kind):
    if msg is None: return
    DLQ.execute("INSERT INTO failed(src_chat,src_id,tgt,kind,next_try,ts) VALUES(?,?,?,?,?,?)",
                (msg.chat_id, msg.id, tgt, kind, time.time()+60, time.time()))
    DLQ.commit()
    STATS["dlq_added"] += 1

# ── BACKFILL ──────────────────────────────────────────────────
BF_FILE = "backfill_state.json"
try: BF_STATE = json.load(open(BF_FILE))
except Exception: BF_STATE = {}
def bf_save(): json.dump(BF_STATE, open(BF_FILE, "w"))

# ── TEXT HELPERS ──────────────────────────────────────────────
def sanitize(t):
    if not t: return ""
    return t.encode("utf-16-le", errors="surrogatepass") \
            .decode("utf-16-le", errors="ignore").replace("\x00","")

def tg_len(t): return len(sanitize(t).encode("utf-16-le")) // 2

def safe_truncate(text, limit):
    text = sanitize(text)
    if tg_len(text) <= limit: return text
    sfx = TRUNCATE_SUFFIX
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo+hi+1)//2
        if tg_len(text[:mid]+sfx) <= limit: lo = mid
        else: hi = mid-1
    return text[:lo]+sfx

def next_header():
    arm = BANDIT.choose()
    _msg_arm["pending"] = arm
    return HEADER_STYLES[arm]

def wrap(text, is_caption=False):
    """Build branded message with font style, compact time, and enrichment."""
    limit = MAX_CAPTION_CHARS if is_caption else MAX_MESSAGE_CHARS
    ts    = format_time()
    raw   = sanitize(text.strip()) if text else ""
    # enrich
    raw   = enrich_text(raw)
    # apply font style to body only (not headers/footer)
    body  = apply_font_style(raw, TEXT_FONT_STYLE) if raw else "📢"
    full  = (f"{next_header()}\n\n"
             f"{body}\n\n"
             f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
             f"🕒 {ts}\n"
             f"{BRAND_FOOTER}")
    return safe_truncate(full, limit)

# ── ENTITY PIPELINE ───────────────────────────────────────────
URL_RE = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|t\.me/[^\s]+|telegram\.me/[^\s]+|@[A-Za-z0-9_]{3,})",
    re.IGNORECASE)

def strip_links(text, entities=None):
    if not text: return text, list(entities or [])
    s = utils.add_surrogate(text)
    ranges = [(m.start(),m.end()) for m in URL_RE.finditer(s)]
    if not ranges: return text, list(entities or [])
    pieces, last = [], 0
    for a,b in ranges: pieces.append(s[last:a]); last=b
    pieces.append(s[last:])
    new_s = "".join(pieces)
    def shift(pos):
        d=0
        for a,b in ranges:
            if pos>=b: d+=b-a
        return pos-d
    new_ents=[]
    for ent in (entities or []):
        a,b=ent.offset,ent.offset+ent.length
        if any(a<rb and b>ra for ra,rb in ranges): continue
        ent=copy.copy(ent); ent.offset=shift(a); new_ents.append(ent)
    return utils.del_surrogate(new_s), new_ents

def clean(text, entities):
    text, ents = strip_links(text, entities)
    ents = [e for e in ents if not isinstance(e, types.MessageEntityCustomEmoji)]
    return sanitize(text), ents

def apply_rep(text):
    if not text: return text
    for old,new in REPLACEMENTS.items(): text=text.replace(old,new)
    return text

def allowed(msg):
    if _paused: return False
    text=(msg.raw_text or "").lower()
    if EXCLUDE_KEYWORDS and any(k.lower() in text for k in EXCLUDE_KEYWORDS): return False
    if INCLUDE_KEYWORDS and not any(k.lower() in text for k in INCLUDE_KEYWORDS): return False
    if MEDIA_FILTER:
        kind=("photo" if msg.photo else "video" if msg.video else
              "doc" if msg.document else "audio" if (msg.audio or msg.voice) else
              "sticker" if msg.sticker else "text")
        if kind not in MEDIA_FILTER: return False
    return True

# ── FINGERPRINT DEDUP ─────────────────────────────────────────
_content_hashes = set()

def is_duplicate(msg):
    if not GROWTH_FINGERPRINT: return False
    raw = (msg.raw_text or "") + str(getattr(msg,"file",None))
    h = hashlib.md5(raw.encode("utf-8","ignore")).hexdigest()
    if h in _content_hashes: return True
    _content_hashes.add(h)
    while len(_content_hashes) > 4000: _content_hashes.pop()
    return False

_orig_allowed = allowed
def allowed(msg):
    if not _orig_allowed(msg): return False
    if is_duplicate(msg):
        log.debug(f"🔁 Duplicate content skipped: {getattr(msg,'id','?')}")
        return False
    return True

# ── HASHTAG INJECTION ─────────────────────────────────────────
def inject_hashtags(text):
    if not GROWTH_HASHTAGS or not GROWTH_HASHTAG_POOL: return text
    tags = random.sample(GROWTH_HASHTAG_POOL,
                         min(GROWTH_HASHTAG_COUNT, len(GROWTH_HASHTAG_POOL)))
    suffix = "  " + " ".join(tags)
    if GROWTH_LANG_TAG: suffix += f"  #{GROWTH_LANG}"
    return (text or "") + suffix

_orig_wrap = wrap
def wrap(text, is_caption=False):
    if text and GROWTH_HASHTAGS and not is_caption:
        text = inject_hashtags(text)
    return _orig_wrap(text, is_caption)

# ── ADMIN NOTIFY ──────────────────────────────────────────────
async def notify_admin(msg):
    if not GROWTH_NOTIFY_ADMIN or not GROWTH_ADMIN_ID: return
    try:
        await client.send_message(GROWTH_ADMIN_ID,
                                  f"🔔 *888 Sport Bot*\n{msg}", parse_mode="markdown")
    except Exception: pass

# ── BOOSTER: LOGIN + JOIN ─────────────────────────────────────
async def booster_login():
    if not BOOST_ENABLED: return
    for name in BOOST_SESSIONS:
        if name in DEAD_BOOSTERS: continue
        try:
            c = TelegramClient(name, api_id, api_hash)
            await c.connect()
            if not await c.is_user_authorized():
                log.warning(f"⚠️  '{name}' not authed — login manually first")
                await c.disconnect(); continue
            BOOST_ACCOUNTS[name] = c
            for tgt in ALL_TARGETS:
                try:
                    await c(functions.channels.JoinChannelRequest(
                        channel=await c.get_input_entity(tgt)))
                except Exception: pass
            log.info(f"🚀 Booster '{name}' ready")
        except (UserDeactivatedBanError, AuthKeyUnregisteredError):
            DEAD_BOOSTERS.add(name)
            log.error(f"💀 Booster '{name}' banned — skipping permanently")
            await notify_admin(f"💀 Booster `{name}` banned/dead")
        except Exception as e:
            log.error(f"Booster '{name}': {e}")
    log.info(f"🚀 {len(BOOST_ACCOUNTS)}/{len(BOOST_SESSIONS)} boosters ready")

async def booster_disconnect():
    for c in BOOST_ACCOUNTS.values():
        try: await c.disconnect()
        except Exception: pass

# ── BOOST PROBE ───────────────────────────────────────────────
async def probe_channel(tgt_id, c):
    if tgt_id in BOOST_METHOD: return
    methods = []
    try:
        peer = await c.get_input_entity(tgt_id)
        info = await c(functions.channels.GetFullChannelRequest(channel=peer))
        fc   = info.full_chat
        if BOOST_TRY_REACTION:
            avail = getattr(fc, "available_reactions", None)
            rx_ok = (avail is None
                     or (hasattr(avail,"reactions") and len(avail.reactions)>0)
                     or (isinstance(avail,list) and len(avail)>0))
            if rx_ok: methods.append("reaction")
        if BOOST_TRY_COMMENT:
            linked = getattr(fc, "linked_chat_id", None)
            if linked:
                LINKED_GROUP[tgt_id] = linked
                methods.append("comment")
        if BOOST_TRY_CHANNEL_BOOST: methods.append("channel_boost")
    except Exception as e: log.debug(f"probe_channel {tgt_id}: {e}")
    if BOOST_TRY_VIEW:    methods.append("view")
    if BOOST_TRY_FORWARD: methods.append("forward")
    BOOST_METHOD[tgt_id] = methods
    log.info(f"🔍 Boost methods for {tgt_id}: {methods}")

# ── BOOST ACTIONS ─────────────────────────────────────────────
async def _do_reaction(name, c, tgt_id, tgt_msg):
    rxs = [types.ReactionEmoji(emoticon=e) for e in FILL_REACTIONS[:11]]
    try:
        peer = await c.get_input_entity(tgt_id)
        await c(functions.messages.SendReactionRequest(peer=peer,msg_id=tgt_msg,reaction=rxs,big=True))
        return True
    except ReactionsTooManyError:
        try:
            peer = await c.get_input_entity(tgt_id)
            await c(functions.messages.SendReactionRequest(peer=peer,msg_id=tgt_msg,reaction=[],big=False))
            await asyncio.sleep(0.5)
            await c(functions.messages.SendReactionRequest(peer=peer,msg_id=tgt_msg,reaction=rxs,big=True))
            return True
        except Exception: pass
    except FloodWaitError as e: await asyncio.sleep(e.seconds+1)
    except Exception as e:
        if any(d in str(e) for d in ("No reaction provided","REACTION_INVALID","disabled")):
            if tgt_id in BOOST_METHOD and "reaction" in BOOST_METHOD[tgt_id]:
                BOOST_METHOD[tgt_id].remove("reaction")
        log.debug(f"_do_reaction '{name}': {e}")
    return False

async def _do_comment(name, c, tgt_id, tgt_msg):
    group_id = LINKED_GROUP.get(tgt_id)
    if not group_id: return False
    try:
        disc = await c(functions.messages.GetDiscussionMessageRequest(
            peer=await c.get_input_entity(tgt_id), msg_id=tgt_msg))
        if not disc or not disc.messages: return False
        emoji = random.choice(["🔥","⚡️","🏆","💪","👏","❤️","😍","🎉","😮","🙌","👍"])
        await c.send_message(group_id, emoji, reply_to=disc.messages[0].id)
        return True
    except FloodWaitError as e: await asyncio.sleep(e.seconds+1)
    except Exception as e: log.debug(f"_do_comment '{name}': {e}")
    return False

async def _do_view(name, c, tgt_id, tgt_msg):
    try:
        peer = await c.get_input_entity(tgt_id)
        await c(functions.channels.ReadHistoryRequest(channel=peer, max_id=tgt_msg))
        return True
    except Exception as e: log.debug(f"_do_view '{name}': {e}")
    return False

async def _do_forward(name, c, tgt_id, tgt_msg):
    try:
        await c.forward_messages("me", tgt_msg, tgt_id)
        return True
    except FloodWaitError as e: await asyncio.sleep(e.seconds+1)
    except Exception as e: log.debug(f"_do_forward '{name}': {e}")
    return False

async def _do_channel_boost(name, c, tgt_id):
    try:
        peer = await c.get_input_entity(tgt_id)
        await c(functions.premium.ApplyBoostRequest(peer=peer))
        return True
    except FloodWaitError as e: await asyncio.sleep(e.seconds+1)
    except Exception as e:
        return "ALREADY" in str(e).upper()

async def _do_vote(name, c, tgt_id, tgt_msg):
    try:
        msg = await c.get_messages(tgt_id, ids=tgt_msg)
        if not msg or not isinstance(getattr(msg,"media",None), types.MessageMediaPoll): return False
        poll = msg.media.poll
        if poll.closed or not poll.answers: return False
        peer = await c.get_input_entity(tgt_id)
        await c(functions.messages.SendVoteRequest(
            peer=peer, msg_id=tgt_msg, options=[poll.answers[0].option]))
        return True
    except FloodWaitError as e: await asyncio.sleep(e.seconds+1)
    except Exception as e: log.debug(f"_do_vote '{name}': {e}")
    return False

async def boost_post(tgt_id, tgt_msg, is_poll=False):
    if not BOOST_ENABLED or not BOOST_ACCOUNTS: return
    accounts = [(n,c) for n,c in BOOST_ACCOUNTS.items() if n not in DEAD_BOOSTERS]
    if not accounts: return
    if tgt_id not in BOOST_METHOD:
        await probe_channel(tgt_id, accounts[0][1])
    methods = BOOST_METHOD.get(tgt_id, ["view","forward"])
    if "channel_boost" in methods and BOOST_TRY_CHANNEL_BOOST:
        for name,c in accounts:
            asyncio.create_task(_do_channel_boost(name, c, tgt_id))
    ok_total = 0
    for i in range(0, len(accounts), BOOST_BATCH):
        wave = accounts[i:i+BOOST_BATCH]
        async def _one(name, c):
            score = 0
            for method in methods:
                if method == "reaction" and BOOST_TRY_REACTION:
                    if await _do_reaction(name,c,tgt_id,tgt_msg): score+=1
                elif method == "comment" and BOOST_TRY_COMMENT:
                    if await _do_comment(name,c,tgt_id,tgt_msg): score+=1
                elif method == "view" and BOOST_TRY_VIEW:
                    if await _do_view(name,c,tgt_id,tgt_msg): score+=1
                elif method == "forward" and BOOST_TRY_FORWARD:
                    if await _do_forward(name,c,tgt_id,tgt_msg): score+=1
                if is_poll and BOOST_TRY_VOTE:
                    await _do_vote(name,c,tgt_id,tgt_msg)
                await asyncio.sleep(random.uniform(0.5, BOOST_DELAY_PER))
            return score
        results = await asyncio.gather(*[_one(n,cc) for n,cc in wave])
        wave_ok = sum(r for r in results if r)
        ok_total += wave_ok
        STATS["boosted"] += wave_ok
        log.info(f"🚀 Boost wave {i//BOOST_BATCH+1}: {wave_ok}/{len(wave)} on {tgt_msg}")
        if i+BOOST_BATCH < len(accounts):
            await asyncio.sleep(BOOST_DELAY)
    log.info(f"🚀 Boost complete: {ok_total} actions on msg {tgt_msg} @ {tgt_id}")

# ── REACTION MIRROR ───────────────────────────────────────────
EMOJI_CACHE = {}

async def resolve_emoji(doc_id):
    if doc_id in EMOJI_CACHE: return EMOJI_CACHE[doc_id]
    alt = None
    try:
        docs = await client(functions.messages.GetCustomEmojiDocumentsRequest(document_id=[doc_id]))
        if docs and getattr(docs[0],"alt",None):
            alt = sanitize(utils.del_surrogate(docs[0].alt)) or None
    except Exception: pass
    EMOJI_CACHE[doc_id] = alt; return alt

async def build_reactions(raw):
    out, seen = [], set()
    for r in raw:
        if isinstance(r, types.ReactionPaid): continue
        if isinstance(r, types.ReactionCustomEmoji):
            em = TRANSLATION_TABLE.get(r.document_id)
            if not em and TRANSLATE_PREMIUM: em = await resolve_emoji(r.document_id) or "👍"
            if em and em not in seen: out.append(types.ReactionEmoji(emoticon=em)); seen.add(em)
        elif isinstance(r, types.ReactionEmoji):
            em = TRANSLATION_TABLE.get(r.emoticon, r.emoticon)
            if em and em.strip() and em not in seen:
                out.append(types.ReactionEmoji(emoticon=em)); seen.add(em)
    return out

_DEAD_ERR = {"No reaction provided","REACTION_INVALID","REACTIONS_TOO_MANY_CUSTOM"}

async def probe_reactions(tgt_id, peer):
    if REACTION_CAPABLE.get(tgt_id) is not None: return REACTION_CAPABLE[tgt_id]
    ok = True
    try:
        if isinstance(peer, (types.InputPeerChannel, types.InputPeerChannelFromMessage)):
            info = await client(functions.channels.GetFullChannelRequest(channel=peer))
        else:
            info = await client(functions.messages.GetFullChatRequest(chat_id=peer.chat_id))
        avail = getattr(info.full_chat,"available_reactions",None)
        ok = (avail is None
              or (hasattr(avail,"reactions") and len(avail.reactions)>0)
              or (isinstance(avail,list) and len(avail)>0))
    except Exception: ok = True
    REACTION_CAPABLE[tgt_id] = ok
    if not ok: log.warning(f"🚫 Reactions disabled on {tgt_id}")
    return ok

async def send_reaction(peer, tgt_id, msg_id, reactions):
    if REACTION_CAPABLE.get(tgt_id) is False: return False
    try:
        await client(functions.messages.SendReactionRequest(peer=peer,msg_id=msg_id,reaction=reactions,big=True))
        REACTION_CAPABLE[tgt_id] = True; return True
    except ReactionsTooManyError:
        try:
            await client(functions.messages.SendReactionRequest(peer=peer,msg_id=msg_id,reaction=[],big=False))
            await asyncio.sleep(0.5)
            await client(functions.messages.SendReactionRequest(peer=peer,msg_id=msg_id,reaction=reactions,big=True))
            return True
        except Exception as e:
            if any(d in str(e) for d in _DEAD_ERR): REACTION_CAPABLE[tgt_id]=False
            return False
    except FloodWaitError as e: await asyncio.sleep(e.seconds+FLOOD_BACKOFF_EXTRA); return False
    except (MessageIdInvalidError,PeerIdInvalidError,ChatAdminRequiredError): return False
    except Exception as e:
        if any(d in str(e) for d in _DEAD_ERR): REACTION_CAPABLE[tgt_id]=False
        return False

_pending_rx = {}

async def mirror_reactions(src_id, src_chat):
    if not REACTIONS_ENABLED: return
    tmap = MAPPING.get(key(src_chat, src_id))
    if not tmap: return
    try:
        msg = await client.get_messages(src_chat, ids=src_id)
        if not msg or not msg.reactions: return
        raw = [r.reaction for r in msg.reactions.results
               if getattr(r,"reaction",None) and not isinstance(r.reaction,types.ReactionPaid)]
        if not raw: return
        rxs = await build_reactions(raw)
        if not rxs: return
        ok = 0
        for tgt_str, tgt_msg in tmap.items():
            tgt_id = int(tgt_str)
            if tgt_id in DEAD_TARGETS or REACTION_CAPABLE.get(tgt_id) is False: continue
            peer = await client.get_input_entity(tgt_id)
            if REACTION_CAPABLE.get(tgt_id) is None:
                if not await probe_reactions(tgt_id,peer): continue
            if await send_reaction(peer,tgt_id,tgt_msg,rxs): ok+=1
        if ok:
            log.info(f"⚡ {len(rxs)} reaction(s) → {ok} target(s) [msg {src_id}]")
            STATS["reactions"] += ok
            arm = _msg_arm.get(key(src_chat, src_id))
            if arm is not None: BANDIT.update(arm, ok)
    except Exception as e: log.debug(f"mirror_reactions: {e}")

async def schedule_rx(src_id, src_chat):
    k = key(src_chat, src_id)
    if k in _pending_rx: _pending_rx[k].cancel()
    async def _job():
        await asyncio.sleep(REACTION_DEBOUNCE)
        await mirror_reactions(src_id, src_chat)
        _pending_rx.pop(k,None)
    _pending_rx[k] = asyncio.create_task(_job())

# ── MEDIA CACHE ───────────────────────────────────────────────
_MEDIA_CACHE = {}

async def cached_media(msg):
    doc = getattr(msg.media, "document", None) or getattr(msg.media, "photo", None)
    h = getattr(doc, "access_hash", None) or hash(str(msg.media))
    if h not in _MEDIA_CACHE:
        data = await client.download_media(msg.media, file=bytes)
        if data and len(data) < 20*1024*1024:
            _MEDIA_CACHE[h] = data
            while len(_MEDIA_CACHE) > MEDIA_CACHE_MAX:
                _MEDIA_CACHE.pop(next(iter(_MEDIA_CACHE)))
        else:
            return msg.media
    return _MEDIA_CACHE[h]

# ── NEW: AUTO THREAD REPLY ────────────────────────────────────
async def auto_thread_reply(tgt_id, msg_id):
    if not AUTO_THREAD_REPLY_ENABLED: return
    linked = LINKED_GROUP.get(tgt_id)
    if not linked: return
    await asyncio.sleep(AUTO_THREAD_DELAY)
    try:
        disc = await client(functions.messages.GetDiscussionMessageRequest(
            peer=await client.get_input_entity(tgt_id), msg_id=msg_id))
        if not disc or not disc.messages: return
        reply_text = random.choice(AUTO_THREAD_REPLY_MSGS)
        await client.send_message(linked, reply_text,
                                   reply_to=disc.messages[0].id, link_preview=False)
        STATS["thread_replies"] += 1
    except Exception as e: log.debug(f"auto_thread_reply: {e}")

# ── SEND ENGINE ───────────────────────────────────────────────
def _dlq_kind(album, media, is_poll):
    if album is not None: return "album"
    if is_poll: return "poll"
    if media is not None: return "media"
    return "text"

def _resolve_caption(text, has_media):
    """Ensure media messages always have a proper caption."""
    if text:
        return wrap(text, is_caption=True)
    # no text — use fallback
    return safe_truncate(
        MEDIA_NO_CAPTION_TEXT.format(brand=BRAND_NAME) + f"\n\n🕒 {format_time()}\n{BRAND_FOOTER}",
        MAX_CAPTION_CHARS)

async def _send_to(tgt, msg=None, text=None, media=None,
                   caption=None, album=None, is_poll=False):
    if tgt in DEAD_TARGETS: return None
    kind = _dlq_kind(album, media, is_poll)
    for attempt in range(MAX_SEND_RETRIES):
        try:
            if is_poll:
                r = await client.send_message(tgt, file=types.InputMediaPoll(msg.media.poll),
                                               silent=SILENT_FORWARD)
            elif album is not None:
                sent = await client.send_file(tgt, album, caption=caption, silent=SILENT_FORWARD)
                r = sent if isinstance(sent,list) else [sent]
            elif media is not None:
                r = await client.send_file(tgt, media, caption=caption,
                    formatting_entities=None, supports_streaming=True,
                    link_preview=LINK_PREVIEW_ENABLED, silent=SILENT_FORWARD)
            elif text:
                r = await client.send_message(tgt, text, formatting_entities=None,
                    link_preview=LINK_PREVIEW_ENABLED, silent=SILENT_FORWARD)
            else:
                # attach default image if configured
                if ATTACH_DEFAULT_IMAGE and DEFAULT_IMAGE_PATH and os.path.exists(DEFAULT_IMAGE_PATH):
                    cap = caption or f"📢 {BRAND_NAME}\n\n🕒 {format_time()}\n{BRAND_FOOTER}"
                    r = await client.send_file(tgt, DEFAULT_IMAGE_PATH, caption=cap,
                        supports_streaming=True, link_preview=False, silent=SILENT_FORWARD)
                else:
                    return None
            limiter.calm(tgt)
            return r
        except FloodWaitError as e:
            log.warning(f"⏳ FloodWait {e.seconds}s → {tgt}")
            limiter.flood_hit(tgt, e.seconds)
            await asyncio.sleep(e.seconds+FLOOD_BACKOFF_EXTRA)
        except SlowModeWaitError as e: await asyncio.sleep(e.seconds+1)
        except MediaCaptionTooLongError:
            caption=safe_truncate(BRAND_FOOTER, MAX_CAPTION_CHARS)
        except FilePartMissingError:
            await asyncio.sleep(3)
        except (UserBannedInChannelError,ChatWriteForbiddenError,ChannelPrivateError) as e:
            DEAD_TARGETS.add(tgt)
            log.error(f"💀 {tgt} dead ({type(e).__name__})")
            await notify_admin(f"💀 Target `{tgt}` dead: {type(e).__name__}")
            return None
        except Exception as e:
            log.error(f"Send {tgt} attempt {attempt+1}: {e}")
            await asyncio.sleep(2*(attempt+1))
    log.error(f"📦 DLQ: {kind} msg → {tgt}")
    dlq_add(msg, tgt, kind)
    return None

async def send_one(msg, targets):
    global _msg_counter
    if not allowed(msg): return None
    if msg.media and is_media_duplicate(msg):
        log.debug(f"🔁 Media duplicate skipped: {msg.id}")
        return None
    text,_ = clean(msg.message or "", msg.entities or [])
    text   = apply_rep(text).strip() or None
    if not msg.media and not text: return None
    is_poll   = isinstance(msg.media, types.MessageMediaPoll)
    has_media = bool(msg.media and not isinstance(
        msg.media,(types.MessageMediaWebPage,types.MessageMediaPoll)))
    caption = _resolve_caption(text, has_media) if has_media else None
    message = wrap(text, is_caption=False) if (not is_poll and not has_media and text) else None
    k = key(msg.chat_id, msg.id)
    _msg_arm[k] = _msg_arm.pop("pending", None)
    media = await cached_media(msg) if has_media else None
    sent_map = {}
    htag_count = text.count("#") if text else 0
    for tgt in targets:
        result = await _send_to(tgt, msg=msg, text=message, media=media,
                                 caption=caption, is_poll=is_poll)
        if result:
            sent_map[str(tgt)] = result.id
            log.info(f"  ↳ {tgt} id={result.id}")
            STATS["forwarded"] += 1
            _msg_counter += 1
            if BOOST_ENABLED:
                asyncio.create_task(boost_post(tgt, result.id, is_poll=is_poll))
            if MOD_AUTO_PIN:
                asyncio.create_task(auto_pin(tgt, result.id))
            if AUTO_THREAD_REPLY_ENABLED:
                asyncio.create_task(auto_thread_reply(tgt, result.id))
        await limiter.gate(tgt)
    if sent_map:
        MAPPING[k] = sent_map; mark_seen(k); save_mapping()
        log_analytics(msg.chat_id, msg.id, targets, has_media,
                      len(text) if text else 0, htag_count)
        log.info(f"✅ {msg.chat_id}/{msg.id} → {len(sent_map)}/{len(targets)} [#{_msg_counter}]")
    return sent_map or None

async def send_album(msgs, targets):
    msgs = [m for m in msgs if allowed(m) and m.media]
    if not msgs: return
    first_text,_ = clean(msgs[0].message or "", msgs[0].entities or [])
    first_text   = apply_rep(first_text).strip()
    cap0 = _resolve_caption(first_text, True)
    captions     = [cap0] + [""] * (len(msgs)-1)
    media_list   = [m.media for m in msgs]
    for tgt in targets:
        result = await _send_to(tgt, album=media_list, caption=captions, msg=msgs[0])
        if result:
            for m,s in zip(msgs,result):
                kk=key(m.chat_id,m.id); MAPPING.setdefault(kk,{})[str(tgt)]=s.id; mark_seen(kk)
            log.info(f"  ↳ album {len(msgs)} → {tgt}"); STATS["albums"]+=1
            if BOOST_ENABLED: asyncio.create_task(boost_post(tgt, result[0].id))
        await limiter.gate(tgt)
    save_mapping()

# ── DLQ WORKER ────────────────────────────────────────────────
async def dlq_worker():
    while True:
        await asyncio.sleep(60)
        try:
            rows = DLQ.execute("SELECT id,src_chat,src_id,tgt,kind,tries FROM failed "
                               "WHERE next_try<? AND tries<5", (time.time(),)).fetchall()
            for rid, sc, si, tgt, kind, tries in rows:
                if tgt in DEAD_TARGETS: continue
                try:
                    if kind == "album":
                        src_msg = await client.get_messages(sc, ids=si)
                        if not src_msg: raise ValueError("gone")
                        sibs = await client.get_messages(sc, min_id=si-10, max_id=si+10)
                        group = [m for m in sibs
                                 if isinstance(m,types.Message) and m.grouped_id == src_msg.grouped_id]
                        await send_album(sorted(group, key=lambda m: m.id), [tgt])
                    else:
                        src_msg = await client.get_messages(sc, ids=si)
                        if not src_msg: raise ValueError("gone")
                        await send_one(src_msg, [tgt])
                    DLQ.execute("DELETE FROM failed WHERE id=?", (rid,))
                    STATS["dlq_recovered"] += 1
                except Exception:
                    DLQ.execute("UPDATE failed SET tries=?, next_try=? WHERE id=?",
                                (tries+1, time.time()+120*(tries+1), rid))
                DLQ.commit()
        except Exception as e: log.debug(f"dlq_worker: {e}")

# ── WATCHDOG ──────────────────────────────────────────────────
async def watchdog():
    while True:
        await asyncio.sleep(300)
        if time.monotonic() - _last_activity[0] > WATCHDOG_TIMEOUT:
            log.error("🐕 Watchdog: silent too long — restarting")
            await notify_admin("🐕 Watchdog restart")
            os._exit(1)

# ── NEW: HEARTBEAT ────────────────────────────────────────────
async def heartbeat_loop():
    if not HEARTBEAT_ENABLED: return
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        up = datetime.now() - STATS_START
        msg = (f"💓 Heartbeat — {datetime.now().strftime('%H:%M')}\n"
               f"⏱ Uptime: {str(up).split('.')[0]}\n"
               f"📤 Fwd: {STATS['forwarded']} | 🚀 Boost: {STATS['boosted']}\n"
               f"💀 Dead: {len(DEAD_TARGETS)} tgt / {len(DEAD_BOOSTERS)} boost")
        log.info(msg.replace("\n"," | "))
        if not HEARTBEAT_LOG_ONLY:
            await notify_admin(msg)

# ── BACKFILL ──────────────────────────────────────────────────
async def backfill(src, tgts):
    log.info(f"📦 Backfilling {src} from checkpoint {BF_STATE.get(str(src), 0)}...")
    count,album_buf,album_gid = 0,[],None
    async for msg in client.iter_messages(src, limit=BACKFILL_LIMIT or None,
                                          reverse=True,
                                          min_id=BF_STATE.get(str(src)) or None):
        if not isinstance(msg,types.Message): continue
        kk=key(msg.chat_id,msg.id)
        if already_seen(kk): continue
        if BACKFILL_LIMIT and count>=BACKFILL_LIMIT: break
        BF_STATE[str(src)] = msg.id; bf_save()
        if msg.grouped_id:
            if msg.grouped_id!=album_gid:
                if album_buf: await send_album(album_buf,tgts)
                album_buf,album_gid=[],msg.grouped_id
            album_buf.append(msg)
        else:
            if album_buf: await send_album(album_buf,tgts); album_buf,album_gid=[],None
            await send_one(msg,tgts); count+=1
    if album_buf: await send_album(album_buf,tgts)
    log.info(f"📦 Done: {count} msgs from {src}")

# ── EVENTS ────────────────────────────────────────────────────
@client.on(events.NewMessage(chats=ALL_SOURCES))
async def on_new(event):
    touch()
    msg=event.message
    if not isinstance(msg,types.Message) or msg.grouped_id: return
    k=key(msg.chat_id,msg.id)
    if already_seen(k): return
    mark_seen(k)
    tgts=targets_for(msg.chat_id)
    if not tgts: return
    sent=await send_one(msg,tgts)
    if sent and REACTIONS_ENABLED:
        await asyncio.sleep(2)
        await mirror_reactions(msg.id,msg.chat_id)

@client.on(events.Album(chats=ALL_SOURCES))
async def on_album(event):
    touch()
    msgs=[m for m in event.messages
          if isinstance(m,types.Message) and not already_seen(key(m.chat_id,m.id))]
    if not msgs: return
    tgts=targets_for(msgs[0].chat_id)
    if tgts: await send_album(msgs,tgts)

@client.on(events.Raw)
async def on_raw(update):
    touch()
    if isinstance(update,types.UpdateMessageReactions):
        try:
            pid=utils.get_peer_id(update.peer)
            if pid in ALL_SOURCES: await schedule_rx(update.msg_id,pid)
        except Exception: pass
    if PIN_SYNC and isinstance(update,(types.UpdatePinnedChannelMessages,
                                        types.UpdatePinnedMessages)):
        try:
            pid=utils.get_peer_id(update.peer)
            if pid not in ALL_SOURCES: return
            for mid in getattr(update,"messages",[]):
                tmap=MAPPING.get(key(pid,mid))
                if not tmap: continue
                for tgt_str,tgt_msg in tmap.items():
                    tgt_id=int(tgt_str)
                    if tgt_id in DEAD_TARGETS: continue
                    try:
                        await client(functions.messages.UpdatePinnedMessageRequest(
                            channel=await client.get_input_entity(tgt_id),
                            id=tgt_msg, unpin=not update.pinned))
                        log.info(f"{'📌' if update.pinned else '📍'} {tgt_id}")
                    except Exception as e: log.debug(f"Pin {tgt_str}: {e}")
        except Exception: pass

if FORWARD_EDITS:
    @client.on(events.MessageEdited(chats=ALL_SOURCES))
    async def on_edit(event):
        touch()
        msg=event.message
        tmap=MAPPING.get(key(msg.chat_id,msg.id))
        if not tmap: return
        text,_=clean(msg.message or "",msg.entities or [])
        branded=wrap(apply_rep(text).strip(),is_caption=False)
        for tgt_str,tgt_msg in tmap.items():
            tgt_id=int(tgt_str)
            if tgt_id in DEAD_TARGETS: continue
            try:
                await client.edit_message(tgt_id,tgt_msg,branded,
                                          formatting_entities=None,
                                          link_preview=LINK_PREVIEW_ENABLED)
                STATS["edits"]+=1
            except MessageNotModifiedError: pass
            except Exception as e: log.debug(f"Edit {tgt_str}: {e}")

if DELETE_ON_DELETE:
    @client.on(events.MessageDeleted(chats=ALL_SOURCES))
    async def on_delete(event):
        touch()
        for mid in event.deleted_ids:
            tmap=MAPPING.pop(key(event.chat_id,mid),None)
            if not tmap: continue
            for tgt_str,tgt_msg in tmap.items():
                tgt_id=int(tgt_str)
                if tgt_id in DEAD_TARGETS: continue
                try: await client.delete_messages(tgt_id,tgt_msg); STATS["deletes"]+=1
                except Exception as e: log.debug(f"Delete {tgt_str}: {e}")
            save_mapping()

# ── MOD ENGINE ────────────────────────────────────────────────
def _mod_tgts(override): return override if override else ALL_TARGETS

_last_member_count  = {}
_msg_timestamps     = defaultdict(list)
_muted_users        = {}
_last_shoutout      = defaultdict(float)
_last_digest_day    = defaultdict(int)
_scheduled_posted   = set()
_smart_sched_posted = set()
_growth_last_check  = defaultdict(float)
_last_viral_repost  = defaultdict(float)

@client.on(events.ChatAction())
async def on_chat_action(event):
    if not MOD_ENABLED or not MOD_WELCOME: return
    try:
        if event.chat_id not in _mod_tgts(MOD_WELCOME_TARGETS): return
        if not event.user_joined and not event.user_added: return
        user = await event.get_user()
        if not user or user.bot: return
        name = ((user.first_name or "") + (" " + user.last_name if user.last_name else "")).strip() or "Friend"
        await client.send_message(event.chat_id,
            random.choice(MOD_WELCOME_MSGS).format(name=name, brand=BRAND_NAME),
            link_preview=False)
        STATS["mod_welcome"] += 1
    except Exception as e: log.debug(f"welcome: {e}")

@client.on(events.NewMessage())
async def on_any_msg(event):
    if not MOD_ENABLED or not MOD_ANTISPAM: return
    try:
        if event.chat_id not in _mod_tgts(MOD_ANTISPAM_TARGETS): return
        uid = event.sender_id
        if not uid: return
        kk = (event.chat_id, uid)
        now = time.time()
        if kk in _muted_users:
            if now < _muted_users[kk]:
                try: await event.delete()
                except Exception: pass
                return
            del _muted_users[kk]
        _msg_timestamps[kk] = [t for t in _msg_timestamps[kk] if now-t < 60]
        _msg_timestamps[kk].append(now)
        if len(_msg_timestamps[kk]) > MOD_MAX_MSG_PER_MIN:
            until = int(now + MOD_MUTE_DURATION)
            _muted_users[kk] = until
            try:
                await client(functions.channels.EditBannedRequest(
                    channel=event.chat_id, participant=uid,
                    banned_rights=types.ChatBannedRights(
                        until_date=until, send_messages=True)))
                await client.send_message(event.chat_id,
                    f"⚠️ Slow down! Muted for {MOD_MUTE_DURATION//60} min.")
                STATS["mod_muted"] += 1
            except Exception as e: log.debug(f"mute: {e}")
    except Exception as e: log.debug(f"antispam: {e}")

async def check_milestones():
    if not MOD_ENABLED or not MOD_MILESTONE: return
    for tgt_id in _mod_tgts(MOD_MILESTONE_TARGETS):
        try:
            info = await client(functions.channels.GetFullChannelRequest(
                channel=await client.get_input_entity(tgt_id)))
            count = getattr(info.full_chat, "participants_count", 0)
            prev = _last_member_count.get(tgt_id, 0)
            _last_member_count[tgt_id] = count
            for ms in MOD_MILESTONES:
                if prev < ms <= count:
                    await client.send_message(tgt_id,
                        random.choice(MOD_MILESTONE_MSGS).format(count=f"{ms:,}", brand=BRAND_NAME),
                        link_preview=False)
                    STATS["mod_milestone"] += 1
                    await notify_admin(f"🎉 Milestone {ms:,} on {tgt_id}!")
        except Exception as e: log.debug(f"milestone {tgt_id}: {e}")

async def auto_pin(tgt_id, msg_id):
    if not MOD_ENABLED or not MOD_AUTO_PIN: return
    if tgt_id not in _mod_tgts(MOD_AUTO_PIN_TARGETS): return
    try:
        await client(functions.messages.UpdatePinnedMessageRequest(
            channel=await client.get_input_entity(tgt_id), id=msg_id))
        STATS["mod_pinned"] += 1
    except Exception as e: log.debug(f"auto_pin: {e}")

async def do_shoutouts():
    if not MOD_ENABLED or not MOD_SHOUTOUT or not MOD_SHOUTOUT_CHANNELS: return
    now = time.time()
    for tgt_id in _mod_tgts(MOD_SHOUTOUT_TARGETS):
        if now - _last_shoutout[tgt_id] < MOD_SHOUTOUT_INTERVAL: continue
        for ch in MOD_SHOUTOUT_CHANNELS:
            try:
                await client.send_message(tgt_id,
                    f"📣 *Check out {ch}!*\n👉 Great content — follow them!\n\n💎 {BRAND_NAME}",
                    link_preview=True)
                STATS["mod_shoutout"] += 1
                await asyncio.sleep(5)
            except Exception as e: log.debug(f"shoutout: {e}")
        _last_shoutout[tgt_id] = now

async def do_daily_digest():
    if not MOD_ENABLED or not MOD_DAILY_DIGEST: return
    now = datetime.now()
    if now.hour != MOD_DIGEST_HOUR: return
    today = now.date().toordinal()
    for tgt_id in _mod_tgts(MOD_DIGEST_TARGETS):
        if _last_digest_day[tgt_id] == today: continue
        try:
            info = await client(functions.channels.GetFullChannelRequest(
                channel=await client.get_input_entity(tgt_id)))
            count = getattr(info.full_chat, "participants_count", "?")
            uptime = datetime.now() - STATS_START
            digest = (
                f"📊 *Daily Report — {now.strftime('%d %b %Y')}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 Members: *{count:,}*\n"
                f"📤 Forwarded: *{STATS['forwarded']}*\n"
                f"⚡️ Reactions: *{STATS['reactions']}*\n"
                f"🚀 Boosts: *{STATS['boosted']}*\n"
                f"🗑 Deletes: *{STATS['deletes']}*\n"
                f"📦 DLQ recovered: *{STATS['dlq_recovered']}*\n"
                f"💬 Thread replies: *{STATS['thread_replies']}*\n"
                f"📈 Msg counter: *{_msg_counter}*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏱ Uptime: {str(uptime).split('.')[0]}\n💎 {BRAND_NAME}")
            await client.send_message(tgt_id, digest, parse_mode="markdown", link_preview=False)
            _last_digest_day[tgt_id] = today
        except Exception as e: log.debug(f"digest {tgt_id}: {e}")

async def do_scheduled_posts():
    if not MOD_ENABLED or not MOD_SCHEDULER: return
    now = datetime.now()
    for hour in MOD_SCHEDULE_HOURS:
        if now.hour != hour: continue
        for tgt_id in _mod_tgts(MOD_SCHEDULE_TARGETS):
            pk = f"{tgt_id}:{now.strftime('%Y-%m-%d')}:{hour}"
            if pk in _scheduled_posted: continue
            try:
                await client.send_message(tgt_id,
                    random.choice(MOD_SCHEDULE_MSGS).format(brand=BRAND_NAME),
                    parse_mode="markdown", link_preview=False)
                _scheduled_posted.add(pk)
                STATS["mod_scheduled"] += 1
            except Exception as e: log.debug(f"scheduled: {e}")

# ── NEW: SMART SCHEDULER ──────────────────────────────────────
async def do_smart_scheduled():
    if not SMART_SCHEDULE_ENABLED: return
    now = datetime.now()
    hour = now.hour
    if hour not in SMART_SCHEDULE_SLOTS: return
    tgts = _mod_tgts(SMART_SCHEDULE_TARGETS)
    for tgt_id in tgts:
        pk = f"smart:{tgt_id}:{now.strftime('%Y-%m-%d')}:{hour}"
        if pk in _smart_sched_posted: continue
        try:
            await client.send_message(
                tgt_id,
                SMART_SCHEDULE_SLOTS[hour].format(brand=BRAND_NAME),
                parse_mode="markdown", link_preview=False)
            _smart_sched_posted.add(pk)
            STATS["smart_scheduled"] += 1
            log.info(f"📅 Smart schedule hour={hour} → {tgt_id}")
        except Exception as e: log.debug(f"smart_schedule: {e}")

async def mod_loop():
    await asyncio.sleep(30)
    while True:
        try:
            await do_scheduled_posts()
            await do_smart_scheduled()
            await do_shoutouts()
            await do_daily_digest()
            await check_milestones()
        except Exception as e: log.debug(f"mod_loop: {e}")
        await asyncio.sleep(60)

# ── GROWTH SYSTEMS ────────────────────────────────────────────
async def growth_tracker_tick():
    if not GROWTH_TRACKER: return
    now = time.time()
    for tgt_id in ALL_TARGETS:
        if now - _growth_last_check[tgt_id] < GROWTH_TRACKER_INTERVAL: continue
        _growth_last_check[tgt_id] = now
        try:
            info = await client(functions.channels.GetFullChannelRequest(
                channel=await client.get_input_entity(tgt_id)))
            count = getattr(info.full_chat,"participants_count",0)
            with open(GROWTH_TRACKER_FILE,"a",encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{tgt_id},{count}\n")
        except Exception as e: log.debug(f"tracker {tgt_id}: {e}")

async def check_viral_reposts():
    if not GROWTH_REPOST_VIRAL: return
    now = time.time()
    for tgt_id in ALL_TARGETS:
        if now - _last_viral_repost[tgt_id] < GROWTH_VIRAL_INTERVAL: continue
        try:
            async for msg in client.iter_messages(tgt_id, limit=50):
                if not isinstance(msg,types.Message) or not msg.reactions: continue
                total = sum(r.count for r in msg.reactions.results)
                if total >= GROWTH_VIRAL_THRESH:
                    text = (msg.raw_text or "")
                    branded = wrap(f"🔥 *TOP POST — {total} reactions!*\n\n" + inject_hashtags(text),
                                   is_caption=bool(msg.media))
                    if msg.media and not isinstance(msg.media,(types.MessageMediaWebPage,types.MessageMediaPoll)):
                        await client.send_file(tgt_id, msg.media, caption=branded,
                            formatting_entities=None, supports_streaming=True,
                            link_preview=False, silent=SILENT_FORWARD)
                    else:
                        await client.send_message(tgt_id, branded, formatting_entities=None,
                            link_preview=False, silent=SILENT_FORWARD)
                    _last_viral_repost[tgt_id] = now
                    STATS["viral_reposts"] += 1
                    await notify_admin(f"🔥 Viral repost on {tgt_id} ({total} rx)")
                    break
        except Exception as e: log.debug(f"viral {tgt_id}: {e}")

async def growth_loop():
    await asyncio.sleep(60)
    while True:
        try:
            await growth_tracker_tick(); await check_viral_reposts()
        except Exception as e: log.debug(f"growth_loop: {e}")
        await asyncio.sleep(300)

# ── DASHBOARD HELPERS ─────────────────────────────────────────
def sparkline(values):
    bars = "▁▂▃▄▅▆▇█"
    if not values: return "—"
    lo, hi = min(values), max(values)
    if hi == lo: return bars[0]*len(values)
    return "".join(bars[min(7, int((v-lo)/(hi-lo)*8))] for v in values[-20:])

def growth_series(tgt_id):
    vals = []
    try:
        for line in open(GROWTH_TRACKER_FILE):
            ts, tid, cnt = line.strip().split(",")
            if int(tid) == tgt_id: vals.append(int(cnt))
    except FileNotFoundError: pass
    return vals

def apply_hot_config():
    if not os.path.exists(HOT_CONFIG_FILE): return "no hotconfig.json"
    cfg = json.load(open(HOT_CONFIG_FILE))
    g, applied = globals(), []
    for k, v in cfg.items():
        if k in g and not k.startswith("_"):
            if isinstance(g[k], bool) and not isinstance(v, bool): continue
            if isinstance(g[k], (int, float)) and not isinstance(v, (int, float)): continue
            g[k] = v; applied.append(k)
    limiter.base = RATE_LIMIT
    log.info(f"🔥 Hot config applied: {applied}")
    return ", ".join(applied) or "nothing valid"

# ── OWNER COMMANDS ────────────────────────────────────────────
@client.on(events.NewMessage(
    pattern=r"^/(ping|stats|status|queue|pause|resume|reload|fontset|timefmt|testmsg|analytics)(\s+\S+)?$",
    from_users="me"))
async def on_cmd(event):
    global MAPPING, _paused, TEXT_FONT_STYLE, TIME_COMPACT
    parts = event.raw_text.strip().split(maxsplit=1)
    cmd   = parts[0].lower()
    arg   = parts[1].strip() if len(parts) > 1 else ""

    if cmd == "/ping":
        up = datetime.now() - STATS_START
        await event.reply(
            f"🏓 *Pong!*\n"
            f"⏱ Uptime: `{str(up).split('.')[0]}`\n"
            f"📨 Forwarded: `{STATS['forwarded']}`\n"
            f"⚡ Reactions: `{STATS['reactions']}`\n"
            f"🚀 Boosts: `{STATS['boosted']}`\n"
            f"📦 DLQ recovered: `{STATS['dlq_recovered']}`\n"
            f"💀 Dead: `{len(DEAD_TARGETS)}` tgt / `{len(DEAD_BOOSTERS)}` boosters\n"
            f"🕒 {format_time()}",
            parse_mode="markdown")

    elif cmd == "/stats":
        up = datetime.now() - STATS_START
        lines = [f"📊 *888 SPORT v{VERSION}* — `{str(up).split('.')[0]}`", ""]
        for i,(srcs,tgts) in enumerate(PIPELINES,1):
            lines.append(f"Pipeline {i}: `{srcs}` → `{tgts}`")
        lines += [
            "", f"fwd=`{STATS['forwarded']}` albums=`{STATS['albums']}`",
            f"rx=`{STATS['reactions']}` boost=`{STATS['boosted']}`",
            f"edits=`{STATS['edits']}` del=`{STATS['deletes']}`",
            f"welcome=`{STATS['mod_welcome']}` muted=`{STATS['mod_muted']}`",
            f"milestones=`{STATS['mod_milestone']}` viral=`{STATS['viral_reposts']}`",
            f"thread_replies=`{STATS['thread_replies']}` smart_sched=`{STATS['smart_scheduled']}`",
            f"mapping=`{len(MAPPING)}` boosters=`{len(BOOST_ACCOUNTS)}`",
            f"msg_counter=`{_msg_counter}` font=`{TEXT_FONT_STYLE}` time_compact=`{TIME_COMPACT}`",
        ]
        await event.reply("\n".join(lines), parse_mode="markdown")

    elif cmd == "/status":
        lines = ["📊 *LIVE STATUS*", ""]
        for tgt in ALL_TARGETS:
            s = growth_series(tgt)
            lim = limiter.interval.get(tgt, RATE_LIMIT)
            lines.append(f"`{tgt}`  ⏱{lim:.1f}s")
            lines.append(f"  growth `{sparkline(s)}` {s[-1]:,}" if s else "  growth `no data`")
        lines += ["", "*Bandit:*"]
        for i, d in sorted(BANDIT.snapshot().items(), key=lambda x: -x[1]["avg_rx"]):
            lines.append(f"  header#{i}: {d['pulls']} posts · {d['avg_rx']} rx avg")
        pending = DLQ.execute("SELECT COUNT(*) FROM failed").fetchone()[0]
        lines += [
            "", f"*Boosters:* `{len(BOOST_ACCOUNTS)}`✓ / `{len(DEAD_BOOSTERS)}`💀",
            f"*DLQ:* `{pending}` pending | *Mapping:* `{len(MAPPING)}`",
            f"*Font:* `{TEXT_FONT_STYLE}` | *Time compact:* `{TIME_COMPACT}`",
            f"*Paused:* `{_paused}` | *Version:* `{VERSION}`",
        ]
        await event.reply("\n".join(lines), parse_mode="markdown")

    elif cmd == "/queue":
        n = DLQ.execute("SELECT COUNT(*) FROM failed").fetchone()[0]
        rows = DLQ.execute("SELECT id,src_chat,src_id,tgt,kind,tries FROM failed "
                           "ORDER BY id DESC LIMIT 10").fetchall()
        txt = f"📦 *DLQ: {n} pending*\n" + "\n".join(
            f"`#{i}` {sc}/{si}→{tgt} [{k}] tries={t}" for i,sc,si,tgt,k,t in rows)
        await event.reply(txt or "📦 DLQ empty", parse_mode="markdown")

    elif cmd == "/pause":
        _paused = True
        await event.reply("⏸ *Paused* — no messages will be forwarded", parse_mode="markdown")

    elif cmd == "/resume":
        _paused = False
        await event.reply("▶️ *Resumed*", parse_mode="markdown")

    elif cmd == "/reload":
        try:
            with open("mapping.json", encoding="utf-8") as f: MAPPING = json.load(f)
        except Exception: pass
        hot = apply_hot_config()
        await event.reply(f"🔄 Mapping reloaded (`{len(MAPPING)}`)\n🔥 Hot config: {hot}",
                           parse_mode="markdown")

    elif cmd == "/fontset":
        # /fontset bold|italic|mono|normal
        valid = {"bold","italic","mono","normal"}
        if arg in valid:
            TEXT_FONT_STYLE = arg
            await event.reply(f"🖋 Font style set to `{arg}`", parse_mode="markdown")
        else:
            await event.reply(f"Usage: /fontset bold|italic|mono|normal\nCurrent: `{TEXT_FONT_STYLE}`",
                               parse_mode="markdown")

    elif cmd == "/timefmt":
        # /timefmt compact|full
        if arg == "compact":
            TIME_COMPACT = True
            await event.reply("🕒 Time format: *compact* (· HH:MM)", parse_mode="markdown")
        elif arg == "full":
            TIME_COMPACT = False
            await event.reply("🕒 Time format: *full* (DD Mon YYYY · HH:MM)", parse_mode="markdown")
        else:
            cur = "compact" if TIME_COMPACT else "full"
            await event.reply(f"Usage: /timefmt compact|full\nCurrent: `{cur}`",
                               parse_mode="markdown")

    elif cmd == "/testmsg":
        # Send a test branded message to Saved Messages
        sample = "⚽ Live: Real Madrid 2–1 Barcelona | 88' | Champions League"
        branded = wrap(sample)
        await client.send_message("me", branded, link_preview=False)
        await event.reply("✅ Test message sent to Saved Messages")

    elif cmd == "/analytics":
        try:
            lines_count = sum(1 for _ in open(ANALYTICS_FILE))
            await event.reply(f"📈 Analytics: `{lines_count}` events logged in `{ANALYTICS_FILE}`",
                               parse_mode="markdown")
        except FileNotFoundError:
            await event.reply("📈 Analytics file not created yet (no messages forwarded)")

# ── STATS LOOP ────────────────────────────────────────────────
async def stats_loop():
    while True:
        await asyncio.sleep(3600)
        persist_bandit()
        uptime=datetime.now()-STATS_START
        log.info(f"📊 uptime={uptime} | fwd={STATS['forwarded']} rx={STATS['reactions']} "
                 f"boost={STATS['boosted']} del={STATS['deletes']} "
                 f"dlq+={STATS['dlq_added']} dlq✓={STATS['dlq_recovered']} "
                 f"dead={len(DEAD_TARGETS)}/{len(DEAD_BOOSTERS)} "
                 f"welcome={STATS['mod_welcome']} muted={STATS['mod_muted']} "
                 f"milestone={STATS['mod_milestone']} "
                 f"smart_sched={STATS['smart_scheduled']} "
                 f"thread_replies={STATS['thread_replies']}")

# ── MAIN ──────────────────────────────────────────────────────
async def main():
    flat = [x for p in PIPELINES for x in p[0]+p[1]]
    if len(flat) != len(set(flat)): log.warning("⚠️ Duplicate IDs in pipelines")
    for srcs,tgts in PIPELINES:
        if set(srcs) & set(tgts): log.warning("⚠️ Source/target overlap — loop risk!")

    await client.start(phone=phone)
    me=await client.get_me()
    log.info("╔══════════════════════════════════════════════════╗")
    log.info(f"║  🔥  888 SPORT FORWARDER v{VERSION} EXTREME  🔥  ║")
    log.info(f"║  🛠  Prepared by Abuta                         ║")
    log.info("╚══════════════════════════════════════════════════╝")
    log.info(f"👤 {me.first_name} (@{me.username})")
    for i,(srcs,tgts) in enumerate(PIPELINES,1):
        log.info(f"📡 Pipeline {i}: {srcs} → {tgts}")
    log.info(f"🖋  Font: {TEXT_FONT_STYLE} | ⏰ Time: {'compact' if TIME_COMPACT else 'full'}")
    log.info(f"🧠 limiter=ADAPTIVE bandit={sum(BANDIT.pulls)}pulls dlq=ON "
             f"cache={MEDIA_CACHE_MAX} watchdog={WATCHDOG_TIMEOUT}s "
             f"analytics={'ON' if ANALYTICS_ENABLED else 'OFF'} "
             f"heartbeat={'ON' if HEARTBEAT_ENABLED else 'OFF'}")

    REACTION_CAPABLE.clear(); BOOST_METHOD.clear()
    if BOOST_ENABLED: await booster_login()
    apply_hot_config()

    asyncio.create_task(stats_loop())
    asyncio.create_task(dlq_worker())
    asyncio.create_task(watchdog())
    asyncio.create_task(heartbeat_loop())
    if MOD_ENABLED: asyncio.create_task(mod_loop())
    asyncio.create_task(growth_loop())

    if BACKFILL_ON_START:
        for srcs,tgts in PIPELINES:
            for src in srcs: await backfill(src,tgts)

    log.info("🚀 Live — all systems active.")
    log.info("   /ping /stats /status /queue /pause /resume /reload")
    log.info("   /fontset bold|italic|mono|normal")
    log.info("   /timefmt compact|full")
    log.info("   /testmsg  /analytics")
    await client.run_until_disconnected()

# ── PROCESS MANAGEMENT ────────────────────────────────────────
def kill_old_instance():
    import subprocess
    try:
        current_pid = os.getpid()
        result = subprocess.run(["pgrep","-f","forwarder.py"],
                                capture_output=True, text=True)
        for p in result.stdout.strip().split():
            if p.isdigit() and int(p) != current_pid:
                try:
                    os.kill(int(p), 9)
                    log.info(f"🔫 Killed old instance PID {p}")
                except Exception: pass
        time.sleep(2)
    except Exception: pass

def remove_session_lock():
    import glob
    for pat in ["*.session-journal","*.session-wal","session.session-shm"]:
        for f in glob.glob(pat):
            try: os.remove(f); log.info(f"🗑 Removed lock: {f}")
            except Exception: pass

async def run():
    kill_old_instance()
    remove_session_lock()
    while True:
        try:
            async with client: await main()
        except KeyboardInterrupt:
            log.info("👋 Stopped"); await booster_disconnect(); break
        except Exception as e:
            err = str(e)
            if "database is locked" in err:
                log.warning("🔒 Session locked — cleaning and retrying...")
                kill_old_instance(); remove_session_lock()
                await asyncio.sleep(3); continue
            if not AUTO_RECONNECT: await booster_disconnect(); raise
            log.error(f"💥 {e} — reconnecting in 10s...")
            await asyncio.sleep(10)

asyncio.run(run())
