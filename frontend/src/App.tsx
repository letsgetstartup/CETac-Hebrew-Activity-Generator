
import ActivityGenerator from './components/ActivityGenerator';

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 h-8 w-8 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                C
              </div>
              <span className="font-bold text-xl tracking-tight text-slate-900">
                CET<span className="text-blue-600">ac</span> Platform
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-xs font-semibold px-2 py-1 bg-green-100 text-green-700 rounded border border-green-200">
                v1.0.0-beta
              </span>
              <div className="h-8 w-8 rounded-full bg-slate-200 border-2 border-white shadow-sm overflow-hidden">
                <img src={`https://ui-avatars.com/api/?name=Teacher+User&background=0D8ABC&color=fff`} alt="User" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="py-10">
        <ActivityGenerator />
      </main>

      <footer className="bg-white border-t border-slate-200 mt-auto py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-400 text-sm">
          © 2024 Center for Educational Technology. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;
