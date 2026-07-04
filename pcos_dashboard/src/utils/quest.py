import random

# =============================================================================
# PCOS 28-Day Evidence-Based Quest System
# =============================================================================
# Each day of the week has its own large pool (~10 major, 6 minor) drawn
# directly from peer-reviewed PCOS lifestyle literature (2020–2026).
#
# Because random.sample picks a different subset each week, across 4 weeks
# (28 days) you experience 28 meaningfully different quest combinations —
# even though the day-of-week trigger stays identical to the original system.
#
# After Day 28 the randomisation naturally reshuffles a new varied plan.
# The function signature and return format are unchanged from the original
# quest.py, so 12_user_daily_quest.py requires zero modifications.
#
# Key sources (full citations in PCOS_Filtered_Papers_2020plus.xlsx):
#   Che et al. (2021)          – Dietary Interventions
#   Líška & Záhumensky (2021)  – Importance of Nutrition
#   Pirotta et al. (2021)      – Barriers & Facilitators to Lifestyle Guidelines
#   Pietrasińska et al. (2022) – Vegetarian vs Non-Vegetarian Eating Habits
#   Scannell et al. (2022)     – Mediterranean Diet Protocol
#   Mei et al. (2022)          – Mediterranean + Low-Carb Diet
#   Han et al. (2023)          – High-Fat Diet & Lifestyle Intervention
#   Das & Fatima (2023)        – Importance of Lifestyle Modifications
#   Cowan et al. (2023)        – Lifestyle Beyond Diet & Physical Activity
#   Dutkiewicz et al. (2023)   – Eating Patterns & Emotional Distress
#   Colombo et al. (2023)      – Diet & Exercise, Person-Centred Care
#   Sabag et al. (2024)        – Exercise Position Statement (ESSA)
#   Zhang et al. (2024)        – Dietary Patterns & Reproductive Endocrinology
#   Delavar et al. (2024)      – Lifestyle Policy Brief
#   Ghafari et al. (2025)      – PCOS Diagnosis & Novel Treatment Update
#   Scannell et al. (2025)     – Mediterranean Diet Review
#   Wang et al. (2025)         – Lifestyle Intervention Progress
#   Rao et al. (2025)          – Traditional Indian Medicine & Dietary Management
#   Gautam et al. (2025)       – Lifestyle Interventions Systematic Review
#   Capozzi et al. (2025)      – Lifestyle and Diet in PCOS
#   Sengupta & Dutta (2026)    – Phenotype-Guided Interventions
# =============================================================================


def get_todays_quests(day_name, user_rank):
    """
    Returns (selected_major, selected_minor, daily_theme) for today.

    Parameters
    ----------
    day_name  : str  – Full weekday name, e.g. "Monday" (from datetime.strftime("%A"))
    user_rank : str  – Must contain "Seedling", "Sprout", or neither (Warrior)

    Returns
    -------
    selected_major : list[dict]  – Major quests with keys: name, desc, points
    selected_minor : list[dict]  – Minor quests with keys: name, desc, points
    daily_theme    : str         – Emoji + theme label for the UI header
    """

    # =========================================================================
    # MONDAY — 🥗 Nourish & Balance
    # Focus: whole-food dietary habits, blood sugar regulation, macronutrient balance
    # Pool size: 11 major, 6 minor
    # =========================================================================
    if day_name == "Monday":
        daily_theme = "🥗 Nourish & Balance"

        day_major = [
            {
                "name": "Low-GI Breakfast",
                "desc": "Start with oats, eggs, or avocado on whole-grain toast. "
                        "A low-glycaemic first meal keeps blood glucose stable for hours. "
                        "(Zhang et al., 2024)"
            },
            {
                "name": "Eat 30g Protein per Meal",
                "desc": "Fill your plate with lean poultry, fish, legumes, or Greek yoghurt. "
                        "Adequate protein reduces androgen-driven hunger and cravings. "
                        "(Che et al., 2021)"
            },
            {
                "name": "2 Cups of Leafy Greens",
                "desc": "Spinach, kale, rocket, or bok choy — the fibre actively helps flush "
                        "excess oestrogen and lowers chronic inflammation. "
                        "(Scannell et al., 2025)"
            },
            {
                "name": "Choose Whole Grains Today",
                "desc": "Swap white rice or pasta for brown rice, quinoa, or whole-grain bread. "
                        "Lowers the glycaemic load of every meal you eat. "
                        "(Mei et al., 2022)"
            },
            {
                "name": "Cook Dinner at Home",
                "desc": "Full control over ingredients, oils, and portions. Home cooking "
                        "eliminates hidden sugars and inflammatory seed oils. "
                        "(Colombo et al., 2023)"
            },
            {
                "name": "Include Legumes in a Meal",
                "desc": "Chickpeas, lentils, black beans, or edamame — high fibre, low GI, "
                        "and a key pillar of the Mediterranean dietary pattern for PCOS. "
                        "(Líška & Záhumensky, 2021)"
            },
            {
                "name": "Eat 5 Portions of Fruit & Veg",
                "desc": "Variety across colours throughout the day — each pigment delivers "
                        "different antioxidants that combat PCOS-related oxidative stress. "
                        "(Pietrasińska et al., 2022)"
            },
            {
                "name": "Anti-Inflammatory Meal",
                "desc": "Include turmeric, ginger, or an omega-3-rich ingredient (salmon, "
                        "walnuts, flaxseed) in at least one meal today. "
                        "(Scannell et al., 2025)"
            },
            {
                "name": "No Refined Sugar Today",
                "desc": "Avoid sweets, pastries, sugary drinks, and white bread. Even small "
                        "daily reductions in refined sugar meaningfully improve insulin "
                        "resistance over weeks. (Han et al., 2023)"
            },
            {
                "name": "High-Protein Savoury Breakfast",
                "desc": "Eggs, smoked salmon, or cottage cheese instead of sugary cereal. "
                        "A protein-led morning stabilises cortisol and prevents mid-morning "
                        "energy crashes. (Das & Fatima, 2023)"
            },
            {
                "name": "Add Flax or Chia Seeds to a Meal",
                "desc": "Two tablespoons in porridge, a smoothie, or a salad. Lignans in "
                        "flaxseed support oestrogen metabolism and phytoestrogens aid hormone "
                        "balance. (Rao et al., 2025)"
            },
        ]

        day_minor = [
            {
                "name": "Swap Sugary Drink for Herbal Tea",
                "desc": "Eliminate liquid sugar — one of the fastest wins for insulin "
                        "sensitivity, with zero sacrifice in flavour. (Han et al., 2023)"
            },
            {
                "name": "Use Olive Oil as Your Primary Fat",
                "desc": "Drizzle on salads or use for light cooking. MUFAs and polyphenols "
                        "in extra-virgin olive oil actively reduce inflammation. "
                        "(Scannell et al., 2025)"
            },
            {
                "name": "Eat Slowly & Without Screens",
                "desc": "Chew each bite 15–20 times. Mindful pacing improves digestion, "
                        "reduces overeating, and reconnects hunger signals disrupted by PCOS. "
                        "(Dutkiewicz et al., 2023)"
            },
            {
                "name": "Protein-Rich Snack",
                "desc": "Nuts, Greek yoghurt, boiled eggs, or hummus with veggies. "
                        "Avoid carb-only snacks to prevent blood sugar dips between meals. "
                        "(Che et al., 2021)"
            },
            {
                "name": "Read Food Labels Before Buying",
                "desc": "Check for hidden sugars, inflammatory seed oils, and additives. "
                        "Label awareness is the first step toward dietary empowerment. "
                        "(Colombo et al., 2023)"
            },
            {
                "name": "Drink 8 Glasses of Water",
                "desc": "Proper hydration supports metabolic function and reduces false hunger "
                        "signals that can mimic PCOS cravings. (Das & Fatima, 2023)"
            },
        ]

    # =========================================================================
    # TUESDAY — 🏃 Move & Strengthen
    # Focus: aerobic exercise, resistance training, reducing sedentary behaviour
    # Pool size: 10 major, 6 minor
    # =========================================================================
    elif day_name == "Tuesday":
        daily_theme = "🏃 Move & Strengthen"

        day_major = [
            {
                "name": "30 Min Moderate Aerobic Exercise",
                "desc": "Brisk walking, cycling, swimming, or dancing. Improves insulin "
                        "resistance independently of weight loss — the mechanism matters more "
                        "than the scale. (Sabag et al., 2024)"
            },
            {
                "name": "Strength Training Session",
                "desc": "Squats, lunges, push-ups, rows, or any resistance work targeting "
                        "major muscle groups. Building muscle tissue is one of the most "
                        "effective long-term insulin-resistance strategies. "
                        "(Sabag et al., 2024)"
            },
            {
                "name": "Reach 10,000 Steps Today",
                "desc": "Track with your phone or watch. Consistent daily movement — not just "
                        "one gym session — is a core PCOS lifestyle pillar. "
                        "(Sabag et al., 2024)"
            },
            {
                "name": "Post-Meal Walk (10 Min × 3)",
                "desc": "A short walk after breakfast, lunch, and dinner. Muscles soak up "
                        "circulating glucose and blunt post-meal insulin spikes. "
                        "(Sabag et al., 2024)"
            },
            {
                "name": "HIIT Session (20 Min)",
                "desc": "Alternate 40 seconds of effort with 20 seconds of rest for 20 rounds. "
                        "Time-efficient and clinically effective for improving PCOS hormonal "
                        "profiles. (Sabag et al., 2024)"
            },
            {
                "name": "Yoga or Pilates Session (30 Min)",
                "desc": "Low-cortisol movement that improves core strength, flexibility, and "
                        "nervous system regulation — all disrupted in PCOS. "
                        "(Cowan et al., 2023)"
            },
            {
                "name": "Bodyweight Home Circuit (15 Min)",
                "desc": "Squats, lunges, push-ups, and planks. No equipment, no excuses. "
                        "Consistency over intensity is what drives hormonal improvement. "
                        "(Colombo et al., 2023)"
            },
            {
                "name": "45 Min Outdoor Walk",
                "desc": "Combines cardiovascular benefit, nature exposure, and Vitamin D "
                        "synthesis — three independent PCOS management tools in one activity. "
                        "(Das & Fatima, 2023)"
            },
            {
                "name": "Active Break Every 30 Min",
                "desc": "Set a timer. Stand, stretch, or walk for 2 minutes every 30 minutes "
                        "of sitting. Prolonged sitting independently worsens insulin resistance "
                        "even in active people. (Sabag et al., 2024)"
            },
            {
                "name": "Fun Movement for 20 Min",
                "desc": "Dance, hula hoop, a sport you love — anything joyful counts. Exercise "
                        "adherence is highest when the activity feels like a reward, not a "
                        "punishment. (Pirotta et al., 2021)"
            },
        ]

        day_minor = [
            {
                "name": "Take the Stairs All Day",
                "desc": "Every flight is a micro-workout. Small, consistent elevation choices "
                        "add up to meaningful daily NEAT. (Sabag et al., 2024)"
            },
            {
                "name": "5 Min Morning Stretch",
                "desc": "Full-body gentle stretching upon waking. Lowers morning cortisol and "
                        "activates the nervous system without spiking it. "
                        "(Colombo et al., 2023)"
            },
            {
                "name": "Stand During Phone Calls",
                "desc": "An effortless way to reduce total sitting time by 30–60 minutes a day "
                        "without changing anything else. (Sabag et al., 2024)"
            },
            {
                "name": "10 Squats Every Hour",
                "desc": "Micro-bursts of muscle activation throughout the day improve glucose "
                        "uptake and reduce insulin resistance cumulatively. "
                        "(Sabag et al., 2024)"
            },
            {
                "name": "Foam Roll or Stretch Before Bed",
                "desc": "5–10 minutes of gentle floor stretching signals the body to wind "
                        "down for sleep — combining recovery with sleep preparation. "
                        "(Colombo et al., 2023)"
            },
            {
                "name": "Park Further Away & Walk",
                "desc": "Deliberate extra steps — every bit of non-exercise activity "
                        "thermogenesis (NEAT) contributes to the 10,000-step target. "
                        "(Sabag et al., 2024)"
            },
        ]

    # =========================================================================
    # WEDNESDAY — 🌿 Anti-Inflammation
    # Focus: anti-inflammatory foods, omega-3, polyphenols, gut health
    # Pool size: 10 major, 6 minor
    # =========================================================================
    elif day_name == "Wednesday":
        daily_theme = "🌿 Anti-Inflammation"

        day_major = [
            {
                "name": "Eat Fatty Fish or Take Omega-3",
                "desc": "Salmon, sardines, or mackerel — or 1–2g EPA/DHA supplement with a "
                        "meal. Omega-3 directly reduces systemic inflammation central to "
                        "PCOS pathophysiology. (Scannell et al., 2025)"
            },
            {
                "name": "Build a Rainbow Plate",
                "desc": "5 different coloured vegetables on your dinner plate. Each colour "
                        "delivers unique anti-inflammatory phytonutrients that operate via "
                        "distinct pathways. (Scannell et al., 2025)"
            },
            {
                "name": "Cook with Turmeric Today",
                "desc": "Golden milk, scrambled eggs, curry, or soup — curcumin is one of the "
                        "most studied anti-inflammatory compounds for metabolic conditions. "
                        "(Rao et al., 2025)"
            },
            {
                "name": "Drink 2 Cups Spearmint Tea",
                "desc": "Morning and afternoon. Clinically shown to lower free testosterone "
                        "within 30 days of consistent daily use. "
                        "(Rao et al., 2025)"
            },
            {
                "name": "Eat a Handful of Walnuts or Almonds",
                "desc": "Omega-3, magnesium, and Vitamin E in one snack. Walnuts in particular "
                        "reduce oxidative stress markers in metabolic syndrome. "
                        "(Scannell et al., 2025)"
            },
            {
                "name": "Eat Berries as a Snack",
                "desc": "Blueberries, strawberries, or raspberries — highest antioxidant "
                        "density of any fruit. Anthocyanins specifically reduce inflammatory "
                        "cytokines elevated in PCOS. (Han et al., 2023)"
            },
            {
                "name": "Use Only Olive Oil for Cooking",
                "desc": "Replace all other fats today. Polyphenols and MUFAs in extra-virgin "
                        "olive oil actively suppress NF-κB inflammatory signalling pathways. "
                        "(Scannell et al., 2025)"
            },
            {
                "name": "Avoid All Ultra-Processed Food",
                "desc": "No chips, fast food, packaged sweets, or processed meats. "
                        "Ultra-processed foods are independently associated with worsened PCOS "
                        "inflammation and insulin resistance. (Han et al., 2023)"
            },
            {
                "name": "Cook with Fresh Ginger",
                "desc": "Grate into tea, a stir-fry, or soup. Gingerols are potent inhibitors "
                        "of prostaglandin synthesis — the same pathway targeted by NSAID "
                        "pain relief. (Rao et al., 2025)"
            },
            {
                "name": "Eat Cruciferous Vegetables Today",
                "desc": "Broccoli, cauliflower, cabbage, or Brussels sprouts. Indole-3-carbinol "
                        "supports liver oestrogen clearance, directly addressing oestrogen "
                        "dominance in PCOS. (Scannell et al., 2025)"
            },
        ]

        day_minor = [
            {
                "name": "Take Your Omega-3 Supplement",
                "desc": "1–2g EPA/DHA with a meal. Consistent daily use over 8–12 weeks "
                        "produces measurable reductions in PCOS inflammation markers. "
                        "(Ghafari et al., 2025)"
            },
            {
                "name": "Add Cinnamon to Breakfast",
                "desc": "Sprinkle on porridge, coffee, or yoghurt. Ceylon cinnamon improves "
                        "insulin receptor sensitivity with consistent daily use. "
                        "(Rao et al., 2025)"
            },
            {
                "name": "Have a Probiotic Today",
                "desc": "Plain yoghurt, kefir, kimchi, or a probiotic capsule. Gut microbiome "
                        "diversity is directly linked to PCOS hormonal and metabolic profile. "
                        "(Ghafari et al., 2025)"
            },
            {
                "name": "Swap Processed Snack for Fruit & Nuts",
                "desc": "Whole-food snacks prevent the blood sugar spikes that drive "
                        "inflammatory cytokine release between meals. (Han et al., 2023)"
            },
            {
                "name": "Add Ground Flaxseeds to Breakfast",
                "desc": "1 tablespoon in porridge or smoothie. Lignans support oestrogen "
                        "metabolism and the omega-3 ALA reduces systemic inflammation. "
                        "(Rao et al., 2025)"
            },
            {
                "name": "Drink 2 Cups of Green Tea",
                "desc": "EGCG improves insulin sensitivity and has been shown to reduce "
                        "androgen levels in women with PCOS with consistent use. "
                        "(Rao et al., 2025)"
            },
        ]

    # =========================================================================
    # THURSDAY — 🧘 Rest & Restore
    # Focus: sleep quality, stress reduction, cortisol management, mental health
    # Pool size: 10 major, 6 minor
    # =========================================================================
    elif day_name == "Thursday":
        daily_theme = "🧘 Rest & Restore"

        day_major = [
            {
                "name": "Consistent Sleep & Wake Time",
                "desc": "Same bedtime and wake time as yesterday — even by 15 minutes. "
                        "Circadian disruption independently worsens insulin resistance and "
                        "androgen production in PCOS. (Cowan et al., 2023)"
            },
            {
                "name": "10 Min Guided Meditation",
                "desc": "Use an app (Headspace, Calm, Insight Timer) or a YouTube session. "
                        "MBSR practice measurably lowers HPA-axis activity and cortisol "
                        "output. (Cowan et al., 2023)"
            },
            {
                "name": "Digital Sunset (1 Hour Before Bed)",
                "desc": "No phones, tablets, or TV from one hour before sleep. Blue-light "
                        "suppresses melatonin, delays sleep onset, and compounds hormonal "
                        "disruption in PCOS. (Cowan et al., 2023)"
            },
            {
                "name": "15 Min Deep Breathing Practice",
                "desc": "Try box breathing (4-4-4-4) or 4-7-8 breathing for 15 minutes. "
                        "Directly activates the parasympathetic nervous system and lowers "
                        "cortisol within a single session. (Das & Fatima, 2023)"
            },
            {
                "name": "Gentle Restorative Yoga (20 Min)",
                "desc": "Yin or restorative yoga, held poses for 3–5 minutes each. "
                        "Reduces stress-induced hyperandrogenism and signals full systemic "
                        "recovery. (Das & Fatima, 2023)"
            },
            {
                "name": "Gratitude Journal — 3 Entries",
                "desc": "Write 3 specific things you are grateful for today. This simple "
                        "practice measurably shifts the nervous system from sympathetic "
                        "(stress) to parasympathetic (rest) state. (Cowan et al., 2023)"
            },
            {
                "name": "20 Min in Nature or Sunlight",
                "desc": "A walk in a green space or simply sitting outside. Reduces cortisol, "
                        "boosts Vitamin D synthesis, and increases serotonin — all disrupted "
                        "in PCOS. (Das & Fatima, 2023)"
            },
            {
                "name": "Progressive Muscle Relaxation",
                "desc": "Tense and slowly release each muscle group from toes to head, "
                        "10 seconds per group. Proven to reduce anxiety and improve sleep "
                        "quality in chronic conditions including PCOS. (Cowan et al., 2023)"
            },
            {
                "name": "No Screens After 9 PM",
                "desc": "A stricter cut-off than usual. Consistent screen-free evenings "
                        "meaningfully improve sleep architecture and morning cortisol levels "
                        "within 2 weeks. (Cowan et al., 2023)"
            },
            {
                "name": "Strategic Power Nap (20 Min Max)",
                "desc": "If fatigued, a short nap before 3 PM restores cortisol regulation "
                        "without disrupting night sleep. Sleep debt accumulates and worsens "
                        "insulin sensitivity daily. (Das & Fatima, 2023)"
            },
        ]

        day_minor = [
            {
                "name": "Brew a Calming Herbal Tea",
                "desc": "Chamomile, passionflower, or valerian root 30 minutes before bed. "
                        "A consistent pre-sleep ritual cues the nervous system to wind down. "
                        "(Cowan et al., 2023)"
            },
            {
                "name": "Epsom Salt Bath",
                "desc": "15–20 min soak with 2 cups of Epsom salts. Magnesium absorbed "
                        "transdermally supports muscle relaxation and deeper sleep stages. "
                        "(Cowan et al., 2023)"
            },
            {
                "name": "Phone in Another Room at Bedtime",
                "desc": "Physically removing the device eliminates both temptation and "
                        "blue-light exposure in one move. (Cowan et al., 2023)"
            },
            {
                "name": "5 Min Feelings Journal",
                "desc": "Write freely about your day without editing. Emotional processing "
                        "on paper reduces overnight stress hormone release and rumination. "
                        "(Cowan et al., 2023)"
            },
            {
                "name": "Turn Off Notifications for 2 Hours",
                "desc": "Constant alerts maintain a low-grade cortisol elevation throughout "
                        "the day. A notification-free window allows genuine nervous system "
                        "recovery. (Pirotta et al., 2021)"
            },
            {
                "name": "Listen to Calming Music or Sleep Story",
                "desc": "30 minutes before bed. Shown to lower resting heart rate and "
                        "prepare the body for deep, hormone-restorative sleep. "
                        "(Cowan et al., 2023)"
            },
        ]

    # =========================================================================
    # FRIDAY — 🔬 Hormone Harmony
    # Focus: targeted hormonal balance, supplementation, androgen reduction
    # Pool size: 10 major, 6 minor
    # =========================================================================
    elif day_name == "Friday":
        daily_theme = "🔬 Hormone Harmony"

        day_major = [
            {
                "name": "High-Fibre Breakfast (≥10g Fibre)",
                "desc": "Oats with chia, whole-grain toast with flaxseed, or a vegetable "
                        "omelette. Dietary fibre is the primary driver of healthy oestrogen "
                        "clearance via the gut. (Scannell et al., 2025)"
            },
            {
                "name": "Take Myo-Inositol Supplement",
                "desc": "2g myo-inositol + 50mg D-chiro-inositol (or combined formulation). "
                        "Clinically proven to improve insulin signalling and restore ovulatory "
                        "function in PCOS. (Ghafari et al., 2025)"
            },
            {
                "name": "Drink 2 Cups Spearmint Tea",
                "desc": "One cup morning, one cup afternoon. Two daily cups shown in clinical "
                        "trials to reduce free testosterone levels within 30 days of "
                        "consistent use. (Rao et al., 2025)"
            },
            {
                "name": "Low-Carb High-Protein Lunch",
                "desc": "Grilled fish or chicken with salad dressed in olive oil. Reduces "
                        "LH:FSH ratio and lowers ovarian androgen production — a direct "
                        "hormonal lever. (Mei et al., 2022)"
            },
            {
                "name": "Mediterranean Dinner",
                "desc": "Fish or legumes, a large salad, olive oil, and a small portion of "
                        "whole grain. The Mediterranean pattern is the most studied dietary "
                        "intervention for PCOS hormonal health. (Scannell et al., 2025)"
            },
            {
                "name": "30 Min Exercise for Hormones",
                "desc": "Any moderate-intensity movement. Exercise reduces circulating "
                        "androgens and improves insulin sensitivity independently of "
                        "weight change — the mechanism is the benefit. "
                        "(Sabag et al., 2024)"
            },
            {
                "name": "Alcohol-Free Day",
                "desc": "Alcohol impairs liver oestrogen metabolism and directly worsens "
                        "insulin resistance. Even one drink disrupts hormonal balance — "
                        "take today completely off. (Capozzi et al., 2025)"
            },
            {
                "name": "Include Cruciferous Vegetables",
                "desc": "Broccoli, cauliflower, kale, or Brussels sprouts with dinner. "
                        "DIM (diindolylmethane) produced during digestion actively clears "
                        "excess oestrogen from the body. (Scannell et al., 2025)"
            },
            {
                "name": "Limit Caffeine to 1 Cup Before Noon",
                "desc": "Excess caffeine elevates cortisol, which drives insulin resistance "
                        "and androgen production via the adrenal pathway. One cup, early, "
                        "is the safe zone. (Cowan et al., 2023)"
            },
            {
                "name": "Add Fenugreek to a Meal or Tea",
                "desc": "Fenugreek seeds or powder in curry, yoghurt, or tea. Shown to improve "
                        "insulin sensitivity and support menstrual regularity in women "
                        "with PCOS. (Rao et al., 2025)"
            },
        ]

        day_minor = [
            {
                "name": "Take Your Omega-3 Supplement",
                "desc": "1–2g EPA/DHA with a meal. Reduces inflammatory prostaglandins that "
                        "disrupt follicular development and ovulation. "
                        "(Ghafari et al., 2025)"
            },
            {
                "name": "Take Your Vitamin D Supplement",
                "desc": "Deficiency is found in up to 85% of women with PCOS and is directly "
                        "linked to worsened insulin resistance, mood, and irregular cycles. "
                        "(Ghafari et al., 2025)"
            },
            {
                "name": "Low-GI Snacks Only Today",
                "desc": "Apple with nut butter, a small handful of nuts, or plain Greek "
                        "yoghurt. Keeping insulin flat between meals is the goal. "
                        "(Zhang et al., 2024)"
            },
            {
                "name": "No Refined Sugar Today",
                "desc": "Check every label. Even consistent small reductions in added sugar "
                        "produce measurable improvements in PCOS metabolic markers over "
                        "weeks. (Che et al., 2021)"
            },
            {
                "name": "Add Zinc-Rich Foods",
                "desc": "Pumpkin seeds, cashews, chickpeas, or hemp seeds. Zinc is essential "
                        "for healthy testosterone metabolism and follicular development. "
                        "(Líška & Záhumensky, 2021)"
            },
            {
                "name": "Hit Your 2L Water Target",
                "desc": "Dehydration increases cortisol output, which then drives the adrenal "
                        "androgen production that worsens PCOS. Stay consistent all day. "
                        "(Das & Fatima, 2023)"
            },
        ]

    # =========================================================================
    # SATURDAY — 🧠 Mindful Habits
    # Focus: mindful eating, behaviour change, planning, emotional wellbeing
    # Pool size: 9 major, 6 minor
    # =========================================================================
    elif day_name == "Saturday":
        daily_theme = "🧠 Mindful Habits"

        day_major = [
            {
                "name": "Mindful Eating at Every Meal",
                "desc": "Sit down, put away screens, and eat slowly at all three meals. "
                        "Mindful eating reduces emotional overeating and improves hormonal "
                        "satisfaction signals disrupted by PCOS. (Dutkiewicz et al., 2023)"
            },
            {
                "name": "Hunger & Fullness Journal",
                "desc": "Before and after each meal, rate your hunger and fullness (1–10). "
                        "Reconnects body awareness disrupted by PCOS-driven insulin "
                        "dysregulation. (Dutkiewicz et al., 2023)"
            },
            {
                "name": "Set 3 SMART Goals for Next Week",
                "desc": "Specific, Measurable, Achievable, Relevant, Time-bound — one for "
                        "diet, one for exercise, one for wellbeing. Written goals double "
                        "PCOS lifestyle adherence. (Pirotta et al., 2021)"
            },
            {
                "name": "Track Your Food Intake Today",
                "desc": "Use Cronometer, MyFitnessPal, or a written journal for all meals. "
                        "Self-monitoring is consistently the single strongest predictor of "
                        "sustained lifestyle change. (Pirotta et al., 2021)"
            },
            {
                "name": "Cook a New PCOS-Friendly Recipe",
                "desc": "Mediterranean, low-GI, or anti-inflammatory — find one online and "
                        "make it from scratch. Cooking skill-building improves long-term "
                        "dietary adherence. (Colombo et al., 2023)"
            },
            {
                "name": "Meal Prep for the Week Ahead",
                "desc": "Batch-cook grains, proteins, and roasted vegetables for 3 days. "
                        "Preparation removes the decision fatigue that leads to processed "
                        "food choices. (Scannell et al., 2022)"
            },
            {
                "name": "Identify One Emotional Eating Trigger",
                "desc": "Write the trigger, the emotion it creates, and one healthier coping "
                        "response. Awareness of the trigger-emotion-behaviour loop is the "
                        "essential first step. (Dutkiewicz et al., 2023)"
            },
            {
                "name": "Reach Out to a Support Person",
                "desc": "Share a win or challenge with a friend, partner, or PCOS community "
                        "member. Social support is one of the strongest independent "
                        "predictors of lifestyle adherence. (Pirotta et al., 2021)"
            },
            {
                "name": "20 Min Intentional Self-Care Ritual",
                "desc": "Face mask, relaxing bath, journaling, or reading — whatever feels "
                        "genuinely restorative. Intentional self-care measurably lowers "
                        "cortisol. (Cowan et al., 2023)"
            },
        ]

        day_minor = [
            {
                "name": "Review Progress Toward Your Goals",
                "desc": "Spend 5 minutes looking back at this week. Reflection reinforces "
                        "positive behaviour loops and motivates the next cycle. "
                        "(Pirotta et al., 2021)"
            },
            {
                "name": "Log Your Mood & Energy Level",
                "desc": "Rate both 1–10 in a journal or app. Tracking over weeks reveals "
                        "links between diet, sleep, and hormonal fluctuation. "
                        "(Pirotta et al., 2021)"
            },
            {
                "name": "3 Deep Breaths Before Each Meal",
                "desc": "Activates 'rest and digest' mode so your body actually absorbs "
                        "and processes the nutrients you eat efficiently. "
                        "(Dutkiewicz et al., 2023)"
            },
            {
                "name": "Drink Water Before Each Meal",
                "desc": "A glass of water 10 minutes before eating reduces false hunger, "
                        "slows eating pace, and supports digestive function. "
                        "(Das & Fatima, 2023)"
            },
            {
                "name": "One Positive Body Affirmation",
                "desc": "Say or write one compassionate statement about your body today. "
                        "Self-compassion is a measurable protective factor for PCOS "
                        "adherence and mental health. (Cowan et al., 2023)"
            },
            {
                "name": "Declutter Your Kitchen",
                "desc": "Remove one processed or high-sugar item from your pantry. Your "
                        "food environment shapes your choices more powerfully than willpower. "
                        "(Colombo et al., 2023)"
            },
        ]

    # =========================================================================
    # SUNDAY — 🌱 Holistic Wellness
    # Focus: weekly review, planning, supplementation, social & holistic care
    # Pool size: 10 major, 6 minor
    # =========================================================================
    else:
        daily_theme = "🌱 Holistic Wellness"

        day_major = [
            {
                "name": "Full Weekly Health Check-In",
                "desc": "Rate your energy, sleep, mood, digestion, and cycle regularity "
                        "(1–10). Identifying patterns across the 28-day cycle is how you "
                        "personalise the programme. (Gautam et al., 2025)"
            },
            {
                "name": "Prepare a Mediterranean-Style Meal",
                "desc": "Fish or legumes, a large salad, olive oil, and a whole grain. "
                        "Practise cooking as an act of self-care and hormonal investment. "
                        "(Capozzi et al., 2025)"
            },
            {
                "name": "Restorative Movement (45 Min)",
                "desc": "Gentle yoga, tai chi, or a relaxed nature walk. Sunday movement "
                        "should feel like recovery — keeps cortisol low while maintaining "
                        "the physical activity habit. (Cowan et al., 2023)"
            },
            {
                "name": "Review & Restock Your Supplements",
                "desc": "Check inositol, Vitamin D, Omega-3, and any others in your routine. "
                        "Consistent supplementation requires consistent supply — gaps break "
                        "the hormonal benefit. (Ghafari et al., 2025)"
            },
            {
                "name": "Plan Next Week's Exercise Schedule",
                "desc": "Write specific days, times, and exercise types into your calendar. "
                        "Pre-planning exercise is one of the highest-impact adherence "
                        "strategies across all PCOS lifestyle studies. "
                        "(Gautam et al., 2025)"
            },
            {
                "name": "Weekly Reflection Journal",
                "desc": "Write 3 wins, 1 challenge, and 1 clear intention for next week. "
                        "Written weekly reflection consolidates behaviour change across "
                        "the 28-day cycle. (Pirotta et al., 2021)"
            },
            {
                "name": "PCOS-Friendly Grocery Shop",
                "desc": "Stock up on leafy greens, omega-3 fish, legumes, whole grains, "
                        "olive oil, nuts, seeds, and berries. Your food environment is the "
                        "foundation of every habit this week. (Colombo et al., 2023)"
            },
            {
                "name": "Quality Time with Supportive People",
                "desc": "A meal, a call, or a walk with someone who supports your wellbeing. "
                        "Social connection is a measurable protective factor for mental "
                        "health outcomes in PCOS. (Pirotta et al., 2021)"
            },
            {
                "name": "20 Min Meditation or Breathwork",
                "desc": "Close the week with intention. Weekly mindfulness practice builds "
                        "cumulative HPA-axis resilience that carries into every day of the "
                        "next cycle. (Cowan et al., 2023)"
            },
            {
                "name": "Read One PCOS Habit or Recipe",
                "desc": "10 minutes of reading from a credible source. Health literacy "
                        "consistently improves self-management in chronic hormonal conditions. "
                        "(Gautam et al., 2025)"
            },
        ]

        day_minor = [
            {
                "name": "Drink 2 Cups Spearmint or Herbal Tea",
                "desc": "A calming Sunday ritual that doubles as androgen support. "
                        "Spearmint reduces free testosterone with consistent daily use. "
                        "(Rao et al., 2025)"
            },
            {
                "name": "Write Your Intention for Next Week",
                "desc": "One clear sentence is enough. Weekly intentions improve goal "
                        "pursuit and habit consistency across the 28-day cycle. "
                        "(Pirotta et al., 2021)"
            },
            {
                "name": "Relaxing Bath or Shower Ritual",
                "desc": "Intentional self-care signals the nervous system to shift from "
                        "stress mode to recovery — compounding the hormonal benefits of "
                        "the week's other habits. (Cowan et al., 2023)"
            },
            {
                "name": "Review This Week's Hydration",
                "desc": "Were you hitting 2L/day consistently? Chronic mild dehydration "
                        "is one of the most overlooked drivers of cortisol elevation. "
                        "(Das & Fatima, 2023)"
            },
            {
                "name": "Spend 15 Min in Sunlight",
                "desc": "Boosts Vitamin D synthesis, serotonin, and melatonin regulation — "
                        "three systems directly dysregulated in PCOS. "
                        "(Das & Fatima, 2023)"
            },
            {
                "name": "Prep Overnight Oats for Monday",
                "desc": "Set yourself up for a low-GI, high-fibre breakfast tomorrow. "
                        "Preparation is the most reliable form of motivation. "
                        "(Scannell et al., 2022)"
            },
        ]

    # =========================================================================
    # RANK LOGIC & POINT DISTRIBUTION
    # Points always sum to exactly 100 regardless of rank.
    # =========================================================================
    if "Seedling" in user_rank:
        n_major, n_minor = 5, 0
        pt_major, pt_minor = 20, 0       # 5 × 20 = 100

    elif "Sprout" in user_rank:
        n_major, n_minor = 5, 2
        pt_major, pt_minor = 16, 10      # (5 × 16) + (2 × 10) = 100

    else:  # PCOS Warrior
        n_major, n_minor = 7, 3
        pt_major, pt_minor = 10, 10      # (7 × 10) + (3 × 10) = 100

    # =========================================================================
    # SAMPLE THE QUESTS
    # random.sample guarantees no duplicates within a session.
    # Each call across 4 weeks (28 days) will produce a different combination
    # from the same pool — effectively creating 28 unique quest days.
    # =========================================================================
    selected_major = random.sample(day_major, n_major)
    selected_minor = random.sample(day_minor, n_minor) if n_minor > 0 else []

    for q in selected_major:
        q['points'] = pt_major
    for q in selected_minor:
        q['points'] = pt_minor

    return selected_major, selected_minor, daily_theme