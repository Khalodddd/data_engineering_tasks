-- Clear old data
TRUNCATE TABLE names, email_domains CASCADE;

-- Insert comprehensive US names
INSERT INTO names (locale_id, name_type, name_value) VALUES
-- US Male names
('en_US', 'first_male', 'James'), ('en_US', 'first_male', 'John'),
('en_US', 'first_male', 'Robert'), ('en_US', 'first_male', 'Michael'),
('en_US', 'first_male', 'William'), ('en_US', 'first_male', 'David'),
('en_US', 'first_male', 'Richard'), ('en_US', 'first_male', 'Joseph'),
('en_US', 'first_male', 'Thomas'), ('en_US', 'first_male', 'Charles'),
('en_US', 'first_male', 'Christopher'), ('en_US', 'first_male', 'Daniel'),
('en_US', 'first_male', 'Matthew'), ('en_US', 'first_male', 'Anthony'),
('en_US', 'first_male', 'Donald'), ('en_US', 'first_male', 'Mark'),
('en_US', 'first_male', 'Paul'), ('en_US', 'first_male', 'Steven'),
('en_US', 'first_male', 'Andrew'), ('en_US', 'first_male', 'Kenneth'),
('en_US', 'first_male', 'Joshua'), ('en_US', 'first_male', 'Kevin'),
('en_US', 'first_male', 'Brian'), ('en_US', 'first_male', 'George'),
('en_US', 'first_male', 'Edward'), ('en_US', 'first_male', 'Ronald'),
('en_US', 'first_male', 'Timothy'), ('en_US', 'first_male', 'Jason'),
('en_US', 'first_male', 'Jeffrey'), ('en_US', 'first_male', 'Ryan'),
('en_US', 'first_male', 'Jacob'), ('en_US', 'first_male', 'Gary'),
('en_US', 'first_male', 'Nicholas'), ('en_US', 'first_male', 'Eric'),
('en_US', 'first_male', 'Stephen'), ('en_US', 'first_male', 'Jonathan'),
('en_US', 'first_male', 'Larry'), ('en_US', 'first_male', 'Justin'),
('en_US', 'first_male', 'Scott'), ('en_US', 'first_male', 'Brandon'),
('en_US', 'first_male', 'Frank'), ('en_US', 'first_male', 'Benjamin'),
('en_US', 'first_male', 'Gregory'), ('en_US', 'first_male', 'Raymond'),
('en_US', 'first_male', 'Samuel'), ('en_US', 'first_male', 'Patrick'),
('en_US', 'first_male', 'Alexander'), ('en_US', 'first_male', 'Jack'),

-- US Female names
('en_US', 'first_female', 'Mary'), ('en_US', 'first_female', 'Patricia'),
('en_US', 'first_female', 'Jennifer'), ('en_US', 'first_female', 'Linda'),
('en_US', 'first_female', 'Elizabeth'), ('en_US', 'first_female', 'Barbara'),
('en_US', 'first_female', 'Susan'), ('en_US', 'first_female', 'Jessica'),
('en_US', 'first_female', 'Sarah'), ('en_US', 'first_female', 'Karen'),
('en_US', 'first_female', 'Nancy'), ('en_US', 'first_female', 'Lisa'),
('en_US', 'first_female', 'Margaret'), ('en_US', 'first_female', 'Betty'),
('en_US', 'first_female', 'Sandra'), ('en_US', 'first_female', 'Ashley'),
('en_US', 'first_female', 'Dorothy'), ('en_US', 'first_female', 'Kimberly'),
('en_US', 'first_female', 'Emily'), ('en_US', 'first_female', 'Donna'),
('en_US', 'first_female', 'Michelle'), ('en_US', 'first_female', 'Carol'),
('en_US', 'first_female', 'Amanda'), ('en_US', 'first_female', 'Melissa'),
('en_US', 'first_female', 'Deborah'), ('en_US', 'first_female', 'Stephanie'),
('en_US', 'first_female', 'Rebecca'), ('en_US', 'first_female', 'Laura'),
('en_US', 'first_female', 'Helen'), ('en_US', 'first_female', 'Sharon'),
('en_US', 'first_female', 'Cynthia'), ('en_US', 'first_female', 'Kathleen'),
('en_US', 'first_female', 'Amy'), ('en_US', 'first_female', 'Shirley'),
('en_US', 'first_female', 'Angela'), ('en_US', 'first_female', 'Anna'),
('en_US', 'first_female', 'Brenda'), ('en_US', 'first_female', 'Pamela'),
('en_US', 'first_female', 'Nicole'), ('en_US', 'first_female', 'Ruth'),
('en_US', 'first_female', 'Katherine'), ('en_US', 'first_female', 'Samantha'),
('en_US', 'first_female', 'Christine'), ('en_US', 'first_female', 'Emma'),
('en_US', 'first_female', 'Catherine'), ('en_US', 'first_female', 'Debra'),
('en_US', 'first_female', 'Virginia'), ('en_US', 'first_female', 'Rachel'),

-- US Last names
('en_US', 'last', 'Smith'), ('en_US', 'last', 'Johnson'),
('en_US', 'last', 'Williams'), ('en_US', 'last', 'Brown'),
('en_US', 'last', 'Jones'), ('en_US', 'last', 'Garcia'),
('en_US', 'last', 'Miller'), ('en_US', 'last', 'Davis'),
('en_US', 'last', 'Rodriguez'), ('en_US', 'last', 'Martinez'),
('en_US', 'last', 'Hernandez'), ('en_US', 'last', 'Lopez'),
('en_US', 'last', 'Gonzalez'), ('en_US', 'last', 'Wilson'),
('en_US', 'last', 'Anderson'), ('en_US', 'last', 'Thomas'),
('en_US', 'last', 'Taylor'), ('en_US', 'last', 'Moore'),
('en_US', 'last', 'Jackson'), ('en_US', 'last', 'Martin'),
('en_US', 'last', 'Lee'), ('en_US', 'last', 'Perez'),
('en_US', 'last', 'Thompson'), ('en_US', 'last', 'White'),
('en_US', 'last', 'Harris'), ('en_US', 'last', 'Sanchez'),
('en_US', 'last', 'Clark'), ('en_US', 'last', 'Ramirez'),
('en_US', 'last', 'Lewis'), ('en_US', 'last', 'Robinson'),
('en_US', 'last', 'Walker'), ('en_US', 'last', 'Young'),
('en_US', 'last', 'Allen'), ('en_US', 'last', 'King'),
('en_US', 'last', 'Wright'), ('en_US', 'last', 'Scott'),
('en_US', 'last', 'Torres'), ('en_US', 'last', 'Nguyen'),
('en_US', 'last', 'Hill'), ('en_US', 'last', 'Flores'),
('en_US', 'last', 'Green'), ('en_US', 'last', 'Adams'),
('en_US', 'last', 'Nelson'), ('en_US', 'last', 'Baker'),
('en_US', 'last', 'Hall'), ('en_US', 'last', 'Rivera'),
('en_US', 'last', 'Campbell'), ('en_US', 'last', 'Mitchell'),
('en_US', 'last', 'Carter'), ('en_US', 'last', 'Roberts');

-- Insert email domains
INSERT INTO email_domains (locale_id, domain_name) VALUES
('en_US', 'gmail.com'), ('en_US', 'yahoo.com'),
('en_US', 'hotmail.com'), ('en_US', 'outlook.com'),
('en_US', 'aol.com'), ('en_US', 'icloud.com'),
('en_US', 'protonmail.com'), ('en_US', 'zoho.com');

SELECT 'Data populated successfully!' as info;
SELECT 'Names count:' as info, COUNT(*) as total_names FROM names;
SELECT 'Email domains:' as info, COUNT(*) as total_domains FROM email_domains;
