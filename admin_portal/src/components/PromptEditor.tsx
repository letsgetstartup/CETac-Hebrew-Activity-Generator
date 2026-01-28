import React, { useState } from 'react';

// Mock Config Data (since we don't have a backend config API yet)
const INITIAL_CONFIG = {
    level: "A1",
    version: "1.0.0",
    morphological_constraints: {
        allowed_tenses: ["PRESENT"],
        allowed_binyanim: ["PAAL"],
        max_sentence_length: 10,
        niqqud_required: true
    },
    system_prompt_template: "אתה מורה מומחה...",
    bloom_taxonomy_rules: {
        distribution: {
            Remembering: 0.4,
            Understanding: 0.4,
            Applying: 0.2
        }
    }
};

const PromptEditor: React.FC = () => {
    const [config, setConfig] = useState(JSON.stringify(INITIAL_CONFIG, null, 2));
    const [error, setError] = useState<string | null>(null);
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
        try {
            JSON.parse(config); // Validate JSON
            setSaved(true);
            setError(null);
            setTimeout(() => setSaved(false), 2000);
            // In real app, POST to /api/admin/config
        } catch (e) {
            setError("Invalid JSON format");
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-slate-800">A1 Prompt Configuration</h3>
                <div className="space-x-2">
                    <button
                        onClick={handleSave}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors font-medium shadow-sm"
                    >
                        Save Changes
                    </button>
                </div>
            </div>

            {error && (
                <div className="mb-4 bg-red-50 text-red-700 p-3 rounded-md border border-red-200 text-sm">
                    ⚠️ {error}
                </div>
            )}

            {saved && (
                <div className="mb-4 bg-green-50 text-green-700 p-3 rounded-md border border-green-200 text-sm">
                    ✅ Configuration saved successfully to version draft.
                </div>
            )}

            <div className="relative">
                <textarea
                    value={config}
                    onChange={(e) => setConfig(e.target.value)}
                    className="w-full h-96 font-mono text-sm bg-slate-50 border border-slate-300 rounded-md p-4 focus:ring-2 focus:ring-blue-500 outline-none text-slate-800"
                    spellCheck={false}
                />
                <div className="absolute top-2 right-2 text-xs text-slate-400 bg-white px-2 py-1 rounded border border-slate-200">
                    JSON
                </div>
            </div>

            <div className="mt-4 border-t border-slate-100 pt-4">
                <h4 className="text-sm font-semibold text-slate-700 mb-2">Morphological Constraints Preview</h4>
                <div className="flex gap-2 flex-wrap">
                    {(() => {
                        try {
                            const parsed = JSON.parse(config);
                            return parsed.morphological_constraints?.allowed_tenses?.map((t: string) => (
                                <span key={t} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-md border border-purple-200">
                                    {t}
                                </span>
                            ));
                        } catch { return null; }
                    })()}
                </div>
            </div>
        </div>
    );
};

export default PromptEditor;
