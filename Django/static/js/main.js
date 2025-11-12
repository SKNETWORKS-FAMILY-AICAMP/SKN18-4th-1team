// DOM Elements
const symptomsInput = document.getElementById('symptoms-input');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const diseasesList = document.getElementById('diseases-list');
const hospitalsList = document.getElementById('hospitals-list');

// Analyze button click handler
analyzeBtn.addEventListener('click', async () => {
    const symptoms = symptomsInput.value.trim();
    
    if (!symptoms) {
        alert('증상을 입력해주세요.');
        return;
    }
    
    // Disable button
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="button-icon">⏳</span><span class="button-text">분석 중...</span>';
    
    // Show loading
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    try {
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Call API
        const response = await fetch('/api/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ symptoms: symptoms })
        });
        
        if (!response.ok) {
            throw new Error('분석 요청에 실패했습니다.');
        }
        
        const data = await response.json();
        
        // Simulate loading delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Hide loading
        loadingSection.style.display = 'none';
        
        // Display results
        displayResults(data);
        resultsSection.style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        alert('분석 중 오류가 발생했습니다: ' + error.message);
        loadingSection.style.display = 'none';
    } finally {
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span class="button-icon">✨</span><span class="button-text">증상 분석하기</span>';
    }
});

// Display results
function displayResults(data) {
    // Clear previous results
    diseasesList.innerHTML = '';
    hospitalsList.innerHTML = '';
    
    // Display diseases
    if (data.diseases && data.diseases.length > 0) {
        data.diseases.forEach((disease, index) => {
            const diseaseCard = createDiseaseCard(disease, index);
            diseasesList.appendChild(diseaseCard);
        });
    }
    
    // Display hospitals
    if (data.hospitals && data.hospitals.length > 0) {
        data.hospitals.forEach((hospital, index) => {
            const hospitalCard = createHospitalCard(hospital, index);
            hospitalsList.appendChild(hospitalCard);
        });
    }
}

// Create disease card
function createDiseaseCard(disease, index) {
    const card = document.createElement('div');
    card.className = 'disease-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    const severityClass = `severity-${disease.severity}`;
    const severityLabel = getSeverityLabel(disease.severity);
    
    card.innerHTML = `
        <div class="disease-header">
            <div class="disease-name">${disease.name}</div>
            <div class="severity-badge ${severityClass}">${severityLabel}</div>
        </div>
        <div class="disease-description">${disease.description}</div>
        <div class="disease-recommendations">
            <div class="recommendations-title">권장사항:</div>
            <ul class="recommendations-list">
                ${disease.recommendations.map(rec => `
                    <li class="recommendation-item">${rec}</li>
                `).join('')}
            </ul>
        </div>
    `;
    
    return card;
}

// Create hospital card
function createHospitalCard(hospital, index) {
    const card = document.createElement('div');
    card.className = 'hospital-card';
    card.style.animationDelay = `${0.4 + index * 0.1}s`;
    
    card.innerHTML = `
        <div class="medical-cross-icon"></div>
        <div class="hospital-header">
            <div class="hospital-name">${hospital.name}</div>
            <div class="hospital-specialty">${hospital.specialty}</div>
        </div>
        <div class="hospital-info">
            <div class="hospital-detail">
                <svg class="hospital-detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span>${hospital.address}</span>
            </div>
            <div class="hospital-detail">
                <svg class="hospital-detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
                <span>${hospital.phone}</span>
            </div>
            <div class="hospital-footer">
                <div class="hospital-detail">
                    <svg class="hospital-detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    <span>${hospital.distance}</span>
                </div>
                <div class="hospital-detail">
                    <svg class="hospital-detail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>${hospital.waitTime}</span>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Get severity label
function getSeverityLabel(severity) {
    const labels = {
        'low': '경증',
        'medium': '중등도',
        'high': '중증'
    };
    return labels[severity] || '예정 없음';
}

// Scroll to results when they appear
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
            if (resultsSection.style.display === 'block') {
                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
});

observer.observe(resultsSection, { attributes: true });

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

