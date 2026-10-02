import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    mode: 'demo',
    datasets: [
      {
        id: 'population',
        name: 'Population régionale',
        source: 'ANSD',
        territory: 'National',
        period: '2023',
        frequency: 'Annuel',
      },
      {
        id: 'depenses',
        name: 'Dépenses par tête',
        source: 'EHCVM II',
        territory: 'National',
        period: '2021-2022',
        frequency: 'Annuel',
      },
    ],
  });
}
