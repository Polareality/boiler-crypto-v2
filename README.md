# Boiler Crypto V2

A Purdue black-and-gold Streamlit cryptography quiz. Answer correctly to earn 10 coins, open cases, and equip collectibles on the Workshop Bot. The quiz uses a static question bank with topic and difficulty filters, hints, and answer explanations.

## Install and play

Extract the ZIP and open PowerShell in the folder containing `app.py`. With Python installed, run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit opens the quiz in your browser. For a fresh install, the first launch creates `profile.sqlite3` beside `app.py`. This is a local, single-profile app. Sessions launched against the same database share one profile.

## Upgrade a saved profile

1. Stop the old Streamlit app and back up your project folder, including the SQLite database and any SQLite sidecar files.
2. Extract the new project to a separate folder and copy your existing `profile.sqlite3` next to the new `app.py`. If your installation sets `BOILER_PROFILE_DB`, point it to the saved database you intend to use.
3. Install the requirements and launch using the commands above. Open Collection to confirm your loadout and inventory. The ZIP leaves your personal database out.

The upgrade retains coins, correct-answer totals, recorded quiz rewards, collectible IDs, loadouts, and case history. Startup adds a purchase-request table alongside the existing tables. Old color-shop data remains stored in the legacy tables. Restore your backup to roll back to the exact state before the upgrade.

## Cases and collectibles

| Case | Cost | Common | Rare | Epic | Legendary | Mythic |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Standard | 50 | 55% | 28% | 12% | 4% | 1% |
| Premium | 200 | 0% | 60% | 28% | 10% | 2% |
| Elite | 500 | 0% | 0% | 0% | 85% | 15% |

Each case rolls rarity first, then gives every item in that rarity an equal chance. The 25 collectibles span head, face, body, effect, and companion slots. The Workshop Bot is starter gear outside the drop pool. Duplicate drops refund 20 coins. There are no real-money purchases, cash-out, or trading.

Case lab shows the selected case odds above the scrollable catalog. The case reel slows to a stop on your collectible. Skip the reel using the checkbox. Your browser's reduced-motion preference skips the reel and pauses equipped gear animations. The purchase commits before the reveal and can be recovered in Recent drops if you leave the page. Select Done to start another purchase. Balance, inventory, history, and the purchase identifier are committed together in SQLite. Repeated requests with the same identifier return the original result.


Turn on **∞ Coins** at the top left to open any case for free for the current session. These openings save your drops without spending coins or issuing duplicate refunds. Turn it off to use your saved balance again.

In Collection, choose **Avatar color · Free** to change the robot shell. Your preference is saved in the local profile. Case lab has a **Case sound** switch. The original reel audio uses mechanical ticks and a landing chime. Playback depends on your browser's autoplay settings.
