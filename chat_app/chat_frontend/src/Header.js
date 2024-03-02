import React from 'react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './header.module.css';

const Header = ( {onQuerySubmit} ) => {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const [model_name_1, setmodelname1] = useState("model1");
  const [model_name_2, setmodelname2] = useState("No");

  const handleModel1Change = (event) => {
    setmodelname1(event.target.value);
  };

  const handleModel2Change = (event) => {
    setmodelname2(event.target.value);
  };

  const handleSearch = (event) => {
    event.preventDefault();
    console.log("確認");
    fetch(`/api/syllabus_search?q=${encodeURIComponent(query)}&model_name_1=${model_name_1}&model_name_2=${model_name_2}`)
    .then(response => response.json())
    .then(data => {
      onQuerySubmit(data);
      navigate('/search_result');
    }
    )
  };

  return (
    <header className={styles.header}>

      <h1 className={styles.h1}>Search model lab with Syllabus Search</h1>
      <p className={styles.p}> シラバス検索で見るさまざまな検索モデル</p>
      <p className={styles.p2}> モデルを選択することで検索結果の比較ができます </p>
      <form onSubmit={handleSearch}>
      <div className={styles.input_div}>
        <input className={styles.input} type="text" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className={styles.query_button} onClick={handleSearch}>
         <i className="fa fa-search"></i>
        </button>

      </div>
      </form>
      
      <select className={styles.model_select_1} name="model_name_1" value={model_name_1} onChange={handleModel1Change} >
      <option value="model1">モデル1を選択</option>
      <option value="BM25">BM25 (単語一致)</option>
      <option value="E5-small">ベクトル検索（384次元）</option>
      <option value="E5-large">ベクトル検索（1024次元）</option>
      <option value="Hyblid">ハイブリッド検索</option>
      </select>

      <select className={styles.model_select_2} name="model_name_2" value={model_name_2} onChange={handleModel2Change} >
      <option value="model2">モデル2を選択</option>
      <option value="BM25">BM25 (単語一致)</option>
      <option value="E5-small">ベクトル検索（384次元）</option>
      <option value="E5-large">ベクトル検索（1024次元）</option>
      <option value="Hyblid">ハイブリッド検索</option>
      </select>

    </header>
  );
};

export default Header;