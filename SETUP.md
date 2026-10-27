# Jarvis Setup Guide — Sirf Phone Users Ke Liye

Ye guide Roman Hindi me hai, taaki beginner bhi bina PC ke follow kar sake.

## Pehle Ye Samajh Lo

- **Shell prompt (`$`)** aur **assistant prompt (`JARVIS >`)** alag hain.
- Shell command Termux ke `$` par likhna hai.
- Assistant command Jarvis ke andar, jab wo chal raha ho, tab likhna ya bolna hai.
- File ka naam command nahi hota. Jaise `jarvis_new.py` likhne se file nahi chalegi, usko `python jarvis_new.py` se chalana hota hai.

---

## Tareeka 1: Web Jarvis — 2 Minute, Koi Install Nahi

1. Is repo se `index.html` download karo.
2. Phone ke Chrome me us file ko kholo.
3. Upar Settings wala gear icon dabao.
4. Google AI Studio ki key banao:
   - Chrome me `aistudio.google.com` kholo.
   - Google account se sign in karo.
   - Get API Key dabao, Create API Key dabao, key copy karo.
   - Key ko chat me ya screenshot me mat bhejo.
5. Jarvis ke Settings me key paste karo, model waisa hi rehne do, Save dabao.
6. Upar `AI Brain: ON` dikhna chahiye.
7. Ab try karo: `YouTube par relaxing music chalao` ya `Ek funny story sunao`.

**Agar mic error aaye:**
- Chrome me is site ke liye Mic Allow karo, page reload karo.
- Agar file par mic block ho, to page ko HTTPS wali site par kholo (jaise GitHub Pages).
- Tab bhi likhkar wale commands chalenge.

---

## Tareeka 2: Termux Jarvis — Full Voice Assistant

### Step 1: Termux aur zaroori tools

Termux install karo, phir Termux ke `$` prompt par ye chalao:

```bash
pkg update
pkg install python termux-api mpv yt-dlp git
```

Termux:API app bhi install karo, aur wo Termux ke hi source se hona chahiye (F-Droid wala Termux hai to F-Droid wala Termux:API, GitHub wala Termux hai to GitHub wala Termux:API).

### Step 2: File ko home folder me daalo

Is repo se `jarvis_new.py` download karo aur Termux ke home folder me rakho. Check karo:

```bash
cd ~
ls -lh jarvis_new.py
```

Agar file nahi dikhe to wo Downloads folder me hogi, home me nahi. Tabhi Python `No such file` bolega.

### Step 3: Pehle text mode me test karo

```bash
python jarvis_new.py
```

Andar prompt `JARVIS >` dikhega. Wahan ye likho:

```
check karo
tum kaun ho
```

`check karo` batayega ki kaunsa tool OK hai aur kaunsa MISSING hai. Jo MISSING hai, usko `pkg install` se lao. Yehi tumhara asli bug hoga.

### Step 4: Voice mode

Text kaam kar jaye, tabhi ye chalao:

```bash
python jarvis_new.py mic
```

Mic ke liye Termux ko battery optimisation off rakhna aur Termux khula rakhna zaroori hai.

### Step 5: Contact aur permission

Pehle contact save karo:

```
mummy ka number 9876543210 yaad rakho
```

Phir naam se WhatsApp ya call kar sakte ho. WhatsApp aur Call pehli baar permission poochega. Sirf `haan hamesha` bologe to permission save hogi, warna sirf ek baar ke liye hogi.

WhatsApp me message prefill hoga, Send tumko dabana hoga. Call me dialer khulega, green button tumko dabana hoga.

### Step 6: DeepSeek (Optional, Paid Hai)

DeepSeek sirf tab on karo jab tumko chahiye, kyunki ye paid API hai.

1. `platform.deepseek.com` par API key banao, balance check karo.
2. Phone par hi ye file banao, key chat me mat bhejo:

```bash
nano ~/.jarvis_new_deepseek.env
```

Usme ye likho:

```
DEEPSEEK_API_KEY=tumhari_key_yahan
DEEPSEEK_MODEL=deepseek-chat
```

Save karo, phir:

```bash
chmod 600 ~/.jarvis_new_deepseek.env
```

Jarvis ke andar ye chalao:

```
deepseek key check
deepseek on
deepseek se poochho ki aaj ka mausam kaisa hai
```

Kaam khatam ho to `deepseek off` bol do, taaki balance bache.

---

## Aam Problems Aur Unka Hal

- **File not found:** Tum galat folder me ho. `cd ~` karke `ls` se check karo.
- **Mirror bad / pkg install fail:** Mirror badalna padega, `termux-change-repo` se official mirror chuno, phir `pkg update` karo.
- **Mic nahi sun raha:** Termux:API app missing ya permission off hogi. Text mode me kaam karo, phir voice check karo.
- **Permission command not found:** `permission dikhao` jaise command sirf Jarvis ke andar chalte hain, shell `$` par nahi.
- **Gaana nahi chal raha:** `mpv` aur `yt-dlp` install hai ya nahi, `check karo` se dekho.

---

## Important Safety

- API key, password aur OTP kabhi chat me, screenshot me ya GitHub file me mat daalo.
- Key sirf apne phone ki file ya apne browser ke Settings me rakho.
- Agar key leak ho jaye to turant delete karke nayi banao.
