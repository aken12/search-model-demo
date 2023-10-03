import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Header from './Header';
import Searchresult from './Searchresult'
import { useState } from 'react';
import './App.css';

function App() {
  const [results, setResults] = useState(null);
  return (
  <div className="appcomponent">
    <Router>
      <Header onQuerySubmit={setResults}/>
      <Routes>
        <Route path="/search_result"  element={<Searchresult results={results}/>} />
      </Routes>
    </Router>
  </div>
);
}

export default App;
