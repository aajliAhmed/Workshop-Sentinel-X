import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function SensorChart({
  title,
  data,
  dataKey,
  unit,
}) {

  return (
    <div className="chart-container">

      <div className="chart-header">

        <h3>{title}</h3>

        <span>
          {unit}
        </span>

      </div>

      <ResponsiveContainer
        width="100%"
        height={260}
      >

        <LineChart data={data}>

          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#202838"
          />

          <XAxis
            dataKey="time"
            stroke="#8b93a7"
            tick={{ fontSize: 12 }}
          />

          <YAxis
            stroke="#8b93a7"
            tick={{ fontSize: 12 }}
          />

          <Tooltip
            contentStyle={{
              background: "#111621",
              border: "1px solid #202838",
              borderRadius: "8px",
              color: "#ffffff",
            }}
          />

          <Line
            type="monotone"
            dataKey={dataKey}
            stroke="#32d583"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 5 }}
          />

        </LineChart>

      </ResponsiveContainer>

    </div>
  );
}