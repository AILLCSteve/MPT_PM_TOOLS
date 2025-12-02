// ============================================================================
// CIPP ANALYZER - CLEAN JAVASCRIPT (Rebuilt from Scratch)
// ============================================================================

// Global State
let currentFile = null;
let currentSessionId = null;
let currentAnalysisResult = null;
let activeEventSource = null;
let questionConfig = {
    sections: [],
    totalQuestions: 0
};

// ============================================================================
// LOGGER - Simple, Working (Exactly like legacy that worked)
// ============================================================================

class Logger {
    static log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logContainer = document.getElementById('logContent');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;

        if (typeof message === 'object') {
            entry.innerHTML = `[${timestamp}] <pre>${JSON.stringify(message, null, 2)}</pre>`;
        } else {
            entry.textContent = `[${timestamp}] ${message}`;
        }

        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
        document.getElementById('logContainer').style.display = 'block';
    }

    static info(msg) { this.log(msg, 'info'); }
    static success(msg) { this.log(msg, 'success'); }
    static error(msg) { this.log(msg, 'error'); }
    static warning(msg) { this.log(msg, 'warning'); }
    static debug(msg) { this.log(msg, 'debug'); }
}

// ============================================================================
// PROGRESS TRACKER
// ============================================================================

class ProgressTracker {
    static show() {
        document.getElementById('progressContainer').style.display = 'block';
    }

    static hide() {
        document.getElementById('progressContainer').style.display = 'none';
    }

    static update(percentage, text) {
        document.getElementById('progressFill').style.width = `${percentage}%`;
        document.getElementById('progressText').textContent = text;
    }
}

// ============================================================================
// FILE UPLOAD HANDLING
// ============================================================================

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    currentFile = file;

    // Update UI
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;

    Logger.info(`📄 PDF file selected: ${file.name}`);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// ============================================================================
// ANALYSIS - Main Flow (CLEAN, SIMPLE)
// ============================================================================

async function startAnalysis() {
    if (!currentFile) {
        Logger.error('Please upload a PDF file first');
        alert('Please upload a PDF file first');
        return;
    }

    try {
        Logger.info('🔥 Starting HOTDOG AI analysis...');

        // Get context guardrails
        const contextGuardrails = document.getElementById('contextGuardrails').value.trim();
        if (contextGuardrails) {
            Logger.info(`📋 Context Guardrails: ${contextGuardrails}`);
        }

        // Disable/enable buttons
        document.getElementById('analyzeBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;

        // Show progress
        ProgressTracker.show();
        ProgressTracker.update(10, 'Uploading document...');

        // STEP 1: Upload PDF
        const formData = new FormData();
        formData.append('file', currentFile);

        const uploadResp = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!uploadResp.ok) {
            throw new Error('File upload failed');
        }

        const uploadData = await uploadResp.json();
        const pdfPath = uploadData.filepath;

        Logger.success(`✅ File uploaded: ${pdfPath}`);
        ProgressTracker.update(20, 'Connecting to HOTDOG AI...');

        // Generate session ID
        currentSessionId = `session_${Date.now()}`;

        // STEP 2: Connect to SSE BEFORE starting analysis
        const progressUrl = `/api/progress/${currentSessionId}`;
        activeEventSource = new EventSource(progressUrl);

        activeEventSource.onopen = () => {
            Logger.info('📡 Connected to live progress stream');
        };

        activeEventSource.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);

                // Route events (SIMPLE - just call Logger)
                if (data.event === 'connected') {
                    Logger.success('✅ Progress stream connected');
                }
                else if (data.event === 'document_ingested') {
                    Logger.info(`📄 Extracted ${data.total_pages} pages into ${data.window_count} windows`);
                    ProgressTracker.update(30, `Extracted ${data.total_pages} pages`);
                }
                else if (data.event === 'config_loaded') {
                    Logger.info(`⚙️ Loaded ${data.total_questions} questions in ${data.section_count} sections`);
                }
                else if (data.event === 'expert_generated') {
                    Logger.info(`🤖 Generated expert: ${data.expert_name}`);
                }
                else if (data.event === 'window_processing') {
                    Logger.info(`🔍 Processing Window ${data.window_num}/${data.total_windows}: Pages ${data.pages}`);
                    const progress = 30 + ((data.window_num / data.total_windows) * 60);
                    ProgressTracker.update(progress, `Window ${data.window_num}/${data.total_windows}`);
                }
                else if (data.event === 'experts_dispatched') {
                    Logger.info(`🤖 Dispatching ${data.expert_count} experts to analyze ${data.question_count} questions`);
                }
                else if (data.event === 'experts_complete') {
                    Logger.success(`✅ Experts found ${data.answers_returned} answers (${data.tokens_used} tokens)`);
                }
                else if (data.event === 'window_complete') {
                    Logger.success(`✅ Window ${data.window_num}: ${data.answers_found} answers (${data.processing_time.toFixed(1)}s)`);

                    // Display live unitary log if provided
                    if (data.unitary_log_markdown) {
                        displayLiveUnitaryLog(data.unitary_log_markdown);
                    }
                }
                else if (data.event === 'progress_milestone') {
                    Logger.info(`📊 Progress: ${data.progress_summary}`);
                }
                else if (data.event === 'done') {
                    Logger.success('🎉 Analysis complete - fetching results...');
                    activeEventSource.close();
                    fetchResults();
                }
                else if (data.event === 'error') {
                    Logger.error(`❌ Error: ${data.error}`);
                    activeEventSource.close();
                    throw new Error(data.error);
                }

            } catch (err) {
                Logger.error('Failed to parse SSE message: ' + err.message);
            }
        };

        activeEventSource.onerror = (err) => {
            Logger.warning('📡 Progress stream disconnected');
        };

        // STEP 3: Start analysis (returns immediately - runs in background)
        const analyzeResp = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: currentSessionId,
                pdf_path: pdfPath,
                context_guardrails: contextGuardrails || undefined
            })
        });

        if (!analyzeResp.ok) {
            throw new Error('Analysis failed to start');
        }

        const analyzeData = await analyzeResp.json();
        Logger.info(`✅ Analysis started in background (Session: ${currentSessionId})`);

    } catch (error) {
        Logger.error('Analysis failed: ' + error.message);
        alert('Analysis failed: ' + error.message);
        ProgressTracker.hide();
        document.getElementById('analyzeBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        if (activeEventSource) {
            activeEventSource.close();
        }
    }
}

// ============================================================================
// FETCH RESULTS (Called when 'done' event received)
// ============================================================================

async function fetchResults() {
    try {
        const resp = await fetch(`/api/results/${currentSessionId}`);
        const data = await resp.json();

        if (!data.success) {
            throw new Error(data.error);
        }

        currentAnalysisResult = data.result;

        Logger.success(`Questions answered: ${data.statistics.questions_answered}/${data.statistics.total_questions}`);
        Logger.success(`Processing time: ${data.statistics.processing_time.toFixed(2)}s`);
        Logger.success(`Estimated cost: ${data.statistics.estimated_cost}`);

        // Display results
        displayResults(data.result);
        displayStatistics(data.statistics);

        // Enable export
        document.getElementById('exportBtn').disabled = false;

        ProgressTracker.hide();
        document.getElementById('analyzeBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;

    } catch (error) {
        Logger.error('Failed to fetch results: ' + error.message);
    }
}

// ============================================================================
// DISPLAY RESULTS
// ============================================================================

function displayResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');

    if (!result || !result.sections) {
        Logger.error('No results to display');
        return;
    }

    let html = '<div style="background: white; padding: 20px; border-radius: 8px;">';

    // Display each section
    result.sections.forEach(section => {
        html += `<h2>${section.section_name}</h2>`;

        section.questions.forEach(q => {
            html += `<div style="margin: 15px 0; padding: 10px; border-left: 3px solid #5b7fcc;">`;
            html += `<strong>Q: ${q.question}</strong><br>`;

            if (q.answer) {
                html += `<p style="margin: 10px 0;">${q.answer}</p>`;
                if (q.page_citations && q.page_citations.length > 0) {
                    html += `<small style="color: #666;">Pages: ${q.page_citations.join(', ')}</small>`;
                }
            } else {
                html += `<p style="color: #999; font-style: italic;">Not found in document</p>`;
            }

            html += `</div>`;
        });
    });

    html += '</div>';

    resultsContent.innerHTML = html;
    resultsSection.style.display = 'block';
}

function displayStatistics(stats) {
    const statsContent = document.getElementById('statisticsContent');

    const html = `
        <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
            <h3>Analysis Statistics</h3>
            <p><strong>Questions Answered:</strong> ${stats.questions_answered} / ${stats.total_questions}</p>
            <p><strong>Processing Time:</strong> ${stats.processing_time.toFixed(2)}s</p>
            <p><strong>Total Tokens:</strong> ${stats.total_tokens.toLocaleString()}</p>
            <p><strong>Estimated Cost:</strong> ${stats.estimated_cost}</p>
            <p><strong>Average Confidence:</strong> ${stats.average_confidence}</p>
        </div>
    `;

    statsContent.innerHTML = html;
}

function displayLiveUnitaryLog(markdownContent) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');

    // Simple markdown to HTML
    const htmlContent = markdownContent
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/\n/g, '<br>');

    resultsContent.innerHTML = `<div style="background: white; padding: 20px; border-radius: 8px;">${htmlContent}</div>`;
    resultsSection.style.display = 'block';
}

// ============================================================================
// STOP ANALYSIS
// ============================================================================

async function stopAnalysis() {
    if (!currentSessionId) {
        Logger.warning('No active analysis to stop');
        return;
    }

    try {
        const resp = await fetch(`/api/stop/${currentSessionId}`, {
            method: 'POST'
        });

        const data = await resp.json();

        if (data.success) {
            Logger.warning('⏹️ Analysis stopped');
            if (activeEventSource) {
                activeEventSource.close();
            }
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('analyzeBtn').disabled = false;
            ProgressTracker.hide();
        }

    } catch (error) {
        Logger.error('Failed to stop analysis: ' + error.message);
    }
}

// ============================================================================
// EXPORT FUNCTIONS (Simplified)
// ============================================================================

function showExportMenu() {
    const menu = document.getElementById('exportMenu');
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

function exportResults(format) {
    if (!currentAnalysisResult) {
        alert('No results to export');
        return;
    }

    Logger.info(`Exporting as ${format}...`);

    if (format === 'json') {
        downloadJSON(currentAnalysisResult, 'cipp_analysis.json');
    }
    else if (format === 'csv') {
        downloadCSV(currentAnalysisResult);
    }
    else {
        alert(`Export format ${format} not yet implemented`);
    }

    document.getElementById('exportMenu').style.display = 'none';
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
}

function downloadCSV(data) {
    let csv = 'Section,Question,Answer,Pages\n';

    data.sections.forEach(section => {
        section.questions.forEach(q => {
            const answer = q.answer ? q.answer.replace(/"/g, '""') : 'Not found';
            const pages = q.page_citations ? q.page_citations.join(';') : '';
            csv += `"${section.section_name}","${q.question}","${answer}","${pages}"\n`;
        });
    });

    const blob = new Blob([csv], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cipp_analysis.csv';
    a.click();
}

// ============================================================================
// CLEAR RESULTS
// ============================================================================

function clearResults() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('resultsContent').innerHTML = '';
    document.getElementById('statisticsContent').innerHTML = '';
    document.getElementById('logContent').innerHTML = '';
    document.getElementById('exportBtn').disabled = true;
    currentAnalysisResult = null;
    currentSessionId = null;
    ProgressTracker.hide();
    Logger.info('🗑️ Results cleared');
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    Logger.info('🚀 CIPP Bid-Spec Analyzer initialized (Clean Rebuild)');
    Logger.info('✅ Ready for document analysis');

    // Load question configuration
    loadQuestionConfig();

    // Setup file drag-and-drop
    setupFileDragDrop();
});

function loadQuestionConfig() {
    // Default CIPP questions configuration
    questionConfig = {
        sections: [
            {id: 'project_info', name: 'Project Information', questions: 10, enabled: true},
            {id: 'pipe_specs', name: 'Pipe Specifications', questions: 10, enabled: true},
            {id: 'cipp_requirements', name: 'CIPP Liner Requirements', questions: 10, enabled: true},
            {id: 'pre_installation', name: 'Pre-Installation Work', questions: 10, enabled: true},
            {id: 'installation', name: 'Installation Process', questions: 10, enabled: true},
            {id: 'quality_control', name: 'Quality Control & Testing', questions: 10, enabled: true},
            {id: 'warranty', name: 'Warranty & Maintenance', questions: 10, enabled: true},
            {id: 'environmental', name: 'Environmental & Safety', questions: 10, enabled: true},
            {id: 'payment', name: 'Payment & Documentation', questions: 10, enabled: true},
            {id: 'special', name: 'Special Conditions', questions: 10, enabled: true}
        ],
        totalQuestions: 100
    };

    // Display sections
    const container = document.getElementById('questionSections');
    container.innerHTML = questionConfig.sections.map(section => `
        <div class="question-section ${section.enabled ? 'enabled' : 'disabled'}"
             onclick="toggleSection('${section.id}')">
            <span class="section-name">${section.name}</span>
            <span class="section-count">${section.questions}</span>
        </div>
    `).join('');

    updateActiveQuestionCount();
}

function updateActiveQuestionCount() {
    const count = questionConfig.sections
        .filter(s => s.enabled)
        .reduce((sum, s) => sum + s.questions, 0);

    document.getElementById('activeQuestionCount').textContent = count;
}

function setupFileDragDrop() {
    const dropZone = document.getElementById('fileUpload');

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#5b7fcc';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#ddd';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ddd';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('fileInput').files = files;
            handleFileSelect({target: {files: files}});
        }
    });
}

// ============================================================================
// STUB FUNCTIONS (To be implemented)
// ============================================================================

function loadTestDocument() {
    alert('Test document loader not implemented');
}

function showQuestionManager() {
    alert('Question manager not implemented');
}

function addQuestionSection() {
    alert('Add section not implemented');
}

function exportQuestions() {
    alert('Export questions not implemented');
}

function showSettings() {
    alert('Settings not implemented');
}

function toggleSection(sectionId) {
    const section = questionConfig.sections.find(s => s.id === sectionId);
    if (section) {
        section.enabled = !section.enabled;
        loadQuestionConfig();
    }
}

function runSecondPass() {
    alert('Second pass not implemented');
}

function exportExcelDashboard() {
    alert('Excel dashboard not implemented');
}

function exportLog() {
    const log = document.getElementById('logContent').innerText;
    downloadJSON({log: log}, 'activity_log.txt');
}

function clearLog() {
    document.getElementById('logContent').innerHTML = '';
}
