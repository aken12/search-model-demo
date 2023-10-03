import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Chatcomponent = ({onQuestionSubmit}) => {
    const [question, setQuestion] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        fetch(`http://localhost:5000/syllabus_search?q=${encodeURIComponent(question)}`)
        .then(response => response.json())
        .then(data => {
            onQuestionSubmit(data);
            navigate('/search_result')

        .then(data => {
          fetch(`http://localhost:5000/gpt_generate?data=${encodeURIComponent(JSON.stringify(data))}`)
          .then(response => response.json())
          .then(generatedAnswer => {
            // generatedAnswerをユーザーに表示するなどの処理
          });
        });
    })
};

    return (
      <div >
        <h2>We answer to question about syllabus</h2>
        <form onSubmit={handleSubmit}>
            <label htmlFor="question-input">どんな授業が受けたいですか？</label>
            <input
            id="question-input"
            type="text"
            value={question}
            onChange={event => setQuestion(event.target.value)}
            />
            <button type="submit">送信</button>
        </form>
      </div>
    );
};

export default Chatcomponent;