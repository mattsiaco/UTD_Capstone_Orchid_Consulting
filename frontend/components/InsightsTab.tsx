'use client';

import { EnrichResponse } from './types';

export interface ScoreResult {
  investmentScore:  number;
  scoreLabel:       string;
  variableScores:   Record<string, number>;
  weights:          Record<string, number>;
  weightedScores:   Record<string, number>;
}

// ── Formatters ────────────────────────────────────────────────────────────────

function fmtMoney(val: number | null): string {
  if (val == null) return '—';
  if (val >= 1_000_000) return `$${(val / 1_000_000).toFixed(2)}M`;
  if (val >= 1_000)     return `$${Math.round(val).toLocaleString('en-US')}`;
  return `$${val}`;
}

// ── Insight generation ────────────────────────────────────────────────────────

type InsightType = 'strength' | 'risk' | 'caution';

interface Insight {
  key:   string;
  title: string;   // active headline — states the finding
  body:  string;   // 1-2 sentences with specific data + recommendation
  type:  InsightType;
  stat?: string;   // optional big callout number
  statLabel?: string;
}

function generateInsight(key: string, score: number, data: EnrichResponse): Insight | null {
  const p = data.property;
  const n = data.neighborhood;
  const m = data.market;

  const type: InsightType = score >= 0.65 ? 'strength' : score >= 0.40 ? 'caution' : 'risk';

  switch (key) {

    case 'yearBuilt':
      if (p.yearBuilt == null) return null;
      return type === 'strength'
        ? { key, type, stat: String(p.yearBuilt), statLabel: 'Year Built',
            title: 'Modern construction reduces near-term maintenance risk',
            body: `Built in ${p.yearBuilt}, this property is relatively recent — fewer immediate capital improvements expected, which protects your cash flow in early years of ownership.` }
        : { key, type, stat: String(p.yearBuilt), statLabel: 'Year Built',
            title: 'Older construction demands a renovation budget',
            body: `At ${p.yearBuilt}, factor in potential costs for systems upgrades (HVAC, roofing, plumbing). Get an inspection report before finalizing your offer and negotiate the price accordingly.` };

    case 'squareFootage':
      if (p.squareFootage == null) return null;
      const sqft = Math.round(p.squareFootage).toLocaleString();
      return type === 'strength'
        ? { key, type, stat: `${sqft} sq ft`, statLabel: 'Living Area',
            title: 'Generous square footage supports premium pricing',
            body: `At ${sqft} sq ft, this property sits above the median — giving you pricing power on both rent and resale without over-improving.` }
        : { key, type, stat: `${sqft} sq ft`, statLabel: 'Living Area',
            title: 'Limited square footage caps your rent ceiling',
            body: `${sqft} sq ft restricts your target tenant pool. Price competitively, focus on finishes, and target single professionals or couples rather than families.` };

    case 'numBedrooms':
      if (p.numBedrooms == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${p.numBedrooms} bed`, statLabel: 'Bedrooms',
            title: `${p.numBedrooms}-bedroom layout appeals to the widest tenant pool`,
            body: 'This bedroom count hits the market sweet spot — broad demand from families and working professionals supports both rental stability and resale liquidity.' }
        : { key, type,
            title: 'Bedroom count limits your target audience',
            body: `A ${p.numBedrooms}-bedroom unit narrows your options. Focus your marketing on the right profile and price accordingly to minimize vacancy.` };

    case 'numBathrooms':
      if (p.numBathrooms == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${p.numBathrooms} bath`, statLabel: 'Bathrooms',
            title: 'Above-average bathrooms are a proven rent premium driver',
            body: 'Multiple bathrooms consistently rank among the top features tenants and buyers pay more for. This is a genuine competitive advantage in this market.' }
        : { key, type,
            title: 'Limited bathrooms will constrain your asking rent',
            body: `${p.numBathrooms} bathroom(s) may reduce appeal to multi-person households. Budget for an addition if market comparables consistently show more.` };

    case 'constructionType':
      if (p.constructionType == null) return null;
      return type === 'strength'
        ? { key, type,
            title: `${p.constructionType} is the most liquid property class`,
            body: 'Broad market appeal means easier exit when you are ready to sell. Financing is also more accessible for buyers, expanding your eventual buyer pool.' }
        : { key, type,
            title: `${p.constructionType} may face a narrower buyer pool`,
            body: 'Understand your specific target market before committing. Niche property classes can still perform well but require more targeted marketing and may face stricter financing rules.' };

    case 'roofType':
      if (p.roofType == null) return null;
      return type === 'strength'
        ? { key, type,
            title: `${p.roofType.trim()} roof is low-maintenance and long-lasting`,
            body: 'Quality roof materials protect your cash flow by reducing replacement frequency. This is a genuine cost advantage relative to properties with wood shake or flat roofs.' }
        : { key, type,
            title: 'Roof type may require earlier-than-expected replacement',
            body: `${p.roofType?.trim()} roofing has a shorter service life. Verify remaining life with an inspector and use the finding to negotiate a price concession or seller credit.` };

    case 'foundationType':
      if (p.foundationType == null) return null;
      return type === 'strength'
        ? { key, type,
            title: `${p.foundationType} foundation is the most stable and insurable`,
            body: 'Solid foundation type reduces structural risk and insurance complexity. This is a background factor investors rarely think about until it becomes a problem — here it works in your favor.' }
        : { key, type,
            title: 'Foundation type warrants a structural inspection',
            body: `${p.foundationType} foundations can be serviceable but carry higher long-term maintenance risk. Commission a structural engineer report before closing — use findings in price negotiations.` };

    case 'floodZone':
      if (p.floodZone == null) return null;
      return p.floodZone === 'X'
        ? { key, type: 'strength', stat: 'Zone X', statLabel: 'FEMA Flood',
            title: 'Minimal flood risk — no mandatory insurance required',
            body: 'FEMA Zone X means this property sits outside the 100-year flood plain. No mandatory flood insurance policy saves you hundreds to thousands per year in carrying costs.' }
        : { key, type: 'risk', stat: `Zone ${p.floodZone}`, statLabel: 'FEMA Flood',
            title: 'Flood insurance is mandatory and will eat into your returns',
            body: `Zone ${p.floodZone} requires lender-mandated flood insurance. Get a flood insurance quote before committing — factor the annual premium into your cash flow model.` };

    case 'hazardRiskZone':
      if (p.hazardRiskZone == null) return null;
      return type === 'strength'
        ? { key, type, stat: p.hazardRiskZone, statLabel: 'FEMA Hazard',
            title: 'Low natural hazard risk protects long-term ownership stability',
            body: 'Low FEMA risk scores correlate with lower insurance premiums and fewer weather-related disruptions. This factor quietly compounds in your favor over a long hold period.' }
        : { key, type, stat: p.hazardRiskZone, statLabel: 'FEMA Hazard',
            title: 'Elevated hazard risk inflates insurance and damages your NOI',
            body: `${p.hazardRiskZone} hazard classification will drive up homeowners insurance costs. Request insurance quotes before closing and stress-test your returns with higher premium scenarios.` };

    case 'medianHouseholdIncome':
      if (n.medianHouseholdIncome == null) return null;
      return type === 'strength'
        ? { key, type, stat: fmtMoney(n.medianHouseholdIncome), statLabel: 'Median Income',
            title: 'High neighborhood income supports strong rent collection',
            body: `At ${fmtMoney(n.medianHouseholdIncome)} median household income, tenants in this area are financially stable. This reduces delinquency risk and supports above-market rents.` }
        : { key, type, stat: fmtMoney(n.medianHouseholdIncome), statLabel: 'Median Income',
            title: 'Below-average income limits the rent you can realistically charge',
            body: `${fmtMoney(n.medianHouseholdIncome)} median household income constrains affordability. Model your rent at no more than 30% of median income to maintain stable occupancy.` };

    case 'unemploymentRate':
      if (n.unemploymentRate == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${n.unemploymentRate.toFixed(1)}%`, statLabel: 'Unemployment',
            title: 'Low unemployment signals a healthy, resilient local economy',
            body: `${n.unemploymentRate.toFixed(1)}% unemployment indicates a strong local labor market. Employed tenants pay rent — this is a fundamental driver of rental income reliability.` }
        : { key, type, stat: `${n.unemploymentRate.toFixed(1)}%`, statLabel: 'Unemployment',
            title: 'High unemployment increases your vacancy and collection risk',
            body: `At ${n.unemploymentRate.toFixed(1)}% unemployment, build a larger cash reserve buffer. Screen tenants rigorously and consider shorter lease terms to maintain flexibility.` };

    case 'schoolRatings':
      if (n.schoolRatings == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${n.schoolRatings.toFixed(1)} / 4.3`, statLabel: 'School Rating',
            title: 'Top-rated schools drive long-term appreciation and tenant demand',
            body: 'Families actively pay a premium to live in strong school districts — and they stay longer. This is one of the most durable drivers of property value appreciation over a 5–10 year hold.' }
        : { key, type, stat: `${n.schoolRatings.toFixed(1)} / 4.3`, statLabel: 'School Rating',
            title: 'Weak school ratings narrow your tenant profile',
            body: 'Below-average schools will limit demand from family tenants. Pivot your marketing strategy toward young professionals, retirees, or students who are indifferent to school quality.' };

    case 'crimeStatistics':
      if (n.crimeStatistics == null) return null;
      return type === 'strength'
        ? { key, type,
            title: 'Low crime supports tenant retention and property condition',
            body: 'Safe neighborhoods experience less vacancy, less property damage, and attract higher-quality tenants. This is a compounding advantage over a long hold period.' }
        : { key, type,
            title: 'Elevated crime increases turnover, damage, and insurance costs',
            body: 'Higher crime areas require more active management, stronger tenant screening, and better property security. Model a higher vacancy rate and maintenance budget into your underwriting.' };

    case 'homeownershipRate':
      if (n.homeownershipRate == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${n.homeownershipRate.toFixed(0)}%`, statLabel: 'Homeownership',
            title: 'Owner-occupied neighborhood means neighbors invest in upkeep',
            body: `${n.homeownershipRate.toFixed(0)}% homeownership rate indicates a stable, maintained neighborhood. This protects your property value and reduces the risk of neighborhood decline over your hold period.` }
        : { key, type, stat: `${n.homeownershipRate.toFixed(0)}%`, statLabel: 'Homeownership',
            title: 'Renter-dominated area increases turnover and maintenance costs',
            body: `With ${n.homeownershipRate.toFixed(0)}% homeownership, expect higher tenant churn in the surrounding area. Price competitively, maintain the property well, and budget for more frequent unit turns.` };

    case 'populationGrowth':
      if (m.populationGrowth == null) return null;
      const growthStr = `${m.populationGrowth > 0 ? '+' : ''}${m.populationGrowth.toFixed(1)}%`;
      return type === 'strength'
        ? { key, type, stat: growthStr, statLabel: 'Pop. Growth (4yr)',
            title: 'Growing population creates compounding demand for housing',
            body: `${growthStr} population growth over 4 years means more households competing for housing. This structural tailwind supports both rent increases and property value appreciation over your hold period.` }
        : { key, type, stat: growthStr, statLabel: 'Pop. Growth (4yr)',
            title: 'Population decline will suppress future rent growth and appreciation',
            body: `${growthStr} population growth indicates shrinking demand. If you proceed, target a shorter hold period and lock in long-term leases early to protect income stability.` };

    case 'medianHomeValue':
      if (m.medianHomeValue == null) return null;
      return type === 'strength'
        ? { key, type, stat: fmtMoney(m.medianHomeValue), statLabel: 'Median Home Value',
            title: 'Home values sit in the ideal appreciation range',
            body: `${fmtMoney(m.medianHomeValue)} median value is in the sweet spot — affordable enough for broad buyer demand, high enough to signal an established market. This supports both resale liquidity and continued appreciation.` }
        : { key, type, stat: fmtMoney(m.medianHomeValue), statLabel: 'Median Home Value',
            title: 'Home values signal limited upside or affordability pressure',
            body: `At ${fmtMoney(m.medianHomeValue)}, model your appreciation expectations conservatively. Focus your returns on cash flow rather than price appreciation in your underwriting.` };

    case 'homePriceAppreciationRate':
      if (m.homePriceAppreciationRate == null) return null;
      return type === 'strength'
        ? { key, type, stat: `$${m.homePriceAppreciationRate.toFixed(0)}/sqft`, statLabel: 'Price per Sq Ft',
            title: 'Competitive price-per-sq-ft signals strong market demand',
            body: `At $${m.homePriceAppreciationRate.toFixed(0)}/sq ft, this property reflects healthy market demand. Strong price density typically correlates with faster sales and more competitive offers when you exit.` }
        : { key, type, stat: `$${m.homePriceAppreciationRate.toFixed(0)}/sqft`, statLabel: 'Price per Sq Ft',
            title: 'Low price per sq ft may reflect weak demand or oversupply',
            body: `$${m.homePriceAppreciationRate.toFixed(0)}/sq ft is below typical healthy market ranges. Investigate whether this reflects a buying opportunity or a sign of structural market weakness before proceeding.` };

    case 'daysOnMarket':
      if (m.daysOnMarket == null) return null;
      return type === 'strength'
        ? { key, type, stat: `${m.daysOnMarket} days`, statLabel: 'Avg Days on Market',
            title: 'Fast-moving market validates strong buyer and renter demand',
            body: `Properties here sell in ${m.daysOnMarket} days on average — a sign of competitive, liquid demand. Move decisively when you find the right property. Hesitation is costly in this market.` }
        : { key, type, stat: `${m.daysOnMarket} days`, statLabel: 'Avg Days on Market',
            title: `Slow market (${m.daysOnMarket} days) gives you negotiating leverage`,
            body: `With an average of ${m.daysOnMarket} days on market, sellers are motivated. Use extended market time as justification to push the purchase price down 3–5% below asking. The data supports a lower offer.` };

    case 'rentPrices':
      if (m.rentPrices == null) return null;
      return type === 'strength'
        ? { key, type, stat: fmtMoney(m.rentPrices), statLabel: 'Rent AVM Est.',
            title: 'Strong rental market supports reliable cash flow',
            body: `At ${fmtMoney(m.rentPrices)} estimated rent, this market supports healthy yields. Run your cash-on-cash return model at 90% occupancy to stress-test the income before committing.` }
        : { key, type, stat: fmtMoney(m.rentPrices), statLabel: 'Rent AVM Est.',
            title: 'Below-average rents will compress your yield',
            body: `${fmtMoney(m.rentPrices)} estimated rent limits your income potential. Model cash flow conservatively — any vacancy or repair expense will significantly impact your return in a low-rent market.` };

    default:
      return null;
  }
}

// ── Big Idea generation ───────────────────────────────────────────────────────

function getBigIdea(score: number, label: string, strengths: Insight[], risks: Insight[]): { headline: string; sub: string } {
  const topStrength = strengths[0];
  const topRisk     = risks[0];

  if (score >= 80) {
    return {
      headline: `Strong investment case${topStrength ? ` — ${topStrength.title.toLowerCase()}` : ''}`,
      sub: topRisk
        ? `Your priority factors score well overall. Your most significant watch item is ${ATTR_LABELS[topRisk.key]?.toLowerCase() ?? 'a key risk factor'} — address it in due diligence to protect your returns.`
        : 'Fundamentals align across your priority factors. Act decisively — properties with profiles like this tend to move quickly.',
    };
  }
  if (score >= 65) {
    return {
      headline: 'Solid potential with addressable risks',
      sub: topRisk
        ? `This property has real merit, but ${ATTR_LABELS[topRisk.key]?.toLowerCase() ?? 'a key factor'} is working against you. Negotiate accordingly and factor the downside into your underwriting.`
        : 'Most of your priority factors are favorable. Run a thorough inspection and model conservative cash flow assumptions before committing.',
    };
  }
  if (score >= 50) {
    return {
      headline: 'Moderate opportunity — proceed with caution and a lower offer',
      sub: topRisk
        ? `${ATTR_LABELS[topRisk.key] ?? 'A key factor'} is your biggest drag. Use the data to justify an aggressive offer — the numbers need to work harder here to deliver an acceptable return.`
        : 'Multiple factors are underperforming. Ensure your purchase price leaves enough margin to absorb risk and still hit your return targets.',
    };
  }
  return {
    headline: 'Significant risk factors identified — due diligence is critical',
    sub: topRisk
      ? `${ATTR_LABELS[topRisk.key] ?? 'Key factors'} present material risk. If you proceed, require a substantial price discount, commission all relevant inspections, and stress-test every assumption in your model.`
      : 'The current data does not support a confident investment thesis. Consider alternative properties or wait for more favorable conditions.',
  };
}

// ── Lookup for labels ─────────────────────────────────────────────────────────

const ATTR_LABELS: Record<string, string> = {
  yearBuilt: 'Year Built', squareFootage: 'Square Footage', numBedrooms: 'Bedrooms',
  numBathrooms: 'Bathrooms', numFloors: 'Floors', constructionType: 'Construction Type',
  roofType: 'Roof Type', foundationType: 'Foundation Type', floodZone: 'Flood Zone',
  hazardRiskZone: 'Hazard Risk', medianHouseholdIncome: 'Median Income',
  unemploymentRate: 'Unemployment Rate', schoolRatings: 'School Ratings',
  crimeStatistics: 'Crime Index', homeownershipRate: 'Homeownership Rate',
  populationGrowth: 'Population Growth', medianHomeValue: 'Median Home Value',
  homePriceAppreciationRate: 'Price per Sq Ft', daysOnMarket: 'Days on Market',
  rentPrices: 'Rent Prices',
};

// ── UI Components ─────────────────────────────────────────────────────────────

function ScoreDial({ score, label }: { score: number; label: string }) {
  const colors = score >= 80 ? { ring: '#0a7c42', text: 'text-positive', bg: 'bg-positive-bg' }
               : score >= 65 ? { ring: '#1d6fdb', text: 'text-accent',   bg: 'bg-accent-light' }
               : score >= 50 ? { ring: '#b45309', text: 'text-warning',  bg: 'bg-warning-bg' }
               :               { ring: '#c0392b', text: 'text-danger',   bg: 'bg-danger-bg' };
  const circumference = 2 * Math.PI * 54;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="flex flex-col items-center shrink-0">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="none" stroke="#e2e6ec" strokeWidth="10" />
          <circle cx="60" cy="60" r="54" fill="none" stroke={colors.ring} strokeWidth="10"
            strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset}
            className="transition-all duration-700 ease-out" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-extrabold ${colors.text}`}>{score.toFixed(0)}</span>
          <span className="text-xs text-ink-light font-medium">/ 100</span>
        </div>
      </div>
      <div className={`mt-2 px-3 py-1 rounded-full text-xs font-bold ${colors.bg} ${colors.text}`}>
        {label}
      </div>
    </div>
  );
}

function InsightCard({ insight }: { insight: Insight }) {
  const isStrength = insight.type === 'strength';
  const isCaution  = insight.type === 'caution';

  const style = isStrength
    ? { border: 'border-l-positive',  iconBg: 'bg-positive-bg',  iconColor: 'text-positive',  badge: 'bg-positive-bg text-positive border-positive/20' }
    : isCaution
    ? { border: 'border-l-warning',   iconBg: 'bg-warning-bg',   iconColor: 'text-warning',   badge: 'bg-warning-bg text-warning border-warning/20' }
    : { border: 'border-l-danger',    iconBg: 'bg-danger-bg',    iconColor: 'text-danger',     badge: 'bg-danger-bg text-danger border-danger/20' };

  return (
    <div className={`bg-white border border-border border-l-4 ${style.border} rounded-lg p-5`}>
      <div className="flex items-start gap-3">
        <div className={`w-8 h-8 rounded-lg ${style.iconBg} flex items-center justify-center shrink-0 mt-0.5`}>
          {isStrength
            ? <svg className={style.iconColor} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            : isCaution
            ? <svg className={style.iconColor} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="9" x2="12" y2="13"/><circle cx="12" cy="12" r="10"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            : <svg className={style.iconColor} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
          }
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-ink leading-snug mb-1">{insight.title}</p>
          <p className="text-xs text-ink-mid leading-relaxed">{insight.body}</p>
          {insight.stat && (
            <div className="mt-3 inline-flex items-baseline gap-1.5">
              <span className={`text-xl font-extrabold ${style.iconColor}`}>{insight.stat}</span>
              {insight.statLabel && <span className="text-xs text-ink-light font-medium">{insight.statLabel}</span>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ label, score, weight }: { label: string; score: number; weight: number }) {
  const color = score >= 0.65 ? 'bg-positive' : score >= 0.40 ? 'bg-warning' : 'bg-danger';
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
      <span className="text-xs text-ink-mid w-44 shrink-0">{label}</span>
      <div className="flex-1 h-2 rounded-full bg-slate-mid overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${score * 100}%` }} />
      </div>
      <span className="text-xs font-semibold text-ink w-10 text-right">{(score * 100).toFixed(0)}</span>
      <span className="text-[10px] text-ink-light w-12 text-right">{(weight * 100).toFixed(1)}% wt</span>
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyState({ onGoSimulate }: { onGoSimulate: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center fade-up">
      <div className="w-14 h-14 rounded-full bg-accent-light flex items-center justify-center mb-5">
        <svg className="text-accent" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>
      </div>
      <h3 className="text-lg font-bold text-navy mb-2">No simulation run yet</h3>
      <p className="text-sm text-ink-mid max-w-sm leading-relaxed mb-6">
        Head over to <strong>Investor Simulator</strong>, rate each factor by importance,
        then click <strong>Run Simulation</strong> to generate your personalized investment report.
      </p>
      <button onClick={onGoSimulate}
        className="bg-navy text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-navy-light transition-colors text-sm">
        Go to Investor Simulator →
      </button>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

interface Props {
  data:         EnrichResponse;
  scoreResult:  ScoreResult | null;
  onGoSimulate: () => void;
}

export default function InsightsTab({ data, scoreResult, onGoSimulate }: Props) {
  if (!scoreResult) return <EmptyState onGoSimulate={onGoSimulate} />;

  const { investmentScore, scoreLabel, variableScores, weights, weightedScores } = scoreResult;

  // Generate narrative insights for every scored variable
  const allInsights: Insight[] = Object.keys(variableScores)
    .map(key => generateInsight(key, variableScores[key], data))
    .filter((x): x is Insight => x !== null);

  // Sort by weighted score desc so the most impactful appear first
  allInsights.sort((a, b) => (weightedScores[b.key] ?? 0) - (weightedScores[a.key] ?? 0));

  const strengths = allInsights.filter(i => i.type === 'strength').slice(0, 4);
  const risks     = allInsights.filter(i => i.type === 'risk' || i.type === 'caution').slice(0, 4);
  const bigIdea   = getBigIdea(investmentScore, scoreLabel, strengths, risks);

  // Sorted variable list for compact breakdown
  const sortedVars = Object.keys(variableScores).sort(
    (a, b) => (weightedScores[b] ?? 0) - (weightedScores[a] ?? 0),
  );

  const scoredVars  = sortedVars.length;
  const totalVars   = Object.keys(weights).length;
  const coveragePct = totalVars > 0 ? Math.round((scoredVars / totalVars) * 100) : 0;

  // Score color for recommendation box
  const recStyle = investmentScore >= 80 ? 'bg-positive-bg border-positive/20 text-positive'
                 : investmentScore >= 65 ? 'bg-accent-light border-accent/20 text-accent'
                 : investmentScore >= 50 ? 'bg-warning-bg border-warning/20 text-warning'
                 :                         'bg-danger-bg border-danger/20 text-danger';

  return (
    <div className="space-y-6 fade-up">

      {/* ── 1. The Big Idea ── */}
      <div className="rounded-xl text-white px-7 py-6"
        style={{ background: 'linear-gradient(135deg, #0f2342 0%, #1a3a6b 100%)' }}>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <ScoreDial score={investmentScore} label={scoreLabel} />
          <div className="flex-1">
            <div className="text-xs text-blue-200 uppercase tracking-widest font-semibold mb-2">
              Investment Analysis
            </div>
            <h2 className="text-xl font-extrabold text-white leading-snug mb-3 capitalize">
              {bigIdea.headline}
            </h2>
            <p className="text-sm text-blue-200 leading-relaxed">{bigIdea.sub}</p>
            <div className="mt-4 flex items-center gap-4 text-xs text-blue-300">
              <span>{scoredVars} of {totalVars} variables scored</span>
              <span>·</span>
              <span>{coveragePct}% data coverage</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── 2. Strengths & Risks side-by-side ── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">

        {/* Strengths */}
        {strengths.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-positive" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-ink-mid">
                Working in Your Favor
              </h3>
            </div>
            <div className="space-y-3">
              {strengths.map(i => <InsightCard key={i.key} insight={i} />)}
            </div>
          </div>
        )}

        {/* Risks */}
        {risks.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-danger" />
              <h3 className="text-xs font-bold uppercase tracking-widest text-ink-mid">
                Risks That Demand Action
              </h3>
            </div>
            <div className="space-y-3">
              {risks.map(i => <InsightCard key={i.key} insight={i} />)}
            </div>
          </div>
        )}

      </div>

      {/* ── 3. Score Breakdown ── */}
      <div className="bg-white border border-border rounded-lg overflow-hidden">
        <div className="flex items-center gap-3 px-5 py-3.5 border-b border-border">
          <div className="w-1 h-4 rounded-full bg-accent" />
          <h2 className="text-xs font-bold uppercase tracking-widest text-ink-mid">
            Full Score Breakdown — by Weighted Impact
          </h2>
        </div>
        <div className="px-5 py-1">
          {sortedVars.map(key => (
            <ScoreBar
              key={key}
              label={ATTR_LABELS[key] ?? key}
              score={variableScores[key]}
              weight={weights[key]}
            />
          ))}
        </div>
      </div>

      {/* ── 4. Recommendation ── */}
      <div className={`border rounded-xl px-6 py-5 ${recStyle}`}>
        <div className="text-xs font-bold uppercase tracking-widest mb-2 opacity-70">
          Bottom Line
        </div>
        <p className="text-sm font-semibold leading-relaxed">
          {investmentScore >= 80 && 'The data supports a confident move. Proceed to offer stage, use any risk factors identified above as negotiating points, and lock in financing quickly.'}
          {investmentScore >= 65 && investmentScore < 80 && 'Proceed with targeted due diligence. Address the risks flagged above before committing — negotiate price concessions for any unresolved concerns.'}
          {investmentScore >= 50 && investmentScore < 65 && 'This deal requires a discount to work. Use the risk factors above to justify a lower offer and ensure your return targets survive a stress test.'}
          {investmentScore < 50 && 'Current fundamentals do not support a confident investment thesis at market price. Either negotiate aggressively or direct capital to a stronger opportunity.'}
        </p>
      </div>

    </div>
  );
}
