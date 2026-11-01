import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#22c55e', '#eab308', '#ef4444', '#3b82f6', '#a855f7']

export function CategoryBar({ data }: { data: { name: string; solved: number; total: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
        <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: 8 }}
          labelStyle={{ color: '#fff' }}
        />
        <Bar dataKey="solved" fill="#22c55e" radius={[4, 4, 0, 0]} />
        <Bar dataKey="total" fill="#1f2937" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

export function SkillRadar({ data }: { data: { subject: string; score: number; fullMark: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid stroke="#1f2937" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 11 }} />
        <PolarRadiusAxis tick={{ fill: '#6b7280', fontSize: 10 }} />
        <Radar dataKey="score" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
      </RadarChart>
    </ResponsiveContainer>
  )
}

export function DifficultyPie({ data }: { data: { name: string; value: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: 8 }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
