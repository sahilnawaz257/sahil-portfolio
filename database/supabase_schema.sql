-- =============================================================================
-- Sahil Nawaz Portfolio — Supabase PostgreSQL Schema & Security Migration
-- Step 2: Production Schema with UUID Primary Keys & Row Level Security (RLS)
-- =============================================================================
-- Features:
-- - UUID Primary Keys (using native gen_random_uuid())
-- - Appropriate PostgreSQL types, constraints, and created_at timestamps
-- - Optimized indexes for search and filtering
-- - Safe Row Level Security (RLS) policies protecting visitor privacy
-- - Zero Admin Dashboard / Zero Admin Tables
-- =============================================================================

-- Ensure UUID extensions are available
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 01. TABLE: contact_messages
-- Stores incoming visitor inquiries submitted through the contact form.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.contact_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT DEFAULT '',
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 02. TABLE: meeting_bookings
-- Stores visitor requests to schedule a Google Meet consultation session.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.meeting_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    purpose TEXT NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' NOT NULL,
    meeting_link TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 03. TABLE: projects
-- Dynamic showcase of authentic AI, Computer Vision, and Software systems.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    technologies TEXT NOT NULL,
    github_url TEXT DEFAULT '',
    live_demo_url TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 04. TABLE: education
-- Formal university degrees and accredited academic qualifications.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution TEXT NOT NULL UNIQUE,
    degree TEXT NOT NULL,
    field TEXT NOT NULL,
    location TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    status TEXT NOT NULL,
    logo_url TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 05. TABLE: experience
-- Professional venture leadership, company track record, and operational scope.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.experience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    duration TEXT NOT NULL,
    description TEXT NOT NULL,
    powered_by TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 06. TABLE: skills
-- Technical, analytical, and product/business capability inventory.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- -----------------------------------------------------------------------------
-- INDEXES FOR FREQUENTLY SEARCHED FIELDS
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_contact_messages_email ON public.contact_messages(email);
CREATE INDEX IF NOT EXISTS idx_contact_messages_created ON public.contact_messages(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_meeting_bookings_email ON public.meeting_bookings(email);
CREATE INDEX IF NOT EXISTS idx_meeting_bookings_pref_date ON public.meeting_bookings(preferred_date);
CREATE INDEX IF NOT EXISTS idx_meeting_bookings_created ON public.meeting_bookings(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_projects_created ON public.projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_skills_category ON public.skills(category);
CREATE INDEX IF NOT EXISTS idx_education_institution ON public.education(institution);
CREATE INDEX IF NOT EXISTS idx_experience_company ON public.experience(company_name);

-- -----------------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Strict Security: Zero public access to private visitor messages/bookings
-- Public read access to display data (projects, education, experience, skills)
-- -----------------------------------------------------------------------------

-- Enable RLS on all 6 tables
ALTER TABLE public.contact_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.meeting_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.education ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experience ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;

-- 1. Policies for contact_messages
DROP POLICY IF EXISTS "Allow public insert to contact_messages" ON public.contact_messages;
CREATE POLICY "Allow public insert to contact_messages"
    ON public.contact_messages
    FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service_role full access to contact_messages" ON public.contact_messages;
CREATE POLICY "Allow service_role full access to contact_messages"
    ON public.contact_messages
    FOR ALL
    TO service_role
    USING (true);

-- 2. Policies for meeting_bookings
DROP POLICY IF EXISTS "Allow public insert to meeting_bookings" ON public.meeting_bookings;
CREATE POLICY "Allow public insert to meeting_bookings"
    ON public.meeting_bookings
    FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

DROP POLICY IF EXISTS "Allow service_role full access to meeting_bookings" ON public.meeting_bookings;
CREATE POLICY "Allow service_role full access to meeting_bookings"
    ON public.meeting_bookings
    FOR ALL
    TO service_role
    USING (true);

-- 3. Policies for projects (Public Read)
DROP POLICY IF EXISTS "Allow public read access to projects" ON public.projects;
CREATE POLICY "Allow public read access to projects"
    ON public.projects
    FOR SELECT
    TO anon, authenticated, public
    USING (true);

DROP POLICY IF EXISTS "Allow service_role manage projects" ON public.projects;
CREATE POLICY "Allow service_role manage projects"
    ON public.projects
    FOR ALL
    TO service_role
    USING (true);

-- 4. Policies for education (Public Read)
DROP POLICY IF EXISTS "Allow public read access to education" ON public.education;
CREATE POLICY "Allow public read access to education"
    ON public.education
    FOR SELECT
    TO anon, authenticated, public
    USING (true);

DROP POLICY IF EXISTS "Allow service_role manage education" ON public.education;
CREATE POLICY "Allow service_role manage education"
    ON public.education
    FOR ALL
    TO service_role
    USING (true);

-- 5. Policies for experience (Public Read)
DROP POLICY IF EXISTS "Allow public read access to experience" ON public.experience;
CREATE POLICY "Allow public read access to experience"
    ON public.experience
    FOR SELECT
    TO anon, authenticated, public
    USING (true);

DROP POLICY IF EXISTS "Allow service_role manage experience" ON public.experience;
CREATE POLICY "Allow service_role manage experience"
    ON public.experience
    FOR ALL
    TO service_role
    USING (true);

-- 6. Policies for skills (Public Read)
DROP POLICY IF EXISTS "Allow public read access to skills" ON public.skills;
CREATE POLICY "Allow public read access to skills"
    ON public.skills
    FOR SELECT
    TO anon, authenticated, public
    USING (true);

DROP POLICY IF EXISTS "Allow service_role manage skills" ON public.skills;
CREATE POLICY "Allow service_role manage skills"
    ON public.skills
    FOR ALL
    TO service_role
    USING (true);

-- -----------------------------------------------------------------------------
-- SEED DATA (Authentic Portfolio Records — Avoid Duplicates with ON CONFLICT)
-- -----------------------------------------------------------------------------

-- 1. Authentic Projects
INSERT INTO public.projects (title, description, technologies, github_url, live_demo_url)
VALUES
    (
        'Crowd Density Counting System',
        'A technology-based system designed to monitor and count crowd density using computer vision and deep learning.',
        'Python, AI / ML, YOLOv8',
        'https://github.com/sahilnawaz257',
        ''
    ),
    (
        'Library Management Software',
        'A software solution to manage library books, student records and transactions with automated persistence.',
        'Python, SQL, SQLite',
        'https://github.com/sahilnawaz257',
        ''
    ),
    (
        'Brand Guideline Audit Tool',
        'A tool designed to check brand consistency, typography compliance, and visual palette auditing.',
        'HTML, CSS, JavaScript',
        'https://github.com/sahilnawaz257',
        ''
    )
ON CONFLICT (title) DO NOTHING;

-- 2. Formal Academic Education
INSERT INTO public.education (institution, degree, field, location, start_date, end_date, status, logo_url)
VALUES
    (
        'JB Group of Institutions of Technology',
        'Bachelor of Technology (B.Tech)',
        'Computer Science and Engineering (CSE)',
        'Dehradun, Uttarakhand, India',
        '2025',
        '2029',
        'Current (2nd Year)',
        'images/jbit-dehradun-logo.png'
    ),
    (
        'The Open University',
        'Data Analyst Online',
        'Computer Science (AI & LangChain RAG)',
        'United Kingdom (Online)',
        'June 2026',
        'July 2029',
        'Enrolled / Upcoming',
        'images/the-open-university-logo.png'
    )
ON CONFLICT (institution) DO NOTHING;

-- 3. Professional Experience & Venture Leadership
INSERT INTO public.experience (company_name, role, duration, description, powered_by)
VALUES
    (
        'Gymsewa',
        'Founder',
        '2024 – Present',
        'Founder of Gymsewa, working on building and developing a business-focused platform. Responsible for product planning, business development, platform strategy, innovation and overall project direction.',
        'Bytewave Innovation'
    )
ON CONFLICT (company_name) DO NOTHING;

-- 4. Technical and Product/Business Skills
INSERT INTO public.skills (skill_name, category)
VALUES
    ('Python', 'Programming Languages'),
    ('C', 'Programming Languages'),
    ('C++', 'Programming Languages'),
    ('Data Structures & Algorithms', 'Programming Languages'),
    ('HTML5', 'Frontend Engineering'),
    ('CSS3', 'Frontend Engineering'),
    ('JavaScript (ES6+)', 'Frontend Engineering'),
    ('React JS', 'Frontend Engineering'),
    ('Responsive UI/UX', 'Frontend Engineering'),
    ('SQL', 'Database Management'),
    ('SQLite', 'Database Management'),
    ('Relational Schemas', 'Database Management'),
    ('Parameterized Queries', 'Database Management'),
    ('NumPy', 'Data Analysis & AI'),
    ('Pandas', 'Data Analysis & AI'),
    ('YOLOv8 Computer Vision', 'Data Analysis & AI'),
    ('LangChain (RAG)', 'Data Analysis & AI'),
    ('Git', 'Tools & Workflow'),
    ('GitHub', 'Tools & Workflow'),
    ('Flask REST APIs', 'Tools & Workflow'),
    ('VS Code', 'Tools & Workflow'),
    ('Product Management', 'Product & Business'),
    ('Business & Entrepreneurship', 'Product & Business'),
    ('Leadership & Management', 'Product & Business'),
    ('Digital & Growth', 'Product & Business')
ON CONFLICT (skill_name) DO NOTHING;
