'use client';

// ── Category definitions ──────────────────────────────────────────────────────
// Keys must match the field names in the API response (property_schema.py)
// so they map directly into the scoring service's VARIABLE_CONFIG.

interface Attribute { key: string; label: string; description: string }
interface Category  { title: string; color: string; border: string; attributes: Attribute[] }

const CATEGORIES: Category[] = [
  {
    title:  'Property',
    color:  'bg-positive',
    border: 'border-l-positive',
    attributes: [
      { key: 'yearBuilt',         label: 'Year Built',          description: 'How much weight to give the age of the property' },
      { key: 'squareFootage',     label: 'Square Footage',       description: 'Importance of total living area' },
      { key: 'numBedrooms',       label: 'Bedrooms',             description: 'Number of bedrooms for target tenant or buyer' },
      { key: 'numBathrooms',      label: 'Bathrooms',            description: 'Number of bathrooms for target tenant or buyer' },
      { key: 'numFloors',         label: 'Number of Floors',     description: 'Single vs multi-story preference' },
      { key: 'constructionType',  label: 'Construction Type',    description: 'Property class (single family, condo, multi-family, etc.)' },
      { key: 'roofType',          label: 'Roof Type',            description: 'Roof material quality and longevity' },
      { key: 'foundationType',    label: 'Foundation Type',      description: 'Structural foundation quality' },
      { key: 'floodZone',         label: 'Flood Zone',           description: 'Sensitivity to FEMA flood classification' },
      { key: 'hazardRiskZone',    label: 'Hazard Risk',          description: 'Natural disaster risk tolerance' },
    ],
  },
  {
    title:  'Neighborhood',
    color:  'bg-[#7c3aed]',
    border: 'border-l-[#7c3aed]',
    attributes: [
      { key: 'medianHouseholdIncome', label: 'Median Household Income', description: 'Neighborhood income levels and stability' },
      { key: 'unemploymentRate',      label: 'Unemployment Rate',       description: 'Local labor market health (lower is better)' },
      { key: 'schoolRatings',         label: 'School Ratings',          description: 'Value placed on nearby school quality' },
      { key: 'crimeStatistics',       label: 'Crime Index',             description: 'Safety and security of the area (lower is better)' },
      { key: 'homeownershipRate',     label: 'Homeownership Rate',      description: 'Owner-occupancy as a neighborhood stability signal' },
    ],
  },
  {
    title:  'Market',
    color:  'bg-accent',
    border: 'border-l-accent',
    attributes: [
      { key: 'populationGrowth',          label: 'Population Growth',   description: 'Long-term demand driven by growth trends' },
      { key: 'medianHomeValue',           label: 'Median Home Value',   description: 'Benchmark against comparable properties' },
      { key: 'homePriceAppreciationRate', label: 'Price per Sq Ft',     description: 'Value density relative to market comparables' },
      { key: 'daysOnMarket',             label: 'Days on Market',       description: 'Market liquidity (fewer days = higher demand)' },
      { key: 'rentPrices',               label: 'Rent Prices',          description: 'Rental yield potential' },
    ],
  },
];

// Build default ratings (all 3) from category definitions
export function defaultRatings(): Record<string, number> {
  const out: Record<string, number> = {};
  CATEGORIES.forEach(cat => cat.attributes.forEach(a => { out[a.key] = 3; }));
  return out;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function ImportanceLabel({ value }: { value: number }) {
  const labels = ['', 'Not Important', 'Low', 'Moderate', 'High', 'Critical'];
  const colors  = ['', 'text-ink-light', 'text-ink-mid', 'text-warning', 'text-accent', 'text-positive'];
  return (
    <span className={`text-xs font-medium w-24 text-right ${colors[value]}`}>
      {labels[value]}
    </span>
  );
}

interface RatingRowProps {
  label:       string;
  description: string;
  value:       number;
  onChange:    (val: number) => void;
}

function RatingRow({ label, description, value, onChange }: RatingRowProps) {
  return (
    <div className="flex items-center gap-4 py-3.5 border-b border-border last:border-0">
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-ink">{label}</div>
        <div className="text-xs text-ink-light mt-0.5 leading-relaxed">{description}</div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map(n => (
            <button
              key={n}
              onClick={() => onChange(n)}
              className={`w-8 h-8 rounded-lg text-sm font-bold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
                value === n
                  ? 'bg-accent text-white shadow-md scale-105'
                  : 'bg-slate text-ink-mid hover:bg-slate-mid hover:text-ink'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <ImportanceLabel value={value} />
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface Props {
  ratings:        Record<string, number>;
  onRatingChange: (key: string, val: number) => void;
  onRun:          () => void;
  loading:        boolean;
}

export default function InvestorSimulator({ ratings, onRatingChange, onRun, loading }: Props) {
  return (
    <div className="space-y-5 fade-up">

      {/* Instruction banner */}
      <div className="flex items-start gap-3 bg-accent-light border border-accent/20 rounded-lg px-5 py-4">
        <svg className="text-accent mt-0.5 shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <p className="text-sm text-accent leading-relaxed">
          Rate how important each factor is to your investment decision.{' '}
          <strong>1 = Not Important</strong> &nbsp;·&nbsp; <strong>5 = Critical</strong>.
          Hit <strong>Run Simulation</strong> when done to generate your personalized score.
        </p>
      </div>

      {/* Category cards */}
      {CATEGORIES.map(cat => (
        <div key={cat.title} className={`bg-white border border-border border-l-4 ${cat.border} rounded-lg overflow-hidden`}>
          <div className="flex items-center gap-3 px-5 py-3 border-b border-border bg-slate/20">
            <div className={`w-2 h-2 rounded-full ${cat.color}`} />
            <h3 className="font-bold text-navy text-sm uppercase tracking-wider">{cat.title}</h3>
            <span className="ml-auto text-[10px] text-ink-light font-medium uppercase tracking-widest">
              Importance Rating
            </span>
          </div>
          <div className="px-5">
            {cat.attributes.map(attr => (
              <RatingRow
                key={attr.key}
                label={attr.label}
                description={attr.description}
                value={ratings[attr.key] ?? 3}
                onChange={val => onRatingChange(attr.key, val)}
              />
            ))}
          </div>
        </div>
      ))}

      {/* Run button */}
      <div className="flex items-center justify-between pt-2">
        <p className="text-xs text-ink-light">
          Adjust ratings to reflect your investment priorities, then run the simulation.
        </p>
        <button
          onClick={onRun}
          disabled={loading}
          className="bg-navy text-white font-semibold px-8 py-2.5 rounded-lg hover:bg-navy-light transition-colors shadow-sm disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              Scoring…
            </>
          ) : (
            'Run Simulation →'
          )}
        </button>
      </div>

    </div>
  );
}
