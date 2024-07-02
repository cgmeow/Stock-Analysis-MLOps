import React from "react";
import "./graph.css";
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

// Register the required components for Chart.js
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

class Graph extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            data: {
                labels: [], // Labels for x-axis
                datasets: [
                    {
                        label: '',
                        data: [],
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    },
                    {
                        label: '(Predicted)',
                        data: [],
                        fill: false,
                        borderColor: 'rgb(255, 99, 132)', // Red color for predicted data
                        tension: 0.1
                    }
                ]
            }
        };

        this.options = {
            scales: {
                x: {
                    type: 'category',
                    ticks: {
                        color: 'white',
                         // Set x-axis label color to white
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'white', // Set y-axis label color to white
                    },
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Stock Price', // Title text
                    color: 'white', // Title color
                    font: {
                        size: 20, // Title font size
                    }
                },
                tooltip: {
                    titleColor: 'white', // Tooltip title color
                    bodyColor: 'white', // Tooltip body text color
                },
                legend: {
                    labels: {
                        color: 'white', // Legend label color
                    }
                }
            }
        };
    }

    componentDidMount() {
        // Initial update of chart data
        this.updateChartData(this.props.stockData, this.props.stockName);
    }

    componentDidUpdate(prevProps) {
        // Check if stockData or stockName props have changed
        if (prevProps.stockData !== this.props.stockData || prevProps.stockName !== this.props.stockName) {
            this.updateChartData(this.props.stockData, this.props.stockName);
        }
    }

    updateChartData = (stockData, stockName) => {
        if (!stockData || stockData.length === 0) {
            return;
        }

        // Separate historical data and predicted data based on "Inference" key
        const historicalData = stockData.filter(item => item.Inference !== "Y");
        const predictedData = stockData.filter(item => item.Inference === "Y");

        // Extract labels and data for historical data
        const historicalLabels = historicalData.map(item => item.Date);
        const historicalClose = historicalData.map(item => item.Close);

        // Extract labels and data for predicted data
        const predictedLabels = predictedData.map(item => item.Date);
        const predictedClose = predictedData.map(item => item.Close);

        // Merge all labels (historical and predicted)
        const allLabels = [...historicalLabels, ...predictedLabels];

        // Update the dataset
        this.setState({
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: stockName,
                        data: [...historicalClose, ...Array(predictedLabels.length).fill(null)], // Fill historical data with null for predicted labels
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    },
                    {
                        label: `${stockName} (Predicted)`,
                        data: [...Array(historicalLabels.length).fill(null), ...predictedClose], // Fill predicted data with null for historical labels
                        fill: false,
                        borderColor: 'rgb(255, 99, 132)', // Red color for predicted data
                        tension: 0.1
                    }
                ]
            }
        });
    };

    render() {
        return (
            <div className="graph"> 
                <Line data={this.state.data} options={this.options} />
            </div>
        );
    }
}

export default Graph;
