export default function GoldRule({ width = 48 }) {
  return (
    <div style={{
      width, height: '1px',
      background: 'linear-gradient(90deg, var(--gold), transparent)',
      margin: '16px 0 32px',
    }} />
  );
}
