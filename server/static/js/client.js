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
let videoIndex = 0;
let availableVideos = []; // Lista de vídeos disponíveis
let downloadedBlobs = []; // Blobs dos vídeos baixados

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
    
    // Configurar evento de fim do vídeo
    videoPlayer.addEventListener('ended', function() {
        playNextVideo();
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
            console.log(`📹 ${data.videos.length} vídeo(s) encontrado(s)`);
            
            // Verificar se há vídeos novos ou removidos
            const hasChanges = checkVideoListChanges(data.videos);
            
            if (hasChanges) {
                console.log('🔄 Mudanças detectadas na lista de vídeos');
                availableVideos = data.videos;
                await updateVideoList();
            } else {
                console.log('✅ Lista de vídeos sem alterações');
            }
        } else {
            console.log('ℹ️ Nenhum vídeo disponível para esta localização');
            document.getElementById('video-info').textContent = 'Nenhum disponível';
            
            // Limpar vídeos
            if (availableVideos.length > 0) {
                clearAllVideos();
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

// Verificar se há mudanças na lista de vídeos
function checkVideoListChanges(newVideos) {
    // Se não há vídeos baixados, há mudança
    if (downloadedBlobs.length === 0 && newVideos.length > 0) {
        return true;
    }
    
    // Se a quantidade mudou, há mudança
    if (newVideos.length !== downloadedBlobs.length) {
        return true;
    }
    
    // Verificar se todos os IDs são os mesmos
    const newIds = newVideos.map(v => v.id).sort();
    const currentIds = downloadedBlobs.map(v => v.id).sort();
    
    for (let i = 0; i < newIds.length; i++) {
        if (newIds[i] !== currentIds[i]) {
            return true;
        }
    }
    
    return false;
}

// Atualizar lista de vídeos (baixar apenas novos, remover excluídos)
async function updateVideoList() {
    try {
        // Identificar vídeos novos (que não estão baixados)
        const newVideos = availableVideos.filter(video => 
            !downloadedBlobs.some(blob => blob.id === video.id)
        );
        
        // Identificar vídeos removidos (que estão baixados mas não estão mais na lista)
        const removedVideos = downloadedBlobs.filter(blob => 
            !availableVideos.some(video => video.id === blob.id)
        );
        
        // Remover vídeos que não existem mais
        if (removedVideos.length > 0) {
            console.log(`🗑️ Removendo ${removedVideos.length} vídeo(s) antigo(s)...`);
            removedVideos.forEach(removed => {
                const index = downloadedBlobs.findIndex(blob => blob.id === removed.id);
                if (index !== -1) {
                    URL.revokeObjectURL(downloadedBlobs[index].url);
                    downloadedBlobs.splice(index, 1);
                    console.log(`   ✅ Removido: ${removed.filename}`);
                }
            });
        }
        
        // Baixar apenas vídeos novos
        if (newVideos.length > 0) {
            console.log(`📥 Baixando ${newVideos.length} vídeo(s) novo(s)...`);
            showLoading(`Baixando ${newVideos.length} vídeo(s) novo(s)...`);
            
            for (let i = 0; i < newVideos.length; i++) {
                const video = newVideos[i];
                console.log(`   📥 ${i + 1}/${newVideos.length}: ${video.original_filename}`);
                
                const url = `${config.serverUrl}/api/download/${video.id}`;
                const response = await fetch(url);
                
                if (!response.ok) {
                    throw new Error(`Erro ao baixar ${video.original_filename}: ${response.status}`);
                }
                
                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);
                
                downloadedBlobs.push({
                    id: video.id,
                    url: blobUrl,
                    filename: video.original_filename
                });
                
                console.log(`   ✅ Baixado: ${video.original_filename}`);
            }
            
            hideLoading();
            console.log(`✅ ${newVideos.length} vídeo(s) novo(s) adicionado(s)`);
        }
        
        // Se não há vídeos tocando, iniciar reprodução
        if (videoPlayer.paused && downloadedBlobs.length > 0) {
            videoIndex = 0;
            playVideoAtIndex(0);
        }
        
        console.log(`📊 Total de vídeos em memória: ${downloadedBlobs.length}`);
        
    } catch (error) {
        console.error('❌ Erro ao atualizar lista de vídeos:', error);
        hideLoading();
        showError(`Erro ao atualizar vídeos: ${error.message}`);
    }
}

// Baixar todos os vídeos disponíveis (usado apenas na primeira vez)
async function downloadAllVideos() {
    try {
        // Limpar blobs anteriores
        clearAllVideos();
        
        showLoading(`Baixando ${availableVideos.length} vídeo(s)...`);
        
        // Baixar todos os vídeos
        for (let i = 0; i < availableVideos.length; i++) {
            const video = availableVideos[i];
            console.log(`📥 Baixando vídeo ${i + 1}/${availableVideos.length}: ${video.original_filename}`);
            
            const url = `${config.serverUrl}/api/download/${video.id}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Erro ao baixar vídeo ${video.original_filename}: ${response.status}`);
            }
            
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            
            downloadedBlobs.push({
                id: video.id,
                url: blobUrl,
                filename: video.original_filename
            });
        }
        
        console.log(`✅ ${downloadedBlobs.length} vídeo(s) baixado(s) com sucesso`);
        hideLoading();
        
        // Iniciar reprodução
        videoIndex = 0;
        playVideoAtIndex(0);
        
    } catch (error) {
        console.error('❌ Erro ao baixar vídeos:', error);
        hideLoading();
        showError(`Erro ao carregar vídeos: ${error.message}`);
    }
}

// Reproduzir vídeo no índice especificado
function playVideoAtIndex(index) {
    if (downloadedBlobs.length === 0) {
        console.log('ℹ️ Nenhum vídeo disponível para reproduzir');
        return;
    }
    
    // Garantir que o índice está dentro dos limites
    videoIndex = index % downloadedBlobs.length;
    
    const videoData = downloadedBlobs[videoIndex];
    console.log(`▶️ Reproduzindo vídeo ${videoIndex + 1}/${downloadedBlobs.length}: ${videoData.filename}`);
    
    videoPlayer.src = videoData.url;
    videoPlayer.load();
    
    // Atualizar interface
    document.getElementById('video-info').textContent = 
        `${videoData.filename} (${videoIndex + 1}/${downloadedBlobs.length})`;
    
    // Tentar reproduzir
    const playPromise = videoPlayer.play();
    
    if (playPromise !== undefined) {
        playPromise.then(() => {
            console.log('✅ Vídeo reproduzindo');
            // Registrar visualização no servidor
            registerVisualization(videoData.id);
        }).catch((error) => {
            console.warn('⚠️ Autoplay bloqueado, clique na tela para iniciar:', error);
            // Adicionar evento de clique para iniciar reprodução
            document.body.addEventListener('click', function playOnClick() {
                videoPlayer.play().then(() => {
                    // Registrar visualização após o play manual
                    registerVisualization(videoData.id);
                });
                document.body.removeEventListener('click', playOnClick);
            }, { once: true });
        });
    }
}

// Registrar visualização no servidor (consome crédito)
async function registerVisualization(videoId) {
    try {
        const url = `${config.serverUrl}/api/visualizacao/${videoId}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                latitude: config.latitude,
                longitude: config.longitude
            })
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`📊 Visualização registrada - Créditos restantes: ${data.creditos_restantes}`);
        
        // Se o vídeo ficou sem créditos, será pausado automaticamente
        // Na próxima verificação, ele não aparecerá mais na lista
        
    } catch (error) {
        console.error('❌ Erro ao registrar visualização:', error);
        // Não mostrar erro ao usuário, apenas logar
    }
}

// Reproduzir próximo vídeo
function playNextVideo() {
    if (downloadedBlobs.length === 0) {
        return;
    }
    
    console.log('⏭️ Próximo vídeo...');
    const nextIndex = (videoIndex + 1) % downloadedBlobs.length;
    playVideoAtIndex(nextIndex);
}

// Limpar todos os vídeos
function clearAllVideos() {
    // Liberar todos os blobs
    downloadedBlobs.forEach(item => {
        URL.revokeObjectURL(item.url);
    });
    
    downloadedBlobs = [];
    availableVideos = [];
    videoIndex = 0;
    
    // Parar reprodução
    videoPlayer.src = '';
    videoPlayer.pause();
}

// Baixar e reproduzir vídeo (mantido para compatibilidade, mas não é mais usado)
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
    clearAllVideos();
    
    if (checkTimer) {
        clearInterval(checkTimer);
    }
});
