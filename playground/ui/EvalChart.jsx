import React, { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export default function EvalChart({ promptId, timeRange = '30d' }) {
  const [evals, setEvals] = useState([]);
  const [chartType, setChartType] = useState('bar');
  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    averageScore: 0,
    totalEvaluations: 0,
    bestPerforming: null,
    trend: 'stable'
  });

  useEffect(() => {
    fetchEvaluations();
  }, [promptId, timeRange]);

  const fetchEvaluations = async () => {
    setIsLoading(true);
    try {
      const url = promptId 
        ? `/api/evals/chart/${promptId}?range=${timeRange}`
        : `/api/evals/chart?range=${timeRange}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      setEvals(data.evals || []);
      setMetrics(data.metrics || metrics);
    } catch (error) {
      console.error('Error fetching evaluations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const chartData = {
    labels: evals.map(e => e.prompt_name || new Date(e.created_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Evaluation Score',
        data: evals.map(e => e.score),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
        fill: chartType === 'line' ? false : true
      },
      {
        label: 'Pass Rate %',
        data: evals.map(e => e.pass_rate * 100),
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 2,
        yAxisID: 'y1'
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: promptId ? `Evaluations for Prompt ${promptId}` : 'All Prompt Evaluations'
      }
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        min: 0,
        max: 10,
        title: {
          display: true,
          text: 'Score (0-10)'
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        min: 0,
        max: 100,
        title: {
          display: true,
          text: 'Pass Rate (%)'
        },
        grid: {
          drawOnChartArea: false
        }
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Evaluation Analytics</h2>
        <div className="flex gap-2">
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => window.location.search = `?range=${e.target.value}`}
            className="px-3 py-1 border border-gray-300 rounded text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{metrics.averageScore.toFixed(1)}</div>
          <div className="text-sm text-blue-800">Average Score</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{metrics.totalEvaluations}</div>
          <div className="text-sm text-green-800">Total Evaluations</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {metrics.bestPerforming?.score || 'N/A'}
          </div>
          <div className="text-sm text-purple-800">Best Score</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600 capitalize">{metrics.trend}</div>
          <div className="text-sm text-yellow-800">Trend</div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-96">
        {evals.length > 0 ? (
          chartType === 'bar' ? (
            <Bar data={chartData} options={chartOptions} />
          ) : (
            <Line data={chartData} options={chartOptions} />
          )
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-lg font-medium mb-2">No evaluation data</h3>
            <p className="text-sm">Run some prompt evaluations to see analytics here</p>
          </div>
        )}
      </div>

      {/* Recent Evaluations Table */}
      {evals.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Recent Evaluations</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prompt
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pass Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {evals.slice(0, 5).map(evaluation => (
                  <tr key={evaluation.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {evaluation.prompt_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        evaluation.score >= 8 ? 'bg-green-100 text-green-800' :
                        evaluation.score >= 6 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {evaluation.score}/10
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(evaluation.pass_rate * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(evaluation.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}