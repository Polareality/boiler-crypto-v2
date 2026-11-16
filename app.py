"""Boiler Crypto — accessible learning game with earn-only collectible rewards."""
import html
import random
from pathlib import Path
from uuid import uuid4
import streamlit as st
from question_bank import QUESTIONS
from rewards import (CASES, DEFAULT_AVATAR_COLOR, DUPLICATE_REFUND, ITEMS, RARITIES, ROLL_POOL, SLOTS, equip, open_case,
                     profile, recent_cases, reward, set_avatar_color, unequip)

st.set_page_config(page_title="Boiler Crypto | Learn & Collect", page_icon="🔐", layout="wide", initial_sidebar_state="collapsed")
st.markdown('''<style>
:root{--gold:#CFB991;--gold2:#E9D9B5;--bg:#0C0D0E;--surface:#191B1D;--line:#383735;--white:#F5F3ED;--muted:#B9B6AC}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--white)!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stMainBlockContainer"]{max-width:1250px!important;padding-top:4rem!important;padding-bottom:3rem!important}
.block-container{max-width:1250px!important}
html{font-size:18px!important}
h1,h2,h3,p,span,label,div,button{font-family:Inter,"Segoe UI",Arial,sans-serif}
h1{font-size:clamp(2.25rem,4vw,3.6rem)!important;font-weight:850!important;letter-spacing:-.045em!important;line-height:1.15!important}
h2{font-size:clamp(1.65rem,2.5vw,2.3rem)!important;letter-spacing:-.03em!important}
h3{font-size:1.42rem!important}
p{line-height:1.55!important}
[data-testid="stCaptionContainer"] p{font-size:.9rem!important;color:var(--muted)!important}
[data-testid="stWidgetLabel"] p{font-size:1rem!important;font-weight:650!important;color:#E6E0D0!important}
.stButton button,[data-testid="stFormSubmitButton"] button{min-height:52px!important;border-radius:10px!important;font-size:1.05rem!important;font-weight:750!important}
.stButton button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{background:var(--gold)!important;border:1px solid var(--gold)!important;color:#111!important}
.stButton button[kind="secondary"]{background:#202123!important;border:1px solid #55514A!important;color:var(--gold2)!important}
.stButton button:hover,[data-testid="stFormSubmitButton"] button:hover{filter:brightness(1.05)}
button:focus-visible,input:focus-visible,[role="radio"]:focus-visible{outline:3px solid #F1D79D!important;outline-offset:3px!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{background:#202123!important;border:1px solid #59564F!important;min-height:52px!important;border-radius:10px!important}
[data-testid="stRadio"]{background:transparent!important;border:none!important;padding:0!important}
/* Answer rows: flat by default. No outer answer-panel border or glowing hover boxes. */
[data-testid="stRadio"] [role="radiogroup"]{gap:10px!important}
[data-testid="stRadio"] [role="radiogroup"]>label{border:1px solid #474642!important;border-radius:10px!important;background:#1B1D1E!important;padding:14px 16px!important;min-height:58px!important;transition:background .1s ease,border-color .1s ease!important;box-shadow:none!important}
[data-testid="stRadio"] [role="radiogroup"]>label:hover{background:#252625!important;border-color:#787061!important;box-shadow:none!important}
[data-testid="stRadio"] [role="radiogroup"]>label:has(input:checked){background:#332E24!important;border:2px solid var(--gold)!important;box-shadow:none!important}
[data-testid="stRadio"] [role="radiogroup"]>label p{font-size:1.07rem!important}
/* Navigation radio is styled separately to avoid answer-card treatment. */
[data-testid="stRadio"]:has([aria-label="Navigation"]) [role="radiogroup"]>label{background:transparent!important;border:none!important;padding:9px 12px!important;min-height:42px!important}
[data-testid="stRadio"]:has([aria-label="Navigation"]) [role="radiogroup"]>label:has(input:checked){background:#363124!important;border:1px solid #8B7955!important}
[data-testid="stMetric"]{background:#181A1B;border:1px solid #343635;border-radius:13px;padding:16px}
[data-testid="stMetricValue"]{font-size:1.8rem!important;color:var(--gold)!important}
[data-testid="stProgress"] [role="progressbar"]>div{background:var(--gold)!important}
[data-testid="stExpander"]{border:1px solid #45423B!important;border-radius:10px!important;background:#181A1B!important}
[data-testid="stAlert"]{border-radius:10px!important}
[data-testid="stForm"]{border:none!important;padding:0!important}
hr{border-color:#343434!important}
.kicker{color:var(--gold);font-size:.79rem;font-weight:850;letter-spacing:.14em;text-transform:uppercase;margin:0 0 9px}
.brandline{border-bottom:1px solid #393936;padding-bottom:14px;margin-bottom:23px}
.hero{background:linear-gradient(110deg,#24251F,#17191B);border:1px solid #484337;border-radius:16px;padding:28px 30px;margin:0 0 23px}
.hero p{color:#D5D0C4;font-size:1.08rem;margin:10px 0 0}
.surface{background:#181A1C;border:1px solid #3D3C37;border-radius:14px;padding:22px;margin-bottom:16px}
.item{background:#191B1D;border:1px solid #47443E;border-radius:14px;padding:16px 18px;min-height:175px;margin-bottom:4px}
.item-title{font-size:1.13rem;font-weight:800;color:#F5F1E7;margin:8px 0 2px}
.item-meta{font-size:.87rem;color:#BBB7AB;margin:0 0 8px}
.pill{display:inline-block;border:1px solid currentColor;border-radius:999px;padding:3px 9px;font-size:.74rem;font-weight:800;letter-spacing:.035em}
.avatar-scene{position:relative;display:flex;align-items:center;justify-content:center;min-height:285px;border-radius:15px;background:radial-gradient(circle at 50% 52%,#3B3425 0,#1B1C1B 48%,#131515 100%);border:1px solid #454039;overflow:hidden}
.avatar-figure{position:relative;width:220px;height:230px;text-align:center}
.bot-head{position:absolute;top:53px;left:58px;width:106px;height:86px;border-radius:25px 25px 21px 21px;background:linear-gradient(145deg,#E4D4B2,#9E865B);border:3px solid #F3E5C9;box-shadow:inset -10px -8px 0 #0002}
.bot-eyes{position:absolute;top:32px;left:14px;width:73px;height:28px;border-radius:13px;background:#171D20;display:flex;align-items:center;justify-content:space-around}
.bot-eyes b{height:13px;width:12px;background:#D7C092;border-radius:5px}
.bot-body{position:absolute;top:148px;left:71px;width:80px;height:69px;border-radius:18px 18px 24px 24px;background:linear-gradient(145deg,#DDCA9F,#9C8050);border:3px solid #F3E4BD;display:flex;align-items:center;justify-content:center;font-size:33px;color:#262827}
.bot-head,.bot-body{box-sizing:border-box;background:linear-gradient(145deg,color-mix(in srgb,var(--bot-color) 73%,white),color-mix(in srgb,var(--bot-color) 66%,black));border-color:color-mix(in srgb,var(--bot-color) 47%,white)}
.bot-gear{position:absolute;display:block;box-sizing:border-box;pointer-events:none}
.bot-headpiece{position:absolute;z-index:5;top:53px;left:58px;width:106px;height:86px;pointer-events:none}
.bot-facepiece{position:absolute;z-index:6;top:53px;left:58px;width:106px;height:86px;pointer-events:none}
.gear-goggles,.gear-specs{left:0;right:0;top:40px;height:16px;background:#44453E;border:2px solid #6D706B;border-radius:8px;display:flex;align-items:center;justify-content:center;gap:5px}
.gear-goggles i,.gear-specs i{box-sizing:border-box;width:36px;height:31px;border:3px solid #B9DDE4;border-radius:11px;background:linear-gradient(135deg,#B6F3FF55 22%,#E8FCFFCC 23% 29%,#43C6EB55 30% 75%,#21798C99);box-shadow:0 2px 4px #0008}
.gear-specs{background:#141719;border-color:#555B60}
.gear-specs i{height:26px;border-color:#858F94;border-radius:5px 5px 10px 10px;background:linear-gradient(155deg,#677981,#13191C 60%)}
.gear-mask{left:0;right:0;top:51px;height:30px;border:2px solid #8BA7AC;background:linear-gradient(#ABC2CA,#446772);clip-path:polygon(0 2%,24% 20%,50% 0,76% 20%,100% 2%,84% 68%,67% 99%,33% 99%,16% 68%)}
.gear-mask::after{content:"";position:absolute;inset:12px 29px 6px;border-block:2px solid #24424C}
.gear-prism{left:11px;right:11px;top:31px;height:34px;border:2px solid #C0A2EE;border-radius:14px;background:linear-gradient(110deg,#32235A,#515397,#34255D)}
.gear-prism::after{content:"";position:absolute;left:calc(50% - 9px);top:6px;width:18px;height:18px;transform:rotate(45deg);background:linear-gradient(135deg,#E7D8FF,#9171F4 55%,#4DD7EB);border:1px solid #EEE5FF}
.gear-cap{top:-21px;left:6px;width:91px;height:43px;border:2px solid #9A824D;border-radius:44px 44px 8px 8px;background:radial-gradient(at 45% 95%,#444135,#20211F 71%)}
.gear-cap::after{content:"";position:absolute;left:34px;top:31px;width:69px;height:13px;border-radius:65% 42% 45% 18%;background:#CFB991;border:2px solid #615236;transform:rotate(-5deg)}
.gear-beanie{top:-19px;left:1px;right:1px;height:42px;border:2px solid #777677;border-radius:45px 45px 9px 9px;background:repeating-linear-gradient(90deg,#333438 0 6px,#48494D 6px 8px);box-shadow:inset 0 -12px #202124}
.gear-halo,.gear-void{left:10px;right:10px;top:-22px;height:26px;border:3px solid #F4CD78;border-radius:50%;box-shadow:0 0 12px #E9BD6F77;transform:rotate(-9deg)}
.gear-void{left:28px;right:28px;top:-36px;height:45px;border:0;background:radial-gradient(circle at 37% 30%,#C1A6E7,#64448C 48%,#24163E 77%);box-shadow:0 0 11px #8361B477}
.gear-void::after{content:"";position:absolute;inset:16px -16px;border:2px solid #D6BCF4;border-radius:50%;transform:rotate(-23deg)}
.gear-antenna{left:43px;top:-28px;width:32px;height:32px;border:2px solid #9D90AB;border-radius:4px 4px 65% 65%;background:linear-gradient(145deg,#E2D9EA,#675975);transform:rotate(-28deg)}
.gear-antenna::before{content:"";position:absolute;left:13px;top:-12px;width:3px;height:15px;background:#C5AEE1}
.gear-antenna::after{content:"";position:absolute;left:9px;top:-16px;width:10px;height:10px;border-radius:50%;background:#E7D6FC;box-shadow:0 0 9px #B191F7}
.gear-headset{left:-5px;right:-5px;top:-8px;height:62px;border:5px solid #373D44;border-bottom:0;border-radius:34px 34px 0 0}
.gear-headset i{position:absolute;top:35px;width:15px;height:34px;background:linear-gradient(#666F7A,#242A31);border:2px solid #9AA0A6;border-radius:8px}
.gear-headset i:first-child{left:-8px}.gear-headset i:last-child{right:-8px}
.gear-knight,.gear-crown{top:-21px;left:10px;right:10px;height:44px;clip-path:polygon(0 10%,23% 42%,50% 0,77% 42%,100% 10%,91% 92%,9% 92%);background:linear-gradient(135deg,#F9E7B4,#C29647 45%,#88612E);box-shadow:inset 0 -12px #5B4325}
.gear-knight{top:-15px;left:1px;right:1px;height:38px;clip-path:polygon(0 60%,20% 18%,42% 18%,50% 0,58% 18%,80% 18%,100% 60%,100% 98%,0 98%);background:linear-gradient(135deg,#CBD1D8,#677589 56%,#343B48);box-shadow:inset 0 -6px #191F29}
.bot-body-equipment{position:absolute;inset:3px;box-sizing:border-box;border-radius:14px 14px 19px 19px}
.gear-shield{inset:4px 9px;clip-path:polygon(50% 0,98% 14%,92% 65%,50% 100%,8% 65%,2% 14%);background:linear-gradient(135deg,#CED8DB,#879DA7 50%,#314752)}
.gear-shield::after,.gear-reactor::after{content:"";position:absolute;inset:14px 20px;border-radius:50%;background:#19292D;border:3px solid #BBE3EE}
.gear-cape{inset:-2px -14px -7px;clip-path:polygon(5% 0,50% 16%,95% 0,100% 100%,74% 88%,50% 100%,26% 88%,0 100%);background:linear-gradient(90deg,#98723B,#3B2A1F 25%,#74603B 50%,#3B2A1F 75%,#98723B)}
.gear-cape::after{content:"";position:absolute;top:8px;left:calc(50% - 7px);width:14px;height:14px;background:#EBD7A0;transform:rotate(45deg);border:2px solid #886436}
.gear-apron{inset:0 5px 2px;clip-path:polygon(11% 0,25% 0,33% 20%,67% 20%,75% 0,89% 0,100% 100%,0 100%);background:linear-gradient(150deg,#795B45,#392923)}
.gear-apron::after{content:"";position:absolute;inset:32px 15px 8px;border:1px dashed #E2BA83;border-radius:3px 3px 8px 8px;background:linear-gradient(90deg,#634733 50%,#52392A 50%)}
.gear-reactor{border:3px solid #475F66;background:repeating-linear-gradient(0deg,#213033 0 8px,#293D42 8px 11px)}
.gear-reactor::after{inset:8px 16px;background:radial-gradient(circle,#EDFBFF,#60D8DB 42%,#207482 70%);border-color:#9DE5EF;box-shadow:0 0 10px #59DADC}
.bot-effect{position:absolute;inset:28px 10px 0;display:flex;align-items:center;justify-content:space-between;font-size:39px;color:#DDB85A;pointer-events:none}
.bot-pet{position:absolute;bottom:0;right:0;font-size:57px;filter:drop-shadow(0 5px 3px #0009)}
.case-symbol{font-size:76px;text-align:center;line-height:1.3;padding:12px 0;color:var(--gold)}
.reveal{border:2px solid var(--tier);background:linear-gradient(125deg,#272520,#161719);border-radius:16px;padding:25px;text-align:center;margin:20px 0}
.st-key-case_audio_playback{display:none!important}
.case-reel{position:relative;overflow:hidden;isolation:isolate;border:1px solid #65573D;border-radius:12px;background:#0C0D0E;padding:14px 0;margin-top:20px}
.case-reel::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#0C0D0E 0%,transparent 19%,transparent 81%,#0C0D0E 100%);z-index:1;pointer-events:none}
.reel-marker{position:absolute;inset:0 auto 0 50%;width:2px;background:var(--gold2);transform:translateX(-50%);z-index:2}
.reel-marker::before,.reel-marker::after{content:"";position:absolute;left:50%;transform:translateX(-50%);border:7px solid transparent}
.reel-marker::before{top:0;border-top-color:var(--gold2)}
.reel-marker::after{bottom:0;border-bottom-color:var(--gold2)}
.reel-track{position:relative;left:50%;display:flex;gap:8px;width:max-content;transform:translateX(var(--stop));animation:reel-roll 4.2s cubic-bezier(.08,.64,.11,1) both}
.reel-card{box-sizing:border-box;width:140px;min-height:120px;display:grid;grid-template-rows:44px 1fr auto;place-items:center;text-align:center;padding:8px 7px;border:1px solid #45413A;border-bottom:4px solid var(--tier);border-radius:8px;background:linear-gradient(155deg,#2A2A2A,#171819);font-size:.85rem;line-height:1.12}
.reel-card small{color:var(--tier);margin-top:4px}
.reel-card span{font-size:32px}
.reel-card-winner{animation:reel-winner .35s 4.2s both}
.reveal-after-roll{animation:reveal-drop .38s 4.2s both}
@keyframes reel-roll{from{transform:translateX(-70px)}to{transform:translateX(var(--stop))}}
@keyframes reel-winner{to{border-color:var(--tier);background:#393026}}
@keyframes reveal-drop{from{visibility:hidden;opacity:0;transform:translateY(7px)}to{visibility:visible;opacity:1;transform:translateY(0)}}
.bot-headpiece:has(.gear-halo,.gear-void){animation:gear-hover 3s ease-in-out infinite}
.bot-facepiece:not(:empty){animation:visor-scan 3.4s ease-in-out infinite}
.gear-reactor,.gear-shield{animation:armor-charge 2.6s ease-in-out infinite}
.bot-effect span:not(:empty){animation:effect-orbit 3s ease-in-out infinite alternate}
.bot-effect span:nth-child(2){animation-direction:alternate-reverse}
.bot-pet:not(:empty){animation:pet-hop 2.8s ease-in-out infinite}
@keyframes gear-hover{50%{transform:translateY(-5px) rotate(-5deg)}}
@keyframes visor-scan{50%{filter:brightness(1.35) drop-shadow(0 0 4px var(--gold))}}
@keyframes armor-charge{50%{filter:brightness(1.23)}}
@keyframes effect-orbit{to{transform:translateY(-12px) rotate(24deg) scale(1.17);opacity:.72}}
@keyframes pet-hop{0%,55%,100%{transform:translateY(0)}72%{transform:translateY(-10px) rotate(-7deg)}}
[class*="st-key-clear_"] button{min-width:0}
[class*="st-key-clear_"] button p{white-space:nowrap;overflow:visible;text-overflow:clip}
@media(prefers-reduced-motion:reduce){.case-reel{display:none}}
@media(max-width:740px){[data-testid="stMainBlockContainer"]{padding:4.25rem .9rem 1rem!important}.hero{padding:20px}html{font-size:16px!important}.avatar-scene{min-height:255px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>''', unsafe_allow_html=True)


def item_badge(item):
    tier = ITEMS[item]["rarity"]
    color = RARITIES.get(tier, (0, '#CFB991'))[1]
    return f'<span class="pill" style="color:{color}">{tier}</span>'


def case_reel(result, purchase_id):
    """Build a decorative reel around the already committed drop."""
    winner = result['item']
    _, weights = CASES[result['case']]
    odds = dict(zip(RARITIES, weights))
    eligible = [item for item in ROLL_POOL if odds[ITEMS[item]['rarity']]]
    rng = random.Random(purchase_id)
    winning_index = 29
    drops = rng.choices(eligible, k=winning_index + 5)
    drops[winning_index] = winner
    cards = []
    for index, item in enumerate(drops):
        details = ITEMS[item]
        tier = details['rarity']
        color = RARITIES[tier][1]
        highlight = ' reel-card-winner' if index == winning_index else ''
        cards.append(
            f'<div class="reel-card{highlight}" style="--tier:{color}">'
            f'<span>{details["symbol"]}</span><b>{html.escape(details["name"])}</b>'
            f'<small>{tier}</small></div>'
        )
    stop = -(winning_index * 148 + 70)
    return (f'<div class="case-reel" aria-hidden="true" style="--stop:{stop}px">'
            f'<div class="reel-track">{"".join(cards)}</div>'
            '<div class="reel-marker"></div></div>')


def show_avatar(loadout, color=DEFAULT_AVATAR_COLOR):
    def fitted_gear(slot):
        item = loadout.get(slot)
        if item not in ITEMS or item == 'basic' or ITEMS[item]['slot'] != slot:
            return '◆' if slot == 'body' else ''
        parts = '<i></i><i></i>' if item in ('goggles', 'specs', 'headset') else ''
        base = 'bot-body-equipment' if slot == 'body' else 'bot-gear'
        return f'<span class="{base} gear-{item}">{parts}</span>'

    head, face, body = (fitted_gear(slot) for slot in ('head', 'face', 'body'))
    effect = ITEMS.get(loadout.get('effect',''),{}).get('symbol','')
    pet = ITEMS.get(loadout.get('pet',''),{}).get('symbol','')
    return f'''<div class="avatar-scene" style="--bot-color:{html.escape(color, quote=True)}" role="img" aria-label="Robot wearing {html.escape(', '.join(ITEMS[i]['name'] for i in loadout.values() if i in ITEMS) or 'starter equipment')}">
      <div class="avatar-figure"><div class="bot-effect"><span>{effect}</span><span>{effect}</span></div>
      <div class="bot-headpiece">{head}</div><div class="bot-head"><div class="bot-eyes"><b></b><b></b></div></div>
      <div class="bot-facepiece">{face}</div><div class="bot-body">{body}</div><div class="bot-pet">{pet}</div></div></div>'''


def new_game(topic, difficulty, count):
    pool = [q for q in QUESTIONS if (topic == 'All topics' or topic == q['topic']) and (difficulty == 'All levels' or difficulty == q['difficulty'])]
    selected = random.sample(pool, min(count, len(pool)))
    questions = []
    for q in selected:
        order = list(range(4))
        random.shuffle(order)
        questions.append({**q, 'options': [q['options'][j] for j in order], 'answer':order.index(q['answer'])})
    st.session_state.game = {'id':uuid4().hex,'questions':questions,'index':0,'answers':{},'hints_used':set()}

if 'game' not in st.session_state:
    st.session_state.game = None
if 'reveal' not in st.session_state:
    st.session_state.reveal = None

infinite_coins = st.toggle('∞ Coins', key='infinite_coins',
                           help='Open cases for free without changing your saved coin balance. Resets when the session ends.')
player = profile()
header, balance = st.columns([4,1],vertical_alignment='center')
with header:
    st.markdown('<div class="kicker">PURDUE-INSPIRED · CRYPTOGRAPHY LEARNING</div>', unsafe_allow_html=True)
    st.title('🔐 Boiler Crypto')
with balance:
    st.metric('◈ Coin balance','∞' if infinite_coins else f"{player['coins']:,}")
st.markdown('<div class="brandline"></div>',unsafe_allow_html=True)
nav = st.radio('Navigation',['Play quiz','Case lab','Collection'],horizontal=True,label_visibility='collapsed',key='main_nav')
st.write('')

if nav == 'Play quiz':
    game = st.session_state.game
    if game is None:
        hero, side = st.columns([2.1,1],gap='large')
        with hero:
            st.markdown('<div class="hero"><div class="kicker">PLAY · LEARN · COLLECT</div><h2>Get sharper. Earn your gear.</h2><p>Answer cryptography questions to earn 10 coins per correct answer. Spend coins on collectible cases, then equip the items you unlock.</p></div>',unsafe_allow_html=True)
            st.subheader('Create a quiz')
            topics=['All topics']+sorted({q['topic'] for q in QUESTIONS})
            c1,c2=st.columns(2)
            with c1: topic=st.selectbox('Topic',topics)
            with c2: difficulty=st.selectbox('Difficulty',['All levels','Easy','Medium','Hard'])
            available=sum((topic=='All topics' or q['topic']==topic) and (difficulty=='All levels' or q['difficulty']==difficulty) for q in QUESTIONS)
            count=st.slider('Number of questions',1,max(available,1),min(10,max(available,1))) if available > 1 else 1
            st.caption(f'{available} questions available · No timer · Hints and detailed explanations')
            if st.button('Start quiz',type='primary',use_container_width=True,disabled=not available):
                new_game(topic,difficulty,count)
                st.rerun()
        with side:
            st.markdown(show_avatar(player['equipped'], player['color']),unsafe_allow_html=True)
            st.write('')
            st.caption('YOUR CURRENT LOADOUT')
            c1,c2=st.columns(2)
            c1.metric('Correct answers',player['correct'])
            c2.metric('Items found',len(player['owned'])-1)
    else:
        qs=game['questions']; i=game['index']
        if i>=len(qs):
            score=sum(game['answers'][j]==q['answer'] for j,q in enumerate(qs))
            st.markdown('<div class="kicker">QUIZ COMPLETE</div>',unsafe_allow_html=True)
            st.header('Results & review')
            a,b,c=st.columns(3)
            a.metric('Score',f'{score}/{len(qs)}')
            b.metric('Accuracy',f'{score/len(qs)*100:.0f}%')
            c.metric('Coins earned',f'◈ {score*10}')
            for j,q in enumerate(qs):
                ok=game['answers'][j]==q['answer']
                with st.expander(f"{'✓' if ok else '✕'}  {j+1}. {q['q']}"):
                    st.write('Your answer:',q['options'][game['answers'][j]])
                    st.write('Correct answer:',q['options'][q['answer']])
                    st.write(q['explanation']); st.caption(q['source'])
            left,right=st.columns(2)
            missed=[q for j,q in enumerate(qs) if game['answers'][j]!=q['answer']]
            with left:
                if st.button('Practice missed questions',use_container_width=True,disabled=not missed):
                    st.session_state.game={'id':uuid4().hex,'questions':random.sample(missed,len(missed)),'index':0,'answers':{},'hints_used':set()}
                    st.rerun()
            with right:
                if st.button('New quiz',type='primary',use_container_width=True):
                    st.session_state.game=None;st.rerun()
        else:
            q=qs[i]
            main,sidebar=st.columns([2.4,1],gap='large')
            with main:
                st.markdown(f'<div class="kicker">QUESTION {i+1} OF {len(qs)} · {html.escape(q["difficulty"]).upper()}</div>',unsafe_allow_html=True)
                st.progress(i/len(qs))
                st.header(q['q'])
                st.caption(q['topic'])
                if i in game['answers']:
                    selected=game['answers'][i]
                    if selected==q['answer']:st.success('Correct! +10 coins ◈')
                    else:st.error(f'Correct answer: {q["options"][q["answer"]]}')
                    st.markdown('**Why:** '+q['explanation'])
                    st.caption(q['source'])
                    if st.button('Next question' if i<len(qs)-1 else 'View results',type='primary',use_container_width=True):
                        game['index']+=1;st.rerun()
                else:
                    with st.form(f'question_{i}'):
                        # A hidden label gives screen readers context without a visible outlined header.
                        choice=st.radio('Select your answer',q['options'],index=None,label_visibility='collapsed')
                        submitted=st.form_submit_button('Submit answer',type='primary',use_container_width=True)
                    if submitted:
                        if choice is None:st.warning('Choose one option before submitting.')
                        else:
                            selected=q['options'].index(choice)
                            if selected==q['answer']:
                                reward(f"{game['id']}:{i}")
                            game['answers'][i]=selected
                            st.rerun()
            with sidebar:
                st.markdown('<div class="surface"><div class="kicker">QUIZ PROGRESS</div><p>Answer each question to earn coins. Review explanations as you go.</p></div>',unsafe_allow_html=True)
                if i not in game['answers']:
                    if st.button('Show hint',use_container_width=True):game['hints_used'].add(i)
                    if i in game['hints_used']:st.info('💡 '+q['hint'])
                st.caption(f"{len(game['answers'])}/{len(qs)} completed · {len(game['hints_used'])} hints used")
                if st.button('Exit quiz',use_container_width=True):
                    st.session_state.game=None;st.rerun()

elif nav == 'Case lab':
    st.header('Case lab')
    st.write(f'Spend coins earned in the quiz to unlock avatar gear. Duplicates from paid cases return {DUPLICATE_REFUND} coins. All purchases use in-game coins.')
    left, right = st.columns([1.35, 1], gap='large')
    with left:
        case_name = st.selectbox('Choose a case', CASES, format_func=lambda name: f'{name} · {CASES[name][0]} coins')
        cost, weights = CASES[case_name]
        st.caption({
            'Standard': 'Drops can come from all five rarities.',
            'Premium': 'Guaranteed Rare or higher.',
            'Elite': 'Guaranteed Legendary or Mythic.',
        }[case_name])
        case_sound = st.checkbox('Case sound', value=True, key='case_sound')
        reduce_motion = st.checkbox('Skip reveal animation', key='skip_reveal')
        if 'purchase_id' not in st.session_state:
            st.session_state.purchase_id = uuid4().hex
        result = st.session_state.reveal
        if result is None:
            st.markdown('<div class="surface case-symbol" aria-hidden="true">▣</div>', unsafe_allow_html=True)
            price_label = 'Free' if infinite_coins else f'{cost} coins'
            if st.button(f'Open {case_name} · {price_label}', key=f'open_{st.session_state.purchase_id}',
                         type='primary', use_container_width=True, disabled=not infinite_coins and player['coins'] < cost):
                result = open_case(case_name, st.session_state.purchase_id, infinite_coins=infinite_coins)
                if result is None:
                    st.warning('Your balance changed. Select a case again to refresh it.')
                else:
                    st.session_state.reveal = result
                    st.session_state.animate_reveal = not reduce_motion
                    st.rerun()
            if not infinite_coins and player['coins'] < cost:
                st.info(f'Earn {cost - player["coins"]:,} more coins to open this case.')
        else:
            item = result['item']
            details = ITEMS[item]
            tier_color = RARITIES[details['rarity']][1]
            animate = st.session_state.pop('animate_reveal', False) and not reduce_motion
            animation = ' reveal-after-roll' if animate else ''
            if animate:
                st.markdown(case_reel(result, st.session_state.purchase_id), unsafe_allow_html=True)
            if case_sound and animate:
                project = Path(__file__).parent
                for audio_path in (project / 'assets' / 'case-reel.wav', project / 'case-reel.wav'):
                    try:
                        audio_data = audio_path.read_bytes()
                    except FileNotFoundError:
                        continue
                    if audio_data:
                        with st.container(key='case_audio_playback'):
                            st.audio(audio_data, format='audio/wav', autoplay=True)
                        break
            subtitle = 'Duplicate' if result['duplicate'] else 'New collectible unlocked'
            if result['refund']:
                subtitle += f' · {result["refund"]} coins returned'
            st.markdown(f"""<div class="reveal{animation}" style="--tier:{tier_color}" role="status">
                <div class="kicker">{result['case']} case opened</div>
                <div style="font-size:70px" aria-hidden="true">{details['symbol']}</div>
                <div class="item-title">{html.escape(details['name'])}</div>
                {item_badge(item)}<p>{html.escape(details['description'])}</p>
                <p>{subtitle}</p></div>""", unsafe_allow_html=True)
            equipped = player['equipped'].get(details['slot']) == item
            if st.button('Equipped' if equipped else 'Equip item', disabled=equipped, use_container_width=True):
                if equip(item):
                    st.rerun()
            if st.button('Done', use_container_width=True):
                st.session_state.reveal = None
                st.session_state.purchase_id = uuid4().hex
                st.rerun()
    with right:
        st.subheader(f'{case_name} drop odds')
        for tier, weight in zip(RARITIES, weights):
            color = RARITIES[tier][1]
            st.markdown(f'<div class="item" style="min-height:auto;padding:10px 14px;border-left:4px solid {color}"><b>{tier}</b><span style="float:right;color:{color};font-weight:800">{weight}%</span></div>', unsafe_allow_html=True)
        st.subheader('Available rewards')
        st.caption('25 collectibles across all cases. Each item in a rolled rarity is equally likely.')
        with st.container(height=370, border=True):
            for tier, weight in zip(RARITIES, weights):
                for item in ROLL_POOL:
                    details = ITEMS[item]
                    if details['rarity'] != tier:
                        continue
                    availability = 'In collection' if item in player['owned'] else 'Undiscovered'
                    eligibility = f' · Unavailable in {case_name}' if not weight else ''
                    st.markdown(f"{details['symbol']} **{details['name']}**")
                    st.caption(f"{tier} · {details['slot'].title()} · {availability}{eligibility}")
        with st.expander('Recent drops'):
            history = recent_cases(6)
            if not history:
                st.caption('No cases opened yet.')
            for item, duplicate in history:
                details = ITEMS.get(item)
                label = f"{details['symbol']} **{details['name']}** · {details['rarity']}" if details else item
                st.markdown(label + (' · Duplicate' if duplicate else ''))

else:
    st.markdown('<div class="hero"><div class="kicker">YOUR COLLECTION</div><h2>Build your own companion.</h2><p>Collect distinct equipment across five slots. Use the loadout panel to see your robot change as you equip new items.</p></div>',unsafe_allow_html=True)
    preview,inventory=st.columns([1,1.7],gap='large')
    with preview:
        st.markdown(show_avatar(player['equipped'], player['color']),unsafe_allow_html=True)
        st.write('')
        st.color_picker('Avatar color · Free', player['color'], key='avatar_color',
                        on_change=lambda: set_avatar_color(st.session_state.avatar_color))
        st.subheader('Equipped gear')
        for slot in SLOTS:
            chosen=player['equipped'].get(slot)
            c1,c2=st.columns([1.8,1],gap='small',vertical_alignment='center')
            c1.write(f"**{slot.title()}** · {ITEMS[chosen]['name'] if chosen in ITEMS else 'None'}")
            with c2:
                if st.button('Remove',key=f'clear_{slot}',disabled=not chosen,use_container_width=True):
                    unequip(slot);st.rerun()
    with inventory:
        st.subheader(f"Inventory · {len(player['owned'])-1} items found")
        st.caption('Each case unlocks an item permanently. Equip it in its matching slot; duplicate drops refund coins.')
        for slot in SLOTS:
            st.markdown(f'<div class="kicker">{slot.upper()}</div>',unsafe_allow_html=True)
            items=[item for item in player['owned'] if item in ITEMS and ITEMS[item]['slot']==slot and item!='basic']
            if not items:
                st.caption('No items discovered yet.')
                continue
            for item in sorted(items,key=lambda k: list(RARITIES).index(ITEMS[k]['rarity']) if ITEMS[k]['rarity'] in RARITIES else 0,reverse=True):
                col1,col2=st.columns([3.5,1.2],vertical_alignment='center')
                with col1:
                    st.markdown(f'''<div class="item" style="min-height:80px;padding:12px 15px"><span style="font-size:28px">{ITEMS[item]['symbol']}</span> <b>{ITEMS[item]['name']}</b> {item_badge(item)}<div class="item-meta">{ITEMS[item]['description']}</div></div>''',unsafe_allow_html=True)
                with col2:
                    active=player['equipped'].get(slot)==item
                    if st.button('Equipped' if active else 'Equip',key=f'equip_{item}',disabled=active,use_container_width=True):
                        if equip(item):st.rerun()
    st.caption('Progress resets when you reload the page.')

st.divider()
st.caption('Independent educational project')




