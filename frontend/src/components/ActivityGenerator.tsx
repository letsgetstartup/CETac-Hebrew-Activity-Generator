import React, { useState } from 'react';
import { generateActivity, adaptActivity } from '../api';
import type { ContentModel, AdaptedContentResponse, VocabularyItem, Question, GlossaryItem, ScaffoldedQuestion } from '../types';

const ActivityGenerator: React.FC = () => {
    const [topic, setTopic] = useState('');
    const [level, setLevel] = useState<'A1' | 'A2' | 'B1'>('A1');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ContentModel | null>(null);
    const [adaptedResult, setAdaptedResult] = useState<AdaptedContentResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [adaptedLoading, setAdaptedLoading] = useState(false);

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!topic) return;

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await generateActivity({ topic, level });

            if (response.success && response.data) {
                setResult(response.data);

                // --- Task #3: Trigger Scaffolding ---
                setAdaptedLoading(true);
                try {
                    const adaptation = await adaptActivity({
                        original_text: response.data.text_content,
                        original_questions: response.data.questions.map(q => ({ id: q.id, text: q.stem_hebrew })),
                        student_needs: "general_difficulty"
                    });
                    if (adaptation && !adaptation.error) {
                        setAdaptedResult(adaptation);
                    }
                } catch (e) {
                    console.error("Scaffolding failed", e);
                } finally {
                    setAdaptedLoading(false);
                }
            } else {
                setError(response.message || response.error || 'Unknown error occurred');
            }
        } catch (err) {
            setError('Failed to connect to generator service');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-8">
            {/* Search Header */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <h2 className="text-2xl font-bold text-slate-800 mb-6 font-display">
                    Hebrew Activity Generator
                </h2>

                <form onSubmit={handleGenerate} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="md:col-span-3">
                            <label className="block text-sm font-medium text-slate-600 mb-1">
                                Topic
                            </label>
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="e.g., Summer vacation, Shopping at the market"
                                className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-600 mb-1">
                                CEFR Level
                            </label>
                            <select
                                value={level}
                                onChange={(e) => setLevel(e.target.value as any)}
                                className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                                disabled={loading}
                            >
                                <option value="A1">A1 (Beginner)</option>
                                <option value="A2">A2 (Elementary)</option>
                                <option value="B1">B1 (Intermediate)</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            disabled={loading || !topic}
                            className={`
                px-8 py-3 rounded-lg font-semibold text-white transition-all transform
                ${loading || !topic
                                    ? 'bg-slate-300 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0'
                                }
              `}
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Generating...
                                </span>
                            ) : 'Generate Activity'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Error State */}
            {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                    <div className="flex items-start">
                        <div className="ml-3">
                            <h3 className="text-red-800 font-medium">Generation Failed</h3>
                            <p className="text-red-700 text-sm mt-1">{error}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Results Display */}
            {result && (
                <div className="space-y-6 animate-fade-in">
                    {/* Main Text Card */}
                    <div className="bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden">
                        <div className="bg-blue-50/50 px-6 py-4 border-b border-blue-100 flex justify-between items-center">
                            <h3 className="text-xl font-bold text-slate-800" dir="rtl">
                                {result.title_hebrew}
                            </h3>
                            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold uppercase rounded-full tracking-wide">
                                Level {result.cefr_level}
                            </span>
                        </div>
                        <div className="p-8">
                            <p className="text-2xl leading-loose font-serif text-slate-800 text-right" dir="rtl">
                                {result.text_content}
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Vocabulary Card */}
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                            <div className="bg-amber-50/50 px-6 py-4 border-b border-amber-100">
                                <h4 className="font-bold text-slate-700">Vocabulary Checklist</h4>
                            </div>
                            <div className="p-0">
                                <ul className="divide-y divide-slate-100">
                                    {result.vocabulary_list.map((word: VocabularyItem, idx: number) => (
                                        <li key={idx} className="px-6 py-3 flex justify-between items-center hover:bg-slate-50 transition-colors">
                                            <span className="text-sm text-slate-500 font-medium">{word.english}</span>
                                            <span className="text-lg font-bold text-slate-800" dir="rtl">{word.hebrew}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        {/* Questions Card */}
                        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                            <div className="bg-emerald-50/50 px-6 py-4 border-b border-emerald-100">
                                <h4 className="font-bold text-slate-700">Comprehension Questions</h4>
                            </div>
                            <div className="p-6 space-y-6">
                                {result.questions.map((q: Question, idx: number) => (
                                    <div key={q.id} className="bg-slate-50 rounded-lg p-4" dir="rtl">
                                        <div className="flex items-start gap-2 mb-2">
                                            <span className="bg-emerald-100 text-emerald-700 text-xs px-2 py-0.5 rounded font-bold">
                                                {idx + 1}
                                            </span>
                                            <p className="font-bold text-slate-800 text-lg">{q.stem_hebrew}</p>
                                        </div>
                                        <div className="mr-8 grid grid-cols-2 gap-2">
                                            {q.options.map((opt: string, optIdx: number) => (
                                                <div
                                                    key={optIdx}
                                                    className={`
                             text-center py-2 px-3 rounded text-sm font-medium border
                             ${optIdx === q.correct_answer_index
                                                            ? 'bg-emerald-100 border-emerald-300 text-emerald-800'
                                                            : 'bg-white border-slate-200 text-slate-600'
                                                        }
                           `}
                                                >
                                                    {opt}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* --- Task #3: Pedagogical Scaffolding Section --- */}
                    {(adaptedLoading || adaptedResult) && (
                        <div className="pt-12 border-t-2 border-dashed border-slate-200 mt-12">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="p-2 bg-indigo-100 rounded-lg">
                                    <svg className="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-slate-900">Pedagogical Scaffolding (Task #3)</h3>
                                    <p className="text-slate-500">Accessible version for students with reading difficulties</p>
                                </div>
                            </div>

                            {adaptedLoading ? (
                                <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-slate-100 border-dashed">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                                    <p className="text-slate-600 font-medium">Adapting content for special needs...</p>
                                    <p className="text-slate-400 text-sm mt-1">Simplifying syntax and generating cognitive hints</p>
                                </div>
                            ) : adaptedResult && (
                                <div className="space-y-8 animate-fade-in-up">
                                    {/* Simplified Text */}
                                    <div className="bg-indigo-50/50 rounded-2xl p-8 border border-indigo-100">
                                        <div className="flex justify-between items-center mb-6">
                                            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold uppercase rounded-full">Simplified Text</span>
                                            <span className="text-indigo-400 text-sm italic font-medium px-4 py-1 bg-white rounded-full shadow-sm border border-indigo-50">High Frequency SVO Structure</span>
                                        </div>
                                        <p className="text-3xl leading-[1.8] font-serif text-slate-800 text-right whitespace-pre-wrap" dir="rtl">
                                            {adaptedResult.simplified_text}
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                        {/* Glossary Card */}
                                        <div className="lg:col-span-1 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden self-start">
                                            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-2">
                                                <span className="bg-white p-1.5 rounded-md shadow-sm border border-slate-200">
                                                    <svg className="h-4 w-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                                    </svg>
                                                </span>
                                                <h4 className="font-bold text-slate-800">Support Glossary</h4>
                                            </div>
                                            <div className="p-0">
                                                {adaptedResult.glossary.map((item: GlossaryItem, idx: number) => (
                                                    <div key={idx} className="px-6 py-4 hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0" dir="rtl">
                                                        <div className="font-bold text-indigo-600 text-lg mb-1">{item.term}</div>
                                                        <div className="text-slate-600 text-sm leading-relaxed">{item.definition}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        {/* Cognitive Hints */}
                                        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                                            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center gap-2">
                                                <span className="bg-white p-1.5 rounded-md shadow-sm border border-slate-200">
                                                    <svg className="h-4 w-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0012 18.75c-1.03 0-1.9-.4-2.511-1.033l-.552-.547z" />
                                                    </svg>
                                                </span>
                                                <h4 className="font-bold text-slate-800">Question Scaffolding & Hints</h4>
                                            </div>
                                            <div className="p-6 space-y-6">
                                                {adaptedResult.scaffolded_questions.map((hint: ScaffoldedQuestion, idx: number) => (
                                                    <div key={hint.original_id} className="group relative" dir="rtl">
                                                        <div className="flex gap-4">
                                                            <div className="flex-shrink-0 w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center font-bold border border-indigo-100 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                                                                {idx + 1}
                                                            </div>
                                                            <div className="flex-grow pt-1.5">
                                                                <div className="bg-amber-50 text-amber-900 px-4 py-3 rounded-xl border-2 border-amber-100 mb-3 shadow-sm relative">
                                                                    <span className="font-bold ml-2">רמז:</span>
                                                                    {hint.hint}
                                                                </div>
                                                                <div className="text-slate-500 text-xs flex items-center gap-2 pr-2">
                                                                    <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                                    </svg>
                                                                    תמיכה קוגניטיבית: {hint.cognitive_support}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ActivityGenerator;
