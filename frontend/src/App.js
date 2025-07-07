/**
 * The App component in this JavaScript code is a React component that allows users to search for
 * companies by industry and location, view company details, and read news articles related to selected
 * companies.
 * @returns The `App` component is being returned, which contains the main structure of the
 * application. It includes a Navbar component, SearchBar component, CompanyCard component, pagination
 * functionality, CompanyDetail component, and NewsFeed component. The content displayed in the app is
 * based on the selected menu item (SCRAPER in this case) and the data fetched from the API based on
 * industry and location search.
 */
import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import CompanyCard from "./components/CompanyCard";
import CompanyDetail from "./components/CompanyDetail";
import Navbar from "./components/Navbar";
import NewsFeed from "./components/NewsFeed";
import axios from "axios";

const App = () => {
  const [companies, setCompanies] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const companiesPerPage = 10;

  const sortedCompanies = [...companies].sort(
    (a, b) => (b.score || 0) - (a.score || 0)
  );

  const paginatedCompanies = sortedCompanies.slice(
    (currentPage - 1) * companiesPerPage,
    currentPage * companiesPerPage
  );

  const totalPages = Math.ceil(companies.length / companiesPerPage);

  const [selectedCompany, setSelectedCompany] = useState(null);
  const [articles, setArticles] = useState([]);
  const [menu, setMenu] = useState("SCRAPER");

  const handleSearch = async ({ industry, location }) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/scrape-companies`,
        {
          params: { industry, location },
        }
      );

      const data = response.data;
      console.log("Fetched companies:", response.data.companies);
      setCompanies(data.companies || data || []);
      setSelectedCompany(null);
      setArticles([]);
      setCurrentPage(1);
    } catch (error) {
      console.error("Error finding companies", error);
      alert("Failed to fetch companies. Please check your server.");
    }
  };

  const handleCompanySelect = (company) => {
    setSelectedCompany(company);
    setArticles(company.news_articles || []);
  };

  return (
    <div className="app-container">
      <Navbar
        menuItems={["HOME", "SCRAPER", "LEAD", "DOCUMENTATION", "CONTACT US"]}
        onSelect={setMenu}
        selected={menu}
      />

      <div className="CenterContainer">
        <div className="main-content">
          {menu === "SCRAPER" && (
            <>
              <h1>Company Finder</h1>
              <p>Find companies by industry and location</p>
              <SearchBar onSearch={handleSearch} />

              <div className="company-list">
                {paginatedCompanies.length > 0 ? (
                  <CompanyCard
                    companies={paginatedCompanies}
                    onCompanyClick={handleCompanySelect}
                  />
                ) : (
                  <p className="text-white mt-4">No companies found.</p>
                )}
              </div>

              <div className="pagination">
                {Array.from({ length: totalPages }, (_, idx) => (
                  <button
                    key={idx + 1}
                    className={currentPage === idx + 1 ? "active-page" : ""}
                    onClick={() => setCurrentPage(idx + 1)}
                  >
                    {idx + 1}
                  </button>
                ))}
              </div>

              <CompanyDetail company={selectedCompany} />
              <NewsFeed articles={articles} />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
