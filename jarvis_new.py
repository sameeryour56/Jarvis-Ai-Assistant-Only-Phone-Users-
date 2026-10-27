#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS NEW v2 - Clean rewrite, purani file ko patch karke nahi banaya gaya
===========================================================================
Purani file me problem kyun aa rahi thi (jo humne theek kiya):
  1. Purani file patch-on-patch badi ho gayi thi, aur Ollama, kai voice
     engine, kai permission sawal ek saath the - ek jagah fail hoti to
     samajh nahi aata kahan atka.
  2. Termux:API app na ho to termux-tts-speak / speech-to-text hang ho
     jata tha. Nayi file pehle tool check karti hai, na mile to turant
     text mode me aa jati hai, hang nahi karti.
  3. Shell prompt ($) aur assistant prompt (JARVIS >) ka confusion tha.
     Nayi file ka prompt saaf alag hai, aur banner me likha hai ki tum
     assistant ke andar ho.
  4. Permission me do-do sawal poochhe jate the, jo confusing tha.
     Nayi file me sirf ek sawal: kar dun? Agar tum "haan hamesha" bologe
     to hi permission save hogi, warna sirf ek baar ke liye hogi.

Run (pehle text me test karo, voice baad me):
  python jarvis_new.py            -> text mode (sabse safe, pehle yahi chalao)
  python jarvis_new.py mic        -> seedha voice mode
  python jarvis_new.py wake       -> standby mode (sirf Jaanu/Jarvis sunega)

Install (sirf jo chahiye):
  pkg install python termux-api mpv yt-dlp git
  # Termux:API app bhi chahiye, Termux ke hi source (F-Droid/GitHub) se.

Nayi files (purani files se alag, taaki purana bug isme na aaye):
  ~/.jarvis_new_contacts.json
  ~/.jarvis_new_permissions.json
  ~/.jarvis_new_deepseek.env   (DEEPSEEK_API_KEY=..., DEEPSEEK_MODEL=deepseek-chat)

Sachai (ye nayi file bhi nahi badal sakti):
  - WhatsApp ka Send button tumko dabana hoga.
  - Call ka green button / dialer ka button tumko dabana hoga, jab tak
    termux-telephony-call permission se seedha na lage.
  - Instagram/YouTube ke andar tap, Back button, aur call cut Termux se
    aam taur par nahi hote. File koshish karegi, fail ho to saaf bolegi.
  - DeepSeek API paid hai, key chat me kabhi mat bhejo.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

NAME = "JARVIS"
VERSION = "NEW v2"
CONTACTS_FILE = os.path.expanduser("~/.jarvis_new_contacts.json")
PERMISSIONS_FILE = os.path.expanduser("~/.jarvis_new_permissions.json")
DEEPSEEK_ENV_FILE = os.path.expanduser("~/.jarvis_new_deepseek.env")
MIC_FILE = os.path.expanduser("~/.jarvis_new_mic.json")

mpv_proc = None
keep_mic_on = False
deepseek_on = False
deepseek_key = ""
deepseek_model = "deepseek-chat"
MODE = "text"


# ---------- safe tools: kabhi hang mat karo ----------

def tool_exists(name):
    return shutil.which(name) is not None


def run(cmd, timeout=15):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "").strip()
    except Exception as e:
        return -1, str(e)


def speak(text):
    print(f"{NAME}: {text}", flush=True)
    if not tool_exists("termux-tts-speak"):
        return
    run(["termux-tts-speak", "-p", "1.4", "-r", "1.0", text], timeout=10)


def listen_once(timeout=20):
    if not tool_exists("termux-speech-to-text"):
        return None
    rc, out = run(["termux-speech-to-text"], timeout=timeout)
    if rc != 0 or not out:
        return None
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            return (data.get("text") or "").strip() or None
        if isinstance(data, list) and data:
            return str(data[0]).strip() or None
    except Exception:
        pass
    return out.strip() or None


def open_url(url):
    if not tool_exists("termux-open"):
        speak("termux-open nahi mila, isliye app/link nahi khol sakti. termux-api install karo.")
        return False
    rc, _ = run(["termux-open", url], timeout=15)
    return rc == 0


def diagnose():
    lines = []
    lines.append(f"JARVIS {VERSION} check:")
    lines.append(f"Python: {sys.version.split()[0]}")
    lines.append(f"python: {'OK' if (tool_exists('python') or tool_exists('python3')) else 'MISSING'}")
    for tool in ("termux-tts-speak", "termux-speech-to-text",
                 "termux-open", "termux-telephony-call", "mpv", "yt-dlp", "git"):
        lines.append(f"{tool}: {'OK' if tool_exists(tool) else 'MISSING'}")
    lines.append(f"Contacts file: {'YES' if os.path.exists(CONTACTS_FILE) else 'NO'}")
    lines.append(f"Permissions file: {'YES' if os.path.exists(PERMISSIONS_FILE) else 'NO'}")
    lines.append(f"DeepSeek key file: {'YES' if os.path.exists(DEEPSEEK_ENV_FILE) else 'NO'}")
    lines.append("Agar koi MISSING hai to wahi tumhara bug hai, usko pkg install se lao.")
    return "\n".join(lines)


# ---------- numbers, contacts, permissions ----------

DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
NUM_WORDS = {"shunya": "0", "zero": "0", "ek": "1", "one": "1", "do": "2", "two": "2",
             "teen": "3", "three": "3", "char": "4", "chaar": "4", "four": "4",
             "panch": "5", "paanch": "5", "five": "5", "chhe": "6", "chhah": "6",
             "six": "6", "saat": "7", "sath": "7", "seven": "7", "aath": "8",
             "eight": "8", "nau": "9", "nine": "9"}
DEV_NUM = {"शून्य": "zero", "एक": "one", "दो": "two", "तीन": "three",
           "चार": "four", "पाँच": "five", "पांच": "five", "छह": "six",
           "सात": "seven", "आठ": "eight", "नौ": "nine"}


def spoken_number(raw):
    if not raw:
        return ""
    s = str(raw).translate(DEV_DIGITS).lower()
    for k, v in DEV_NUM.items():
        s = s.replace(k, v)
    groups = re.findall(r"\d+", s)
    for g in groups:
        if len(g) >= 10:
            return g[-10:]
    toks = re.split(r"[^a-z]+", s)
    out, i = "", 0
    while i < len(toks):
        w = toks[i]
        if w in ("double", "triple") and i + 1 < len(toks) and toks[i + 1] in NUM_WORDS:
            out += NUM_WORDS[toks[i + 1]] * (2 if w == "double" else 3)
            i += 2
        elif w in NUM_WORDS:
            out += NUM_WORDS[w]
            i += 1
        else:
            i += 1
    if len(out) >= 7:
        return out[-10:]
    for g in groups:
        if len(g) >= 7:
            return g[-10:]
    return ""


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_contact(name, number):
    c = load_json(CONTACTS_FILE)
    c[name.strip().lower()] = number[-10:]
    save_json(CONTACTS_FILE, c)


def find_contact(text):
    c = load_json(CONTACTS_FILE)
    for name in sorted(c, key=len, reverse=True):
        if name and name in text:
            return name, c[name]
    return None, None


def is_allowed(category, key):
    return bool(load_json(PERMISSIONS_FILE).get(f"{category}:{key}"))


def grant_permission(category, key):
    p = load_json(PERMISSIONS_FILE)
    p[f"{category}:{key}"] = True
    save_json(PERMISSIONS_FILE, p)


def revoke_all_permissions():
    save_json(PERMISSIONS_FILE, {})


def ask_yes_no(question):
    """Sirf ek sawal. Text me type karo, voice me bolo. 'haan hamesha' = save bhi karo."""
    if MODE == "text":
        print(f"{NAME}: {question} (haan / na / haan hamesha)", flush=True)
        try:
            ans = input("JARVIS > ").strip().lower()
        except Exception:
            return False, False
        if "hamesha" in ans and ("haan" in ans or "han" in ans):
            return True, True
        return any(w in ans for w in ("haan", "han", "yes", "kar do", "theek hai", "ok")), False
    speak(question + " Haan, Na, ya Haan Hamesha bolo.")
    ans = listen_once(timeout=20)
    if not ans:
        return False, False
    a = normalize(ans)
    if "hamesha" in a and ("haan" in a or "han" in a):
        return True, True
    if any(w in a for w in ("nahi", "no", "mat karo")):
        return False, False
    return any(w in a for w in ("haan", "han", "yes", "kar do", "theek hai", "ok")), False


def permission_gate(category, key, label, detail=""):
    if is_allowed(category, key):
        speak(f"{label} ki permission pehle se hai, seedha kar rahi hoon.")
        return True
    ok, always = ask_yes_no(f"{label} {detail} kar dun?")
    if not ok:
        speak("Theek hai, ye kaam nahi kar rahi hoon.")
        return False
    if always:
        grant_permission(category, key)
        speak("Permission hamesha ke liye save ho gayi hai.")
    return True


def normalize(text):
    x = str(text or "").translate(DEV_DIGITS).lower()
    rep = {"कॉल": "call", "फ़ोन": "phone", "फोन": "phone",
           "व्हाट्सऐप": "whatsapp", "व्हाट्सएप": "whatsapp",
           "रील्स": "reels", "रील": "reel", "यूट्यूब": "youtube",
           "चलाओ": "chalao", "चला दो": "chala do", "खोलो": "kholo",
           "खोल": "kholo", "मम्मी": "mummy", "कहानी": "story",
           "सुनाओ": "sunao", "गाना": "gaana", "संगीत": "music",
           "ईमेल": "email", "कैलेंडर": "calendar", "जोक": "joke",
           " कि ": " ki ", " की ": " ki ", " को ": " ko ",
           " लगाओ": " lagao", " करो": " karo", " भेजो": " bhejo",
           " काटो": " kato", " वापस": " wapas", " पीछे": " peeche",
           " म्यूट": " mute", " अनम्यूट": " unmute", " चालू": " chalu",
           " बंद": " band"}
    for k, v in rep.items():
        x = x.replace(k, v)
    return x


# ---------- DeepSeek ----------

def load_deepseek_config():
    global deepseek_key, deepseek_model
    deepseek_key = ""
    deepseek_model = "deepseek-chat"
    try:
        with open(DEEPSEEK_ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == "DEEPSEEK_API_KEY":
                    deepseek_key = v
                elif k == "DEEPSEEK_MODEL":
                    deepseek_model = v or "deepseek-chat"
    except Exception:
        pass
    return bool(deepseek_key)


def ask_deepseek(question):
    if not deepseek_key:
        return None
    payload = {"model": deepseek_model,
               "messages": [{"role": "system", "content": "Tum JARVIS ho, friendly Hindi/Hinglish voice assistant. Chhota, saaf, bolne layak jawab do."},
                            {"role": "user", "content": question}],
               "temperature": 0.7, "max_tokens": 500}
    try:
        req = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + deepseek_key},
            method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices") or []
        if choices:
            return ((choices[0].get("message") or {}).get("content") or "").strip() or None
        return None
    except urllib.error.HTTPError as e:
        print(f"DeepSeek error: HTTP {e.code} (401=galat key, 402=balance khatam, 429=zyada request)", flush=True)
        return None
    except Exception as e:
        print(f"DeepSeek error: {type(e).__name__}", flush=True)
        return None


# ---------- music ----------

def stop_music():
    global mpv_proc
    if mpv_proc is not None:
        try:
            mpv_proc.terminate()
        except Exception:
            pass
        mpv_proc = None
    run(["pkill", "mpv"], timeout=5)


def play_music(query):
    global mpv_proc
    if not tool_exists("mpv") or not tool_exists("yt-dlp"):
        speak("mpv ya yt-dlp nahi mila, isliye YouTube search khol rahi hoon, wahan video par tap karo.")
        open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
        return False
    stop_music()
    print(f"Gaana dhoond rahi hoon: {query} ...", flush=True)
    rc, url = run(["yt-dlp", "-f", "bestaudio", "--get-url", f"ytsearch1:{query}"], timeout=40)
    if rc != 0 or not url:
        speak("Gaana nahi mila, YouTube search khol rahi hoon.")
        open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(query))
        return False
    try:
        mpv_proc = subprocess.Popen(["mpv", "--no-video", "--really-quiet", url.splitlines()[0].strip()],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        if mpv_proc.poll() is not None:
            speak("Gaana shuru nahi hua, mpv check karo.")
            return False
        speak(f"Ye lo, {query} chal raha hai.")
        return True
    except Exception:
        speak("mpv chalane me dikkat aayi.")
        return False


def try_system_key(keyevent, label):
    rc, _ = run(["input", "keyevent", str(keyevent)], timeout=10)
    if rc == 0:
        speak(f"{label} kar diya hai.")
        return True
    speak(f"{label} Termux se nahi hua. Android ne permission nahi di, haath se {label.lower()} karo.")
    return False


STORIES = {
    "horror": "Ek purane ghar me raat ko chalne ki awaaz aati thi. Riya ne andar jaakar dekha to ek purani photo thi, jiski aankhen hil gayi. Tab ek dheemi awaaz aayi, mat daro, main sirf apni kahani sunana chahti hoon. Us raat ke baad gaon walon ne milkar us ghar ko dobara roshan kiya.",
    "bedtime": "Chandni raat me ek chhota khargosh ghar wapas ja raha tha. Raste me use ek thaka hua jugnu mila. Khargosh ne kaha, aaram karo, subah sab theek ho jayega. Dono ne taare dekhe aur dheere dheere neend ki duniya me chale gaye. Tum bhi aankhen band karo, shubh ratri.",
    "funny": "Ek tota apne malik ka phone utha kar bola, hello, main tota bol raha hoon. Doosri taraf se awaaz aayi, aaj khana kaun banayega. Tota bola, jo pehle hassega, wahi banayega. Malik ne hasna roka, lekin tota zor se hasne laga, aur aakhir me malik bhi has pada.",
}
JOKES = [
    "Teacher ne poochha, homework kyun nahi kiya. Bachha bola, kyunki mera pen bhi so gaya tha.",
    "Maine apne phone se poochha, tum smart ho. Phone bola, charger lagao, phir baat karte hain.",
]


def do_whatsapp(text):
    body = text.split(" ki ", 1)[1].strip() if " ki " in text else ""
    name, number = find_contact(text)
    num = spoken_number(text) or ""
    if not name and len(num) >= 10:
        number = num[-10:]
    if not number:
        speak("Number nahi mila. Pehle bolo: uska naam ka number yaad rakho.")
        return False
    if not permission_gate("whatsapp", name or number, f"{name or number} ko WhatsApp", f"message: {body or 'Hi'}"):
        return False
    url = "https://wa.me/91" + number + "?text=" + urllib.parse.quote(body or "Hi")
    if open_url(url):
        speak("WhatsApp khol diya hai, message likha hua milega. Send ka button tumko dabana hoga.")
        return True
    speak("WhatsApp kholne me dikkat aayi.")
    return False


def do_call(text):
    name, number = find_contact(text)
    num = spoken_number(text) or ""
    if not name and len(num) >= 10:
        number = num[-10:]
    if not number:
        speak("Number nahi mila. Pehle contact save karo.")
        return False
    if not permission_gate("call", name or number, f"{name or number} ko call"):
        return False
    rc, _ = run(["termux-telephony-call", number], timeout=15)
    if rc == 0:
        speak(f"{name or number} ko call laga rahi hoon.")
        return True
    if open_url("tel:" + number):
        speak("Dialer khol diya hai, number bhara hua hai, green call button dabao.")
        return True
    speak("Call lagane me dikkat aayi, Termux:API aur CALL_PHONE permission check karo.")
    return False


# ---------- main command routing (saaf order) ----------

def handle(text_raw):
    global keep_mic_on, deepseek_on
    text = normalize(text_raw)
    print(f"Tumne kaha: {text_raw}", flush=True)

    if "check karo" in text or "diagnose" in text:
        print(diagnose(), flush=True)
        speak("Check poora ho gaya hai, upar wali list me MISSING wali cheez hi bug hai.")
        return "active"
    if "help" in text or "kya kar sakti ho" in text:
        speak("Main ye kar sakti hoon: check karo, gaana play karo, music band karo, youtube kholo, instagram reel chalao, whatsapp, call, deepseek on, permission dikhao, mic mute karo, aur kahani sunana.")
        return "active"
    if any(w in text for w in ("mic mute karo", "mic band karo", "mic off karo")):
        speak("Mic mute kar rahi hoon. Wapas bulane ke liye Jarvis ya Jaanu bolo.")
        return "standby"
    if any(w in text for w in ("mic unmute karo", "mic on karo", "mic chalu karo")):
        speak("Mic unmute ho gaya hai, batao kya karna hai?")
        return "active"
    if "mic on rakho" in text or "mic hamesha on rakho" in text:
        keep_mic_on = True
        try:
            save_json(MIC_FILE, {"keep_mic_on": True})
        except Exception:
            pass
        speak("Mic on hi rakha hai, Termux khula rahe to sunti rahungi.")
        return "active"
    if "voice on" in text:
        return "voice"

    if "permission" in text:
        if "dikhao" in text or "kya hai" in text or "batao" in text:
            perms = load_json(PERMISSIONS_FILE)
            speak("Saved permission ye hai: " + ", ".join(sorted(perms.keys())) + "." if perms else "Abhi koi saved permission nahi hai.")
            return "active"
        if "wapas lo" in text or "hatao" in text:
            name2, _ = find_contact(text)
            if name2:
                p = load_json(PERMISSIONS_FILE)
                for k in list(p):
                    if k.endswith(":" + name2):
                        p.pop(k, None)
                save_json(PERMISSIONS_FILE, p)
                speak(f"{name2} ki permission wapas le li hai.")
            else:
                revoke_all_permissions()
                speak("Saari permission wapas le li hai.")
            return "active"
        if "de do" in text:
            cat = "whatsapp" if "whatsapp" in text else ("call" if "call" in text else None)
            name2, _ = find_contact(text)
            if cat and name2:
                grant_permission(cat, name2)
                speak(f"{name2} ko {cat} ki permission save ho gayi hai.")
            else:
                speak("Pehle uska naam aur number save karo, phir permission de paungi.")
            return "active"

    m = re.match(r"(.+?) ka number (.+?) (yaad rakho|save karo|save kar lo)", text)
    if m:
        nm = re.sub(r"jarvis|please|ko", "", m.group(1)).strip()
        num = spoken_number(m.group(2))
        if len(num) >= 7 and nm:
            save_contact(nm, num)
            speak(f"Yaad rakh liya, {nm} ka number {num} save ho gaya.")
        else:
            speak("Number poora nahi mila, dobara number ke saath bolo.")
        return "active"

    if "wapas jao" in text or "back jao" in text or "peeche jao" in text:
        try_system_key(4, "Back")
        return "active"
    if "music band karo" in text or "gaana band karo" in text:
        stop_music()
        speak("Music band kar diya.")
        return "active"
    if ("gaana" in text or "song" in text or "music" in text) and ("chalao" in text or "play" in text or "chala do" in text):
        q = (text.replace("youtube par", "").replace("youtube pe", "")
             .replace("gaana", "").replace("song", "").replace("music", "")
             .replace("chalao", "").replace("play karo", "").replace("play", "")
             .replace("chala do", "").replace("ek", "").replace("doosra", "")
             .replace("dusra", "").strip()) or "relaxing music"
        play_music(q)
        return "active"
    if "youtube" in text:
        if "kholo" in text:
            open_url("https://www.youtube.com/")
            speak("YouTube khol diya hai.")
        else:
            q = text.replace("youtube par", "").replace("youtube pe", "").replace("youtube", "").replace("chalao", "").replace("play karo", "").strip()
            open_url("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q or "music"))
            speak("YouTube search khol diya hai, video par tap karo.")
        return "active"
    if "instagram" in text or "reel" in text:
        if "kholo" in text and "reel" not in text:
            open_url("https://www.instagram.com/")
            speak("Instagram khol diya hai.")
        else:
            speak("Instagram Reels khol rahi hoon, reel par tap tumko karna hoga.")
            open_url("https://www.instagram.com/reels/")
        return "active"
    if "whatsapp" in text or "message bhejo" in text:
        if "kholo" in text:
            open_url("https://wa.me/")
            speak("WhatsApp khol diya hai.")
        else:
            do_whatsapp(text)
        return "active"
    if "call cut karo" in text or "call kato" in text:
        try_system_key(6, "Call cut")
        return "active"
    if "call" in text or "phone karo" in text:
        do_call(text)
        return "active"

    if "deepseek on" in text:
        if load_deepseek_config():
            deepseek_on = True
            speak(f"DeepSeek on ho gaya hai, model {deepseek_model} se jawab dungi.")
        else:
            speak("DeepSeek key nahi mili. Pehle ~/.jarvis_new_deepseek.env me key daalo, phir deepseek reload bolo.")
        return "active"
    if "deepseek off" in text:
        deepseek_on = False
        speak("DeepSeek off ho gaya hai.")
        return "active"
    if "deepseek reload" in text or "deepseek key check" in text or "deepseek check" in text:
        if load_deepseek_config():
            speak(f"DeepSeek key mili hui hai, model {deepseek_model} hai. Key kabhi bolkar nahi bataungi.")
        else:
            speak("DeepSeek key nahi mili hai.")
        return "active"
    if "deepseek se poochho" in text:
        q = text.split("deepseek se poochho", 1)[1].strip(" ki ").strip()
        if not q:
            speak("DeepSeek se kya poochhun? Sawal bhi bolo.")
            return "active"
        if not load_deepseek_config():
            speak("DeepSeek key nahi mili, pehle key file me daalo.")
            return "active"
        ans = ask_deepseek(q)
        speak(ans if ans else "DeepSeek se jawab nahi mila. Key, balance ya internet check karo.")
        return "active"

    if "tum kaun ho" in text or "tumhara naam" in text:
        speak(f"Main {NAME} hoon, tumhara naya Termux assistant. Main insaan nahi hoon.")
        return "active"
    if "time" in text or "baj rahe" in text:
        import datetime
        speak("Abhi time hai " + datetime.datetime.now().strftime("%I:%M %p") + ".")
        return "active"
    if "joke" in text or "hasao" in text:
        import random
        speak(random.choice(JOKES))
        return "active"
    if "story" in text or "kahani" in text:
        key = "horror" if "horror" in text or "bhoot" in text else ("bedtime" if ("sone" in text or "bedtime" in text) else "funny")
        speak(STORIES[key])
        return "active"
    if "band karo" in text:
        speak("Mic mute kar rahi hoon. Wapas bulane ke liye Jarvis bolo.")
        return "standby"
    if "exit karo" in text or "program band karo" in text:
        speak("Theek hai, bye bye.")
        return "exit"

    if deepseek_on:
        if load_deepseek_config():
            ans = ask_deepseek(text_raw)
            if ans:
                speak(ans)
                return "active"
            speak("DeepSeek se jawab nahi mila. Key, balance ya internet check karo.")
            return "active"
        speak("DeepSeek on hai lekin key nahi mili.")
        return "active"
    speak("Samajh nahi aaya. Pehle 'check karo' likho, phir try karo: gaana play karo, whatsapp kholo, ya deepseek on bolo.")
    return "active"


def text_loop():
    global MODE
    MODE = "text"
    print("Typing mode. Tum ASSISTANT ke andar ho, shell ($) me nahi.", flush=True)
    print("Exit ke liye 'exit karo' likho. Voice me jaane ke liye 'voice on' likho.", flush=True)
    while True:
        try:
            t = input("JARVIS > ").strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"
        if not t:
            continue
        result = handle(t)
        if result in ("exit", "voice", "standby"):
            return result


def active_loop():
    global MODE, keep_mic_on
    MODE = "voice"
    try:
        keep_mic_on = bool(load_json(MIC_FILE).get("keep_mic_on"))
    except Exception:
        pass
    if not tool_exists("termux-speech-to-text"):
        print("Voice tool nahi mila, isliye text mode me ja rahi hoon.", flush=True)
        return "text"
    print("Mic ACTIVE hai. 'mic mute karo' bolkar mute karo.", flush=True)
    empty = 0
    while True:
        heard = listen_once()
        if not heard:
            empty += 1
            if not keep_mic_on and empty >= 3:
                speak("Tum chup ho, isliye mic mute kar rahi hoon. Wapas bulane ke liye Jarvis bolo.")
                return "standby"
            if keep_mic_on and empty >= 10:
                speak("Lambi chuppi hai, standby me ja rahi hoon, wake word sunti rahungi.")
                return "standby"
            continue
        empty = 0
        result = handle(heard)
        if result in ("standby", "exit", "text"):
            return result


def standby_loop():
    global MODE
    MODE = "voice"
    print("Mic MUTE (standby) hai. Sirf Jarvis / Jaanu / mic unmute karo sun rahi hoon.", flush=True)
    if not tool_exists("termux-speech-to-text"):
        print("Voice tool nahi mila, text mode me ja rahi hoon.", flush=True)
        return "text"
    while True:
        heard = listen_once()
        if not heard:
            continue
        text = normalize(heard)
        if any(w in text for w in ("jarvis", "jaanu", "baat karo", "mic unmute karo", "mic on karo")):
            speak("Haan, main sun rahi hoon, batao kya karna hai?")
            return "active"
        print(f"(standby me ignore kiya: {heard})", flush=True)


def main():
    global MODE
    mode = sys.argv[1] if len(sys.argv) > 1 else "text"
    print(f"=== JARVIS {VERSION} - NEW, CLEAN ===", flush=True)
    print("Pehle TEXT me test karo. Kaam kare to hi voice me jao.", flush=True)
    print("Commands: check karo / gaana play karo / whatsapp / call / reel / deepseek on / permission dikhao", flush=True)
    load_deepseek_config()
    try:
        if mode == "mic":
            state = "active"
            speak("Namaste, main JARVIS hoon, mic on hai.")
        elif mode == "wake":
            state = "standby"
            speak("Main JARVIS hoon, standby me hoon, mujhe bulane ke liye Jarvis bolo.")
        else:
            state = "text"
            speak("Namaste, main JARVIS hoon, text mode me hoon.")
        while True:
            if state == "text":
                state = text_loop()
                if state == "voice":
                    state = "active"
            elif state == "active":
                state = active_loop()
            elif state == "standby":
                state = standby_loop()
            else:
                break
    except KeyboardInterrupt:
        print("\nBye bye.", flush=True)
        stop_music()


if __name__ == "__main__":
    main()
