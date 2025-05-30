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
    associated_committee_or_delegation_name
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
    'Committee on the Internal Market and Consumer Protection'
),
(
    'Hearing on Green Transition Policies',
    'Bas Eickhout',
    '2025-06-03',
    'Strasbourg, Room A3G-2',
    'Vice-Chair',
    '2021/0202(COD)',
    'ENVI',
    'Committee on the Environment, Public Health and Food Safety'
);

-- =======================
-- Seed for ep_meetings
-- =======================
INSERT INTO ep_meetings (
    title,
    datetime,
    place,
    subtitles
)
VALUES
(
    'Plenary Session on EU Enlargement Strategy',
    '2025-06-10 09:00:00',
    'European Parliament, Strasbourg',
    'Live interpretation in EN, FR, DE'
),
(
    'Debate on Artificial Intelligence Act',
    '2025-06-12 14:30:00',
    'European Parliament, Brussels',
    'Subtitles available in 24 EU languages'
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
    embedding_input,
    scraped_at
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
    'Committee Hearing on Data Protection Reform Parlament Wien, Sitzungssaal 2',
    '2025-05-29 10:00:00'
),
(
    'test_2',
    'Budget Debate for 2026 Fiscal Year',
    'Budgetdebatte zum Haushaltsjahr 2026',
    'Plenary Session',
    '2025-06-25',
    'Plenarsaal, Parlament Wien',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/PLEN/PLEN_00456/index.shtml',
    'Budget Debate for 2026 Fiscal Year Parlament Wien, Plenarsaal',
    '2025-05-29 10:00:00'
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
    tags
)
VALUES
(
    'ipex-2025-001',
    'Interparliamentary Conference on Foreign Affairs',
    '2025-06-05',
    '2025-06-06',
    'Vienna, Austria',
    ARRAY['foreign policy', 'EU cooperation', 'diplomacy']
),
(
    'ipex-2025-002',
    'Joint Parliamentary Scrutiny Meeting on Europol',
    '2025-06-15',
    '2025-06-15',
    'The Hague, Netherlands',
    ARRAY['security', 'Europol', 'law enforcement']
);
