function iconFor(weatherIcon) {
  if (weatherIcon === "Rainy") return "🌧️";
  if (weatherIcon === "Sunny") return "☀️";
  return "☁️";
}

export default function PredictionCard({ item }) {
  const isRain = item.rain_prediction === "Yes";
  const icon = iconFor(item.predicted_weather_icon);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-900/40 p-5 shadow-glow">
      {isRain ? <div className="rain-overlay" /> : null}
      <div className="relative flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-slate-400">{new Date(item.date).toDateString()}</div>
          <div className="mt-2 text-3xl font-semibold tracking-tight">
            {Number(item.predicted_temperature).toFixed(1)}°C
          </div>
          <div className="mt-1 text-sm text-slate-300">
            Humidity: {Number(item.predicted_humidity).toFixed(0)}%
          </div>
          <div className="mt-2 inline-flex items-center gap-2 rounded-full border border-slate-700/70 bg-slate-950/40 px-3 py-1 text-xs">
            <span className={isRain ? "text-sky-300" : "text-amber-300"}>
              {isRain ? "Rainy" : "Not Rainy"}
            </span>
            <span className="text-slate-400">
              Prob: {(Number(item.rain_probability) * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950/40 text-3xl shadow-glow animate-floaty">
          {icon}
        </div>
      </div>
    </div>
  );
}

