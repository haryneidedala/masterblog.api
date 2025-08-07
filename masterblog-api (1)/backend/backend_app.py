from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour

# Initialize extensions
jwt = JWTManager(app)

# Correct Limiter initialization
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Database (in-memory for demo)
POSTS = [
    {
        "id": 1,
        "title": "First post",
        "content": "This is the first post.",
        "author": "admin",
        "comments": [],
        "tags": ["tech", "python"]
    }
]
USERS = {
    "admin": {"password": "securepassword", "role": "admin"}
}


# Helper functions
def generate_id():
    return max(post['id'] for post in POSTS) + 1 if POSTS else 1


# Routes
@app.route('/')
def home():
    return "Welcome to Blog API. Endpoints: /api/v1/posts"


@app.route('/api/v1/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"msg": "Missing credentials"}), 400

    if username not in USERS or USERS[username]['password'] != password:
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route('/api/v1/posts', methods=['GET'])
@limiter.limit("10 per minute")
def get_posts():
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Sorting
    sort_field = request.args.get('sort', '').lower()
    direction = request.args.get('direction', '').lower()

    if sort_field and sort_field not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field"}), 400
    if direction and direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid direction"}), 400

    posts = POSTS.copy()
    if sort_field:
        reverse_sort = (direction == 'desc')
        posts.sort(key=lambda x: x[sort_field].lower(), reverse=reverse_sort)

    # Pagination
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_posts = posts[start_idx:end_idx]

    return jsonify({
        'posts': paginated_posts,
        'page': page,
        'per_page': per_page,
        'total': len(posts)
    })


@app.route('/api/v1/posts', methods=['POST'])
@jwt_required()
def add_post():
    data = request.get_json()
    current_user = get_jwt_identity()

    if not data or 'title' not in data or 'content' not in data:
        return jsonify({"error": "Title and content required"}), 400

    new_post = {
        "id": generate_id(),
        "title": data['title'],
        "content": data['content'],
        "author": current_user,
        "comments": [],
        "tags": data.get('tags', [])
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/v1/posts/<int:post_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_post(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)
    current_user = get_jwt_identity()

    if not post:
        return jsonify({"error": "Post not found"}), 404

    if post['author'] != current_user and USERS[current_user]['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'DELETE':
        POSTS.remove(post)
        return jsonify({"message": "Post deleted"}), 200

    if request.method == 'PUT':
        data = request.get_json()
        if 'title' in data: post['title'] = data['title']
        if 'content' in data: post['content'] = data['content']
        if 'tags' in data: post['tags'] = data['tags']
        return jsonify(post), 200


@app.route('/api/v1/posts/<int:post_id>/comments', methods=['GET', 'POST'])
def post_comments(post_id):
    post = next((p for p in POSTS if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if request.method == 'POST':
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content required"}), 400

        new_comment = {
            "id": max(c.get('id', 0) for c in post['comments']) + 1,
            "author": get_jwt_identity(),
            "content": data['content']
        }
        post['comments'].append(new_comment)
        return jsonify(new_comment), 201

    return jsonify(post['comments'])


@app.route('/api/v1/posts/search', methods=['GET'])
def search_posts():
    query = request.args.get('q', '').lower()
    tag = request.args.get('tag', '').lower()

    results = [
        post for post in POSTS
        if (not query or query in post['title'].lower() or query in post['content'].lower()) and
           (not tag or tag in [t.lower() for t in post.get('tags', [])])
    ]
    return jsonify(results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)