INSERT INTO users
    (id, name, email_address, created_at, updated_at, _password, mobile_number, password_changed_at, logged_in_at, failed_login_count, state, platform_admin, current_session_id, auth_type, email_access_validated_at)
VALUES
    ('0d2e9b87-9c54-448c-b549-f764231ee599', 'Functional Tests - Broadcast User Create',     'emergency-alerts-tests+user1@digital.cabinet-office.gov.uk', '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900111', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', false, NULL, 'sms_auth',   NOW()),
    ('1048af40-45f6-4249-a670-df72ba3352d7', 'Functional Tests - Broadcast User Approve',    'emergency-alerts-tests+user2@digital.cabinet-office.gov.uk', '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900222', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', false, NULL, 'sms_auth',   NOW()),
    ('f972899a-3aff-4474-a800-2d9d9e9b0b23', 'Functional Tests - Broadcast User Auth Test',  'emergency-alerts-tests+user3@digital.cabinet-office.gov.uk', '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900222', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', false, NULL, 'sms_auth',   NOW()),
    ('69634ab0-28ab-4ea1-856e-36423058de45', 'Functional Tests - Broadcast User Email Auth', 'emergency-alerts-tests+user4@digital.cabinet-office.gov.uk', '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900222', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', false, NULL, 'email_auth', NOW()),
    ('c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'Functional Tests - Platform Admin',            'emergency-alerts-tests+admin@digital.cabinet-office.gov.uk',      '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900222', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', true,  NULL, 'sms_auth',   NOW()),
    ('7a7d9571-7583-4b69-86c7-256753797dbe', 'Functional Tests - Throttling Login', 'emergency-alerts-tests+user5@digital.cabinet-office.gov.uk', '2021-07-14 14:52:41.503215', '2021-07-14 14:53:59.806529', '$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC', '07700900222', '2021-07-14 14:52:41.496841', '2021-07-14 14:53:00.204258', 0, 'active', false, NULL, 'email_auth', NOW());


INSERT INTO organisation
    (id, name, active, created_at, updated_at, email_branding_id, letter_branding_id, agreement_signed, agreement_signed_at, agreement_signed_by_id, agreement_signed_version, crown, organisation_type, request_to_go_live_notes, agreement_signed_on_behalf_of_email_address, agreement_signed_on_behalf_of_name, billing_contact_email_addresses, billing_contact_names, billing_reference, notes, purchase_order_number)
VALUES
    ('e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5', 'Functional Tests Org', true, '2019-03-25 15:04:27.500149', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


INSERT INTO services
    (id, name, created_at, updated_at, active, message_limit, restricted, email_from, created_by_id, version, research_mode, organisation_type, prefix_sms, crown, rate_limit, contact_link, consent_to_research, volume_email, volume_letter, volume_sms, count_as_live, go_live_at, go_live_user_id, organisation_id, notes, billing_contact_email_addresses, billing_contact_names, billing_reference, purchase_order_number)
VALUES
    ('34b725f0-1f47-49bc-a9f5-aa2a84587c53', 'Functional Tests', '2019-03-25 15:02:40.869192', '2019-03-25 15:35:17.203589', true, 250000, false, 'functional.tests', '0d2e9b87-9c54-448c-b549-f764231ee599', 5, false, 'central', true, true, 3000, 'e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5', NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'Functional Tests Broadcast Service', '2021-07-14 14:36:03.423486', '2021-07-14 14:37:35.234642', true, 50, false, 'functional.tests.broadcast.service', '0d2e9b87-9c54-448c-b549-f764231ee599', 2, false, 'central', true, NULL, 3000, NULL, NULL, NULL, NULL, NULL, false, '2021-07-14 14:37:35.122431', NULL, '38e4bf69-93b0-445d-acee-53ea53fe02df', NULL, NULL, NULL, NULL, NULL);


INSERT INTO api_keys
    (id, name, secret, service_id, expiry_date, created_at, created_by_id, updated_at, version, key_type)
VALUES
    ('22404b3f-779c-49d5-9c3f-46464fb37a62', 'func_tests_broadcast_service_live_key', 'ImMzZTZiNjhmLWJkNDMtNGUzMy04ZmJhLTY3YThjMWJhZDRhMyI.58oYXhsespJeQQ0zolZUdfyTnPw', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', NULL, '2019-03-25 15:07:44.583174', '0d2e9b87-9c54-448c-b549-f764231ee599', NULL, 1, 'normal');


INSERT INTO api_keys_history
    (id, name, secret, service_id, expiry_date, created_at, updated_at, created_by_id, version, key_type)
VALUES
    ('22404b3f-779c-49d5-9c3f-46464fb37a62', 'func_tests_broadcast_service_live_key', 'ImMzZTZiNjhmLWJkNDMtNGUzMy04ZmJhLTY3YThjMWJhZDRhMyI.58oYXhsespJeQQ0zolZUdfyTnPw', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', NULL, '2019-03-25 15:07:44.583174', NULL, '0d2e9b87-9c54-448c-b549-f764231ee599', 1, 'normal');


INSERT INTO permissions
    (id, service_id, user_id, permission, created_at)
VALUES
    -- Functional Tests - Broadcast User Create
    ('57e897b2-a5e2-4e09-bd1b-fd655ea0d2a9', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '0d2e9b87-9c54-448c-b549-f764231ee599', 'create_broadcasts', '2021-07-14 14:53:00.40982'),
    ('85b443b3-2d07-476f-9740-220187f12305', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '0d2e9b87-9c54-448c-b549-f764231ee599', 'manage_templates', '2021-07-14 14:53:00.409842'),
    ('f2060ce7-7966-45a1-b5e1-17aedc93af18', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '0d2e9b87-9c54-448c-b549-f764231ee599', 'cancel_broadcasts', '2021-07-14 14:53:00.409852'),
    ('d9488323-0ad7-4489-a69f-cf1afc4c24c2', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '0d2e9b87-9c54-448c-b549-f764231ee599', 'view_activity', '2021-07-14 14:53:00.409881'),
    ('ea0ec5d2-ce6c-4499-98d7-60a94fd72800', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '0d2e9b87-9c54-448c-b549-f764231ee599', 'reject_broadcasts', '2021-07-14 14:53:00.409891'),

    -- Functional Tests - Broadcast User Approve
    ('4866284f-9414-4f5a-954e-131b189d235f', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '1048af40-45f6-4249-a670-df72ba3352d7', 'cancel_broadcasts', '2021-07-14 14:53:00.409852'),
    ('1b15bb85-52fc-43da-8365-4364103ffc7f', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '1048af40-45f6-4249-a670-df72ba3352d7', 'view_activity', '2021-07-14 14:53:00.409881'),
    ('4be6e744-efea-4b8b-8af9-0d6c66de628b', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '1048af40-45f6-4249-a670-df72ba3352d7', 'reject_broadcasts', '2021-07-14 14:53:00.409891'),
    ('307aaac1-66b0-48b1-aff1-7029be941a03', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '1048af40-45f6-4249-a670-df72ba3352d7', 'approve_broadcasts', '2021-07-14 14:53:00.409891'),

    -- Functional Tests - Broadcast User Auth Test
    ('42a6d8a0-ba01-40c1-8ab3-c1f10d0a20a3', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'f972899a-3aff-4474-a800-2d9d9e9b0b23', 'view_activity', '2021-07-14 14:53:00.409881'),

    -- Functional Tests - Broadcast User Email Auth
    ('47077214-ca6e-4ee2-85b1-c04e72b85407', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', '69634ab0-28ab-4ea1-856e-36423058de45', 'view_activity', '2021-07-14 14:53:00.409881'),

    -- Functional Tests - Platform Admin
    ('c12e1f1a-7635-4a1f-80f9-d25cd2cef26f', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'manage_api_keys', '2021-07-14 14:53:00.40982'),
    ('308280b1-10b3-417b-934c-ea090cd79c6a', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'manage_settings', '2021-07-14 14:53:00.409842'),
    ('9b7b5770-7299-4e25-9d85-85bb65814f33', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'manage_templates', '2021-07-14 14:53:00.409852'),
    ('e1042928-5c7c-4dc4-b150-b6614b65d4f5', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'manage_users', '2021-07-14 14:53:00.409881'),
    ('ee8f6a8b-cbc0-43ab-a710-402c5929f557', '8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'c3d33860-a967-40cf-8eb4-ec1ee38a4df9', 'view_activity', '2021-07-14 14:53:00.409891');


INSERT INTO service_broadcast_settings
    (service_id, channel, created_at, updated_at, provider)
VALUES
    ('8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'severe', '2021-07-14 14:37:35.103872', NULL, 'all');


INSERT INTO service_permissions
    (service_id, permission, created_at)
VALUES
    ('8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'broadcast', '2021-07-14 14:37:35.112856');


INSERT INTO services_history
    (id, name, created_at, updated_at, active, message_limit, restricted, email_from, created_by_id, version, research_mode, organisation_type, prefix_sms, crown, rate_limit, contact_link, consent_to_research, volume_email, volume_letter, volume_sms, count_as_live, go_live_at, go_live_user_id, organisation_id, notes, billing_contact_email_addresses, billing_contact_names, billing_reference, purchase_order_number)
VALUES
    ('8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'Functional Tests Broadcast Service', '2021-07-14 14:36:03.423486', NULL, true, 50, true, 'functional.tests.broadcast.service', '0d2e9b87-9c54-448c-b549-f764231ee599', 1, false, 'central', true, NULL, 3000, NULL, NULL, NULL, NULL, NULL, false, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    ('8e1d56fa-12a8-4d00-bed2-db47180bed0a', 'Functional Tests Broadcast Service', '2021-07-14 14:36:03.423486', '2021-07-14 14:37:35.234642', true, 50, false, 'functional.tests.broadcast.service', '0d2e9b87-9c54-448c-b549-f764231ee599', 2, false, 'central', true, NULL, 3000, NULL, NULL, NULL, NULL, NULL, false, '2021-07-14 14:37:35.122431', NULL, '38e4bf69-93b0-445d-acee-53ea53fe02df', NULL, NULL, NULL, NULL, NULL);


INSERT INTO user_to_service
    (user_id, service_id)
VALUES
    ('0d2e9b87-9c54-448c-b549-f764231ee599', '8e1d56fa-12a8-4d00-bed2-db47180bed0a'),
    ('1048af40-45f6-4249-a670-df72ba3352d7', '8e1d56fa-12a8-4d00-bed2-db47180bed0a'),
    ('f972899a-3aff-4474-a800-2d9d9e9b0b23', '8e1d56fa-12a8-4d00-bed2-db47180bed0a'),
    ('69634ab0-28ab-4ea1-856e-36423058de45', '8e1d56fa-12a8-4d00-bed2-db47180bed0a'),
    ('c3d33860-a967-40cf-8eb4-ec1ee38a4df9', '8e1d56fa-12a8-4d00-bed2-db47180bed0a'),
    ('7a7d9571-7583-4b69-86c7-256753797dbe', '8e1d56fa-12a8-4d00-bed2-db47180bed0a');


INSERT INTO user_to_organisation
    (user_id, organisation_id)
VALUES
    ('0d2e9b87-9c54-448c-b549-f764231ee599', 'e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5');
