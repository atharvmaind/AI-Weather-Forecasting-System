export default function Navbar() {
  return (
    <div className="sticky top-0 z-40 border-b border-slate-800/70 bg-slate-950/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-sky-400 to-indigo-500 shadow-glow" />
          <div>
            <div className="text-sm font-semibold tracking-wide text-slate-100">
              AI Weather Forecasting System
            </div>
            <div className="text-xs text-slate-400">10-Day Prediction Dashboard</div>
          </div>
        </div>
        <div className="hidden text-xs text-slate-400 sm:block">
          FastAPI · RandomForest · PostgreSQL · React
        </div>
      </div>
    </div>
  );
}

