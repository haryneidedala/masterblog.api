// Load posts when page loads
window.onload = function() {
    const savedBaseUrl = localStorage.getItem('apiBaseUrl');
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Load all posts
function loadPosts() {
    const baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    fetch(`${baseUrl}/posts`)
        .then(response => response.json())
        .then(posts => {
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            posts.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.innerHTML = `
                    <h2>${post.title}</h2>
                    <p>${post.content}</p>
                    <div class="post-actions">
                        <input type="text" id="edit-title-${post.id}" value="${post.title}">
                        <input type="text" id="edit-content-${post.id}" value="${post.content}">
                        <button onclick="updatePost(${post.id})">Update</button>
                        <button onclick="deletePost(${post.id})">Delete</button>
                    </div>
                `;
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));
}

// Add new post
function addPost() {
    const baseUrl = document.getElementById('api-base-url').value;
    const postTitle = document.getElementById('post-title').value;
    const postContent = document.getElementById('post-content').value;

    fetch(`${baseUrl}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: postTitle,
            content: postContent
        })
    })
    .then(response => response.json())
    .then(() => {
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        loadPosts();
    })
    .catch(error => console.error('Error:', error));
}

// Update existing post
function updatePost(postId) {
    const baseUrl = document.getElementById('api-base-url').value;
    const title = document.getElementById(`edit-title-${postId}`).value;
    const content = document.getElementById(`edit-content-${postId}`).value;

    fetch(`${baseUrl}/posts/${postId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: title,
            content: content
        })
    })
    .then(response => response.json())
    .then(() => loadPosts())
    .catch(error => console.error('Error:', error));
}

// Delete post
function deletePost(postId) {
    const baseUrl = document.getElementById('api-base-url').value;

    fetch(`${baseUrl}/posts/${postId}`, {
        method: 'DELETE'
    })
    .then(() => loadPosts())
    .catch(error => console.error('Error:', error));
}