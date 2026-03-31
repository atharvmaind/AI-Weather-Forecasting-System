import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

function formatDate(d) {
  return new Date(d).toLocaleDateString(undefined, { month: "short", day: "2-digit" });
}

export default function WeatherChart({ forecastItems }) {
  const data = forecastItems.map((it) => ({
    date: it.date,
    temp: Number(it.predicted_temp.toFixed(2)),
    humidity: Number(it.predicted_humidity.toFixed(2)),
    rainProb: Number((it.rain_probability * 100).toFixed(0))
  }));

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow lg:col-span-2">
        <div className="mb-3 text-sm font-semibold text-slate-100">Temperature (°C)</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ left: 6, right: 18, top: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="tempFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0} />
                </linearGradient>
              </defs>
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
              <Area
                type="monotone"
                dataKey="temp"
                name="Temperature"
                stroke="#38bdf8"
                fill="url(#tempFill)"
                strokeWidth={2}
                isAnimationActive
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow">
        <div className="mb-3 text-sm font-semibold text-slate-100">Humidity (%)</div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ left: 6, right: 18, top: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="humFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#a78bfa" stopOpacity={0.0} />
                </linearGradient>
              </defs>
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
              <Area
                type="monotone"
                dataKey="humidity"
                name="Humidity"
                stroke="#a78bfa"
                fill="url(#humFill)"
                strokeWidth={2}
                isAnimationActive
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800/70 bg-slate-900/40 p-4 shadow-glow lg:col-span-3">
        <div className="mb-3 text-sm font-semibold text-slate-100">Rain Probability (%)</div>
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
              <Bar
                dataKey="rainProb"
                name="Rain Probability"
                fill="#22c55e"
                radius={[10, 10, 0, 0]}
                isAnimationActive
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

