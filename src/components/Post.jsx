import React from 'react';
import './Post.css';

function Post({ post }) {
  return (
    <article className="post">
      <h2>{post.title}</h2>
      <p className="date">{post.date}</p>
      <p>{post.excerpt}</p>
      <button className="read-more">Read More</button>
    </article>
  );
}

export default Post;