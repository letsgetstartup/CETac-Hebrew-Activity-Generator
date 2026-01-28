export interface VocabularyItem {
    hebrew: string;
    english: string;
}

export interface Question {
    id: number;
    stem_hebrew: string;
    options: string[];
    correct_answer_index: number;
    explanation: string;
    cognitive_level: string;
}

export interface ContentModel {
    title_hebrew: string;
    cefr_level: string;
    text_content: string;
    vocabulary_list: VocabularyItem[];
    questions: Question[];
}

export interface ActivityResponse {
    success: boolean;
    data?: ContentModel;
    error?: string;
    message?: string;
    generation_time_ms?: number;
    metadata?: Record<string, any>;
}

export interface GenerateRequest {
    topic: string;
    level: "A1" | "A2" | "B1" | "B2" | "C1";
    variant?: string;
}

// --- Adaptation Types (Task #3) ---

export interface GlossaryItem {
    term: string;
    definition: string;
}

export interface ScaffoldedQuestion {
    original_id: number;
    hint: string;
    cognitive_support: string;
}

export interface AdaptedContentResponse {
    simplified_text: string;
    glossary: GlossaryItem[];
    scaffolded_questions: ScaffoldedQuestion[];
}

export interface AdaptRequest {
    original_text: string;
    original_questions: { id: number; text: string }[];
    student_needs?: string;
}
