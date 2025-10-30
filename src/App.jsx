import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Post from './components/Post';
import './App.css';

function App() {
  const posts = [
    {
      id: 1,
      title: "Emo Nights: Reflections on Darkness",
      excerpt: "In the shadows of the night, we find our true selves...",
      date: "October 31, 2023"
    },
    {
      id: 2,
      title: "Heartbreak and Heavy Eyeliner",
      excerpt: "Tales of love lost and mascara runs...",
      date: "November 5, 2023"
    },
    {
      id: 3,
      title: "Gothic Vibes in the Modern World",
      excerpt: "Blending black lace with city lights...",
      date: "November 10, 2023"
    }
  ];

  return (
    <div className="app">
      <Header />
      <main className="main">
        <div className="posts">
          {posts.map(post => (
            <Post key={post.id} post={post} />
          ))}
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;