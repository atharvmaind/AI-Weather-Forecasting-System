import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar.jsx";
import WeatherCard from "../components/WeatherCard.jsx";
import RealWeatherCard from "../components/RealWeatherCard.jsx";
import PredictionCard from "../components/PredictionCard.jsx";
import ComparisonChart from "../components/ComparisonChart.jsx";
import { api } from "../api.js";

function Loading() {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-300">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-sky-400" />
      <div>Generating AI forecast…</div>
    </div>
  );
}

export default function Dashboard() {
  const [city, setCity] = useState("Pune");
  const defaultStart = useMemo(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1); // open-meteo is typically for near-future
    return d.toISOString().slice(0, 10);
  }, []);

  const [startDate, setStartDate] = useState(defaultStart);
  const [days, setDays] = useState(10);
  const [past, setPast] = useState([]);
  const [comparison, setComparison] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const rainDays = useMemo(() => comparison.filter((x) => x.rain_prediction === "Yes").length, [comparison]);

  async function ensureTrained() {
    await api.post("/train-model");
  }

  async function loadPast() {
    const res = await api.get("/past-weather", {
      params: { city: String(city || "").trim(), start_date: startDate }
    });
    setPast(res.data.items || []);
  }

  async function predict() {
    setError("");
    setLoading(true);
    try {
      await ensureTrained();
      const res = await api.post("/predict", {
        city: String(city || "").trim(),
        start_date: startDate,
        days: Number(days)
      });
      setComparison(res.data.items || []);
      await loadPast();
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Failed to fetch predictions. Check backend connection.";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPast().catch(() => {
      // ignore until backend is running or invalid input
    });
  }, [city, startDate]);

  return (
    <div className="min-h-screen bg-slate-950">
      <Navbar />

      <div className="bg-grid">
        <div className="mx-auto max-w-6xl px-4 py-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="text-2xl font-semibold tracking-tight text-slate-100">
                AI Weather Forecasting System
              </div>
              <div className="mt-1 max-w-2xl text-sm text-slate-400">
                Smart weather forecasting to help you stay prepared with upcoming temperature, 
                humidity, and rainfall predictions.
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="w-full sm:w-52">
                <label className="text-xs text-slate-400">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g. Pune"
                  className="mt-1 w-full rounded-xl border border-slate-800/70 bg-slate-950/40 px-4 py-3 text-sm text-slate-100 outline-none ring-0 focus:border-sky-500/60"
                />
              </div>

              <div className="w-full sm:w-52">
                <label className="text-xs text-slate-400">Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800/70 bg-slate-950/40 px-4 py-3 text-sm text-slate-100 outline-none ring-0 focus:border-sky-500/60"
                />
              </div>

              <div className="w-full sm:w-36">
                <label className="text-xs text-slate-400">Days</label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={days}
                  onChange={(e) => setDays(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-800/70 bg-slate-950/40 px-4 py-3 text-sm text-slate-100 outline-none ring-0 focus:border-sky-500/60"
                />
              </div>
              <button
                onClick={predict}
                disabled={loading}
                className="inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 px-5 py-3 text-sm font-semibold text-white shadow-glow transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Predict
              </button>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-slate-800/70 bg-slate-900/30 p-5 shadow-glow">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-sm text-slate-300">
                <span className="text-slate-100 font-semibold">Real vs Predicted</span>{" "}
                {comparison.length ? (
                  <>
                    • {comparison.length} days in {city || "your city"} • {rainDays} predicted rainy days
                  </>
                ) : (
                  <>• Run a prediction to see results</>
                )}
              </div>
              {loading ? <Loading /> : null}
            </div>
            {error ? (
              <div className="mt-3 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
                {error}
              </div>
            ) : null}
          </div>

          {comparison.length ? (
            <>
              <div className="mt-6">
                <div className="mb-3 text-sm font-semibold text-slate-100">Real Weather</div>
                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                  {comparison.map((it) => (
                    <RealWeatherCard key={it.date} item={it} />
                  ))}
                </div>
              </div>

              <div className="mt-8">
                <div className="mb-3 text-sm font-semibold text-slate-100">Predicted Weather</div>
                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                  {comparison.map((it) => (
                    <PredictionCard key={it.date} item={it} />
                  ))}
                </div>
              </div>

              <div className="mt-8">
                <ComparisonChart items={comparison} />
              </div>
            </>
          ) : null}

          <div className="mt-10">
            <div className="mb-3 text-sm font-semibold text-slate-100">
              Past 7 Days Weather
            </div>
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {past.map((it) => (
                <WeatherCard key={it.date} item={it} variant="past" />
              ))}
              {!past.length ? (
                <div className="rounded-2xl border border-slate-800/70 bg-slate-900/20 p-6 text-sm text-slate-400">
                  Start the backend + train the model to load past data.
                </div>
              ) : null}
            </div>
          </div>

          <div className="mt-10 pb-10 text-xs text-slate-500">
            Tip: set <span className="text-slate-300">VITE_API_URL</span> for deployment.
          </div>
        </div>
      </div>
    </div>
  );
}

