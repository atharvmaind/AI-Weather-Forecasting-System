export default function ForecastTable({ items }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800/70 bg-slate-900/40 shadow-glow">
      <div className="px-5 py-4 text-sm font-semibold text-slate-100">Forecast Table</div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-y border-slate-800/70 bg-slate-950/30 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-5 py-3">Date</th>
              <th className="px-5 py-3">Temp (°C)</th>
              <th className="px-5 py-3">Humidity (%)</th>
              <th className="px-5 py-3">Rain</th>
              <th className="px-5 py-3">Rain Prob</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {items.map((it) => (
              <tr key={it.date} className="text-slate-200">
                <td className="px-5 py-3 text-slate-300">
                  {new Date(it.date).toLocaleDateString()}
                </td>
                <td className="px-5 py-3">{it.predicted_temp.toFixed(1)}</td>
                <td className="px-5 py-3">{it.predicted_humidity.toFixed(0)}</td>
                <td className="px-5 py-3">
                  <span
                    className={
                      it.rain_prediction
                        ? "rounded-full bg-sky-500/15 px-3 py-1 text-xs text-sky-300"
                        : "rounded-full bg-amber-500/10 px-3 py-1 text-xs text-amber-300"
                    }
                  >
                    {it.rain_prediction ? "Rainy" : "Not Rainy"}
                  </span>
                </td>
                <td className="px-5 py-3 text-slate-300">
                  {(it.rain_probability * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

