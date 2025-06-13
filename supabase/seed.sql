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
