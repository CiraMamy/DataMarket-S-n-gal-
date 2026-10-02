import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { territory: 'Dakar', tam: 200, sam: 90, som: 27 },
  { territory: 'Thiès', tam: 120, sam: 50, som: 15 },
  { territory: 'Saint-Louis', tam: 80, sam: 35, som: 10 },
];

export function MarketSizeChart() {
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="territory" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="tam" fill="#10233F" name="TAM (M FCFA)" />
          <Bar dataKey="sam" fill="#D5A021" name="SAM (M FCFA)" />
          <Bar dataKey="som" fill="#667085" name="SOM (M FCFA)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
