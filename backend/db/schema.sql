-- Prompt Build Tool Database Schema
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR UNIQUE,
    full_name VARCHAR,
    avatar_url VARCHAR,
    website VARCHAR,
    bio TEXT,
    role VARCHAR DEFAULT 'user' CHECK (role IN ('user', 'admin', 'editor')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Prompt Packs table
CREATE TABLE IF NOT EXISTS prompt_packs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    yaml_content TEXT,
    version VARCHAR DEFAULT '0.1.0',
    category VARCHAR DEFAULT 'general',
    tags TEXT[],
    price DECIMAL(10,2) DEFAULT 0.00,
    stripe_price_id VARCHAR,
    is_public BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    downloads INTEGER DEFAULT 0,
    stars INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES prompt_packs(id) ON DELETE CASCADE,
    prompt_name VARCHAR,
    score DECIMAL(3,1) CHECK (score >= 0 AND score <= 10),
    pass_rate DECIMAL(3,2) CHECK (pass_rate >= 0 AND pass_rate <= 1),
    model_used VARCHAR,
    test_case JSONB,
    result JSONB,
    user_id UUID REFERENCES profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stars/Favorites table
CREATE TABLE IF NOT EXISTS prompt_stars (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    prompt_id UUID REFERENCES prompt_packs(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, prompt_id)
);

-- Analytics table
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    event_type VARCHAR NOT NULL,
    user_id UUID REFERENCES profiles(id),
    prompt_id UUID REFERENCES prompt_packs(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test Cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    prompt_id UUID REFERENCES prompt_packs(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    input_data JSONB,
    expected_output TEXT,
    test_type VARCHAR DEFAULT 'functional',
    criteria TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (RLS) Policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_packs ENABLE ROW LEVEL SECURITY;
ALTER TABLE evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_stars ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Public profiles are viewable by everyone" ON profiles
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Prompt packs policies
CREATE POLICY "Public prompt packs are viewable by everyone" ON prompt_packs
    FOR SELECT USING (is_public = true OR auth.uid() = user_id);

CREATE POLICY "Users can insert their own prompt packs" ON prompt_packs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own prompt packs" ON prompt_packs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own prompt packs" ON prompt_packs
    FOR DELETE USING (auth.uid() = user_id);

-- Evaluations policies
CREATE POLICY "Users can view evaluations for public prompts" ON evaluations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM prompt_packs 
            WHERE prompt_packs.id = evaluations.prompt_id 
            AND (prompt_packs.is_public = true OR prompt_packs.user_id = auth.uid())
        )
    );

CREATE POLICY "Users can insert evaluations" ON evaluations
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Stars policies
CREATE POLICY "Users can view all stars" ON prompt_stars
    FOR SELECT USING (true);

CREATE POLICY "Users can star prompts" ON prompt_stars
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unstar prompts" ON prompt_stars
    FOR DELETE USING (auth.uid() = user_id);

-- Test cases policies
CREATE POLICY "Users can view test cases for accessible prompts" ON test_cases
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM prompt_packs 
            WHERE prompt_packs.id = test_cases.prompt_id 
            AND (prompt_packs.is_public = true OR prompt_packs.user_id = auth.uid())
        )
    );

CREATE POLICY "Users can manage test cases for their prompts" ON test_cases
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM prompt_packs 
            WHERE prompt_packs.id = test_cases.prompt_id 
            AND prompt_packs.user_id = auth.uid()
        )
    );

-- Functions
CREATE OR REPLACE FUNCTION increment_downloads(pack_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE prompt_packs 
    SET downloads = downloads + 1,
        updated_at = NOW()
    WHERE id = pack_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION increment_stars(pack_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE prompt_packs 
    SET stars = (
        SELECT COUNT(*) FROM prompt_stars 
        WHERE prompt_id = pack_id
    ),
    updated_at = NOW()
    WHERE id = pack_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO profiles (id, full_name, avatar_url, username)
    VALUES (
        NEW.id,
        NEW.raw_user_meta_data->>'full_name',
        NEW.raw_user_meta_data->>'avatar_url',
        NEW.raw_user_meta_data->>'username'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE handle_new_user();

-- Updated at triggers
CREATE OR REPLACE FUNCTION handle_updated_at()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER handle_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE PROCEDURE handle_updated_at();

CREATE TRIGGER handle_prompt_packs_updated_at
    BEFORE UPDATE ON prompt_packs
    FOR EACH ROW EXECUTE PROCEDURE handle_updated_at();

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_prompt_packs_user_id ON prompt_packs(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_packs_category ON prompt_packs(category);
CREATE INDEX IF NOT EXISTS idx_prompt_packs_is_public ON prompt_packs(is_public);
CREATE INDEX IF NOT EXISTS idx_prompt_packs_created_at ON prompt_packs(created_at);
CREATE INDEX IF NOT EXISTS idx_evaluations_prompt_id ON evaluations(prompt_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_created_at ON evaluations(created_at);
CREATE INDEX IF NOT EXISTS idx_prompt_stars_user_id ON prompt_stars(user_id);
CREATE INDEX IF NOT EXISTS idx_prompt_stars_prompt_id ON prompt_stars(prompt_id);