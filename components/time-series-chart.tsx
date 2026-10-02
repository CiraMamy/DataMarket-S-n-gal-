import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { year: '2020', value: 85, upper: 95, lower: 75 },
  { year: '2021', value: 92, upper: 105, lower: 80 },
  { year: '2022', value: 110, upper: 125, lower: 95 },
  { year: '2023', value: 135, upper: 155, lower: 115 },
];

export function TimeSeriesChart({ title }: { title?: string }) {
  return (
    <div className="h-80 w-full">
      {title && <p className="mb-4 font-medium text-navy">{title}</p>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#10233F" name="Valeur observée" />
          <Line type="monotone" dataKey="upper" stroke="#D5A021" name="Intervalle sup." strokeDasharray="5 5" />
          <Line type="monotone" dataKey="lower" stroke="#667085" name="Intervalle inf." strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
