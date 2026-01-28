import React, { useState } from 'react';
import { generateActivity } from '../api';
import type { ContentModel } from '../types';

const ActivityGenerator: React.FC = () => {
    const [topic, setTopic] = useState('');
    const [level, setLevel] = useState<'A1' | 'A2' | 'B1'>('A1');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ContentModel | null>(null);
    const [error, setError] = useState<string | null>(null);

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
                                    {result.vocabulary_list.map((word, idx) => (
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
                                {result.questions.map((q, idx) => (
                                    <div key={q.id} className="bg-slate-50 rounded-lg p-4" dir="rtl">
                                        <div className="flex items-start gap-2 mb-2">
                                            <span className="bg-emerald-100 text-emerald-700 text-xs px-2 py-0.5 rounded font-bold">
                                                {idx + 1}
                                            </span>
                                            <p className="font-bold text-slate-800 text-lg">{q.stem_hebrew}</p>
                                        </div>
                                        <div className="mr-8 grid grid-cols-2 gap-2">
                                            {q.options.map((opt, optIdx) => (
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
                </div>
            )}
        </div>
    );
};

export default ActivityGenerator;
