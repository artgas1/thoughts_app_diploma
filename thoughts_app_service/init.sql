CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DO $$
BEGIN
    -- Insert sample data into User table
    IF NOT EXISTS (SELECT 1 FROM auth_user) THEN
        INSERT INTO auth_user (first_name, last_name, username, email, password, is_staff, is_superuser, is_active, date_joined)
        VALUES
        ('', '', 'admin', 'admin@admin.admin', 'pbkdf2_sha256$720000$FSKT5OljZen5IPAzo7MiXA$g6VH4ofoQnIMiJAoGFIWXGphkuUoMgWgSfKJAKc1ZpI=', true, true, true, '2024-03-29 09:26:39.796'),
        ('', '', 'john_doe', 'john.doe@example.com', 'pbkdf2_sha256$720000$FSKT5OljZen5IPAzo7MiXA$g6VH4ofoQnIMiJAoGFIWXGphkuUoMgWgSfKJAKc1ZpI=', false, false, true, '2023-05-09'),
        ('', '', 'jane_doe', 'jane.doe@example.com', 'pbkdf2_sha256$720000$FSKT5OljZen5IPAzo7MiXA$g6VH4ofoQnIMiJAoGFIWXGphkuUoMgWgSfKJAKc1ZpI=', false, false, true, '2023-05-09');
    END IF;

    -- Insert sample data into Achievement table
    IF NOT EXISTS (SELECT 1 FROM thoughts_core_achievement) THEN
        INSERT INTO thoughts_core_achievement (name, cover_file_url, description)
        VALUES
        ('Mindful Mastery', 'http://example.com/mindful_mastery.jpg', 'Achieve mindfulness through guided meditation.'),
        ('Zen Peak', 'http://example.com/zen_peak.jpg', 'Reach the peak of tranquility with our curated Zen sessions'),
        ('Advanced Mindfulness', 'http://example.com/advanced_mindfulness.jpg', 'Master advanced mindfulness techniques for personal growth.');

    END IF;
    
    -- Insert sample data into UserInfo table
    IF NOT EXISTS (SELECT 1 FROM thoughts_core_userinfo) THEN
        INSERT INTO thoughts_core_userinfo (user_id, name, phone_number)
        VALUES
        ((SELECT id FROM auth_user WHERE username='john_doe'), 'John Doe', '+1234567890'),
        ((SELECT id FROM auth_user WHERE username='jane_doe'), 'Jane Doe', '+0987654321'),
        ((SELECT id FROM auth_user WHERE username='admin'), 'Admin', '+1122334455');
    END IF;


    IF NOT EXISTS (SELECT 1 FROM thoughts_core_meditationtheme) THEN
        -- Insert sample data into MeditationTheme table
        INSERT INTO thoughts_core_meditationtheme (name, cover_file_url)
        VALUES
        ('Relaxation', 'http://example.com/relaxation_theme.jpg'),
        ('Focus', 'http://example.com/focus_theme.jpg');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM thoughts_core_meditationnarrator) THEN
        -- Insert sample data into MeditationNarrator table
        INSERT INTO thoughts_core_meditationnarrator (name)
        VALUES
        ('Alice Wonder'),
        ('Bob Smith');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM thoughts_core_meditation) THEN
        -- Insert sample data into Meditation table
        INSERT INTO thoughts_core_meditation (name, meditation_theme_id, meditation_narrator_id, audio_file_url, cover_file_url)
        VALUES
        ('Deep Relaxation', (SELECT id FROM thoughts_core_meditationtheme WHERE name='Relaxation'), (SELECT id FROM thoughts_core_meditationnarrator WHERE name='Alice Wonder'), 'http://example.com/deep_relaxation.mp3', 'http://example.com/deep_relaxation_cover.jpg'),
        ('Daily Focus', (SELECT id FROM thoughts_core_meditationtheme WHERE name='Focus'), (SELECT id FROM thoughts_core_meditationnarrator WHERE name='Bob Smith'), 'http://example.com/daily_focus.mp3', 'http://example.com/daily_focus_cover.jpg');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM thoughts_core_meditationsession WHERE user_id = (SELECT id FROM auth_user WHERE username='john_doe') AND meditation_id = (SELECT id FROM thoughts_core_meditation WHERE name='Deep Relaxation') AND session_start_time = '2023-05-09 09:00:00') THEN
        INSERT INTO thoughts_core_meditationsession (user_id, meditation_id, session_start_time)
        VALUES
        ((SELECT id FROM auth_user WHERE username='john_doe'), (SELECT id FROM thoughts_core_meditation WHERE name='Deep Relaxation'), '2023-05-09 09:00:00'),
        ((SELECT id FROM auth_user WHERE username='jane_doe'), (SELECT id FROM thoughts_core_meditation WHERE name='Daily Focus'), '2023-05-09 10:00:00'),
        ((SELECT id FROM auth_user WHERE username='admin'), (SELECT id FROM thoughts_core_meditation WHERE name='Deep Relaxation'), '2023-05-09 09:00:00'),
        ((SELECT id FROM auth_user WHERE username='admin'), (SELECT id FROM thoughts_core_meditation WHERE name='Daily Focus'), '2023-05-09 09:00:00');
    END IF;


    IF NOT EXISTS (SELECT 1 FROM thoughts_core_meditationgrade) THEN
        -- Insert sample data into MeditationGrade table
        INSERT INTO thoughts_core_meditationgrade (user_id, meditation_id, grade)
        VALUES
        ((SELECT id FROM auth_user WHERE username='john_doe'), (SELECT id FROM thoughts_core_meditation WHERE name='Deep Relaxation'), 5),
        ((SELECT id FROM auth_user WHERE username='jane_doe'), (SELECT id FROM thoughts_core_meditation WHERE name='Daily Focus'), 4),
        ((SELECT id FROM auth_user WHERE username='admin'), (SELECT id FROM thoughts_core_meditation WHERE name='Deep Relaxation'), 5),
        ((SELECT id FROM auth_user WHERE username='admin'), (SELECT id FROM thoughts_core_meditation WHERE name='Daily Focus'), 5);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM thoughts_core_chat) THEN
        -- Insert sample data into Chat table
        INSERT INTO thoughts_core_chat (id, user_id, chat_messages, created_at, updated_at)
        VALUES
        (uuid_generate_v4(), (SELECT id FROM auth_user WHERE username='john_doe'), '[{"text":"Hello", "timestamp":"2023-05-09 09:15:00"}]', '2023-05-09 09:15:00', '2023-05-09 09:15:00'),
        (uuid_generate_v4(), (SELECT id FROM auth_user WHERE username='admin'), '[{"text":"Welcome to the Admin Session", "timestamp":"2024-04-30 12:00:00"}]', '2024-04-30 12:00:00', '2024-04-30 12:00:00');

    END IF;

    IF NOT EXISTS (SELECT 1 FROM thoughts_core_userachievement) THEN
        -- Assign the new achievement to John and Jane
        insert into thoughts_core_userachievement (user_info_id, achievement_id)
        values
        ((SELECT id FROM thoughts_core_userinfo WHERE name='John Doe'), (select id from thoughts_core_achievement where name='Mindful Mastery')),
        ((SELECT id FROM thoughts_core_userinfo WHERE name='Jane Doe'), (select id from thoughts_core_achievement where name='Zen Peak')),
        ((SELECT id FROM thoughts_core_userinfo WHERE name='Admin'), (SELECT id FROM thoughts_core_achievement WHERE name='Mindful Mastery')),
        ((SELECT id FROM thoughts_core_userinfo WHERE name='Admin'), (SELECT id FROM thoughts_core_achievement WHERE name='Zen Peak')),
        ((SELECT id FROM thoughts_core_userinfo WHERE name='Admin'), (SELECT id FROM thoughts_core_achievement WHERE name='Advanced Mindfulness'));
    END IF;
END $$;