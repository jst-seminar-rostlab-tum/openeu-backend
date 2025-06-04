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
    'Committee Hearing on Data Protection Reform - Ausschusssitzung zur Datenschutzreform'
),
(
    'test_2',
    'Budget Debate for 2026 Fiscal Year',
    'Budgetdebatte zum Haushaltsjahr 2026',
    'Plenary Session',
    '2025-06-25',
    'Plenarsaal, Parlament Wien',
    'https://www.parlament.gv.at/PAKT/VHG/XXVII/PLEN/PLEN_00456/index.shtml',
    'Budget Debate for 2026 Fiscal Year - Budgetdebatte zum Haushaltsjahr 2026'
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
    'Interparliamentary Conference on Foreign Affairs - Vienna, Austria - foreign policy, EU cooperation, diplomacy'
),
(
    'ipex-2025-002',
    'Joint Parliamentary Scrutiny Meeting on Europol',
    '2025-06-15',
    '2025-06-15',
    'The Hague, Netherlands',
    ARRAY['security', 'Europol', 'law enforcement'],
    'Joint Parliamentary Scrutiny Meeting on Europol - The Hague, Netherlands - security, Europol, law enforcement'
);



--------------------------------
--Seed for users in auth.users--
--------------------------------
INSERT INTO auth.users (
  instance_id,
  id,
  aud,
  role,
  email,
  encrypted_password,
  email_confirmed_at,
  invited_at,
  confirmation_token,
  confirmation_sent_at,
  recovery_token,
  recovery_sent_at,
  email_change_token_new,
  email_change,
  email_change_sent_at,
  last_sign_in_at,
  raw_app_meta_data,
  raw_user_meta_data,
  is_super_admin,
  created_at,
  updated_at,
  phone,
  phone_confirmed_at,
  phone_change,
  phone_change_token,
  phone_change_sent_at,
  email_change_token_current,
  email_change_confirm_status,
  banned_until,
  reauthentication_token,
  reauthentication_sent_at,
  is_sso_user,
  deleted_at,
  is_anonymous
) VALUES
(
  -- Row 1 (anonymized)
  '9ef6c467-f47b-43f4-be9c-6bde6d347f7b',  -- new instance_id v4
  'e3635af1-7b33-4aa6-b367-159aeebdc03f',  -- new id v4
  'authenticated',
  'authenticated',
  'user1@example.com',
  '$2a$10$v1cH69URAjWSMZepjd8XA.dP5CEe1/xQHTQTUisQ52hLmqeRUmfwq',
  TIMESTAMP WITH TIME ZONE '2025-06-01 09:18:48.530899+00',
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-01 09:17:07.41681+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-01 09:19:49.115159+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "e3635af1-7b33-4aa6-b367-159aeebdc03f",
    "email": "user1@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-01 09:17:07.409983+00',
  TIMESTAMP WITH TIME ZONE '2025-06-01 09:19:49.118124+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 2 (anonymized)
  'edfc669c-ee8d-42f0-9278-86649c403bd4',
  '30ff223b-65f8-42bc-ba42-9ee3a8052707',
  'authenticated',
  'authenticated',
  'user2@example.com',
  '$2a$10$idVehPj0teKxdp1APzWMMOBQ6tC5WtToa22KgI9VeSbT5d7obO/Ym',
  TIMESTAMP WITH TIME ZONE '2025-05-16 11:05:56.605687+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-04 08:34:55.503992+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "30ff223b-65f8-42bc-ba42-9ee3a8052707",
    "email": "user2@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-16 10:49:26.451432+00',
  TIMESTAMP WITH TIME ZONE '2025-06-04 08:34:55.506764+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 3 (anonymized)
  '3dbce52c-a175-4788-a75e-e57c3f9bb3c0',
  'f7578b59-21d2-437a-a1a2-2f2c5659e23d',
  'authenticated',
  'authenticated',
  'user3@example.com',
  '$2a$10$pjAjck1DCdLifTL2mETJk.9QFD/HKkxF3UXBx8R3sAL32GMPYqkXq',
  TIMESTAMP WITH TIME ZONE '2025-05-31 10:40:51.656284+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-04 07:36:12.257698+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "f7578b59-21d2-437a-a1a2-2f2c5659e23d",
    "email": "user3@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-31 10:39:36.61825+00',
  TIMESTAMP WITH TIME ZONE '2025-06-04 08:36:30.009455+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 4 (anonymized)
  '94f6b6f4-376b-425c-8a38-9b0fd3df60eb',
  '26f23949-b506-426e-af68-6554c207a771',
  'authenticated',
  'authenticated',
  'user4@example.com',
  '$2a$10$tmqs3SpUmIbTRIdCsE5tvubJFJvzEe7MoXb0GHnfU4YDaPED.SMv6',
  TIMESTAMP WITH TIME ZONE '2025-05-18 11:03:12.14758+00',
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-18 11:02:52.142772+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-20 08:24:54.201418+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "26f23949-b506-426e-af68-6554c207a771",
    "email": "user4@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-18 11:02:52.091688+00',
  TIMESTAMP WITH TIME ZONE '2025-06-02 17:13:11.837308+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 5 (anonymized)
  '3c40ae9a-79f7-4293-8861-32d559709c0a',
  '3cf90183-4be3-4d90-a399-ca663f00b04d',
  'authenticated',
  'authenticated',
  'user5@example.com',
  '$2a$10$gcL7tD0FpkTA6kvi0Ipgz.5SIxvApdspL4jr5G/WeyILNTmKbTjIi',
  TIMESTAMP WITH TIME ZONE '2025-06-03 13:43:00.321512+00',
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-03 13:42:42.379267+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "3cf90183-4be3-4d90-a399-ca663f00b04d",
    "email": "user5@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-03 13:42:42.353995+00',
  TIMESTAMP WITH TIME ZONE '2025-06-03 13:43:00.329449+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 6 (anonymized)
  '80064aa6-dd2c-4ba6-a818-744a4f39151c',
  '253abc33-d273-499b-a744-685c78a901cb',
  'authenticated',
  'authenticated',
  'user6@example.com',
  '$2a$10$zRlXtP.sgqkvfkoWj1d2u.wP52bD0X2kM1OoFy2uvTu6r2OPg0Nm2',
  TIMESTAMP WITH TIME ZONE '2025-05-26 21:17:15.598307+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-02 10:24:55.961892+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "253abc33-d273-499b-a744-685c78a901cb",
    "email": "user6@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-26 21:17:15.595473+00',
  TIMESTAMP WITH TIME ZONE '2025-06-02 10:24:55.966487+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 7 (anonymized)
  'fe627323-230a-4c3e-9480-383be1cc8adb',
  'cf68c8b0-53dc-4be9-8367-7191f6561ad0',
  'authenticated',
  'authenticated',
  'user7@example.com',
  '$2a$10$eh3RWRIO3KI/yv6iXBFxBedikAXyVmJMoA5FqTjsa9qfKra/0/tOu',
  TIMESTAMP WITH TIME ZONE '2025-05-31 14:21:24.684144+00',
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-31 14:20:37.749102+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-03 23:32:13.499421+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "cf68c8b0-53dc-4be9-8367-7191f6561ad0",
    "email": "user7@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-31 14:20:37.741096+00',
  TIMESTAMP WITH TIME ZONE '2025-06-04 08:43:02.266801+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 8 (anonymized)
  '78ce6f48-d892-401f-a78d-11c50e44c0bb',
  '3658a969-d89f-4412-98af-60c02f0da0e4',
  'authenticated',
  'authenticated',
  'user8@example.com',
  '$2a$10$OsMmscg54TTJv.4TKZREV.eeM/81BGXBz/o6J8ueRQJv2WU/owonK',
  TIMESTAMP WITH TIME ZONE '2025-06-03 16:15:32.714452+00',
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-03 16:15:03.109542+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "3658a969-d89f-4412-98af-60c02f0da0e4",
    "email": "user8@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-06-03 16:15:03.09975+00',
  TIMESTAMP WITH TIME ZONE '2025-06-03 16:15:32.717243+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
),
(
  -- Row 9 (anonymized)
  '48086918-3713-4582-8ae7-cd8301794816',
  '456378e1-39f2-4715-98d9-78f80698ffb0',
  'authenticated',
  'authenticated',
  'user9@example.com',
  '$2a$10$fQ/LBzZ5xqWE1cmMuqvI0uk/OiARgHu31Qc/1ni5Ce2z6XwBf/Nqe',
  TIMESTAMP WITH TIME ZONE '2025-05-18 20:45:50.847323+00',
  NULL,
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-31 10:37:01.502825+00',
  NULL,
  NULL,
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-18 20:54:37.963288+00',
  '{"provider":"email","providers":["email"]}',
  '{
    "sub": "456378e1-39f2-4715-98d9-78f80698ffb0",
    "email": "user9@example.com",
    "email_verified": true,
    "phone_verified": false
  }',
  NULL,
  TIMESTAMP WITH TIME ZONE '2025-05-18 20:43:21.671373+00',
  TIMESTAMP WITH TIME ZONE '2025-05-31 10:37:19.272071+00',
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  NULL,
  0,
  NULL,
  NULL,
  NULL,
  FALSE,
  NULL,
  FALSE
);


