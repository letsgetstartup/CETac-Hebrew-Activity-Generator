
import PromptEditor from './components/PromptEditor';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <nav className="bg-slate-900 text-white h-16 flex items-center px-6 shadow-md border-b border-slate-700">
        <span className="font-bold text-xl tracking-tight">CETac <span className="text-slate-400 font-light">Admin</span></span>
        <div className="ml-8 space-x-4 text-sm font-medium text-slate-300">
          <a href="#" className="text-white hover:text-white transition-colors">Prompt Engineering</a>
          <a href="#" className="hover:text-white transition-colors">Users</a>
          <a href="#" className="hover:text-white transition-colors">Analytics</a>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Prompt Management</h1>
          <p className="text-slate-500 mt-2">Configure pedagogical rules and linguistic constraints for each CEFR level.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="space-y-2">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-200">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Levels</h3>
              <nav className="space-y-1">
                <button className="w-full text-left px-3 py-2 bg-blue-50 text-blue-700 font-medium rounded-md border border-blue-200">
                  A1 (Beginner)
                </button>
                <button className="w-full text-left px-3 py-2 text-slate-600 hover:bg-slate-50 rounded-md transition-colors">
                  A2 (Elementary)
                </button>
                <button className="w-full text-left px-3 py-2 text-slate-600 hover:bg-slate-50 rounded-md transition-colors">
                  B1 (Intermediate)
                </button>
              </nav>
            </div>
          </aside>

          <section className="lg:col-span-3">
            <PromptEditor />
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
