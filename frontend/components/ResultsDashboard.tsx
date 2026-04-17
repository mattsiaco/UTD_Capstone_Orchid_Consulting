'use client';

import { EnrichResponse } from './types';

// ── Formatters ───────────────────────────────────────────────────────────────

function fmtMoney(val: number | null): string {
  if (val == null) return '—';
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
  if (val >= 1_000)     return `$${Math.round(val).toLocaleString('en-US')}`;
  return `$${val}`;
}

function fmtPct(val: number | null, decimals = 1): string {
  if (val == null) return '—';
  return `${val.toFixed(decimals)}%`;
}

// ── Atoms ────────────────────────────────────────────────────────────────────

function NA() {
  return <span className="text-ink-light text-sm font-normal">—</span>;
}

function Tag({ label, variant = 'default' }: { label: string; variant?: 'green' | 'yellow' | 'red' | 'default' }) {
  const cls = {
    green:   'bg-positive-bg text-positive border-positive/20',
    yellow:  'bg-warning-bg text-warning border-warning/20',
    red:     'bg-danger-bg text-danger border-danger/20',
    default: 'bg-slate-mid text-ink-mid border-border',
  }[variant];
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-semibold border ${cls}`}>
      {label}
    </span>
  );
}

function FloodTag({ zone }: { zone: string | null }) {
  if (!zone) return <NA />;
  const isX = zone === 'X';
  const isA = zone.startsWith('A');
  const label   = isX ? `Zone X — Minimal` : `Zone ${zone} — High Risk`;
  const variant = isX ? 'green' : isA ? 'red' : 'default';
  return <Tag label={label} variant={variant} />;
}

function RiskTag({ rating }: { rating: string | null }) {
  if (!rating) return <NA />;
  const lower   = rating.toLowerCase();
  const variant = lower.includes('very high') || lower.includes('high') ? 'red'
                : lower.includes('moderate')                            ? 'yellow'
                : lower.includes('low')                                 ? 'green'
                :                                                         'default';
  return <Tag label={rating} variant={variant} />;
}

// ── Layout ───────────────────────────────────────────────────────────────────

function Section({ title, accent, children }: { title: string; accent?: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-4">
        {accent && <div className={`w-1 h-4 rounded-full ${accent}`} />}
        <h2 className="text-xs font-bold uppercase tracking-widest text-ink-mid">{title}</h2>
        <div className="flex-1 h-px bg-border" />
      </div>
      {children}
    </div>
  );
}

interface StatCardProps {
  label:     string;
  value:     React.ReactNode;
  source?:   string;
  bar?:      number;
  positive?: boolean;
  accent?:   string; // left border color class
}

function StatCard({ label, value, source, bar, positive, accent }: StatCardProps) {
  return (
    <div className={`bg-white border border-border rounded-lg p-5 ${accent ? `border-l-4 ${accent}` : ''}`}>
      <div className="text-xs text-ink-light font-medium mb-2 uppercase tracking-wide">{label}</div>
      <div className="text-2xl font-bold text-ink leading-none mb-1">{value}</div>
      {bar != null && (
        <div className="mt-2.5 h-1.5 rounded-full bg-slate-mid overflow-hidden">
          <div className="score-fill h-full rounded-full bg-accent" style={{ width: `${Math.min(100, bar)}%` }} />
        </div>
      )}
      {source && <div className="text-[10px] text-ink-light mt-2 font-medium">{source}</div>}
    </div>
  );
}

function DataTable({ rows }: { rows: { label: string; value: React.ReactNode }[] }) {
  return (
    <div className="bg-white border border-border rounded-lg overflow-hidden">
      {rows.map((row, i) => (
        <div key={row.label}
          className={`flex justify-between items-center px-5 py-3 text-sm ${i !== rows.length - 1 ? 'border-b border-border' : ''} ${i % 2 === 0 ? '' : 'bg-slate/50'}`}
        >
          <span className="text-ink-mid">{row.label}</span>
          <span className="font-semibold text-ink text-right max-w-[55%]">{row.value ?? <NA />}</span>
        </div>
      ))}
    </div>
  );
}

// ── Dashboard ────────────────────────────────────────────────────────────────

interface Props { address: string; data: EnrichResponse; }

export default function ResultsDashboard({ address, data }: Props) {
  const p = data.property;
  const n = data.neighborhood;
  const m = data.market;

  const popDelta  = m.populationGrowth != null
    ? `${m.populationGrowth > 0 ? '+' : ''}${m.populationGrowth.toFixed(1)}% (4-yr)`
    : null;
  const schoolBar = n.schoolRatings    != null ? (n.schoolRatings / 4.3) * 100 : undefined;
  const ownerBar  = n.homeownershipRate ?? undefined;

  return (
    <div className="max-w-5xl mx-auto px-6 pb-24 pt-8 fade-up">

      {/* Property header */}
      <div className="rounded-xl px-7 py-6 mb-7 text-white"
        style={{ background: 'linear-gradient(135deg, #0f2342 0%, #1a3a6b 100%)' }}>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs text-blue-200 uppercase tracking-widest font-semibold mb-2">
              Property Report
            </div>
            <div className="text-xl font-bold text-white mb-2">{address}</div>
            <div className="flex flex-wrap gap-3 mt-1">
              {p.constructionType && (
                <span className="text-xs bg-white/10 text-blue-100 px-2.5 py-1 rounded-full font-medium">
                  {p.constructionType}
                </span>
              )}
              {p.yearBuilt && (
                <span className="text-xs bg-white/10 text-blue-100 px-2.5 py-1 rounded-full font-medium">
                  Built {p.yearBuilt}
                </span>
              )}
              {p.squareFootage && (
                <span className="text-xs bg-white/10 text-blue-100 px-2.5 py-1 rounded-full font-medium">
                  {Math.round(p.squareFootage).toLocaleString()} sq ft
                </span>
              )}
              {p.numBedrooms && (
                <span className="text-xs bg-white/10 text-blue-100 px-2.5 py-1 rounded-full font-medium">
                  {p.numBedrooms} bed
                </span>
              )}
              {p.numBathrooms && (
                <span className="text-xs bg-white/10 text-blue-100 px-2.5 py-1 rounded-full font-medium">
                  {p.numBathrooms} bath
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-blue-200 font-semibold mb-1.5">Hazard Risk</div>
            <RiskTag rating={p.hazardRiskZone} />
          </div>
        </div>
      </div>

      {/* Market */}
      <Section title="Market Overview" accent="bg-accent">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard
            label="Median Home Value"
            value={m.medianHomeValue != null ? fmtMoney(m.medianHomeValue) : <NA />}
            source="Census ACS 5-yr"
            accent="border-l-accent"
          />
          <StatCard
            label="Avg Days on Market"
            value={m.daysOnMarket != null ? `${m.daysOnMarket} days` : <NA />}
            source="RentCast"
            accent="border-l-accent"
          />
          <StatCard
            label="Population Growth"
            value={m.populationGrowth != null
              ? <span className={m.populationGrowth > 0 ? 'text-positive' : 'text-danger'}>
                  {m.populationGrowth > 0 ? '+' : ''}{m.populationGrowth.toFixed(1)}%
                </span>
              : <NA />}
            source="Census 2018 → 2022"
            accent="border-l-accent"
          />
          <StatCard
            label="Price / Sq Ft"
            value={m.homePriceAppreciationRate != null ? `$${m.homePriceAppreciationRate.toFixed(0)}` : <NA />}
            source="ATTOM sales"
            accent="border-l-accent"
          />
        </div>
      </Section>

      {/* Neighborhood */}
      <Section title="Neighborhood" accent="bg-[#7c3aed]">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <StatCard
            label="Median Household Income"
            value={n.medianHouseholdIncome != null ? fmtMoney(n.medianHouseholdIncome) : <NA />}
            source="ACS 5-yr estimate"
            accent="border-l-[#7c3aed]"
          />
          <StatCard
            label="Homeownership Rate"
            value={n.homeownershipRate != null ? fmtPct(n.homeownershipRate) : <NA />}
            bar={ownerBar}
            accent="border-l-[#7c3aed]"
          />
          <StatCard
            label="Unemployment Rate"
            value={n.unemploymentRate != null ? fmtPct(n.unemploymentRate) : <NA />}
            source="Civilian labor force"
            accent="border-l-[#7c3aed]"
          />
          <StatCard
            label="School Rating"
            value={n.schoolRatings != null ? `${n.schoolRatings.toFixed(2)} / 4.3` : <NA />}
            bar={schoolBar}
            source="Nearby schools avg"
            accent="border-l-[#7c3aed]"
          />
          <StatCard
            label="Crime Index"
            value={n.crimeStatistics != null ? String(n.crimeStatistics) : <NA />}
            accent="border-l-[#7c3aed]"
          />
        </div>
      </Section>

      {/* Property + Market side by side */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Section title="Property Details" accent="bg-positive">
          <DataTable rows={[
            { label: 'Year Built',     value: p.yearBuilt ?? <NA /> },
            { label: 'Square Footage', value: p.squareFootage != null ? `${Math.round(p.squareFootage).toLocaleString()} sq ft` : <NA /> },
            { label: 'Bedrooms',       value: p.numBedrooms ?? <NA /> },
            { label: 'Bathrooms',      value: p.numBathrooms ?? <NA /> },
            { label: 'Floors',         value: p.numFloors ?? <NA /> },
            { label: 'Construction',   value: p.constructionType ?? <NA /> },
            { label: 'Roof',           value: p.roofType ? p.roofType.trim() : <NA /> },
            { label: 'Foundation',     value: p.foundationType ?? <NA /> },
            { label: 'Flood Zone',     value: <FloodTag zone={p.floodZone} /> },
            { label: 'Hazard Risk',    value: <RiskTag rating={p.hazardRiskZone} /> },
          ]} />
        </Section>

        <Section title="Market Details" accent="bg-warning">
          <DataTable rows={[
            { label: 'Rent (AVM Est.)',    value: m.rentPrices != null ? fmtMoney(m.rentPrices) : <NA /> },
            { label: 'Zoning',             value: m.zoningInformation ?? <NA /> },
            { label: 'Days on Market',     value: m.daysOnMarket != null ? `${m.daysOnMarket} days` : <NA /> },
            { label: 'Price / Sq Ft',      value: m.homePriceAppreciationRate != null ? `$${m.homePriceAppreciationRate.toFixed(2)}` : <NA /> },
            { label: 'Population Growth',  value: popDelta ?? <NA /> },
            { label: 'Median Home Value',  value: m.medianHomeValue != null ? fmtMoney(m.medianHomeValue) : <NA /> },
          ]} />
        </Section>
      </div>

    </div>
  );
}
