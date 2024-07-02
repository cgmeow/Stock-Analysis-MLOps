import React, { Component } from 'react';
import axios from 'axios';
import './newsticker.css';

class NewsTicker extends Component {
  constructor(props) {
    super(props);
    this.state = {
      news: []
    };
  }

  componentDidMount() {
    this.fetchNews();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.stockName !== this.props.stockName ||
        prevProps.startDate !== this.props.startDate ||
        prevProps.endDate !== this.props.endDate) {
      this.fetchNews();
    }
  }

  fetchNews = async () => {
    const { stockName, startDate, endDate } = this.props;
    const formattedStartDate = new Date(startDate).toLocaleDateString('en-GB');
    const formattedEndDate = new Date(endDate).toLocaleDateString('en-GB');
    
    try {
      const response = await axios.post('https://ykhg7z1bzl.execute-api.ap-southeast-1.amazonaws.com/Dev/', {
        stock: stockName,
        s3_bucket_name: 'webscrape-bucket-mle611',
        source_file: 'news_data_overall.csv',
        date_range: [formattedStartDate, formattedEndDate]
      });

      const newsData = JSON.parse(response.data.body);
      this.setState({ news: newsData });
    } catch (error) {
      console.error('Error fetching news:', error);
    }
  };

  render() {
    const { stockName } = this.props;

    return (
      <div style={{ width: "100%"}}>
        <div className="row"  >
          <div className="col-2 col-sm-1 col-md-3 col-lg-2 py-1 pe-md-0 mb-md-1" >
            <div className="d-inline-block d-md-block bg-primary text-white text-center breaking-caret py-1 px-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="1rem" height="1rem" fill="currentColor" className="bi bi-lightning-fill" viewBox="0 0 16 16">
                <path d="M11.251.068a.5.5 0 0 1 .227.58L9.677 6.5H13a.5.5 0 0 1 .364.843l-8 8.5a.5.5 0 0 1-.842-.49L6.323 9.5H3a.5.5 0 0 1-.364-.843l8-8.5a.5.5 0 0 1 .615-.09z" />
              </svg>
              <span className="d-none d-md-inline-block">{stockName} Stock news</span>
            </div>
          </div>

          <div className="col-10 col-sm-11 col-md-9 col-lg-10 ps-1 ps-md-2">
            <div className="breaking-box pt-2 pb-1">
              <marquee behavior="scroll" direction="left" style={{ whiteSpace: 'nowrap' }}>
                {this.state.news.map((item, index) => (
                  <a key={index} className="h6 fw-normal" href={item.URL} target="_blank" style={{ margin: '0 10px' }}>
                    <span className="position-relative mx-2 badge bg-primary rounded-0">{item.Stock}</span>
                    {item.Title}
                  </a>
                ))}
              </marquee>
            </div>
          </div>

        </div>
      </div>
    );
  }
}

export default NewsTicker;
