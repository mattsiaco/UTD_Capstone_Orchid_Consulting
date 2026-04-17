'use client';

import { useEffect, useState } from 'react';

const STEPS = [
  { label: 'ATTOM',    detail: 'Property records & building data'   },
  { label: 'FEMA',     detail: 'Flood zone & hazard risk index'     },
  { label: 'Census',   detail: 'Demographics & income data'         },
  { label: 'RentCast', detail: 'Market activity & days on market'   },
  { label: 'ArcGIS',   detail: 'Zoning & land use'                  },
];

const DELAYS = [0, 700, 1200, 1700, 2200];

export default function LoadingSteps() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const timers = DELAYS.map((delay, i) =>
      setTimeout(() => setActiveIndex(i), delay)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="max-w-md mx-auto px-6 py-16 text-center">
      <div className="spinner mx-auto mb-6" />
      <p className="text-sm font-medium text-ink mb-1">Pulling property data</p>
      <p className="text-xs text-ink-light mb-8">Querying {STEPS.length} data sources simultaneously</p>

      <div className="text-left space-y-2">
        {STEPS.map((step, i) => {
          const done   = i < activeIndex;
          const active = i === activeIndex;
          return (
            <div key={step.label} className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-300 ${
              active ? 'bg-accent-light' : ''
            }`}>
              <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                done   ? 'bg-positive border-positive' :
                active ? 'border-accent bg-white'      :
                         'border-border bg-white'
              }`}>
                {done && (
                  <svg width="10" height="10" fill="none" stroke="white" strokeWidth="2.5" viewBox="0 0 12 12">
                    <polyline points="2,6 5,9 10,3"/>
                  </svg>
                )}
                {active && <div className="w-2 h-2 rounded-full bg-accent" />}
              </div>
              <div>
                <div className={`text-sm font-semibold ${active ? 'text-accent' : done ? 'text-positive' : 'text-ink-light'}`}>
                  {step.label}
                </div>
                <div className="text-xs text-ink-light">{step.detail}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
