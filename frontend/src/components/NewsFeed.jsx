import React from 'react';
import './NewsFeed.css'; // 👈 Make sure to import the CSS file

const NewsFeed = ({ articles }) => {
  return (
    <div className="news-feed-container">
      <h3 className="news-title">Related News</h3>
      {articles && articles.length > 0 ? (
        <div className="news-grid">
          {articles.map((article, idx) => (
            <div key={idx} className="news-card">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="news-link"
              >
                <h4 className="news-headline">{article.title}</h4>
              </a>
              <p className="news-summary">{article.summary}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="news-empty">No related news available</p>
      )}
    </div>
  );
};

export default NewsFeed;
