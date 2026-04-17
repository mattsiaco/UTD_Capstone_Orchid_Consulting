'use client';

import { useState } from 'react';
import SearchBar from '@/components/SearchBar';
import LoadingSteps from '@/components/LoadingSteps';
import ResultsDashboard from '@/components/ResultsDashboard';
import { EnrichResponse } from '@/components/types';

export default function Home() {
  const [address,         setAddress]         = useState('');
  const [searchedAddress, setSearchedAddress] = useState('');
  const [loading,         setLoading]         = useState(false);
  const [error,           setError]           = useState<string | null>(null);
  const [results,         setResults]         = useState<EnrichResponse | null>(null);

  async function handleSearch(addr: string) {
    const trimmed = addr.trim();
    if (!trimmed) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setSearchedAddress(trimmed);

    try {
      const res  = await fetch('/api/enrich', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ address: trimmed }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? 'Failed to fetch property data');
      setResults(data as EnrichResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not connect — is the API server running?');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Header */}
      <header className="bg-white border-b border-border px-8 py-3.5 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-2 font-bold text-lg text-navy">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Orchid Consulting Property Investment App
        </div>
        <div className="flex items-center gap-6 text-sm text-ink-mid">
          <span className="hidden sm:inline text-xs bg-accent-light text-accent font-semibold px-2.5 py-1 rounded">
          </span>
        </div>
      </header>

      {/* Hero */}
      <div className="border-b border-border" style={{ background: 'linear-gradient(135deg, #0f2342 0%, #1a3a6b 100%)' }}>
        <div className="max-w-3xl mx-auto px-6 py-16 text-center">
          <div className="inline-flex items-center gap-2 text-xs font-semibold text-blue-200 bg-white/10 px-3 py-1.5 rounded-full mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-300 inline-block" />
            Sourced by ATTOM · Census · FEMA · RentCast
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight mb-3">
            Property Investment Analysis
          </h1>
          <p className="text-blue-200 text-base mb-8 max-w-xl mx-auto">
            Enter any U.S. property address to instantly pull property records, neighborhood demographics, flood risk, and live market data.
          </p>
          <SearchBar
            value={address}
            onChange={setAddress}
            onSearch={handleSearch}
            loading={loading}
          />
          <p className="text-xs text-blue-300/70 mt-3">
          </p>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="max-w-2xl mx-auto px-6 mt-8">
          <div className="bg-danger-bg border border-danger/20 text-danger text-sm px-5 py-3.5 rounded-lg">
            {error}
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSteps />}

      {/* Results */}
      {results && !loading && (
        <ResultsDashboard address={searchedAddress} data={results} />
      )}

      {/* Empty state */}
      {!loading && !results && !error && (
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {[
              { title: 'Property Records',    body: 'Year built, sq footage, bedrooms, bathrooms, roof type, foundation, and more from ATTOM.',                                         bar: 'bg-accent' },
              { title: 'Neighborhood Data',   body: 'Median income, unemployment, homeownership rate, and school ratings from the U.S. Census.',                                        bar: 'bg-[#7c3aed]' },
              { title: 'Market Intelligence', body: 'Days on market, home values, price per sq ft, zoning, and flood risk for informed decisions.',                                     bar: 'bg-positive' },
            ].map(card => (
              <div key={card.title} className="bg-white border border-border rounded-lg p-6">
                <div className={`w-10 h-1 ${card.bar} rounded mb-4`} />
                <h3 className="font-semibold text-navy mb-2">{card.title}</h3>
                <p className="text-sm text-ink-mid leading-relaxed">{card.body}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
