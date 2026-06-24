import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import dashboardData from './data/dashboard-data.json';

type LeaderboardRow = {
  skill: string;
  variant: string;
  runs: number;
  successes: number;
  success_rate_pct: number;
  success_distribution: number[];
  first_try_success_rate_pct: number;
  pass_at_k_pct: number;
  success_rate_stddev_pct: number;
  tokens_mean: number;
  tokens_distribution: number[];
  validated_confidence_mean: number;
  clarifications: number;
  corrections: number;
  contract_errors: number;
  safety_errors: number;
  api_contract_last_verified?: string | null;
};

type DashboardData = {
  metadata: {
    methodology: string;
    success_rate_note: string;
  };
  summary: {
    total_runs: number;
    skills: string[];
    variants: string[];
    contract_errors: number;
    safety_errors: number;
  };
  leaderboard: LeaderboardRow[];
};

const colors: Record<string, string> = {
  ai_kit: '#6ee7b7',
  docs: '#93c5fd',
  no_context: '#fbbf24',
  'Success rate': '#6ee7b7',
  'First try': '#93c5fd',
  'pass@k': '#a78bfa',
  Tokens: '#fbbf24',
  'Contract errors': '#f87171',
  'Safety errors': '#fb7185',
  Neutral: '#a1a1aa',
};

const data = dashboardData as DashboardData;

const outcomeRows = data.leaderboard.map((row) => ({
  name: formatVariant(row.variant),
  'Success rate': row.success_rate_pct,
  'First try': row.first_try_success_rate_pct,
  'pass@k': row.pass_at_k_pct,
}));

const tokenRows = data.leaderboard.map((row) => ({
  name: formatVariant(row.variant),
  Tokens: row.tokens_mean,
}));

const riskRows = data.leaderboard.map((row) => ({
  name: formatVariant(row.variant),
  'Contract errors': row.contract_errors,
  'Safety errors': row.safety_errors,
}));

function formatVariant(variant: string) {
  if (variant === 'ai_kit') return 'AI Kit';
  if (variant === 'docs') return 'Docs';
  if (variant === 'no_context') return 'No context';
  return variant;
}

function formatPercent(value: number) {
  return `${Number.isInteger(value) ? value : value.toFixed(1)}%`;
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <section className="stat-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </section>
  );
}

function ChartCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="chart-card">
      <header>
        <h2>{title}</h2>
        <p>{description}</p>
      </header>
      <div className="chart-body">{children}</div>
    </section>
  );
}

function ChartLegend({ items }: { items: string[] }) {
  return (
    <div className="chart-legend" aria-label="Chart legend">
      {items.map((item) => (
        <span key={item} className="legend-item">
          <span className="legend-swatch" style={{ background: colors[item] ?? colors.Neutral }} />
          {item}
        </span>
      ))}
    </div>
  );
}

function MetricBars({
  data,
  series,
  yMax,
  suffix = '',
}: {
  data: Array<Record<string, string | number>>;
  series: string[];
  yMax?: number;
  suffix?: string;
}) {
  return (
    <>
      <ChartLegend items={series} />
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 20, right: 16, left: 0, bottom: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.10)" />
          <XAxis dataKey="name" tick={{ fill: '#a1a1aa', fontSize: 12 }} />
          <YAxis domain={yMax ? [0, yMax] : undefined} tick={{ fill: '#a1a1aa', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: '#111318', border: '1px solid #2a2f3a', color: '#f4f4f5' }}
            formatter={(value) => [`${value}${suffix}`, '']}
          />
          {series.map((name) => (
            <Bar key={name} dataKey={name} fill={colors[name] ?? '#a78bfa'} radius={[4, 4, 0, 0]}>
              <LabelList
                dataKey={name}
                position="top"
                fill="#d4d4d8"
                fontSize={11}
                formatter={(value) => `${value ?? ''}${suffix}`}
              />
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </>
  );
}

function Distribution({ values }: { values: number[] }) {
  return (
    <div className="distribution" aria-label="Success distribution">
      {values.map((value, index) => (
        <span key={`${index}-${value}`} className={value ? 'dot pass' : 'dot fail'}>
          {value ? '1' : '0'}
        </span>
      ))}
    </div>
  );
}

export default function App() {
  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">AI Kit Evaluation</p>
          <h1>Xsolla AI Kit Skill Evals</h1>
          <p className="subtitle">
            Production-ready view for comparing AI Kit skills against docs and no-context baselines.
            The dashboard shows k-run distributions, pass@k, process metrics, and contract/safety errors.
          </p>
        </div>
      </section>

      <section className="stats-grid">
        <StatCard value={`${data.summary.total_runs}`} label="Total eval runs" />
        <StatCard value={`${data.summary.skills.length}`} label="Skills discovered" />
        <StatCard value={`${data.summary.contract_errors}`} label="Contract errors" />
        <StatCard value={`${data.summary.safety_errors}`} label="Safety errors" />
      </section>

      <section className="metrics">
        <h2>What we measure</h2>
        <div className="metric-list">
          <span>Success distribution over k runs</span>
          <span>First-try success</span>
          <span>pass@k</span>
          <span>Tokens to success</span>
          <span>Validated confidence</span>
          <span>Contract and safety errors</span>
        </div>
        <p className="muted">{data.metadata.success_rate_note}</p>
      </section>

      <section className="chart-grid">
        <ChartCard title="Outcome rates" description="Y-axis: percent. Compare first try, full distribution success, and pass@k.">
          <MetricBars data={outcomeRows} series={['Success rate', 'First try', 'pass@k']} yMax={100} suffix="%" />
        </ChartCard>

        <ChartCard title="Tokens to accepted result" description="Y-axis: estimated tokens per run. Lower is better.">
          <MetricBars data={tokenRows} series={['Tokens']} suffix=" tokens" />
        </ChartCard>

        <ChartCard title="Contract and safety errors" description="Y-axis: count. Target is zero for both metrics.">
          <MetricBars data={riskRows} series={['Contract errors', 'Safety errors']} />
        </ChartCard>
      </section>

      <section className="leaderboard">
        <header>
          <h2>Skill leaderboard</h2>
          <p className="muted">{data.metadata.methodology}</p>
        </header>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Skill</th>
                <th>Variant</th>
                <th>Runs</th>
                <th>Distribution</th>
                <th>Success</th>
                <th>First try</th>
                <th>pass@k</th>
                <th>Tokens</th>
                <th>Confidence</th>
                <th>Errors</th>
              </tr>
            </thead>
            <tbody>
              {data.leaderboard.map((row) => (
                <tr key={`${row.skill}-${row.variant}`}>
                  <td>{row.skill}</td>
                  <td>
                    <span className={`variant ${row.variant}`}>{formatVariant(row.variant)}</span>
                  </td>
                  <td>{row.runs}</td>
                  <td>
                    <Distribution values={row.success_distribution} />
                  </td>
                  <td>{formatPercent(row.success_rate_pct)}</td>
                  <td>{formatPercent(row.first_try_success_rate_pct)}</td>
                  <td>{formatPercent(row.pass_at_k_pct)}</td>
                  <td>{row.tokens_mean}</td>
                  <td>{formatPercent(row.validated_confidence_mean)}</td>
                  <td>
                    C {row.contract_errors} / S {row.safety_errors}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="decision">
        <h2>Deployment contract</h2>
        <p>
          This is a read-only mini-site. It uses static eval output from <code>dashboard-data.json</code>,
          no browser secrets, no external network calls, and relative Vite assets for
          <code> prototype.xsolla.dev/mini-apps/ai-kit-eval-dashboard</code>.
        </p>
      </section>
    </main>
  );
}
