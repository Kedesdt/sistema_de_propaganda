// Configurações do Cliente
let config = {
    serverUrl: localStorage.getItem('serverUrl') || window.location.origin,
    latitude: parseFloat(localStorage.getItem('latitude')) || null,
    longitude: parseFloat(localStorage.getItem('longitude')) || null,
    checkInterval: parseInt(localStorage.getItem('checkInterval')) || 60
};

let currentVideoId = null;
let currentVideoBlob = null;
let checkTimer = null;
let videoPlayer = null;
let inactivityTimer = null;
const INACTIVITY_DELAY = 3000; // 3 segundos

// Inicializar quando a página carregar
window.onload = function() {
    videoPlayer = document.getElementById('video-player');
    loadConfig();
    setupMouseInactivity();
    
    if (config.latitude && config.longitude) {
        startClient();
    } else {
        showError('Configure a localização do cliente antes de começar.');
        toggleConfig();
    }
    
    // Configurar evento de loop do vídeo
    videoPlayer.addEventListener('ended', function() {
        console.log('🔄 Reiniciando vídeo...');
        this.currentTime = 0;
        this.play();
    });
    
    // Adicionar eventos de mouse
    document.addEventListener('mousemove', resetInactivityTimer);
    document.addEventListener('mousedown', resetInactivityTimer);
    document.addEventListener('keypress', resetInactivityTimer);
    document.addEventListener('touchstart', resetInactivityTimer);
};

// Configurar sistema de inatividade do mouse
function setupMouseInactivity() {
    // Iniciar timer de inatividade
    resetInactivityTimer();
}

// Resetar timer de inatividade
function resetInactivityTimer() {
    // Mostrar controles
    showControls();
    
    // Limpar timer anterior
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }
    
    // Criar novo timer
    inactivityTimer = setTimeout(() => {
        hideControls();
    }, INACTIVITY_DELAY);
}

// Mostrar controles
function showControls() {
    const toggleButton = document.querySelector('.toggle-config');
    const infoDisplay = document.getElementById('info-display');
    const status = document.getElementById('status');
    
    if (toggleButton) toggleButton.style.opacity = '1';
    if (infoDisplay) infoDisplay.style.opacity = '1';
    if (status) status.style.opacity = '1';
    
    document.body.style.cursor = 'default';
}

// Esconder controles
function hideControls() {
    const configPanel = document.getElementById('config-panel');
    const toggleButton = document.querySelector('.toggle-config');
    const infoDisplay = document.getElementById('info-display');
    const status = document.getElementById('status');
    
    // Não esconder se o painel de configuração estiver aberto
    if (!configPanel.classList.contains('hidden')) {
        return;
    }
    
    if (toggleButton) toggleButton.style.opacity = '0';
    if (infoDisplay) infoDisplay.style.opacity = '0';
    if (status) status.style.opacity = '0';
    
    document.body.style.cursor = 'none';
}

// Carregar configurações na interface
function loadConfig() {
    document.getElementById('server-url').value = config.serverUrl;
    document.getElementById('latitude').value = config.latitude || '';
    document.getElementById('longitude').value = config.longitude || '';
    document.getElementById('check-interval').value = config.checkInterval;
    updateLocationInfo();
}

// Salvar configurações
function saveConfig() {
    config.serverUrl = document.getElementById('server-url').value.replace(/\/$/, ''); // Remove trailing slash
    config.latitude = parseFloat(document.getElementById('latitude').value);
    config.longitude = parseFloat(document.getElementById('longitude').value);
    config.checkInterval = parseInt(document.getElementById('check-interval').value);

    // Validações
    if (isNaN(config.latitude) || config.latitude < -90 || config.latitude > 90) {
        alert('❌ Latitude inválida! Deve estar entre -90 e 90');
        return;
    }
    
    if (isNaN(config.longitude) || config.longitude < -180 || config.longitude > 180) {
        alert('❌ Longitude inválida! Deve estar entre -180 e 180');
        return;
    }
    
    if (isNaN(config.checkInterval) || config.checkInterval < 10) {
        alert('❌ Intervalo inválido! Deve ser no mínimo 10 segundos');
        return;
    }

    // Salvar no localStorage
    localStorage.setItem('serverUrl', config.serverUrl);
    localStorage.setItem('latitude', config.latitude);
    localStorage.setItem('longitude', config.longitude);
    localStorage.setItem('checkInterval', config.checkInterval);

    updateLocationInfo();
    toggleConfig();
    startClient();
}

// Alternar painel de configuração
function toggleConfig() {
    const panel = document.getElementById('config-panel');
    panel.classList.toggle('hidden');
    
    // Se abriu o painel, mostrar controles e parar timer
    if (!panel.classList.contains('hidden')) {
        showControls();
        if (inactivityTimer) {
            clearTimeout(inactivityTimer);
        }
    } else {
        // Se fechou, reiniciar timer
        resetInactivityTimer();
    }
}

// Atualizar informações de localização na tela
function updateLocationInfo() {
    if (config.latitude && config.longitude) {
        document.getElementById('location-info').textContent = 
            `${config.latitude.toFixed(6)}, ${config.longitude.toFixed(6)}`;
    } else {
        document.getElementById('location-info').textContent = 'Não configurado';
    }
}

// Obter localização do GPS do navegador
function getLocation() {
    if (navigator.geolocation) {
        showLoading('Obtendo localização do GPS...');
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
                hideLoading();
                alert('✅ Localização obtida com sucesso!');
            },
            (error) => {
                hideLoading();
                let errorMsg = '';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = 'Permissão negada. Por favor, permita o acesso à localização.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = 'Localização indisponível.';
                        break;
                    case error.TIMEOUT:
                        errorMsg = 'Tempo esgotado para obter localização.';
                        break;
                    default:
                        errorMsg = 'Erro desconhecido ao obter localização.';
                }
                alert('❌ ' + errorMsg);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        alert('❌ Geolocalização não suportada pelo navegador');
    }
}

// Iniciar cliente
async function startClient() {
    console.log('🚀 Iniciando cliente web...');
    hideError();
    hideLoading();
    
    // Verificar imediatamente
    await checkForVideos();
    
    // Configurar verificação periódica
    if (checkTimer) clearInterval(checkTimer);
    checkTimer = setInterval(checkForVideos, config.checkInterval * 1000);
    
    updateStatus(true);
}

// Verificar vídeos disponíveis no servidor
async function checkForVideos() {
    try {
        console.log('🔍 Verificando novos vídeos...');
        
        const url = `${config.serverUrl}/api/videos?latitude=${config.latitude}&longitude=${config.longitude}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const data = await response.json();
        const now = new Date();
        document.getElementById('last-check').textContent = now.toLocaleTimeString('pt-BR');
        
        if (data.videos && data.videos.length > 0) {
            const video = data.videos[0]; // Pega o primeiro vídeo disponível
            console.log('📹 Vídeo encontrado:', video.original_filename);
            
            // Verificar se precisa baixar novo vídeo
            if (currentVideoId !== video.id) {
                await downloadAndPlayVideo(video);
            }
        } else {
            console.log('ℹ️ Nenhum vídeo disponível para esta localização');
            document.getElementById('video-info').textContent = 'Nenhum disponível';
            
            // Limpar vídeo atual se não houver mais vídeos
            if (currentVideoBlob) {
                URL.revokeObjectURL(currentVideoBlob);
                currentVideoBlob = null;
                currentVideoId = null;
                videoPlayer.src = '';
                videoPlayer.pause();
            }
        }
        
        updateStatus(true);
    } catch (error) {
        console.error('❌ Erro ao verificar vídeos:', error);
        updateStatus(false);
        // Não mostrar erro se já estiver reproduzindo um vídeo
        if (!currentVideoId) {
            showError(`Erro ao conectar ao servidor: ${error.message}`);
        }
    }
}

// Baixar e reproduzir vídeo
async function downloadAndPlayVideo(video) {
    try {
        showLoading(`Baixando: ${video.original_filename}`);
        
        const url = `${config.serverUrl}/api/download/${video.id}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Erro ao baixar vídeo: ${response.status}`);
        }
        
        const blob = await response.blob();
        
        // Liberar blob anterior
        if (currentVideoBlob) {
            URL.revokeObjectURL(currentVideoBlob);
        }
        
        currentVideoBlob = URL.createObjectURL(blob);
        currentVideoId = video.id;
        
        videoPlayer.src = currentVideoBlob;
        videoPlayer.load();
        
        // Tentar reproduzir (pode falhar se não houver interação do usuário)
        const playPromise = videoPlayer.play();
        
        if (playPromise !== undefined) {
            playPromise.then(() => {
                console.log('✅ Vídeo carregado e reproduzindo');
                document.getElementById('video-info').textContent = video.original_filename;
                hideLoading();
            }).catch((error) => {
                console.warn('⚠️ Autoplay bloqueado, clique na tela para iniciar:', error);
                hideLoading();
                // Adicionar evento de clique para iniciar reprodução
                document.body.addEventListener('click', function playOnClick() {
                    videoPlayer.play();
                    document.body.removeEventListener('click', playOnClick);
                }, { once: true });
            });
        }
        
    } catch (error) {
        console.error('❌ Erro ao baixar/reproduzir vídeo:', error);
        hideLoading();
        showError(`Erro ao carregar vídeo: ${error.message}`);
    }
}

// Atualizar status de conexão
function updateStatus(online) {
    const statusText = document.getElementById('status-text');
    if (online) {
        statusText.className = 'status-online';
        statusText.textContent = '● Online';
    } else {
        statusText.className = 'status-offline';
        statusText.textContent = '● Offline';
    }
}

// Mostrar loading
function showLoading(message = 'Carregando...') {
    const loading = document.getElementById('loading');
    loading.querySelector('p').textContent = message;
    loading.classList.remove('hidden');
}

// Esconder loading
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Mostrar erro
function showError(message) {
    document.getElementById('error-text').textContent = message;
    document.getElementById('error-message').style.display = 'block';
}

// Esconder erro
function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

// Tentar reconectar
function retryConnection() {
    hideError();
    startClient();
}

// Limpar recursos ao fechar a página
window.addEventListener('beforeunload', function() {
    if (currentVideoBlob) {
        URL.revokeObjectURL(currentVideoBlob);
    }
    if (checkTimer) {
        clearInterval(checkTimer);
    }
});
