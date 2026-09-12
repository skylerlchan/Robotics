# Startup Name Generation & Screening: Programmatic Tooling Research

**Research compiled: April 17, 2026, 1:19 AM ET**

---

## Table of Contents

1. [Domain Availability Checking from CLI](#1-domain-availability-checking-from-cli)
2. [Name Availability Screening Tools](#2-name-availability-screening-tools)
3. [Trademark Search: Programmatic Access](#3-trademark-search-programmatic-access)
4. [Brand Name Generators & AI Naming Tools](#4-brand-name-generators--ai-naming-tools)
5. [Professional Naming Agency Generative Processes](#5-professional-naming-agency-generative-processes)
6. [Phonetic Symbolism: Complete Sound-Meaning Map](#6-phonetic-symbolism-complete-sound-meaning-map)
7. [Architecture for a Name Generation & Evaluation Skill](#7-architecture-for-a-name-generation--evaluation-skill)

---

## 1. Domain Availability Checking from CLI

Three methods, ranked from most reliable to fastest.

### Method 1: `whois` (Most Reliable)

Available natively on macOS and Linux. The gold standard for definitive availability checks.

**Check a single domain:**
```bash
whois example.com
```

**Parse for availability** (`.com` domains use Verisign which returns "No match" for unregistered domains):
```bash
whois somename.com 2>&1 | grep -i "No match"
# If output: "No match for domain "SOMENAME.COM"." --> domain is available
# If no output (or shows "Domain Name: SOMENAME.COM") --> domain is taken
```

**Batch check script:**
```bash
for name in "alpha" "beta" "gamma" "delta"; do
  result=$(whois "${name}.com" 2>&1 | grep -ci "No match")
  if [ "$result" -gt 0 ]; then
    echo "AVAILABLE: ${name}.com"
  else
    echo "TAKEN: ${name}.com"
  fi
  sleep 1  # rate limit to avoid getting blocked
done
```

**Caveats:**
- Whois output is **not standardized** across TLDs. `.com`/`.net` return "No match for", `.org` returns "NOT FOUND", `.io` returns "is available" ([LinuxConfig](https://linuxconfig.org/check-domain-name-availability-with-bash-and-whois))
- Rate limited: Verisign will temporarily block you after ~50 rapid queries
- Some registrars front-run whois queries (rare but documented)

### Method 2: RDAP (Modern, Structured, Free API)

RDAP (Registration Data Access Protocol) is the IETF-standard replacement for WHOIS. Returns machine-readable JSON. No authentication required ([RDAP.org](https://about.rdap.org/)).

**Check a single domain:**
```bash
# Returns HTTP 200 with JSON if registered, HTTP 404 if available
curl -sL -o /dev/null -w "%{http_code}" "https://rdap.org/domain/somename.com"
# 200 = registered, 404 = available
```

**Get registration details:**
```bash
curl -sL "https://rdap.org/domain/google.com" | python3 -m json.tool
```

**Batch check with RDAP (faster, structured):**
```bash
for name in "alpha" "beta" "gamma" "delta"; do
  code=$(curl -sL -o /dev/null -w "%{http_code}" "https://rdap.org/domain/${name}.com")
  if [ "$code" = "404" ]; then
    echo "AVAILABLE: ${name}.com"
  else
    echo "TAKEN: ${name}.com"
  fi
done
```

**Advantages over whois:**
- Structured JSON output (no parsing text)
- Standard HTTP status codes (404 = available)
- No authentication needed
- Same bootstrap server works for all TLDs

**CLI client:** [OpenRDAP](https://www.openrdap.org/) provides a dedicated RDAP command-line client.

### Method 3: `dig` (Fastest, Least Reliable)

DNS lookup -- instant but only tells you if the domain has active DNS records, not whether it's registered.

```bash
dig somename.com +short
# Empty output = possibly available (but could be registered with no DNS)
# IP address output = definitely registered
```

**Use case:** Fast pre-filter. If `dig` returns an IP, the domain is definitely taken. If empty, follow up with `whois` or RDAP to confirm.

### Method 4: Third-Party Free APIs

**Who-Dat** ([GitHub](https://github.com/Lissy93/who-dat)): Free, no-CORS WHOIS/RDAP lookup API. Can be self-hosted or used at their public endpoint.

**domain-check CLI** ([Terminal Trove](https://terminaltrove.com/domain-check/)): A fast CLI tool that uses RDAP and WHOIS together.

### Recommended Approach for a Skill

Use a tiered approach:
1. **Fast filter with `dig`** -- eliminate obviously taken domains instantly
2. **Confirm with RDAP** -- structured JSON, HTTP 404 = available
3. **Final verify with `whois`** -- for edge cases or TLDs where RDAP coverage is incomplete

---

## 2. Name Availability Screening Tools

### Browser-Based Tools (No API)

| Tool | What It Checks | Notes |
|---|---|---|
| [Namechk](https://namechk.com/) | Username availability across 100+ social platforms + domains | Green = available, dim = taken. No API. |
| [Namecheckr](https://www.namecheck.com/en/) | Domains + major social platforms | Cleaner interface, fewer platforms than Namechk |
| [Startup Name Check](https://startupnamecheck.com/) | Domain, social media, local presence | Uses AI analysis of brand presence + real-time DNS probe ([Product Hunt](https://www.producthunt.com/products/startup-name-check)) |
| [KnowEm](https://knowem.com/) | 500+ social networks + USPTO trademark database | Most comprehensive for social handle checks |
| [BrandSearches](https://brandsearches.pixstru.com/) | Domains (.com, .in, .ai), social media, local presence | Uses Gemini AI for brand presence analysis |
| [Nameboy](https://www.nameboy.com/) | Domain name generation + availability | One of the oldest tools, focuses on domain combos |

### What Can Be Done from CLI

**Domain checking:** Fully automatable (see Section 1 above).

**Social media handle checking:** No free bulk API exists. You can:
- Check Twitter/X: `curl -sL -o /dev/null -w "%{http_code}" "https://twitter.com/somename"` (200 = taken, 404 = available) -- but rate limited and unreliable due to login walls
- Most social platforms block automated handle checking. Namechk does it through browser automation

**The practical CLI approach:**
1. Domain availability -- fully scriptable via RDAP/whois
2. Social handles -- use Namechk/KnowEm in browser (no reliable free CLI method)
3. Trademark -- scriptable via APIs (see Section 3)
4. State business registry -- varies by state, most require manual web search

### For the Skill

Automate domain and trademark checking. For social media, output a link to Namechk with the name pre-populated: `https://namechk.com/?q=YOURNAME`

---

## 3. Trademark Search: Programmatic Access

### The USPTO Landscape (as of 2026)

TESS (the old trademark search system) was retired November 30, 2023. It was replaced by the cloud-based [Trademark Search](https://tmsearch.uspto.gov/) at tmsearch.uspto.gov ([Signa Blog](https://signa.so/blog/tess-is-gone-how-to-search-trademarks)).

The USPTO Open Data Portal is migrating to [data.uspto.gov](https://data.uspto.gov/) with the legacy developer.uspto.gov portal scheduled for decommission by April 20, 2026 ([USPTO Developer Portal](https://developer.uspto.gov/api-catalog)).

### Option 1: USPTO TSDR API (Official, Free, Requires API Key)

The Trademark Status & Document Retrieval API provides programmatic access to trademark case status, documents, and images ([USPTO TSDR](https://developer.uspto.gov/api-catalog/tsdr-data-api)).

**Limitations:** This is a **status retrieval** API, not a search API. You need to already know the serial number or registration number. It answers "what is the status of trademark #X?" not "does the word 'Alpha' exist as a trademark?"

**Rate limit:** 60 requests per API key per minute.

**To get an API key:** Email TEAS@uspto.gov or register at the developer portal.

```bash
# Example: Get status of a known trademark by serial number
curl -sL "https://tsdrapi.uspto.gov/ts/cd/casestatus/sn78787878/info.json" \
  -H "USPTO-API-KEY: YOUR_KEY"
```

### Option 2: Marker API (Third-Party, Free Tier)

[Marker API](https://markerapi.com/) provides actual trademark **search** functionality with a free tier.

**Pricing:**
- Free: 1,000 searches/month
- $25/month: 25,000 searches
- $100/month: 10,000,000 searches

**Endpoints:**
- Trademark Search (search by word mark)
- Serial Number Search
- Description Search
- Owner Search
- Expiration Search

**Supports wildcard searches** using asterisks and filtering by status (active/all).

```bash
# Example: Search for a trademark (requires username/password from registration)
curl "https://markerapi.com/api/v2/trademarks/mark/alpha/status/all/username/YOUR_USER/password/YOUR_PASS"
```

### Option 3: RapidAPI USPTO Trademark API

Available on RapidAPI marketplace. Provides search by mark name.

```bash
curl --request GET \
  --url "https://uspto-trademark.p.rapidapi.com/v1/trademarkSearch/alpha/active" \
  --header "x-rapidapi-host: uspto-trademark.p.rapidapi.com" \
  --header "x-rapidapi-key: YOUR_KEY"
```

### Option 4: Direct Web Scraping of tmsearch.uspto.gov

The new trademark search is a web app. It can potentially be scraped using headless browsers (Playwright, Puppeteer), though this is against USPTO's terms of service and fragile.

### Option 5: Trademark Bulk Data Download

The USPTO provides [bulk trademark data](https://www.uspto.gov/trademarks/apply/check-status-view-documents/trademark-bulk-data) as downloadable XML files. You could build a local search index for offline trademark screening -- this is the most comprehensive approach but requires significant setup.

### Recommended for a Skill

Use **Marker API** (free tier, 1K searches/month) for preliminary screening. Output a direct link to [tmsearch.uspto.gov](https://tmsearch.uspto.gov/) for users to do the official check. Trademark search should be flagged as **preliminary only** -- always recommend professional trademark counsel before final selection.

---

## 4. Brand Name Generators & AI Naming Tools

### Landscape Overview

| Tool | Approach | Key Feature | Pricing |
|---|---|---|---|
| [Namelix](https://namelix.com/) | GPT-based generation | Generates short brandable names, checks .com availability, learns from user preferences | Free to generate; monetizes via Brandmark.io logos ([AIxploria](https://www.aixploria.com/en/namelix/)) |
| [Squadhelp/Atom](https://www.squadhelp.com/) | AI + human crowdsourcing | Contests where naming professionals compete; includes trademark validation | Contests from $199+ |
| [Shopify Name Generator](https://www.shopify.com/tools/business-name-generator) | Keyword combination | Simple word combos + instant domain check | Free |
| [Looka](https://looka.com/) | AI generation + logo | Name generation bundled with AI logo creation | Free to generate |
| [Brandmark.io](https://brandmark.io/) | AI generation + branding | Name + logo + brand identity generation | From $25 for a package |
| [NameRobot](https://www.namerobot.com/) | Modular toolbox approach | Separate tools for merging, checking, spinning words | Free tools + premium |
| [Panabee](https://www.panabee.com/) | Keyword-based + phonetic variations | Shows domain + social + app store availability | Free |

### How They Work

**Namelix's approach** ([Namelix](https://namelix.com/)):
1. User enters keywords describing the business
2. Selects name style (short brandable, two-word combo, rhyming, etc.) and name length
3. AI generates candidates using language models
4. Real-time domain availability checking across TLDs (.com, .io, .ai, .app)
5. User saves favorites; the algorithm learns preferences and improves suggestions
6. Does not just combine dictionary words -- actually invents new words focused on being short and brandable

**Squadhelp's approach** ([Squadhelp](https://www.squadhelp.com/)):
1. Client writes a brief describing the company, values, target audience
2. Creative professionals from around the world submit name ideas (contest model)
3. AI-powered validation checks trademark availability
4. Curated marketplace of pre-vetted premium domain names also available
5. Hybrid model: AI generation for speed + human creativity for quality

**NameRobot's Merger tool** ([NameRobot](https://www.namerobot.com/)):
- Takes two input words and systematically finds overlap points to create portmanteaus
- Example: "flow" + "power" finds the shared "ow" and produces "Flower," "Flowpower," etc.
- Pure algorithmic approach, no AI

### What's Missing from All of Them

None of these tools incorporate:
- Sound symbolism research (which phonemes convey which brand perceptions)
- Professional naming agency methodology (multi-team generation, competitive taxonomy mapping)
- Morpheme-level construction (NameLab's approach)
- Strategic evaluation frameworks (Igor's 9 criteria, SMILE/SCRATCH)

This is the gap a naming skill should fill.

---

## 5. Professional Naming Agency Generative Processes

This section focuses on **how names are actually created** -- the generative techniques, not just evaluation.

### Lexicon Branding's Process (David Placek)

Lexicon created Pentium, BlackBerry, Swiffer, Dasani, Sonos, Vercel, Azure, Windsurf, and Impossible Foods. Their process takes 8-10 weeks and costs six figures ([Lexicon](https://www.lexiconbranding.com/brand-naming-process/), [Lenny's Newsletter](https://www.lennysnewsletter.com/p/naming-expert-david-placek)).

**Step 1: The Diamond Framework**

Before generating any names, define the strategic space. Draw a diamond with four points:
- **Top: "Win"** -- What does winning look like?
- **Right: "What we have to win"** -- Current assets, capabilities
- **Bottom: "What we need to win"** -- What's missing?
- **Left: "What we need to say"** -- The core message the name must communicate

This shifts the team from "finding words" to "defining behavior and experience."

**Step 2: Multi-Team Divergent Generation**

Lexicon's signature technique. Three separate small teams work simultaneously:
- **Team A:** Knows the real brief (e.g., "name a code editor")
- **Team B:** Thinks they're naming a competitor (e.g., "name an alternative to VS Code")
- **Team C:** Works on an unrelated category entirely (e.g., "name a new bicycle brand")

Why this works: Team C, unconstrained by category conventions, produces the most original names. Windsurf (the IDE) came from a team listing "flow" concepts without knowing they were naming a code editor. The deliberate misdirection prevents category-conventional thinking.

**Critical rule: Ban evaluation during generation.** No judging, filtering, or critiquing during the creative phase. Lexicon strictly separates creation from judgment to protect originality.

**Step 3: Volume-Based Filtering**

Quantitative targets from Lexicon:
- Start with **2,000-3,000 raw ideas**
- First pass: reduce to ~250 "diamonds worth polishing"
- Legal clearance + linguistic filters eliminate ~90% of candidates
- Final shortlist: 5-10 names for client presentation

**Step 4: Sound Engineering**

Apply Lexicon's proprietary phonetic symbolism research to evaluate and refine candidates:
- **"V"** is the most alive/vibrant sound (Corvette, Viagra, Vercel)
- **"B"** is the most reliable sound (BlackBerry)
- **"Z"** draws attention (Azure)
- **"X"** signals innovation
- Test whether the phonetic profile matches the desired brand personality

**Step 5: Global Linguistic Screening**

Run candidates through a worldwide network of linguists to check for:
- Negative connotations in major languages
- Pronunciation difficulties across cultures
- Unintended meanings or associations

### Igor Naming Agency's Process

Igor created names for Aria, Gogo, TruTV, and many others. Their approach is more strategy-first than Lexicon's ([Igor International](https://www.igorinternational.com/), [Igor Naming Guide](https://burnsclay.pbworks.com/f/Igor+Naming+Guide.pdf)).

**Step 1: Competitive Taxonomy Mapping**

Before generating anything, Igor maps every competitor's name on a two-axis taxonomy chart:
- **Y-axis:** Functional to Invented (how the name is constructed)
- **X-axis:** Experiential to Evocative (what the name communicates)

This reveals where the category's naming conventions cluster and where white space exists. The goal is to find the quadrant **nobody occupies** and deliberately go there.

**Igor's Four Name Types:**
1. **Functional names:** Directly describe what you do (General Electric, PayPal)
2. **Experiential names:** Connect to something real in human experience, presented imaginatively (Netscape, Palm Pilot)
3. **Evocative names:** Evoke positioning through metaphor, not literal experience (Virgin, Apple, Cracker Jack)
4. **Invented names:** Pure fabrications with no prior meaning (Kodak, Xerox)

**Step 2: Deliberate Category Violation**

Igor's core philosophy: the best names deliberately violate naming conventions. Apple succeeded because every computer company was named with acronyms and technical jargon. Apple was the most "wrong" name for a computer company, which made it the most memorable.

**Step 3: Generation Using Evocative Exploration**

Igor favors real, natural-sounding words over constructed/invented names. Their generation process:
1. Brainstorm word families around the brand's core metaphor
2. Explore words from unexpected domains (if naming a tech company, look at nature, food, textiles, architecture)
3. Test each candidate against the taxonomy map -- does it land in white space?

### NameLab's Constructional Linguistics Approach

NameLab uses a morpheme-based approach that is more systematic and "engineering-like" than other agencies ([NameLab](https://www.namelab.com/approach)).

**The Process:**

1. **Morpheme selection:** American English has 8,000+ morphemes (the smallest units of language carrying semantic meaning). NameLab identifies morphemes that express the desired brand messaging.
   - Example: the morpheme "van" means "top of" or "in front of" (appears in "vanguard," "advantage")
   - Example: "compaq" = "comp" (computer/companion) + "paq" (suggesting compact/packed)

2. **Systematic combination:** Morphemes are combined to construct **neologisms** (new words) rather than using existing vocabulary. This is different from portmanteau (blending two full words) -- it's combining meaning-units.

3. **Refinement filters:**
   - **Speechstream visibility:** How recognizable the name is when spoken in flowing conversation
   - **Phonetic transparency:** Does the name sound as it's spelled?
   - **Notational visibility:** How distinctly the name appears in writing. NameLab changed "Compak" to "Compaq" specifically because the "Q" is more visually distinctive

### The Combined Generative Technique Set

Synthesizing all agency approaches, here are the distinct generative techniques:

| Technique | Description | Example |
|---|---|---|
| **Metaphor transfer** | Take a real word from one domain and apply to another | Apple (fruit to tech), Slack (adjective to chat) |
| **Morpheme construction** | Combine meaning-carrying word parts to build new words | Compaq (comp + paq), Acura (acu = precision) |
| **Portmanteau** | Blend two recognizable words at an overlap point | Pinterest (pin + interest), Instagram (instant + telegram) |
| **Phonetic sculpting** | Design a word sound-first based on desired phonetic profile | Dasani (CVCVCV pattern, "san" = health), Swiffer (sw- = sweep, -ffer = light/playful) |
| **Category violation** | Name using the conventions of a completely unrelated category | Apple in tech, Amazon in e-commerce |
| **Domain-first** | Search available .com domains, then pick the best-sounding option | Stripe (the Collisons searched available .coms) |
| **Truncation/clipping** | Shorten a real word or phrase | Cisco (San Francisco), FedEx (Federal Express) |
| **Respelling** | Take a real word and alter spelling for distinctiveness | Lyft, Fiverr, Tumblr |
| **Foreign loan** | Borrow a word from another language | Volvo (Latin: "I roll"), Audi (Latin: "hear") |
| **Competitive white space** | Map competitor names on taxonomy, go where nobody is | Igor's approach: find the empty quadrant |

---

## 6. Phonetic Symbolism: Complete Sound-Meaning Map

### Vowel Effects (Extensively Replicated)

The "mil/mal" effect, first demonstrated by Edward Sapir in 1929, has been replicated across 80%+ of languages studied ([Wikipedia - Sound Symbolism](https://en.wikipedia.org/wiki/Sound_symbolism)).

| Vowel Class | Specific Sounds | Perceived As | Brand Examples |
|---|---|---|---|
| **High front** | /i/ (as in "see"), /ɪ/ (as in "sit") | Small, light, fast, thin, sharp, cold, feminine | Nike, Visa, Wii, Kindle, Pixar |
| **Low front** | /e/ (as in "set"), /ae/ (as in "cat") | Medium size, energetic, open | Etsy, Gap, Zara |
| **High back** | /u/ (as in "moon"), /ʊ/ (as in "put") | Large, heavy, dark, round, powerful | Google, Roku, Lululemon |
| **Low back** | /ɑ/ (as in "father"), /ɔ/ (as in "law") | Large, warm, expansive, stable | Sonos, Volvo, Amazon |
| **Central** | /ʌ/ (as in "cup"), /ə/ (as in "about") | Neutral, unobtrusive | Uber |

**Quantitative finding:** In Sapir's experiment, over 80% of participants assigned "mal" (back vowel) to a larger table and "mil" (front vowel) to a smaller table. This effect replicates across diverse languages and cultures ([JSTOR Daily](https://daily.jstor.org/whats-brand-name-sounds-persuasion/)).

**Product-specific finding:** Ice cream branded "Frosh" (back vowel) was perceived as smoother, richer, and creamier than "Frish" (front vowel) and was evaluated more favorably ([ResearchGate - Phonetic Symbolism and Brand Name Preference](https://www.researchgate.net/publication/23547390_Phonetic_Symbolism_and_Brand_Name_Preference)).

### Consonant Effects

| Consonant Class | Specific Sounds | Perceived As | Source |
|---|---|---|---|
| **Voiceless plosives** | /p/, /t/, /k/ | Hard, sharp, crisp, efficient, decisive; **highest brand recall** | [JSTOR Daily](https://daily.jstor.org/whats-brand-name-sounds-persuasion/) |
| **Voiced plosives** | /b/, /d/, /g/ | Softer than voiceless but still bold; suggest power with warmth | [OYZTA](https://www.oyzta.com/blog/how-sound-shapes-brand-names-the-science-of-phonetic-symbolism/) |
| **Voiceless fricatives** | /f/, /s/, /ʃ/ (sh), /θ/ (th) | Smooth, fast, light, elegant, smaller | [The Identity Bureau](https://www.theidbureau.com/blog/using-sound-symbolism) |
| **Voiced fricatives** | /v/, /z/, /ʒ/ (zh) | Vibrant, alive, attention-grabbing | Lexicon research via [Lenny's Newsletter](https://www.lennysnewsletter.com/p/naming-expert-david-placek) |
| **Nasals** | /m/, /n/, /ŋ/ (ng) | Warm, soft, comforting, nurturing | [OYZTA](https://www.oyzta.com/blog/how-sound-shapes-brand-names-the-science-of-phonetic-symbolism/) |
| **Liquids** | /l/, /r/ | Flowing, liquid, smooth | [OYZTA](https://www.oyzta.com/blog/how-sound-shapes-brand-names-the-science-of-phonetic-symbolism/) |
| **Affricates** | /tʃ/ (ch), /dʒ/ (j) | Distinctive, unconventional; associated with luxury | NTU Singapore research |

### Lexicon's Proprietary Consonant Findings

From David Placek's research at Lexicon Branding ([Lenny's Newsletter](https://www.lennysnewsletter.com/p/naming-expert-david-placek)):

| Sound | Primary Association | Example Brands |
|---|---|---|
| **V** | Most alive, most vibrant of all consonants | Corvette, Viagra, Vercel, Visa |
| **B** | Most reliable | BlackBerry, BMW, Boeing |
| **Z** | Draws attention, demands notice | Azure, Zoom, Zappos |
| **X** | Signals innovation, the unknown | SpaceX, Xerox, Xbox |

### Consonant Cluster Effects

| Cluster | Perception | Examples |
|---|---|---|
| str- | Strength, structure, precision | Stripe, Stream, Strata |
| sl- | **Negative connotations** (slime, sloppy, slug) -- avoid | - |
| sn- | Sharp, distinctive, sometimes playful | Snapchat, Snowflake |
| sw- | Sweeping motion, swiftness | Swiffer, Swift |
| fl- | Flowing, light, airborne | Flicker, Flow, Flutter |
| pl- | Pleasant, pleasing, plentiful | Plaid, Play, Plenty |
| -ump | Heavy, clumsy -- avoid | - |

### Frequency-Based Model

From the Oxford University framework ([Oxford Research Archive](https://ora.ox.ac.uk/objects/uuid:39ccf1b1-1b79-497f-944c-a7e3f815ecbc/files/rpn89d721s)):

**Higher-frequency sounds** (front vowels + fricatives + voiceless consonants):
- Associated with higher evaluation (liked more)
- Associated with lower potency (perceived as less powerful)
- Best for: elegance, speed, precision, lightness

**Lower-frequency sounds** (back vowels + stops + voiced consonants):
- Associated with lower evaluation (liked less on their own)
- Associated with higher potency (perceived as more powerful)
- Best for: strength, reliability, substance, authority

### The "K" Effect in Branding

Names starting with "K" occur more frequently in brand naming than in general English usage. Research shows K-initial names are **more memorable and more effective in brand recognition**. This helps explain: Kodak, Kraft, Kayak, Kindle, Keurig, Kleenex ([JSTOR Daily](https://daily.jstor.org/whats-brand-name-sounds-persuasion/)).

### Sound-Brand Attribute Prescription Table

For practical use in a naming skill, here is the synthesized prescription:

| Desired Brand Attribute | Recommended Sounds | Avoid |
|---|---|---|
| **Speed/precision** | Front vowels (i, e), voiceless fricatives (s, f), crisp plosives (t, k) | Back vowels, nasals |
| **Power/authority** | Voiced plosives (b, d, g), back vowels (o, u), hard endings | Fricatives, high front vowels |
| **Innovation/tech** | X, Z, front vowels, consonant clusters (str-, pl-) | Warm nasals (m, n) |
| **Warmth/comfort** | Nasals (m, n), liquids (l, r), back vowels | Sharp plosives, fricatives |
| **Luxury/premium** | Late-acquired phonemes (sh, ch, zh, th), affricates, open vowels, 2-3 syllables | Early-acquired phonemes (m, b, p), monosyllabic |
| **Reliability/trust** | B, voiced stops, balanced vowels | Z, X, unusual clusters |
| **Energy/vitality** | V, plosives, front vowels | Slow nasals, back vowels |
| **Smoothness/flow** | Fricatives (f, v, s), liquids (l, r), back vowels | Hard plosives, consonant clusters |

---

## 7. Architecture for a Name Generation & Evaluation Skill

Based on the research, a name generation and evaluation skill should implement:

### Generation Pipeline

```
Input: Industry, brand attributes, target audience, competitors
                    |
                    v
    +---------------------------------+
    | 1. STRATEGIC FRAMING            |
    |    - Diamond framework           |
    |    - Competitive taxonomy map    |
    |    - Identify white space        |
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 2. MULTI-TECHNIQUE GENERATION   |
    |    Run all techniques in parallel:|
    |    - Metaphor transfer            |
    |    - Morpheme construction        |
    |    - Portmanteau generation       |
    |    - Phonetic sculpting           |
    |    - Category violation           |
    |    - Foreign loan words           |
    |    - Respelling of real words     |
    |    Target: 200+ raw candidates   |
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 3. PHONETIC SCORING             |
    |    For each candidate:           |
    |    - Map vowels/consonants       |
    |    - Score alignment with        |
    |      desired brand attributes    |
    |    - Flag negative clusters (sl-)|
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 4. STRUCTURAL SCORING           |
    |    - Character count (4-8 ideal) |
    |    - Syllable count (1-2 ideal)  |
    |    - CV pattern analysis         |
    |    - Spelling transparency       |
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 5. EVALUATION FRAMEWORK         |
    |    Score 0-10 on each:           |
    |    - Distinctiveness             |
    |    - Memorability                |
    |    - Sound quality               |
    |    - Depth/layers of meaning     |
    |    - Energy/"33" factor          |
    |    - Strategic fit               |
    |    - Phonetic profile match      |
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 6. AVAILABILITY SCREENING       |
    |    For top ~30 candidates:       |
    |    - .com domain (RDAP/whois)    |
    |    - Trademark (Marker API)      |
    |    - Output Namechk link         |
    +---------------------------------+
                    |
                    v
    +---------------------------------+
    | 7. FINAL SHORTLIST              |
    |    Present top 10 with:          |
    |    - Score breakdown             |
    |    - Phonetic analysis           |
    |    - Domain availability status  |
    |    - Trademark preliminary check |
    |    - Metaphor/meaning narrative  |
    +---------------------------------+
```

### Key Implementation Details

**Domain checking (automated):**
```bash
# RDAP check - returns 200 (taken) or 404 (available)
curl -sL -o /dev/null -w "%{http_code}" "https://rdap.org/domain/${name}.com"
```

**Trademark preliminary check (via Marker API, free tier):**
```bash
curl "https://markerapi.com/api/v2/trademarks/mark/${name}/status/all/username/USER/password/PASS"
```

**Social media link (manual follow-up):**
```
https://namechk.com/?q=${name}
```

**Phonetic analysis (programmatic):**
Use Python's `eng_to_ipa` library to convert candidate names to IPA, then classify each phoneme against the sound-attribute map.

### What This Skill Would Do That No Existing Tool Does

1. **Generate using multiple professional techniques** (not just keyword combination)
2. **Score phonetic alignment** against desired brand attributes using research-backed sound symbolism data
3. **Map competitive white space** using Igor's taxonomy approach
4. **Automate domain + trademark screening** in the pipeline
5. **Evaluate using professional frameworks** (Igor 9-criteria, SMILE/SCRATCH)
6. **Explain the "why"** -- provide narrative for why each name works (metaphor layers, sound profile, strategic positioning)
