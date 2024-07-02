import React from 'react';
import Navbar from '../Navbar/navbar';
import UserForm from '../UserInput/userinput';
import Cards from '../Cards/card';
import Graph from '../Graph/graph';
import axios from 'axios';
import './dashboard.css'; // Import the CSS file for Dashboard styles
import NewsTracker from '../NewsTicker/newsticker';

class Dashboard extends React.Component {
  constructor(props) {
    super(props);

    const today = new Date();
    const eightMonthsAgo = new Date(today.getFullYear(), today.getMonth() - 8, today.getDate());

    this.state = {
      stockName: localStorage.getItem('selectedStock') || 'AMD', // Initialize with stored value or default 'AMD'
      startDate: localStorage.getItem('startDate') || eightMonthsAgo.toISOString().substr(0, 10), // Initialize with stored value or default eight months ago
      endDate: localStorage.getItem('endDate') || today.toISOString().substr(0, 10), // Initialize with stored value or default today
      stockData: [],
      currentOpenPrice: '',
      currentClosePrice: '',
      currentLowPrice: '',
      currentHighPrice: '',
      newsSentiment:'',
    };

    console.log(this.state.endDate);

    this.handleStockNameChange = this.handleStockNameChange.bind(this);
    this.handleStartDateChange = this.handleStartDateChange.bind(this);
    this.handleEndDateChange = this.handleEndDateChange.bind(this);
  }

  handleStockNameChange = (stockName) => {
    this.setState({ stockName }, () => {
      localStorage.setItem('selectedStock', stockName); // Save selected stock name to localStorage
      this.fetchStockData(stockName, this.state.startDate, this.state.endDate);
    });
  };

  handleStartDateChange = (startDate) => {
    this.setState({ startDate }, () => {
      localStorage.setItem('startDate', startDate); // Save selected start date to localStorage
      this.fetchStockData(this.state.stockName, startDate, this.state.endDate);
    });
  };

  handleEndDateChange = (endDate) => {
    this.setState({ endDate }, () => {
      localStorage.setItem('endDate', endDate); // Save selected end date to localStorage
      this.fetchStockData(this.state.stockName, this.state.startDate, endDate);
    });
  };

  componentDidMount() {
    this.fetchStockData(this.state.stockName, this.state.startDate, this.state.endDate);
  }

  fetchStockData = async (stockName, startDate, endDate) => {
    const formattedStartDate = new Date(startDate).toLocaleDateString('en-GB');
    const formattedEndDate = new Date(endDate).toLocaleDateString('en-GB');

    // First API call to update stockData
    const firstApiBody = {
      stock: stockName,
      s3_bucket_name: 'webscrape-bucket-mle611',
      source_file: 'stock_price_consolidated.csv',
      date_range: [formattedStartDate, formattedEndDate],
      inference_bucket: 'webscrape-bucket-mle611',
      inference_key: 'Inference_Finance_Consoliated.csv'
    };

    try {
      const response1 = await axios.post(
        'https://kkpa7x2an0.execute-api.ap-southeast-1.amazonaws.com/Dev/Yahoo-Finance-Data',
        firstApiBody,
        {
          headers: {
            // 'Access-Control-Request-Method': 'POST',
            // 'Access-Control-Request-Headers': 'Content-Type',
          }
        }
      );

      const stockData = JSON.parse(response1.data.body);

      //console.log(stockData)

      // Second API call to update open, close, high, low
      const secondApiBody = {
        stock: stockName,
        s3_bucket_name: 'webscrape-bucket-mle611',
        source_file: 'stock_price_consolidated.csv'
      };

      const response2 = await axios.post(
        'https://kkpa7x2an0.execute-api.ap-southeast-1.amazonaws.com/Dev/Yahoo-Finance-Data',
        secondApiBody,
        {
          headers: {
            // 'Access-Control-Request-Method': 'POST',
            // 'Access-Control-Request-Headers': 'Content-Type',
          }
        }
      );

      const latestStockData = JSON.parse(response2.data.body)[0]; // Assuming response2.data.body contains a single object

    
      const thirdApiBody = {
        stock: stockName,
        s3_bucket_name: 'mle-project',
        source_file: 'SA_model_'
      };

      const response3 = await axios.post(
        'https://ileg8qjl28.execute-api.ap-southeast-1.amazonaws.com/Dev/',
        thirdApiBody,
        {
          // headers: {
          //    'Access-Control-Request-Method': 'POST',
          //    'Access-Control-Request-Headers': 'Content-Type',
          // }
        }
      );

      const newsSentiment = JSON.parse(response3.data.body);

      //console.log(newsSentiment[0].Sentiment)

      this.setState({
        stockData,
        currentClosePrice: latestStockData.Close,
        currentOpenPrice: latestStockData.Open,
        currentHighPrice: latestStockData.High,
        currentLowPrice: latestStockData.Low,
        newsSentiment: newsSentiment[0].Sentiment
      });
      


    } catch (error) {
      console.error('Error fetching stock data:', error);
    }
  };

  render() {
    const { userData } = this.state;

    return (
      <div className="dashboard-container">
        <Navbar userData={userData} />
        <div className="dashboard-content">
          <div className="dashboard-header" style={{ color: 'white', marginTop: '0rem', marginLeft: '5rem' }}>
            <h4>
              <b>Stock Dashboard for {this.state.stockName}</b>
            </h4>
            <UserForm
              stockName={this.state.stockName}
              startDate={this.state.startDate}
              endDate={this.state.endDate}
              onStockNameChange={this.handleStockNameChange}
              onStartDateChange={this.handleStartDateChange}
              onEndDateChange={this.handleEndDateChange}
            />
          </div>
          <Cards open={this.state.currentOpenPrice} close={this.state.currentClosePrice} low={this.state.currentLowPrice} high={this.state.currentHighPrice} sentiment={this.state.newsSentiment}/>
          <div className="dashboard-graph">
            <Graph stockData={this.state.stockData} stockName={this.state.stockName} />
          </div>
          <div className="dashboard-news">
            <NewsTracker stockName={this.state.stockName} startDate={this.state.startDate} endDate={this.state.endDate} />
          </div>
        </div>
      </div>
    );
  }
}

export default Dashboard;
