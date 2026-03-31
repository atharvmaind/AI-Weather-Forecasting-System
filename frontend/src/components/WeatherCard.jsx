function iconFor({ rain }) {
  if (rain) return "🌧️";
  return "☀️";
}

export default function WeatherCard({ item, variant = "forecast" }) {
  const rawRain = variant === "forecast" ? item.rain_prediction : item.rain;
  const isRain = typeof rawRain === "string" ? rawRain.toLowerCase() === "yes" : !!rawRain;
  const temp = variant === "forecast" ? item.predicted_temp : item.temperature;
  const hum = variant === "forecast" ? item.predicted_humidity : item.humidity;

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-900/40 p-5 shadow-glow">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900/20 via-slate-900/40 to-slate-950/10" />
      {isRain ? <div className="rain-overlay" /> : null}

      <div className="relative flex items-start justify-between gap-4">
        <div>
          <div className="text-sm text-slate-400">{new Date(item.date).toDateString()}</div>
          <div className="mt-2 text-3xl font-semibold tracking-tight">
            {temp.toFixed(1)}°C
          </div>
          <div className="mt-1 text-sm text-slate-300">Humidity: {hum.toFixed(0)}%</div>
          <div className="mt-2 inline-flex items-center gap-2 rounded-full border border-slate-700/70 bg-slate-950/40 px-3 py-1 text-xs">
            <span className={isRain ? "text-sky-300" : "text-amber-300"}>
              {isRain ? "Rainy" : "Not Rainy"}
            </span>
            {variant === "forecast" ? (
              <span className="text-slate-400">
                Prob: {(item.rain_probability * 100).toFixed(0)}%
              </span>
            ) : null}
          </div>
        </div>

        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950/40 text-3xl shadow-glow animate-floaty">
          {iconFor({ rain: isRain })}
        </div>
      </div>
    </div>
  );
}

