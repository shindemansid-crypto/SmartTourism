# -*- coding: utf-8 -*-
from pathlib import Path

sql = r'''-- ============================================================
-- Smart Tourism & Local Culture Discovery Platform
-- MySQL 8.0+  |  Import in MySQL Workbench: File > Run SQL Script
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_tourism
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_tourism;
SET NAMES utf8mb4;

DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS AttractionTranslations;
DROP TABLE IF EXISTS Attractions;
DROP TABLE IF EXISTS Businesses;
DROP TABLE IF EXISTS SpecialityTranslations;
DROP TABLE IF EXISTS Specialities;
DROP TABLE IF EXISTS CultureTranslations;
DROP TABLE IF EXISTS CultureItems;
DROP TABLE IF EXISTS DestinationTranslations;
DROP TABLE IF EXISTS Destinations;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    UserID            INT AUTO_INCREMENT PRIMARY KEY,
    Username          VARCHAR(50)  NOT NULL UNIQUE,
    Email             VARCHAR(120) NOT NULL UNIQUE,
    PasswordHash      VARCHAR(255) NOT NULL,
    Role              ENUM('Tourist', 'Business', 'Admin') NOT NULL DEFAULT 'Tourist',
    PreferredLanguage VARCHAR(5)   NOT NULL DEFAULT 'en'
) ENGINE=InnoDB;

CREATE TABLE Destinations (
    DestinationID INT AUTO_INCREMENT PRIMARY KEY,
    Name          VARCHAR(100) NOT NULL,
    State         VARCHAR(50)  NOT NULL,
    Region        VARCHAR(50),
    Category      VARCHAR(50)  NOT NULL DEFAULT 'Heritage',
    ImageURL      VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE DestinationTranslations (
    TranslationID INT AUTO_INCREMENT PRIMARY KEY,
    DestinationID INT        NOT NULL,
    LanguageCode  VARCHAR(5) NOT NULL,
    Description   TEXT       NOT NULL,
    CONSTRAINT uq_dest_lang UNIQUE (DestinationID, LanguageCode),
    CONSTRAINT fk_desttrans_dest FOREIGN KEY (DestinationID)
        REFERENCES Destinations(DestinationID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Attractions (
    AttractionID  INT AUTO_INCREMENT PRIMARY KEY,
    Name          VARCHAR(150) NOT NULL,
    Category      VARCHAR(50)  NOT NULL,
    Latitude      DECIMAL(9,6) NOT NULL,
    Longitude     DECIMAL(9,6) NOT NULL,
    ImageURL      VARCHAR(255),
    DestinationID INT NOT NULL,
    CreatorID     INT NOT NULL,
    CONSTRAINT chk_latitude  CHECK (Latitude  BETWEEN -90 AND 90),
    CONSTRAINT chk_longitude CHECK (Longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_attr_dest FOREIGN KEY (DestinationID)
        REFERENCES Destinations(DestinationID) ON DELETE RESTRICT,
    CONSTRAINT fk_attr_creator FOREIGN KEY (CreatorID)
        REFERENCES Users(UserID) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE AttractionTranslations (
    TranslationID     INT AUTO_INCREMENT PRIMARY KEY,
    AttractionID      INT        NOT NULL,
    LanguageCode      VARCHAR(5) NOT NULL,
    Description       TEXT       NOT NULL,
    LocalSpecialities TEXT,
    CONSTRAINT uq_attr_lang UNIQUE (AttractionID, LanguageCode),
    CONSTRAINT fk_attrtrans_attr FOREIGN KEY (AttractionID)
        REFERENCES Attractions(AttractionID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Reviews (
    ReviewID     INT AUTO_INCREMENT PRIMARY KEY,
    UserID       INT NOT NULL,
    AttractionID INT NOT NULL,
    Rating       TINYINT NOT NULL,
    Comment      TEXT,
    `Timestamp`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rating CHECK (Rating BETWEEN 1 AND 5),
    CONSTRAINT uq_one_review UNIQUE (UserID, AttractionID),
    CONSTRAINT fk_review_user FOREIGN KEY (UserID)
        REFERENCES Users(UserID) ON DELETE CASCADE,
    CONSTRAINT fk_review_attr FOREIGN KEY (AttractionID)
        REFERENCES Attractions(AttractionID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE CultureItems (
    CultureID     INT AUTO_INCREMENT PRIMARY KEY,
    Title         VARCHAR(120) NOT NULL,
    ItemType      VARCHAR(40)  NOT NULL,
    ImageURL      VARCHAR(255),
    DestinationID INT NOT NULL,
    CONSTRAINT fk_culture_dest FOREIGN KEY (DestinationID)
        REFERENCES Destinations(DestinationID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE CultureTranslations (
    TranslationID INT AUTO_INCREMENT PRIMARY KEY,
    CultureID     INT        NOT NULL,
    LanguageCode  VARCHAR(5) NOT NULL,
    Description   TEXT       NOT NULL,
    CONSTRAINT uq_culture_lang UNIQUE (CultureID, LanguageCode),
    CONSTRAINT fk_culturetrans_item FOREIGN KEY (CultureID)
        REFERENCES CultureItems(CultureID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Specialities (
    SpecialityID   INT AUTO_INCREMENT PRIMARY KEY,
    Name           VARCHAR(120) NOT NULL,
    SpecialityType ENUM('Food', 'Craft') NOT NULL,
    ImageURL       VARCHAR(255),
    DestinationID  INT NOT NULL,
    CONSTRAINT fk_spec_dest FOREIGN KEY (DestinationID)
        REFERENCES Destinations(DestinationID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE SpecialityTranslations (
    TranslationID INT AUTO_INCREMENT PRIMARY KEY,
    SpecialityID  INT        NOT NULL,
    LanguageCode  VARCHAR(5) NOT NULL,
    Description   TEXT       NOT NULL,
    CONSTRAINT uq_spec_lang UNIQUE (SpecialityID, LanguageCode),
    CONSTRAINT fk_spectrans_item FOREIGN KEY (SpecialityID)
        REFERENCES Specialities(SpecialityID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Businesses (
    BusinessID    INT AUTO_INCREMENT PRIMARY KEY,
    Name          VARCHAR(150) NOT NULL,
    BusinessType  VARCHAR(40)  NOT NULL,
    Address       VARCHAR(200) NOT NULL,
    Phone         VARCHAR(20),
    Description   TEXT,
    ImageURL      VARCHAR(255),
    DestinationID INT NOT NULL,
    OwnerID       INT NOT NULL,
    CONSTRAINT fk_biz_dest FOREIGN KEY (DestinationID)
        REFERENCES Destinations(DestinationID) ON DELETE CASCADE,
    CONSTRAINT fk_biz_owner FOREIGN KEY (OwnerID)
        REFERENCES Users(UserID) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Passwords: Admin@123 | Business@123 | Tourist@123
INSERT INTO Users (UserID, Username, Email, PasswordHash, Role, PreferredLanguage) VALUES
(1, 'Admin',          'admin@smarttourism.com', 'pbkdf2:sha256:1000000$P49JlM19VyQ5HRgi$708a64b78886a9d6072d95a3d801d648dbe44d343b02a753fd2acd3342cf4869', 'Admin',    'en'),
(2, 'Meera Deshmukh', 'meera@example.com',      'pbkdf2:sha256:1000000$YZkf77ASR7F7lnTx$e8b58f13503627df0b39a27a017777faec6876a28b009772bc238a11fcadc30d', 'Business', 'mr'),
(3, 'Rajesh Patil',   'rajesh@example.com',     'pbkdf2:sha256:1000000$YZkf77ASR7F7lnTx$e8b58f13503627df0b39a27a017777faec6876a28b009772bc238a11fcadc30d', 'Business', 'en'),
(4, 'Aarav Sharma',   'aarav@example.com',      'pbkdf2:sha256:1000000$ZfXS8ktaDJm7Cnbf$6c140b8bbed03055c3229ee01a3738ae95f590e6e817f490bec87a18d43e4484', 'Tourist',  'hi'),
(5, 'Sneha Joshi',    'sneha@example.com',      'pbkdf2:sha256:1000000$ZfXS8ktaDJm7Cnbf$6c140b8bbed03055c3229ee01a3738ae95f590e6e817f490bec87a18d43e4484', 'Tourist',  'mr'),
(6, 'John Fernandes', 'john@example.com',       'pbkdf2:sha256:1000000$ZfXS8ktaDJm7Cnbf$6c140b8bbed03055c3229ee01a3738ae95f590e6e817f490bec87a18d43e4484', 'Tourist',  'en');

INSERT INTO Destinations (DestinationID, Name, State, Region, Category, ImageURL) VALUES
(1,  'Mumbai',                    'Maharashtra',         'West India',     'Heritage',     'images/dest-mumbai.svg'),
(2,  'Pune',                      'Maharashtra',         'West India',     'Cultural',     'images/dest-pune.svg'),
(3,  'Chhatrapati Sambhajinagar', 'Maharashtra',         'West India',     'Heritage',     'images/dest-sambhajinagar.svg'),
(4,  'Lonavala',                  'Maharashtra',         'West India',     'Hill Station', 'images/dest-lonavala.svg'),
(5,  'Mahabaleshwar',             'Maharashtra',         'West India',     'Hill Station', 'images/dest-mahableshwar.svg'),
(6,  'Delhi',                     'Delhi',               'North India',    'Historical',   'images/dest-delhi.svg'),
(7,  'Agra',                      'Uttar Pradesh',       'North India',    'Heritage',     'images/dest-agra.svg'),
(8,  'Varanasi',                  'Uttar Pradesh',       'North India',    'Religious',    'images/dest-varanasi.svg'),
(9,  'Jaipur',                    'Rajasthan',           'North India',    'Heritage',     'images/dest-jaipur.svg'),
(10, 'Udaipur',                   'Rajasthan',           'North India',    'Heritage',     'images/dest-udaipur.svg'),
(11, 'Amritsar',                  'Punjab',              'North India',    'Religious',    'images/dest-amritsar.svg'),
(12, 'Goa',                       'Goa',                 'West India',     'Beach',        'images/dest-goa.svg'),
(13, 'Munnar',                    'Kerala',              'South India',    'Hill Station', 'images/dest-munnar.svg'),
(14, 'Alleppey',                  'Kerala',              'South India',    'Nature',       'images/dest-alleppey.svg'),
(15, 'Hampi',                     'Karnataka',           'South India',    'Heritage',     'images/dest-hampi.svg'),
(16, 'Mysuru',                    'Karnataka',           'South India',    'Heritage',     'images/dest-mysore.svg'),
(17, 'Madurai',                   'Tamil Nadu',          'South India',    'Religious',    'images/dest-madurai.svg'),
(18, 'Ooty',                      'Tamil Nadu',          'South India',    'Hill Station', 'images/dest-ooty.svg'),
(19, 'Kevadia',                   'Gujarat',             'West India',     'Cultural',     'images/dest-kevadia.svg'),
(20, 'Rann of Kutch',             'Gujarat',             'West India',     'Cultural',     'images/dest-kutch.svg'),
(21, 'Kolkata',                   'West Bengal',         'East India',     'Heritage',     'images/dest-kolkata.svg'),
(22, 'Darjeeling',                'West Bengal',         'East India',     'Hill Station', 'images/dest-darjeeling.svg'),
(23, 'Shimla',                    'Himachal Pradesh',    'North India',    'Hill Station', 'images/dest-shimla.svg'),
(24, 'Manali',                    'Himachal Pradesh',    'North India',    'Adventure',    'images/dest-manali.svg'),
(25, 'Rishikesh',                 'Uttarakhand',         'North India',    'Adventure',    'images/dest-rishikesh.svg'),
(26, 'Nainital',                  'Uttarakhand',         'North India',    'Hill Station', 'images/dest-nainital.svg'),
(27, 'Srinagar',                  'Jammu & Kashmir',     'North India',    'Nature',       'images/dest-srinagar.svg'),
(28, 'Gulmarg',                   'Jammu & Kashmir',     'North India',    'Adventure',    'images/dest-gulmarg.svg'),
(29, 'Khajuraho',                 'Madhya Pradesh',      'Central India',  'Heritage',     'images/dest-khajuraho.svg');
'''

# Destination translations
dest_en = {
1: "India's financial capital on the Arabian Sea, mixing colonial landmarks, island caves and lively street food.",
2: "The cultural capital of Maharashtra, known for Peshwa-era monuments, hill forts and a rich food tradition.",
3: "Gateway to the UNESCO cave temples of Ajanta and Ellora, and a historic centre of Himroo weaving.",
4: "A Sahyadri hill station between Mumbai and Pune, famous for misty valleys, viewpoints and monsoon waterfalls.",
5: "A cool plateau in the Western Ghats known for strawberry farms, lake views and forest walks.",
6: "The national capital, layered with Mughal forts, colonial avenues and living markets.",
7: "Home of the Taj Mahal, a Mughal city on the Yamuna that remains one of the world's most visited heritage sites.",
8: "One of the world's oldest living cities, where the Ganga ghats, temples and silk weaving define daily life.",
9: "The Pink City of Rajasthan, known for palaces, forts and vibrant bazaars.",
10: "The City of Lakes, with palaces reflected in calm waters and a graceful Rajput heritage.",
11: "Spiritual heart of Sikhism, centred on the Golden Temple and its tradition of langar.",
12: "India's smallest state, known for beaches, Portuguese heritage churches and coastal cuisine.",
13: "Rolling tea gardens in the Western Ghats of Kerala, with cool weather and mountain viewpoints.",
14: "Kerala's backwater town, famous for houseboats gliding through palm-lined canals.",
15: "A landscape of boulder hills and ruined Vijayanagara temples, a UNESCO World Heritage Site.",
16: "The royal city of Karnataka, known for Mysore Palace, silk and Dasara festivities.",
17: "Temple city of Tamil Nadu, dominated by the towering gopurams of Meenakshi Amman Temple.",
18: "The Queen of Hill Stations in the Nilgiris, known for toy trains, gardens and cool climate.",
19: "Town beside the Narmada that hosts the Statue of Unity, one of the world's tallest statues.",
20: "A vast seasonal salt desert that turns into a white landscape and hosts the Rann Utsav.",
21: "Cultural capital of East India, known for colonial architecture, literature, sweets and Durga Puja.",
22: "Himalayan tea-town with toy-train rides, Kanchenjunga views and colonial-era charm.",
23: "Former summer capital of British India, set on forested ridges with Victorian architecture.",
24: "Adventure hub of Himachal, known for snow peaks, Solang Valley and mountain rivers.",
25: "Yoga capital on the Ganga, known for ashrams, the Lakshman Jhula and river rafting.",
26: "A lake town in the Kumaon hills, with Naini Lake, a mall road and forested viewpoints.",
27: "Summer capital of Jammu and Kashmir, famous for Dal Lake, houseboats and Mughal gardens.",
28: "A high meadow of flowers, now a popular skiing and gondola destination.",
29: "A cluster of Chandela temples famous for intricate stone sculpture, a UNESCO World Heritage Site.",
}
dest_hi = {
1: "अरब सागर पर भारत की आर्थिक राजधानी, जहाँ औपनिवेशिक इमारतें, द्वीप की गुफाएँ और जीवंत स्ट्रीट फूड मिलते हैं।",
2: "महाराष्ट्र की सांस्कृतिक राजधानी, पेशवाकालीन स्मारक, पहाड़ी किले और समृद्ध खान-पान परंपरा।",
3: "अजंता और एलोरा की यूनेस्को गुफाओं का प्रवेशद्वार तथा हिमरू बुनाई का ऐतिहासिक केंद्र।",
4: "मुंबई और पुणे के बीच सह्याद्रि की पहाड़ी, धुंधली घाटियों और मानसून जलप्रपातों के लिए प्रसिद्ध।",
5: "पश्चिमी घाट की ठंडी पठारी जगह, स्ट्रॉबेरी बागानों और झील के दृश्यों के लिए जानी जाती है।",
6: "राष्ट्रीय राजधानी, जहाँ मुगल किले, औपनिवेशिक मार्ग और जीवंत बाज़ार एक साथ हैं।",
7: "ताज महल की नगरी, यमुना तट पर बसा मुगल शहर और विश्व के प्रमुख धरोहर स्थलों में से एक।",
8: "विश्व के सबसे पुराने जीवित शहरों में से एक, जहाँ गंगा घाट, मंदिर और रेशम बुनाई जीवन का हिस्सा हैं।",
9: "राजस्थान का गुलाबी नगर, महलों, किलों और रंगीन बाज़ारों के लिए प्रसिद्ध।",
10: "झीलों का शहर, जहाँ महल शांत जल में प्रतिबिम्बित होते हैं।",
11: "सिख धर्म का आध्यात्मिक केंद्र, स्वर्ण मंदिर और लंगर की परंपरा के साथ।",
12: "भारत का सबसे छोटा राज्य, समुद्र तटों, पुर्तगाली गिरजाघरों और तटीय भोजन के लिए जाना जाता है।",
13: "केरल के पश्चिमी घाट में चाय बागान, ठंडी हवा और पहाड़ी दृश्य।",
14: "केरल का बैकवाटर नगर, ताड़ के पेड़ों के बीच हाउसबोट सफर के लिए प्रसिद्ध।",
15: "चट्टानी पहाड़ियों और विजयनगर के खंडित मंदिरों का यूनेस्को विश्व धरोहर स्थल।",
16: "कर्नाटक का राजसी शहर, मैसूर पैलेस, रेशम और दशहरा के लिए प्रसिद्ध।",
17: "तमिलनाडु का मंदिर नगर, मीनाक्षी अम्मन मंदिर के ऊँचे गोपुरम से जाना जाता है।",
18: "नीलगिरी की पहाड़ी रानी, टॉय ट्रेन, बगीचों और ठंडे मौसम के लिए प्रसिद्ध।",
19: "नर्मदा किनारे का नगर, जहाँ विश्व की सबसे ऊँची प्रतिमाओं में से एक स्टैच्यू ऑफ यूनिटी है।",
20: "विशाल नमक का रेगिस्तान, जो श्वेत परिदृश्य बन जाता है और रण उत्सव का आयोजन होता है।",
21: "पूर्व भारत की सांस्कृतिक राजधानी, औपनिवेशिक वास्तुकला, साहित्य, मिठाइयों और दुर्गा पूजा के लिए प्रसिद्ध।",
22: "हिमालय का चाय नगर, टॉय ट्रेन, कंचनजंगा के दृश्य और औपनिवेशिक आकर्षण।",
23: "ब्रिटिश भारत की ग्रीष्मकालीन राजधानी, जंगली पहाड़ियों पर विक्टोरियन वास्तुकला के साथ।",
24: "हिमाचल का साहसिक केंद्र, बर्फीली चोटियाँ, सोलंग घाटी और पर्वतीय नदियाँ।",
25: "गंगा तट पर योग नगरी, आश्रम, लक्ष्मण झूला और रिवर राफ्टिंग के लिए प्रसिद्ध।",
26: "कुमाऊँ की पहाड़ियों में झील नगर, नैनी झील और वन दृश्यों के साथ।",
27: "जम्मू-कश्मीर की ग्रीष्मकालीन राजधानी, डल झील, हाउसबोट और मुगल गार्डन के लिए प्रसिद्ध।",
28: "फूलों का ऊँचा मैदान, स्कीइंग और गोंडोला सफर के लिए लोकप्रिय।",
29: "चंदेल मंदिरों का समूह, जटिल पत्थर की मूर्तिकला के लिए यूनेस्को विश्व धरोहर।",
}

rows = []
for i, en in dest_en.items():
    rows.append(f"({i}, 'en', {repr(en)})")
    rows.append(f"({i}, 'hi', {repr(dest_hi[i])})")
sql += "\nINSERT INTO DestinationTranslations (DestinationID, LanguageCode, Description) VALUES\n"
sql += ",\n".join(rows) + ";\n"

sql += r'''
INSERT INTO Attractions (AttractionID, Name, Category, Latitude, Longitude, ImageURL, DestinationID, CreatorID) VALUES
(1,  'Ajanta Caves',                'Heritage',     20.551900, 75.703300, 'images/ajanta-caves.svg',         3,  1),
(2,  'Ellora Caves',                'Heritage',     20.026800, 75.179000, 'images/ellora-caves.svg',         3,  1),
(3,  'Gateway of India',            'Heritage',     18.922000, 72.834700, 'images/gateway-of-india.svg',     1,  1),
(4,  'Lonavala',                    'Hill Station', 18.748100, 73.407200, 'images/lonavala.svg',             4,  1),
(5,  'Mahabaleshwar',               'Hill Station', 17.930700, 73.647700, 'images/mahabaleshwar.svg',        5,  1),
(6,  'India Gate',                  'Historical',   28.612900, 77.229500, 'images/india-gate.svg',           6,  1),
(7,  'Red Fort',                    'Historical',   28.656200, 77.241000, 'images/red-fort.svg',             6,  1),
(8,  'Qutub Minar',                 'Heritage',     28.524500, 77.185500, 'images/qutub-minar.svg',          6,  1),
(9,  'Taj Mahal',                   'Heritage',     27.175100, 78.042100, 'images/taj-mahal.svg',            7,  1),
(10, 'Varanasi Ghats',              'Religious',    25.280700, 83.007500, 'images/varanasi-ghats.svg',       8,  1),
(11, 'Hawa Mahal',                  'Heritage',     26.923900, 75.826700, 'images/hawa-mahal.svg',           9,  1),
(12, 'Amer Fort',                   'Heritage',     26.985500, 75.851300, 'images/amer-fort.svg',            9,  1),
(13, 'City Palace Udaipur',         'Heritage',     24.576400, 73.683500, 'images/city-palace-udaipur.svg', 10,  1),
(14, 'Golden Temple',               'Religious',    31.620000, 74.876500, 'images/golden-temple.svg',       11,  1),
(15, 'Goa Beaches',                 'Beach',        15.552500, 73.754000, 'images/goa-beach.svg',           12,  1),
(16, 'Basilica of Bom Jesus',       'Heritage',     15.500900, 73.911600, 'images/basilica-bom-jesus.svg',  12,  1),
(17, 'Munnar Tea Hills',            'Hill Station', 10.088900, 77.059500, 'images/munnar.svg',              13,  1),
(18, 'Alleppey Backwaters',         'Nature',        9.498100, 76.338800, 'images/alleppey-backwaters.svg', 14,  1),
(19, 'Hampi Temples',               'Heritage',     15.335000, 76.460000, 'images/hampi.svg',               15,  1),
(20, 'Mysore Palace',               'Heritage',     12.305200, 76.655200, 'images/mysore-palace.svg',       16,  1),
(21, 'Meenakshi Temple',            'Religious',     9.919500, 78.119300, 'images/meenakshi-temple.svg',    17,  1),
(22, 'Ooty',                        'Hill Station', 11.406400, 76.693200, 'images/ooty.svg',                18,  1),
(23, 'Statue of Unity',             'Cultural',     21.838000, 73.719100, 'images/statue-of-unity.svg',     19,  1),
(24, 'Rann of Kutch',               'Cultural',     23.833300, 69.750000, 'images/rann-of-kutch.svg',       20,  1),
(25, 'Victoria Memorial',           'Heritage',     22.544800, 88.342600, 'images/victoria-memorial.svg',   21,  1),
(26, 'Darjeeling',                  'Hill Station', 27.036000, 88.262700, 'images/darjeeling.svg',          22,  1),
(27, 'Shimla Ridge',                'Hill Station', 31.104800, 77.173400, 'images/shimla.svg',              23,  1),
(28, 'Manali',                      'Adventure',    32.239600, 77.188700, 'images/manali.svg',              24,  1),
(29, 'Rishikesh',                   'Adventure',    30.086900, 78.267600, 'images/rishikesh.svg',           25,  1),
(30, 'Nainital Lake',               'Hill Station', 29.391900, 79.454200, 'images/nainital.svg',            26,  1),
(31, 'Dal Lake Srinagar',           'Nature',       34.108000, 74.868000, 'images/srinagar.svg',            27,  1),
(32, 'Gulmarg',                     'Adventure',    34.048400, 74.380500, 'images/gulmarg.svg',             28,  1),
(33, 'Khajuraho Temples',           'Heritage',     24.831800, 79.919900, 'images/khajuraho.svg',           29,  1);
'''

attr = [
(1, "A UNESCO World Heritage Site of rock-cut Buddhist caves famous for ancient paintings from the 2nd century BCE.", "Cave murals, Buddhist art, Himroo shawls",
 "छत्रपति संभाजीनगर के पास यूनेस्को विश्व धरोहर, प्राचीन बौद्ध चित्रों और मूर्तियों के लिए प्रसिद्ध शैलकृत गुफाएँ।", "प्राचीन भित्तिचित्र, बौद्ध कला"),
(2, "UNESCO rock-cut monuments of Buddhist, Hindu and Jain faiths, including the monolithic Kailasa Temple.", "Kailasa Temple, Maharashtrian thali, Himroo fabric",
 "बौद्ध, हिंदू और जैन शैलकृत स्मारक, जिनमें एकाश्म कैलास मंदिर शामिल है।", "कैलास मंदिर, महाराष्ट्रीयन थाली"),
(3, "An iconic basalt arch on the Mumbai waterfront, built in 1924, and the starting point for harbour ferries.", "Vada pav, street food, Elephanta ferry",
 "मुंबई के समुद्र तट पर 1924 में बना प्रतिष्ठित बेसाल्ट द्वार, बंदरगाह नौकाओं का प्रारंभ बिंदु।", "वड़ा पाव, स्ट्रीट फूड"),
(4, "A Sahyadri hill station known for misty valleys, monsoon waterfalls and viewpoints such as Lion's Point.", "Chikki, Maganlal farsan, valley viewpoints",
 "सह्याद्रि की पहाड़ी, धुंधली घाटियों, मानसून जलप्रपातों और लायंस पॉइंट जैसे दृश्य स्थलों के लिए प्रसिद्ध।", "चिक्की, घाटी दृश्य"),
(5, "A Western Ghats plateau famous for strawberries, Mapro gardens, Venna Lake and cool forest air.", "Strawberries, Mapro jam, lake boating",
 "पश्चिमी घाट का पठार, स्ट्रॉबेरी, मैप्रो गार्डन और वेन्ना झील के लिए प्रसिद्ध।", "स्ट्रॉबेरी, झील नौका"),
(6, "A 42-metre sandstone arch on Rajpath, a national war memorial and gathering place in New Delhi.", "Street food of Delhi, India Gate lawns",
 "राजपथ पर 42 मीटर का बलुआ पत्थर का द्वार, राष्ट्रीय युद्ध स्मारक।", "दिल्ली का स्ट्रीट फूड"),
(7, "The Mughal-era Lal Qila, a UNESCO World Heritage Site and the venue of the Independence Day address.", "Old Delhi food, Mughal architecture",
 "मुगलकालीन लाल किला, यूनेस्को विश्व धरोहर और स्वतंत्रता दिवस भाषण का स्थान।", "पुरानी दिल्ली का भोजन"),
(8, "A 12th-century victory tower, among the tallest brick minarets in the world, set in the Qutub complex.", "Mehrauli heritage, Indo-Islamic architecture",
 "12वीं शताब्दी का विजय स्तंभ, कुतुब परिसर में विश्व के सबसे ऊँचे ईंट मीनारों में से एक।", "इंडो-इस्लामिक वास्तुकला"),
(9, "White-marble mausoleum built by Shah Jahan for Mumtaz Mahal, a UNESCO World Heritage Site and symbol of India.", "Petha, Mughlai cuisine, marble inlay craft",
 "शाहजहाँ द्वारा मुमताज़ महल के लिए बनवाया श्वेत संगमरमर का मकबरा, भारत का प्रतीक।", "पेठा, मुग़लई व्यंजन, संगमरमर जड़ाई"),
(10, "Sacred stone steps along the Ganga, where aarti, pilgrimage and daily city life meet at dawn and dusk.", "Banarasi paan, silk, Ganga aarti",
 "गंगा के पवित्र घाट, जहाँ आरती, तीर्थ और शहर का दैनिक जीवन मिलते हैं।", "बनारसी पान, रेशम, गंगा आरती"),
(11, "The Palace of Winds, a five-storey honeycomb facade of pink sandstone built so royal women could watch street festivals.", "Rajasthani thali, blue pottery, bazaars",
 "हवा महल, गुलाबी बलुआ पत्थर का पाँच मंजिला छत्ते जैसा अग्रभाग।", "राजस्थानी थाली, ब्लू पॉटरी"),
(12, "A hill fort above Jaipur combining Rajput and Mughal styles, with palaces, gardens and elephant approaches.", "Dal baati churma, fort views",
 "जयपुर के ऊपर राजपूत-मुगल शैली का पहाड़ी किला, महलों और उद्यानों के साथ।", "दाल बाटी चूरमा"),
(13, "A sprawling palace complex on Lake Pichola, reflecting centuries of Mewar court life.", "Lake views, Mewari cuisine, miniature painting",
 "पिछोला झील पर विस्तृत महल परिसर, मेवाड़ दरबार की झलक।", "झील दृश्य, मेवाड़ी व्यंजन"),
(14, "Harmandir Sahib, the holiest gurdwara of Sikhism, with a golden sanctum in a sacred pool and free langar for all.", "Langar, Amritsari kulcha, phulkari",
 "हरमंदिर साहिब, सिख धर्म का पवित्र गुरुद्वारा, स्वर्ण गर्भगृह और सबके लिए लंगर।", "लंगर, अमृतसरी कुलचा, फुलकारी"),
(15, "Golden-sand beaches of North and South Goa, known for palm groves, seafood and a relaxed coastal rhythm.", "Goan fish curry, bebinca, beach shacks",
 "गोवा के सुनहरे समुद्र तट, ताड़ के पेड़, समुद्री भोजन और शांत तटीय जीवन।", "गोअन फिश करी, बेबिंका"),
(16, "A 16th-century UNESCO church in Old Goa that holds the relics of St. Francis Xavier.", "Old Goa heritage, Portuguese architecture",
 "ओल्ड गोवा का 16वीं शताब्दी का यूनेस्को गिरजाघर, संत फ्रांसिस जेवियर के अवशेषों के साथ।", "पुर्तगाली वास्तुकला"),
(17, "Carpeted tea estates in the Western Ghats, with cool mist, Eravikulam wildlife and mountain roads.", "Kerala tea, spices, hill viewpoints",
 "पश्चिमी घाट में चाय बागान, ठंडी धुंध और एराविकुलम वन्यजीव क्षेत्र।", "केरल चाय, मसाले"),
(18, "A maze of palm-lined canals travelled by houseboat, one of Kerala's most distinctive landscapes.", "Karimeen pollichathu, coconut dishes, houseboat stay",
 "ताड़ के पेड़ों वाले नहरों का जाल, हाउसबोट से घूमा जाने वाला केरल का विशिष्ट परिदृश्य।", "करीमीन, नारियल व्यंजन"),
(19, "Ruins of the Vijayanagara empire spread across boulder hills, with Vitthala and Virupaksha temples.", "Temple architecture, local banana, craft stalls",
 "विजयनगर साम्राज्य के खंडहर, विट्ठल और विरूपाक्ष मंदिरों के साथ।", "मंदिर वास्तुकला"),
(20, "An Indo-Saracenic royal palace illuminated at night, the centre of Mysuru Dasara.", "Mysore pak, silk, sandalwood",
 "रात में प्रकाशित इंडो-सरासेनिक राजमहल, मैसूर दशहरा का केंद्र।", "मैसूर पाक, रेशम, चंदन"),
(21, "A historic Dravidian temple with towering painted gopurams dedicated to Meenakshi and Sundareswarar.", "Idli, filter coffee, temple town markets",
 "मीनाक्षी और सुंदरेश्वर को समर्पित ऊँचे चित्रित गोपुरम वाला द्रविड़ मंदिर।", "इडली, फ़िल्टर कॉफ़ी"),
(22, "Nilgiri hill station with botanical gardens, a heritage toy train and eucalyptus-scented air.", "Nilgiri tea, chocolate, toy train",
 "नीलगिरी की पहाड़ी, बॉटनिकल गार्डन और विरासत टॉय ट्रेन।", "नीलगिरी चाय"),
(23, "A 182-metre statue of Sardar Vallabhbhai Patel on the Narmada, with a viewing gallery and valley views.", "Gujarati thali, dhokla, river cruise",
 "नर्मदा पर सरदार वल्लभभाई पटेल की 182 मीटर ऊँची प्रतिमा।", "गुजराती थाली, ढोकला"),
(24, "A seasonal white salt desert that hosts the Rann Utsav of crafts, music and tent stays.", "Kutchi embroidery, white desert, folk music",
 "मौसमी श्वेत नमक मरुस्थल, जहाँ शिल्प और संगीत का रण उत्सव लगता है।", "कच्छी कढ़ाई, लोक संगीत"),
(25, "A white-marble memorial in a formal garden, the grandest colonial monument of Kolkata.", "Rosogolla, mishti doi, book markets",
 "औपचारिक उद्यान में श्वेत संगमरमर का स्मारक, कोलकाता का भव्य औपनिवेशिक स्मारक।", "रसगुल्ला, मिष्टि दही"),
(26, "A Himalayan tea town with the Darjeeling Himalayan Railway, Kanchenjunga views and colonial hotels.", "Darjeeling tea, momos, toy train",
 "हिमालय का चाय नगर, दार्जिलिंग हिमालयन रेलवे और कंचनजंगा के दृश्य।", "दार्जिलिंग चाय, मोमो"),
(27, "Ridge and Mall Road of the former British summer capital, with cedar forests and Victorian buildings.", "Himachali dham, cedar walks, colonial architecture",
 "ब्रिटिश ग्रीष्मकालीन राजधानी की रिज और मॉल रोड, देवदार वनों के साथ।", "हिमाचली धाम"),
(28, "Gateway to Rohtang and Solang, a base for snow sports, treks and mountain rivers.", "Siddu, trout, adventure sports",
 "रोहतांग और सोलंग का प्रवेशद्वार, बर्फ खेल और ट्रेक का आधार।", "सिडू, एडवेंचर खेल"),
(29, "Ashrams, the Ganga aarti and white-water rafting in the yoga capital of India.", "Aloo puri, ashram stays, river rafting",
 "भारत की योग राजधानी, आश्रम, गंगा आरती और रिवर राफ्टिंग।", "आश्रम, राफ्टिंग"),
(30, "A pear-shaped Himalayan lake circled by a mall road, boats and forested viewpoints.", "Bal mithai, lake boating, hill walks",
 "नाशपाती के आकार की हिमालयी झील, नौकाओं और वन दृश्यों के साथ।", "बाल मिठाई, झील नौका"),
(31, "Lotus-dotted Dal Lake with wooden houseboats and shikara rides beside Mughal gardens.", "Rogan josh, kahwa, pashmina",
 "कमलों वाली डल झील, लकड़ी के हाउसबोट और शिकारा सफर।", "रोगन जोश, कहवा, पश्मीना"),
(32, "A high meadow famous for skiing in winter and gondola rides over pine forests in summer.", "Kahwa, skiing, meadow walks",
 "सर्दियों में स्कीइंग और गर्मियों में गोंडोला सफर के लिए प्रसिद्ध ऊँचा मैदान।", "कहवा, स्कीइंग"),
(33, "Chandela-era temples covered in sculpted friezes, a UNESCO World Heritage Site in Bundelkhand.", "Temple sculpture, Bundelkhand cuisine",
 "मूर्तिकला से ढके चंदेलकालीन मंदिर, बुंदेलखंड में यूनेस्को विश्व धरोहर।", "मंदिर शिल्प"),
]

rows = []
for aid, en, spec, hi, hispec in attr:
    rows.append(f"({aid}, 'en', {repr(en)}, {repr(spec)})")
    rows.append(f"({aid}, 'hi', {repr(hi)}, {repr(hispec)})")
sql += "\nINSERT INTO AttractionTranslations (AttractionID, LanguageCode, Description, LocalSpecialities) VALUES\n"
sql += ",\n".join(rows) + ";\n"

sql += r'''
INSERT INTO Reviews (UserID, AttractionID, Rating, Comment) VALUES
(4, 9,  5, 'The Taj at sunrise is unforgettable. Hire a licensed guide for the inlay work details.'),
(6, 3,  4, 'Gateway of India is beautiful at sunset, though weekends are crowded.'),
(5, 1,  5, 'Ajanta paintings are breathtaking. Start early to avoid queues.'),
(4, 2,  5, 'The Kailasa Temple at Ellora feels impossible to believe until you stand there.'),
(6, 14, 5, 'The Golden Temple at night is peaceful. The langar is a moving experience.'),
(5, 11, 4, 'Hawa Mahal is smaller than photos suggest but the pink facade is stunning.'),
(4, 18, 5, 'Alleppey houseboat was the highlight of Kerala. Ask for karimeen for dinner.'),
(6, 15, 4, 'North Goa beaches are lively; Old Goa churches are worth a quiet morning.'),
(5, 31, 5, 'A shikara ride on Dal Lake at dusk is the most beautiful hour in Srinagar.'),
(4, 32, 5, 'Gulmarg gondola views are spectacular. Carry warm clothes even in summer.'),
(6, 23, 4, 'Statue of Unity is massive. Combine it with the valley garden.'),
(5, 21, 5, 'Meenakshi Temple gopurams are overwhelming in the best way.'),
(4, 29, 4, 'Rishikesh aarti on the Ganga is soulful. Rafting needs a trusted operator.'),
(6, 25, 4, 'Victoria Memorial gardens are perfect in winter light.'),
(5, 4,  4, 'Lonavala in the monsoon is magical. Chikki shopping is mandatory.');

INSERT INTO CultureItems (CultureID, Title, ItemType, ImageURL, DestinationID) VALUES
(1,  'Ganesh Chaturthi',     'Festival',     'images/culture-ganesh-chaturthi.svg', 1),
(2,  'Lavani',               'Folk Dance',   'images/culture-lavani.svg',           2),
(3,  'Warli Art',            'Handicraft',   'images/culture-warli.svg',            1),
(4,  'Kathakali',            'Folk Arts',    'images/culture-kathakali.svg',        13),
(5,  'Onam',                 'Festival',     'images/culture-onam.svg',             14),
(6,  'Garba',                'Festival',     'images/culture-garba.svg',            20),
(7,  'Bhangra',              'Folk Dance',   'images/culture-bhangra.svg',          11),
(8,  'Phulkari',             'Traditional Clothing', 'images/culture-phulkari.svg', 11),
(9,  'Durga Puja',           'Festival',     'images/culture-durga-puja.svg',       21),
(10, 'Rajasthani Folk',      'Folk Arts',    'images/culture-rajasthani.svg',       9),
(11, 'Kathak',               'Folk Dance',   'images/culture-kathak.svg',           7),
(12, 'Kumbh Mela Tradition', 'Local Tradition', 'images/culture-kumbh-mela.svg',   8);

INSERT INTO CultureTranslations (CultureID, LanguageCode, Description) VALUES
(1,  'en', 'A ten-day festival of clay Ganesha idols in homes and public pandals, ending with immersion in water.'),
(1,  'hi', 'मिट्टी की गणेश प्रतिमाओं का दस दिवसीय उत्सव, घरों और पंडालों में स्थापना के बाद विसर्जन।'),
(2,  'en', 'Energetic Maharashtrian folk dance performed to the dholki, with nine-yard sarees and expressive songs.'),
(2,  'hi', 'ढोलकी पर महाराष्ट्रीयन लोकनृत्य, नौवारी साड़ी और भावपूर्ण गीतों के साथ।'),
(3,  'en', 'Tribal painting of Maharashtra using simple white figures of humans, animals and harvest scenes on mud walls.'),
(3,  'hi', 'महाराष्ट्र की आदिवासी चित्रकला, मिट्टी की दीवारों पर सफेद मानवाकृतियाँ और फसल के दृश्य।'),
(4,  'en', 'Classical dance-drama of Kerala with elaborate makeup, costumes and mudras that tell epic stories.'),
(4,  'hi', 'केरल का शास्त्रीय नृत्य-नाट्य, विस्तृत मेकअप और मुद्राओं के साथ महाकाव्य कथाएँ।'),
(5,  'en', 'Kerala harvest festival marked by pookalam flower carpets, the Onam sadya feast and snake-boat races.'),
(5,  'hi', 'केरल का फसल उत्सव, फूलों की पookalam rangoli, ओणम साध्य भोज और नाव दौड़।'),
(6,  'en', 'Circular folk dance of Gujarat performed during Navratri around a garba lantern, in colourful chaniya choli.'),
(6,  'hi', 'नवरात्रि में गुजरात का चक्राकार लोकनृत्य, रंगीन चनिया चोली में गर्बा के चारों ओर।'),
(7,  'en', 'High-energy Punjabi harvest dance with dhol beats, jumps and bright phulkari dupattas.'),
(7,  'hi', 'ढोल की थाप पर ऊर्जावान पंजाबी फसल नृत्य, फुलकारी दुपट्टों के साथ।'),
(8,  'en', 'Punjab embroidery of floral motifs in silk floss on coarse cotton, traditionally made for weddings.'),
(8,  'hi', 'पंजाब की फूलों वाली कढ़ाई, मोटे सूती कपड़े पर रेशम से, पारंपरिक रूप से विवाह के लिए।'),
(9,  'en', 'Bengal''s grand autumn festival of Goddess Durga, with artistic pandals, dhak drums and community feasts.'),
(9,  'hi', 'देवी दुर्गा का बंगाल का भव्य शरद उत्सव, कलात्मक पंडाल, ढाक और सामुदायिक भोज।'),
(10, 'en', 'Music and dance of Rajasthan, from kalbeliya and ghoomar to puppetry and desert folk instruments.'),
(10, 'hi', 'राजस्थान का संगीत और नृत्य, कलबेलिया, घूमर, कठपुतली और मरुस्थली लोक वाद्य।'),
(11, 'en', 'North Indian classical dance of storytelling through footwork, spins and expressive eyes, linked to temple and court traditions.'),
(11, 'hi', 'उत्तर भारतीय शास्त्रीय नृत्य, पद संचालन और भाव से कथा कथन, मंदिर और दरबार परंपरा से जुड़ा।'),
(12, 'en', 'A major Hindu pilgrimage held in cycles on sacred rivers, including gatherings associated with Varanasi and other tirthas.'),
(12, 'hi', 'पवित्र नदियों पर चक्रों में लगने वाला प्रमुख हिंदू तीर्थ, वाराणसी सहित कई तीर्थों से जुड़ा।');

INSERT INTO Specialities (SpecialityID, Name, SpecialityType, ImageURL, DestinationID) VALUES
(1,  'Misal Pav',           'Food',  'images/spec-misal-pav.svg',     2),
(2,  'Puran Poli',          'Food',  'images/spec-puran-poli.svg',    2),
(3,  'Modak',               'Food',  'images/spec-modak.svg',         1),
(4,  'Vada Pav',            'Food',  'images/spec-vada-pav.svg',      1),
(5,  'Dhokla',              'Food',  'images/spec-dhokla.svg',        19),
(6,  'Dal Baati Churma',    'Food',  'images/spec-dal-baati.svg',     9),
(7,  'Amritsari Kulcha',    'Food',  'images/spec-amritsari.svg',     11),
(8,  'Rosogolla',           'Food',  'images/spec-rosogolla.svg',     21),
(9,  'Masala Dosa',         'Food',  'images/spec-dosa.svg',          16),
(10, 'Goan Fish Curry',     'Food',  'images/spec-goan-curry.svg',    12),
(11, 'Rogan Josh',          'Food',  'images/spec-rogan-josh.svg',    27),
(12, 'Paithani Saree',      'Craft', 'images/spec-paithani.svg',      2),
(13, 'Blue Pottery',        'Craft', 'images/spec-blue-pottery.svg',  9),
(14, 'Pashmina',            'Craft', 'images/spec-pashmina.svg',      27),
(15, 'Chikankari',          'Craft', 'images/spec-chikankari.svg',    8);

INSERT INTO SpecialityTranslations (SpecialityID, LanguageCode, Description) VALUES
(1,  'en', 'A spicy sprouted-moth curry topped with farsan and served with pav, a signature Maharashtrian breakfast.'),
(1,  'hi', 'फरसान से सजी तीखी मोठ की मिसल, पाव के साथ महाराष्ट्रीयन नाश्ता।'),
(2,  'en', 'A sweet stuffed flatbread of jaggery and chana dal, prepared for festivals in Maharashtra.'),
(2,  'hi', 'गुड़ और चना दाल से भरी मीठी रोटी, महाराष्ट्र के त्योहारों की विशेषता।'),
(3,  'en', 'Steamed rice-flour dumplings with coconut-jaggery filling, offered to Lord Ganesha.'),
(3,  'hi', 'नारियल-गुड़ की भरावन वाले भाप में पके मोदक, गणेश को अर्पित किए जाते हैं।'),
(4,  'en', 'A spiced potato fritter in a bun with garlic chutney, Mumbai''s classic street snack.'),
(4,  'hi', 'लहसुन चटनी के साथ पाव में आलू वड़ा, मुंबई का क्लासिक स्ट्रीट स्नैक।'),
(5,  'en', 'A steamed fermented gram-flour cake, light and spongy, a Gujarati favourite.'),
(5,  'hi', 'भाप में पका नरम बेसन का ढोकला, गुजरात का प्रिय नाश्ता।'),
(6,  'en', 'Hard baked wheat balls with lentil curry and sweet crushed churma, the hearty meal of Rajasthan.'),
(6,  'hi', 'दाल के साथ पकी बाटी और मीठा चूरमा, राजस्थान का हृष्ट-पुष्ट भोजन।'),
(7,  'en', 'Stuffed tandoor bread of Amritsar, served with chole, butter and pickle.'),
(7,  'hi', 'अमृतसर की तंदूरी भरी कुलचा, छोले, मक्खन और अचार के साथ।'),
(8,  'en', 'Soft chenna balls in light sugar syrup, Bengal''s most famous sweet.'),
(8,  'hi', 'हल्की चाशनी में नरम छेने के रसगुल्ले, बंगाल की प्रसिद्ध मिठाई।'),
(9,  'en', 'Crisp fermented rice-lentil crepe filled with spiced potato, a South Indian staple.'),
(9,  'hi', 'मसालेदार आलू भरी कुरकुरी चावल-दाल की डोसा, दक्षिण भारत का मुख्य व्यंजन।'),
(10, 'en', 'Tangy coconut and kokum fish curry of the Goan coast, served with rice.'),
(10, 'hi', 'नारियल और कोकम वाली तीखी-खट्टी गोअन मछली करी, चावल के साथ।'),
(11, 'en', 'Aromatic Kashmiri lamb curry coloured with Kashmiri chilli, served with steamed rice.'),
(11, 'hi', 'कश्मीरी मिर्च से रंगी सुगंधित मटन करी, भात के साथ परोसी जाती है।'),
(12, 'en', 'Handwoven silk sarees with peacock and lotus motifs and gold zari borders from Maharashtra.'),
(12, 'hi', 'मोर और कमल की नक्काशी तथा सुनहरी जरी किनारी वाली महाराष्ट्र की रेशमी साड़ियाँ।'),
(13, 'en', 'Quartz-glazed turquoise pottery of Jaipur, painted with floral and animal motifs.'),
(13, 'hi', 'जयपुर की फ़िरोज़ी ब्लू पॉटरी, फूलों और पशु आकृतियों से चित्रित।'),
(14, 'en', 'Fine wool shawls from Kashmir, prized for warmth, softness and woven or embroidered patterns.'),
(14, 'hi', 'कश्मीर की महीन ऊनी शॉल, कोमलता और कढ़ाई के लिए प्रसिद्ध।'),
(15, 'en', 'Delicate white-on-white embroidery of Lucknow, used on muslin kurtas and dupattas.'),
(15, 'hi', 'लखनऊ की सफेद चिकनकारी कढ़ाई, मलमल कुर्ते और दुपट्टों पर।');

INSERT INTO Businesses (BusinessID, Name, BusinessType, Address, Phone, Description, ImageURL, DestinationID, OwnerID) VALUES
(1, 'Yeola Paithani Weaving Centre', 'Handloom',         'Main Road, Yeola, Nashik district',     '9800000001', 'Family-run centre where visitors can watch Paithani weaving and buy sarees from weavers.', 'images/biz-paithani.svg', 2, 2),
(2, 'Puneri Misal House',            'Restaurant',       'Laxmi Road, Pune',                      '9800000002', 'Local eatery serving misal pav, puran poli and tea-time bakarwadi.', 'images/biz-misal.svg', 2, 3),
(3, 'Jaipur Heritage Walks',         'Local Guide',      'Old City, near Hawa Mahal, Jaipur',     '9800000003', 'Licensed local guides for Amber Fort, bazaars and evening heritage walks.', 'images/biz-guide-jaipur.svg', 9, 3),
(4, 'Kashmir Craft House',           'Handicraft',       'Boulevard Road, Srinagar',              '9800000004', 'Pashmina, papier-mache and walnut woodwork from local artisan families.', 'images/biz-kashmir-crafts.svg', 27, 2),
(5, 'Goa Coastal Guides',            'Tourism Service',  'Calangute, North Goa',                  '9800000005', 'Beach and Old Goa heritage walks with local naturalists.', 'images/biz-goa-guide.svg', 12, 3),
(6, 'Alleppey Houseboat Co-op',      'Tourism Service',  'Boat Jetty Road, Alappuzha',            '9800000006', 'Community-run kettuvallam houseboats with home-style Kerala meals.', 'images/biz-kerala-houseboat.svg', 14, 2),
(7, 'Kolkata Mishti Ghar',           'Restaurant',       'College Street, Kolkata',               '9800000007', 'Neighbourhood sweet shop for rosogolla, sandesh and mishti doi.', 'images/biz-kolkata-sweet.svg', 21, 3),
(8, 'Banarasi Silk Atelier',         'Handloom',         'Godaulia, Varanasi',                    '9800000008', 'Weaver-owned shop for authentic Banarasi brocades.', 'images/biz-varanasi-silk.svg', 8, 2),
(9, 'Amritsar Culinary Walks',       'Cultural Service', 'Hall Bazaar, Amritsar',                 '9800000009', 'Food walks covering kulcha, lassi and the Golden Temple neighbourhood.', 'images/biz-amritsar-langar.svg', 11, 3),
(10,'Kolhapuri Craft Studio',        'Artisan',          'Mahadwar Road, Kolhapur',               '9800000010', 'Handmade Kolhapuri chappals and leathercraft by local artisans.', 'images/biz-chappal.svg', 2, 2);
'''

# Fix the Onam hi text that accidentally had English inside
sql = sql.replace("फूलों की पookalam rangoli", "फूलों की पूकलम रंगोली")

Path("database.sql").write_text(sql, encoding="utf-8")
print("Wrote database.sql", len(sql), "chars")
