import React, { useState } from 'react';
import styles from './searchresult.module.css';

const SearchResult = ({ results }) => {
    if (!results) {
        return null;
    }
    // 結果オブジェクト内のフィールド処理

    return(
        <div className={styles.results}>
            {results.result1.result && (
            <div className={`${styles.bm25_results} ${!results.result2.result ? styles.full_width : ''}`}>
                <h2 className={styles.h2}>{results.result1.name}検索結果</h2>
                <p className={styles.p}>検索結果数: {results.result1.result.length}</p>
                <p className={styles.p}>検索時間: {results.result1.search_time}</p>
                {results.result1.result.map((result, index) => (
                    <div className={styles.result_card} key={index}>
                        <header className={styles.header}>
                            <div className={styles.card_title}>
                                <p className={styles.subject_name}>{result._source.subject_name}</p>
                                <p className={styles.subject_number}>科目番号 {result._source.subject_number}</p>
                            </div>
                            <p className='result-description'>{result._source.course_overview}</p>
                            {/* <p className='timeslot'>{result._source.time_slot}</p> */}
                        </header>
                        {/* 他の情報 */}
                    </div>
                ))}
            </div>
            )}
            
            {results.result2.result && (
            <div className={`${styles.dpr_results} ${!results.result1.result ? styles.full_width : ''}`}>
                <h2 className={styles.h2}>{results.result2.name}検索結果</h2>
                <p className={styles.p}>検索結果数: {results.result2.result.length}</p>
                <p className={styles.p}>検索時間: {results.result2.search_time}</p>
                {results.result2.result.map((result, index) => (
                    <div className={styles.result_card} key={index}>
                        <header className={styles.header}>
                            <div className={styles.card_title}>
                                <p className={styles.subject_name}>{result._source.subject_name}</p>
                                <p className={styles.subject_number}>科目番号 {result._source.subject_number}</p>
                            </div>
                            <p className='result-description'>{result._source.course_overview}</p>
                        </header>
                        {/* 他の情報 */}
                    </div>
                ))}
            </div>
            )}
        </div>
    );    
};

export default SearchResult;