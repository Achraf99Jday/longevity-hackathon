// AI Search Functions - extracted for clarity

async function performAISearch() {
    const input = document.getElementById('ai-search-input');
    const query = input.value.trim();
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    const resultsDiv = document.getElementById('ai-search-results');
    const summaryDiv = document.getElementById('ai-search-summary');
    const contentDiv = document.getElementById('ai-search-results-content');
    const suggestionsDiv = document.getElementById('ai-suggestions-list');
    
    resultsDiv.style.display = 'block';
    summaryDiv.innerHTML = '<strong>🔍 Searching with AI...</strong>';
    contentDiv.innerHTML = '';
    suggestionsDiv.innerHTML = '';
    
    try {
        console.log('[AI Search] Query:', query);
        const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('[AI Search] Results:', data);
        
        // Show summary
        summaryDiv.innerHTML = `<strong>💬 ${data.summary || 'Search completed'}</strong>`;
        
        // Show results
        let html = '';
        
        if (data.results && data.results.problems && data.results.problems.length > 0) {
            html += '<h3 style="color: #667eea; margin-top: 20px;">📋 Problems (' + (data.total_problems || data.results.problems.length) + ')</h3>';
            html += '<div style="display: grid; gap: 10px; margin-top: 10px;">';
            data.results.problems.slice(0, 5).forEach(p => {
                html += `
                    <div class="problem-card" onclick="showProblemDetails(${p.id})" style="cursor: pointer;">
                        <span class="category">${p.category.replace(/_/g, ' ')}</span>
                        <h4>${p.title}</h4>
                        <p>${p.description.substring(0, 150)}...</p>
                        ${p.reason ? `<small style="color: #666;">💡 ${p.reason}</small>` : ''}
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (data.results && data.results.capabilities && data.results.capabilities.length > 0) {
            html += '<h3 style="color: #667eea; margin-top: 20px;">🛠️ Capabilities (' + (data.total_capabilities || data.results.capabilities.length) + ')</h3>';
            html += '<div style="display: grid; gap: 10px; margin-top: 10px;">';
            data.results.capabilities.slice(0, 5).forEach(c => {
                html += `
                    <div style="padding: 15px; background: white; border-radius: 8px; border-left: 3px solid #667eea;">
                        <strong>${c.name}</strong> (${c.type.replace(/_/g, ' ')})
                        <p style="margin-top: 5px; color: #666;">${c.description ? c.description.substring(0, 100) + '...' : ''}</p>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (data.results && data.results.gaps && data.results.gaps.length > 0) {
            html += '<h3 style="color: #667eea; margin-top: 20px;">⚠️ Gaps (' + (data.total_gaps || data.results.gaps.length) + ')</h3>';
            html += '<div style="display: grid; gap: 10px; margin-top: 10px;">';
            data.results.gaps.slice(0, 5).forEach(g => {
                html += `
                    <div class="gap-card" onclick="showGapDetails(${g.id})" style="cursor: pointer;">
                        <h4>${g.capability_name}</h4>
                        <p><strong>Priority:</strong> ${g.priority.toUpperCase()} | 
                           <strong>Blocked Value:</strong> $${(g.blocked_value / 1000000).toFixed(1)}M</p>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (!html) {
            html = '<p>No results found. Try rephrasing your query or ask something like:<br>"What problems need mouse models?" or "Show me gaps in mitochondrial research"</p>';
        }
        
        contentDiv.innerHTML = html;
        
        // Show suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            suggestionsDiv.innerHTML = data.suggestions.map(s => 
                `<button onclick="document.getElementById('ai-search-input').value='${s.replace(/'/g, "\\'")}'; performAISearch();" 
                         style="margin: 5px; padding: 8px 15px; background: white; border: 1px solid #667eea; color: #667eea; border-radius: 5px; cursor: pointer;">
                    ${s}
                 </button>`
            ).join('');
        }
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        console.error('[AI Search] Error:', error);
        summaryDiv.innerHTML = `<strong style="color: red;">❌ Error: ${error.message}</strong>`;
        contentDiv.innerHTML = '<p>Make sure the API server is running and OpenAI API key is configured.</p>';
    }
}

function closeAISearch() {
    document.getElementById('ai-search-results').style.display = 'none';
    document.getElementById('ai-search-input').value = '';
}


