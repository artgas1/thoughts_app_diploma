DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM public.auth_user
    ) THEN
        INSERT INTO public.auth_user (
            id,
            "password",
            last_login,
            is_superuser,
            username,
            first_name,
            last_name,
            email,
            is_staff,
            is_active,
            date_joined
        ) VALUES (
            1,
            'pbkdf2_sha256$720000$FSKT5OljZen5IPAzo7MiXA$g6VH4ofoQnIMiJAoGFIWXGphkuUoMgWgSfKJAKc1ZpI=',
            '2024-04-30 18:08:12.347',
            true,
            'admin',
            '',
            '',
            'admin@admin.admin',
            true,
            true,
            '2024-03-29 09:26:39.796'
        );
    END IF;
END $$;
