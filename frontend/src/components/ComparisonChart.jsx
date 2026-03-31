import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

function formatDate(d) {
  return new Date(d).toLocaleDateString(undefined, { month: "short", day: "2-digit" });
}

export default function ComparisonChart({ items }) {
  const data = (items || []).map((it) => ({
    date: it.date,
    realTemp: Number(it.real_temperature),
    predTemp: Number(it.predicted_temperature),
    realHum: Number(it.real_humidity),
    predHum: Number(it.predicted_humidity),
    realRain: it.real_rain ? 1 : 0,
    predRain: it.rain_prediction === "Yes" ? 1 : 0,
    realRainPct: (it.real_rain ? 1 : 0) * 100,
    predRainPct: (it.rain_prediction === "Yes" ? 1 : 0) * 100,
    rainProb: Number(it.rain_probability) * 100
  }));

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow lg:col-span-2">
        <div className="mb-3 text-sm font-semibold text-slate-100">Temperature Comparison</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ left: 6, right: 18, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
              <XAxis dataKey="date" tickFormatter={formatDate} stroke="rgba(148,163,184,0.65)" />
              <YAxis stroke="rgba(148,163,184,0.65)" />
              <Tooltip
                contentStyle={{
                  background: "rgba(2,6,23,0.95)",
                  border: "1px solid rgba(148,163,184,0.2)"
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="realTemp"
                name="Real Temp"
                stroke="#38bdf8"
                strokeWidth={2}
                dot={false}
                isAnimationActive
              />
              <Line
                type="monotone"
                dataKey="predTemp"
                name="Pred Temp"
                stroke="#a78bfa"
                strokeWidth={2}
                dot={false}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow">
        <div className="mb-3 text-sm font-semibold text-slate-100">Humidity Comparison</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ left: 6, right: 18, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
              <XAxis dataKey="date" tickFormatter={formatDate} stroke="rgba(148,163,184,0.65)" />
              <YAxis stroke="rgba(148,163,184,0.65)" />
              <Tooltip
                contentStyle={{
                  background: "rgba(2,6,23,0.95)",
                  border: "1px solid rgba(148,163,184,0.2)"
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="realHum"
                name="Real Hum"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
                isAnimationActive
              />
              <Line
                type="monotone"
                dataKey="predHum"
                name="Pred Hum"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow lg:col-span-3">
        <div className="mb-3 text-sm font-semibold text-slate-100">Rain Prediction vs Real</div>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: 6, right: 18, top: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.15)" />
              <XAxis dataKey="date" tickFormatter={formatDate} stroke="rgba(148,163,184,0.65)" />
              <YAxis stroke="rgba(148,163,184,0.65)" />
              <Tooltip
                contentStyle={{
                  background: "rgba(2,6,23,0.95)",
                  border: "1px solid rgba(148,163,184,0.2)"
                }}
              />
              <Legend />
              <Bar dataKey="realRainPct" name="Real Rain (0/100)" fill="#38bdf8" radius={[10, 10, 0, 0]} isAnimationActive />
              <Bar dataKey="predRainPct" name="Pred Rain Label (0/100)" fill="#a78bfa" radius={[10, 10, 0, 0]} isAnimationActive />
              <Bar dataKey="rainProb" name="Predicted Rain Probability (%)" fill="#22c55e" radius={[10, 10, 0, 0]} isAnimationActive />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

