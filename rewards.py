"""Persistent game economy: earned-only coins, collectible inventory, and atomic cases."""
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

DB = Path(os.environ.get('BOILER_PROFILE_DB', str(Path(__file__).with_name('profile.sqlite3'))))
CASES = {
    "Standard": (50, (55, 28, 12, 4, 1)),
    "Premium": (200, (0, 60, 28, 10, 2)),
    "Elite": (500, (0, 0, 0, 85, 15)),
}
DUPLICATE_REFUND = 20
DEFAULT_AVATAR_COLOR = "#CFB991"
RARITIES = {"Common": (55, "#B8C0C8"), "Rare": (28, "#68B7F7"), "Epic": (12, "#BD92FF"), "Legendary": (4, "#F0BC64"), "Mythic": (1, "#F68FB3")}
# Each item changes its relevant avatar layer, rather than merely repainting the robot.
ITEMS = {
    "basic": {"name":"Workshop Bot", "rarity":"Starter", "slot":"body", "symbol":"◆", "description":"Your first companion."},
    "cap": {"name":"Boiler Cap", "rarity":"Common", "slot":"head", "symbol":"🧢", "description":"A classic campus cap."},
    "beanie": {"name":"Night Shift Beanie", "rarity":"Common", "slot":"head", "symbol":"🎩", "description":"For long study sessions."},
    "shield": {"name":"Firewall Plate", "rarity":"Common", "slot":"body", "symbol":"🛡️", "description":"Defensive armor plating."},
    "specs": {"name":"Cyber Specs", "rarity":"Rare", "slot":"face", "symbol":"🕶️", "description":"An unmistakable dark visor."},
    "halo": {"name":"Circuit Halo", "rarity":"Rare", "slot":"head", "symbol":"◉", "description":"A floating energy ring."},
    "cape": {"name":"Goldline Cloak", "rarity":"Rare", "slot":"body", "symbol":"⚡", "description":"A polished power cloak."},
    "spark": {"name":"Static Field", "rarity":"Epic", "slot":"effect", "symbol":"✦", "description":"Electric sparks orbit your bot."},
    "owl": {"name":"Cipher Owl", "rarity":"Epic", "slot":"pet", "symbol":"🦉", "description":"A curious study companion."},
    "crown": {"name":"Cryptic Crown", "rarity":"Legendary", "slot":"head", "symbol":"♛", "description":"A royal gold crown."},
    "dragon": {"name":"Byte Dragon", "rarity":"Legendary", "slot":"pet", "symbol":"🐉", "description":"A miniature digital dragon."},
    "nebula": {"name":"Nebula Core", "rarity":"Mythic", "slot":"effect", "symbol":"✺", "description":"A cosmic aura for the rarest collectors."},
}
# Keep existing item IDs and rarity assignments for saved collections.
for item_id, name, rarity, slot, symbol, description in (
    ("antenna", "Signal Mast", "Common", "head", "📡", "A dish for picking up signals."),
    ("goggles", "Lab Goggles", "Common", "face", "🥽", "Clear goggles for the workshop."),
    ("apron", "Forge Apron", "Common", "body", "🧰", "A tool rig across the chest."),
    ("mouse", "Packet Mouse", "Common", "pet", "🐁", "A tiny courier for lost packets."),
    ("headset", "Bandwidth Headset", "Rare", "head", "🎧", "Oversized padded headphones."),
    ("mask", "Filter Mask", "Rare", "face", "😷", "A filter over the lower face."),
    ("orbit", "Satellite Array", "Rare", "effect", "🛰️", "Two satellites hang in orbit."),
    ("knight", "Checksum Helm", "Epic", "head", "⚔", "A crossed-blade crest."),
    ("reactor", "Reactor Harness", "Epic", "body", "☢", "A reactor mounted on the chest."),
    ("fox", "Phantom Fox", "Epic", "pet", "🦊", "An orange fox with sharp ears."),
    ("prism", "Prismatic Lens", "Legendary", "face", "🔷", "A diamond lens at the center of the visor."),
    ("thunder", "Thunder Engine", "Legendary", "effect", "ϟ", "Lightning bolts frame the robot."),
    ("phoenix", "Cipher Phoenix", "Mythic", "pet", "🔥", "A phoenix wreathed in fire."),
    ("void", "Event Horizon", "Mythic", "head", "🪐", "A ringed planet floats above the head."),
):
    ITEMS[item_id] = dict(name=name, rarity=rarity, slot=slot,
                          symbol=symbol, description=description)

ROLL_POOL = [k for k in ITEMS if k != "basic"]
SLOTS = ("head", "face", "body", "effect", "pet")

def profile_database():
    if os.environ.get('BOILER_PROFILE_DB'):
        return DB
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    if get_script_run_ctx(suppress_warning=True) is None:
        return DB
    if 'profile_directory' not in st.session_state:
        st.session_state.profile_directory = TemporaryDirectory(prefix='boiler-crypto-')
    return Path(st.session_state.profile_directory.name) / 'profile.sqlite3'


@contextmanager
def connect():
    db = sqlite3.connect(profile_database(), timeout=15)
    db.execute("PRAGMA busy_timeout=15000")
    db.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, coins INTEGER NOT NULL, correct INTEGER NOT NULL, equipped TEXT NOT NULL)")
    db.execute("INSERT OR IGNORE INTO profile VALUES (1,0,0,'starter')")
    db.execute("CREATE TABLE IF NOT EXISTS owned (item TEXT PRIMARY KEY)")
    db.execute("INSERT OR IGNORE INTO owned VALUES ('starter')")
    db.execute("CREATE TABLE IF NOT EXISTS rewards (event TEXT PRIMARY KEY)")
    db.execute("CREATE TABLE IF NOT EXISTS inventory (item TEXT PRIMARY KEY)")
    db.execute("INSERT OR IGNORE INTO inventory VALUES ('basic')")
    db.execute("CREATE TABLE IF NOT EXISTS loadout (slot TEXT PRIMARY KEY, item TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS case_history (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT NOT NULL, duplicate INTEGER NOT NULL, opened_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    db.execute("CREATE TABLE IF NOT EXISTS avatar_style (id INTEGER PRIMARY KEY CHECK(id=1), color TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS case_requests (request_id TEXT PRIMARY KEY, case_name TEXT NOT NULL, history_id INTEGER NOT NULL REFERENCES case_history(id))")
    db.commit()
    if "refund" not in {column[1] for column in db.execute("PRAGMA table_info(case_requests)")}:
        db.execute("BEGIN IMMEDIATE")
        if "refund" not in {column[1] for column in db.execute("PRAGMA table_info(case_requests)")}:
            db.execute("ALTER TABLE case_requests ADD COLUMN refund INTEGER")
    db.commit()
    try:
        yield db
    finally:
        db.close()

def profile():
    with connect() as db:
        coins, correct, old_equipped = db.execute('SELECT coins,correct,equipped FROM profile WHERE id=1').fetchone()
        inventory = {r[0] for r in db.execute('SELECT item FROM inventory')}
        loadout = dict(db.execute('SELECT slot,item FROM loadout'))
        style = db.execute("SELECT color FROM avatar_style WHERE id=1").fetchone()
        cases = db.execute('SELECT COUNT(*) FROM case_history').fetchone()[0]
    return dict(coins=coins, correct=correct, owned=inventory, equipped=loadout, cases=cases,
                color=style[0] if style else DEFAULT_AVATAR_COLOR)

def set_avatar_color(color):
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        raise ValueError("Expected a six-digit hex color")
    with connect() as db, db:
        db.execute("INSERT OR REPLACE INTO avatar_style VALUES (1,?)", (color,))


def reward(event):
    with connect() as db:
        with db:
            inserted = db.execute('INSERT OR IGNORE INTO rewards VALUES (?)', (event,)).rowcount
            if inserted:
                db.execute('UPDATE profile SET coins=coins+10, correct=correct+1 WHERE id=1')
    return bool(inserted)

def open_case(case_name, request_id, *, infinite_coins=False):
    """Commit one charge and drop per purchase request, including retries."""
    cost, weights = CASES[case_name]
    with connect() as db, db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute(
            """SELECT h.item, h.duplicate, r.case_name, r.refund FROM case_requests r
               JOIN case_history h ON h.id = r.history_id WHERE r.request_id = ?""",
            (request_id,),
        ).fetchone()
        if previous:
            item, duplicate, original_case, refund = previous
            if refund is None:
                refund = DUPLICATE_REFUND if duplicate else 0
            return dict(item=item, duplicate=bool(duplicate), case=original_case,
                        refund=refund)
        if infinite_coins:
            cost = 0
        coins = db.execute("SELECT coins FROM profile WHERE id=1").fetchone()[0]
        if coins < cost:
            return None
        ticket = secrets.randbelow(100)
        for rarity, weight in zip(RARITIES, weights):
            if ticket < weight:
                break
            ticket -= weight
        candidates = [item for item in ROLL_POOL if ITEMS[item]["rarity"] == rarity]
        item = secrets.choice(candidates)
        duplicate = not db.execute("INSERT OR IGNORE INTO inventory VALUES (?)", (item,)).rowcount
        refund = DUPLICATE_REFUND if duplicate and not infinite_coins else 0
        db.execute("UPDATE profile SET coins=coins-?+? WHERE id=1", (cost, refund))
        history_id = db.execute(
            "INSERT INTO case_history(item,duplicate) VALUES (?,?)", (item, int(duplicate))
        ).lastrowid
        db.execute("INSERT INTO case_requests (request_id,case_name,history_id,refund) VALUES (?,?,?,?)",
                   (request_id, case_name, history_id, refund))
        return dict(item=item, duplicate=duplicate, case=case_name, refund=refund)

def equip(item):
    if item not in ITEMS:
        return False
    slot = ITEMS[item]['slot']
    if slot not in SLOTS:
        return False
    with connect() as db:
        with db:
            if not db.execute('SELECT 1 FROM inventory WHERE item=?', (item,)).fetchone():
                return False
            db.execute('INSERT OR REPLACE INTO loadout(slot,item) VALUES (?,?)', (slot,item))
    return True

def unequip(slot):
    if slot not in SLOTS:
        return
    with connect() as db:
        with db:
            db.execute('DELETE FROM loadout WHERE slot=?', (slot,))

def recent_cases(limit=8):
    with connect() as db:
        return db.execute('SELECT item,duplicate FROM case_history ORDER BY id DESC LIMIT ?', (limit,)).fetchall()


