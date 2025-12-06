DROP FUNCTION IF EXISTS generate_users_batch(VARCHAR, INTEGER, INTEGER, INTEGER);

CREATE OR REPLACE FUNCTION generate_users_batch(
    p_locale VARCHAR(10),
    p_seed INTEGER DEFAULT 12345,
    p_batch_index INTEGER DEFAULT 0,
    p_batch_size INTEGER DEFAULT 10
) RETURNS TABLE(
    user_id INTEGER,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20)
) AS $$
DECLARE
    i INTEGER;
    global_id INTEGER;
    rnum INTEGER;
    fname TEXT;
    lname TEXT;
    domain TEXT;
    email_local TEXT;
BEGIN
    FOR i IN 1..p_batch_size LOOP
        global_id := (p_batch_index * p_batch_size) + i;
        rnum := (p_seed + global_id) % 1000000;
        
        -- Get first name deterministically
        IF rnum % 2 = 0 THEN
            -- Male
            SELECT name_value INTO fname
            FROM names 
            WHERE locale_id = p_locale AND name_type = 'first_male'
            ORDER BY name_id
            LIMIT 1
            OFFSET (rnum % 50);
        ELSE
            -- Female
            SELECT name_value INTO fname
            FROM names 
            WHERE locale_id = p_locale AND name_type = 'first_female'
            ORDER BY name_id
            LIMIT 1
            OFFSET (rnum % 50);
        END IF;
        
        -- Get last name
        SELECT name_value INTO lname
        FROM names 
        WHERE locale_id = p_locale AND name_type = 'last'
        ORDER BY name_id
        LIMIT 1
        OFFSET ((rnum * 2) % 50);
        
        -- Get domain
        SELECT domain_name INTO domain
        FROM email_domains 
        WHERE locale_id = p_locale
        ORDER BY domain_id
        LIMIT 1
        OFFSET ((rnum * 3) % 8);
        
        -- Fallbacks
        IF fname IS NULL THEN fname := CASE WHEN rnum % 2 = 0 THEN 'John' ELSE 'Jane' END; END IF;
        IF lname IS NULL THEN lname := 'Smith'; END IF;
        IF domain IS NULL THEN domain := 'example.com'; END IF;
        
        -- Create email
        email_local := LOWER(
            REGEXP_REPLACE(fname, '[^a-zA-Z]', '', 'g') || '.' || 
            REGEXP_REPLACE(lname, '[^a-zA-Z]', '', 'g') || 
            global_id::TEXT
        );
        
        -- Return
        RETURN QUERY SELECT 
            global_id,
            fname::VARCHAR(100),
            lname::VARCHAR(100),
            (email_local || '@' || domain)::VARCHAR(255),
            ('(' || LPAD(((200 + (rnum * 5) % 800)::INTEGER)::TEXT, 3, '0') || 
             ') ' || LPAD(((200 + (rnum * 7) % 800)::INTEGER)::TEXT, 3, '0') || 
             '-' || LPAD(((rnum * 11) % 10000)::INTEGER::TEXT, 4, '0'))::VARCHAR(20);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Test
SELECT * FROM generate_users_batch('en_US', 12345, 0, 10);
