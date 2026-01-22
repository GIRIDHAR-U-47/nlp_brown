// Tab Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        const tabId = this.getAttribute('data-tab');
        
        // Remove active from all nav items and tab contents
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
        
        // Add active to clicked nav item and corresponding tab
        this.classList.add('active');
        document.getElementById(tabId).classList.add('active');
    });
});

// Custom Text Processing
document.getElementById('processBtn').addEventListener('click', processText);
document.getElementById('clearBtn').addEventListener('click', clearForm);

function clearForm() {
    document.getElementById('textInput').value = '';
    document.getElementById('resultsSection').style.display = 'none';
}

function processText() {
    const text = document.getElementById('textInput').value;
    const stopwordRemoval = document.getElementById('stopwordRemoval').checked;
    const stemming = document.getElementById('stemming').checked;
    const lemmatization = document.getElementById('lemmatization').checked;

    if (!text.trim()) {
        alert('Please enter some text to process');
        return;
    }

    fetch('/preprocess', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            stopword_removal: stopwordRemoval,
            stemming: stemming,
            lemmatization: lemmatization
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayResults(data) {
    const results = data.results;
    
    document.getElementById('normalizedResult').textContent = results.normalized;
    document.getElementById('cleanedResult').textContent = results.cleaned;
    document.getElementById('tokenizedResult').innerHTML = formatTokens(results.tokenized);
    document.getElementById('stopwordResult').innerHTML = formatTokens(results.after_stopword_removal);
    document.getElementById('finalResult').innerHTML = formatTokens(results.final_tokens);
    document.getElementById('processingType').textContent = results.processing_type;
    document.getElementById('tokenCount').textContent = data.token_count;
    document.getElementById('uniqueCount').textContent = data.unique_tokens;
    
    document.getElementById('resultsSection').style.display = 'block';
}

function formatTokens(tokens) {
    return tokens.map(token => `<span class="token">${escapeHtml(token)}</span>`).join('');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Brown Corpus Processing
document.getElementById('processBrownBtn').addEventListener('click', processBrownCorpus);

function processBrownCorpus() {
    const stopwordRemoval = document.getElementById('brownStopword').checked;
    const stemming = document.getElementById('brownStemming').checked;
    const lemmatization = document.getElementById('brownLemmatization').checked;

    fetch('/process_brown_corpus', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            stopword_removal: stopwordRemoval,
            stemming: stemming,
            lemmatization: lemmatization
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayBrownResults(data.results);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

function displayBrownResults(results) {
    const brownResults = document.getElementById('brownResults');
    brownResults.innerHTML = '';

    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'corpus-item';
        
        const processingType = result.processed.processing_type || 'No Processing';
        
        item.innerHTML = `
            <h5>📄 Sentence ${index + 1}</h5>
            <div class="original"><strong>Original:</strong> ${escapeHtml(result.original)}</div>
            <div class="processed">
                <strong>Processing:</strong> ${processingType}<br>
                <strong>Final Tokens:</strong> ${formatTokens(result.processed.final_tokens)}
            </div>
        `;
        
        brownResults.appendChild(item);
    });

    document.getElementById('brownResultsSection').style.display = 'block';
}

// Load Brown Corpus samples on page load
window.addEventListener('load', function() {
    console.log('Page loaded - ready to process text');
});