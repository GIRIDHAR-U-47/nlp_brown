from flask import Flask, render_template, request, jsonify
from nltk.corpus import brown
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk
import re
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4')

app = Flask(__name__)

class TextPreprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def text_normalization(self, text):
        """Convert text to lowercase"""
        return text.lower()

    def text_cleaning(self, text):
        """Remove special characters, extra spaces, and numbers"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^a-zA-Z\s\.\!\?\,]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenization(self, text):
        """Split text into tokens"""
        return word_tokenize(text)

    def sentence_tokenization(self, text):
        """Split text into sentences"""
        return sent_tokenize(text)

    def stop_word_removal(self, tokens):
        """Remove common stop words"""
        return [word for word in tokens if word.lower() not in self.stop_words]

    def stemming(self, tokens):
        """Apply stemming to tokens"""
        return [self.stemmer.stem(word) for word in tokens]

    def lemmatization(self, tokens):
        """Apply lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(word) for word in tokens]

    def full_preprocessing(self, text, include_stopword_removal=True, apply_stemming=False, apply_lemmatization=False):
        """Complete preprocessing pipeline"""
        results = {}
        
        # Step 1: Normalization
        normalized = self.text_normalization(text)
        results['normalized'] = normalized
        
        # Step 2: Cleaning
        cleaned = self.text_cleaning(normalized)
        results['cleaned'] = cleaned
        
        # Step 3: Tokenization
        tokens = self.tokenization(cleaned)
        results['tokenized'] = tokens
        
        # Step 4: Stop word removal
        if include_stopword_removal:
            tokens = self.stop_word_removal(tokens)
        results['after_stopword_removal'] = tokens
        
        # Step 5: Stemming or Lemmatization
        if apply_stemming:
            tokens = self.stemming(tokens)
            results['final_tokens'] = tokens
            results['processing_type'] = 'Stemming Applied'
        elif apply_lemmatization:
            tokens = self.lemmatization(tokens)
            results['final_tokens'] = tokens
            results['processing_type'] = 'Lemmatization Applied'
        else:
            results['final_tokens'] = tokens
            results['processing_type'] = 'No Stemming/Lemmatization'
        
        return results

preprocessor = TextPreprocessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_brown_samples', methods=['GET'])
def get_brown_samples():
    """Get sample sentences from Brown Corpus"""
    try:
        samples = brown.sents()[:10]  # Get first 10 sentences
        sample_texts = [' '.join(sent) for sent in samples]
        return jsonify({
            'success': True,
            'samples': sample_texts,
            'total_samples': len(sample_texts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/preprocess', methods=['POST'])
def preprocess():
    """Main preprocessing endpoint"""
    try:
        data = request.json
        text = data.get('text', '')
        include_stopword_removal = data.get('stopword_removal', True)
        apply_stemming = data.get('stemming', False)
        apply_lemmatization = data.get('lemmatization', False)
        
        if not text.strip():
            return jsonify({'success': False, 'error': 'Please enter some text'})
        
        results = preprocessor.full_preprocessing(
            text,
            include_stopword_removal=include_stopword_removal,
            apply_stemming=apply_stemming,
            apply_lemmatization=apply_lemmatization
        )
        
        return jsonify({
            'success': True,
            'results': results,
            'token_count': len(results['final_tokens']),
            'unique_tokens': len(set(results['final_tokens']))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/process_brown_corpus', methods=['POST'])
def process_brown_corpus():
    """Process Brown Corpus with preprocessing"""
    try:
        data = request.json
        include_stopword_removal = data.get('stopword_removal', True)
        apply_stemming = data.get('stemming', False)
        apply_lemmatization = data.get('lemmatization', False)
        
        # Get first 5 sentences from Brown Corpus
        brown_sents = brown.sents()[:5]
        results = []
        
        for sent in brown_sents:
            text = ' '.join(sent)
            processed = preprocessor.full_preprocessing(
                text,
                include_stopword_removal=include_stopword_removal,
                apply_stemming=apply_stemming,
                apply_lemmatization=apply_lemmatization
            )
            results.append({
                'original': text,
                'processed': processed
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)