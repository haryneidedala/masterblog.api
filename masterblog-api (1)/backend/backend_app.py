from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory database (replace with real database in production)
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


# Helper function to generate new IDs
def generate_id():
    return max(post['id'] for post in POSTS) + 1 if POSTS else 1


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content are required"}), 400

    new_post = {
        "id": generate_id(),
        "title": data['title'],
        "content": data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    post = next((p for p in POSTS if p['id'] == post_id), None)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    if 'title' in data:
        post['title'] = data['title']
    if 'content' in data:
        post['content'] = data['content']

    return jsonify(post)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post = next((p for p in POSTS if p['id'] == post_id), None)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    POSTS = [p for p in POSTS if p['id'] != post_id]
    return jsonify({"message": "Post deleted successfully"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)