<div align="center">

![Jarvis Banner](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=JARVIS%20%7C%20Phone%20Users&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=38)

# **Jarvis AI Assistant — Only Phone Users**

### **Welcome my Jarvis Guide Setup**

**No PC needed. Sirf phone se Jarvis chalao.**

![Phone Only](https://img.shields.io/badge/Phone_Only-Yes-00D5FF?style=for-the-badge)
![Web Jarvis](https://img.shields.io/badge/Web_Jarvis-Single_HTML-7B2FF7?style=for-the-badge&logo=googlechrome&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-Python-000000?style=for-the-badge&logo=android&logoColor=white)
![Google AI Studio](https://img.shields.io/badge/Google_AI_Studio-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)

> 📚 **SEbooksaller** — Hindi Ebooks, **₹49 se** shuru — [Store kholo](https://muse.ai/s/ebook-store-xhc63xfuxrsv2xn/3kZAE072X8CAfs2-CmlALWhXAlwa2-CjL0yoMypvr_Y)

</div>

---

## **Ye Repo Kis Ke Liye Hai?**

**Sirf phone users ke liye.** Agar tumhare paas PC/laptop nahi hai, tab bhi tum apna personal Jarvis assistant phone par chala sakte ho.

Is repo me **2 tareeke** hain, dono phone par kaam karte hain:

| **Tareeka** | **Kya Chahiye** | **Time** | **Best Kis Ke Liye** |
|---|---|---|---|
| **1. Web Jarvis** | Sirf Chrome | **2 minute** | **Beginner, sabse aasan** |
| **2. Termux Jarvis** | Termux app | **10-15 minute** | **Voice, music, WhatsApp, call** |

---

## **Tareeka 1: Web Jarvis (Sabse Aasan)**

**File:** `index.html` — ek hi file, koi install nahi.

1. Repo se `index.html` download karo.
2. Phone ke **Chrome** me kholo.
3. **Settings (⚙️)** dabao.
4. **Google AI Studio** ki API key daalo aur Save karo.
5. Bolo ya likho, jaise: *YouTube par relaxing music chalao*, *Ek horror story sunao*.

**Bina key ke bhi** simple commands chalenge, lekin natural baat samajhne ke liye key chahiye. Key sirf tumhare browser me save hoti hai, is repo me nahi.

**Detail guide:** [SETUP.md](SETUP.md) dekho.

---

## **Tareeka 2: Termux Jarvis (Full Voice Assistant)**

**File:** `jarvis_new.py` — clean, naya version.

1. Termux install karo (Termux ke hi source se, F-Droid ya GitHub).
2. Termux me ye chalao:
```bash
pkg install python termux-api mpv yt-dlp git
```
3. Is repo se `jarvis_new.py` apne home folder me daalo.
4. Pehle text mode me test karo:
```bash
python jarvis_new.py
```
5. Andar `check karo` likho — jo tool MISSING dikhe, wahi asli problem hai.
6. Text kaam kar jaye, tabhi voice mode me jao:
```bash
python jarvis_new.py mic
```

**Detail guide:** [SETUP.md](SETUP.md) dekho.

---

## **Jarvis Kya-Kya Kar Sakta Hai?**

- **YouTube** search kholna, music chalana
- **Instagram Reels** page kholna
- **WhatsApp** message prefill karna
- **Call** ke liye dialer kholna
- **Stories, jokes, time** batana
- **Contacts** yaad rakhna, naam se call/WhatsApp karna
- **DeepSeek / Gemini** se sawaalon ke jawab dena (key ke saath)

---

## **Sachai Note — Jo Jarvis Nahi Kar Sakta**

Ye baat pehle se saaf rakhna zaroori hai, taaki galat ummeed na rahe:

- **WhatsApp ka Send button tumko dabana hoga.** Koi website ya Termux app bina tumhare tap ke message send nahi kar sakti.
- **Call ka green button tumko dabana hoga**, jab tak Termux direct call permission se na lage.
- **YouTube / Instagram ke andar ka tap, play ya pause** is page se control nahi hoga.
- **API key kabhi chat me ya screenshot me mat bhejo.** Agar leak ho jaye to delete karke nayi banao.

---

## **Files Is Repo Me**

- `index.html` — Web Jarvis, Google AI Studio wala (main file)
- `google_ai_studio_jarvis.html` — Wahi web Jarvis, original naam se
- `jarvis_new.py` — Termux Jarvis, clean version
- `SETUP.md` — Phone par step-by-step setup guide (Roman Hindi)
- `README.md` — Ye file

---

## **Repo Ko Achha Kaise Chalayein?**

Ek achha repo sirf file daalne se nahi chalta. Is repo ko achha banane ke liye ye kiya gaya hai:

- **Saaf naam aur description:** Phone users ke liye hi hai, ye pehli line me saaf hai.
- **Working files:** Khali README nahi, chalane wali HTML aur Python file dono hain.
- **Step-by-step guide:** Beginner bhi bina PC ke follow kar sake.
- **Sachai note:** Jo nahi ho sakta, wo pehle se likha hai, taaki user trust kare.

Stars aur traffic time ke saath aate hain, jab log repo ko kaam ka samjhenge aur share karenge. Koi bhi repo raat bhar me famous hone ka guarantee nahi de sakta.

---

<div align="center">

**Made for phone users, by a phone user.**

![Footer](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer)

</div>
