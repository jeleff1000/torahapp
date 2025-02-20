# Define the Parshiyot of the Torah and their corresponding books
parshiyot = {
    "Genesis": ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sarah", "Toldot", "Vayetzei", "Vayishlach",
                "Vayeshev", "Miketz", "Vayigash", "Vayechi"],
    "Exodus": ["Shemot", "Vaera", "Bo", "Beshalach", "Yitro", "Mishpatim", "Terumah", "Tetzaveh", "Ki Tisa", "Vayakhel",
               "Pekudei"],
    "Leviticus": ["Vayikra", "Tzav", "Shemini", "Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar",
                  "Bechukotai"],
    "Numbers": ["Bamidbar", "Naso", "Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak", "Pinchas", "Matot",
                "Masei"],
    "Deuteronomy": ["Devarim", "Vaetchanan", "Eikev", "Re'eh", "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim",
                    "Vayeilech", "Haazinu", "V'Zot HaBerachah"]
}

# Define the Haftarah readings for each Parsha
parsha_haftarah = {
    "Bereshit": "Isaiah 42:5-43:10",
    "Noach": "Isaiah 54:1-55:5",
    "Lech Lecha": "Isaiah 40:27-41:16",
    "Vayera": "II Kings 4:1-37",
    "Chayei Sarah": "I Kings 1:1-31",
    "Toldot": "Malachi 1:1-2:7",
    "Vayetzei": "Hosea 12:13-14:10",
    "Vayishlach": "Obadiah 1:1-21",
    "Vayeshev": "Amos 2:6-3:8",
    "Miketz": "I Kings 3:15-4:1",
    "Vayigash": "Ezekiel 37:15-28",
    "Vayechi": "I Kings 2:1-12",
    "Shemot": ["Isaiah 27:6-28:13", "Isaiah 29:22-23"],
    "Vaera": "Ezekiel 28:25-29:21",
    "Bo": "Jeremiah 46:13-28",
    "Beshalach": "Judges 4:4-5:31",
    "Yitro": ["Isaiah 6:1-7:6", "Isaiah 9:5-6"],
    "Mishpatim": ["Jeremiah 34:8-22", "Jeremiah 33:25-26"],
    "Terumah": "I Kings 5:26-6:13",
    "Tetzaveh": "Ezekiel 43:10-27",
    "Ki Tisa": "I Kings 18:1-39",
    "Vayakhel": "I Kings 7:40-50",
    "Pekudei": "I Kings 7:51-8:21",
    "Vayikra": "Isaiah 43:21-44:23",
    "Tzav": ["Jeremiah 7:21-8:3", "Jeremiah 9:22-23"],
    "Shemini": "II Samuel 6:1-7:17",
    "Tazria": "II Kings 4:42-5:19",
    "Metzora": "II Kings 7:3-20",
    "Achrei Mot": "Ezekiel 22:1-19",
    "Kedoshim": "Amos 9:7-15",
    "Emor": "Ezekiel 44:15-31",
    "Behar": "Jeremiah 32:6-27",
    "Bechukotai": "Jeremiah 16:19-17:14",
    "Bamidbar": "Hosea 2:1-22",
    "Naso": "Judges 13:2-25",
    "Beha'alotcha": "Zechariah 2:14-4:7",
    "Sh'lach": "Joshua 2:1-24",
    "Korach": "I Samuel 11:14-12:22",
    "Chukat": "Judges 11:1-33",
    "Balak": "Micah 5:6-6:8",
    "Pinchas": "I Kings 18:46-19:21",
    "Matot": "Jeremiah 1:1-2:3",
    "Masei": ["Jeremiah 2:4-28", "Jeremiah 3:4"],
    "Devarim": "Isaiah 1:1-27",
    "Vaetchanan": "Isaiah 40:1-26",
    "Eikev": "Isaiah 49:14-51:3",
    "Re'eh": "Isaiah 54:11-55:5",
    "Shoftim": "Isaiah 51:12-52:12",
    "Ki Teitzei": "Isaiah 54:1-10",
    "Ki Tavo": "Isaiah 60:1-22",
    "Nitzavim": "Isaiah 61:10-63:9",
    "Vayeilech":"Isaiah 55:6-56:8",
    "Haazinu": "II Samuel 22:1-51",
    "V'Zot HaBerachah": "Joshua 1:1-18"
}

# Define the chronological order for holiday readings
holiday_order = [
    "First Day of Rosh Hashanah",
    "Second Day of Rosh Hashanah",
    "Fast of Gedaliah",
    "Shabbat Shuvah (between Rosh Hashanah and Yom Kippur)",
    "Shabbat Shuvah (between Rosh Hashanah and Yom Kippur alternative)",
    "Shabbat Shuvah (Sephardim), or alternative for Shabbat Shuvah",
    "Yom Kippur Morning",
    "Fast of Yom Kippur (Mincha)",
    "First Day of Sukkot",
    "Second Day of Sukkot",
    "Shabbat Chol HaMoed Sukkot",
    "Shemini Atzeret",
    "Fast of Tevet 10",
    "Fast of Esther",
    "First Day of Pesach",
    "Second Day of Pesach",
    "Shabbat Chol HaMoed Pesach",
    "First Day of Shavuot",
    "Second Day of Shavuot",
    "Fast of Tammuz 17",
    "Fast of Tisha B’Av (Evening & Morning)",
    "Fast of Tisha B’Av (Afternoon)"
]

# Define the full Haftarah mapping
haftarah_mapping = {
    "I Samuel 1:1-2:10": "First Day of Rosh Hashanah",
    "Jeremiah 31:1-19": "Second Day of Rosh Hashanah",
    "Isaiah 55:6-56:8": "Fast of Gedaliah",
    "Hosea 14:2-10": "Shabbat Shuvah (between Rosh Hashanah and Yom Kippur)",
    "Joel 2:15-27": "Shabbat Shuvah (between Rosh Hashanah and Yom Kippur alternative)",
    "Micah 7:18-20": "Shabbat Shuvah (Sephardim), or alternative for Shabbat Shuvah",
    "Isaiah 57:14-58:14": "Yom Kippur Morning",
    "Jonah 1:1-4:11, Micah 7:18-20": "Fast of Yom Kippur (Mincha)",
    "Zechariah 14:1-21": "First Day of Sukkot",
    "I Kings 8:2-21": "Second Day of Sukkot",
    "Ezekiel 38:18-39:16": "Shabbat Chol HaMoed Sukkot",
    "I Kings 8:54-66": "Shemini Atzeret",
    "Isaiah 55:6-56:8": "Fast of Tevet 10",
    "Exodus 32:11-34:10": "Fast of Esther",
    "Joshua 5:2-6:1": "First Day of Pesach",
    "II Kings 23:1-9, 23:21-25": "Second Day of Pesach",
    "Ezekiel 37:1-14": "Shabbat Chol HaMoed Pesach",
    "Ezekiel 1:1-28, 3:12": "First Day of Shavuot",
    "Habakkuk 3:1-19": "Second Day of Shavuot",
    "Isaiah 55:6-56:8": "Fast of Tammuz 17",
    "Jeremiah 8:13-9:23": "Fast of Tisha B’Av (Evening & Morning)",
    "Isaiah 55:6-56:8": "Fast of Tisha B’Av (Afternoon)"
}

# Create separate dictionaries for Shabbat and Holiday readings
shabbat_readings = {}
holiday_readings = {}

# Map Haftarah readings to corresponding Parshiyot and Holidays
for parsha, haftarahs in parsha_haftarah.items():
    for book, parshas in parshiyot.items():
        if parsha in parshas:
            if book not in shabbat_readings:
                shabbat_readings[book] = {}
            shabbat_readings[book][parsha] = haftarahs

for haftarah, occasion in haftarah_mapping.items():
    holiday_readings[occasion] = haftarah

# Sort Holiday readings chronologically
sorted_holiday_readings = {holiday: holiday_readings[holiday] for holiday in holiday_order if holiday in holiday_readings}

# Sort Shabbat readings by book and parsha
sorted_shabbat_readings = [(book, parsha, haftarah) for book in parshiyot for parsha in parshiyot[book] if book in shabbat_readings and parsha in shabbat_readings[book]]