const API_BASE = 'http://localhost:5002/api/v1';
let authToken = null;

// DOM Elements
const loginForm = document.getElementById('login-form');
const postForm = document.getElementById('post-form');
const postContainer = document.getElementById('post-container');
const searchInput = document.getElementById('search-input');

// Load posts when page loads
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('post-section').style.display = 'block';
        loadPosts();
    }
});

// Login function
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            document.getElementById('auth-section').style.display = 'none';
            document.getElementById('post-section').style.display = 'block';
            loadPosts();
        } else {
            showError(data.msg || 'Login failed');
        }
    } catch (error) {
        showError('Network error');
    }
});

// Load posts with pagination and sorting
async function loadPosts(page = 1, sort = '', direction = '') {
    try {
        const url = new URL(`${API_BASE}/posts`);
        url.searchParams.set('page', page);
        if (sort) url.searchParams.set('sort', sort);
        if (direction) url.searchParams.set('direction', direction);

        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        const data = await response.json();

        if (response.ok) {
            renderPosts(data.posts);
            renderPagination(data.page, data.per_page, data.total);
        } else {
            showError(data.error || 'Failed to load posts');
        }
    } catch (error) {
        showError('Network error');
    }
}

// Render posts to DOM
function renderPosts(posts) {
    postContainer.innerHTML = '';

    if (posts.length === 0) {
        postContainer.innerHTML = '<p>No posts found</p>';
        return;
    }

    posts.forEach(post => {
        const postEl = document.createElement('div');
        postEl.className = 'post';
        postEl.innerHTML = `
            <h2>${post.title}</h2>
            <div class="post-meta">By ${post.author}</div>
            <div class="post-content">${post.content}</div>
            <div class="post-tags">
                ${post.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
            <button onclick="deletePost(${post.id})">Delete</button>
            <div class="comments">
                <h4>Comments (${post.comments.length})</h4>
                ${post.comments.map(comment => `
                    <div class="comment">
                        <div class="comment-author">${comment.author}</div>
                        <div>${comment.content}</div>
                    </div>
                `).join('')}
                <form onsubmit="addComment(event, ${post.id})">
                    <input type="text" placeholder="Add a comment" required>
                    <button type="submit">Post Comment</button>
                </form>
            </div>
        `;
        postContainer.appendChild(postEl);
    });
}

// Other CRUD operations (addPost, deletePost, updatePost, etc.)
// Search functionality, pagination rendering, etc.