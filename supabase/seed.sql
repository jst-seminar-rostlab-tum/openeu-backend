-- =======================
-- Seed for mep_meetings
-- =======================
INSERT INTO mep_meetings (
    title,
    member_name,
    meeting_date,
    meeting_location,
    member_capacity,
    procedure_reference,
    associated_committee_or_delegation_code,
    associated_committee_or_delegation_name,
    embedding_input
)
VALUES 
(
    'Meeting on Digital Markets Act',
    'Alexandra Geese',
    '2025-05-25',
    'Brussels, EU Parliament',
    'Shadow Rapporteur',
    '2020/0374(COD)',
    'IMCO',
    'Committee on the Internal Market and Consumer Protection',
    'Meeting on Digital Markets Act, on 2025-05-25 at Brussels, EU Parliament, by Alexandra Geese (Shadow Rapporteur), referenced procedure: 2020/0374(COD), committee: Committee on the Internal Market and Consumer Protection'

),
(
    'Hearing on Green Transition Policies',
    'Bas Eickhout',
    '2025-06-03',
    'Strasbourg, Room A3G-2',
    'Vice-Chair',
    '2021/0202(COD)',
    'ENVI',
    'Committee on the Environment, Public Health and Food Safety',
    'Hearing on Green Transition Policies, on 2025-06-03 at Strasbourg, Room A3G-2, by Bas Eickhout (Vice-Chair), referenced procedure: 2021/0202(COD), committee: Committee on the Environment, Public Health and Food Safety'
),
(
    'AI Act Implementation Discussion',
    'Dragos Tudorache',
    '2025-06-10',
    'Brussels, Room PHS 3C50',
    'Rapporteur',
    '2021/0106(COD)',
    'LIBE',
    'Committee on Civil Liberties, Justice and Home Affairs',
    'AI Act Implementation Discussion, on 2025-06-10 at Brussels, Room PHS 3C50, by Dragos Tudorache (Rapporteur), referenced procedure: 2021/0106(COD), committee: Committee on Civil Liberties, Justice and Home Affairs'
),
(
    'Data Privacy Framework Review',
    'Birgit Sippel',
    '2025-06-15',
    'Brussels, Room JAN 4Q1',
    'Coordinator',
    '2021/0136(COD)',
    'LIBE',
    'Committee on Civil Liberties, Justice and Home Affairs',
    'Data Privacy Framework Review, on 2025-06-15 at Brussels, Room JAN 4Q1, by Birgit Sippel (Coordinator), referenced procedure: 2021/0136(COD), committee: Committee on Civil Liberties, Justice and Home Affairs'
),
(
    'Cybersecurity Strategy Meeting',
    'Bart Groothuis',
    '2025-06-20',
    'Strasbourg, Room LOW N1.4',
    'Rapporteur',
    '2022/0163(COD)',
    'ITRE',
    'Committee on Industry, Research and Energy',
    'Cybersecurity Strategy Meeting, on 2025-06-20 at Strasbourg, Room LOW N1.4, by Bart Groothuis (Rapporteur), referenced procedure: 2022/0163(COD), committee: Committee on Industry, Research and Energy'
);

-- =======================
-- Seed for ep_meetings
-- =======================
INSERT INTO ep_meetings (
    title,
    datetime,
    place,
    subtitles,
    embedding_input
)
VALUES
(
    'Plenary Session on EU Enlargement Strategy',
    '2025-06-10 09:00:00',
    'European Parliament, Strasbourg',
    'Live interpretation in EN, FR, DE',
    'Plenary Session on EU Enlargement Strategy 2025-06-10 09:00:00 European Parliament, Strasbourg Live interpretation in EN, FR, DE'
),
(
    'Debate on Artificial Intelligence Act',
    '2025-06-12 14:30:00',
    'European Parliament, Brussels',
    'Subtitles available in 24 EU languages',
    'Debate on Artificial Intelligence Act 2025-06-12 14:30:00 European Parliament, Brussels Subtitles available in 24 EU languages'
),
(
    'Committee Meeting on Climate Law',
    '2025-06-15 10:00:00',
    'European Parliament, Brussels',
    'Live interpretation in EN, FR, DE, ES, IT',
    'Committee Meeting on Climate Law 2025-06-15 10:00:00 European Parliament, Brussels Live interpretation in EN, FR, DE, ES, IT'
),
(
    'Joint Committee Session on Digital Services',
    '2025-06-18 11:00:00',
    'European Parliament, Brussels',
    'Subtitles available in all EU languages',
    'Joint Committee Session on Digital Services 2025-06-18 11:00:00 European Parliament, Brussels Subtitles available in all EU languages'
),
(
    'Special Session on Energy Security',
    '2025-06-20 09:30:00',
    'European Parliament, Strasbourg',
    'Live interpretation in 24 EU languages',
    'Special Session on Energy Security 2025-06-20 09:30:00 European Parliament, Strasbourg Live interpretation in 24 EU languages'
);

-- ==========================================
-- Seed for austrian_parliament_meetings
-- ==========================================
INSERT INTO austrian_parliament_meetings (
    id,
    title,
    title_de,
    meeting_type,
    meeting_date,
    meeting_location,
    meeting_url,
    embedding_input
)
VALUES
(
    'test_1',
    'Committee Hearing on Data Protection Reform',
    'Ausschusssitzung zur Datenschutzreform',
    'Committee Meeting',
    '2025-06-18',
    'Parlament Wien, Sitzungssaal 2',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/A-AU/A-AU_00123/index.shtml',
    'Committee Hearing on Data Protection Reform Committee Meeting 2025-06-18 Parlament Wien, Sitzungssaal 2'
),
(
    'test_2',
    'Budget Debate for 2026 Fiscal Year',
    'Budgetdebatte zum Haushaltsjahr 2026',
    'Plenary Session',
    '2025-06-25',
    'Plenarsaal, Parlament Wien',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/PLEN/PLEN_00456/index.shtml',
    'Budget Debate for 2026 Fiscal Year Plenary Session 2025-06-25 Plenarsaal, Parlament Wien'
),
(
    'test_3',
    'Digital Infrastructure Development Plan',
    'Digitale Infrastrukturentwicklungsplan',
    'Committee Meeting',
    '2025-07-02',
    'Parlament Wien, Sitzungssaal 3',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/A-AU/A-AU_00124/index.shtml',
    'Digital Infrastructure Development Plan Committee Meeting 2025-07-02 Parlament Wien, Sitzungssaal 3'
),
(
    'test_4',
    'Climate Protection Measures Review',
    'Überprüfung der Klimaschutzmaßnahmen',
    'Special Session',
    '2025-07-05',
    'Parlament Wien, Sitzungssaal 1',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/A-AU/A-AU_00125/index.shtml',
    'Climate Protection Measures Review Special Session 2025-07-05 Parlament Wien, Sitzungssaal 1'
),
(
    'test_5',
    'Education Reform Discussion',
    'Diskussion zur Bildungsreform',
    'Committee Meeting',
    '2025-07-10',
    'Parlament Wien, Sitzungssaal 4',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/A-AU/A-AU_00126/index.shtml',
    'Education Reform Discussion - Diskussion zur Bildungsreform'
);

-- ==========================================
-- Seed for belgian_parliament_meetings
-- ==========================================
INSERT INTO belgian_parliament_meetings (
    id,
    title,
    title_en,
    description,
    description_en,
    meeting_date,
    location,
    meeting_url,
    embedding_input
)
VALUES
(
    'bpm_001',
    'Commissievergadering over Digitale Transformatie',
    'Committee Meeting on Digital Transformation',
    'Bespreking van het nationale plan voor digitale transformatie',
    'Discussion of the national digital transformation plan',
    '2025-07-15',
    'Kamer van Volksvertegenwoordigers, Brussel',
    'https://www.dekamer.be/meeting/001',
    'Committee Meeting on Digital Transformation - Discussion of the national digital transformation plan'
),
(
    'bpm_002',
    'Plenaire Vergadering: Klimaatbeleid',
    'Plenary Session: Climate Policy',
    'Debat over nieuwe klimaatwetgeving',
    'Debate on new climate legislation',
    '2025-07-18',
    'Belgisch Parlement, Brussel',
    'https://www.dekamer.be/meeting/002',
    'Plenary Session: Climate Policy - Debate on new climate legislation'
),
(
    'bpm_003',
    'Hoorzitting Cyberveiligheid',
    'Hearing on Cybersecurity',
    'Expertpanel over nationale cyberveiligheid',
    'Expert panel on national cybersecurity',
    '2025-07-20',
    'Senaat, Brussel',
    'https://www.dekamer.be/meeting/003',
    'Hearing on Cybersecurity - Expert panel on national cybersecurity'
),
(
    'bpm_004',
    'Begrotingscommissie',
    'Budget Committee',
    'Analyse van de federale begroting 2026',
    'Analysis of the 2026 federal budget',
    '2025-07-22',
    'Kamer van Volksvertegenwoordigers, Brussel',
    'https://www.dekamer.be/meeting/004',
    'Budget Committee - Analysis of the 2026 federal budget'
),
(
    'bpm_005',
    'Commissie Sociale Zaken',
    'Social Affairs Committee',
    'Hervorming van het sociale zekerheidsstelsel',
    'Reform of the social security system',
    '2025-07-25',
    'Belgisch Parlement, Brussel',
    'https://www.dekamer.be/meeting/005',
    'Social Affairs Committee - Reform of the social security system'
);

-- ==========================================
-- Seed for bt_documents
-- ==========================================
INSERT INTO bt_documents (
    id,
    datum,
    titel,
    drucksachetyp,
    text,
    title_english
)
VALUES
(
    'BT_001_2025',
    '2025-06-01',
    'Gesetzentwurf zur Digitalen Verwaltung',
    'Gesetzentwurf',
    'Der Bundestag wolle beschließen... [Vollständiger Text]',
    'Draft Law on Digital Administration'
),
(
    'BT_002_2025',
    '2025-06-05',
    'Antrag zur Förderung erneuerbarer Energien',
    'Antrag',
    'Die Bundesregierung wird aufgefordert... [Vollständiger Text]',
    'Motion on Renewable Energy Promotion'
),
(
    'BT_003_2025',
    '2025-06-10',
    'Kleine Anfrage zur Cybersicherheit',
    'Kleine Anfrage',
    'Die Bundesregierung wird gefragt... [Vollständiger Text]',
    'Minor Interpellation on Cybersecurity'
),
(
    'BT_004_2025',
    '2025-06-15',
    'Beschlussempfehlung zum Klimaschutz',
    'Beschlussempfehlung',
    'Der Bundestag möge folgendes beschließen... [Vollständiger Text]',
    'Resolution Recommendation on Climate Protection'
),
(
    'BT_005_2025',
    '2025-06-20',
    'Gesetzentwurf zur KI-Regulierung',
    'Gesetzentwurf',
    'Der Bundestag wolle beschließen... [Vollständiger Text]',
    'Draft Law on AI Regulation'
);

-- ==========================================
-- Seed for bt_plenarprotokolle
-- ==========================================
INSERT INTO bt_plenarprotokolle (
    id,
    datum,
    titel,
    sitzungsbemerkung,
    text,
    title_english
)
VALUES
(
    'PP_001_2025',
    '2025-07-01',
    'Plenarprotokoll der 123. Sitzung',
    'Beginn: 9:00 Uhr, Ende: 18:30 Uhr',
    'Präsident: Die Sitzung ist eröffnet... [Vollständiger Text]',
    'Plenary Protocol of the 123rd Session'
),
(
    'PP_002_2025',
    '2025-07-05',
    'Plenarprotokoll der 124. Sitzung',
    'Beginn: 10:00 Uhr, Ende: 17:45 Uhr',
    'Präsident: Guten Morgen, liebe Kolleginnen und Kollegen... [Vollständiger Text]',
    'Plenary Protocol of the 124th Session'
),
(
    'PP_003_2025',
    '2025-07-10',
    'Plenarprotokoll der 125. Sitzung',
    'Beginn: 9:30 Uhr, Ende: 19:00 Uhr',
    'Präsident: Die Sitzung ist eröffnet... [Vollständiger Text]',
    'Plenary Protocol of the 125th Session'
),
(
    'PP_004_2025',
    '2025-07-15',
    'Plenarprotokoll der 126. Sitzung',
    'Beginn: 11:00 Uhr, Ende: 18:15 Uhr',
    'Präsident: Ich eröffne die Sitzung... [Vollständiger Text]',
    'Plenary Protocol of the 126th Session'
),
(
    'PP_005_2025',
    '2025-07-20',
    'Plenarprotokoll der 127. Sitzung',
    'Beginn: 10:30 Uhr, Ende: 20:00 Uhr',
    'Präsident: Die Sitzung ist eröffnet... [Vollständiger Text]',
    'Plenary Protocol of the 127th Session'
);

-- ====================
-- Seed for ipex_events
-- ====================
INSERT INTO ipex_events (
    id,
    title,
    start_date,
    end_date,
    meeting_location,
    tags,
    embedding_input
)
VALUES
(
    'ipex-2025-001',
    'Interparliamentary Conference on Foreign Affairs',
    '2025-06-05',
    '2025-06-06',
    'Vienna, Austria',
    ARRAY['foreign policy', 'EU cooperation', 'diplomacy'],
    'Interparliamentary Conference on Foreign Affairs 2025-06-05 2025-06-06 Vienna, Austria foreign policy, EU cooperation, diplomacy'
),
(
    'ipex-2025-002',
    'Joint Parliamentary Scrutiny Meeting on Europol',
    '2025-06-15',
    '2025-06-15',
    'The Hague, Netherlands',
    ARRAY['security', 'Europol', 'law enforcement'],
    'Joint Parliamentary Scrutiny Meeting on Europol 2025-06-15 2025-06-15 The Hague, Netherlands security, Europol, law enforcement'
),
(
    'ipex-2025-003',
    'Conference on EU Digital Policy',
    '2025-06-20',
    '2025-06-21',
    'Stockholm, Sweden',
    ARRAY['digital policy', 'innovation', 'technology'],
    'Conference on EU Digital Policy 2025-06-20 2025-06-21 Stockholm, Sweden digital policy, innovation, technology'
),
(
    'ipex-2025-004',
    'Climate Action Parliamentary Forum',
    '2025-06-25',
    '2025-06-26',
    'Copenhagen, Denmark',
    ARRAY['climate change', 'environmental policy', 'sustainability'],
    'Climate Action Parliamentary Forum 2025-06-25 2025-06-26 Copenhagen, Denmark climate change, environmental policy, sustainability'
),
(
    'ipex-2025-005',
    'EU-Africa Parliamentary Summit',
    '2025-07-01',
    '2025-07-02',
    'Brussels, Belgium',
    ARRAY['international cooperation', 'development', 'trade'],
    'EU-Africa Parliamentary Summit 2025-07-01 2025-07-02 Brussels, Belgium international cooperation, development, trade'
);


INSERT INTO profiles (
  id,
  name,
  surname,
  company_name,
  company_description,
  topic_list,
  subscribed_newsletter,
  embedding
)
VALUES (
  'f82dc603-3148-4ba3-af07-89a34ef3162a',
  'Alice',
  'Smith',
  'BrightWave Technologies',
  'We develop AI-driven analytics for retail optimization.',
  -- topic_list as a PostgreSQL TEXT[]:
  ARRAY[
    'Machine Learning',
    'Retail Analytics',
    'Data Visualization',
    'Predictive Modeling'
  ],
  FALSE,
  '[-0.0236724,-0.029242376,-0.0019247214,-0.0035783083,0.009098074,0.010363369,-0.010095582,0.0016192765,0.0023715915,-0.028439015,-0.011782642,0.01922713,-0.014607799,0.0018226275,0.002210919,0.015022869,0.014888976,-0.0046695415,0.005536503,-0.012505668,-0.03609773,0.025265735,-0.010088888,-0.021530101,-0.0025305902,-0.0099951625,0.016549258,-0.025734363,0.014634578,-0.015518276,0.00087281934,-0.013442924,0.007417709,-0.0002244811,0.00335571,-0.01945475,0.016843824,0.011896452,0.025305903,-0.013155052,0.009586786,-0.0131148845,-0.0012770108,-0.009252052,-0.016308248,0.012445416,0.018785281,-0.005034402,9.1633476e-05,0.0041607455,-0.0031247435,0.0154245505,-0.0113474885,-0.00040984014,0.018704945,0.021168588,0.0022326768,0.028171226,-2.0450165e-05,-0.015558444,0.0073708463,-0.0070093335,-0.028787138,-0.02576114,0.005034402,-0.00972068,-0.021730943,0.030902658,0.01606724,-0.0046963203,0.012980991,0.004418491,-0.0013188527,0.012278049,0.005593408,-0.000548964,-0.011963399,-0.010042025,-0.0031682588,0.01500948,0.0018025434,0.00783278,-0.015464718,0.017848026,0.016830433,-0.0063867276,-0.04630043,0.017607016,-0.022587862,-0.015732506,0.0051749903,-0.00565366,0.008703088,-0.00071800477,-0.023377834,0.017914973,0.010885555,0.016375195,0.004077062,-0.027582094,0.006611,-0.0018008698,-0.03783835,-0.011963399,-0.009486366,0.019548476,-0.030849101,0.006955776,0.024636434,0.012746677,-0.020807076,0.015384382,-0.0011414435,-0.0061658034,-0.00887715,-0.003218469,-0.0030845753,0.005395915,-0.006410159,-0.0154245505,0.014741693,0.023123436,0.0044419225,-0.032080922,0.017848026,0.018423768,-0.03320563,-0.037168883,0.022306684,-0.011146648,-0.005419346,-0.0008962507,0.011528244,-0.025091672,-0.02007066,0.0103901485,0.0030996383,0.019628812,-0.009888047,0.008261239,-0.005235242,0.02451593,0.0077122753,-0.007846169,-0.010028635,0.02005727,-0.011916536,0.034089327,0.015143373,0.0035783083,-0.008241155,-0.009740764,0.000945624,0.020231333,0.0026510945,-0.0028937769,0.0036486024,0.015384382,-0.03379476,-0.0030912699,0.006436938,0.0051917266,-0.005429388,0.00876334,0.038266808,0.011119869,0.007297205,-0.021463154,-0.0026611367,0.008977571,-0.012177628,0.022279905,-0.031357896,0.0063934224,0.002866998,0.003909695,-0.00877673,-7.609972e-05,-0.015317435,-0.022641419,0.015263878,-0.009124854,0.007926505,-0.0053490517,0.027354475,-0.0065206215,0.011916536,-0.0121374605,0.023029711,-0.042551406,0.0036619918,0.023980355,-0.0011380961,-0.0088102035,-0.6478311,-0.020780297,-0.0069223023,-0.005201769,0.004592553,-0.00018086105,0.027019741,0.0009380925,0.030741986,0.009104769,0.0036988126,-0.0011891432,-0.01942797,-0.00877673,0.0044787433,-0.007498045,0.014982701,-0.028867474,0.028224785,0.01966898,-0.046220094,0.037008207,-0.024288312,0.008401828,0.02134265,0.005456167,0.0014226201,0.007317289,-0.0209008,0.008950791,-0.016401974,0.054253712,0.02411425,0.008107262,0.04065012,0.0035180561,-0.011769253,0.0070093335,0.01215085,0.01456763,-0.020258112,-0.029965403,0.008194292,0.009185106,-0.0011213594,0.03740989,0.0096403435,-0.0047264462,-0.021704163,-0.015585222,0.01056421,-0.015036259,-0.0020904148,0.0042076083,0.020110829,0.019521696,0.00065691577,-0.0046594995,-0.003554877,-0.010919028,-0.013978499,-0.0128872655,-0.02534607,-0.026296716,-0.010430316,0.017406177,0.021503322,-0.012940823,-0.0049440237,-0.0017113284,0.022453967,0.0030008918,-0.009814406,-0.008328186,0.0029858288,0.020445563,0.033982214,0.0075382134,-0.008569195,0.0034845825,0.01320861,-0.019186962,-0.017071443,-0.016442142,-0.003742328,0.0045323004,-0.0037557173,-0.034089327,0.013161747,0.0022661502,0.022654807,0.029563721,-0.0044051018,-0.04560418,0.0024368647,0.005292147,0.00031046593,0.015089816,-0.0063499073,-0.012934128,-0.031250782,0.0048670345,0.014058835,0.016642982,0.0059515736,-0.0035816554,-0.003295458,-0.019146794,0.022146013,-0.016576035,-0.004341502,-0.011575107,-0.033660866,0.010644547,0.012311523,-0.035696052,0.0069022183,-0.016187744,-0.007417709,-0.010363369,0.022507524,-0.0029925234,0.018704945,-0.013001075,-0.007611855,0.005921447,-0.01130732,0.004036894,-0.0018075645,0.004729794,0.016736709,-0.03044742,0.00080001465,0.007939895,0.00681184,-0.008207682,0.014768471,0.0016996127,-0.0010753334,-0.011581802,-0.043970678,-0.0018728377,0.022641419,0.008582584,-0.04439914,-0.020766906,-0.005412651,0.02175772,-0.0196422,-0.009774238,-0.012980991,0.0010226129,-0.013288946,0.030822322,0.018410379,0.000107637956,-0.017071443,-0.014447127,0.0012477216,-0.028278342,-0.008187598,0.017700743,-0.010108972,0.011782642,0.018343432,-0.02364562,0.0058712373,0.02219957,-0.024730159,-0.012599394,0.03258972,-0.013871384,-0.0046226787,0.031813134,-0.021074863,0.031304337,-0.031090109,-0.010437011,0.019682368,-0.022119233,-0.0031046593,0.014835418,-0.008529026,-0.021115031,0.013449619,0.012090598,0.015357603,0.016375195,-0.0196422,-0.0050310544,-0.024917612,0.04501505,-0.0051950742,0.013831216,-0.019709148,0.0009816079,-0.03508014,0.010664631,-0.00877673,0.013282252,0.012733287,0.04097146,0.027582094,0.02051251,0.0023347707,-0.024154417,-0.004056978,-0.023712568,0.009278831,0.030956214,0.018852228,-0.0029121873,-0.0045189112,-0.026671618,0.009600176,0.008515637,-0.00565366,0.016830433,-0.009901436,-0.006440285,0.007016028,-0.009004349,0.015960125,-0.006771672,-0.021409597,0.019548476,-0.015183542,0.044747263,0.010570905,-0.027367866,-0.0019732579,0.030822322,0.03599062,0.003395878,0.0045423424,-0.013690627,0.0392844,-0.020592846,0.026765343,-0.004053631,-0.010095582,0.0295905,0.024382036,-0.01650909,0.017513292,0.0057942485,0.026269937,0.00814743,-0.011796032,-0.013596902,-0.02999218,-0.0007326494,-0.020110829,0.008703088,0.01902629,-0.021074863,0.019588644,-0.009258747,0.021503322,0.026444,0.0011623644,0.038561374,5.5911067e-05,0.015571834,-0.015317435,-0.017781079,0.0038728742,0.012552531,-0.0002055477,-0.010979281,0.00033243286,-0.024837274,0.027956998,-0.009379251,0.031090109,0.009057906,0.026885848,0.01582623,-0.0055398503,0.04158737,-0.03042064,-0.030715207,0.013349199,0.027140245,-0.018879008,-0.010108972,-0.018450547,0.011200205,-0.037758015,-0.001682876,0.016335027,0.026671618,-0.0036285182,-0.0046762363,-0.0066712517,-0.01668315,0.04225684,-0.00038640873,0.013844605,-0.019588644,0.015357603,0.02661806,-0.0071900897,-0.0070428066,0.021115031,-0.010664631,-0.011608581,0.0021640563,-0.011387656,-0.0126998145,-0.0065808734,-0.014647967,0.014406959,0.000109625435,-0.007250342,0.009539924,-0.005740691,-0.0033791414,0.014085613,0.030286746,-0.0077256644,-0.008341575,0.001876185,0.030982994,0.083228305,0.010503958,-0.007752443,0.018303264,-0.02032506,-0.004930634,-0.047692925,-0.0070896694,0.0056770914,0.0024787064,-0.032830726,-0.005613492,0.013831216,-0.0001464462,0.0048201717,0.007123143,-0.011709001,-0.025935203,0.011842894,0.021597048,-0.0018209538,-0.00022741003,-0.015036259,-0.0034126148,0.020994527,-0.0042377342,0.026189601,0.03226837,-0.020164385,-0.018557662,-0.009265441,0.029911844,-0.00750474,0.0077658324,-0.011488076,0.032027364,-0.0067951037,0.0040134625,-0.0071767005,-0.011782642,0.012030345,0.024890833,-0.013175136,-0.014273064,0.0043448494,-0.007879642,0.02071335,0.02408747,-0.028599687,-0.014085613,0.012117377,0.010242865,-0.048201717,-0.0064637167,-0.010403538,0.038936276,-0.0015623717,-1.763892e-05,0.022788702,-0.045925528,-0.011186816,-0.0034310252,-0.019079847,-0.005415999,0.009426114,-0.01416595,-0.019749315,-0.011441214,-0.021516712,0.009633649,-0.014527462,-0.02790344,-0.030902658,-0.0177543,0.027501758,0.004525606,0.010731577,0.008716478,-0.0055130715,0.023993745,0.0046561523,0.0035013193,-0.01089225,-0.02809089,-0.005037749,-0.016000293,-0.021115031,-0.0044151437,-0.0074310983,-0.012920738,-0.0019548475,-0.0026979574,0.042578187,0.008836982,0.017888194,0.01415256,0.015504886,0.009727375,-0.0034209832,-0.008294713,0.016388584,-0.021597048,-0.023190383,-0.016388584,0.017593628,0.00176907,-0.003228511,-0.010490568,0.021864835,0.0041507035,-0.011548328,0.02005727,0.014955922,-0.0038929584,-0.00037615752,-0.0020067312,0.02091419,-0.012063819,-0.003106333,-0.0044653537,0.0255603,-0.024569487,0.021021305,-0.01499609,-0.013188526,0.008796814,0.004528953,-0.0026661577,-0.014406959,-0.0030377125,0.003218469,-0.0019146794,-0.005047791,-0.028465793,-0.029831508,-0.010550821,-0.017473124,0.003889611,-0.03189347,-0.02747498,-0.015732506,0.015411161,0.002831851,-0.007913115,-0.001958195,-0.028010555,0.011682223,-0.015906567,-0.014527462,0.02639044,-0.0140722245,0.0044753957,-0.00084478536,-0.027983775,-0.0056302287,-0.0380258,-0.014286454,0.0017590281,0.029322712,0.028921032,0.036258403,-0.0039532105,0.014755081,0.026122654,-0.005606797,-0.018584441,-0.006788409,0.0075181294,-0.0078060008,0.0019732579,-0.0072034793,-0.0028151143,0.016254691,-0.0030829017,0.0017774384,0.019588644,0.0054996824,-0.021918394,-0.020177776,-0.0012184323,-0.031947028,0.0007991778,0.004626026,0.0146747455,-0.01902629,0.00803362,0.05623534,0.03066165,-0.006125635,0.00072511786,0.021663995,-0.008294713,0.019561864,0.00781939,-0.010524042,-0.017406177,-0.021275703,-0.032562938,-0.020753518,0.044292025,0.017660575,0.015103205,0.013657154,0.015036259,-0.023176994,0.02787666,-0.0140722245,-0.007464572,-0.009165022,-0.012900654,-0.0005698849,-0.025172008,-0.024288312,-0.029697616,0.001133912,0.0044921325,-0.013128274,0.026122654,-0.01709822,-0.024837274,0.013764269,-0.0075716865,0.036070954,0.019267298,0.06721462,0.035347927,0.0105976835,-0.012920738,-0.006641126,-0.0133224195,-0.020740129,0.0017506597,0.015036259,-0.040221658,-0.035160474,0.006821882,-0.004083757,-0.010349981,-0.040516224,0.03446423,0.0013464681,-0.0069892495,-0.02620299,-0.0044419225,-0.019160183,0.041105356,-0.03976642,0.010222781,0.008281323,-0.015786063,-0.0030594703,-0.00866292,-0.0013657154,0.013583512,0.00428125,0.013831216,0.023792904,0.031813134,-0.0032904367,-0.0001583711,0.0016033766,-0.007136532,-0.0072235633,0.020539287,0.023712568,0.012318217,0.013884773,-0.01320861,0.0056804386,0.028867474,-0.016214523,-0.02260125,-0.0011757538,-0.01629486,0.022681586,-0.014192728,-0.026952794,-0.00949306,0.002038531,-0.01393833,0.03133112,0.0015071406,-0.02158366,-0.011247068,-3.922666e-05,-0.009211884,0.0069223023,4.6235156e-05,0.0035950448,-0.03869527,-0.028064111,0.027367866,-0.014781861,0.0066578626,0.017914973,0.004528953,-0.00940603,0.021235535,0.0013807784,-0.011514856,0.007893031,-0.0039866837,-0.042765636,0.004800088,-0.020525899,-0.0103901485,0.016589426,-0.008622752,-0.022547694,-0.009600176,-0.020874022,0.010256255,-0.0006556605,-0.0041808295,-0.024689991,0.033125293,-0.0033372997,-0.005415999,-0.01774091,0.0043247654,0.00486034,-0.00854911,0.015143373,-0.030715207,0.033741202,0.008816898,0.014380179,-0.021048084,-0.01521032,-0.040355552,-0.027956998,0.035214033,-0.0054996824,0.0019364371,0.006955776,0.009754154,-0.0044954796,0.005774164,0.0060017835,-0.025265735,0.011528244,-0.0002366152,0.0056302287,0.014085613,-0.00078662526,-0.02576114,-0.029429827,-0.020753518,-0.026685007,-0.01479525,-0.015143373,0.039177287,0.017848026,-0.043836787,-0.021717552,-0.023953576,-0.019401193,-0.00844869,0.020338448,0.009566702,0.010376759,0.020177776,-0.002150667,0.026725175,-0.008823592,0.013315725,-0.009138242,0.019990325,-0.008408522,-0.019521696,0.0049908864,-0.0024803802,-0.036686864,-0.004053631,0.0018393642,-0.00063432124,-0.0021992035,0.01587979,-0.031009773,-0.00014560936,0.02238702,0.010631157,0.007826084,0.018959343,0.019481529,-0.047103792,0.013871384,-0.0068553556,-0.015116595,-0.021851446,-0.0020619624,0.008488858,-0.00729051,0.009586786,-0.041533813,-0.0049942336,-0.015103205,0.00012228257,0.010216086,-0.0017138389,0.017888194,0.013088105,0.013483092,-0.011688917,-0.014299843,0.007826084,-0.013911552,-0.013657154,-0.0119700935,-0.03510692,-0.008160819,-0.021489933,0.010289728,0.0043247654,-0.005958268,-0.026685007,0.0045992476,-0.03165246,-0.00096989225,0.015799452,-0.009740764,-0.0031582168,0.0094127245,-0.007464572,0.006607652,-0.014942533,0.02136943,-0.023846462,-0.020967748,0.025720973,-0.01225127,-0.008227766,0.041078575,0.0026427263,-0.0026443999,0.03703499,0.2066247,-0.00018776495,-0.036419075,0.01692416,0.013442924,0.009539924,0.011079701,0.017888194,0.018879008,-0.024047302,0.007524824,0.01587979,-0.017673964,0.0017707438,0.026323494,-0.016027072,-0.034571346,-0.022641419,-0.0017874804,0.0075114346,0.01016253,-0.013965109,-0.004184177,-0.0027381254,0.03403577,-0.009285525,-0.022922596,0.011662139,0.008227766,0.0190129,-0.019481529,0.0012577636,0.012713203,0.019481529,-0.0023330972,-0.0003119304,0.011066311,-0.0098277945,0.022159401,0.021396207,0.008167514,0.0025791267,-0.019173572,-0.020432172,0.009024433,0.02217279,-0.0038594848,0.0047164042,-0.006289655,0.018102424,-0.011749169,0.001439357,0.011682223,0.024850665,-0.012010261,0.009566702,-0.010269644,0.03042064,-0.0073641515,-0.006821882,-0.0048201717,0.0071900897,-0.0048168246,0.014835418,-0.0283319,-0.019374413,-0.0078729475,0.024408815,0.019387802,-0.0009548292,0.019575253,0.0027682516,-0.004753225,0.0065139267,-0.043194097,-0.02999218,0.00972068,0.013550038,0.0033624046,0.033982214,-0.01046379,0.0058076377,-0.012512363,-0.02537285,-0.0135098705,-0.029804729,0.02639044,-0.0037490225,0.0020920886,-0.0004774146,-0.008783424,-0.011139953,-0.01130732,-0.007973367,0.018129202,0.0041473564,-0.010678019,0.0077390536,-0.0025021378,-6.0409056e-05,-0.018048866,0.037168883,0.040007427,0.0041908715,-0.022065677,0.0061959294,-0.026122654,0.029858287,0.0084553845,-0.0047264462,-0.028037334,-0.035829946,0.019950155,-0.011675527,-0.020967748,0.011702307,0.0071967845,-0.00972068,0.02051251,-0.019682368,0.0119700935,-0.017486513,0.014781861,0.015973514,-0.0042779027,-0.014915754,-0.0041674403,-0.008314797,-0.032670055,-0.013181832,0.025185399,-0.0014686461,-0.004468701,-0.01648231,0.008716478,0.008529026,0.0096202595,-0.0061825397,-0.016763486,-0.0013514892,-0.008040315,0.009372557,-0.017981919,-0.0011104806,0.020110829,-0.011401045,0.028921032,0.009171716,-0.011160037,-0.019521696,-0.0012954212,0.00876334,-0.008897234,-0.010704799,0.023351055,-0.0006564974,-0.019387802,0.011581802,0.010885555,0.0018092381,-0.033714425,-0.002028489,0.029108483,0.0010142445,-0.00095650286,0.012947517,-0.17138389,0.019120015,0.011360877,-0.023110047,0.02535946,0.019548476,0.0050511383,0.0070294174,-0.018691555,0.01479525,-0.0062093185,0.019909987,-0.03175958,-0.004077062,0.0049038553,0.0034946247,-0.010129056,0.022159401,0.008696393,-0.0051917266,0.022025507,-0.009546618,0.004719752,-0.008154124,0.017673964,-0.00803362,-0.00287704,0.018370211,0.025747752,-0.027207192,-0.013965109,-0.022681586,0.017647184,-0.0015824557,0.016950937,0.0034226568,-0.008790119,-0.012010261,-0.017432956,0.02617621,0.040944684,0.030179633,-0.0030895963,0.016013682,0.0177543,0.02663145,0.016027072,-0.019682368,-0.0031615642,-0.032188036,0.027528537,-0.036901094,0.025386238,-0.0085625,0.013436229,0.01500948,-0.007082975,0.0031649114,0.008984265,-0.047639366,-0.013141663,-0.0006690499,0.002003384,-0.030688427,-0.009553313,0.0032552897,-0.013724101,0.006440285,-0.021958562,0.014500684,-0.0010418601,0.008174208,-0.0008489695,0.009472976,0.008522332,0.02131587,-0.016776877,0.019414581,0.039364737,-0.0041607455,-0.018410379,0.0009548292,-0.021623828,0.0209008,-0.0061490666,0.002572432,0.0162413,0.012043735,-0.0041306196,-0.0109926695,0.0073239836,-0.023096656,0.0053423573,-0.018048866,0.011802726,0.012967601,7.055568e-05,0.0036050868,0.0026092527,0.010885555,0.010704799,0.0077457484,-0.0021941825,0.018142592,0.006272918,0.026912626,0.0056904806,0.027930219,0.027113467,-0.017928362,-0.0050210124,0.0034812354,0.018972732,-0.0021674037,-0.005369136,0.0031816482,-0.005476251,-0.009553313,0.0190129,0.0005464535,0.042497847,0.0047766566,-0.013650459,0.022976153,-0.019307466,-0.035749607,-0.061537527,-0.037784792,-0.00491055,0.024997948,-0.010637851,0.016281469,-0.01606724,0.021730943,-0.0270733,0.040060986,-0.0088302875,-0.04078401,-0.029670836,0.0017673963,0.012552531,-0.0012008589,-0.0027448202,0.013764269,-0.026778733,0.008000147,-0.017794468,-0.031465013,0.0053758305,0.014540852,0.0011406067,0.0015021196,-0.027180415,0.019334245,0.028626466,0.005104696,0.0035716135,-0.035160474,0.02260125,-0.014366791,-0.022842258,-0.006821882,-0.013456313,-0.0115550235,-0.0063632964,-0.023632232,0.02136943,-0.005067875,0.019709148,-0.015397771,-0.02724736,-0.0064904955,-0.01521032,0.023404613,0.002796704,-0.00028870822,0.0038594848,-0.0046327207,-0.008836982,-0.0011347488,0.00086361414,-0.008408522,-0.00075524393,-0.017165167,-0.0037055071,0.0058411113,-0.023779515,0.022025507,-0.033741202,0.015304046,0.0023414656,0.011421129,-0.030822322,-0.0055398503,-0.012358385,-0.0041105356,0.012452111,0.018463936,0.009472976,0.025640637,-0.04099824,-0.013898162,-0.007116448,-0.013610291,0.016321639,0.00613233,-0.0321077,-0.022694977,0.020659793,0.020606235,-0.005235242,-0.0013447945,-0.020017102,-0.0022577818,0.010544126,-0.031572126,0.009854574,0.030313525,0.018745113,-0.028813917,0.005087959,-0.022909205,-0.0177543,-0.012512363,0.0115349395,0.0045523844,-0.0040201573,-0.0043649334,-0.08617396,0.034303557,-0.000255444,-0.0030996383,0.015812842,-0.033982214,0.0033423207,-0.0055298083,0.0062193605,0.0019766053,-0.0043281126,0.01566556,-0.01816937,-0.03234871,-0.023833072,-0.0065708314,0.02811767,-0.019401193,0.019628812,-0.0076587177,0.020191165,0.008609363,0.032696832,0.003106333,-0.0037356333,-0.015437939,-0.01646892,0.0103700645,-0.0041373144,-0.00025125983,0.008334881,-0.004749878,-0.023418002,0.03657975,-0.010517348,-0.020592846,-0.012733287,0.01988321,0.030045738,0.008227766,-0.008924013,-0.022788702,0.0048737293,-0.011247068,-0.015946735,-0.010765051,-0.0011163384,-0.017151779,0.017714132,-0.0011422803,0.016910769,0.027528537,-0.019347634,-0.033098515,-0.019923378,-0.017647184,-0.009305609,8.065001e-05,0.017486513,0.03020641,0.023176994,0.015063037,0.015437939,0.0024720118,-0.0018795324,0.013991888,-0.0030728595,0.019749315,-0.0033255839,-0.021704163,-0.010309813,-0.00015439613,0.0119700935,0.011702307,0.0190129,-0.021088252,0.005399262,-0.008602668,-0.013590207,0.032723613,0.008113956,0.009138242,0.0006949918,0.011588497,0.031304337,0.015478107,-0.0090177385,-0.010885555,-0.00053013524,0.0001368226,-0.006594263,-0.003213448,-0.014219508,0.015397771,-0.027796324,0.01319522,-0.010885555,0.008964181,0.0034410672,0.05682447,0.0118362,0.017004495,0.014326622,-0.0039866837,-0.029456606,0.018477326,-0.0022996238,-0.012726593,-0.00089039287,0.024636434,0.018008698,0.008174208,0.00012552532,-0.012070514,-0.0133224195,0.020137608,-0.002949008,-0.020110829,-0.011755864,0.016549258,0.00950645,-0.0023330972,0.0092453575,-0.007959979,0.004528953,0.023551896,-0.012666341,-0.016830433,0.009948299,-0.031973805,-0.010236171,-0.016174356,-0.012438721,0.019374413,-0.01689738,-0.007417709,-0.012545836,0.002018447,-0.007899726,0.08006841,0.019976934,0.0012058798,-0.001016755,-0.044640146,0.024689991,0.024663214,0.02280209,-0.030849101,-0.009586786,0.0034377198,-0.01500948,-0.025948592,-0.016335027,0.0056201867,0.0038460954,-0.0053222734,0.015504886,0.002882061,-0.0008912297,0.018691555,0.005255326,0.022895817,0.012940823,-0.026979573,-0.005921447,0.0026360315,0.017874803,-0.00066612096,-0.039418295,0.021677384,-0.003081228,-0.026484167,0.00287704,-0.010075498,-0.020258112,-0.0075516026,-0.0183836,-0.0049808444,0.01626808,-0.014607799,0.021878224,-0.0119299255,-0.009633649,0.0056603546,-0.0019648895,-0.0043850173,-0.013898162,0.0014259676]'
  );
-- ==========================================
-- Seed for lawtracker_procedures
-- ==========================================
INSERT INTO eu_law_procedures (
    id,
    title,
    status,
    active_status,
    started_date,
    topic_codes,
    topic_labels,
    embedding_input
)
VALUES
(
    'PROC_2025_001',
    'Regulation on Artificial Intelligence Governance',
    'In Progress',
    'Committee Stage',
    '2025-01-15',
    ARRAY['TECH', 'AI', 'REG'],
    ARRAY['Technology', 'Artificial Intelligence', 'Regulation'],
    'Regulation on Artificial Intelligence Governance, status: In Progress, active: Committee Stage, started: 2025-01-15, topics: Technology, AI, Regulation'
),
(
    'PROC_2025_002',
    'Directive on Renewable Energy Sources',
    'Under Review',
    'First Reading',
    '2025-02-01',
    ARRAY['ENV', 'ENER', 'CLIM'],
    ARRAY['Environment', 'Energy', 'Climate'],
    'Directive on Renewable Energy Sources, status: Under Review, active: First Reading, started: 2025-02-01, topics: Environment, Energy, Climate'
),
(
    'PROC_2025_003',
    'Regulation on Digital Markets',
    'Adopted',
    'Completed',
    '2025-03-10',
    ARRAY['DIG', 'COMP', 'MARK'],
    ARRAY['Digital', 'Competition', 'Market'],
    'Regulation on Digital Markets, status: Adopted, active: Completed, started: 2025-03-10, topics: Digital, Competition, Market'
),
(
    'PROC_2025_004',
    'Directive on Cybersecurity Standards',
    'In Progress',
    'Second Reading',
    '2025-04-01',
    ARRAY['SEC', 'TECH', 'DIG'],
    ARRAY['Security', 'Technology', 'Digital'],
    'Directive on Cybersecurity Standards, status: In Progress, active: Second Reading, started: 2025-04-01, topics: Security, Technology, Digital'
),
(
    'PROC_2025_005',
    'Regulation on Data Privacy',
    'Under Review',
    'Committee Stage',
    '2025-05-15',
    ARRAY['DATA', 'PRIV', 'TECH'],
    ARRAY['Data', 'Privacy', 'Technology'],
    'Regulation on Data Privacy, status: Under Review, active: Committee Stage, started: 2025-05-15, topics: Data, Privacy, Technology'
);

-- ==========================================
-- Seed for mec_prep_bodies_meetings
-- ==========================================
INSERT INTO mec_prep_bodies_meeting (
    id,
    url,
    title,
    meeting_timestamp,
    meeting_location,
    embedding_input
)
VALUES
(
    'MEC_PREP_001',
    'https://www.consilium.europa.eu/meetings/prep001',
    'Coreper I Meeting on Digital Single Market',
    '2025-08-01 10:00:00',
    'Council Building, Brussels',
    'Coreper I Meeting on Digital Single Market, 2025-08-01 10:00:00, Council Building, Brussels'
),
(
    'MEC_PREP_002',
    'https://www.consilium.europa.eu/meetings/prep002',
    'Working Party on Competitiveness',
    '2025-08-05 09:30:00',
    'Justus Lipsius Building, Brussels',
    'Working Party on Competitiveness, 2025-08-05 09:30:00, Justus Lipsius Building, Brussels'
),
(
    'MEC_PREP_003',
    'https://www.consilium.europa.eu/meetings/prep003',
    'Special Committee on Agriculture',
    '2025-08-10 11:00:00',
    'Europa Building, Brussels',
    'Special Committee on Agriculture, 2025-08-10 11:00:00, Europa Building, Brussels'
),
(
    'MEC_PREP_004',
    'https://www.consilium.europa.eu/meetings/prep004',
    'Working Party on Energy',
    '2025-08-15 14:00:00',
    'Council Building, Brussels',
    'Working Party on Energy, 2025-08-15 14:00:00, Council Building, Brussels'
),
(
    'MEC_PREP_005',
    'https://www.consilium.europa.eu/meetings/prep005',
    'Political and Security Committee',
    '2025-08-20 10:30:00',
    'Justus Lipsius Building, Brussels',
    'Political and Security Committee, 2025-08-20 10:30:00, Justus Lipsius Building, Brussels'
);

-- ==========================================
-- Seed for mec_summit_ministerial_meeting
-- ==========================================
INSERT INTO mec_summit_ministerial_meeting (
    id,
    url,
    title,
    meeting_date,
    meeting_end_date,
    category_abbr,
    embedding_input
)
VALUES
(
    'MEC_SUM_001',
    'https://www.consilium.europa.eu/meetings/sum001',
    'European Council Summit on Strategic Autonomy',
    '2025-09-01',
    '2025-09-02',
    'EUCO',
    'European Council Summit on Strategic Autonomy 2025-09-01 2025-09-02'
),
(
    'MEC_SUM_002',
    'https://www.consilium.europa.eu/meetings/sum002',
    'Foreign Affairs Council',
    '2025-09-05',
    '2025-09-05',
    'FAC',
    'Foreign Affairs Council 2025-09-05 2025-09-05'
),
(
    'MEC_SUM_003',
    'https://www.consilium.europa.eu/meetings/sum003',
    'Economic and Financial Affairs Council',
    '2025-09-10',
    '2025-09-10',
    'ECOFIN',
    'Economic and Financial Affairs Council 2025-09-10 2025-09-10'
),
(
    'MEC_SUM_004',
    'https://www.consilium.europa.eu/meetings/sum004',
    'Justice and Home Affairs Council',
    '2025-09-15',
    '2025-09-16',
    'JHA',
    'Justice and Home Affairs Council 2025-09-15 2025-09-16'
),
(
    'MEC_SUM_005',
    'https://www.consilium.europa.eu/meetings/sum005',
    'Agriculture and Fisheries Council',
    '2025-09-20',
    '2025-09-20',
    'AGRIFISH',
    'Agriculture and Fisheries Council 2025-09-20 2025-09-20'
);

-- ==========================================
-- Seed for polish_presidency_meeting
-- ==========================================
INSERT INTO polish_presidency_meeting (
    id,
    title,
    meeting_date,
    meeting_end_date,
    meeting_location,
    meeting_url,
    embedding_input
)
VALUES
(
    'POL_PRES_001',
    'Conference on European Digital Innovation',
    '2025-10-01',
    '2025-10-02',
    'Warsaw Congress Center',
    'https://presidency.poland.eu/meetings/001',
    'Conference on European Digital Innovation, on 2025-10-01 2025-10-02, in Warsaw Congress Center'
),
(
    'POL_PRES_002',
    'EU-Eastern Partnership Summit',
    '2025-10-05',
    '2025-10-06',
    'Palace of Culture and Science, Warsaw',
    'https://presidency.poland.eu/meetings/002',
    'EU-Eastern Partnership Summit, on 2025-10-05 2025-10-06, in Palace of Culture and Science, Warsaw'
),
(
    'POL_PRES_003',
    'Ministerial Conference on Energy Security',
    '2025-10-10',
    '2025-10-10',
    'ICE Krakow Congress Centre',
    'https://presidency.poland.eu/meetings/003',
    'Ministerial Conference on Energy Security, on 2025-10-10 2025-10-10, in ICE Krakow Congress Centre'
),
(
    'POL_PRES_004',
    'EU Cohesion Policy Forum',
    '2025-10-15',
    '2025-10-16',
    'Poznan International Fair',
    'https://presidency.poland.eu/meetings/004',
    'EU Cohesion Policy Forum, on 2025-10-15 2025-10-16, in Poznan International Fair'
),
(
    'POL_PRES_005',
    'Conference on Climate Innovation',
    '2025-10-20',
    '2025-10-21',
    'European Solidarity Centre, Gdansk',
    'https://presidency.poland.eu/meetings/005',
    'Conference on Climate Innovation, on 2025-10-20 2025-10-21, in European Solidarity Centre, Gdansk'
);

-- ==========================================
-- Seed for spanish_commission_meetings
-- ==========================================
INSERT INTO spanish_commission_meetings (
    id,
    date,
    time,
    title,
    title_en,
    location,
    location_en,
    description,
    description_en,
    url,
    embedding_input,
    links
)
VALUES
(
    'ESP_COM_001',
    '2025-11-01',
    '10:00',
    'Comisión de Transformación Digital',
    'Digital Transformation Commission',
    'Congreso de los Diputados, Sala 1',
    'Congress of Deputies, Room 1',
    'Sesión sobre la estrategia digital española',
    'Session on Spanish Digital Strategy',
    'https://www.congreso.es/meeting/001',
    'Digital Transformation Commission - Session on Spanish Digital Strategy Congress of Deputies, Room 1 Session on Spanish Digital Strategy',
    '{"broadcast": "https://www.congreso.es/live/001"}'
),
(
    'ESP_COM_002',
    '2025-11-05',
    '11:30',
    'Comisión de Asuntos Económicos',
    'Economic Affairs Commission',
    'Congreso de los Diputados, Sala 2',
    'Congress of Deputies, Room 2',
    'Debate sobre el presupuesto 2026',
    'Debate on 2026 Budget',
    'https://www.congreso.es/meeting/002',
    'Economic Affairs Commission - Debate on 2026 Budget Congress of Deputies, Room 2 Debate on 2026 Budget',
    '{"broadcast": "https://www.congreso.es/live/002"}'
),
(
    'ESP_COM_003',
    '2025-11-10',
    '09:00',
    'Comisión de Medio Ambiente',
    'Environmental Commission',
    'Congreso de los Diputados, Sala 3',
    'Congress of Deputies, Room 3',
    'Análisis de políticas climáticas',
    'Analysis of Climate Policies',
    'https://www.congreso.es/meeting/003',
    'Environmental Commission - Analysis of Climate Policies Congress of Deputies, Room 3 Analysis of Climate Policies',
    '{"broadcast": "https://www.congreso.es/live/003"}'
),
(
    'ESP_COM_004',
    '2025-11-15',
    '12:00',
    'Comisión de Innovación',
    'Innovation Commission',
    'Congreso de los Diputados, Sala 4',
    'Congress of Deputies, Room 4',
    'Estrategia de innovación tecnológica',
    'Technological Innovation Strategy',
    'https://www.congreso.es/meeting/004',
    'Innovation Commission - Technological Innovation Strategy Congress of Deputies, Room 4 Technological Innovation Strategy',
    '{"broadcast": "https://www.congreso.es/live/004"}'
),
(
    'ESP_COM_005',
    '2025-11-20',
    '10:30',
    'Comisión de Asuntos Europeos',
    'European Affairs Commission',
    'Congreso de los Diputados, Sala 5',
    'Congress of Deputies, Room 5',
    'Coordinación de políticas europeas',
    'European Policy Coordination',
    'https://www.congreso.es/meeting/005',
    'European Affairs Commission - European Policy Coordination Congress of Deputies, Room 5 European Policy Coordination',
    '{"broadcast": "https://www.congreso.es/live/005"}'
);

-- ==========================================
-- Seed for weekly_agenda
-- ==========================================
INSERT INTO weekly_agenda (
    id,
    type,
    date,
    time,
    title,
    committee,
    location,
    description,
    embedding_input
)
VALUES
(
    'WA_001_2025',
    'Plenary Session',
    '2025-12-01',
    '09:00',
    'Debate on Digital Services Act Implementation',
    'IMCO',
    'European Parliament, Brussels',
    'Discussion on the implementation progress of the Digital Services Act',
    'Debate on Digital Services Act Implementation 2025-12-01 09:00 European Parliament, Brussels Discussion on the implementation progress of the Digital Services Act'
),
(
    'WA_002_2025',
    'Committee Meeting',
    '2025-12-02',
    '10:30',
    'Climate Law Amendments Review',
    'ENVI',
    'European Parliament, Brussels',
    'Review of proposed amendments to the Climate Law',
    'Committee Meeting - Climate Law Amendments Review - ENVI European Parliament, Brussels Review of proposed amendments to the Climate Law'
),
(
    'WA_003_2025',
    'Delegation',
    '2025-12-03',
    '14:00',
    'EU-US Parliamentary Meeting',
    'D-US',
    'European Parliament, Brussels',
    'Bilateral discussion on trade and technology cooperation',
    'Delegation - EU-US Parliamentary Meeting - Trade and Technology European Parliament, Brussels Bilateral discussion on trade and technology cooperation'
),
(
    'WA_004_2025',
    'Public Hearing',
    '2025-12-04',
    '11:00',
    'Artificial Intelligence and Ethics',
    'AIDA',
    'European Parliament, Brussels',
    'Expert hearing on ethical implications of AI development',
    'Public Hearing - Artificial Intelligence and Ethics - AIDA European Parliament, Brussels Expert hearing on ethical implications of AI development'
),
(
    'WA_005_2025',
    'Workshop',
    '2025-12-05',
    '15:30',
    'Cybersecurity Best Practices',
    'ITRE',
    'European Parliament, Brussels',
    'Technical workshop on implementing cybersecurity measures',
    'Workshop - Cybersecurity Best Practices - ITRE European Parliament, Brussels Technical workshop on implementing cybersecurity measures'
);
