from flask import Flask, request, jsonify, render_template
from transformations.RemoveUnnecessaryElseTransformation import RemoveUnnecessaryElseTransformation
from transformations.ConvertForLoopsToListComprehensionTransformation import ConvertForLoopsToListComprehensionTransformation
from transformations.ReorderPlusOperandsTransformation import ReorderPlusOperandsTransformation
from transformations.FixingMissingWhiteSpacesTransformation import FixingMissingWhiteSpacesTransformation
from transformations.AddExpectedLinesTransformation import AddExpectedLinesTransformation
from transformations.MergeComparisonTransformation import MergeComparisonTransformation
from encoder import Encoder
from callgpt import call_gpt

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Modify app.py endpoint
@app.route('/transform', methods=['POST'])
def transform():
    code = request.json['code']
    transform_order = request.json.get('transformationOrder', [])
    
    # Create ordered transformation list
    transformation_map = {
        "RemoveUnnecessaryElse": RemoveUnnecessaryElseTransformation(),
        "ConvertForLoopsToListComprehension": ConvertForLoopsToListComprehensionTransformation(),
        "FixingMissingWhiteSpaces": FixingMissingWhiteSpacesTransformation(),
        "ReorderPlusOperands": ReorderPlusOperandsTransformation(),
        "MergeComparison": MergeComparisonTransformation(),
        "AddExpectedLines": AddExpectedLinesTransformation()
    }
    
    transformations = [transformation_map[name] for name in transform_order]
    
    watermark = [1, 0]
    n = 2
    l = 4
    e = 0
    
    transformed_code = Encoder(code, transformations, watermark, n, l, e)
    return jsonify({
        'transformed_code': transformed_code,
        'applied_transformations': transform_order[:n]
    })

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    original_code = data['original_code']
    transformed_code = data['transformed_code']
    summary = call_gpt(original_code, transformed_code)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)