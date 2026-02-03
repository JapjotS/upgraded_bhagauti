// WebSocket connection
const socket = io();

// Charts storage
const charts = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeWebSocket();
    refreshAll();
});

// Initialize charts for all symbols
function initializeCharts() {
    const cards = document.querySelectorAll('.symbol-card');
    
    cards.forEach(card => {
        const symbol = card.dataset.symbol;
        const canvas = document.getElementById(`chart-${symbol}`);
        
        if (canvas) {
            charts[symbol] = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Price',
                        data: [],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            display: false
                        },
                        y: {
                            display: true,
                            grid: {
                                color: 'rgba(148, 163, 184, 0.1)'
                            },
                            ticks: {
                                color: '#94a3b8',
                                font: {
                                    size: 10
                                }
                            }
                        }
                    }
                }
            });
        }
    });
}

// Initialize WebSocket handlers
function initializeWebSocket() {
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('market_data', function(data) {
        console.log('Market data received:', data);
        handleMarketData(data);
    });
    
    socket.on('trade_signals', function(data) {
        console.log('Trade signal received:', data);
        handleTradeSignal(data);
    });
    
    socket.on('trade_executions', function(data) {
        console.log('Trade execution:', data);
        handleTradeExecution(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    const statusText = statusEl.querySelector('.status-text');
    
    if (connected) {
        statusEl.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusEl.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Handle market data updates
function handleMarketData(data) {
    const symbol = data.symbol;
    
    if (data.type === 'quote') {
        updateQuote(symbol, data.data);
    } else if (data.type === 'candles') {
        updateChart(symbol, data.data);
    } else if (data.type === 'sentiment') {
        updateSentiment(symbol, data.data);
    }
    
    updateLastUpdateTime(symbol);
}

// Update quote display
function updateQuote(symbol, quote) {
    const priceEl = document.getElementById(`price-${symbol}`);
    const changeEl = document.getElementById(`change-${symbol}`);
    const volumeEl = document.getElementById(`volume-${symbol}`);
    
    if (priceEl && quote.current_price) {
        const priceValue = priceEl.querySelector('.price-value');
        priceValue.textContent = `$${quote.current_price.toFixed(2)}`;
        
        // Animate price change
        priceValue.style.transform = 'scale(1.1)';
        setTimeout(() => {
            priceValue.style.transform = 'scale(1)';
        }, 300);
    }
    
    if (changeEl && quote.percent_change !== undefined) {
        const changeValue = changeEl.querySelector('.change-value');
        const change = quote.percent_change;
        changeValue.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
        
        // Update color
        changeEl.classList.remove('positive', 'negative');
        changeEl.classList.add(change >= 0 ? 'positive' : 'negative');
    }
    
    if (volumeEl && quote.volume) {
        volumeEl.textContent = formatVolume(quote.volume);
    }
}

// Update chart with candle data
function updateChart(symbol, candles) {
    const chart = charts[symbol];
    
    if (chart && candles.close && candles.timestamps) {
        const labels = candles.timestamps.map(ts => {
            const date = new Date(ts * 1000);
            return date.toLocaleTimeString();
        });
        
        chart.data.labels = labels.slice(-30); // Last 30 data points
        chart.data.datasets[0].data = candles.close.slice(-30);
        chart.update('none'); // Update without animation for performance
    }
}

// Update sentiment display
function updateSentiment(symbol, sentiment) {
    const sentimentEl = document.getElementById(`sentiment-${symbol}`);
    
    if (sentimentEl && sentiment.sentiment_score !== undefined) {
        const score = (sentiment.sentiment_score * 100).toFixed(0);
        sentimentEl.textContent = `${score}%`;
        
        // Color based on sentiment
        if (sentiment.sentiment_score > 0.6) {
            sentimentEl.style.color = '#10b981';
        } else if (sentiment.sentiment_score < 0.4) {
            sentimentEl.style.color = '#ef4444';
        } else {
            sentimentEl.style.color = '#94a3b8';
        }
    }
}

// Handle trade signals
function handleTradeSignal(data) {
    const symbol = data.symbol;
    const signal = data.signal;
    
    // Update signal badge
    const signalEl = document.getElementById(`signal-${symbol}`);
    if (signalEl) {
        const badge = signalEl.querySelector('.badge');
        badge.textContent = signal.action;
        badge.className = `badge ${signal.action}`;
    }
    
    // Add to signal feed
    addToSignalFeed(signal);
}

// Add signal to feed
function addToSignalFeed(signal) {
    const feedList = document.getElementById('signalFeed');
    
    // Remove empty message
    const emptyMsg = feedList.querySelector('.feed-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    // Create feed item
    const feedItem = document.createElement('div');
    feedItem.className = `feed-item ${signal.action}`;
    feedItem.innerHTML = `
        <div class="feed-item-header">
            <span class="feed-symbol">${signal.symbol}</span>
            <span class="feed-action ${signal.action}">${signal.action}</span>
        </div>
        <div class="feed-reason">${signal.reason}</div>
        <div class="feed-confidence">Confidence: ${(signal.confidence * 100).toFixed(0)}%</div>
    `;
    
    // Add to top of feed
    feedList.insertBefore(feedItem, feedList.firstChild);
    
    // Limit feed to 20 items
    const items = feedList.querySelectorAll('.feed-item');
    if (items.length > 20) {
        items[items.length - 1].remove();
    }
}

// Handle trade executions
function handleTradeExecution(data) {
    console.log('Trade executed:', data);
    // Could show a notification or update UI
}

// Update last update time
function updateLastUpdateTime(symbol) {
    const updateEl = document.getElementById(`update-${symbol}`);
    if (updateEl) {
        const now = new Date();
        updateEl.textContent = now.toLocaleTimeString();
    }
}

// Refresh all symbols
function refreshAll() {
    fetch('/api/refresh-all', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Refresh all triggered:', data);
    })
    .catch(error => {
        console.error('Error refreshing all:', error);
    });
}

// Refresh single symbol
function refreshSymbol(symbol) {
    fetch(`/api/refresh/${symbol}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Refresh triggered for ${symbol}:`, data);
    })
    .catch(error => {
        console.error(`Error refreshing ${symbol}:`, error);
    });
}

// Utility: Format volume
function formatVolume(volume) {
    if (volume >= 1000000000) {
        return (volume / 1000000000).toFixed(2) + 'B';
    } else if (volume >= 1000000) {
        return (volume / 1000000).toFixed(2) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(2) + 'K';
    }
    return volume.toString();
}

// Auto-refresh every 60 seconds
setInterval(refreshAll, 60000);
