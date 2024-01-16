from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
client = Elasticsearch(
  "https://1d56addfa820429f81bae63913b7ffb2.us-central1.gcp.cloud.es.io:443",
  api_key="dzVuWkVZMEIzYlhQU244dUlHSlc6S0g1OTRhQmVSNENveTlkOTZmZVowQQ=="
)

def create_index():
    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"}
            }
        }
    }
    client.indices.create(index="knowledge_index", body=index_body)

def list_all_notes():
    search_body = {
        "query": {"match_all": {}}
    }
    result = client.search(index="knowledge_index", body=search_body)
    return result['hits']['hits']

@app.route('/api/notes', methods=['GET'])
def get_all_notes():
    # Create index if it doesn't exist
    if not client.indices.exists(index="knowledge_index"):
        create_index()

    # List all notes
    notes = list_all_notes()

    # Extract relevant fields
    note_list = [{"title": note['_source']['title'], "content": note['_source']['content']} for note in notes]

    return jsonify({"notes": note_list}), 200

@app.route('/api/notes', methods=['POST'])
def create_knowledge_article():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    client.index(index='knowledge_index', doc_type='_doc', id=title, body={'title': title, 'content': content})
    
    return jsonify({'message': 'Knowledge article created successfully'}), 201

@app.route('/api/notes/<title>', methods=['GET'])
def get_knowledge_article(title):
    result = client.get(index='knowledge_index', doc_type='_doc', id=title)
    
    return jsonify(result['_source'])

#update
def upload_to_elasticsearch(title, content):
    document = {"title": title, "content": content}
    client.index(index="knowledge_index", body=document)

@app.route('/api/upload', methods=['POST'])
def upload_data():
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    # Create index if it doesn't exist
    if not client.indices.exists(index="knowledge_index"):
        create_index()

    # Upload document to Elasticsearch
    upload_to_elasticsearch(title, content)

    return jsonify({"message": "Data uploaded successfully"}), 201

#delete
def delete_from_elasticsearch(title):
    client.delete(index="knowledge_index", id=title)

@app.route('/api/notes/<title>', methods=['DELETE'])
def delete_data(title):
    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Delete document from Elasticsearch
    delete_from_elasticsearch(title)

    return jsonify({"message": f"Knowledge article '{title}' deleted successfully"}), 200

if __name__ == '__main__':
    # API key should have cluster monitor rights
    app.run(debug=True, port=5000)
